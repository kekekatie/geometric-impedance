#!/usr/bin/env python3
"""
Accretion pilot v7 -- magnitude vs direction-consistency (snapshot-only).

Reanalysis of v6's four crossed worlds using v6's retained snapshots
(../v6_intervention/results/edge_snapshots_v6.npz). No new worlds, dynamics, or
parameter sweeps. Frozen v5/v6 reader: S_high = sum s(e) 1[w_e >= 5.5] over present
added diagonals (A-positive, unchanged threshold).

Question: does crossing the inherited arrangements reduce each world's directional
footprint MAGNITUDE (|S_high|), or mainly reduce the CONSISTENCY of its direction
across worlds (sign agreement)?

Also verifies the transpose-symmetry identities on signed means
(mu_AA + mu_BB ~ 0, mu_AB + mu_BA ~ 0), so the signed-mean 'interaction' is zero by
symmetry (v6's sub-additivity reading is withdrawn).

Speculative exploration; not a confirmatory study or a test of cosmology.

Reproduce:
    python accretion_pilot_v7.py
"""
from __future__ import annotations

import csv
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_V6DIR = os.path.join(os.path.dirname(_HERE), "v6_intervention")
_V6NPZ = os.path.join(_V6DIR, "results", "edge_snapshots_v6.npz")
_V6SUM = os.path.join(_V6DIR, "results", "summary_worlds.csv")

THRESH = 5.5
WORLDS = ["WA_TA", "WA_TB", "WB_TA", "WB_TB"]
WLABEL = {"WA_TA": "W_A+T_A (intact A)", "WA_TB": "W_A+T_B (crossed)",
          "WB_TA": "W_B+T_A (crossed)", "WB_TB": "W_B+T_B (intact B)"}
ALIGNED = ("WA_TA", "WB_TB")
CROSSED = ("WA_TB", "WB_TA")
BOOT_CPS = (400, 2000, 10000)


def load():
    z = np.load(_V6NPZ)
    signs = z["signs"].astype(float)
    is_added = z["is_added"].astype(bool)
    checkpoints = tuple(int(c) for c in z["checkpoints"].tolist())
    n_seeds = int(z["n_seeds"])
    arr = {(w, cp): z[f"{w}__{cp}"] for w in WORLDS for cp in checkpoints}
    return signs, is_added, checkpoints, n_seeds, arr


def readers(a, signs, is_added):
    """Per-world vectors -> S_high, |S_high|, n_high_bit, n_present_diag."""
    present_added = is_added[None, :] & (a > 0)
    high = is_added[None, :] & (a >= THRESH)
    S = (signs[None, :] * high).sum(axis=1)
    n_high = high.sum(axis=1)
    n_pres = present_added.sum(axis=1)
    return S, n_high, n_pres


def boot_mean(x, n_boot=4000, seed=31):
    x = np.asarray(x, float); n = len(x); rng = np.random.default_rng(seed)
    bs = np.array([x[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    return float(x.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def main():
    results_dir = os.path.join(_HERE, "results")
    figures_dir = os.path.join(_HERE, "figures")
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    signs, is_added, checkpoints, n_seeds, arr = load()
    print(f"Snapshot coverage: {len(arr)} arrays "
          f"(expect {len(WORLDS) * len(checkpoints)}); n_seeds={n_seeds}; "
          f"added={int(is_added.sum())}")

    # S[world][cp] = signed S_high over seeds ; plus counts
    S = {w: {} for w in WORLDS}
    NH = {w: {} for w in WORLDS}
    NP = {w: {} for w in WORLDS}
    for w in WORLDS:
        for cp in checkpoints:
            s, nh, npd = readers(arr[(w, cp)], signs, is_added)
            S[w][cp] = s; NH[w][cp] = nh; NP[w][cp] = npd

    repro_ok = validate_vs_v6(results_dir, S, checkpoints)
    print("S_high reproduction vs v6:", "PASS" if repro_ok else "CHECK")

    write_frozen_tables(results_dir, S, NH, NP, checkpoints)
    write_alignment(results_dir, S, checkpoints)
    write_symmetry(results_dir, S, checkpoints)
    make_figure(figures_dir, S, checkpoints)

    cfg = {"reader": "S_high = sum s(e) 1[w>=5.5] over added diagonals (frozen v5/v6)",
           "source": os.path.relpath(_V6NPZ, _HERE),
           "aligned": ALIGNED, "crossed": CROSSED,
           "checkpoints": list(checkpoints), "n_seeds": n_seeds,
           "reproduction_vs_v6": "PASS" if repro_ok else "CHECK",
           "env": {"python": sys.version.split()[0], "numpy": np.__version__}}
    with open(os.path.join(results_dir, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)

    console(S, NH, NP, checkpoints)
    print(f"\nWrote results/ and figures/ under {_HERE}")


def validate_vs_v6(results_dir, S, checkpoints):
    lines = ["# v7 reproduces v6 S_high mean per world/checkpoint (from same snapshots)"]
    ok = True
    if not os.path.exists(_V6SUM):
        lines.append(f"# v6 summary not found: {_V6SUM}"); ok = False
    else:
        ref = {}
        with open(_V6SUM) as f:
            for r in csv.DictReader(f):
                ref[(r["world"], int(r["checkpoint"]))] = float(r["S_high_mean"])
        maxd = 0.0; n = 0
        for w in WORLDS:
            for cp in checkpoints:
                got = float(S[w][cp].mean())
                key = (w, cp)
                if key in ref:
                    maxd = max(maxd, abs(got - ref[key])); n += 1
        ok = maxd < 1e-3
        lines.append(f"# compared {n} means; max|d| = {maxd:.2e}; tol 1e-3 "
                     f"(v6 stored 4 dp); status = {'PASS' if ok else 'FAIL'}")
    lines.append(f"# overall: {'PASS' if ok else 'CHECK'}")
    with open(os.path.join(results_dir, "validation_vs_v6.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return ok


def write_frozen_tables(results_dir, S, NH, NP, checkpoints):
    rows = ["world,checkpoint,mean_signed,mean_abs,median_abs,iqr_abs,"
            "frac_pos,frac_zero,frac_neg,n_high_bit_mean,n_present_diag_mean"]
    for w in WORLDS:
        for cp in checkpoints:
            s = S[w][cp]; a = np.abs(s)
            q1, q3 = np.percentile(a, [25, 75])
            rows.append(
                f"{w},{cp},{s.mean():.4f},{a.mean():.4f},{np.median(a):.4f},"
                f"{q3 - q1:.4f},{np.mean(s > 0):.4f},{np.mean(s == 0):.4f},"
                f"{np.mean(s < 0):.4f},{NH[w][cp].mean():.4f},{NP[w][cp].mean():.4f}")
    with open(os.path.join(results_dir, "frozen_readouts.csv"), "w") as f:
        f.write("\n".join(rows) + "\n")


def write_alignment(results_dir, S, checkpoints):
    rows = ["checkpoint,mean_A(|aligned|),mean_C(|crossed|),mean_diff_A_minus_C,"
            "diff_lo,diff_hi,"
            "mean_absAA,mean_absBB,mean_absAB,mean_absBA"]
    for cp in [c for c in BOOT_CPS if c in checkpoints]:
        aAA = np.abs(S["WA_TA"][cp]); aBB = np.abs(S["WB_TB"][cp])
        aAB = np.abs(S["WA_TB"][cp]); aBA = np.abs(S["WB_TA"][cp])
        A_k = (aAA + aBB) / 2.0
        C_k = (aAB + aBA) / 2.0
        d, lo, hi = boot_mean(A_k - C_k, seed=17 + cp)
        rows.append(f"{cp},{A_k.mean():.4f},{C_k.mean():.4f},{d:.4f},{lo:.4f},"
                    f"{hi:.4f},{aAA.mean():.4f},{aBB.mean():.4f},{aAB.mean():.4f},"
                    f"{aBA.mean():.4f}")
    with open(os.path.join(results_dir, "alignment_unsigned.csv"), "w") as f:
        f.write("\n".join(rows) + "\n")


def write_symmetry(results_dir, S, checkpoints):
    rows = ["checkpoint,mean_AA,mean_BB,resid_AA_plus_BB,r1_lo,r1_hi,"
            "mean_AB,mean_BA,resid_AB_plus_BA,r2_lo,r2_hi"]
    for cp in checkpoints:
        aa = S["WA_TA"][cp]; bb = S["WB_TB"][cp]
        ab = S["WA_TB"][cp]; ba = S["WB_TA"][cp]
        r1, r1lo, r1hi = boot_mean(aa + bb, seed=91 + cp)
        r2, r2lo, r2hi = boot_mean(ab + ba, seed=137 + cp)
        rows.append(f"{cp},{aa.mean():.4f},{bb.mean():.4f},{r1:.4f},{r1lo:.4f},"
                    f"{r1hi:.4f},{ab.mean():.4f},{ba.mean():.4f},{r2:.4f},{r2lo:.4f},"
                    f"{r2hi:.4f}")
    with open(os.path.join(results_dir, "symmetry_check.csv"), "w") as f:
        f.write("\n".join(rows) + "\n")


def make_figure(figures_dir, S, checkpoints):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    col = {"WA_TA": "#d62728", "WA_TB": "#ff7f0e", "WB_TA": "#2ca02c",
           "WB_TB": "#1f77b4"}

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # (0) signed distributions at t=2000, identical axes
    ax = axes[0]
    cp = 2000 if 2000 in checkpoints else max(checkpoints)
    allvals = np.concatenate([S[w][cp] for w in WORLDS])
    lim = np.ceil(np.percentile(np.abs(allvals), 99) / 5) * 5
    bins = np.linspace(-lim, lim, 41)
    for w in WORLDS:
        ax.hist(S[w][cp], bins=bins, histtype="step", lw=2, color=col[w],
                label=f"{WLABEL[w]}  (mean {S[w][cp].mean():+.1f}, "
                      f"mean|S| {np.abs(S[w][cp]).mean():.1f})")
    ax.axvline(0, ls="--", color="k", lw=0.8)
    ax.set_title(f"Signed S_high distributions at t={cp} (identical axes)\n"
                 "crossed worlds: near-zero mean but wide spread")
    ax.set_xlabel("S_high (signed; A-positive)"); ax.set_ylabel("count (of 200 seeds)")
    ax.legend(fontsize=7.5)

    # (1) unsigned imbalance over time
    ax = axes[1]
    cps = list(checkpoints)
    for w in WORLDS:
        med = [np.median(np.abs(S[w][cp])) for cp in cps]
        q1 = [np.percentile(np.abs(S[w][cp]), 25) for cp in cps]
        q3 = [np.percentile(np.abs(S[w][cp]), 75) for cp in cps]
        ax.plot(cps, med, "-o", color=col[w], label=WLABEL[w])
        ax.fill_between(cps, q1, q3, color=col[w], alpha=0.12)
    ax.set_xscale("symlog")
    ax.set_title("Unsigned directional imbalance |S_high| over time\n"
                 "median + IQR; aligned and crossed are comparable")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("|S_high|")
    ax.legend(fontsize=7.5)

    fig.suptitle("v7: crossing scrambles direction (sign consistency), not per-world "
                 "magnitude", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(figures_dir, "directionality_v7.png"), dpi=140)
    plt.close(fig)


def console(S, NH, NP, checkpoints):
    print("=" * 78)
    for cp in (2000, 10000):
        if cp not in checkpoints:
            continue
        print(f"t={cp}:")
        for w in WORLDS:
            s = S[w][cp]
            print(f"  {w}: mean {s.mean():+7.3f}  mean|S| {np.abs(s).mean():6.3f}  "
                  f"sd {s.std(ddof=1):6.3f}  frac+ {np.mean(s>0):.2f} "
                  f"frac0 {np.mean(s==0):.2f} frac- {np.mean(s<0):.2f}  "
                  f"n_high {NH[w][cp].mean():.1f}")
    print("=" * 78)


if __name__ == "__main__":
    main()

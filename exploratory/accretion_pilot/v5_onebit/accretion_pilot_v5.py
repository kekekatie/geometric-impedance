#!/usr/bin/env python3
"""
Accretion pilot v5 -- one bit per added diagonal.

Snapshot-only reader analysis. We do NOT rerun trajectories: we load v4's saved
per-edge snapshots (../v4_decomposition/results/edge_snapshots.npz) and change only
the reader. Same 200 seed pairs, models, and checkpoints.

Question: can a single bit per added diagonal -- whether it has accumulated at
least four traversals since activation -- retain the late A/B history distinction?

Threshold (corrected; not exact w==6, which is only float rounding). Under the rule
6 - w_n = 5/2^n, so w >= 5.5 first holds at n=4:
    b(e) = 1 if w_e >= 5.5 else 0      ("four-or-more traversals" / "rounds to 6")

Readers on PRESENT added diagonals only, with the existing coordinate sign s(e):
    P_D    = sum s(e)                 (added-edge presence contrast)
    S_high = sum s(e)*b(e)            (one-bit high-bin contrast; PRIMARY, A-positive)
    S_low  = sum s(e)*(1-b(e))        (low-bin contrast); complementary score = -S_low
Identity asserted per snapshot: S_high + S_low = P_D. On complete topology P_D = 0,
so S_high = -S_low (also checked). Missing diagonals are a distinct state (not
low-weight present edges); their mask/counts are retained.

Speculative exploration; not a confirmatory study or a test of cosmology.

Reproduce:
    python accretion_pilot_v5.py
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from fractions import Fraction as Fr

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_V4DIR = os.path.join(os.path.dirname(_HERE), "v4_decomposition")
_SNAP = os.path.join(_V4DIR, "results", "edge_snapshots.npz")
_V4SUM = os.path.join(_V4DIR, "results", "summary_by_reader.csv")

MODELS = ("Fixed", "Reinforced", "Growing", "Growing-MatchedControl")
HISTS = ("A", "B")
THRESH = 5.5
W_MAX = 6.0
N_CAND = 128
BOOT_CPS = (400, 2000, 10000)

# readers to tabulate: label -> key
READERS = [("onebit_Shigh", "S_high"), ("complement_negSlow", "negS_low"),
           ("added_exact_D0", "D0"), ("added_whole_D1", "D1"),
           ("added_presence_PD", "P_D")]


# ---------------------------------------------------------------------------
# Fixture: threshold b(e)=1 iff w>=5.5 iff n>=4 traversals; 6-w_n = 5/2^n
# ---------------------------------------------------------------------------
def fixture_threshold():
    w = Fr(1)
    ok = True
    first = None
    for n in range(0, 8):
        ok &= (Fr(6) - w == Fr(5, 2 ** n))          # exact gap identity
        if first is None and w >= Fr(11, 2):
            first = n
        # "rounds to 6" iff w >= 5.5
        ok &= ((w >= Fr(11, 2)) == (math.floor(float(w) + 0.5) == 6))
        w = w + Fr(1, 2) * (Fr(6) - w)
    ok &= (first == 4)
    return ok


# ---------------------------------------------------------------------------
# Load snapshots
# ---------------------------------------------------------------------------
def load_snapshots():
    z = np.load(_SNAP)
    signs = z["signs"].astype(float)
    is_original = z["is_original"].astype(bool)
    added = ~is_original
    checkpoints = tuple(int(c) for c in z["checkpoints"].tolist())
    n_seeds = int(z["n_seeds"])
    arrs = {}
    for m in MODELS:
        for hl in HISTS:
            for cp in checkpoints:
                arrs[(m, hl, cp)] = z[f"{m}__{hl}__{cp}"]
    return signs, added, checkpoints, n_seeds, arrs


def validate_schema(signs, added, checkpoints, n_seeds, arrs):
    ok = True
    ok &= signs.shape == (272,)
    ok &= set(np.unique(signs).tolist()) <= {-1.0, 0.0, 1.0}
    ok &= int((~added).sum()) == 144 and int(added.sum()) == 128
    ok &= len(arrs) == len(MODELS) * len(HISTS) * len(checkpoints)
    for a in arrs.values():
        ok &= a.shape == (n_seeds, 272)
    return ok


# ---------------------------------------------------------------------------
# Readers computed vectorised over the (n_seeds, 272) array
# ---------------------------------------------------------------------------
def compute_readers(arr, signs, added):
    s = signs[None, :]
    present_added = added[None, :] & (arr > 0.0)
    hi = (arr >= THRESH) & present_added
    lo = (arr < THRESH) & present_added
    P_D = (s * present_added).sum(axis=1)
    S_high = (s * hi).sum(axis=1)
    S_low = (s * lo).sum(axis=1)
    D0 = (s * arr * present_added).sum(axis=1)
    D1 = (s * np.floor(arr + 0.5) * present_added).sum(axis=1)
    n_present = present_added.sum(axis=1)
    # identity S_high + S_low == P_D
    assert np.allclose(S_high + S_low, P_D, atol=1e-9), "S_high+S_low != P_D"
    return {"P_D": P_D, "S_high": S_high, "S_low": S_low, "negS_low": -S_low,
            "D0": D0, "D1": D1, "n_present": n_present}


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------
def auc(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    allv = np.concatenate([a, b])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv), float)
    ranks[order] = np.arange(1, len(allv) + 1)
    _, inv, counts = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.zeros(len(counts)); np.add.at(sums, inv, ranks)
    ranks = (sums / counts)[inv]
    nA = len(a)
    return float((ranks[:nA].sum() - nA * (nA + 1) / 2.0) / (nA * len(b)))


def paired_frac(a, b):
    d = np.asarray(a, float) - np.asarray(b, float)
    return float(np.mean((d > 0) * 1.0 + (d == 0) * 0.5))


def tie_frac(a, b):
    d = np.asarray(a, float) - np.asarray(b, float)
    return float(np.mean(d == 0))


def bal_acc(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    rA = np.mean((a > 0) * 1.0 + (a == 0) * 0.5)
    rB = np.mean((b < 0) * 1.0 + (b == 0) * 0.5)
    return float((rA + rB) / 2.0)


def boot_auc(a, b, n_boot=2000, seed=51):
    a, b = np.asarray(a, float), np.asarray(b, float)
    n = len(a); rng = np.random.default_rng(seed)
    bs = np.empty(n_boot)
    for k in range(n_boot):
        i = rng.integers(0, n, n)
        bs[k] = auc(a[i], b[i])
    return auc(a, b), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def boot_auc_diff_within(aA, aB, bA, bB, n_boot=2000, seed=53):
    """AUC(reader1) - AUC(reader2), same model, resampling seed pairs."""
    aA, aB, bA, bB = map(lambda x: np.asarray(x, float), (aA, aB, bA, bB))
    n = len(aA); rng = np.random.default_rng(seed)
    pt = auc(aA, aB) - auc(bA, bB)
    bs = np.empty(n_boot)
    for k in range(n_boot):
        i = rng.integers(0, n, n)
        bs[k] = auc(aA[i], aB[i]) - auc(bA[i], bB[i])
    return pt, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def boot_auc_diff_between(m1A, m1B, m2A, m2B, n_boot=2000, seed=57):
    """AUC(model1 reader) - AUC(model2 reader), resampling seed pairs."""
    m1A, m1B, m2A, m2B = map(lambda x: np.asarray(x, float), (m1A, m1B, m2A, m2B))
    n = len(m1A); rng = np.random.default_rng(seed)
    pt = auc(m1A, m1B) - auc(m2A, m2B)
    bs = np.empty(n_boot)
    for k in range(n_boot):
        i = rng.integers(0, n, n)
        bs[k] = auc(m1A[i], m1B[i]) - auc(m2A[i], m2B[i])
    return pt, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=_HERE)
    args = ap.parse_args()
    results_dir = os.path.join(args.outdir, "results")
    figures_dir = os.path.join(args.outdir, "figures")
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    print("Threshold fixture (6-w_n=5/2^n; w>=5.5 iff n>=4 iff rounds to 6):",
          "PASS" if fixture_threshold() else "FAIL")

    signs, added, checkpoints, n_seeds, arrs = load_snapshots()
    print("Snapshot schema:", "PASS" if validate_schema(
        signs, added, checkpoints, n_seeds, arrs) else "FAIL")

    # rv[model][hist][cp] = readers dict
    rv = {m: {"A": {}, "B": {}} for m in MODELS}
    for m in MODELS:
        for hl in HISTS:
            for cp in checkpoints:
                rv[m][hl][cp] = compute_readers(arrs[(m, hl, cp)], signs, added)

    validate_vs_v4(results_dir, rv, checkpoints)
    write_tables(results_dir, rv, checkpoints, n_seeds)
    complete_subset(results_dir, rv, arrs, added, checkpoints)
    make_figure(figures_dir, rv, checkpoints)
    console_summary(rv, checkpoints)
    print(f"\nWrote results/ and figures/ under {args.outdir}")


def validate_vs_v4(results_dir, rv, checkpoints):
    """Reproduce v4's added-edge readers D0, D1 (AUC) from the snapshots."""
    lines = ["# v5 reproduction of v4 added-edge readers (D0, D1) AUC from snapshots"]
    ok = True
    if not os.path.exists(_V4SUM):
        lines.append(f"# v4 summary not found: {_V4SUM}"); ok = False
    else:
        v4 = {}
        with open(_V4SUM) as f:
            for r in csv.DictReader(f):
                v4[(r["model"], int(r["checkpoint"]), r["reader"])] = float(r["auc"])
        maxd = 0.0; n = 0
        for m in MODELS:
            for cp in checkpoints:
                for key, lab in (("D0", "added_D0"), ("D1", "added_D1")):
                    got = auc(rv[m]["A"][cp][key], rv[m]["B"][cp][key])
                    ref = v4.get((m, cp, lab))
                    if ref is not None:
                        maxd = max(maxd, abs(got - ref)); n += 1
        ok = maxd < 5e-4
        lines.append(f"# compared {n} AUC values; max|dAUC| = {maxd:.2e}; "
                     f"tol 5e-4 (v4 stored 4 dp); status = {'PASS' if ok else 'FAIL'}")
    lines.append(f"# overall: {'PASS' if ok else 'CHECK'}")
    with open(os.path.join(results_dir, "validation_vs_v4.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("v4 added-edge reproduction:", "PASS" if ok else "CHECK validation_vs_v4.txt")


def write_tables(results_dir, rv, checkpoints, n_seeds):
    summ = ["model,checkpoint,reader,auc,bal_acc,paired_frac,tie_frac,signed_sep,"
            "mean_added_present"]
    for m in MODELS:
        for cp in checkpoints:
            npres = np.mean(np.concatenate([rv[m]["A"][cp]["n_present"],
                                            rv[m]["B"][cp]["n_present"]]))
            for lab, key in READERS:
                a = rv[m]["A"][cp][key]; b = rv[m]["B"][cp][key]
                summ.append(f"{m},{cp},{lab},{auc(a,b):.4f},{bal_acc(a,b):.4f},"
                            f"{paired_frac(a,b):.4f},{tie_frac(a,b):.4f},"
                            f"{np.mean(a)-np.mean(b):.6f},{npres:.4f}")
    with open(os.path.join(results_dir, "summary_by_reader.csv"), "w") as f:
        f.write("\n".join(summ) + "\n")

    bl = ["quantity,model,checkpoint,point,ci_lo,ci_hi,note"]
    for cp in [c for c in BOOT_CPS if c in checkpoints]:
        for m in MODELS:
            p, lo, hi = boot_auc(rv[m]["A"][cp]["S_high"], rv[m]["B"][cp]["S_high"])
            bl.append(f"onebit_auc,{m},{cp},{p:.4f},{lo:.4f},{hi:.4f},A-positive")
        # one-bit minus D1 within Growing (cost of collapsing to 1 bit)
        p, lo, hi = boot_auc_diff_within(
            rv["Growing"]["A"][cp]["S_high"], rv["Growing"]["B"][cp]["S_high"],
            rv["Growing"]["A"][cp]["D1"], rv["Growing"]["B"][cp]["D1"])
        bl.append(f"onebit_minus_D1_within_Growing,Growing,{cp},{p:.4f},{lo:.4f},"
                  f"{hi:.4f},negative=loss_from_1bit")
        # Growing minus control one-bit
        p, lo, hi = boot_auc_diff_between(
            rv["Growing"]["A"][cp]["S_high"], rv["Growing"]["B"][cp]["S_high"],
            rv["Growing-MatchedControl"]["A"][cp]["S_high"],
            rv["Growing-MatchedControl"]["B"][cp]["S_high"])
        bl.append(f"growing_minus_control_onebit,Growing_vs_Control,{cp},{p:.4f},"
                  f"{lo:.4f},{hi:.4f},positive=Growing_higher")
    with open(os.path.join(results_dir, "bootstrap_onebit.csv"), "w") as f:
        f.write("\n".join(bl) + "\n")

    cfg = {"threshold": "b(e)=1 if w>=5.5 (>=4 traversals / rounds to 6)",
           "readers": "P_D, S_high (primary one-bit), S_low, -S_low (complement), "
                      "D0, D1; identity S_high+S_low=P_D",
           "source_snapshots": os.path.relpath(_SNAP, _HERE),
           "checkpoints": list(checkpoints), "n_seeds": n_seeds,
           "models": list(MODELS),
           "env": {"python": sys.version.split()[0], "numpy": np.__version__}}
    with open(os.path.join(results_dir, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)


def complete_subset(results_dir, rv, arrs, added, checkpoints):
    cp = max(checkpoints)
    lines = ["# Complete-topology subset at t=%d (DESCRIPTIVE; selected after "
             "evolution). A world is complete iff all %d diagonals present." % (cp, N_CAND)]
    # per-model complete masks and excluded seeds
    comp = {}
    for m in MODELS:
        cmask = {}
        for hl in HISTS:
            npres = (arrs[(m, hl, cp)][:, added] > 0).sum(axis=1)
            cmask[hl] = npres == N_CAND
        both = cmask["A"] & cmask["B"]
        comp[m] = both
        excl = np.nonzero(~both)[0].tolist()
        lines.append(f"# {m}: complete pairs = {int(both.sum())}/{len(both)}; "
                     f"excluded seed ids = {excl}")
    # do the model subsets match?
    gset = set(np.nonzero(comp["Growing"])[0].tolist())
    cset = set(np.nonzero(comp["Growing-MatchedControl"])[0].tolist())
    lines.append(f"# Growing vs Control complete-subset identical seed set? "
                 f"{gset == cset}  (|G|={len(gset)}, |C|={len(cset)}, "
                 f"symmetric_diff={sorted(gset ^ cset)})")
    lines.append("# NOTE: subsets are per-model; different subsets are NOT a matched "
                 "comparison.")
    lines.append("")
    # On complete topology P_D=0 -> S_high = -S_low per world; verify per model.
    for m in MODELS:
        both = comp[m]
        if both.sum() == 0:
            lines.append(f"# {m}: no complete pairs; S_high=-S_low identity n/a")
            continue
        idok = True
        for hl in HISTS:
            idok &= bool(np.allclose(rv[m][hl][cp]["S_high"][both],
                                     rv[m][hl][cp]["negS_low"][both], atol=1e-9))
        lines.append(f"# {m}: on complete subset S_high == -S_low (P_D=0)? {idok}")
    lines.append("")
    lines.append("model,reader,n_pairs,auc,bal_acc,paired_frac,tie_frac,signed_sep")
    for m in MODELS:
        both = comp[m]; n = int(both.sum())
        for lab, key in READERS:
            if n == 0:
                lines.append(f"{m},{lab},0,nan,nan,nan,nan,nan"); continue
            a = rv[m]["A"][cp][key][both]; b = rv[m]["B"][cp][key][both]
            lines.append(f"{m},{lab},{n},{auc(a,b):.4f},{bal_acc(a,b):.4f},"
                         f"{paired_frac(a,b):.4f},{tie_frac(a,b):.4f},"
                         f"{np.mean(a)-np.mean(b):.6f}")
    with open(os.path.join(results_dir, "complete_topology_subset.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")


def make_figure(figures_dir, rv, checkpoints):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cps = list(checkpoints)
    rc = {"S_high": "#d62728", "D1": "#ff7f0e", "D0": "#8c564b",
          "P_D": "#9467bd", "negS_low": "#17becf"}
    mc = {"Growing": "#d62728", "Growing-MatchedControl": "#2ca02c",
          "Reinforced": "#1f77b4", "Fixed": "#888888"}

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # (0,0) Growing: one-bit vs added-weight readers vs presence
    ax = axes[0, 0]
    for key, lab in [("S_high", "one-bit S_high (>=4 traversals)"),
                     ("D1", "added whole-number D1"), ("D0", "added exact D0"),
                     ("P_D", "added presence P_D"),
                     ("negS_low", "complement -S_low")]:
        ys = [auc(rv["Growing"]["A"][cp][key], rv["Growing"]["B"][cp][key]) for cp in cps]
        ax.plot(cps, ys, "-o", color=rc[key], label=lab)
    ax.axhline(0.5, ls="--", color="k", lw=0.8)
    ax.set_xscale("symlog"); ax.set_ylim(0.45, 1.02)
    ax.set_title("Growing: one-bit vs added-weight & presence readers")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("AUC"); ax.legend(fontsize=8)

    # (0,1) Growing one-bit vs D1 with bootstrap CIs at 400/2000/10000
    ax = axes[0, 1]
    for key, lab, col in [("S_high", "one-bit S_high", rc["S_high"]),
                          ("D1", "added whole-number D1", rc["D1"])]:
        ys = [auc(rv["Growing"]["A"][cp][key], rv["Growing"]["B"][cp][key]) for cp in cps]
        ax.plot(cps, ys, "-o", color=col, label=lab)
    for cp in [c for c in BOOT_CPS if c in checkpoints]:
        for key, col, dx in [("S_high", rc["S_high"], 0.9), ("D1", rc["D1"], 1.1)]:
            p, lo, hi = boot_auc(rv["Growing"]["A"][cp][key], rv["Growing"]["B"][cp][key])
            ax.errorbar([cp * dx], [p], yerr=[[p - lo], [hi - p]], fmt="none",
                        ecolor=col, capsize=3, alpha=0.8)
    ax.axhline(0.5, ls="--", color="k", lw=0.8)
    ax.set_xscale("symlog"); ax.set_ylim(0.45, 1.02)
    ax.set_title("Growing: cost of collapsing added reader to one bit\n"
                 "(bars = seed-pair bootstrap 95% CI at 400/2000/10000)")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("AUC"); ax.legend(fontsize=8)

    # (1,0) cross-model one-bit
    ax = axes[1, 0]
    for m in MODELS:
        ys = [auc(rv[m]["A"][cp]["S_high"], rv[m]["B"][cp]["S_high"]) for cp in cps]
        ax.plot(cps, ys, "-o", color=mc[m], label=m)
    ax.axhline(0.5, ls="--", color="k", lw=0.8)
    ax.set_xscale("symlog"); ax.set_ylim(0.45, 1.02)
    ax.set_title("One-bit reader S_high across models\n(Reinforced/Fixed have no "
                 "added edges -> chance)")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("AUC"); ax.legend(fontsize=8)

    # (1,1) late (t=10000) bar chart: readers for Growing vs Control
    ax = axes[1, 1]
    cp = max(cps)
    labels = ["one-bit\nS_high", "added\nD1", "added\nD0", "presence\nP_D"]
    keys = ["S_high", "D1", "D0", "P_D"]
    x = np.arange(len(keys)); wbar = 0.38
    for i, (m, off) in enumerate([("Growing", -wbar / 2),
                                  ("Growing-MatchedControl", wbar / 2)]):
        ys = [auc(rv[m]["A"][cp][k], rv[m]["B"][cp][k]) for k in keys]
        ax.bar(x + off, ys, wbar, color=mc[m], label=m, alpha=0.85)
    ax.axhline(0.5, ls="--", color="k", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0.45, 0.72)
    ax.set_title(f"Late (t={cp}) AUC by reader: Growing vs Control")
    ax.set_ylabel("AUC"); ax.legend(fontsize=8)

    fig.suptitle("v5 one-bit reader: does '>=4 traversals per added diagonal' retain "
                 "the history distinction?", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(figures_dir, "onebit_reader_v5.png"), dpi=140)
    plt.close(fig)


def console_summary(rv, checkpoints):
    print("=" * 78)
    print("v5 one-bit reader -- AUC (Growing) by reader")
    for cp in (400, 2000, 10000):
        if cp not in checkpoints:
            continue
        parts = "  ".join(
            f"{lab.split('_')[0]}={auc(rv['Growing']['A'][cp][key], rv['Growing']['B'][cp][key]):.3f}"
            for lab, key in [("onebit", "S_high"), ("D1", "D1"), ("D0", "D0"),
                             ("presence", "P_D")])
        print(f"  t={cp:5d}: {parts}")
    print("=" * 78)


if __name__ == "__main__":
    main()

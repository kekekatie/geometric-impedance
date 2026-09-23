#!/usr/bin/env python3
"""
Accretion pilot v8 -- neutral weight background, history-shaped placement.

Intervention on initial conditions only; the movement/reinforcement/growth rules
are v2's, unchanged. We neutralise the directional cue in original-edge weights by
averaging W_0 = (W_A + W_B)/2 (transpose-invariant -> no A/B bias), keep the two
history-shaped diagonal placements T_A, T_B, and ask whether placement alone guides
a later history-discriminating visitation footprint.

Two worlds (differ only in diagonal placement):
    W_0 + T_A   and   W_0 + T_B
evolved under unchanged Growing rules for 10,000 steps, read with the frozen v5
reader S_high = sum s(e) 1[w(e) >= 5.5] over present added diagonals.

Primary endpoint t=2000 (pre-selected from prior exploration).

Speculative exploration; not a confirmatory study or a test of cosmology.

Reproduce:
    python accretion_pilot_v8.py
    python accretion_pilot_v8.py --quick     # 20 seeds, 1000 steps
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_V2DIR = os.path.join(os.path.dirname(_HERE), "v2_saturation")
sys.path.insert(0, _V2DIR)
import accretion_pilot_v2 as v2   # noqa: E402

BASE_SEED = v2.BASE_SEED
CHECKPOINTS = v2.CHECKPOINTS
PROBE = v2.PROBE
W_MAX = v2.W_MAX
THRESH = 5.5
vid = v2.vid
weighted_step = v2.weighted_step

_BASE = list(v2.build_base_edges())
_CAND = [e for (_c, e) in v2.build_candidates()]
UNIVERSE = _BASE + _CAND
N_UNIV = len(UNIVERSE)
IS_ADDED = np.array([False] * len(_BASE) + [True] * len(_CAND))
SIGNS = np.array([v2.edge_midpoint_sign(e) for e in UNIVERSE], dtype=float)
UIDX = {e: i for i, e in enumerate(UNIVERSE)}
CONDS = ("W0_TA", "W0_TB")
PRIMARY_CP = 2000
BOOT_CPS = (400, 2000, 10000)


# transpose permutation on the universe (edge e -> sigma(e))
def _sigma_vid(x):
    r, c = divmod(x, v2.GRID_N)
    return c * v2.GRID_N + r


def _sigma_edge(e):
    return v2.ekey(_sigma_vid(e[0]), _sigma_vid(e[1]))


SIGMA_PERM = np.array([UIDX[_sigma_edge(e)] for e in UNIVERSE])


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------
def make_initial(history_kind):
    w = v2.World()
    for u, v in v2.history_edges(history_kind):
        w.reinforce(u, v)
        w.grow_from_edge(u, v)
    return w


def build_world(base_w, diag_set):
    w = v2.World()
    for e, val in base_w.items():
        w.weight[e] = val
    for e in sorted(diag_set):
        w._activate(e)                 # weight = W_INIT (1.0)
    return w


def vec_of(world):
    v = np.zeros(N_UNIV)
    for e, w in world.weight.items():
        v[UIDX[e]] = w
    return v


def evolve_capture(world, seed, checkpoints, n_steps):
    rng = np.random.default_rng(BASE_SEED + seed)
    out = {}
    if 0 in checkpoints:
        out[0] = vec_of(world)
    vtx = vid(*PROBE)
    for step in range(1, n_steps + 1):
        nxt = weighted_step(world, vtx, rng)
        world.reinforce(vtx, nxt)
        world.grow_from_edge(vtx, nxt)
        vtx = nxt
        if step in checkpoints:
            out[step] = vec_of(world)
    return out


# ---------------------------------------------------------------------------
# Reader + stats
# ---------------------------------------------------------------------------
def readers(a):
    present_added = IS_ADDED[None, :] & (a > 0)
    high = IS_ADDED[None, :] & (a >= THRESH)
    S = (SIGNS[None, :] * high).sum(axis=1)
    return S, high.sum(axis=1), present_added.sum(axis=1)


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


def boot_auc(a, b, n_boot=4000, seed=41):
    a, b = np.asarray(a, float), np.asarray(b, float)
    n = len(a); rng = np.random.default_rng(seed)
    bs = np.empty(n_boot)
    for k in range(n_boot):
        i = rng.integers(0, n, n)
        bs[k] = auc(a[i], b[i])
    return auc(a, b), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def boot_mean_diff(a, b, n_boot=4000, seed=43):
    d = np.asarray(a, float) - np.asarray(b, float)
    n = len(d); rng = np.random.default_rng(seed)
    bs = np.array([d[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    return float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--steps", type=int, default=v2.T_SUB)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    n_seeds = 20 if args.quick else args.seeds
    n_steps = 1000 if args.quick else args.steps
    checkpoints = tuple(cp for cp in CHECKPOINTS if cp <= n_steps)
    results_dir = os.path.join(_HERE, "results")
    figures_dir = os.path.join(_HERE, "figures")
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    # initial states + neutral background
    wA, wB = make_initial("upper"), make_initial("lower")
    W_A = {e: wA.weight[e] for e in wA.base_edge_set}
    W_B = {e: wB.weight[e] for e in wB.base_edge_set}
    T_A, T_B = set(wA.active), set(wB.active)
    W_0 = {e: (W_A[e] + W_B[e]) / 2.0 for e in W_A}
    T = {"TA": T_A, "TB": T_B}

    cons_ok = construction_checks(results_dir, W_0, W_A, W_B, T_A, T_B)
    print("Construction invariants:", "PASS" if cons_ok else "FAIL")

    init_worlds = {"W0_TA": build_world(W_0, T_A), "W0_TB": build_world(W_0, T_B)}

    S = {c: {} for c in CONDS}
    NH = {c: {} for c in CONDS}
    NP = {c: {} for c in CONDS}
    snaps = {c: {cp: [] for cp in checkpoints} for c in CONDS}
    for seed in range(n_seeds):
        for c, diag in (("W0_TA", T_A), ("W0_TB", T_B)):
            w = build_world(W_0, diag)
            out = evolve_capture(w, seed, checkpoints, n_steps)
            for cp, vec in out.items():
                snaps[c][cp].append(vec)
        if (seed + 1) % 25 == 0:
            print(f"  ... {seed + 1}/{n_seeds} seeds")
    for c in CONDS:
        for cp in checkpoints:
            arr = np.array(snaps[c][cp])
            snaps[c][cp] = arr
            s, nh, npd = readers(arr)
            S[c][cp] = s; NH[c][cp] = nh; NP[c][cp] = npd

    save_snapshots(results_dir, snaps, checkpoints, n_seeds)
    write_tables(results_dir, S, NH, NP, checkpoints, n_seeds, cons_ok)
    make_figure(figures_dir, S, checkpoints)
    console(S, NH, checkpoints)
    print(f"\nWrote results/ and figures/ under {_HERE}")


def construction_checks(results_dir, W_0, W_A, W_B, T_A, T_B):
    lines = ["# v8 construction invariant checks"]
    ok = True

    def rec(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        lines.append(f"[{'PASS' if cond else 'FAIL'}] {name}")

    # W_0 transpose-invariant
    w0_sym = all(abs(W_0[e] - W_0[_sigma_edge(e)]) < 1e-12 for e in W_0)
    rec("W_0 invariant under transpose (no A/B directional bias)", w0_sym)
    # T_B = sigma(T_A)
    rec("T_B == sigma(T_A) (transpose partners)",
        {_sigma_edge(e) for e in T_A} == set(T_B))
    rec("|T_A| == |T_B|", len(T_A) == len(T_B))
    # two worlds match edge count & total weight
    wTA, wTB = build_world(W_0, T_A), build_world(W_0, T_B)
    rec("matching initial edge count", len(wTA.weight) == len(wTB.weight))
    rec("matching initial total weight",
        abs(sum(wTA.weight.values()) - sum(wTB.weight.values())) < 1e-9)
    # zero initial high bits
    rec("zero initial high bits (both worlds)",
        readers(vec_of(wTA)[None, :])[1][0] == 0 and
        readers(vec_of(wTB)[None, :])[1][0] == 0)
    # transpose-related full states
    vTA, vTB = vec_of(wTA), vec_of(wTB)
    rec("W_0+T_B == sigma(W_0+T_A) full state",
        bool(np.allclose(vTB, vTA[SIGMA_PERM], atol=1e-12)))
    # documented: total weight preserved vs v6, multiset changed
    tot0 = sum(W_0.values()); totA = sum(W_A.values())
    ms_changed = sorted(W_0.values()) != sorted(W_A.values())
    rec("total original weight preserved vs v6 (sum W_0 == sum W_A)",
        abs(tot0 - totA) < 1e-9)
    lines.append(f"# NOTE: multiset(W_0) != multiset(W_A): {ms_changed} "
                 f"(averaging changes the weight multiset and local growth triggers)")
    lines.append(f"# edge_count={len(wTA.weight)}, total_weight={sum(wTA.weight.values()):.4f}, "
                 f"|T_A|=|T_B|={len(T_A)}, sumW_0={tot0:.4f}")
    with open(os.path.join(results_dir, "construction_checks.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return ok


def save_snapshots(results_dir, snaps, checkpoints, n_seeds):
    arrays = {"universe_u": np.array([e[0] for e in UNIVERSE]),
              "universe_v": np.array([e[1] for e in UNIVERSE]),
              "is_added": IS_ADDED, "signs": SIGNS,
              "checkpoints": np.array(checkpoints), "n_seeds": np.array(n_seeds)}
    for c in CONDS:
        for cp in checkpoints:
            arrays[f"{c}__{cp}"] = snaps[c][cp]
    path = os.path.join(results_dir, "edge_snapshots_v8.npz")
    np.savez_compressed(path, **arrays)
    print(f"Retained edge snapshots -> {os.path.basename(path)} "
          f"({os.path.getsize(path) / 1e6:.1f} MB)")


def write_tables(results_dir, S, NH, NP, checkpoints, n_seeds, cons_ok):
    rows = ["condition,checkpoint,mean_signed,mean_abs,frac_pos,frac_zero,frac_neg,"
            "n_high_bit_mean,n_present_diag_mean"]
    for c in CONDS:
        for cp in checkpoints:
            s = S[c][cp]
            rows.append(f"{c},{cp},{s.mean():.4f},{np.abs(s).mean():.4f},"
                        f"{np.mean(s > 0):.4f},{np.mean(s == 0):.4f},"
                        f"{np.mean(s < 0):.4f},{NH[c][cp].mean():.4f},"
                        f"{NP[c][cp].mean():.4f}")
    with open(os.path.join(results_dir, "frozen_readouts.csv"), "w") as f:
        f.write("\n".join(rows) + "\n")

    prim = ["quantity,checkpoint,point,ci_lo,ci_hi,note"]
    for cp in [c for c in BOOT_CPS if c in checkpoints]:
        a = S["W0_TA"][cp]; b = S["W0_TB"][cp]
        au, alo, ahi = boot_auc(a, b, seed=41 + cp)
        d, dlo, dhi = boot_mean_diff(a, b, seed=43 + cp)
        tag = "PRIMARY" if cp == PRIMARY_CP else "descriptive"
        prim.append(f"auc_TA_vs_TB,{cp},{au:.4f},{alo:.4f},{ahi:.4f},{tag}(TA positive)")
        prim.append(f"mean_signed_sep_TA_minus_TB,{cp},{d:.4f},{dlo:.4f},{dhi:.4f},{tag}")
    with open(os.path.join(results_dir, "primary_endpoint.csv"), "w") as f:
        f.write("\n".join(prim) + "\n")

    cfg = {"conditions": {c: ("W_0 + " + c[3:]) for c in CONDS},
           "neutral_background": "W_0(e) = (W_A(e)+W_B(e))/2 (transpose-invariant)",
           "reader": "S_high = sum s(e) 1[w>=5.5] over added diagonals (frozen v5)",
           "primary_endpoint": PRIMARY_CP,
           "orientation": "T_A positive; fixed in advance",
           "checkpoints": list(checkpoints), "n_seeds": n_seeds,
           "construction_checks": "PASS" if cons_ok else "FAIL",
           "env": {"python": sys.version.split()[0], "numpy": np.__version__}}
    with open(os.path.join(results_dir, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)


def make_figure(figures_dir, S, checkpoints):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cps = list(checkpoints)
    col = {"W0_TA": "#d62728", "W0_TB": "#1f77b4"}

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # (0) AUC(T_A vs T_B) over time with bootstrap CIs, primary t=2000 marked
    ax = axes[0]
    aucs, los, his = [], [], []
    for cp in cps:
        au, lo, hi = boot_auc(S["W0_TA"][cp], S["W0_TB"][cp], seed=41 + cp)
        aucs.append(au); los.append(au - lo); his.append(hi - au)
    ax.errorbar(cps, aucs, yerr=[los, his], fmt="-o", color="#6a3d9a", capsize=3,
                label="AUC (T_A vs T_B), seed-block bootstrap 95% CI")
    ax.axhline(0.5, ls="--", color="k", lw=0.8, label="chance")
    if PRIMARY_CP in cps:
        ax.axvline(PRIMARY_CP, ls=":", color="grey", lw=1)
        ap = aucs[cps.index(PRIMARY_CP)]
        ax.annotate(f"primary t=2000\nAUC={ap:.3f}", (PRIMARY_CP, ap),
                    textcoords="offset points", xytext=(10, -25), fontsize=9)
    ax.set_xscale("symlog"); ax.set_ylim(0.45, 1.02)
    ax.set_title("Placement-only discrimination under neutral W_0\n"
                 "AUC distinguishing W_0+T_A from W_0+T_B via S_high")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("AUC (T_A positive)")
    ax.legend(fontsize=8)

    # (1) signed mean +/- sd for the two conditions over time
    ax = axes[1]
    for c in CONDS:
        means = np.array([S[c][cp].mean() for cp in cps])
        sds = np.array([S[c][cp].std(ddof=1) for cp in cps])
        lab = "W_0 + T_A" if c == "W0_TA" else "W_0 + T_B"
        ax.plot(cps, means, "-o", color=col[c], label=lab)
        ax.fill_between(cps, means - sds, means + sds, color=col[c], alpha=0.12)
    ax.axhline(0.0, ls="--", color="k", lw=0.8)
    ax.set_xscale("symlog")
    ax.set_title("Signed S_high (mean +/- sd) under neutral W_0\n"
                 "placement is the only difference between the two worlds")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("mean S_high (A-positive)")
    ax.legend(fontsize=8)

    fig.suptitle("v8: does diagonal placement alone guide the later footprint under a "
                 "neutral (transpose-symmetric) weight background?", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(figures_dir, "placement_only_v8.png"), dpi=140)
    plt.close(fig)


def console(S, NH, checkpoints):
    print("=" * 78)
    for cp in (400, 2000, 10000):
        if cp not in checkpoints:
            continue
        a = S["W0_TA"][cp]; b = S["W0_TB"][cp]
        au, lo, hi = boot_auc(a, b, seed=41 + cp)
        d, dlo, dhi = boot_mean_diff(a, b, seed=43 + cp)
        tag = " [PRIMARY]" if cp == PRIMARY_CP else ""
        print(f"t={cp}{tag}: AUC(TA vs TB)={au:.3f} [{lo:.3f},{hi:.3f}]  "
              f"signed_sep={d:+.3f} [{dlo:+.3f},{dhi:+.3f}]  "
              f"meanTA={a.mean():+.3f} meanTB={b.mean():+.3f}  "
              f"n_high {NH['W0_TA'][cp].mean():.1f}/{NH['W0_TB'][cp].mean():.1f}")
    print("=" * 78)


if __name__ == "__main__":
    main()

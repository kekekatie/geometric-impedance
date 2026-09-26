#!/usr/bin/env python3
"""
Accretion pilot v6 -- crossed initial conditions (a 2x2 intervention).

We intervene on INITIAL CONDITIONS only; the subsequent movement / reinforcement /
growth rules are v2's, unchanged. We import v2's dynamics, build the deterministic
post-history Growing states for histories A and B, extract their original-edge
weight maps (W_A, W_B) and activated-diagonal sets (T_A, T_B), and cross them:

    1. W_A + T_A  (intact A)      3. W_B + T_A  (crossed)
    2. W_A + T_B  (crossed)       4. W_B + T_B  (intact B)

All four share initial edge count, total weight and original-edge weight multiset;
only the spatial arrangement differs. Each is evolved under the unchanged Growing
rules for 10,000 steps (200 paired seeds, common random numbers), and read with the
FROZEN v5 added-diagonal one-bit reader S_high = sum s(e) 1[w_e >= 5.5].

Question: does the later four-traversal footprint follow the initial original-edge
reinforcement (W), the initial diagonal placement (T), or their interaction?

Intact worlds are built by replaying the history (adjacency in history-activation
order) so they reproduce v2/v5; crossed worlds use a declared deterministic order
(base edges, then diagonals in sorted edge-key order, each weight 1).

Speculative exploration; not a confirmatory study or a test of cosmology.

Reproduce:
    python accretion_pilot_v6.py
    python accretion_pilot_v6.py --quick     # 20 seeds, 1000 steps
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_V2DIR = os.path.join(os.path.dirname(_HERE), "v2_saturation")
_V4NPZ = os.path.join(os.path.dirname(_HERE), "v4_decomposition", "results",
                      "edge_snapshots.npz")
sys.path.insert(0, _V2DIR)
import accretion_pilot_v2 as v2   # noqa: E402

BASE_SEED = v2.BASE_SEED
CHECKPOINTS = v2.CHECKPOINTS
PROBE = v2.PROBE
W_MAX = v2.W_MAX
W_INIT = v2.W_INIT
THRESH = 5.5
vid = v2.vid
weighted_step = v2.weighted_step

# fixed edge universe: base (original) then candidate (added) -- matches v4
_BASE = list(v2.build_base_edges())
_CAND = [e for (_c, e) in v2.build_candidates()]
UNIVERSE = _BASE + _CAND
N_UNIV = len(UNIVERSE)
IS_ADDED = np.array([False] * len(_BASE) + [True] * len(_CAND))
SIGNS = np.array([v2.edge_midpoint_sign(e) for e in UNIVERSE], dtype=float)
UIDX = {e: i for i, e in enumerate(UNIVERSE)}

WORLD_KEYS = [("A", "A"), ("A", "B"), ("B", "A"), ("B", "B")]
WORLD_LABEL = {("A", "A"): "W_A+T_A (intact A)", ("A", "B"): "W_A+T_B (crossed)",
               ("B", "A"): "W_B+T_A (crossed)", ("B", "B"): "W_B+T_B (intact B)"}
BOOT_CPS = (400, 2000, 10000)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------
def make_initial(history_kind):
    """Exactly v2 run_growing's history phase (traverse->reinforce->grow)."""
    w = v2.World()
    for u, v in v2.history_edges(history_kind):
        w.reinforce(u, v)
        w.grow_from_edge(u, v)
    return w


def extract(w):
    base_w = {e: w.weight[e] for e in w.base_edge_set}
    diag = set(w.active)
    return base_w, diag


def build_intact(history_kind):
    """History-activation adjacency order -> reproduces v2/v5 trajectories."""
    return make_initial(history_kind)


def build_crossed(base_w, diag_set):
    """Declared deterministic order: base edges, then diagonals sorted, weight 1."""
    w = v2.World()
    for e, val in base_w.items():
        w.weight[e] = val
    for e in sorted(diag_set):
        w._activate(e)                 # sets weight = W_INIT (1.0)
    return w


def build_world(wsrc, tsrc, W, T):
    if wsrc == tsrc:
        return build_intact("upper" if wsrc == "A" else "lower")
    return build_crossed(W[wsrc], T[tsrc])


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
# Readers on a weight vector
# ---------------------------------------------------------------------------
def readers(vec):
    present = vec > 0.0
    added_present = IS_ADDED & present
    S_high = float((SIGNS * (IS_ADDED & (vec >= THRESH))).sum())
    P_D = float((SIGNS * added_present).sum())
    B0 = float((SIGNS * vec * (~IS_ADDED)).sum())
    edge_count = int(present.sum())
    total_weight = float(vec.sum())
    headroom = float(np.mean((W_MAX - vec)[present]))
    n_active_diag = int(added_present.sum())
    return {"S_high": S_high, "P_D": P_D, "B0": B0, "edge_count": edge_count,
            "total_weight": total_weight, "headroom": headroom,
            "n_active_diag": n_active_diag}


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


def contrast(S, pos, neg, cp, n_boot=2000, seed=71):
    """Paired mean diff and A-oriented AUC for world[pos] vs world[neg]."""
    a = S[pos][cp]; b = S[neg][cp]
    n = len(a)
    diff = float(np.mean(a - b))
    au = auc(a, b)
    rng = np.random.default_rng(seed)
    dboot = np.empty(n_boot); aboot = np.empty(n_boot)
    for k in range(n_boot):
        idx = rng.integers(0, n, n)           # resample whole seed blocks
        dboot[k] = np.mean(a[idx] - b[idx])
        aboot[k] = auc(a[idx], b[idx])
    return {"mean_diff": diff, "d_lo": float(np.percentile(dboot, 2.5)),
            "d_hi": float(np.percentile(dboot, 97.5)), "auc": au,
            "auc_lo": float(np.percentile(aboot, 2.5)),
            "auc_hi": float(np.percentile(aboot, 97.5))}


def interaction(S, cp, n_boot=2000, seed=91):
    aa, ba = S[("A", "A")][cp], S[("B", "A")][cp]
    ab, bb = S[("A", "B")][cp], S[("B", "B")][cp]
    per = (aa - ba) - (ab - bb)
    n = len(per)
    rng = np.random.default_rng(seed)
    boot = np.array([np.mean(per[rng.integers(0, n, n)]) for _ in range(n_boot)])
    return {"mean": float(np.mean(per)), "lo": float(np.percentile(boot, 2.5)),
            "hi": float(np.percentile(boot, 97.5))}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=200)
    ap.add_argument("--steps", type=int, default=v2.T_SUB)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--outdir", default=_HERE)
    args = ap.parse_args()
    n_seeds = 20 if args.quick else args.seeds
    n_steps = 1000 if args.quick else args.steps
    checkpoints = tuple(cp for cp in CHECKPOINTS if cp <= n_steps)
    results_dir = os.path.join(args.outdir, "results")
    figures_dir = os.path.join(args.outdir, "figures")
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    # --- build initial states and check construction invariants -------------
    wAA, wBB = build_intact("upper"), build_intact("lower")
    W = {"A": extract(wAA)[0], "B": extract(wBB)[0]}
    T = {"A": extract(wAA)[1], "B": extract(wBB)[1]}
    cons_ok = construction_checks(results_dir, W, T)
    print("Construction invariants:", "PASS" if cons_ok else "FAIL")

    initial_worlds = {k: build_world(k[0], k[1], W, T) for k in WORLD_KEYS}
    initial_vecs = {k: vec_of(w) for k, w in initial_worlds.items()}

    # --- evolve all four worlds per seed ------------------------------------
    # rd[key][cp] = list over seeds of reader dict ; snap[key][cp] = (n,272)
    rd = {k: defaultdict(list) for k in WORLD_KEYS}
    snaps = {k: {cp: [] for cp in checkpoints} for k in WORLD_KEYS}
    for seed in range(n_seeds):
        for k in WORLD_KEYS:
            w = build_world(k[0], k[1], W, T)
            out = evolve_capture(w, seed, checkpoints, n_steps)
            for cp, vec in out.items():
                rd[k][cp].append(readers(vec))
                snaps[k][cp].append(vec)
        if (seed + 1) % 25 == 0:
            print(f"  ... {seed + 1}/{n_seeds} seeds")

    for k in WORLD_KEYS:
        for cp in checkpoints:
            snaps[k][cp] = np.array(snaps[k][cp])

    # S[key][cp] = array of S_high over seeds (and other readers)
    S = {k: {cp: np.array([r["S_high"] for r in rd[k][cp]]) for cp in checkpoints}
         for k in WORLD_KEYS}

    repro_ok = validate_vs_v4(results_dir, snaps, checkpoints)
    print("Reproduction of v2/v5 intact worlds:", "PASS" if repro_ok else "CHECK")

    save_snapshots(results_dir, snaps, checkpoints, n_seeds)
    write_tables(results_dir, rd, S, checkpoints, n_seeds, cons_ok, repro_ok)
    make_initial_picture(figures_dir, initial_worlds)
    make_reader_figure(figures_dir, rd, S, checkpoints)
    console_summary(S, checkpoints)
    print(f"\nWrote results/ and figures/ under {args.outdir}")


def construction_checks(results_dir, W, T):
    lines = ["# v6 construction invariant checks"]
    ok = True

    def rec(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        lines.append(f"[{'PASS' if cond else 'FAIL'}] {name}")

    # diagonals all weight 1 in initial states
    for hk, Tset in (("A", T["A"]), ("B", T["B"])):
        # reconstruct to read diagonal weights
        w = build_intact("upper" if hk == "A" else "lower")
        rec(f"history {hk}: all activated diagonals weight 1",
            all(w.weight[e] == 1.0 for e in w.active))
    rec("|T_A| == |T_B|", len(T["A"]) == len(T["B"]))
    rec("multiset(W_A) == multiset(W_B)",
        sorted(W["A"].values()) == sorted(W["B"].values()))

    worlds = {k: build_world(k[0], k[1], W, T) for k in WORLD_KEYS}
    ecounts = {k: len(w.weight) for k, w in worlds.items()}
    tweights = {k: sum(w.weight.values()) for k, w in worlds.items()}
    rec("all four identical initial edge count", len(set(ecounts.values())) == 1)
    rec("all four identical initial total weight",
        max(tweights.values()) - min(tweights.values()) < 1e-9)
    # original-edge weight multiset identical across all four
    base_ms = {k: sorted(worlds[k].weight[e] for e in worlds[k].base_edge_set)
               for k in WORLD_KEYS}
    ref = base_ms[("A", "A")]
    rec("all four identical original-edge weight multiset",
        all(base_ms[k] == ref for k in WORLD_KEYS))
    # initial four-traversal bits all zero
    zero_bits = all(readers(vec_of(worlds[k]))["S_high"] == 0.0 for k in WORLD_KEYS)
    rec("all four initial S_high (four-traversal bits) == 0", zero_bits)
    lines.append(f"# edge_count={list(ecounts.values())[0]}, "
                 f"total_weight={list(tweights.values())[0]:.4f}, "
                 f"|T_A|={len(T['A'])}, |T_B|={len(T['B'])}")
    with open(os.path.join(results_dir, "construction_checks.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return ok


def validate_vs_v4(results_dir, snaps, checkpoints):
    lines = ["# v6 intact worlds reproduce v2/v5 (vs v4 edge_snapshots.npz)"]
    ok = True
    if not os.path.exists(_V4NPZ):
        lines.append(f"# v4 npz not found: {_V4NPZ}"); ok = False
    else:
        z = np.load(_V4NPZ)
        maxd = 0.0; n = 0
        for k, hl in ((("A", "A"), "A"), (("B", "B"), "B")):
            for cp in checkpoints:
                key = f"Growing__{hl}__{cp}"
                if key not in z:
                    continue
                ref = z[key]
                got = snaps[k][cp]
                m = min(len(ref), len(got))
                maxd = max(maxd, float(np.abs(ref[:m] - got[:m]).max())); n += m
        ok = maxd < 1e-9
        lines.append(f"# compared {n} intact per-seed snapshots; max|dw| = {maxd:.3e}; "
                     f"tol 1e-9; status = {'PASS' if ok else 'FAIL'}")
    lines.append(f"# overall: {'PASS' if ok else 'CHECK'}")
    with open(os.path.join(results_dir, "validation_vs_v4.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    return ok


def save_snapshots(results_dir, snaps, checkpoints, n_seeds):
    arrays = {"universe_u": np.array([e[0] for e in UNIVERSE]),
              "universe_v": np.array([e[1] for e in UNIVERSE]),
              "is_added": IS_ADDED, "signs": SIGNS,
              "checkpoints": np.array(checkpoints), "n_seeds": np.array(n_seeds)}
    for k in WORLD_KEYS:
        tag = f"{k[0]}{k[1]}"
        for cp in checkpoints:
            arrays[f"W{k[0]}_T{k[1]}__{cp}"] = snaps[k][cp]
    path = os.path.join(results_dir, "edge_snapshots_v6.npz")
    np.savez_compressed(path, **arrays)
    print(f"Retained edge snapshots -> {os.path.basename(path)} "
          f"({os.path.getsize(path) / 1e6:.1f} MB)")


def write_tables(results_dir, rd, S, checkpoints, n_seeds, cons_ok, repro_ok):
    # per-world summary of readers over time
    keys = ["S_high", "P_D", "B0", "edge_count", "total_weight", "headroom",
            "n_active_diag"]
    rows = ["world,checkpoint," + ",".join(f"{k}_mean" for k in keys)
            + ",S_high_sd"]
    for k in WORLD_KEYS:
        for cp in checkpoints:
            arr = rd[k][cp]
            means = {kk: np.mean([r[kk] for r in arr]) for kk in keys}
            ssd = np.std([r["S_high"] for r in arr], ddof=1)
            rows.append(f"{k[0]}{k[1]},{cp}," +
                        ",".join(f"{means[kk]:.4f}" for kk in keys) +
                        f",{ssd:.4f}")
    with open(os.path.join(results_dir, "summary_worlds.csv"), "w") as f:
        f.write("\n".join(rows) + "\n")

    # factor contrasts
    fc = ["contrast,checkpoint,mean_diff_Shigh,diff_lo,diff_hi,auc,auc_lo,auc_hi"]
    defs = [("weight_effect|T_A", ("A", "A"), ("B", "A")),
            ("weight_effect|T_B", ("A", "B"), ("B", "B")),
            ("topology_effect|W_A", ("A", "A"), ("A", "B")),
            ("topology_effect|W_B", ("B", "A"), ("B", "B"))]
    for cp in [c for c in BOOT_CPS if c in checkpoints]:
        for name, pos, neg in defs:
            r = contrast(S, pos, neg, cp)
            fc.append(f"{name},{cp},{r['mean_diff']:.4f},{r['d_lo']:.4f},"
                      f"{r['d_hi']:.4f},{r['auc']:.4f},{r['auc_lo']:.4f},"
                      f"{r['auc_hi']:.4f}")
        it = interaction(S, cp)
        fc.append(f"interaction_meanShigh,{cp},{it['mean']:.4f},{it['lo']:.4f},"
                  f"{it['hi']:.4f},NA,NA,NA")
    with open(os.path.join(results_dir, "factor_contrasts.csv"), "w") as f:
        f.write("\n".join(fc) + "\n")

    cfg = {"worlds": {f"{k[0]}{k[1]}": WORLD_LABEL[k] for k in WORLD_KEYS},
           "primary_reader": "S_high = sum s(e) 1[w>=5.5] over added diagonals "
                             "(v5, A-positive, frozen)",
           "intervention": "initial conditions only; movement/reinforcement/growth "
                           "rules unchanged from v2",
           "construction_order": "intact = history-activation order; crossed = base "
                                 "then diagonals in sorted edge-key order",
           "checkpoints": list(checkpoints), "n_seeds": n_seeds,
           "construction_checks": "PASS" if cons_ok else "FAIL",
           "reproduction_vs_v4": "PASS" if repro_ok else "CHECK",
           "env": {"python": sys.version.split()[0], "numpy": np.__version__}}
    with open(os.path.join(results_dir, "config.json"), "w") as f:
        json.dump(cfg, f, indent=2)

    # late completeness (reported separately; NOT dropped from comparisons)
    cp = max(checkpoints)
    cl = ["# Late (t=%d) topology completeness per world (reported, not dropped)." % cp,
          "world,n_worlds,n_complete_128,total_missing_diagonals"]
    for k in WORLD_KEYS:
        na = np.array([r["n_active_diag"] for r in rd[k][cp]])
        cl.append(f"{k[0]}{k[1]},{len(na)},{int((na == 128).sum())},"
                  f"{int((128 - na).sum())}")
    with open(os.path.join(results_dir, "late_completeness.txt"), "w") as f:
        f.write("\n".join(cl) + "\n")


def make_initial_picture(figures_dir, worlds):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def draw(ax, world):
        for e, w in world.weight.items():
            (ra, ca), (rb, cb) = v2.rc(e[0]), v2.rc(e[1])
            is_diag = e in world.active
            color = "#ff7f0e" if is_diag else "#bbbbbb"
            if is_diag:
                lw = 1.3
            else:
                lw = max(0.4, min(0.5 + 2.4 * (w - 1.0) / (W_MAX - 1.0), 4.0))
            ax.plot([ca, cb], [-ra, -rb], "-", color=color, lw=lw,
                    zorder=3 if is_diag else 1, solid_capstyle="round")
        pr, pc = PROBE
        ax.plot([pc], [-pr], "s", color="black", markersize=7, zorder=5)
        ax.set_aspect("equal"); ax.axis("off")

    fig, axes = plt.subplots(2, 2, figsize=(11, 11))
    order = [("A", "A"), ("A", "B"), ("B", "A"), ("B", "B")]
    for ax, k in zip(axes.flat, order):
        draw(ax, worlds[k])
        ax.set_title(WORLD_LABEL[k], fontsize=11)
    fig.suptitle("v6 four worlds immediately after construction (before wandering)\n"
                 "base edges grey (width ~ weight), diagonals orange, probe black.\n"
                 "Identical edge count / total weight / original-weight multiset; "
                 "arrangement differs.", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(os.path.join(figures_dir, "four_worlds_initial_v6.png"), dpi=140)
    plt.close(fig)


def make_reader_figure(figures_dir, rd, S, checkpoints):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cps = list(checkpoints)
    col = {("A", "A"): "#d62728", ("A", "B"): "#ff7f0e",
           ("B", "A"): "#2ca02c", ("B", "B"): "#1f77b4"}

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    ax = axes[0]
    for k in WORLD_KEYS:
        means = np.array([S[k][cp].mean() for cp in cps])
        sds = np.array([S[k][cp].std(ddof=1) for cp in cps])
        ax.plot(cps, means, "-o", color=col[k], label=WORLD_LABEL[k])
        ax.fill_between(cps, means - sds, means + sds, color=col[k], alpha=0.12)
    ax.axhline(0.0, ls="--", color="k", lw=0.8)
    ax.set_xscale("symlog")
    ax.set_title("Primary reader S_high (added-diagonal 4-traversal contrast)\n"
                 "mean +/- sd over 200 seeds; A-positive")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("mean S_high")
    ax.legend(fontsize=8)

    ax = axes[1]
    names = [("weight|T_A", ("A", "A"), ("B", "A")),
             ("weight|T_B", ("A", "B"), ("B", "B")),
             ("topo|W_A", ("A", "A"), ("A", "B")),
             ("topo|W_B", ("B", "A"), ("B", "B"))]
    bcps = [c for c in BOOT_CPS if c in checkpoints]
    x = np.arange(len(names) + 1)
    width = 0.8 / len(bcps)
    cpcol = {400: "#8c564b", 2000: "#e377c2", 10000: "#17becf"}
    for j, cp in enumerate(bcps):
        vals, los, his = [], [], []
        for _, pos, neg in names:
            r = contrast(S, pos, neg, cp)
            vals.append(r["mean_diff"]); los.append(r["mean_diff"] - r["d_lo"])
            his.append(r["d_hi"] - r["mean_diff"])
        it = interaction(S, cp)
        vals.append(it["mean"]); los.append(it["mean"] - it["lo"])
        his.append(it["hi"] - it["mean"])
        ax.bar(x + j * width, vals, width, yerr=[los, his], capsize=3,
               color=cpcol[cp], label=f"t={cp}", alpha=0.85)
    ax.axhline(0.0, color="k", lw=0.8)
    ax.set_xticks(x + width * (len(bcps) - 1) / 2)
    ax.set_xticklabels([n[0] for n in names] + ["interaction"], fontsize=8, rotation=15)
    ax.set_title("Factor effects on mean S_high (paired diff, seed-block bootstrap 95% CI)")
    ax.set_ylabel("mean difference in S_high"); ax.legend(fontsize=8)

    fig.suptitle("v6 intervention: does the late 4-traversal footprint follow "
                 "original-edge weights (W) or diagonal placement (T)?", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(figures_dir, "reader_over_time_v6.png"), dpi=140)
    plt.close(fig)


def console_summary(S, checkpoints):
    print("=" * 78)
    print("v6 mean S_high by world:")
    for cp in (400, 2000, 10000):
        if cp not in checkpoints:
            continue
        parts = "  ".join(f"{k[0]}{k[1]}={S[k][cp].mean():7.3f}" for k in WORLD_KEYS)
        print(f"  t={cp:5d}: {parts}")
    print("- factor effects (mean S_high diff) at t=10000:")
    for name, pos, neg in [("weight|T_A", ("A", "A"), ("B", "A")),
                           ("weight|T_B", ("A", "B"), ("B", "B")),
                           ("topo|W_A", ("A", "A"), ("A", "B")),
                           ("topo|W_B", ("B", "A"), ("B", "B"))]:
        if 10000 in checkpoints:
            r = contrast(S, pos, neg, 10000)
            print(f"    {name:12s} {r['mean_diff']:+7.3f} [{r['d_lo']:+.3f},"
                  f"{r['d_hi']:+.3f}]  AUC {r['auc']:.3f}")
    if 10000 in checkpoints:
        it = interaction(S, 10000)
        print(f"    interaction  {it['mean']:+7.3f} [{it['lo']:+.3f},{it['hi']:+.3f}]")
    print("=" * 78)


if __name__ == "__main__":
    main()

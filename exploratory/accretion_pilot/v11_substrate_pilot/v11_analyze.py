#!/usr/bin/env python3
"""
v11_analyze.py -- analysis of the v11 substrate experiment (reads raw_main.csv,
raw_null.csv). Primary discrimination = ordinary fixed-orientation AUC per cell;
within-seed ordering probability secondary. Per-patch equal weight (average the 3
pairs first), then per-arm. Seed-pair bootstrap within cells. Null uses
dynamics-independent random A/B labels. Family comparisons exploratory.
"""
from __future__ import annotations

import csv
import json
import os
from collections import defaultdict

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(_HERE, "results")
FIG = os.path.join(_HERE, "figures")
os.makedirs(FIG, exist_ok=True)
CPS = [0, 100, 200, 400, 1000, 2000, 5000, 10000]
PRIMARY = 2000
ARMS = ["regular", "perturbed"]
OPP = ["frac_active", "headroom", "struct_access", "eff_alt", "bvisit_frac"]


def auc(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    allv = np.concatenate([a, b])
    order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv)); ranks[order] = np.arange(1, len(allv) + 1)
    _, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    s = np.zeros(len(cnt)); np.add.at(s, inv, ranks); ranks = (s / cnt)[inv]
    nA = len(a)
    return float((ranks[:nA].sum() - nA * (nA + 1) / 2) / (nA * len(b)))


def within_seed(a, b):
    d = np.asarray(a, float) - np.asarray(b, float)
    return float(np.mean((d > 0) * 1.0 + (d == 0) * 0.5))


def boot_auc(a, b, n=2000, seed=7):
    a, b = np.asarray(a, float), np.asarray(b, float)
    rng = np.random.default_rng(seed); m = len(a)
    bs = np.empty(n)
    for k in range(n):
        idx = rng.integers(0, m, m)
        bs[k] = auc(a[idx], b[idx])
    return auc(a, b), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def load_main():
    # S[(arm,i,pair,cp,hist)][seed] = S_high ; also opportunity accum
    S = defaultdict(dict)
    opp = defaultdict(lambda: defaultdict(list))     # (arm,cp,metric)->list
    with open(os.path.join(RES, "raw_main.csv")) as f:
        for r in csv.DictReader(f):
            key = (r["arm"], int(r["patch"]), int(r["pair"]), int(r["checkpoint"]),
                   r["history"])
            S[key][int(r["seed"])] = float(r["S_high"])
            cp = int(r["checkpoint"])
            for m in OPP:
                opp[(r["arm"], cp, m)].append(float(r[m]))
    return S, opp


def load_null():
    N = defaultdict(dict)     # (arm,i,pair,cp)->{seed:S_high}
    with open(os.path.join(RES, "raw_null.csv")) as f:
        for r in csv.DictReader(f):
            key = (r["arm"], int(r["patch"]), int(r["pair"]), int(r["checkpoint"]))
            N[key][int(r["seed"])] = float(r["S_high"])
    return N


def cell_arrays(S, arm, i, pair, cp):
    A = S.get((arm, i, pair, cp, "A"), {})
    B = S.get((arm, i, pair, cp, "B"), {})
    seeds = sorted(set(A) & set(B))
    return np.array([A[s] for s in seeds]), np.array([B[s] for s in seeds])


def main():
    S, opp = load_main()
    N = load_null()
    patches = sorted(set((a, i) for (a, i, *_r) in S.keys()))
    npairs = 1 + max(p for (_a, _i, p, *_r) in S.keys())

    # ---- per-cell memory table ----
    rows = ["arm,patch,pair,checkpoint,auc,auc_lo,auc_hi,within_seed,"
            "mean_A,mean_B,n_seeds"]
    cell_auc = defaultdict(dict)     # (arm,i,pair)->cp->auc
    for (arm, i) in patches:
        for pair in range(npairs):
            for cp in CPS:
                a, b = cell_arrays(S, arm, i, pair, cp)
                if len(a) == 0:
                    continue
                if cp in (400, PRIMARY, 10000):
                    au, lo, hi = boot_auc(a, b, seed=100 + cp)
                else:
                    au, lo, hi = auc(a, b), float("nan"), float("nan")
                cell_auc[(arm, i, pair)][cp] = au
                rows.append(f"{arm},{i},{pair},{cp},{au:.4f},{lo:.4f},{hi:.4f},"
                            f"{within_seed(a,b):.4f},{a.mean():.4f},{b.mean():.4f},"
                            f"{len(a)}")
    with open(os.path.join(RES, "summary_memory_cells.csv"), "w") as f:
        f.write("\n".join(rows) + "\n")

    # ---- patch- and arm-level aggregates (equal weight; avg pairs then patches) ----
    agg = ["level,arm,patch,checkpoint,auc_mean,auc_spread_note"]
    arm_curve = {arm: {} for arm in ARMS}
    for arm in ARMS:
        pts = [i for (a, i) in patches if a == arm]
        for cp in CPS:
            patch_means = []
            for i in pts:
                pair_aucs = [cell_auc[(arm, i, pair)][cp] for pair in range(npairs)
                             if cp in cell_auc[(arm, i, pair)]]
                pm = float(np.mean(pair_aucs))
                patch_means.append(pm)
                agg.append(f"patch,{arm},{i},{cp},{pm:.4f},avg_of_{len(pair_aucs)}_pairs")
            arm_mean = float(np.mean(patch_means))
            arm_sd = float(np.std(patch_means, ddof=1)) if len(patch_means) > 1 else 0.0
            arm_curve[arm][cp] = (arm_mean, arm_sd, patch_means)
            agg.append(f"arm,{arm},all,{cp},{arm_mean:.4f},sd_across_patches={arm_sd:.4f}")
    with open(os.path.join(RES, "summary_memory_arms.csv"), "w") as f:
        f.write("\n".join(agg) + "\n")

    # ---- null (random dynamics-independent labels) ----
    nrows = ["arm,patch,pair,checkpoint,null_auc"]
    null_curve = {arm: defaultdict(list) for arm in ARMS}
    rng = np.random.default_rng(999)
    for (arm, i) in patches:
        for pair in range(npairs):
            for cp in CPS:
                d = N.get((arm, i, pair, cp), {})
                seeds = sorted(d)
                if not seeds:
                    continue
                vals = np.array([d[s] for s in seeds])
                lab = rng.integers(0, 2, len(vals))       # labels independent of dynamics
                if lab.sum() == 0 or lab.sum() == len(vals):
                    lab[0] = 1 - lab[0]
                na = auc(vals[lab == 1], vals[lab == 0])
                null_curve[arm][cp].append(na)
                nrows.append(f"{arm},{i},{pair},{cp},{na:.4f}")
    with open(os.path.join(RES, "summary_null.csv"), "w") as f:
        f.write("\n".join(nrows) + "\n")

    # ---- opportunity/capacity ----
    orows = ["arm,checkpoint," + ",".join(f"{m}_mean" for m in OPP)]
    opp_curve = {arm: {m: [] for m in OPP} for arm in ARMS}
    for arm in ARMS:
        for cp in CPS:
            vals = [np.mean(opp[(arm, cp, m)]) for m in OPP]
            for m, v in zip(OPP, vals):
                opp_curve[arm][m].append(v)
            orows.append(f"{arm},{cp}," + ",".join(f"{v:.4f}" for v in vals))
    with open(os.path.join(RES, "summary_opportunity.csv"), "w") as f:
        f.write("\n".join(orows) + "\n")

    make_figures(arm_curve, cell_auc, null_curve, opp_curve, patches, npairs, S)
    console(arm_curve, null_curve)


def make_figures(arm_curve, cell_auc, null_curve, opp_curve, patches, npairs, S):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    col = {"regular": "#d62728", "perturbed": "#1f77b4"}

    # Figure 1: memory
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.2))
    ax = axes[0]
    for arm in ARMS:
        m = [arm_curve[arm][cp][0] for cp in CPS]
        sd = [arm_curve[arm][cp][1] for cp in CPS]
        ax.plot(CPS, m, "-o", color=col[arm], label=f"{arm} (arm mean)")
        ax.fill_between(CPS, np.array(m) - sd, np.array(m) + sd, color=col[arm], alpha=0.15)
        for (a, i) in patches:
            if a != arm:
                continue
            pm = [np.mean([cell_auc[(arm, i, p)][cp] for p in range(npairs)]) for cp in CPS]
            ax.plot(CPS, pm, "-", color=col[arm], lw=0.6, alpha=0.4)
    ax.axhline(0.5, ls="--", color="k", lw=0.8); ax.axvline(PRIMARY, ls=":", color="grey")
    ax.set_xscale("symlog"); ax.set_ylim(0.4, 1.02)
    ax.set_title("Memory: ordinary AUC (A vs B) over time\narm mean +/- across-patch sd; "
                 "thin = patches; primary t=2000")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("AUC"); ax.legend(fontsize=8)

    ax = axes[1]
    for arm in ARMS:
        wm = []
        for cp in CPS:
            vals = []
            for (a, i) in patches:
                if a != arm:
                    continue
                for p in range(npairs):
                    aa, bb = cell_arrays(S, arm, i, p, cp)
                    if len(aa):
                        vals.append(within_seed(aa, bb))
            wm.append(np.mean(vals))
        ax.plot(CPS, wm, "-o", color=col[arm], label=arm)
    ax.axhline(0.5, ls="--", color="k", lw=0.8)
    ax.set_xscale("symlog"); ax.set_ylim(0.4, 1.02)
    ax.set_title("Secondary: within-seed ordering probability\n(CRN-coupled; not the "
                 "primary measure)")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("frac(A>B)"); ax.legend(fontsize=8)

    ax = axes[2]
    for arm in ARMS:
        nm = [np.mean(null_curve[arm][cp]) for cp in CPS]
        ax.plot(CPS, nm, "-o", color=col[arm], label=f"{arm} null")
    ax.axhline(0.5, ls="--", color="k", lw=0.8)
    ax.set_xscale("symlog"); ax.set_ylim(0.4, 1.02)
    ax.set_title("No-history null (random labels)\nshould sit at chance")
    ax.set_xlabel("subsequent step (symlog)"); ax.set_ylabel("null AUC"); ax.legend(fontsize=8)
    fig.suptitle("v11 substrate pilot: history discrimination (regular Penrose vs "
                 "perturbed pentagrid) -- exploratory, conditional on these geometries",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(FIG, "memory_v11.png"), dpi=140); plt.close(fig)

    # Figure 2: opportunity/capacity
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    titles = {"frac_active": "activation fraction", "headroom": "mean headroom (6-w)",
              "struct_access": "structural access (4-hop)",
              "eff_alt": "effective alternatives exp(H)",
              "bvisit_frac": "boundary visitation fraction"}
    for ax, m in zip(axes.flat, OPP):
        for arm in ARMS:
            ax.plot(CPS, opp_curve[arm][m], "-o", color=col[arm], label=arm)
        ax.set_xscale("symlog"); ax.set_title(titles[m]); ax.set_xlabel("step (symlog)")
        ax.legend(fontsize=8)
    axes.flat[-1].axis("off")
    fig.suptitle("v11 opportunity / capacity / boundary (reported separately from "
                 "memory; substrates differ locally)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(FIG, "opportunity_v11.png"), dpi=140); plt.close(fig)


def console(arm_curve, null_curve):
    print("=" * 74)
    print("v11 memory (ordinary AUC, arm mean +/- across-patch sd):")
    for arm in ARMS:
        print(f"  {arm:10s} " + "  ".join(
            f"t={cp}:{arm_curve[arm][cp][0]:.3f}" +
            (f"[PRIMARY]" if cp == PRIMARY else "") for cp in CPS))
    print(f"  primary t={PRIMARY}: regular {arm_curve['regular'][PRIMARY][0]:.3f} "
          f"(patches {[round(x,3) for x in arm_curve['regular'][PRIMARY][2]]}), "
          f"perturbed {arm_curve['perturbed'][PRIMARY][0]:.3f} "
          f"(patches {[round(x,3) for x in arm_curve['perturbed'][PRIMARY][2]]})")
    print("null at primary:", {arm: round(np.mean(null_curve[arm][PRIMARY]), 3)
                               for arm in ARMS})
    print("=" * 74)


if __name__ == "__main__":
    main()

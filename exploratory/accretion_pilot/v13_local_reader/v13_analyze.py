#!/usr/bin/env python3
"""
v13_analyze.py -- analysis of the local-reader pilot (reads visitor_scores.csv,
visitor_null.csv). Primary = per-cell ordinary AUC at B=300 for a SINGLE visitor,
estimated by averaging AUC over the 5 visitor replicates. Global comparator on the
same worlds; local-minus-global reported. Aggregate: average 3 pairs per patch, then
3 patches per arm. Bootstrap whole evolution-seed blocks (shared across cells).
"""
from __future__ import annotations
import csv, os
from collections import defaultdict
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(_HERE, "results")
FIG = os.path.join(_HERE, "figures")
os.makedirs(FIG, exist_ok=True)
BUD = [100, 300, 1000]; PRIMARY = 300; ARMS = ["regular", "perturbed"]
NSEED = 50; REPS = 5


def auc(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    allv = np.concatenate([a, b]); order = allv.argsort(kind="mergesort")
    ranks = np.empty(len(allv)); ranks[order] = np.arange(1, len(allv) + 1)
    _, inv, cnt = np.unique(allv, return_inverse=True, return_counts=True)
    s = np.zeros(len(cnt)); np.add.at(s, inv, ranks); ranks = (s / cnt)[inv]
    nA = len(a)
    return float((ranks[:nA].sum() - nA * (nA + 1) / 2) / (nA * len(b)))


def load():
    # loc[(arm,i,pair,B,rep,hist)][seed]=S_local ; glob[(arm,i,pair,hist)][seed]=global
    loc = defaultdict(dict); glob = defaultdict(dict)
    cover = defaultdict(list)   # (arm,B) -> [(frac_present,frac_high)]
    with open(os.path.join(RES, "visitor_scores.csv")) as f:
        for r in csv.DictReader(f):
            arm = r["arm"]; i = int(r["patch"]); p = int(r["pair"]); h = r["history"]
            B = int(r["budget"]); rep = int(r["replicate"]); sd = int(r["seed"])
            loc[(arm, i, p, B, rep, h)][sd] = float(r["S_local"])
            glob[(arm, i, p, h)][sd] = float(r["global_S_high"])
            cover[(arm, B)].append((float(r["frac_present"]), float(r["frac_high_seen"])))
    null = defaultdict(dict)    # (arm,i,pair,B,rep)->{seed:score}
    with open(os.path.join(RES, "visitor_null.csv")) as f:
        for r in csv.DictReader(f):
            null[(r["arm"], int(r["patch"]), int(r["pair"]), int(r["budget"]),
                  int(r["replicate"]))][int(r["seed"])] = float(r["S_local_null"])
    return loc, glob, cover, null


def cell_local_auc(loc, arm, i, p, B, idx):
    aucs = []
    for rep in range(REPS):
        A = loc[(arm, i, p, B, rep, "A")]; Bd = loc[(arm, i, p, B, rep, "B")]
        seeds = sorted(set(A) & set(Bd))
        a = np.array([A[s] for s in seeds])[idx]; b = np.array([Bd[s] for s in seeds])[idx]
        aucs.append(auc(a, b))
    return float(np.mean(aucs))


def cell_global_auc(glob, arm, i, p, idx):
    A = glob[(arm, i, p, "A")]; Bd = glob[(arm, i, p, "B")]
    seeds = sorted(set(A) & set(Bd))
    return auc(np.array([A[s] for s in seeds])[idx], np.array([Bd[s] for s in seeds])[idx])


def arm_local(loc, arm, B, idx):
    return float(np.mean([np.mean([cell_local_auc(loc, arm, i, p, B, idx)
                                   for p in range(3)]) for i in range(3)]))


def arm_global(glob, arm, idx):
    return float(np.mean([np.mean([cell_global_auc(glob, arm, i, p, idx)
                                   for p in range(3)]) for i in range(3)]))


def main():
    loc, glob, cover, null = load()
    base = np.arange(NSEED)

    # ---- per-cell table ----
    rows = ["arm,patch,pair,budget,local_auc,global_auc,local_minus_global"]
    for arm in ARMS:
        for i in range(3):
            for p in range(3):
                g = cell_global_auc(glob, arm, i, p, base)
                for B in BUD:
                    la = cell_local_auc(loc, arm, i, p, B, base)
                    rows.append(f"{arm},{i},{p},{B},{la:.4f},{g:.4f},{la-g:.4f}")
    open(os.path.join(RES, "local_cells.csv"), "w").write("\n".join(rows) + "\n")

    # ---- arm curves + seed bootstrap (shared across cells) ----
    rng = np.random.default_rng(4242); NB = 2000
    arm_curit = {arm: {} for arm in ARMS}
    for arm in ARMS:
        for B in BUD:
            pt = arm_local(loc, arm, B, base)
            bs = np.array([arm_local(loc, arm, B, rng.integers(0, NSEED, NSEED))
                           for _ in range(NB)])
            arm_curit[arm][B] = (pt, float(np.percentile(bs, 2.5)),
                                 float(np.percentile(bs, 97.5)))
        g = arm_global(glob, arm, base)
        rng2 = np.random.default_rng(99)
        gbs = np.array([arm_global(glob, arm, rng2.integers(0, NSEED, NSEED))
                        for _ in range(NB)])
        arm_curit[arm]["global"] = (g, float(np.percentile(gbs, 2.5)),
                                    float(np.percentile(gbs, 97.5)))
        # local-minus-global at primary with shared resample
        rng3 = np.random.default_rng(7)
        d = np.array([arm_local(loc, arm, PRIMARY, ii := rng3.integers(0, NSEED, NSEED))
                      - arm_global(glob, arm, ii) for _ in range(NB)])
        pt_d = arm_local(loc, arm, PRIMARY, base) - g
        arm_curit[arm]["diff300"] = (pt_d, float(np.percentile(d, 2.5)),
                                     float(np.percentile(d, 97.5)))

    arows = ["arm,quantity,point,ci_lo,ci_hi"]
    for arm in ARMS:
        for B in BUD:
            v = arm_curit[arm][B]; arows.append(f"{arm},local_auc_B{B},{v[0]:.4f},{v[1]:.4f},{v[2]:.4f}")
        for q in ("global", "diff300"):
            v = arm_curit[arm][q]; arows.append(f"{arm},{q},{v[0]:.4f},{v[1]:.4f},{v[2]:.4f}")
    open(os.path.join(RES, "local_arms.csv"), "w").write("\n".join(arows) + "\n")

    # ---- null (fixed random labels per (patch,seed)) ----
    lbl_rng = np.random.default_rng(1234)
    labels = {}
    for arm in ARMS:
        for i in range(3):
            for sd in range(NSEED):
                labels[(arm, i, sd)] = int(lbl_rng.integers(0, 2))
    nrows = ["arm,budget,null_auc_mean"]
    null_curve = {arm: {} for arm in ARMS}
    for arm in ARMS:
        for B in BUD:
            per_patch = []
            for i in range(3):
                per_pair = []
                for p in range(3):
                    aucs = []
                    for rep in range(REPS):
                        d = null[(arm, i, p, B, rep)]
                        seeds = sorted(d)
                        A = [d[s] for s in seeds if labels[(arm, i, s)] == 0]
                        Bd = [d[s] for s in seeds if labels[(arm, i, s)] == 1]
                        aucs.append(auc(A, Bd))
                    per_pair.append(np.nanmean(aucs))
                per_patch.append(np.mean(per_pair))
            null_curve[arm][B] = float(np.mean(per_patch))
            nrows.append(f"{arm},{B},{null_curve[arm][B]:.4f}")
    open(os.path.join(RES, "local_null.csv"), "w").write("\n".join(nrows) + "\n")

    # ---- coverage ----
    crows = ["arm,budget,frac_present_mean,frac_high_seen_mean"]
    covmean = {arm: {} for arm in ARMS}
    for arm in ARMS:
        for B in BUD:
            fp = np.mean([x[0] for x in cover[(arm, B)]])
            fh = np.mean([x[1] for x in cover[(arm, B)]])
            covmean[arm][B] = (fp, fh)
            crows.append(f"{arm},{B},{fp:.4f},{fh:.4f}")
    open(os.path.join(RES, "local_coverage.csv"), "w").write("\n".join(crows) + "\n")

    make_fig(arm_curit, null_curve, covmean)
    console(arm_curit, null_curve, covmean)


def make_fig(arm_curit, null_curve, covmean):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    col = {"regular": "#d62728", "perturbed": "#1f77b4"}
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.2))
    ax = axes[0]
    for arm in ARMS:
        ys = [arm_curit[arm][B][0] for B in BUD]
        lo = [arm_curit[arm][B][0] - arm_curit[arm][B][1] for B in BUD]
        hi = [arm_curit[arm][B][2] - arm_curit[arm][B][0] for B in BUD]
        ax.errorbar(BUD, ys, yerr=[lo, hi], fmt="-o", color=col[arm], capsize=3,
                    label=f"{arm} local")
        g = arm_curit[arm]["global"][0]
        ax.axhline(g, ls="--", color=col[arm], lw=1, alpha=0.7,
                   label=f"{arm} global={g:.2f}")
        ax.plot(BUD, [null_curve[arm][B] for B in BUD], ":", color=col[arm], alpha=0.6)
    ax.axhline(0.5, ls="-", color="k", lw=0.6)
    ax.set_xscale("log"); ax.set_ylim(0.45, 0.75); ax.set_xlabel("visitor budget (steps)")
    ax.set_ylabel("AUC"); ax.set_title("Local tagged reader AUC vs budget\n(dashed=global on same worlds; dotted=null; primary B=300)")
    ax.legend(fontsize=7)
    ax = axes[1]
    for arm in ARMS:
        ax.plot(BUD, [covmean[arm][B][0] for B in BUD], "-o", color=col[arm], label=f"{arm} frac present diag seen")
        ax.plot(BUD, [covmean[arm][B][1] for B in BUD], "--s", color=col[arm], alpha=0.7, label=f"{arm} frac HIGH diag seen")
    ax.set_xscale("log"); ax.set_ylim(0, 1.05); ax.set_xlabel("visitor budget (steps)")
    ax.set_ylabel("fraction encountered"); ax.set_title("Coverage vs budget")
    ax.legend(fontsize=7)
    ax = axes[2]
    for arm in ARMS:
        v = arm_curit[arm]["diff300"]
        ax.bar(arm, v[0], yerr=[[v[0]-v[1]], [v[2]-v[0]]], color=col[arm], capsize=4, alpha=0.85)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_title("local(B=300) - global  (same worlds)\nseed-bootstrap 95% CI")
    ax.set_ylabel("AUC difference")
    fig.suptitle("v13 passive tagged local reader on frozen t=2000 worlds -- "
                 "aided observational accessibility (not autonomous use)", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(FIG, "local_reader_v13.png"), dpi=140); plt.close(fig)


def console(arm_curit, null_curve, covmean):
    print("=" * 74)
    for arm in ARMS:
        print(f"{arm}: " + "  ".join(
            f"B{B}:{arm_curit[arm][B][0]:.3f}[{arm_curit[arm][B][1]:.3f},{arm_curit[arm][B][2]:.3f}]"
            for B in BUD) + f"  global:{arm_curit[arm]['global'][0]:.3f}")
        print(f"    null: " + " ".join(f"B{B}:{null_curve[arm][B]:.3f}" for B in BUD) +
              f"  | coverage@300 present={covmean[arm][300][0]:.2f} high={covmean[arm][300][1]:.2f}"
              f"  | local-global@300 {arm_curit[arm]['diff300'][0]:+.3f} "
              f"[{arm_curit[arm]['diff300'][1]:+.3f},{arm_curit[arm]['diff300'][2]:+.3f}]")
    print("=" * 74)


if __name__ == "__main__":
    main()

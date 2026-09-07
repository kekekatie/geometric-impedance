#!/usr/bin/env python3
"""
v14_analyze.py -- distant-start vs original-start discrimination on the retained v13
worlds. Primary = per-cell ordinary AUC at B=300 for a single visitor, AUC computed per
replicate then averaged. Report distant-start minus original-start AUC with an
evolution-seed-block bootstrap shared across cells (preserving histories, starts, visits,
dependence). Aggregate 3 pairs within a patch, then 3 patches equally, per arm. Coverage
and arrival reported descriptively; the primary comparison is NOT conditioned on arrival.
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
NSEED = 50; REPS = 5; STARTS = ["orig", "distant"]


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
    # loc[(start,arm,i,p,B,rep,hist)][seed]=S_local ; glob[(arm,i,p,hist)][seed]=global
    loc = defaultdict(dict); glob = defaultdict(dict)
    cover = defaultdict(list)     # (start,arm,B)->[(fp,fh)]
    arrive = defaultdict(list)    # (start,arm,B)->[arrived bool]; astep list
    astep = defaultdict(list)     # (start,arm)->[arrival_step (>=0) among reached]
    have_distant = set()
    with open(os.path.join(RES, "scores_main.csv")) as f:
        for r in csv.DictReader(f):
            st = r["start"]; arm = r["arm"]; i = int(r["patch"]); p = int(r["pair"])
            h = r["history"]; B = int(r["budget"]); rep = int(r["replicate"])
            sd = int(r["seed"])
            loc[(st, arm, i, p, B, rep, h)][sd] = float(r["S_local"])
            if st == "orig":
                glob[(arm, i, p, h)][sd] = float(r["global_S_high"])
            if st == "distant":
                have_distant.add((arm, i, p))
            cover[(st, arm, B)].append((float(r["frac_present"]), float(r["frac_high_seen"])))
            arrive[(st, arm, B)].append(int(r["arrived"]))
            if B == max(BUD):
                stp = int(r["arrival_step"])
                if stp >= 0:
                    astep[(st, arm)].append(stp)
    null = defaultdict(dict)
    with open(os.path.join(RES, "scores_null.csv")) as f:
        for r in csv.DictReader(f):
            null[(r["start"], r["arm"], int(r["patch"]), int(r["pair"]),
                  int(r["budget"]), int(r["replicate"]))][int(r["seed"])] = \
                float(r["S_local_null"])
    return loc, glob, cover, arrive, astep, null, have_distant


def cell_local_auc(loc, st, arm, i, p, B, idx):
    aucs = []
    for rep in range(REPS):
        A = loc[(st, arm, i, p, B, rep, "A")]; Bd = loc[(st, arm, i, p, B, rep, "B")]
        seeds = sorted(set(A) & set(Bd))
        if not seeds:
            return float("nan")
        a = np.array([A[s] for s in seeds])[idx]; b = np.array([Bd[s] for s in seeds])[idx]
        aucs.append(auc(a, b))
    return float(np.mean(aucs))


def cell_global_auc(glob, arm, i, p, idx):
    A = glob[(arm, i, p, "A")]; Bd = glob[(arm, i, p, "B")]
    seeds = sorted(set(A) & set(Bd))
    return auc(np.array([A[s] for s in seeds])[idx], np.array([Bd[s] for s in seeds])[idx])


def arm_local(loc, st, arm, B, idx):
    return float(np.mean([np.mean([cell_local_auc(loc, st, arm, i, p, B, idx)
                                   for p in range(3)]) for i in range(3)]))


def arm_global(glob, arm, idx):
    return float(np.mean([np.mean([cell_global_auc(glob, arm, i, p, idx)
                                   for p in range(3)]) for i in range(3)]))


def main():
    loc, glob, cover, arrive, astep, null, have_distant = load()
    base = np.arange(NSEED)

    # ---- per-cell table (orig, distant, global, distant-orig) ----
    rows = ["arm,patch,pair,budget,orig_auc,distant_auc,global_auc,distant_minus_orig"]
    for arm in ARMS:
        for i in range(3):
            for p in range(3):
                g = cell_global_auc(glob, arm, i, p, base)
                for B in BUD:
                    lo = cell_local_auc(loc, "orig", arm, i, p, B, base)
                    ld = cell_local_auc(loc, "distant", arm, i, p, B, base)
                    rows.append(f"{arm},{i},{p},{B},{lo:.4f},{ld:.4f},{g:.4f},{ld-lo:.4f}")
    open(os.path.join(RES, "cells.csv"), "w").write("\n".join(rows) + "\n")

    # ---- arm curves + shared seed-block bootstrap ----
    rng = np.random.default_rng(4242); NB = 2000
    resamples = [rng.integers(0, NSEED, NSEED) for _ in range(NB)]  # shared across cells
    arm_out = {arm: {} for arm in ARMS}
    for arm in ARMS:
        for st in STARTS:
            for B in BUD:
                pt = arm_local(loc, st, arm, B, base)
                bs = np.array([arm_local(loc, st, arm, B, ix) for ix in resamples])
                arm_out[arm][(st, B)] = (pt, float(np.percentile(bs, 2.5)),
                                         float(np.percentile(bs, 97.5)))
        g = arm_global(glob, arm, base)
        gbs = np.array([arm_global(glob, arm, ix) for ix in resamples])
        arm_out[arm]["global"] = (g, float(np.percentile(gbs, 2.5)),
                                  float(np.percentile(gbs, 97.5)))
        # distant - orig at each budget, shared resample (paired dependence preserved)
        for B in BUD:
            pt_d = arm_local(loc, "distant", arm, B, base) - arm_local(loc, "orig", arm, B, base)
            db = np.array([arm_local(loc, "distant", arm, B, ix)
                           - arm_local(loc, "orig", arm, B, ix) for ix in resamples])
            arm_out[arm][("diff", B)] = (pt_d, float(np.percentile(db, 2.5)),
                                         float(np.percentile(db, 97.5)))

    arows = ["arm,quantity,point,ci_lo,ci_hi"]
    for arm in ARMS:
        for st in STARTS:
            for B in BUD:
                v = arm_out[arm][(st, B)]
                arows.append(f"{arm},{st}_auc_B{B},{v[0]:.4f},{v[1]:.4f},{v[2]:.4f}")
        v = arm_out[arm]["global"]; arows.append(f"{arm},global,{v[0]:.4f},{v[1]:.4f},{v[2]:.4f}")
        for B in BUD:
            v = arm_out[arm][("diff", B)]
            arows.append(f"{arm},distant_minus_orig_B{B},{v[0]:.4f},{v[1]:.4f},{v[2]:.4f}")
    open(os.path.join(RES, "arms.csv"), "w").write("\n".join(arows) + "\n")

    # ---- coverage + arrival (descriptive) ----
    crows = ["arm,start,budget,frac_present_mean,frac_high_seen_mean,frac_arrived"]
    covm = {arm: {} for arm in ARMS}
    for arm in ARMS:
        for st in STARTS:
            for B in BUD:
                cc = cover[(st, arm, B)]; aa = arrive[(st, arm, B)]
                fp = float(np.mean([x[0] for x in cc])) if cc else float("nan")
                fh = float(np.mean([x[1] for x in cc])) if cc else float("nan")
                fa = float(np.mean(aa)) if aa else float("nan")
                covm[arm][(st, B)] = (fp, fh, fa)
                crows.append(f"{arm},{st},{B},{fp:.4f},{fh:.4f},{fa:.4f}")
    open(os.path.join(RES, "coverage_arrival.csv"), "w").write("\n".join(crows) + "\n")

    # ---- null (fixed random labels per (patch,seed)) ----
    lbl_rng = np.random.default_rng(1234); labels = {}
    for arm in ARMS:
        for i in range(3):
            for sd in range(NSEED):
                labels[(arm, i, sd)] = int(lbl_rng.integers(0, 2))
    nrows = ["arm,start,budget,null_auc_mean"]; nullc = {arm: {} for arm in ARMS}
    for arm in ARMS:
        for st in STARTS:
            for B in BUD:
                per_patch = []
                for i in range(3):
                    per_pair = []
                    for p in range(3):
                        aucs = []
                        for rep in range(REPS):
                            dd = null.get((st, arm, i, p, B, rep), {})
                            if not dd:
                                continue
                            seeds = sorted(dd)
                            A = [dd[s] for s in seeds if labels[(arm, i, s)] == 0]
                            Bd = [dd[s] for s in seeds if labels[(arm, i, s)] == 1]
                            aucs.append(auc(A, Bd))
                        if aucs:
                            per_pair.append(np.nanmean(aucs))
                    if per_pair:
                        per_patch.append(np.mean(per_pair))
                nullc[arm][(st, B)] = float(np.mean(per_patch)) if per_patch else float("nan")
                nrows.append(f"{arm},{st},{B},{nullc[arm][(st, B)]:.4f}")
    open(os.path.join(RES, "null.csv"), "w").write("\n".join(nrows) + "\n")

    make_fig(arm_out, covm, nullc, astep)
    console(arm_out, covm, nullc, astep)


def make_fig(arm_out, covm, nullc, astep):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    col = {"regular": "#d62728", "perturbed": "#1f77b4"}
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.2))
    # panel 1: AUC vs budget, orig (solid) vs distant (dashed), global dotted
    ax = axes[0]
    for arm in ARMS:
        yo = [arm_out[arm][("orig", B)][0] for B in BUD]
        loo = [arm_out[arm][("orig", B)][0] - arm_out[arm][("orig", B)][1] for B in BUD]
        hio = [arm_out[arm][("orig", B)][2] - arm_out[arm][("orig", B)][0] for B in BUD]
        ax.errorbar(BUD, yo, yerr=[loo, hio], fmt="-o", color=col[arm], capsize=3,
                    label=f"{arm} orig-S")
        yd = [arm_out[arm][("distant", B)][0] for B in BUD]
        lod = [arm_out[arm][("distant", B)][0] - arm_out[arm][("distant", B)][1] for B in BUD]
        hid = [arm_out[arm][("distant", B)][2] - arm_out[arm][("distant", B)][0] for B in BUD]
        ax.errorbar(BUD, yd, yerr=[lod, hid], fmt="--s", color=col[arm], capsize=3,
                    alpha=0.85, label=f"{arm} distant")
        g = arm_out[arm]["global"][0]
        ax.axhline(g, ls=":", color=col[arm], lw=1, alpha=0.6)
    ax.axhline(0.5, ls="-", color="k", lw=0.6)
    ax.set_xscale("log"); ax.set_ylim(0.44, 0.72); ax.set_xlabel("visitor budget (steps)")
    ax.set_ylabel("AUC"); ax.set_title("History AUC: original-S (solid) vs distant (dashed)\n"
                                       "(dotted = global on same worlds; primary B=300)")
    ax.legend(fontsize=7)
    # panel 2: distant - orig at B=300
    ax = axes[1]
    for arm in ARMS:
        v = arm_out[arm][("diff", PRIMARY)]
        ax.bar(arm, v[0], yerr=[[v[0]-v[1]], [v[2]-v[0]]], color=col[arm], capsize=4, alpha=0.85)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_title("distant - original AUC  (B=300, same worlds)\nseed-bootstrap 95% CI")
    ax.set_ylabel("AUC difference")
    # panel 3: coverage + arrival vs budget
    ax = axes[2]
    for arm in ARMS:
        ax.plot(BUD, [covm[arm][("orig", B)][0] for B in BUD], "-o", color=col[arm],
                label=f"{arm} orig frac present")
        ax.plot(BUD, [covm[arm][("distant", B)][0] for B in BUD], "--s", color=col[arm],
                alpha=0.7, label=f"{arm} distant frac present")
        ax.plot(BUD, [covm[arm][("distant", B)][2] for B in BUD], ":^", color=col[arm],
                alpha=0.9, label=f"{arm} distant frac arrived")
    ax.set_xscale("log"); ax.set_ylim(0, 1.05); ax.set_xlabel("visitor budget (steps)")
    ax.set_ylabel("fraction"); ax.set_title("Coverage & arrival at imposed paths")
    ax.legend(fontsize=6.5)
    fig.suptitle("v14 visitor-start intervention -- does aided history discrimination "
                 "depend on starting at S?  (distant start != representative location)",
                 fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(os.path.join(FIG, "visitor_start_v14.png"), dpi=140); plt.close(fig)


def console(arm_out, covm, nullc, astep):
    print("=" * 78)
    for arm in ARMS:
        for st in STARTS:
            print(f"{arm} {st:7s}: " + "  ".join(
                f"B{B}:{arm_out[arm][(st,B)][0]:.3f}[{arm_out[arm][(st,B)][1]:.3f},"
                f"{arm_out[arm][(st,B)][2]:.3f}]" for B in BUD))
        v = arm_out[arm][("diff", PRIMARY)]
        med = int(np.median(astep[("distant", arm)])) if astep[("distant", arm)] else -1
        print(f"    global:{arm_out[arm]['global'][0]:.3f}  distant-orig@300: "
              f"{v[0]:+.3f} [{v[1]:+.3f},{v[2]:+.3f}]  | null orig/dist@300 "
              f"{nullc[arm][('orig',300)]:.3f}/{nullc[arm][('distant',300)]:.3f}")
        print(f"    cover@300 present orig/dist "
              f"{covm[arm][('orig',300)][0]:.2f}/{covm[arm][('distant',300)][0]:.2f}  "
              f"arrived@300 dist {covm[arm][('distant',300)][2]:.2f}  "
              f"median arrival step (dist,reached) {med}")
    print("=" * 78)


if __name__ == "__main__":
    main()

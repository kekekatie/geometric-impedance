#!/usr/bin/env python3
"""
endurance_bridge.py -- ribs and hinges (Experiment D, structural version).
(PREREGISTRATION.md, frozen before this file.)

For every recurring-fingerprint tie, measure forced-support reach: the size of the
forced cascade a settlement anchors (localised forced-only burst, tiles placed).
Join to the tie's birth-decisiveness (A's stiffness value, C's burst fate) and ask:
  D1  decisive births (rigid) anchor larger reach than wobbly (malleable).
  D2  reach is bimodal -- ribs vs hinges.
  D3  reach is structural, not a stopwatch artifact (does not track frontier speed).

Run:  python3 endurance_bridge.py                    # full, 24 worlds, parallel
      python3 endurance_bridge.py --worlds 2 --nadd 500 --serial   # quick test
"""
from __future__ import annotations
from pathlib import Path
import sys, os, json, collections, random, argparse
from multiprocessing import Pool
import numpy as np
from scipy.stats import spearmanr, mannwhitneyu

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "corner-response-catalogue"))
import figures as F
import corner_response as CR

L, D, S, SN = F.L, F.D, F.S, F.SN
RES = HERE / "results"; RES.mkdir(exist_ok=True)
EPS = 1e-9
LOCAL_R = 10
BURST_CAP = 60
_STIFF = json.loads((HERE.parent / "corner-response-catalogue" / "results" / "summary.json").read_text())["stiffness"]
RECUR = set(_STIFF)


def forced_burst_reach(before, edge, mid, cap=BURST_CAP, R=LOCAL_R):
    """Localised forced-only burst; return (fate, reach) where reach = tiles forced."""
    P = L.Patch(list(before)); rr = R * S + EPS; reach = 0; fate = "cap_open"
    for _ in range(cap):
        if len(D.candidates(P, *edge[:3])) <= 1:
            fate = "settled"; break
        forced = {}
        for e in P.frontier():
            if abs((e[0] + e[1]) / 2 - mid) > rr:
                continue
            cs = D.candidates(P, *e[:3])
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        placed = 0
        for t in forced.values():
            if P.legal(t):
                P.add(t); placed += 1
        reach += placed
        if placed == 0:
            fate = "saturated_open"; break
    return fate, reach


def grow_world_d(k):
    rng = random.Random(CR.SEED0 + k)
    P = L.Patch(L.seed_patch(CR.centres()[k], 3 * S)); n0 = len(P.tris); r = 0
    active, done, ties = {}, set(), []
    status = "ok"

    def resolve(sk, rec):
        tie = active.pop(sk); done.add(sk)
        local_added = len(CR.near(P.tris[len(tie["before"]):], tie["mid"], CR.RPRIMARY))
        slices = max(r - tie["first_slice"], 1)
        rec.update(world=k, fp=tie["fp"], stiffness=_STIFF.get(tie["fp"]),
                   burst=tie["burst"], reach=tie["reach"], advance_rate=local_added / slices)
        ties.append(rec)

    while len(P.tris) - n0 < CR.N_ADD:
        r += 1
        fr = P.frontier(); cand = {}; fmap = {}; jam = False
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = True; break
            sk = CR.ek(e); cand[sk] = len(cs); fmap[sk] = e
        if jam:
            status = "JAM"; break
        for sk in list(active):
            tie = active[sk]
            if sk not in cand:
                resolve(sk, dict(drawer="gone"))
            elif cand[sk] == 1:
                added_local = CR.near(P.tris[len(tie["before"]):], tie["mid"], CR.RPRIMARY)
                rec = CR.response_test(tie["before"], added_local, tie["edge"])
                resolve(sk, rec)
            elif r - tie["first_slice"] >= CR.K:
                resolve(sk, dict(drawer="stayed_open"))
        for sk, n in cand.items():
            if n == 2 and sk not in active and sk not in done:
                e = fmap[sk]; mid = (e[0] + e[1]) / 2; before = list(P.tris)
                fp = CR.fingerprint(before, mid, CR.RPRIMARY)
                burst = reach = None
                if fp in RECUR:
                    burst, reach = forced_burst_reach(before, e, mid)
                active[sk] = dict(before=before, edge=e, first_slice=r, mid=mid, fp=fp, burst=burst, reach=reach)
        forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= CR.N_ADD:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            continue
        cs = SN.ordered(D.candidates(P, *fr[0][:3])); gk = CR.ek(fr[0])
        if gk in active:
            resolve(gk, dict(drawer="directly_chosen"))
        P.add(rng.choice(cs))
    for sk in list(active):
        resolve(sk, dict(drawer="stayed_open", at_end=True))
    return dict(world=k, status=status, ties=[t for t in ties if t["fp"] in RECUR])


def dip(x):
    """Crude bimodality flag: Hartigan-free -- compare a 1-gaussian vs 2-cluster gap."""
    x = np.sort(np.asarray(x, float))
    if len(x) < 20:
        return None
    # largest gap between consecutive 5th..95th percentile values, normalized
    lo, hi = np.percentile(x, 5), np.percentile(x, 95)
    core = x[(x >= lo) & (x <= hi)]
    if len(core) < 10:
        return None
    gaps = np.diff(core)
    return float(gaps.max() / (core.std() + EPS))


def score(worlds):
    ties = [t for w in worlds for t in w["ties"]]
    settl = [t for t in ties if t["drawer"] in ("single_keystone", "committee") and t["reach"] is not None and t["stiffness"] is not None]
    lines = [f"worlds {len(worlds)}; recurring ties {len(ties)}; settlements with reach {len(settl)}"]

    reach = np.array([t["reach"] for t in settl]); stiff = np.array([t["stiffness"] for t in settl])
    lines.append(f"reach: median {np.median(reach):.1f}, mean {reach.mean():.1f}, max {reach.max()}, "
                 f"p10 {np.percentile(reach,10):.0f} p90 {np.percentile(reach,90):.0f}")

    # D1 -- decisive births anchor larger reach
    rho, p = spearmanr(stiff, reach)
    rigid = reach[stiff >= CR.RIGID_CUT]; mall = reach[stiff < CR.RIGID_CUT]
    d1 = rho > 0.2 and np.median(rigid) > np.median(mall)
    lines.append(f"D1: {'HELD  ' if d1 else 'did not hold'}  Spearman(stiffness, reach) {rho:.3f} (pledged > 0.2); "
                 f"rigid-fp reach median {np.median(rigid):.1f} (n {len(rigid)}) vs malleable {np.median(mall):.1f} (n {len(mall)})")

    # D2 -- bimodal (ribs vs hinges)
    dd = dip(reach)
    d2 = dd is not None and dd > 0.5
    lines.append(f"D2: {'HELD  ' if d2 else 'did not hold'}  reach bimodality gap/std {dd if dd is None else round(dd,3)} "
                 f"(pledged > 0.5; crude dip -- see histogram)")

    # D3 -- not the stopwatch
    rate = np.array([t["advance_rate"] for t in settl])
    rho3, p3 = spearmanr(reach, rate)
    d3 = abs(rho3) < 0.2
    lines.append(f"D3: {'HELD  ' if d3 else 'did not hold'}  Spearman(reach, frontier-advance-rate) {rho3:.3f} "
                 f"(pledged |rho| < 0.2; structural, not temporal)")

    # reported: reach by burst fate (secretly-rigid vs genuine occurrence)
    for fate in ("settled", "saturated_open", "cap_open"):
        rr = [t["reach"] for t in settl if t["burst"] == fate]
        if rr:
            lines.append(f"  reported: reach median for burst={fate}: {np.median(rr):.1f} (n {len(rr)})")

    summary = dict(settlements=len(settl),
                   reach_median=float(np.median(reach)), reach_p90=float(np.percentile(reach, 90)),
                   D1=dict(held=bool(d1), spearman=float(rho), rigid_median=float(np.median(rigid)), mall_median=float(np.median(mall))),
                   D2=dict(held=bool(d2), dip=dd),
                   D3=dict(held=bool(d3), spearman=float(rho3)),
                   reach_values=[int(t["reach"]) for t in settl],
                   stiffness_values=[float(t["stiffness"]) for t in settl])
    return "\n".join(lines), summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=CR.N_WORLDS)
    ap.add_argument("--nadd", type=int, default=None)
    ap.add_argument("--serial", action="store_true")
    args = ap.parse_args()
    if args.nadd:
        CR.N_ADD = args.nadd
    ids = list(range(args.worlds))
    if args.serial or args.worlds == 1:
        worlds = [grow_world_d(k) for k in ids]
    else:
        with Pool(min(4, args.worlds), maxtasksperchild=1) as p:
            worlds = p.map(grow_world_d, ids)
    report, summary = score(worlds)
    print(report)
    jd = lambda o: o.item() if hasattr(o, "item") else str(o)
    (RES / "worlds.json").write_text(json.dumps(worlds, default=jd))
    (RES / "summary.json").write_text(json.dumps(summary, indent=2, default=jd))
    (RES / "endurance_bridge_report.txt").write_text(report + "\n")


if __name__ == "__main__":
    main()

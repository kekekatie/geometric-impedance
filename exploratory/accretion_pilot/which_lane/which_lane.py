#!/usr/bin/env python3
"""
which_lane.py -- does the side of the cut name the lane the ribbon takes? (PREREGISTRATION.md, frozen before this file.)
Rebuilds the 45 distinct configurations of settled_test/ (same world() and seeds). For each: the cut facet (normal of
option A's side and its window layer), both options' forced-only initial bursts, each side's core (largest connected
chain of the predicted family), and the lane offset (centroid of A's core minus B's, along family j's physical edge
direction). `python3 which_lane.py` writes results/.
"""
from __future__ import annotations
import os, sys, json, math, cmath, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "settled_test"))
import settled_test as ST
CD, Sl, L, D, S = ST.CD, ST.Sl, ST.L, ST.D, ST.S
MIN_OFF = 0.25
RES = os.path.join(HERE, "results")
cen = ST.cen


def cut_facet(c0, cA, cB):
    """as golden_digits cut_line, but also returns A's facet key (layer rank, side)."""
    best = None
    for ka, ca in cA.items():
        if ca <= c0.get(ka, -1e18) + 1e-12:
            continue
        na = Sl.WIN[ka[0]][0][ka[1]]
        for kb, cb in cB.items():
            if cb <= c0.get(kb, -1e18) + 1e-12:
                continue
            nb = Sl.WIN[kb[0]][0][kb[1]]
            if abs(na[0] + nb[0]) < 1e-9 and abs(na[1] + nb[1]) < 1e-9 and abs(ca + cb) < 1e-9:
                best = (ka, (float(na[0]), float(na[1])), float(ca))
    return best


def measure(job):
    key, base, cs = job
    rank = Sl.rank_of(base); c0 = Sl.constraints(base, rank)
    cA, cB = CD.after_first(base, cs[0], rank), CD.after_first(base, cs[1], rank)
    cut = cut_facet(c0, cA, cB)
    if cut is None:
        return dict(key=key, cut=None)
    ka, na, ca = cut
    angle = ST.line_angle(na); j = ST.predicted_family(angle)
    z2 = cmath.exp(1j * math.radians(144 * j)); sA = int(np.sign(na[0] * z2.real + na[1] * z2.imag))
    (bA, _), (bB, _) = ST.burst(base, cs[0]), ST.burst(base, cs[1])
    uA, uB = CD.strip(bA, bB)
    kA, kB = ST.core(uA, j), ST.core(uB, j)
    coreA = [t for t in uA if D.dkey(t) in kA]; coreB = [t for t in uB if D.dkey(t) in kB]
    ej = cmath.exp(1j * math.radians(18 + 72 * j))
    proj = lambda ts: float(np.mean([((cen(t) / S) * ej.conjugate()).real for t in ts])) if ts else None
    off = None if not coreA or not coreB else proj(coreA) - proj(coreB)
    off_all = None if not uA or not uB else proj(uA) - proj(uB)
    return dict(key=key, cut=dict(rank=int(ka[0]), side=int(ka[1]), angle=angle), j=j, sA=sA, n_core=[len(coreA), len(coreB)],
                n_changed=[len(uA), len(uB)], offset=off, offset_all=off_all, dom=ST.dominant(uA + uB))


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(ST.world, range(ST.N_WORLDS))
    first = {}
    for w in W:
        for c in w["choices"]:
            first.setdefault(c["key"], c)
    ref = json.load(open(os.path.join(HERE, "..", "settled_test", "results", "results.json")))
    same = set(first) == {r["key"] for r in ref["situations"]}
    with Pool(4, maxtasksperchild=1) as p:
        R = p.map(measure, [(k, c["base"], c["cs"]) for k, c in first.items()], chunksize=1)
    json.dump(R, open(os.path.join(RES, "results.json"), "w"), default=lambda o: o.item() if hasattr(o, "item") else str(o))
    ok = [r for r in R if r["cut"] is not None and r["offset"] is not None]
    lines = [f"rebuilt {len(first)} configurations (same keys as settled_test: {same}); with cut and both cores: {len(ok)}; "
             f"dominant family = predicted in {sum(r['dom'] == r['j'] for r in ok)}/{len(ok)}"]
    l1 = sum(abs(r["offset"]) >= MIN_OFF for r in ok)
    lines.append(f"  L1: {'HELD  ' if ok and l1 >= 0.8 * len(ok) else 'FAILED'}  |offset| >= {MIN_OFF} edges in {l1}/{len(ok)} (need >= 80%); "
                 f"|offset| values {sorted(round(abs(r['offset']), 2) for r in ok)}")
    big = [r for r in ok if abs(r["offset"]) >= MIN_OFF]
    prod = [int(np.sign(r["offset"])) * r["sA"] for r in big]
    cnt = collections.Counter(prod); top = cnt.most_common(1)[0] if cnt else (None, 0)
    lines.append(f"  L2: {'HELD  ' if big and top[1] >= 0.9 * len(big) else 'FAILED'}  sign(offset) x s_A: {dict(cnt)}; commonest value {top[0]} in "
                 f"{top[1]}/{len(big)} (need >= 90%)")
    by = collections.defaultdict(collections.Counter)
    for r in big:
        by[r["cut"]["rank"]][int(np.sign(r["offset"])) * r["sA"]] += 1
    lines.append(f"  reported: L2 by the cut facet's window layer (rank: counts of the product) {dict((k, dict(v)) for k, v in sorted(by.items()))}")
    lines.append(f"  reported: offset using all changed tiles, |offset_all| median {np.median([abs(r['offset_all']) for r in ok]):.2f}; "
                 f"sign agrees with the core offset in {sum(np.sign(r['offset_all']) == np.sign(r['offset']) for r in ok)}/{len(ok)}")
    lines.append(f"  reported: core sizes A/B median {np.median([r['n_core'][0] for r in ok]):.0f}/{np.median([r['n_core'][1] for r in ok]):.0f}")
    print("\n".join(lines))
    open(os.path.join(RES, "which_lane_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

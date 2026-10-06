#!/usr/bin/env python3
"""
past_or_present.py -- decided by the past or by the present? (PREREGISTRATION.md, frozen before this file.)
During forced-only growth of intact decapod worlds, for every forced tile: the smallest memory horizon a* (rounds) such
that the owner tile plus the tiles laid in the last a* rounds (within 2.5 edges) already force it.
`python3 past_or_present.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, random, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "structure_clock"))
import structure_clock as SC
M, D, L, S = SC.M, SC.D, SC.L, SC.S
HORIZONS = [1, 2, 3, 5, 8, None]          # None = all ages
ALL = 99
SEEDS, N_TILES, NBR = [2, 3, 4, 5], 2000, 2.5
RES = os.path.join(HERE, "results")
cen = lambda t: sum(t[1:]) / 3


def a_star(P_tiles, rnd, r, e, t):
    owner = e[3]; c = cen(t)
    near = [u for u in P_tiles if abs(cen(u) - c) <= NBR * S]
    for a in HORIZONS:
        keep = [u for u in near if a is None or rnd[D.dkey(u)] >= r - a]
        if not any(D.dkey(u) == D.dkey(owner) for u in keep):
            keep.append(owner)
        Q = L.Patch(keep)
        cs = D.candidates(Q, *e[:3])
        if len(cs) == 1 and D.dkey(cs[0]) == D.dkey(t):
            return ALL if a is None else a
    return None                                  # not forced even with everything nearby (violates Z)


def world(s):
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    x = next(v for v in seeds if v["seed"] == s)
    ring = [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    P = L.Patch(list(ring)); n0 = len(P.tris); r = 0
    rnd = {D.dkey(t): 0 for t in ring}; recs = []; guesses = 0
    while len(P.tris) - n0 < N_TILES:
        r += 1
        fr = [e for e in P.frontier() if abs((e[0] + e[1]) / 2) > D.APO + 1e-6]
        forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), (cs[0], e))
        snapshot = list(P.tris)
        placed = 0
        for q, (t, e) in forced.items():
            if len(P.tris) - n0 >= N_TILES:
                break
            if P.legal(t):
                a = a_star(snapshot, rnd, r, e, t)
                recs.append(dict(key=q, round=r, a_star=a, owner_age=r - rnd[D.dkey(e[3])]))
                P.add(t); rnd[q] = r; placed += 1
        if placed == 0:
            if forced:
                continue
            guesses += 1
            cs = sorted(D.candidates(P, *fr[0][:3]), key=lambda u: (u[0], L.key(u[1]), L.key(u[2]), L.key(u[3])))
            t = random.Random(D.SEED0 + 100 * s + r).choice(cs); P.add(t); rnd[D.dkey(t)] = r
    tiles = list(P.tris); geo = {D.dkey(t): t for t in tiles}
    K, pos, conf = M.lift(tiles); dep, areas, lays = M.depths(K)
    for rec in recs:
        t = geo[rec["key"]]
        ds = [dep.get(L.key(z)) for z in t[1:]]
        rec["depth"] = float(np.mean([d for d in ds if d is not None])) if any(d is not None for d in ds) else None
        rec["rad"] = abs(cen(t)) / S
        rec.pop("key")
    ok = [x for x in recs if x["a_star"] is not None and x["depth"] is not None and x["rad"] >= 2.5]
    rho, _ = SC.strat_spearman([x["rad"] for x in ok], [x["depth"] for x in ok], [x["a_star"] for x in ok])
    return dict(seed=s, guesses=guesses, rounds=r, n=len(recs), z_fail=sum(x["a_star"] is None for x in recs),
                rho=float(rho), recs=recs)


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4) as p:
        W = p.map(world, SEEDS)
    json.dump(W, open(os.path.join(RES, "worlds.json"), "w"))
    lines = []
    pooled = [x["a_star"] for w in W for x in w["recs"] if x["a_star"] is not None]
    for w in W:
        a = [x["a_star"] for x in w["recs"] if x["a_star"] is not None]
        dist = collections.Counter(a)
        ok = [x for x in w["recs"] if x["a_star"] is not None and x["depth"] is not None]
        q = np.quantile([x["depth"] for x in ok], [1 / 3, 2 / 3])
        terc = {k: float(np.mean([x["a_star"] for x in ok if sel(x["depth"])]))
                for k, sel in (("shallow", lambda d: d <= q[0]), ("mid", lambda d: q[0] < d <= q[1]), ("deep", lambda d: d > q[1]))}
        lines.append(f"  seed {w['seed']}: guesses {w['guesses']}, forced tiles {w['n']}, Z failures {w['z_fail']}; a* distribution "
                     f"{dict(sorted(dist.items()))}; present-only (a*=1) {dist[1] / len(a):.2f}, needs >= 3 rounds "
                     f"{sum(v for k, v in dist.items() if k >= 3) / len(a):.2f}; mean a* by depth third "
                     f"{({k: round(v, 2) for k, v in terc.items()})}; mean owner age {np.mean([x['owner_age'] for x in w['recs']]):.2f}; "
                     f"rho(depth, a*) {w['rho']:+.3f}")
    z = all(w["z_fail"] == 0 for w in W)
    g1 = float(np.median(pooled)) <= 2
    g2 = sum(w["rho"] > 0 for w in W) >= 3
    lines += [f"  Z : {'PASS' if z else 'FAIL'}  every forced tile is forced by its full 2.5-edge neighbourhood",
              f"  G1: {'HELD  ' if g1 else 'FAILED'}  pooled median a* = {np.median(pooled):.0f} rounds (need <= 2); "
              f"pooled share a*=1: {sum(x == 1 for x in pooled) / len(pooled):.2f}",
              f"  G2: {'HELD  ' if g2 else 'FAILED'}  rho(depth, a*) > 0 in {sum(w['rho'] > 0 for w in W)}/4 (need >= 3); "
              f"values {[round(w['rho'], 3) for w in W]}"]
    print("\n".join(lines))
    open(os.path.join(RES, "past_or_present_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

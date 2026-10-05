#!/usr/bin/env python3
"""
decision_radius.py -- how much of the world must weigh in to decide a place? (PREREGISTRATION.md, frozen before this
file.) For probe vertices in intact decapod worlds: the smallest context radius from which the place's tiles are uniquely
determined, vs hull depth and settling time. `python3 decision_radius.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, random
from multiprocessing import Pool
import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "structure_clock"))
sys.path.insert(0, os.path.join(HERE, "..", "continuation_choices"))
import structure_clock as SC
import continuation_choices as CC
M, D, L, S = SC.M, SC.D, SC.L, SC.S
RADII, CENSORED, ATT, REACH, MAXADD = [1.25, 1.5, 2.0, 2.5, 3.0, 4.0], 5.0, 16, 1.8, 80   # follow-up radii
SEEDS, NPROBE = [2, 3, 4, 5], 100
RES = os.path.join(HERE, "results")
cen = lambda t: sum(t[1:]) / 3


def complete(base, c, pts, rng):
    """CC.complete with decoration-aware candidates (decapod_seed.candidates)."""
    Q = L.Patch(base); cov = CC.cover_of(base, pts)
    for _ in range(MAXADD):
        if all(x is not None for x in cov):
            break
        edges = sorted((e for e in Q.frontier() if abs((e[0] + e[1]) / 2 - c) <= REACH * S),
                       key=lambda e: (abs((e[0] + e[1]) / 2 - c), L.key((e[0] + e[1]) / 2)))
        forced = None; first = None
        for e in edges:
            cs = [t for t in D.candidates(Q, *e[:3]) if abs(cen(t) - c) <= REACH * S]
            if len(cs) == 1:
                forced = cs[0]; break
            if cs and first is None:
                first = cs
        if forced is None and first is None:
            return None
        t = forced if forced is not None else rng.choice(sorted(first, key=lambda u: (u[0], L.key(u[1]), L.key(u[2]), L.key(u[3]))))
        Q.add(t)
        for i, p in enumerate(pts):
            if cov[i] is None and L.inside(p, *t[1:]):
                cov[i] = t
    if any(x is None for x in cov):
        return None
    for e in Q.frontier():
        if abs((e[0] + e[1]) / 2 - c) <= REACH * S and not D.candidates(Q, *e[:3]):
            return None
    return tuple(D.dkey(x) for x in cov)


def world(s):
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    x = next(v for v in seeds if v["seed"] == s)
    ring = [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    P, rnd, rounds, guesses, status = SC.grow(ring, SC.N_TILES, D.SEED0 + 100 * s)
    tiles = list(P.tris); tc = np.array([cen(t) for t in tiles]); tr = np.array([rnd[D.dkey(t)] for t in tiles])
    mids = np.array([(e[0] + e[1]) / 2 for e in P.frontier()])
    K, pos, conf = M.lift(tiles); dep, areas, lays = M.depths(K)
    cands = sorted(v for v in K if v in dep and 4 * S <= abs(pos[v]) <= 10 * S and np.min(np.abs(mids - pos[v])) >= 4.5 * S)
    random.Random(2050 + s).shuffle(cands)
    rows = []
    for v in cands[:NPROBE]:
        c = pos[v]; d = np.abs(tc - c)
        disc_idx = np.where(d <= 1.0 * S)[0]
        disc_keys = {D.dkey(tiles[i]) for i in disc_idx}
        b, f = int(tr[disc_idx].min()), int(tr[disc_idx].max())
        pts = CC.sample_points(c)
        actual = tuple(D.dkey(x) for x in CC.cover_of([tiles[i] for i in np.where(d <= 2.5 * S)[0]], pts))
        drad = CENSORED; detail = {}
        for rho in RADII:
            base = [tiles[i] for i in np.where((d <= rho * S) & (tr <= f))[0] if D.dkey(tiles[i]) not in disc_keys]   # follow-up: the world as it stood when the place was finished
            sigs = [complete(base, c, pts, random.Random((2050 + s) * 100000 + len(rows) * 100 + int(rho * 100) * 3 + a)) for a in range(ATT)]
            ok = [g for g in sigs if g is not None]
            detail[str(rho)] = dict(success=len(ok), distinct=len(set(ok)), all_actual=bool(ok) and all(g == actual for g in ok))
            if ok and all(g == actual for g in ok):
                drad = rho; break
        rows.append(dict(depth=dep[v], radius_from_centre=abs(c) / S, decision_radius=drad, T=f - b, detail=detail))
    dr = [r["decision_radius"] for r in rows]; dp = [r["depth"] for r in rows]; T = [r["T"] for r in rows]
    r1 = spearmanr(dp, dr).correlation if np.ptp(dr) > 0 else float("nan")
    r2 = spearmanr(dr, T).correlation if np.ptp(dr) > 0 else float("nan")
    terc = np.quantile(dp, [1 / 3, 2 / 3])
    tmean = {k: float(np.mean([r["decision_radius"] for r in rows if sel(r["depth"])]))
             for k, sel in (("shallow", lambda x: x <= terc[0]), ("mid", lambda x: terc[0] < x <= terc[1]), ("deep", lambda x: x > terc[1]))}
    return dict(seed=s, status=status, guesses=guesses, n=len(rows), rho_depth=float(r1), rho_T=float(r2),
                dist={str(k): dr.count(k) for k in RADII + [CENSORED]}, terciles=tmean, rows=rows)


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(world, SEEDS)
    json.dump(W, open(os.path.join(RES, "worlds.json"), "w"))
    lines = []
    for w in W:
        lines.append(f"  seed {w['seed']}: {w['status']}, guesses {w['guesses']}, probes {w['n']}; decision radius distribution {w['dist']}; "
                     f"by depth tercile {({k: round(v, 2) for k, v in w['terciles'].items()})}; rho(depth, radius) {w['rho_depth']:+.3f}, "
                     f"rho(radius, T) {w['rho_T']:+.3f}")
    r1 = [w["rho_depth"] for w in W]; r2 = [w["rho_T"] for w in W]
    R1 = sum(x > 0 for x in r1) >= 3 and float(np.nanmedian(r1)) >= 0.15
    R2 = sum(x > 0 for x in r2) >= 3
    lines += [f"  R1: {'HELD  ' if R1 else 'FAILED'}  rho(depth, decision radius) > 0 in {sum(x > 0 for x in r1)}/4 (need >= 3), "
              f"median {np.nanmedian(r1):+.3f} (need >= 0.15)",
              f"  R2: {'HELD  ' if R2 else 'FAILED'}  rho(decision radius, settling time) > 0 in {sum(x > 0 for x in r2)}/4 (need >= 3); "
              f"values {[round(x, 3) for x in r2]}"]
    print("\n".join(lines))
    open(os.path.join(RES, "decision_radius_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

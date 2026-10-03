#!/usr/bin/env python3
"""
structure_clock.py -- structure and the local clock in an intact decapod world (PREREGISTRATION.md, frozen before this
file). For every probe vertex: hull depth (structure) vs settling time T (rounds) and H (local happenings), Spearman
correlations stratified by radius. `python3 structure_clock.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, random, collections
from multiprocessing import Pool
import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "perp_map"))
import perp_map as M
D, L, S = M.D, M.L, M.S
N_TILES, R_IN, FRONT_GAP, DISC, NBHD, MIN_BIN, NPERM = 2000, 4.0, 2.0, 1.0, 2.0, 15, 1000
RES = os.path.join(HERE, "results")
cen = lambda t: sum(t[1:]) / 3


def grow(ring, n_add, rs):
    """M.grow (patient scheduler, decagon wall) with the placement round of every tile recorded."""
    rng = random.Random(rs)
    P = L.Patch(list(ring)); n0 = len(P.tris); r = 0; rnd = {D.dkey(t): 0 for t in ring}; guesses = 0
    while len(P.tris) - n0 < n_add:
        r += 1
        fr = [e for e in P.frontier() if abs((e[0] + e[1]) / 2) > D.APO + 1e-6]
        forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                return P, rnd, r, guesses, "JAM"
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        placed = 0
        for q, t in forced.items():
            if len(P.tris) - n0 >= n_add:
                break
            if P.legal(t):
                P.add(t); rnd[q] = r; placed += 1
        if placed == 0:
            if forced:
                continue
            cs = sorted(D.candidates(P, *fr[0][:3]), key=lambda u: (u[0], L.key(u[1]), L.key(u[2]), L.key(u[3])))
            t = rng.choice(cs); P.add(t); rnd[D.dkey(t)] = r; guesses += 1
    return P, rnd, r, guesses, "ok"


def strat_spearman(rad, x, y):
    bins = collections.defaultdict(list)
    for i, rr in enumerate(rad):
        bins[int(rr)].append(i)
    num = den = 0.0
    for idx in bins.values():
        if len(idx) < MIN_BIN:
            continue
        xs = np.array(x)[idx]; ys = np.array(y)[idx]
        if np.ptp(xs) == 0 or np.ptp(ys) == 0:
            continue
        rho = spearmanr(xs, ys).correlation
        num += rho * len(idx); den += len(idx)
    return num / den if den else float("nan"), bins


def world(args):
    s, ring = args
    P, rnd, rounds, guesses, status = grow(ring, N_TILES, D.SEED0 + 100 * s)
    tiles = list(P.tris)
    mids = np.array([(e[0] + e[1]) / 2 for e in P.frontier()])
    K, pos, conf = M.lift(tiles)
    dep, areas, lays = M.depths(K)
    tc = np.array([cen(t) for t in tiles]); tr = np.array([rnd[D.dkey(t)] for t in tiles])
    rows = []
    for v, k in K.items():
        z = pos[v]
        if abs(z) < R_IN * S or v not in dep or np.min(np.abs(mids - z)) < FRONT_GAP * S:
            continue
        d = np.abs(tc - z)
        disc = tr[d <= DISC * S]
        if len(disc) == 0:
            continue
        b, f = int(disc.min()), int(disc.max())
        H = int(((d <= NBHD * S) & (tr > b) & (tr <= f)).sum())
        rows.append(dict(rad=abs(z) / S, depth=dep[v], T=f - b, H=H, layer=int(k.sum())))
    rad = [r["rad"] for r in rows]; dp = [r["depth"] for r in rows]
    rT, bins = strat_spearman(rad, dp, [r["T"] for r in rows])
    rH, _ = strat_spearman(rad, dp, [r["H"] for r in rows])
    # permutation baseline: shuffle depth within radial bins
    g = np.random.default_rng(2040 + s); exT = exH = 0
    for _ in range(NPERM):
        perm = list(dp)
        for idx in bins.values():
            vals = [dp[i] for i in idx]; g.shuffle(vals)
            for i, vv in zip(idx, vals):
                perm[i] = vv
        exT += abs(strat_spearman(rad, perm, [r["T"] for r in rows])[0]) >= abs(rT)
        exH += abs(strat_spearman(rad, perm, [r["H"] for r in rows])[0]) >= abs(rH)
    by_layer = {}
    for l in sorted({r["layer"] for r in rows}):
        sub = [r for r in rows if r["layer"] == l]
        if len(sub) >= 30:
            by_layer[l] = (strat_spearman([r["rad"] for r in sub], [r["depth"] for r in sub], [r["T"] for r in sub])[0],
                           strat_spearman([r["rad"] for r in sub], [r["depth"] for r in sub], [r["H"] for r in sub])[0], len(sub))
    terc = np.quantile(dp, [1 / 3, 2 / 3])
    groups = {"shallow": [r for r in rows if r["depth"] <= terc[0]], "mid": [r for r in rows if terc[0] < r["depth"] <= terc[1]],
              "deep": [r for r in rows if r["depth"] > terc[1]]}
    summ = {k: dict(T=float(np.mean([r["T"] for r in v])), H=float(np.mean([r["H"] for r in v])),
                    rate=float(np.mean([r["H"] / r["T"] for r in v if r["T"] > 0]))) for k, v in groups.items()}
    return dict(seed=s, status=status, guesses=guesses, rounds=rounds, conflicts=len(conf), n=len(rows),
                rho_T=float(rT), rho_H=float(rH), p_T=(exT + 1) / (NPERM + 1), p_H=(exH + 1) / (NPERM + 1),
                by_layer={str(k): v for k, v in by_layer.items()}, terciles=summ,
                mean_T=float(np.mean([r["T"] for r in rows])), mean_H=float(np.mean([r["H"] for r in rows])))


def main():
    os.makedirs(RES, exist_ok=True)
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    R = [json.loads(l) for l in open(os.path.join(D.RES, "runs.jsonl"))]
    ok0 = lambda s: all(r["status"] == "ok" and not r["guesses"] for r in R if r["seed"] == s)
    dec = [x for x in seeds if x["kind"] == "DECAPOD" and ok0(x["seed"])][:8]
    ring = lambda x: [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    with Pool(4, maxtasksperchild=2) as p:
        W = p.map(world, [(x["seed"], ring(x)) for x in dec])
    json.dump(W, open(os.path.join(RES, "worlds.json"), "w"))
    lines = []
    for w in W:
        lines.append(f"  seed {w['seed']}: {w['status']}, guesses {w['guesses']}, probes {w['n']}, mean T {w['mean_T']:.1f} rounds, "
                     f"mean H {w['mean_H']:.1f}; rho_T {w['rho_T']:+.3f} (perm p {w['p_T']:.3f}), rho_H {w['rho_H']:+.3f} "
                     f"(perm p {w['p_H']:.3f})")
        lines.append("      by depth tercile: " + "; ".join(f"{k}: T {v['T']:.1f}, H {v['H']:.1f}, H/T {v['rate']:.2f}" for k, v in w["terciles"].items()))
        lines.append("      by layer (rho_T, rho_H, n): " + str({k: tuple(round(x, 3) if isinstance(x, float) else x for x in v) for k, v in w["by_layer"].items()}))
    rT = [w["rho_T"] for w in W]; rH = [w["rho_H"] for w in W]
    same = max(sum(x > 0 for x in rT), sum(x < 0 for x in rT))
    c1 = same >= 7 and float(np.median(np.abs(rT))) >= 0.15
    c2 = float(np.median(np.abs(rH))) < 0.15
    lines += [f"  C1: {'HELD  ' if c1 else 'FAILED'}  rho(depth, T rounds): same sign in {same}/8 (need >= 7), median |rho| "
              f"{np.median(np.abs(rT)):.3f} (need >= 0.15); values {[round(x, 3) for x in rT]}",
              f"  C2: {'HELD  ' if c2 else 'FAILED'}  rho(depth, H happenings): median |rho| {np.median(np.abs(rH)):.3f} (need < 0.15); "
              f"values {[round(x, 3) for x in rH]}"]
    print("\n".join(lines))
    open(os.path.join(RES, "structure_clock_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

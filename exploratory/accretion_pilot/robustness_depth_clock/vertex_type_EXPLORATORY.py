#!/usr/bin/env python3
"""EXPLORATORY (post hoc): is 'depth' just standing in for VERTEX TYPE (which of the 8 Penrose vertex stars a corner has;
in a cut-and-project tiling the type is fixed by where the vertex sits in the window)? For disc radii 0.6, 1.0, 2.0 on
4 decapod worlds: rho(depth, T) overall vs WITHIN vertex types (radius-stratified, averaged over types weighted by n)."""
import os, json, collections
from multiprocessing import Pool
import numpy as np
from scipy.stats import spearmanr
import robustness_depth_clock as RB
SC, M, D, L, S = RB.SC, RB.M, RB.D, RB.L, RB.S
seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
R = [json.loads(l) for l in open(os.path.join(D.RES, "runs.jsonl"))]
ok0 = lambda s: all(r["status"] == "ok" and not r["guesses"] for r in R if r["seed"] == s)
dec = [x for x in seeds if x["kind"] == "DECAPOD" and ok0(x["seed"])][:4]
ring = lambda x: [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]


def task(x):
    P, rnd, rounds, g, st = SC.grow(ring(x), SC.N_TILES, D.SEED0 + 100 * x["seed"])
    tiles = list(P.tris); mids = np.array([(e[0] + e[1]) / 2 for e in P.frontier()])
    K, pos, conf = M.lift(tiles); dep, areas, lays = M.depths(K)
    tc = np.array([SC.cen(t) for t in tiles]); tr = np.array([rnd[D.dkey(t)] for t in tiles])
    out = {}
    for r in (0.6, 1.0, 2.0):
        rows = []
        for v, k in K.items():
            z = pos[v]
            if abs(z) < SC.R_IN * S or v not in dep or np.min(np.abs(mids - z)) < SC.FRONT_GAP * S:
                continue
            star = P.V.get(v)
            if not star or abs(sum(d for _, d, _ in star) - 2 * np.pi) > 1e-6:
                continue
            d = np.abs(tc - z); disc = tr[d <= r * S]
            if len(disc) == 0:
                continue
            rows.append((abs(z) / S, dep[v], int(disc.max() - disc.min()), L.star(star)))
        overall, _ = SC.strat_spearman([a for a, _, _, _ in rows], [b for _, b, _, _ in rows], [c for _, _, c, _ in rows])
        num = den = 0.0; types = collections.Counter(t for *_, t in rows)
        for ty, n in types.items():
            sub = [q for q in rows if q[3] == ty]
            if n < 30:
                continue
            rho, _ = SC.strat_spearman([a for a, _, _, _ in sub], [b for _, b, _, _ in sub], [c for _, _, c, _ in sub])
            if not np.isnan(rho):
                num += rho * n; den += n
        # how much does vertex type alone explain T? (share of T variance between types)
        Ts = np.array([c for _, _, c, _ in rows]); grand = Ts.mean()
        between = sum(len([q for q in rows if q[3] == ty]) * (np.mean([q[2] for q in rows if q[3] == ty]) - grand) ** 2 for ty in types)
        out[r] = (overall, num / den if den else float("nan"), between / ((Ts - grand) ** 2).sum(), len(types))
    return x["seed"], out


if __name__ == "__main__":
    with Pool(4) as p:
        res = p.map(task, dec)
    lines = ["EXPLORATORY: depth vs vertex type. For each disc radius: overall rho(depth,T) | mean within-type rho | share of T variance between vertex types | number of types"]
    for s, out in res:
        for r, (o, w, share, nt) in out.items():
            lines.append(f"  seed {s} disc {r}: overall {o:+.3f} | within type {w:+.3f} | between-type share of T variance {share:.2f} | types {nt}")
    print("\n".join(lines))
    open(os.path.join(RB.RES, "vertex_type_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")

#!/usr/bin/env python3
"""
robustness_depth_clock.py -- stress-tests of structure_clock C1 (PREREGISTRATION.md, frozen before this file).
The analysis is ../structure_clock/structure_clock.py's world() body, with disc/neighbourhood radii and the seed patch
as parameters. A: 12 new decapod worlds; B: 12 ordinary worlds (patient scheduler, random guesses); C: disc sizes.
`python3 robustness_depth_clock.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "structure_clock"))
import structure_clock as SC
M, D, L, S = SC.M, SC.D, SC.L, SC.S
RES = os.path.join(HERE, "results")
cen = SC.cen


def analyse(args):
    label, key, ring, rs, disc_r, nbhd_r = args
    P, rnd, rounds, guesses, status = SC.grow(ring, SC.N_TILES, rs)
    tiles = list(P.tris)
    mids = np.array([(e[0] + e[1]) / 2 for e in P.frontier()])
    K, pos, conf = M.lift(tiles)
    dep, areas, lays = M.depths(K)
    tc = np.array([cen(t) for t in tiles]); tr = np.array([rnd[D.dkey(t)] for t in tiles])
    rows = []
    for v, k in K.items():
        z = pos[v]
        if abs(z) < SC.R_IN * S or v not in dep or np.min(np.abs(mids - z)) < SC.FRONT_GAP * S:
            continue
        d = np.abs(tc - z)
        disc = tr[d <= disc_r * S]
        if len(disc) == 0:
            continue
        b, f = int(disc.min()), int(disc.max())
        H = int(((d <= nbhd_r * S) & (tr > b) & (tr <= f)).sum())
        rows.append(dict(rad=abs(z) / S, depth=dep[v], T=f - b, H=H))
    rad = [r["rad"] for r in rows]; dp = [r["depth"] for r in rows]
    rT, _ = SC.strat_spearman(rad, dp, [r["T"] for r in rows])
    rH, _ = SC.strat_spearman(rad, dp, [r["H"] for r in rows])
    q = np.quantile(dp, [1 / 3, 2 / 3])
    terc = {k: float(np.mean([r["T"] for r in rows if sel(r["depth"])]))
            for k, sel in (("shallow", lambda x: x <= q[0]), ("mid", lambda x: q[0] < x <= q[1]), ("deep", lambda x: x > q[1]))}
    hist = hash(frozenset(rnd.keys()))
    return dict(test=label, key=key, status=status, guesses=guesses, n=len(rows), rho_T=float(rT), rho_H=float(rH),
                terciles=terc, history=str(hist))


def main():
    os.makedirs(RES, exist_ok=True)
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    R = [json.loads(l) for l in open(os.path.join(D.RES, "runs.jsonl"))]
    ok0 = lambda s: all(r["status"] == "ok" and not r["guesses"] for r in R if r["seed"] == s)
    dec = [x for x in seeds if x["kind"] == "DECAPOD" and ok0(x["seed"])]
    ring = lambda x: [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    orig8, new12 = dec[:8], dec[8:20]
    tasks = [("A", x["seed"], ring(x), D.SEED0 + 100 * x["seed"], SC.DISC, SC.NBHD) for x in new12]
    tasks += [("B", k, L.seed_patch(0j, 3 * S), 20261080 + k, SC.DISC, SC.NBHD) for k in range(12)]
    tasks += [("C-small", x["seed"], ring(x), D.SEED0 + 100 * x["seed"], 0.8, 1.5) for x in orig8]
    tasks += [("C-large", x["seed"], ring(x), D.SEED0 + 100 * x["seed"], 1.25, 2.5) for x in orig8]
    with Pool(4, maxtasksperchild=2) as p:
        out = p.map(analyse, tasks)
    json.dump(out, open(os.path.join(RES, "worlds.json"), "w"))
    lines = []; verdict = {}
    for test, need, total in (("A", 10, 12), ("B", 9, 12), ("C-small", 7, 8), ("C-large", 7, 8)):
        rs = [o for o in out if o["test"] == test]
        pos_ = sum(o["rho_T"] > 0 for o in rs)
        verdict[test] = pos_ >= need
        lines.append(f"{test}: {len(rs)} worlds; rho_T > 0 in {pos_}/{total} (need >= {need}); rho_T "
                     f"{[round(o['rho_T'], 3) for o in rs]}; rho_H {[round(o['rho_H'], 3) for o in rs]}; guesses "
                     f"{[o['guesses'] for o in rs]}; statuses {sorted(set(o['status'] for o in rs))}")
        lines.append(f"    mean T by depth third (averaged over worlds): " + ", ".join(
            f"{k} {np.mean([o['terciles'][k] for o in rs]):.2f}" for k in ("shallow", "mid", "deep")))
        if test == "B":
            lines.append(f"    distinct histories among the 12 ordinary worlds: {len({o['history'] for o in rs})}")
    lines += [f"  RA: {'HELD  ' if verdict['A'] else 'FAILED'}  new decapod worlds",
              f"  RB: {'HELD  ' if verdict['B'] else 'FAILED'}  ordinary worlds",
              f"  RC: {'HELD  ' if verdict['C-small'] and verdict['C-large'] else 'FAILED'}  disc sizes (small {verdict['C-small']}, large {verdict['C-large']})",
              f"  ROBUST: {'YES' if all(verdict.values()) else 'NO'}"]
    print("\n".join(lines))
    open(os.path.join(RES, "robustness_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

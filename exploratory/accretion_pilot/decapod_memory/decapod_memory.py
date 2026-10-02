#!/usr/bin/env python3
"""
decapod_memory.py -- where does a decapod keep its memory? (PREREGISTRATION.md, frozen before this file.)
Per-sector perp-space window offsets around the decagon, DECAPOD vs FILLABLE worlds (1,500 tiles).
`python3 decapod_memory.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, cmath, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "perp_map"))
import perp_map as M
D, L, S = M.D, M.L, M.S
N_TILES, NSEC, R_MIN, MIN_LAYER, MIN_CELL = 1500, 20, 2.5, 40, 5
RES = os.path.join(HERE, "results")


def world(args):
    s, kind, ring = args
    tiles, _, guesses, status = M.grow(ring, N_TILES, D.SEED0 + 100 * s, wall=True)
    K, pos, conf = M.lift(tiles)
    dep, areas, layers = M.depths(K)
    rows = []
    for v, k in K.items():
        z = pos[v]
        if abs(z) < R_MIN * S:
            continue
        sec = int((cmath.phase(z) % (2 * math.pi)) / (2 * math.pi) * NSEC) % NSEC
        rows.append((sec, int(k.sum()), M.perp(k)))
    lay_count = collections.Counter(l for _, l, _ in rows)
    lays = [l for l, c in lay_count.items() if c >= MIN_LAYER]
    wmean = {l: np.mean([z for _, ll, z in rows if ll == l]) for l in lays}
    cell = {}
    for sec in range(NSEC):
        for l in lays:
            zs = [z for ss, ll, z in rows if ss == sec and ll == l]
            if len(zs) >= MIN_CELL:
                cell[(sec, l)] = complex(np.mean(zs))
    offsets = {}
    for sec in range(NSEC):
        ds = [abs(cell[(sec, l)] - wmean[l]) for l in lays if (sec, l) in cell]
        if ds:
            offsets[sec] = float(np.mean(ds))
    vecs = {sec: [(l, cell[(sec, l)] - wmean[l]) for l in lays if (sec, l) in cell] for sec in range(NSEC)}

    def dist(a, b):
        ca = dict(vecs[a]); cb = dict(vecs[b]); common = [l for l in ca if l in cb]
        return float(np.mean([abs(ca[l] - cb[l]) for l in common])) if common else None
    adj = [dist(a, (a + 1) % NSEC) for a in range(NSEC)]; far = [dist(a, (a + 5) % NSEC) for a in range(NSEC)]
    adj = [x for x in adj if x is not None]; far = [x for x in far if x is not None]
    return dict(seed=s, kind=kind, status=status, guesses=len(guesses), conflicts=len(conf), layers=lays,
                score=float(np.mean(list(offsets.values()))), offsets=offsets,
                ratio=float(np.mean(adj) / np.mean(far)), total_area=float(sum(areas.values())),
                vectors={str(sec): [[l, v.real, v.imag] for l, v in vv] for sec, vv in vecs.items()})


def main():
    os.makedirs(RES, exist_ok=True)
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    R = [json.loads(l) for l in open(os.path.join(D.RES, "runs.jsonl"))]
    ok0 = lambda s: all(r["status"] == "ok" and not r["guesses"] for r in R if r["seed"] == s)
    dec = [x for x in seeds if x["kind"] == "DECAPOD" and ok0(x["seed"])][:8]
    fil = [x for x in seeds if x["kind"] == "FILLABLE"]
    ring = lambda x: [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    with Pool(4, maxtasksperchild=2) as p:
        W = p.map(world, [(x["seed"], x["kind"], ring(x)) for x in dec + fil])
    json.dump(W, open(os.path.join(RES, "worlds.json"), "w"))
    lines = []
    for w in W:
        lines.append(f"  {w['kind']:<8} seed {w['seed']:>3}: {w['status']}, guesses {w['guesses']}, conflicts {w['conflicts']}, "
                     f"layers {sorted(w['layers'])}, memory score {w['score']:.4f}, adjacent/90deg ratio {w['ratio']:.2f}, "
                     f"hull area {w['total_area']:.2f}")
    ds = [w["score"] for w in W if w["kind"] == "DECAPOD"]; fs = [w["score"] for w in W if w["kind"] == "FILLABLE"]
    dr = [w["ratio"] for w in W if w["kind"] == "DECAPOD"]; fr = [w["ratio"] for w in W if w["kind"] == "FILLABLE"]
    d1 = all(x > max(fs) for x in ds)
    d2 = float(np.median(dr)) < 0.8 and float(np.median(dr)) < float(np.median(fr))
    lines += [f"  D1: {'HELD  ' if d1 else 'FAILED'}  DECAPOD memory scores {sorted(round(x, 4) for x in ds)} vs FILLABLE max "
              f"{max(fs):.4f} ({sorted(round(x, 4) for x in fs)}); {sum(x > max(fs) for x in ds)}/8 above",
              f"  D2: {'HELD  ' if d2 else 'FAILED'}  adjacent/90deg ratio: DECAPOD median {np.median(dr):.2f} (need < 0.8) vs "
              f"FILLABLE median {np.median(fr):.2f}"]
    print("\n".join(lines))
    open(os.path.join(RES, "decapod_memory_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

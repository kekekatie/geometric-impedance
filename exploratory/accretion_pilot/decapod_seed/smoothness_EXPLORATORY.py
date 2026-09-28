#!/usr/bin/env python3
"""EXPLORATORY (post hoc): (1) which DECAPOD seeds jammed or needed guesses; (2) is forced-only growth from a decapod
seed a smooth, LOCAL now? Sector spread SS (as in ../local_deciders, 16 sectors) of placement rounds in the 5-7 edge band,
for zero-guess DECAPOD seeds vs FILLABLE seeds (run 0 of each, regrown deterministically with the placement rounds)."""
import os, sys, json, math, cmath, random
from multiprocessing import Pool
import decapod_seed as D
L, S = D.L, D.S


def grow_rounds(args):
    s, ring, rs = args
    rng = random.Random(rs); P = L.Patch(ring); n0 = len(P.tris); r = 0; rnd = {}
    while len(P.tris) - n0 < D.N_ADD:
        r += 1
        fr = [e for e in P.frontier() if abs((e[0] + e[1]) / 2) > D.APO + 1e-6]
        forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                return s, None
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= D.N_ADD:
                break
            if P.legal(t):
                P.add(t); rnd[D.dkey(t)] = (r, D.cen(t)); placed += 1
        if placed == 0:
            if forced:
                continue
            cs = sorted(D.candidates(P, *fr[0][:3]), key=lambda u: (u[0], L.key(u[1]), L.key(u[2]), L.key(u[3])))
            t = rng.choice(cs); P.add(t); rnd[D.dkey(t)] = (r, D.cen(t))
    band = [(cmath.phase(c), x) for x, c in rnd.values() if 5 * S <= abs(c) <= 7 * S]
    secs = [[] for _ in range(16)]
    for a, x in band:
        secs[int((a % (2 * math.pi)) / (2 * math.pi) * 16) % 16].append(x)
    if any(not v for v in secs):
        return s, None
    med = lambda v: sorted(v)[len(v) // 2]
    ms = [med(v) for v in secs]
    return s, dict(SS=(max(ms) - min(ms)) / med([x for _, x in band]), rounds=r)


if __name__ == "__main__":
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    R = [json.loads(l) for l in open(os.path.join(D.RES, "runs.jsonl"))]
    by = {}
    for r in R:
        by.setdefault(r["seed"], []).append(r)
    ring = lambda x: [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    dec = [x for x in seeds if x["kind"] == "DECAPOD"]; fil = [x for x in seeds if x["kind"] == "FILLABLE"]
    out = ["EXPLORATORY (post hoc)"]
    jam_all = [x["seed"] for x in dec if all(r["status"] == "JAM" for r in by[x["seed"]])]
    jam_some = [x["seed"] for x in dec if any(r["status"] == "JAM" for r in by[x["seed"]]) and x["seed"] not in jam_all]
    guess = [x["seed"] for x in dec if x["seed"] not in jam_all + jam_some and any(len(r["guesses"]) for r in by[x["seed"]])]
    out.append(f"1. DECAPOD seeds: {len(dec)}; jam in all 3 runs {len(jam_all)}; jam in some runs {len(jam_some)} {jam_some}; "
               f"no jam but guessed {guess}")
    jr = [r for x in dec for r in by[x['seed']] if r['status'] == 'JAM']
    out.append(f"   jam distance from centre (edges): {sorted(round(abs(complex(*r['jam'])), 2) for r in jr)}; "
               f"tiles laid before jamming: {sorted(r['tiles'] for r in jr)}")
    zero = [x for x in dec if all(r["status"] == "ok" and not r["guesses"] for r in by[x["seed"]])]
    tasks = [(x["seed"], ring(x), D.SEED0 + 100 * x["seed"]) for x in zero[:12] + fil]
    with Pool(4) as p:
        res = dict(p.map(grow_rounds, tasks))
    zs = [res[x["seed"]]["SS"] for x in zero[:12] if res[x["seed"]]]
    fs = [res[x["seed"]]["SS"] for x in fil if res[x["seed"]]]
    out.append(f"2. sector spread SS in the 5-7 edge band (smaller = smoother, more local now):")
    out.append(f"   zero-guess DECAPOD seeds (first 12): median {sorted(zs)[len(zs) // 2]:.2f}; {sorted(round(v, 2) for v in zs)}")
    out.append(f"   FILLABLE seeds: {sorted(round(v, 2) for v in fs)}")
    out.append(f"   rounds to 800 tiles: DECAPOD {[res[x['seed']]['rounds'] for x in zero[:12] if res[x['seed']]]}, "
               f"FILLABLE {[res[x['seed']]['rounds'] for x in fil if res[x['seed']]]}")
    print("\n".join(out))
    open(os.path.join(D.RES, "smoothness_EXPLORATORY.txt"), "w").write("\n".join(out) + "\n")

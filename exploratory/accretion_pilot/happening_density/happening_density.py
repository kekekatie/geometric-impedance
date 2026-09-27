#!/usr/bin/env python3
"""
happening_density.py -- does a quiet place have a wider now? (PREREGISTRATION.md, frozen before this file.)
Ring-of-Gromits growth (../soft_zone machinery, corrected vertex check) with the LEFT half throttled: forced
placements there happen with probability 0.25 per round. Holes are poked in both halves and re-laid; the width
of the now is compared in SPACE (distance behind the front) and in TIME (age of soft holes).
Incremental: results/runs.jsonl; `--summary` evaluates H0-H2.
"""
from __future__ import annotations
import os, sys, json, random, time, collections
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "soft_zone"))
import soft_zone as SZ
L = SZ.L
S = L.SCALE_LEN
N_ADD, RUNS, SEED0, P_SLOW = 500, 8, 20260930, 0.25
BINS = [(0, 1), (1, 2), (2, 4)]
HOLES = 4
RES = os.path.join(HERE, "results"); OUT = os.path.join(RES, "runs.jsonl")
half = lambda z: "slow" if z.real < 0 else "fast"


def grow(rng):
    seed = L.seed_patch(0j, 3 * S)
    P = L.Patch(seed); n0 = len(P.tris)
    rnd = {L.canon(t): 0 for t in seed}; r = 0; guesses = 0; placed_in = collections.Counter()
    while len(P.tris) - n0 < N_ADD:
        r += 1
        fr = P.frontier()
        forced = {}
        for e in fr:
            cs = P.candidates(*e[:3])
            if not cs:
                return P, rnd, r, guesses, placed_in, "JAM"
            if len(cs) == 1:
                forced.setdefault(L.canon(cs[0]), (cs[0], half((e[0] + e[1]) / 2)))
        placed = 0
        for k, (t, h) in forced.items():
            if len(P.tris) - n0 >= N_ADD:
                break
            if h == "slow" and rng.random() >= P_SLOW:
                continue
            if P.legal(t):
                P.add(t); rnd[k] = r; placed += 1; placed_in[h] += 1
        if placed == 0:
            cs = P.candidates(*fr[0][:3])
            t = rng.choice(sorted(cs, key=lambda u: sorted(L.canon(u)[1])))
            P.add(t); rnd[L.canon(t)] = r; guesses += 1; placed_in[half(SZ.centroid(t))] += 1
    return P, rnd, r, guesses, placed_in, "ok"


def run(k):
    rng = random.Random(SEED0 + k); t0 = time.time()
    P, rnd, rounds, guesses, placed_in, status = grow(rng)
    tiles = list(P.tris); mids = [(e[0] + e[1]) / 2 for e in P.frontier()]
    info = [(SZ.centroid(t), min(abs(SZ.centroid(t) - m) for m in mids) / S) for t in tiles if abs(SZ.centroid(t)) >= 4 * S]
    holes = []
    for h in ("slow", "fast"):
        for lo, hi in BINS:
            pool = [c for c, d in info if lo <= d < hi and half(c) == h]
            rng.shuffle(pool); chosen = []
            for c in pool:
                if all(abs(c - q) > 2 * SZ.RHO * S for q in chosen):
                    chosen.append(c)
                if len(chosen) == HOLES:
                    break
            for c in chosen:
                removed = [t for t in tiles if abs(SZ.centroid(t) - c) <= SZ.RHO * S]
                remaining = [t for t in tiles if abs(SZ.centroid(t) - c) > SZ.RHO * S]
                A = sum(SZ.area(t) for t in removed)
                orig = {L.canon(t) for t in removed}
                diff = 0
                for a in range(SZ.ATTEMPTS):
                    laid, done = SZ.refill(remaining, c, A, random.Random((SEED0 + k) * 1000 + len(holes) * 10 + a))
                    if done and frozenset(L.canon(t) for t in laid) != orig:
                        diff += 1
                age = rounds - sum(rnd[L.canon(t)] for t in removed) / len(removed)
                holes.append(dict(half=h, bin=[lo, hi], dist=round(min(abs(c - m) for m in mids) / S, 3),
                                  age=round(age, 2), soft=diff > 0))
    # how far the slow half lags: mean radius of frontier midpoints per half
    lag = {h: sum(abs(m) for m in mids if half(m) == h) / max(1, sum(1 for m in mids if half(m) == h)) / S for h in ("slow", "fast")}
    return dict(run=k, status=status, rounds=rounds, guesses=guesses, placed={h: placed_in[h] for h in ("slow", "fast")},
                front_radius=lag, holes=holes, seconds=round(time.time() - t0))


def summary():
    import numpy as np
    R = [json.loads(l) for l in open(OUT)]
    lines = [f"runs {len(R)}: statuses {[r['status'] for r in R]}, rounds {[r['rounds'] for r in R]}, guesses {[r['guesses'] for r in R]}"]
    hd = {h: np.mean([r["placed"][h] / r["rounds"] for r in R]) for h in ("slow", "fast")}
    lines.append(f"  happening density (tiles per round): slow {hd['slow']:.2f}, fast {hd['fast']:.2f} (ratio {hd['slow'] / hd['fast']:.2f})")
    lines.append(f"  front radius (edges): slow {np.mean([r['front_radius']['slow'] for r in R]):.1f}, fast {np.mean([r['front_radius']['fast'] for r in R]):.1f}")
    H = [h for r in R for h in r["holes"]]
    F = {}
    for hf in ("slow", "fast"):
        for lo, hi in BINS:
            b = [h for h in H if h["half"] == hf and h["bin"] == [lo, hi]]
            F[(hf, lo)] = np.mean([h["soft"] for h in b]) if b else float("nan")
            lines.append(f"  {hf} half, distance {lo}-{hi}: {len(b):>3} holes, freedom {F[(hf, lo)]:.2f}, "
                         f"median age {np.median([h['age'] for h in b]) if b else float('nan'):.1f} rounds")
    soft_age = {hf: [h["age"] for h in H if h["half"] == hf and h["soft"]] for hf in ("slow", "fast")}
    ma = {hf: (float(np.median(v)) if v else float("nan")) for hf, v in soft_age.items()}
    h0 = hd["slow"] < 0.6 * hd["fast"]
    h1 = F[("slow", 2)] <= 0.05 and F[("fast", 2)] <= 0.05 and all(abs(F[("slow", lo)] - F[("fast", lo)]) <= 0.2 for lo in (0, 1))
    h2 = ma["slow"] >= 2 * ma["fast"]
    lines += [f"  H0 (manipulation): {'PASS' if h0 else 'FAIL'}  slow/fast happening density {hd['slow'] / hd['fast']:.2f} (need < 0.6)",
              f"  H1: {'HELD  ' if h1 else 'FAILED'}  spatial width the same in both halves: freedom slow "
              f"{[round(F[('slow', lo)], 2) for lo, _ in BINS]} vs fast {[round(F[('fast', lo)], 2) for lo, _ in BINS]}",
              f"  H2: {'HELD  ' if h2 else 'FAILED'}  temporal width wider where quiet: median age of soft holes slow "
              f"{ma['slow']:.1f} vs fast {ma['fast']:.1f} rounds (need >= 2x); n soft = {len(soft_age['slow'])}, {len(soft_age['fast'])}"]
    print("\n".join(lines))
    open(os.path.join(RES, "happening_density_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    os.makedirs(RES, exist_ok=True)
    if "--summary" in sys.argv:
        summary(); sys.exit(0)
    done = {json.loads(l)["run"] for l in open(OUT)} if os.path.exists(OUT) else set()
    todo = [k for k in range(RUNS) if k not in done]
    with Pool(4, maxtasksperchild=1) as p:
        for res in p.imap_unordered(run, todo):
            with open(OUT, "a") as f:
                f.write(json.dumps(res) + "\n")
            print(f"run {res['run']}: {res['status']}, {res['rounds']} rounds, {len(res['holes'])} holes, {res['seconds']} s", flush=True)
    summary()

#!/usr/bin/env python3
"""
slack.py -- is each choice the reader taking in one digit? (PREREGISTRATION.md, frozen before this file.)
The wiggle room F of a patch: all hidden-window offsets t consistent with every vertex (its perp address minus t lies in
its layer's pentagon of the true Penrose window). Tracked through forced growth, at choices (both options) and in decapod
worlds. `python3 slack.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, random, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("thread_influence", "window_cells", "structure_clock"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import thread_influence as T
import window_cells as WC
import structure_clock as SC
F_, M, D, L, S = T.F, T.M, T.D, T.L, T.S
WIN = WC.window((1, -1, 1, -1))
ZERO, REL = 1e-9, 1e-6
RES = os.path.join(HERE, "results")


def clip(poly, n, c):
    """keep points with n.t >= c (Sutherland-Hodgman)."""
    out = []
    f = lambda p: n[0] * p[0] + n[1] * p[1] - c
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        fa, fb = f(a), f(b)
        if fa >= 0:
            out.append(a)
        if (fa >= 0) != (fb >= 0):
            s = fa / (fa - fb); out.append((a[0] + s * (b[0] - a[0]), a[1] + s * (b[1] - a[1])))
    return out


def area(poly):
    if len(poly) < 3:
        return 0.0
    return 0.5 * abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))))


def constraints(tiles, rank):
    """per (layer rank, side) the tightest c in n.t >= c."""
    K, pos, conf = M.lift(tiles)
    cmax = {}
    for v, k in K.items():
        rk = rank[int(k.sum())]; z = M.perp(k); n, h = WIN[rk]
        for i, (nx, ny) in enumerate(n):
            c = nx * z.real + ny * z.imag - h
            if c > cmax.get((rk, i), -1e18):
                cmax[(rk, i)] = c
    return cmax


def region(*cms):
    poly = [(-50.0, -50.0), (50.0, -50.0), (50.0, 50.0), (-50.0, 50.0)]
    keys = set().union(*cms)
    for key in keys:
        c = max(cm.get(key, -1e18) for cm in cms)
        rk, i = key
        poly = clip(poly, WIN[rk][0][i], c)
        if not poly:
            return []
    return poly


def rank_of(tiles):
    K, _, _ = M.lift(tiles)
    lays = sorted({int(k.sum()) for k in K.values()})
    assert len(lays) == 4, lays
    return {l: i for i, l in enumerate(lays)}


def ordinary(k):
    rng = random.Random(T.SEED0 + k); c0 = T.centres()[k]
    P = L.Patch(L.seed_patch(c0, 3 * S)); n0 = len(P.tris); r = 0
    rank = rank_of(P.tris)
    a0 = area(region(constraints(P.tris, rank))); trace = [(0, a0, "start")]; choices = []; forced_steps = []
    while len(P.tris) - n0 < T.N_ADD:
        r += 1
        fr = P.frontier(); forced = {}; jam = False
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = True; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        if jam:
            break
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= T.N_ADD:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed:
            a = area(region(constraints(P.tris, rank)))
            forced_steps.append((trace[-1][1], a)); trace.append((r, a, "forced"))
            continue
        if forced:
            continue
        e = fr[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
        base = list(P.tris); cm0 = constraints(base, rank)
        aF = area(region(cm0))
        rec = dict(slice=r, n_options=len(cs), area=aF)
        if len(cs) == 2:
            cmA = constraints(base + [cs[0]], rank); cmB = constraints(base + [cs[1]], rank)
            aA, aB = area(region(cmA)), area(region(cmB)); aAB = area(region(cmA, cmB))
            rec.update(aA=aA, aB=aB, overlap=aAB)
        t = rng.choice(cs); rec["picked"] = cs.index(t)
        P.add(t); choices.append(rec)
        trace.append((r, area(region(constraints(P.tris, rank))), "choice"))
    return dict(world=k, trace=trace, choices=choices, forced_steps=forced_steps, a0=a0)


def decapod(s):
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    x = next(v for v in seeds if v["seed"] == s)
    ring = [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    P, rnd, rounds, guesses, status = SC.grow(ring, 800, D.SEED0 + 100 * s)
    tiles = list(P.tris); rank = rank_of(tiles)
    trace = []
    for r in range(0, rounds + 1):
        pre = [t for t in tiles if rnd[D.dkey(t)] <= r]
        try:
            a = area(region(constraints(pre, rank)))
        except KeyError:
            a = None                                   # a layer not yet present in the prefix
        trace.append((r, a))
    first0 = next((r for r, a in trace if a is not None and a < ZERO), None)
    return dict(seed=s, guesses=guesses, status=status, rounds=rounds, ring_area=trace[0][1], final=trace[-1][1], first_zero=first0,
                trace=trace)


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4, maxtasksperchild=1) as p:
        O = p.map(ordinary, range(T.N_WORLDS))
        Dp = p.map(decapod, range(2, 10))
    json.dump(dict(ordinary=O, decapod=Dp), open(os.path.join(RES, "worlds.json"), "w"))
    lines = []
    empty = sum(1 for w in O for _, a, _ in w["trace"] if a <= 0)
    lines.append(f"  S0: {'PASS' if empty == 0 else 'FAIL'}  F non-empty (area > 0) in every recorded ordinary patch; empties {empty}")
    fs = [(b, a) for w in O for b, a in w["forced_steps"]]
    same = sum(abs(a - b) <= REL * max(b, 1e-300) for b, a in fs)
    shrink = [1 - a / b for b, a in fs if b > 0 and abs(a - b) > REL * b]
    lines.append(f"  S1: {'HELD  ' if same >= 0.99 * len(fs) else 'FAILED'}  forced slices with unchanged wiggle room: {same}/{len(fs)} "
                 f"(need >= 99%); changed ones shrank by {sorted(round(x, 4) for x in shrink)[:20]}")
    two = [c for w in O for c in w["choices"] if c["n_options"] == 2]
    ok2 = [c for c in two if c["aA"] > 0 and c["aB"] > 0 and c["overlap"] < 0.01 * c["area"] and abs(c["aA"] + c["aB"] - c["area"]) < 0.01 * c["area"]]
    lines.append(f"  S2: {'HELD  ' if len(ok2) >= 0.9 * len(two) else 'FAILED'}  choices that cut F cleanly in two: {len(ok2)}/{len(two)} (need >= 90%)")
    lines.append("      per choice (area, A share, B share, overlap share): " + "; ".join(
        f"{c['area']:.4g}, {c['aA'] / c['area']:.3f}, {c['aB'] / c['area']:.3f}, {c['overlap'] / c['area']:.3f}" for c in two[:30]))
    mins = [min(c["aA"], c["aB"]) / c["area"] for c in two if c["area"] > 0]
    gold = sum(abs(x - (2 - WC.TAU)) <= 0.05 for x in mins)                      # 1/tau^2 = 2 - tau = 0.382
    lines.append(f"  S3: {'HELD  ' if mins and gold >= 0.6 * len(mins) else 'FAILED'}  smaller share within 0.05 of 0.382 in {gold}/{len(mins)} "
                 f"(need >= 60%); smaller shares {sorted(round(x, 3) for x in mins)}")
    fin = [d["final"] for d in Dp]
    lines.append(f"  S4: {'HELD  ' if all(a is not None and a < ZERO for a in fin) else 'FAILED'}  decapod final area < {ZERO}: {[f'{a:.2e}' for a in fin]}; "
                 f"guesses {[d['guesses'] for d in Dp]}")
    lines.append(f"  reported: decapod bare-ring areas {[None if d['ring_area'] is None else round(d['ring_area'], 4) for d in Dp]}; "
                 f"first slice with zero area {[d['first_zero'] for d in Dp]}")
    bits = [(i + 1, math.log2(w["a0"] / c["area"]) if c["area"] > 0 else None) for w in O for i, c in enumerate(w["choices"])]
    by = collections.defaultdict(list)
    for i, b in bits:
        if b is not None:
            by[i].append(b)
    lines.append("  reported: bits read before the n-th choice (median over worlds): " + ", ".join(f"n={i}: {np.median(v):.2f}" for i, v in sorted(by.items())))
    lines.append(f"  reported: starting wiggle room a0 per world {[round(w['a0'], 4) for w in O]}")
    print("\n".join(lines))
    open(os.path.join(RES, "slack_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

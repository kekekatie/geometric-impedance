#!/usr/bin/env python3
"""
two_decapods.py -- can two centres coexist? (PREREGISTRATION.md, frozen before this file.)
TWO: decapod ring A at the origin + decapod ring B (next seed type) translated by v = n(e_j + e_{j+1}); forced-only
growth with both decagon walls. CTRL: ring A + the tiles of A's own grown world within 2 edges of v. Track merging, jams,
and the kind of the merged patch's wiggle room F. `python3 two_decapods.py`.
"""
from __future__ import annotations
import os, sys, json, math, cmath, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "slack"))
import slack as Sl
import classify_EXPLORATORY as CL
SC, M, D, L, S = Sl.SC, Sl.M, Sl.D, Sl.L, Sl.S
SEEDS, NS, JS, AFTER, MAXT, PIECE_R = [2, 3, 4, 5, 6, 7, 8, 9], [5, 7], [0, 2], 400, 3000, 2.0
RES = os.path.join(HERE, "results")
eps = lambda j: S * cmath.exp(1j * math.radians(18 + 72 * (j % 5)))


def ring_of(s):
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    x = next(v for v in seeds if v["seed"] == s)
    return [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]


def shift(tiles, v):
    return [(t[0], t[1] + v, t[2] + v, t[3] + v) for t in tiles]


def connected(P, a, b):
    """is some tile with key in set a connected (via shared edges) to some tile with key in set b?"""
    adj = collections.defaultdict(list)
    for ek, ts in P.edges.items():
        if len(ts) == 2:
            k0, k1 = D.dkey(ts[0]), D.dkey(ts[1]); adj[k0].append(k1); adj[k1].append(k0)
    start = next(iter(a)); seen = {start}; stack = [start]
    while stack:
        u = stack.pop()
        if u in b:
            return True
        for w in adj[u]:
            if w not in seen:
                seen.add(w); stack.append(w)
    return False


def grow(seed_tiles, centres, a_keys, b_keys):
    P = L.Patch(list(seed_tiles)); n0 = len(P.tris); r = 0; merged_at = None; n_merge = None; status = "max"; jam_edge = None
    walled = lambda e: any(abs((e[0] + e[1]) / 2 - c) <= D.APO + 1e-6 for c in centres)
    while len(P.tris) - n0 < MAXT:
        r += 1
        forced = {}; jam = None
        for e in P.frontier():
            if walled(e):
                continue
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = e; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        if jam is not None:
            status = "JAM"; jam_edge = (jam[0] + jam[1]) / 2; break
        placed = 0
        for t in forced.values():
            if P.legal(t):
                P.add(t); placed += 1
        if not placed:
            status = "STUCK"; break
        if merged_at is None and connected(P, a_keys, b_keys):
            merged_at = r; n_merge = len(P.tris)
        if merged_at is not None and len(P.tris) - n_merge >= AFTER:
            status = "after"; break
    kind = None
    if merged_at is not None:
        try:
            rank = Sl.rank_of(list(P.tris)); kind = CL.classify(Sl.constraints(list(P.tris), rank))[0]
        except AssertionError:
            kind = "layers?"
    return dict(status=status, slices=r, tiles=len(P.tris), merged_at=merged_at, kind=kind,
                jam_edge=None if jam_edge is None else [jam_edge.real, jam_edge.imag])


def two(args):
    s, n, j = args
    A = ring_of(s); s2 = SEEDS[(SEEDS.index(s) + 1) % len(SEEDS)]; v = n * (eps(j) + eps(j + 1))
    B = shift(ring_of(s2), v)
    out = grow(A + B, [0j, v], {D.dkey(t) for t in A}, {D.dkey(t) for t in B})
    if out["jam_edge"]:
        z = complex(*out["jam_edge"]); u = v / abs(v)
        out["jam_from_bisector"] = abs(((z - v / 2) * u.conjugate()).real) / S
    out.update(kind_run="TWO", seed=s, seed_b=s2, n=n, j=j, dist=abs(v) / S)
    return out


def ctrl(args):
    s, n, j = args
    A = ring_of(s); v = n * (eps(j) + eps(j + 1))
    Pw, rnd, rounds, g, st = SC.grow(A, 3000, D.SEED0 + 100 * s)
    piece = [t for t in Pw.tris if abs(SC.cen(t) - v) <= PIECE_R * S]
    out = grow(A + piece, [0j], {D.dkey(t) for t in A}, {D.dkey(t) for t in piece}) if piece else dict(status="NO PIECE")
    out.update(kind_run="CTRL", seed=s, n=n, j=j, dist=abs(v) / S, piece=len(piece))
    return out


def main():
    os.makedirs(RES, exist_ok=True)
    cfg = [(s, n, j) for s in SEEDS for n in NS for j in JS]
    with Pool(4, maxtasksperchild=1) as p:
        T = p.map(two, cfg)
        json.dump(dict(two=T), open(os.path.join(RES, "worlds_two.json"), "w"), default=lambda o: o.item() if hasattr(o, "item") else str(o))
        C = p.map(ctrl, cfg)
    json.dump(dict(two=T, ctrl=C), open(os.path.join(RES, "worlds.json"), "w"), default=lambda o: o.item() if hasattr(o, "item") else str(o))
    lines = []
    for name, R in (("TWO", T), ("CTRL", C)):
        lines.append(f"{name}: statuses {dict(collections.Counter(r['status'] for r in R))}; merged {sum(r.get('merged_at') is not None for r in R)}/{len(R)}; "
                     f"merged-F kinds {dict(collections.Counter(r.get('kind') for r in R if r.get('merged_at') is not None))}")
        lines.append(f"      jammed before merging: {sum(r['status'] == 'JAM' and r.get('merged_at') is None for r in R)}")
    tm = [r for r in T if r.get("merged_at") is not None]
    t1n = sum(r["kind"] == "empty" and r["status"] == "JAM" for r in tm)
    t1 = bool(tm) and t1n >= 0.9 * len(tm)
    cm = [r for r in C if r.get("merged_at") is not None]
    t2n = sum(r["kind"] == "point" and r["status"] != "JAM" for r in cm)
    t2 = bool(cm) and t2n >= 0.9 * len(cm)
    jd = [r["jam_from_bisector"] for r in T if r["status"] == "JAM" and "jam_from_bisector" in r]
    t3 = bool(jd) and float(np.median(jd)) < 2
    lines += [f"  T1: {'HELD  ' if t1 else 'FAILED'}  merged TWO worlds with empty F that then jam: {t1n}/{len(tm)} (need >= 90%)",
              f"  T2: {'HELD  ' if t2 else 'FAILED'}  merged CTRL worlds with point F and no jam: {t2n}/{len(cm)} (need >= 90%)",
              f"  T3: {'HELD  ' if t3 else 'FAILED'}  TWO jams: median distance from the A-B bisector {np.median(jd) if jd else float('nan'):.2f} edges "
              f"(need < 2); values {sorted(round(x, 2) for x in jd)}"]
    lines.append("  per TWO world (seed, seedB, n, j, status, merged slice, kind): " + "; ".join(
        f"{r['seed']},{r['seed_b']},{r['n']},{r['j']},{r['status']},{r.get('merged_at')},{r.get('kind')}" for r in T))
    lines.append("  per CTRL world (seed, n, j, piece, status, merged slice, kind): " + "; ".join(
        f"{r['seed']},{r['n']},{r['j']},{r.get('piece')},{r['status']},{r.get('merged_at')},{r.get('kind')}" for r in C))
    print("\n".join(lines))
    open(os.path.join(RES, "two_decapods_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

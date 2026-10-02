#!/usr/bin/env python3
"""
worm_lines.py -- does a decapod keep its memory on its ten ribbons? (PREREGISTRATION.md, frozen before this file.)
Trace the ten ribbons (rhomb chains through parallel edges) outward from the decagon's edges; split the world into the
wedges between them, and each wedge into two halves; compare perp-space window offsets ACROSS ribbons vs WITHIN wedges.
`python3 worm_lines.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, cmath, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "perp_map"))
import perp_map as M
D, L, S = M.D, M.L, M.S
N_TILES, R_MIN, MIN_LAYER, MIN_CELL = 4000, 2.5, 40, 5
RES = os.path.join(HERE, "results")
ek = lambda p, q: frozenset((L.key(p), L.key(q)))
is_leg = lambda p, q: abs(abs(q - p) - S) < 1e-4 * S


def build(tiles):
    edge_tiles = collections.defaultdict(list)
    for t in tiles:
        for p, q in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
            edge_tiles[ek(p, q)].append(t)
    return edge_tiles


def legs(t):
    return [(p, q) for p, q in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])) if is_leg(p, q)]


def partner(t, edge_tiles):
    for p, q in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
        if not is_leg(p, q):
            others = [u for u in edge_tiles[ek(p, q)] if u is not t and L.canon(u) != L.canon(t)]
            return others[0] if others else None
    return None


def trace(e0, edge_tiles):
    p0, q0 = e0
    ts = [t for t in edge_tiles[ek(p0, q0)] if abs(sum(t[1:]) / 3) > D.APO]
    if not ts:
        return []
    t = ts[0]; entry = (p0, q0); pts = []; seen = set()
    for _ in range(600):
        pt = partner(t, edge_tiles)
        if pt is None:
            break
        key = frozenset((L.canon(t), L.canon(pt)))
        if key in seen:
            break
        seen.add(key)
        pts.append((sum(t[1:]) / 3 + sum(pt[1:]) / 3) / 2)
        j = M.edge_dir(*entry)[0]
        cand = [(p, q) for p, q in legs(t) + legs(pt) if M.edge_dir(p, q)[0] == j and ek(p, q) != ek(*entry)]
        if not cand:
            break
        ex = cand[0]
        nxt = [u for u in edge_tiles[ek(*ex)] if L.canon(u) not in (L.canon(t), L.canon(pt))]
        if not nxt:
            break
        t, entry = nxt[0], ex
    return pts


def angle_at(pts, rho):
    """interpolated (unwrapped) angle of a ribbon polyline at radius rho; None if it never reaches rho"""
    angs = np.unwrap([cmath.phase(z) for z in pts]); rads = [abs(z) for z in pts]
    for i in range(1, len(pts)):
        a, b = rads[i - 1], rads[i]
        if (a - rho) * (b - rho) <= 0 and a != b:
            f = (rho - a) / (b - a)
            return float(angs[i - 1] + f * (angs[i] - angs[i - 1]))
    return None


def world(args):
    s, kind, ring = args
    tiles, _, guesses, status = M.grow(ring, N_TILES, D.SEED0 + 100 * s, wall=True)
    et = build(tiles)
    ribbons = [trace(e, et) for e in D.EDGES]
    reach = [max((abs(z) for z in r), default=0) / S for r in ribbons]
    out = dict(seed=s, kind=kind, status=status, guesses=len(guesses), reach=reach,
               ribbons=[[[z.real / S, z.imag / S] for z in r] for r in ribbons])
    if min(reach) < 4.0:
        out["excluded"] = True
        return out
    rmax = min(reach) * S
    K, pos, conf = M.lift(tiles)
    lay_count = collections.Counter(int(k.sum()) for v, k in K.items() if R_MIN * S <= abs(pos[v]) <= rmax)
    lays = [l for l, c in lay_count.items() if c >= MIN_LAYER]
    cells = collections.defaultdict(list); allz = collections.defaultdict(list)
    straight = []
    for r in ribbons:
        a1, a2 = angle_at(r, R_MIN * S + 0.01 * S), angle_at(r, rmax - 0.01 * S)
        if a1 is not None and a2 is not None:
            straight.append(math.degrees(a2 - a1) / ((rmax / S) - R_MIN))
    for v, k in K.items():
        z = pos[v]; rho = abs(z)
        if not (R_MIN * S <= rho <= rmax) or int(k.sum()) not in lays:
            continue
        phis = [angle_at(r, rho) for r in ribbons]
        if any(p is None for p in phis):
            continue
        th = cmath.phase(z)
        for w in range(10):
            a = phis[w] % (2 * math.pi); b = phis[(w + 1) % 10] % (2 * math.pi)
            span = (b - a) % (2 * math.pi); off = (th - a) % (2 * math.pi)
            if off < span:
                half = 0 if off < span / 2 else 1
                cells[(w, half, int(k.sum()))].append(M.perp(k)); break
        allz[int(k.sum())].append(M.perp(k))
    mean = {c: complex(np.mean(v)) for c, v in cells.items() if len(v) >= MIN_CELL}

    def dist(a, b):
        ds = [abs(mean[(a[0], a[1], l)] - mean[(b[0], b[1], l)]) for l in lays if (a[0], a[1], l) in mean and (b[0], b[1], l) in mean]
        return float(np.mean(ds)) if ds else None
    across = [dist((w, 1), ((w + 1) % 10, 0)) for w in range(10)]
    within = [dist((w, 0), (w, 1)) for w in range(10)]
    a_ok = [x for x in across if x is not None]; w_ok = [x for x in within if x is not None]
    wmean = {l: complex(np.mean(v)) for l, v in allz.items()}
    offs = {f"{w}-{h}": float(np.mean([abs(mean[(w, h, l)] - wmean[l]) for l in lays if (w, h, l) in mean]))
            for w in range(10) for h in (0, 1) if any((w, h, l) in mean for l in lays)}
    out.update(rmax=rmax / S, layers=lays, across=across, within=within, ratio=float(np.mean(a_ok) / np.mean(w_ok)),
               straightness_deg_per_edge=straight, offsets=offs, n_cells=len(mean))
    return out


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
    t0 = all(not w.get("excluded") for w in W)
    for w in W:
        if w.get("excluded"):
            lines.append(f"  {w['kind']:<8} seed {w['seed']:>3}: EXCLUDED, ribbon reach {[round(x, 1) for x in w['reach']]}"); continue
        lines.append(f"  {w['kind']:<8} seed {w['seed']:>3}: {w['status']}, guesses {w['guesses']}, ribbon reach "
                     f"{min(w['reach']):.1f}-{max(w['reach']):.1f} edges (analysis to {w['rmax']:.1f}), cells {w['n_cells']}, "
                     f"across {np.mean([x for x in w['across'] if x is not None]):.3f}, within "
                     f"{np.mean([x for x in w['within'] if x is not None]):.3f}, ratio {w['ratio']:.2f}; ribbon turning "
                     f"{np.round(w['straightness_deg_per_edge'], 1).tolist()} deg/edge")
    dr = [w["ratio"] for w in W if w["kind"] == "DECAPOD" and not w.get("excluded")]
    fr = [w["ratio"] for w in W if w["kind"] == "FILLABLE" and not w.get("excluded")]
    t1 = sum(r > 1.2 for r in dr) >= 7
    t2 = bool(fr) and bool(dr) and float(np.median(fr)) < float(np.median(dr))
    lines += [f"  T0: {'PASS' if t0 else 'FAIL'}  all ten ribbons traced >= 4 edges out in every world",
              f"  T1: {'HELD  ' if t1 else 'FAILED'}  DECAPOD across/within ratio > 1.2 in {sum(r > 1.2 for r in dr)}/{len(dr)} "
              f"(need >= 7); ratios {sorted(round(r, 2) for r in dr)}",
              f"  T2: {'HELD  ' if t2 else 'FAILED'}  FILLABLE median ratio {np.median(fr) if fr else float('nan'):.2f} < DECAPOD median "
              f"{np.median(dr) if dr else float('nan'):.2f}; FILLABLE ratios {sorted(round(r, 2) for r in fr)}"]
    print("\n".join(lines))
    open(os.path.join(RES, "worm_lines_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

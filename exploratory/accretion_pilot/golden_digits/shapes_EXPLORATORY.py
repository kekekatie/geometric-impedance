#!/usr/bin/env python3
"""EXPLORATORY shape census (towards deriving the split). For every two-option choice in the 24 golden_digits worlds:
  * the SHAPE of the wiggle room F at the choice: number of corners and interior angles (in units of 36 degrees),
    side lengths relative to the longest;
  * the CUTTING LINE: a constraint of sibling A and one of sibling B lying on the same line with opposite normals;
  * where the line falls: through a corner of F? parallel to a side of F?
  * the two pieces' shapes and the measured smaller share.
`python3 shapes_EXPLORATORY.py`"""
import os, sys, math, random, collections, json
from multiprocessing import Pool
import numpy as np
import golden_digits as GD
Sl, T, F_, L, D, S = GD.Sl, GD.T, GD.F_, GD.L, GD.D, GD.S
TAU = GD.TAU


def clean(poly, eps=1e-12):
    out = []
    for p in poly:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > eps:
            out.append(p)
    if len(out) > 1 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= eps:
        out.pop()
    # drop collinear corners
    res = []
    for i in range(len(out)):
        a, b, c = out[i - 1], out[i], out[(i + 1) % len(out)]
        cr = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cr) > 1e-14:
            res.append(b)
    return res


def shape(poly):
    p = clean(poly)
    n = len(p)
    if n < 3:
        return None
    ang = []; sides = []
    for i in range(n):
        a, b, c = p[i - 1], p[i], p[(i + 1) % n]
        v1 = (a[0] - b[0], a[1] - b[1]); v2 = (c[0] - b[0], c[1] - b[1])
        cosv = (v1[0] * v2[0] + v1[1] * v2[1]) / (math.hypot(*v1) * math.hypot(*v2))
        ang.append(round(math.degrees(math.acos(max(-1, min(1, cosv)))) / 36, 3))
        sides.append(math.hypot(c[0] - b[0], c[1] - b[1]))
    m = max(sides)
    # canonical rotation of the angle sequence
    seqs = [tuple(ang[i:] + ang[:i]) for i in range(n)]; seqs += [tuple(reversed(s)) for s in seqs]
    return dict(n=n, angles=min(seqs), sides=sorted(round(s / m, 3) for s in sides), pts=p)


def cut_line(c0, cA, cB):
    best = None
    for ka, ca in cA.items():
        if ca <= c0.get(ka, -1e18) + 1e-12:
            continue
        na = Sl.WIN[ka[0]][0][ka[1]]
        for kb, cb in cB.items():
            if cb <= c0.get(kb, -1e18) + 1e-12:
                continue
            nb = Sl.WIN[kb[0]][0][kb[1]]
            if abs(na[0] + nb[0]) < 1e-9 and abs(na[1] + nb[1]) < 1e-9 and abs(ca + cb) < 1e-9:
                best = (na, ca)
    return best


def task(k):
    rng = random.Random(GD.SEED0 + k); c0p = GD.centres()[k]
    P = L.Patch(L.seed_patch(c0p, 3 * S)); n0 = len(P.tris); rank = Sl.rank_of(P.tris); rows = []
    while len(P.tris) - n0 < GD.N_ADD:
        st, placed, anyf = F_.step(P)
        if st == "JAM":
            break
        if placed or anyf:
            continue
        e = P.frontier()[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
        if len(cs) == 2:
            base = list(P.tris); c0 = Sl.constraints(base, rank); pF = Sl.region(c0)
            if Sl.area(pF) > 0:
                cA = Sl.constraints(list(F_.sibling(base, cs[0])[0].tris), rank)
                cB = Sl.constraints(list(F_.sibling(base, cs[1])[0].tris), rank)
                pA, pB = Sl.region(cA), Sl.region(cB)
                aF = Sl.area(pF); sA, sB = Sl.area(pA) / aF, Sl.area(pB) / aF
                if sA > 0 and sB > 0:
                    sh = shape(pF); line = cut_line(c0, cA, cB)
                    thru = par = None
                    if line and sh:
                        n, c = line
                        thru = [i for i, q in enumerate(sh["pts"]) if abs(n[0] * q[0] + n[1] * q[1] - c) < 1e-9]
                        pts = sh["pts"]
                        par = any(abs(n[0] * (pts[(i + 1) % len(pts)][0] - pts[i][0]) + n[1] * (pts[(i + 1) % len(pts)][1] - pts[i][1])) < 1e-9
                                  for i in range(len(pts)))
                    small = pA if sA < sB else pB
                    rows.append(dict(world=k, share=min(sA, sB), F=sh and (sh["n"], sh["angles"], sh["sides"]),
                                     small=(shape(small) or {}).get("angles"), big=(shape(pB if sA < sB else pA) or {}).get("angles"),
                                     line=line is not None, through_corners=None if thru is None else len(thru), parallel_to_side=par,
                                     area=aF))
        P.add(rng.choice(cs))
    return rows


if __name__ == "__main__":
    with Pool(4, maxtasksperchild=1) as p:
        R = [r for out in p.map(task, range(24)) for r in out]
    json.dump(R, open(os.path.join(GD.RES, "shapes_rows.json"), "w"))
    lines = [f"EXPLORATORY shape census: {len(R)} two-option choices with both pieces live"]
    lines.append(f"  cutting line found (A and B constraints on one line, opposite sides): {sum(r['line'] for r in R)}/{len(R)}")
    byF = collections.Counter((r["F"][0], r["F"][1]) for r in R if r["F"])
    lines.append("  shapes of F at the choice (corners, angles in units of 36 deg): " + "; ".join(f"{k}: {v}" for k, v in byF.most_common()))
    tab = collections.defaultdict(collections.Counter)
    for r in R:
        if r["F"]:
            tab[(r["F"][0], r["F"][1])][(round(r["share"], 3), r["through_corners"], r["parallel_to_side"], r["small"], r["big"])] += 1
    for k, v in sorted(tab.items(), key=lambda kv: -sum(kv[1].values())):
        lines.append(f"  F = {k}:")
        for (sh, thr, par, sm, bg), n in v.most_common():
            lines.append(f"      share {sh} x{n}: line through {thr} corner(s), parallel to a side {par}; small piece {sm}, big piece {bg}")
    lines.append("  F side ratios by shape: " + "; ".join(f"{k}: {sorted({tuple(r['F'][2]) for r in R if r['F'] and (r['F'][0], r['F'][1]) == k})}" for k in byF))
    areas = sorted({round(r["area"], 6) for r in R})
    lines.append(f"  distinct F areas: {areas}; successive ratios {[round(areas[i + 1] / areas[i], 3) for i in range(len(areas) - 1)]}")
    print("\n".join(lines))
    open(os.path.join(GD.RES, "shapes_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")

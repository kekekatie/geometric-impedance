#!/usr/bin/env python3
"""EXPLORATORY (after the registered run; M3 failed on the whole defect set): measure each crack separately.
For every LOCAL world: group defect vertices into cracks (single-linkage, 1.5 edges); for each crack with >= 5 defects:
its length (largest extent), elongation, and whether it reaches the rim (its outermost defect within 3 edges of the
world's outermost tile in that 10-degree sector around the seed centre). Writes results/cracks_EXPLORATORY.txt."""
import os, math, cmath, collections
from multiprocessing import Pool
import numpy as np
import carry_forward as CF
L, S = CF.L, CF.S


def groups(pts, link=1.5):
    n = len(pts); par = list(range(n))
    def f(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for i in range(n):
        for j in range(i + 1, n):
            if abs(pts[i] - pts[j]) <= link:
                par[f(i)] = f(j)
    g = collections.defaultdict(list)
    for i in range(n):
        g[f(i)].append(pts[i])
    return list(g.values())


def world(k):
    P, bad, dk, n0 = CF.run((k, "LOCAL"), keep=True)
    c0 = CF.LN.centres()[k] / S
    pts = [complex(*v) / S for v in dk]
    cen = np.array([sum(t[1:]) / 3 for t in P.tris]) / S - c0
    out = []
    for g in groups(pts):
        if len(g) < 5:
            continue
        z = np.array(g)
        X = np.c_[z.real - z.real.mean(), z.imag - z.imag.mean()]
        w, v = np.linalg.eigh(X.T @ X / len(z))
        el = math.sqrt(w[-1] / max(w[0], 1e-12))
        u = complex(v[0, -1], v[1, -1]); proj = ((z - z.mean()) * u.conjugate()).real; length = float(np.ptp(proj))
        far = max(g, key=lambda p: abs(p - c0)); ang = cmath.phase(far - c0)
        sector = cen[np.abs(np.angle(cen * cmath.exp(-1j * ang))) <= math.radians(5)]
        rim = abs(far - c0) >= (np.max(np.abs(sector)) if len(sector) else 0) - 3
        out.append(dict(n=len(g), elong=el, length=length, rim=bool(rim), rmin=float(min(abs(p - c0) for p in g)), rmax=float(abs(far - c0))))
    return k, out


if __name__ == "__main__":
    with Pool(4, maxtasksperchild=1) as p:
        R = p.map(world, range(CF.LN.N_WORLDS))
    C = [c for _, cs in R for c in cs]
    lines = [f"EXPLORATORY cracks in the 24 LOCAL carry-forward worlds: {len(C)} cracks with >= 5 broken corners "
             f"(per world {sorted(len(cs) for _, cs in R)})",
             f"  elongation median {np.median([c['elong'] for c in C]):.1f}; >= 3 in {sum(c['elong'] >= 3 for c in C)}/{len(C)}",
             f"  length median {np.median([c['length'] for c in C]):.1f} edges (max {max(c['length'] for c in C):.1f})",
             f"  reaching the rim (still at the growing edge) {sum(c['rim'] for c in C)}/{len(C)}; radial span (outer - inner radius) median "
             f"{np.median([c['rmax'] - c['rmin'] for c in C]):.1f} edges"]
    print("\n".join(lines))
    open(os.path.join(CF.HERE, "results", "cracks_EXPLORATORY.txt"), "w").write("\n".join(lines) + "\n")

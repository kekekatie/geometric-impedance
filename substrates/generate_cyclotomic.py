#!/usr/bin/env python3
"""
Z^4 cyclotomic quasicrystals: 8-, 10- and 12-fold at matched perpendicular dimension.

An N-fold symmetric quasicrystal's natural module has rank phi(N), Euler's
totient. phi(8) = phi(10) = phi(12) = 4, so all three live in Z^4 with a
2-dimensional perpendicular space. This is what makes them comparable: the
earlier Z^n family varied perpendicular dimension along with everything else,
and the Z^5 Penrose construction carries a redundant fifth direction (measured
inert in discrete_vs_continuous.py).

Parallel space uses the basis zeta^k, k = 0..3, for zeta = exp(2i pi / N).
Perpendicular space uses the Galois conjugate zeta -> zeta^g, where g generates
the relevant part of the Galois group of Q(zeta_N).

    N = 8    silver ratio  1 + sqrt(2)     g = 3
    N = 10   golden ratio  (1+sqrt 5)/2    g = 3
    N = 12   platinum      2 + sqrt(3)     g = 5

Only the cyclotomic field changes. Lattice, rank, perpendicular dimension,
window construction and edge rule are identical across all three.
"""
import argparse, itertools, math
import numpy as np
from scipy.spatial import ConvexHull

GALOIS = {8: 3, 10: 3, 12: 5}

def projections(N):
    g = GALOIS[N]
    k = np.arange(4)
    par  = np.column_stack([np.cos(2*np.pi*k/N),     np.sin(2*np.pi*k/N)])
    perp = np.column_stack([np.cos(2*np.pi*g*k/N),   np.sin(2*np.pi*g*k/N)])
    return par, perp

def window_facets(perp_mat, scale=1.0):
    signs = np.array(list(itertools.product([-0.5, 0.5], repeat=4)))
    hull = ConvexHull(signs @ perp_mat)
    return hull.equations[:, :2], -hull.equations[:, 2] * scale

def generate(N, extent, offset=None, disorder=0.0, seed=0):
    par_mat, perp_mat = projections(N)
    offset = np.array([0.1123, 0.0847]) if offset is None else np.asarray(offset)
    A, b = window_facets(perp_mat)
    rng = np.random.default_rng(seed)
    axis = np.arange(-extent, extent + 1, dtype=np.int32)
    tail = np.array(list(itertools.product(axis, repeat=3)), dtype=np.int32)
    kept = []
    for first in axis:
        blk = np.empty((len(tail), 4), dtype=np.int32)
        blk[:, 0] = first; blk[:, 1:] = tail
        pp = blk @ perp_mat + offset
        if disorder > 0:
            pp = pp + rng.normal(0.0, disorder, pp.shape)
        keep = np.all(pp @ A.T <= b + 1e-9, axis=1)
        if keep.any():
            kept.append(blk[keep])
    lifts = np.concatenate(kept) if kept else np.zeros((0, 4), dtype=np.int32)
    return lifts, lifts @ par_mat, lifts @ perp_mat + offset

def build_edges(lifts):
    idx = {tuple(r): i for i, r in enumerate(lifts)}
    E = set()
    for i, row in enumerate(lifts):
        for ax in range(4):
            nb = list(row); nb[ax] += 1
            j = idx.get(tuple(nb))
            if j is not None: E.add((min(i, j), max(i, j)))
    return sorted(E)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--extent", type=int, default=16)
    ext = ap.parse_args().extent
    print(f"{'N-fold':>7} {'ratio':>12} {'verts':>7} {'edges':>7} {'mean deg':>9} "
          f"{'deg<3':>7} {'edge lens':>10} {'win verts':>10}")
    for N, nm in ((8, "silver"), (10, "golden"), (12, "platinum")):
        lf, par, perp = generate(N, ext); E = build_edges(lf)
        deg = np.zeros(len(lf), int)
        for u, v in E: deg[u] += 1; deg[v] += 1
        L = np.linalg.norm(par[[u for u,_ in E]] - par[[v for _,v in E]], axis=1)
        _, pm = projections(N)
        sg = np.array(list(itertools.product([-0.5,0.5], repeat=4))) @ pm
        nw = len(ConvexHull(sg).vertices)
        print(f"{N:>7} {nm:>12} {len(lf):7d} {len(E):7d} {deg.mean():9.3f} "
              f"{float((deg<3).mean()):7.1%} {len(set(np.round(L,6))):10d} {nw:10d}")

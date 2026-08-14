#!/usr/bin/env python3
"""
Cut-and-project quasicrystal generator for the Z^n -> 2D family.

Generalises generate_ab.py (n=4) to arbitrary n, so perpendicular-space
dimension becomes a controllable variable:

    n = 4   8-fold   perp dim 2    (Ammann-Beenker)
    n = 5  10-fold   perp dim 3
    n = 6  12-fold   perp dim 4
    n = 7  14-fold   perp dim 5

Parallel space is spanned by e_k = (cos(pi*k/n), sin(pi*k/n)); perpendicular
space by the remaining irreducible components of the same cyclic action. The
acceptance window is the projection of the unit n-cube into perpendicular
space, a zonotope whose 2^n signed vertex combinations give its convex hull.

Existing generators are kept separate rather than replaced: generate_ab.py and
generate_penrose.py use the standard octagonal and pentagonal windows and are
verified against the original substrates.
"""

import argparse
import csv
import itertools
import math
import os

import numpy as np
from scipy.spatial import ConvexHull


def projections(n):
    """Parallel (2D) and perpendicular (n-2 D) projection matrices for Z^n.

    Perpendicular space is taken as the orthogonal complement of the parallel
    plane, which is canonical and guarantees the dimension count 2 + (n-2).
    Identifying the individual irreducible blocks is unnecessary and was the
    source of a dimension error in an earlier version.
    """
    k = np.arange(n)
    par = np.column_stack([np.cos(np.pi * k / n), np.sin(np.pi * k / n)])
    par, _ = np.linalg.qr(par)                       # orthonormal parallel basis
    # Orthogonal complement via SVD of the projector onto par.
    resid = np.eye(n) - par @ par.T
    u, sv, _ = np.linalg.svd(resid)
    perp = u[:, sv > 1e-9]
    assert perp.shape[1] == n - 2, (n, perp.shape)
    return par, perp


def window_facets(perp_mat):
    """Facet inequalities A x <= b for the projected unit cube (a zonotope)."""
    n, d = perp_mat.shape
    signs = np.array(list(itertools.product([-0.5, 0.5], repeat=n)))
    verts = signs @ perp_mat
    hull = ConvexHull(verts)
    return hull.equations[:, :d], -hull.equations[:, d]


def generate(n, extent, offset=None, disorder=0.0, seed=0, window_scale=1.0,
             fragments=0, duty=1.0):
    """Cut-and-project patch. `window_scale` inflates or shrinks the acceptance
    window, which varies partition granularity while holding lattice, dimension
    and window connectivity fixed."""
    par_mat, perp_mat = projections(n)
    d = perp_mat.shape[1]
    offset = np.full(d, 0.1123) if offset is None else np.asarray(offset)
    A, b = window_facets(perp_mat)
    b = b * window_scale
    rng = np.random.default_rng(seed)
    frag_dir = perp_mat[0] / np.linalg.norm(perp_mat[0]) if d else None
    # Slab period must come from the WINDOW's extent, fixed once, not from each
    # chunk's coordinate range.
    _sg = np.array(list(itertools.product([-0.5, 0.5], repeat=n))) @ perp_mat
    win_span = float(2.0 * np.abs(_sg @ frag_dir).max()) * window_scale
    period = win_span / max(fragments, 1)

    axis = np.arange(-extent, extent + 1, dtype=np.int32)
    tail = np.array(list(itertools.product(axis, repeat=n - 1)), dtype=np.int32)

    # The acceptance test allocates a (rows x facets) array, which for larger n
    # exceeds memory if the whole slice is tested at once. Test in chunks.
    CHUNK = 400_000
    kept = []
    for first in axis:
        for lo in range(0, len(tail), CHUNK):
            sub = tail[lo:lo + CHUNK]
            blk = np.empty((len(sub), n), dtype=np.int32)
            blk[:, 0] = first
            blk[:, 1:] = sub
            pp = blk @ perp_mat + offset
            if disorder > 0:
                pp = pp + rng.normal(0.0, disorder, pp.shape)
            keep = np.ones(len(blk), dtype=bool)
            for j in range(A.shape[0]):          # facet at a time, no big matrix
                keep &= pp @ A[j] <= b[j] + 1e-9
                if not keep.any():
                    break
            if fragments > 0 and keep.any():
                phase = np.mod(pp @ frag_dir + 10.0 * win_span, period) / period
                keep &= phase < duty
            if keep.any():
                kept.append(blk[keep])

    lifts = np.concatenate(kept) if kept else np.zeros((0, n), dtype=np.int32)
    return lifts, lifts @ par_mat, lifts @ perp_mat + offset


def build_edges(lifts):
    index = {tuple(r): i for i, r in enumerate(lifts)}
    edges = set()
    for i, row in enumerate(lifts):
        for ax in range(lifts.shape[1]):
            nbr = list(row)
            nbr[ax] += 1
            j = index.get(tuple(nbr))
            if j is not None:
                edges.add((min(i, j), max(i, j)))
    return sorted(edges)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--extent", type=int, default=8)
    ap.add_argument("--disorder", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--prefix", default=None)
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    lifts, par, perp = generate(args.n, args.extent, disorder=args.disorder, seed=args.seed)
    edges = build_edges(lifts)
    deg = np.zeros(len(par), dtype=int)
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1

    L = (np.linalg.norm(par[[u for u, _ in edges]] - par[[v for _, v in edges]], axis=1)
         if edges else np.array([0.0]))
    print(f"n = {args.n}   {2*args.n}-fold   perp dim {perp.shape[1]}")
    print(f"vertices         : {len(par)}")
    print(f"edges            : {len(edges)}")
    print(f"mean degree      : {deg.mean():.4f}   range {deg.min()}..{deg.max()}")
    print(f"edge lengths     : {len(set(np.round(L,6)))} distinct, median {np.median(L):.6f}")

    if args.write:
        prefix = args.prefix or f"nfold{args.n}"
        lp = os.path.join(args.out, f"{prefix}_lift.csv")
        with open(lp, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            pcols = [f"perp_{i}" for i in range(perp.shape[1])]
            w.writerow(["index"] + [f"K{i}" for i in range(args.n)] + ["x", "y"]
                       + pcols + ["perp_r", "k_sum"])
            for i in range(len(par)):
                w.writerow([i, *lifts[i].tolist(), f"{par[i,0]:.10f}", f"{par[i,1]:.10f}",
                            *[f"{v:.10f}" for v in perp[i]],
                            f"{np.linalg.norm(perp[i]):.10f}", int(lifts[i].sum())])
        ep = os.path.join(args.out, f"{prefix}_edges.csv")
        with open(ep, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["source_index", "target_index"])
            w.writerows(edges)
        print(f"wrote {lp}\nwrote {ep}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Penrose P3 substrate generator (Z^5 cut-and-project), matching generate_ab.py.

Parallel space:      e_k      = (cos(2*pi*k/5), sin(2*pi*k/5))   k = 0..4
Perpendicular space: e_k_perp = (cos(4*pi*k/5), sin(4*pi*k/5))   k = 0..4

A Z^5 lattice point n is accepted when its index sum j = sum(n_k) lies in
{1,2,3,4} and its perpendicular projection falls inside window_j, the convex
hull of every sum of j distinct perpendicular basis vectors. Those four windows
are the pentagons that section the projected unit 5-cube at integer height.

Edges follow the same rule as the AB generator: lifts differing by exactly one
unit along a single lattice axis.

Phason disorder is applied as an independent perturbation of each candidate's
perpendicular coordinate before the acceptance test, which scatters flips
through the patch instead of translating the whole window.
"""

import argparse
import csv
import itertools
import math
import os

import numpy as np
from scipy.spatial import ConvexHull

PAR = np.array([[math.cos(2 * math.pi * k / 5), math.sin(2 * math.pi * k / 5)] for k in range(5)])
PERP = np.array([[math.cos(4 * math.pi * k / 5), math.sin(4 * math.pi * k / 5)] for k in range(5)])


def windows():
    """Acceptance pentagon for each index sum j = 1..4."""
    out = {}
    for j in range(1, 5):
        pts = np.array([PERP[list(S)].sum(0) for S in itertools.combinations(range(5), j)])
        hull = pts[ConvexHull(pts).vertices]
        a, b, c = hull[0], hull[1], hull[2]
        if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) < 0:
            hull = hull[::-1]
        out[j] = hull
    return out


def inside(poly, pts, tol=1e-9):
    ok = np.ones(len(pts), dtype=bool)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        e, r = b - a, pts - a
        ok &= (e[0] * r[:, 1] - e[1] * r[:, 0]) >= -tol
    return ok


def generate(extent, offset, disorder=0.0, seed=0):
    win = windows()
    rng = np.random.default_rng(seed)
    axis = np.arange(-extent, extent + 1, dtype=np.int32)
    tail = np.array(list(itertools.product(axis, axis, axis, axis)), dtype=np.int32)
    tail_sum = tail.sum(1)

    kept = []
    for n0 in axis:
        j = tail_sum + n0
        sel = (j >= 1) & (j <= 4)
        if not sel.any():
            continue
        blk = np.empty((sel.sum(), 5), dtype=np.int32)
        blk[:, 0] = n0
        blk[:, 1:] = tail[sel]
        pp = blk @ PERP + offset
        if disorder > 0:
            pp = pp + rng.normal(0.0, disorder, pp.shape)
        js = blk.sum(1)
        keep = np.zeros(len(blk), dtype=bool)
        for jj in range(1, 5):
            m = js == jj
            if m.any():
                keep[m] = inside(win[jj], pp[m])
        if keep.any():
            kept.append(blk[keep])

    lifts = np.concatenate(kept) if kept else np.zeros((0, 5), dtype=np.int32)
    return lifts, lifts @ PAR, lifts @ PERP + offset


def build_edges(lifts):
    index = {tuple(r): i for i, r in enumerate(lifts)}
    edges = set()
    for i, row in enumerate(lifts):
        for axis in range(5):
            nbr = list(row)
            nbr[axis] += 1
            j = index.get(tuple(nbr))
            if j is not None:
                edges.add((min(i, j), max(i, j)))
    return sorted(edges)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=12)
    ap.add_argument("--disorder", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--prefix", default="penrose")
    args = ap.parse_args()

    offset = np.array([0.1237, 0.0891])
    lifts, par, perp = generate(args.extent, offset, args.disorder, args.seed)
    edges = build_edges(lifts)

    deg = np.zeros(len(par), dtype=int)
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1

    lift_path = os.path.join(args.out, f"{args.prefix}_lift.csv")
    edge_path = os.path.join(args.out, f"{args.prefix}_edges.csv")
    with open(lift_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["index", "K0", "K1", "K2", "K3", "K4", "x", "y",
                    "perp_x", "perp_y", "perp_r", "k_sum_mod5"])
        for i in range(len(par)):
            w.writerow([i, *lifts[i].tolist(),
                        f"{par[i,0]:.10f}", f"{par[i,1]:.10f}",
                        f"{perp[i,0]:.10f}", f"{perp[i,1]:.10f}",
                        f"{math.hypot(*perp[i]):.10f}", int(lifts[i].sum()) % 5])
    with open(edge_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source_index", "target_index"])
        w.writerows(edges)

    L = np.linalg.norm(par[[u for u, _ in edges]] - par[[v for _, v in edges]], axis=1)
    print(f"vertices         : {len(par)}")
    print(f"edges            : {len(edges)}")
    print(f"mean degree      : {deg.mean():.4f}   range {deg.min()}..{deg.max()}")
    print(f"degree histogram : " + ", ".join(f"{d}:{c}" for d, c in enumerate(np.bincount(deg)) if c))
    print(f"edge lengths     : {len(set(np.round(L,6)))} distinct, median {np.median(L):.6f}")
    print(f"index sums       : {sorted(set(lifts.sum(1).tolist()))}")
    print(f"wrote {lift_path}\nwrote {edge_path}")


if __name__ == "__main__":
    main()

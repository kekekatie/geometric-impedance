#!/usr/bin/env python3
"""
Ammann-Beenker substrate generator (Z^4 cut-and-project).

Produces the two inputs the audit pipeline expects, with full perpendicular-space
coordinates for every vertex, so the audit can be reproduced without external files.

Parallel space:      e_k      = (cos(k*pi/4),   sin(k*pi/4))     k = 0..3
Perpendicular space: e_k_perp = (cos(3k*pi/4), sin(3k*pi/4))     k = 0..3

Acceptance window: the projection of the Z^4 unit cell into perpendicular space,
which is the regular octagon (a zonogon over the four perp generators).

Edges follow the audit's convention: vertices whose integer lifts differ by
exactly one unit along a single lattice axis.
"""

import argparse
import csv
import itertools
import math
import os

import numpy as np

PAR = np.array([[math.cos(k * math.pi / 4), math.sin(k * math.pi / 4)] for k in range(4)])
PERP = np.array([[math.cos(3 * k * math.pi / 4), math.sin(3 * k * math.pi / 4)] for k in range(4)])


def octagon_window():
    """Vertices of the acceptance window: zonogon over the perp generators."""
    gens = [PERP[k] for k in range(4)]
    gens += [-g for g in gens]
    gens.sort(key=lambda g: math.atan2(g[1], g[0]))
    start = -0.5 * sum(PERP[k] for k in range(4))
    pts, cur = [], start.copy()
    for g in gens:
        pts.append(cur.copy())
        cur = cur + g
    return np.array(pts)


def inside(poly, pts, tol=1e-9):
    """Point-in-convex-polygon, vectorised. Polygon must be CCW."""
    ok = np.ones(len(pts), dtype=bool)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        edge = b - a
        rel = pts - a
        cross = edge[0] * rel[:, 1] - edge[1] * rel[:, 0]
        ok &= cross >= -tol
    return ok


def _ccw(poly):
    a, b, c = poly[0], poly[1], poly[2]
    if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) < 0:
        return poly[::-1]
    return poly


def generate(rng_extent, offset):
    """Return (lifts, par, perp) for all accepted lattice points.

    The Z^4 search box grows as extent^4, so candidates are filtered in slices
    along the first axis rather than materialised all at once.
    """
    window = _ccw(octagon_window())
    axis = np.arange(-rng_extent, rng_extent + 1, dtype=np.int32)
    tail = np.array(list(itertools.product(axis, axis, axis)), dtype=np.int32)

    kept_lifts = []
    for n0 in axis:
        block = np.empty((len(tail), 4), dtype=np.int32)
        block[:, 0] = n0
        block[:, 1:] = tail
        perp = block @ PERP + offset
        keep = inside(window, perp)
        if keep.any():
            kept_lifts.append(block[keep])

    lifts = np.concatenate(kept_lifts) if kept_lifts else np.zeros((0, 4), dtype=np.int32)
    perp = lifts @ PERP + offset
    par = lifts @ PAR
    return lifts, par, perp


def build_edges(lifts):
    """Vertices whose lifts differ by exactly one unit along a single axis."""
    index = {tuple(row): i for i, row in enumerate(lifts)}
    edges = set()
    for i, row in enumerate(lifts):
        for axis in range(4):
            nbr = list(row)
            nbr[axis] += 1
            j = index.get(tuple(nbr))
            if j is not None:
                edges.add((min(i, j), max(i, j)))
    return sorted(edges)


def trim_to_disc(lifts, par, perp, edges, keep_fraction):
    """Keep the innermost fraction by radius, reindexing edges."""
    if keep_fraction >= 1.0:
        return lifts, par, perp, edges
    r = np.linalg.norm(par - par.mean(axis=0), axis=1)
    order = np.argsort(r)[: int(round(keep_fraction * len(par)))]
    keep = np.sort(order)
    remap = {old: new for new, old in enumerate(keep)}
    edges = [(remap[u], remap[v]) for u, v in edges if u in remap and v in remap]
    return lifts[keep], par[keep], perp[keep], sorted(edges)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=9, help="Z^4 search half-width")
    ap.add_argument("--keep", type=float, default=1.0, help="central fraction to retain")
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--prefix", default="ab")
    args = ap.parse_args()

    # Generic offset: keeps the window boundary off any lattice point.
    offset = np.array([0.1381, 0.0927])

    lifts, par, perp = generate(args.extent, offset)
    edges = build_edges(lifts)
    lifts, par, perp, edges = trim_to_disc(lifts, par, perp, edges, args.keep)

    deg = np.zeros(len(par), dtype=int)
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1

    lift_path = os.path.join(args.out, f"{args.prefix}_lift.csv")
    edge_path = os.path.join(args.out, f"{args.prefix}_edges.csv")

    with open(lift_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["index", "n0", "n1", "n2", "n3", "x", "y",
                    "perp_x", "perp_y", "perp_r", "k_sum_mod5"])
        for i in range(len(par)):
            w.writerow([i, *lifts[i].tolist(),
                        f"{par[i,0]:.10f}", f"{par[i,1]:.10f}",
                        f"{perp[i,0]:.10f}", f"{perp[i,1]:.10f}",
                        f"{math.hypot(*perp[i]):.10f}",
                        int(lifts[i].sum()) % 5])

    with open(edge_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source_index", "target_index"])
        w.writerows(edges)

    print(f"vertices           : {len(par)}")
    print(f"edges              : {len(edges)}")
    print(f"mean degree        : {deg.mean():.4f}")
    print(f"degree range       : {deg.min()}..{deg.max()}")
    counts = np.bincount(deg)
    print("degree histogram   : " + ", ".join(
        f"{d}:{c}" for d, c in enumerate(counts) if c))
    print(f"edge length spread : {len(set(np.round(np.linalg.norm(par[[u for u,_ in edges]] - par[[v for _,v in edges]], axis=1), 6)))} distinct")
    print(f"wrote {lift_path}")
    print(f"wrote {edge_path}")


if __name__ == "__main__":
    main()

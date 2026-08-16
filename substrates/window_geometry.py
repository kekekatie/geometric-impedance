#!/usr/bin/env python3
"""
Exact acceptance-window geometry for the rank-4 family.

The number of window pieces, and the boundary they carry per unit area, is the
covariate that separates the two live hypotheses in
`PREDICTION_rank4_headline.md`. It therefore has to be measured properly rather
than estimated from sampled points: a convex hull of accepted perpendicular
coordinates underestimates both area and perimeter, and does so unevenly, since
the single 8-fold window is sampled thousands of times while each of the nine
12-fold pieces gets a few hundred. That bias inflates perimeter-to-area for the
more fragmented members - exactly the direction that would fake the result.

So the pieces are computed exactly. The projected m-cube is a zonotope in the
(2 + rank K)-dimensional perpendicular space with known halfspace description.
Each window piece is its slice at one admissible value of the extra coordinate,
which is a 2-dimensional polygon obtained by substituting that value and
intersecting the resulting halfplanes.
"""

import argparse
import itertools
import sys

import numpy as np
from scipy.optimize import linprog
from scipy.spatial import ConvexHull, HalfspaceIntersection

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import EXTRA_OFFSET, structure


def polygon(A2, b2):
    """Vertices of {x in R^2 : A2 x <= b2}, or None if empty or unbounded."""
    norm = np.linalg.norm(A2, axis=1, keepdims=True)
    res = linprog(c=[0, 0, -1],
                  A_ub=np.hstack([A2, norm]), b_ub=b2,
                  bounds=[(None, None), (None, None), (None, 1.0)],
                  method="highs")
    if not res.success or res.x[2] <= 1e-9:
        return None
    hs = HalfspaceIntersection(np.hstack([A2, -b2[:, None]]), res.x[:2])
    p = hs.intersections
    return p[ConvexHull(p).vertices]


def pieces(N, extra_offset=None):
    """Every nonempty window piece, as (extra integer label, polygon)."""
    st = structure(N)
    K, G, Kb, mod = st["K"], st["G"], st["Kb"], st["mod"]
    r = K.shape[0]
    A, b = st["A"], st["b"]
    if r == 0:
        return [((), polygon(A, b))]
    ex_off = np.array((EXTRA_OFFSET if extra_offset is None else extra_offset)[:r])
    Gi = np.linalg.inv(G)
    out = []
    # Admissible extra labels are bounded by the zonotope's own extent.
    span = [range(-int(m) * 2, int(m) * 2 + 1) for m in mod]
    for u in itertools.product(*span):
        ex = (np.array(u, float) @ Gi @ K.astype(float)) @ Kb + ex_off
        poly = polygon(A[:, :2], b - A[:, 2:] @ ex)
        if poly is not None:
            out.append((u, poly))
    return out


def measure(poly):
    e = np.roll(poly, -1, axis=0) - poly
    per = float(np.linalg.norm(e, axis=1).sum())
    area = float(abs(np.cross(poly, np.roll(poly, -1, axis=0)).sum()) / 2)
    return area, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    print(f"{'N':>3} {'pieces':>7} {'classes':>8} {'area':>10} {'perimeter':>10} "
          f"{'perim/area':>11} {'sides':>7}")
    for N, nm in ((8, "silver"), (10, "golden"), (12, "platinum")):
        P = pieces(N)
        st = structure(N)
        A = sum(measure(p)[0] for _, p in P)
        Q = sum(measure(p)[1] for _, p in P)
        sides = sorted({len(p) for _, p in P})
        print(f"{N:>3} {len(P):>7} {st['classes']:>8} {A:>10.4f} {Q:>10.4f} "
              f"{Q/A:>11.4f} {str(sides):>7}   {nm}")
        if args.verbose:
            for u, p in P:
                a, q = measure(p)
                print(f"        label {u}  {len(p)} sides  area {a:.4f}  perim {q:.4f}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simpleton flips: the elementary phason move on a rhombus tiling.

Every damage model used in this project so far has been synthetic jitter on
perpendicular coordinates, with an amplitude that is generator-specific and
uncalibrated - the single criticism the experimental literature survey levelled
at the computational result, and a fair one.

A phason flip is the physical alternative. In a rhombus tiling, three rhombi
meeting at a degree-three vertex fill a hexagon, and that hexagon admits exactly
two tilings; exchanging them moves the interior vertex to the opposite corner
and leaves the tiling valid. This is *the* elementary phason rearrangement, it
is local, it is reversible, and damage is counted in flips rather than measured
in arbitrary units - which makes it directly comparable to experimental defect
densities such as the ~5% tiling-error figure for octagonal Mn80Si15Al5.

In lift coordinates the move is exact. A degree-three vertex v has neighbours
v + s_a e_a, v + s_b e_b, v + s_c e_c for three distinct star directions; the
flip sends v to v + s_a e_a + s_b e_b + s_c e_c. The six hexagon corners are
unchanged, so the operation is purely local.

Requires a genuine rhombus tiling. The Z^4 cyclotomic substrates do not qualify
at 10-fold (see TILING_CONFOUND.md); the Z^n family does at all three folds.
"""

import argparse
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_nfold import build_edges, generate
from tile_audit import faces, shape_key


def neighbours_by_axis(lifts):
    """For each vertex, the list of (axis, sign) steps leading to another vertex."""
    idx = {tuple(r): i for i, r in enumerate(lifts)}
    n = lifts.shape[1]
    out = [[] for _ in range(len(lifts))]
    for i, row in enumerate(lifts):
        for ax in range(n):
            for s in (1, -1):
                nb = list(row)
                nb[ax] += s
                if tuple(nb) in idx:
                    out[i].append((ax, s))
    return idx, out


def flippable(lifts):
    """All simpleton-flip sites.

    Returns a list of (vertex_index, target_lift_tuple). A site qualifies when
    the vertex has exactly three neighbours, on three distinct axes, and all six
    corners of the hexagon they span are present while the opposite interior
    vertex is absent.
    """
    idx, nbr = neighbours_by_axis(lifts)
    sites = []
    for i, steps in enumerate(nbr):
        if len(steps) != 3:
            continue
        axes = {a for a, _ in steps}
        if len(axes) != 3:
            continue
        v = lifts[i]
        d = np.zeros((3, lifts.shape[1]), dtype=lifts.dtype)
        for k, (a, s) in enumerate(steps):
            d[k, a] = s
        tgt = tuple(v + d.sum(0))
        if tgt in idx:
            continue
        corners = [tuple(v + d[k]) for k in range(3)] + \
                  [tuple(v + d[k] + d[(k + 1) % 3]) for k in range(3)]
        if all(c in idx for c in corners):
            sites.append((i, tgt))
    return sites


def apply_flips(lifts, k, rng):
    """Apply k simpleton flips, re-finding sites each time so moves stay legal.

    Returns the new lift set and the number of flips actually performed, which
    can fall short of k only if the tiling runs out of flippable sites.
    """
    L = lifts.copy()
    done = 0
    for _ in range(k):
        sites = flippable(L)
        if not sites:
            break
        i, tgt = sites[rng.integers(len(sites))]
        L[i] = np.array(tgt, dtype=L.dtype)
        done += 1
    return L, done


def tiling_report(lifts, n):
    """Crossing-free, all-quadrilateral, Euler-2 check plus rhombus vocabulary."""
    from scipy.spatial import KDTree
    par, _ = __import__("generate_nfold").projections(n)
    P = lifts @ par
    E = build_edges(lifts)
    A = np.array([P[u] for u, _ in E])
    B = np.array([P[v] for _, v in E])
    pr = KDTree((A + B) / 2).query_pairs(r=1.05, output_type="ndarray")
    Ei = np.array(E)
    i, j = pr[:, 0], pr[:, 1]
    m = ~(Ei[i][:, None, :] == Ei[j][:, :, None]).any(axis=(1, 2))
    p, q, r, s = A[i[m]], B[i[m]], A[j[m]], B[j[m]]
    d1, d2 = q - p, s - r
    den = d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]
    ok = np.abs(den) > 1e-12
    dp = r - p
    t = np.full(len(p), np.nan)
    u = np.full(len(p), np.nan)
    t[ok] = (dp[ok, 0] * d2[ok, 1] - dp[ok, 1] * d2[ok, 0]) / den[ok]
    u[ok] = (dp[ok, 0] * d1[ok, 1] - dp[ok, 1] * d1[ok, 0]) / den[ok]
    e = 1e-9
    cross = int((ok & (t > e) & (t < 1 - e) & (u > e) & (u < 1 - e)).sum())

    F = faces(len(P), E, P)
    sz = Counter(len(c) for c in F)
    outer = max(sz)
    bd = [c for c in F if len(c) != outer]
    quad = sum(1 for c in bd if len(c) == 4) / max(len(bd), 1)
    shapes = len(Counter(shape_key(c, P) for c in bd if len(c) == 4))
    return dict(verts=len(P), edges=len(E), cross=cross, quad=quad,
                euler=len(P) - len(E) + len(F), rhombi=shapes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--extent", type=int, default=9)
    ap.add_argument("--flips", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    lifts, par, _ = generate(args.n, args.extent)
    sites = flippable(lifts)
    print(f"Z^{args.n} ({2*args.n}-fold), {len(lifts)} vertices")
    print(f"flippable sites  : {len(sites)}  "
          f"({len(sites)/len(lifts):.2%} of vertices)")

    r0 = tiling_report(lifts, args.n)
    print(f"\nbefore : {r0}")

    rng = np.random.default_rng(args.seed)
    L, done = apply_flips(lifts, args.flips, rng)
    moved = int((L != lifts).any(axis=1).sum())
    r1 = tiling_report(L, args.n)
    print(f"after  : {r1}")
    print(f"\nflips requested {args.flips}, performed {done}, "
          f"vertices displaced {moved}")

    ok = (r1["cross"] == 0 and r1["quad"] == 1.0 and r1["euler"] == 2
          and r1["verts"] == r0["verts"] and r1["rhombi"] == r0["rhombi"])
    print("TILING PRESERVED" if ok else "*** TILING BROKEN ***")


if __name__ == "__main__":
    main()

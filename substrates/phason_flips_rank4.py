#!/usr/bin/env python3
"""
Simpleton phason flips on the rank-4 congruence family (8-, 10-, 12-fold).

The Z^n version in `phason_flips.py` steps along the integer axes, which works
only because that family's edges are axis vectors. The rank-4 substrates have
edges along the complete N-fold star (`structure(N)["star"]`, m = N/2 integer
steps in Z^4), so the flip has to step along star directions instead. Otherwise
this is the same elementary move: three rhombi meeting at a degree-3 vertex fill
a hexagon that admits two tilings, and exchanging them sends the interior vertex
to the opposite corner, v -> v + s_a + s_b + s_c.

The flip takes the tiling out of the exact cut-and-project family (a flipped
vertex is the window-boundary partner that the ideal window rejects), so the
generation-time kernel/ustar edge rule no longer applies. Post-flip the tiling is
a valid *random-tiling* member of the same rhombus vocabulary, and its edges are
read geometrically: two vertices are joined iff their lift difference is a single
star vector. Validity is asserted the hard way every step - zero crossings, 100%
quadrilateral faces, Euler 2 - so a move that silently breaks the tiling aborts
rather than contaminating a measurement.
"""

import argparse
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import build_edges, generate, structure
from tile_audit import faces, shape_key


def neighbours_by_star(lifts, ustar, star, K):
    """For each vertex, the (star-line, sign) steps to a genuine tiling neighbour.

    Kernel-aware: a lift step by s*star[k] is only an edge when the congruence
    label also advances by s*K[:, k]. Without that check the 12-fold graph picks
    up spurious edges (see generate_rank4.build_edges).
    """
    idx = {tuple(r): i for i, r in enumerate(lifts)}
    m = len(star)
    r = len(K)
    out = [[] for _ in range(len(lifts))]
    for i, row in enumerate(lifts):
        for k in range(m):
            for s in (1, -1):
                j = idx.get(tuple(row + s * star[k]))
                if j is None:
                    continue
                if r and not np.array_equal(ustar[j] - ustar[i], s * K[:, k]):
                    continue
                out[i].append((k, s))
    return idx, out


def flippable(lifts, ustar, star, K):
    """All simpleton-flip sites as (vertex_index, target_lift, target_ustar).

    A site qualifies when the vertex has exactly three neighbours on three
    distinct star lines, all six corners of the hexagon they span are present,
    and the opposite interior vertex is absent. The move is a step in the full
    lattice, so the congruence label advances by the matching sum of K columns.
    """
    idx, nbr = neighbours_by_star(lifts, ustar, star, K)
    r = len(K)
    sites = []
    for i, steps in enumerate(nbr):
        if len(steps) != 3:
            continue
        if len({k for k, _ in steps}) != 3:
            continue
        v = lifts[i]
        d = np.array([s * star[k] for k, s in steps])          # 3 x 4
        du = (np.array([s * K[:, k] for k, s in steps]).sum(0)
              if r else np.zeros(0, dtype=np.int64))
        tgt = tuple(v + d.sum(0))
        if tgt in idx:
            continue
        corners = [tuple(v + d[j]) for j in range(3)] + \
                  [tuple(v + d[j] + d[(j + 1) % 3]) for j in range(3)]
        if all(c in idx for c in corners):
            sites.append((i, tgt, ustar[i] + du))
    return sites


def apply_flips(lifts, ustar, star, K, k, rng):
    """Apply up to k random simpleton flips, re-finding sites each move."""
    L = lifts.copy()
    U = ustar.copy()
    done = 0
    for _ in range(k):
        sites = flippable(L, U, star, K)
        if not sites:
            break
        i, tgt, utgt = sites[rng.integers(len(sites))]
        L[i] = np.array(tgt, dtype=L.dtype)
        U[i] = utgt
        done += 1
    return L, U, done


def tiling_report(lifts, ustar, N, par4):
    """Crossing-free / all-quadrilateral / Euler-2 check plus rhombus vocabulary."""
    from scipy.spatial import KDTree
    P = lifts @ par4
    E = build_edges(lifts, N, ustar)
    if not E:
        return dict(verts=len(P), edges=0, cross=-1, quad=0.0, euler=-1, rhombi=0)
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
    ap.add_argument("--extent", type=int, default=10)
    ap.add_argument("--flips", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    for N, nm in ((8, "silver"), (10, "golden"), (12, "platinum")):
        st = structure(N)
        star, par4, K = st["star"], st["par4"], st["K"]
        lifts, _, _, ustar = generate(N, args.extent)
        sites = flippable(lifts, ustar, star, K)
        r0 = tiling_report(lifts, ustar, N, par4)
        print(f"\n{N:>3}-fold ({nm})  {len(lifts)} vertices")
        print(f"    flippable sites : {len(sites)}  ({len(sites)/len(lifts):.2%} of vertices)")
        print(f"    before : {r0}")

        rng = np.random.default_rng(args.seed)
        L, U, done = apply_flips(lifts, ustar, star, K, args.flips, rng)
        moved = int((L != lifts).any(axis=1).sum())
        r1 = tiling_report(L, U, N, par4)
        print(f"    after  : {r1}")
        print(f"    flips requested {args.flips}, performed {done}, vertices displaced {moved}")
        good = (r1["cross"] == 0 and r1["quad"] == 1.0 and r1["euler"] == 2
                and r1["verts"] == r0["verts"] and r1["rhombi"] == r0["rhombi"])
        print("    " + ("TILING PRESERVED" if good else "*** TILING BROKEN ***"))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
De Bruijn multigrid constructor for the rank-4 families (8-, 10-, 12-fold).

This is the combinatorial route to the lifted-defect audit's Gate 0. The
cut-and-project generator (`generate_rank4.py`) makes the perfect tiling by an
acceptance test; a defect then needs an elastic relaxation we did not solve
(see RESULTS_GATE0_DEFECT.md). The multigrid builds the *same* tilings as the
dual of m = N/2 line grids, where every face is a rhombus BY CONSTRUCTION -- so a
terminating grid line yields an all-rhombus tiling with an isolated core and no
elasticity to solve.

STEP 1 (this file, for now): build the *perfect* dual and prove the bridge --
that a multigrid vertex lives in our existing lift world. A dual vertex is labelled
by its integer grid-index vector K in Z^m; its rank-4 lift is a = K @ S (S =
reduce_powers), its position is K @ par_m, and an edge steps K by a single unit
e_j = one star direction. So the Part-1 closure instrument (`lifted_defect.closure`,
which reads star steps off the Z^4 lift) applies unchanged. The gate for step 1:
the dual is 100% rhombi, and every face closes to zero under the existing
instrument. Only once that holds do we add the terminating-line defect (step 2).
"""

import argparse
import itertools
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import frame, reduce_powers, structure
from tile_audit import faces, shape_key
from lifted_defect import closure

NAME = {8: "silver", 10: "golden", 12: "platinum"}


def default_gamma(m, seed=0):
    """Generic grid intercepts summing to 0 (singularity-free, no triple lines)."""
    rng = np.random.default_rng(seed)
    g = rng.uniform(0.1, 0.4, m)
    return g - g.mean()


def dual(N, L=8, R=None, gamma=None, seed=0):
    """Perfect de Bruijn dual tiling.

    Returns lifts (Z^4), positions, index-vectors K (Z^m), edges, and rhombi
    (4-cycles of vertex indices). Grid family j has lines r . n_j + gamma_j in Z,
    with n_j the j-th star direction; each pairwise line intersection contributes
    one rhombus with corners K + {0,1} e_p + {0,1} e_q.
    """
    m, par_m, perp_m = frame(N)
    S = reduce_powers(N)                      # m x 4  (Z^m -> Z^4 ring reduction)
    n = par_m                                 # m grid normals (unit star dirs)
    if gamma is None:
        gamma = default_gamma(m, seed)
    if R is None:
        R = L * 0.9

    vidx = {}                                 # index-vector tuple -> vertex id
    Ks = []

    def vid(K):
        t = tuple(int(x) for x in K)
        if t not in vidx:
            vidx[t] = len(Ks)
            Ks.append(np.array(t, dtype=np.int64))
        return vidx[t]

    rhombi = []
    for p in range(m):
        for q in range(p + 1, m):
            M = np.array([n[p], n[q]])
            det = M[0, 0] * M[1, 1] - M[0, 1] * M[1, 0]
            if abs(det) < 1e-9:
                continue
            Minv = np.linalg.inv(M)
            for Kp in range(-L, L + 1):
                for Kq in range(-L, L + 1):
                    r = Minv @ np.array([Kp - gamma[p], Kq - gamma[q]])
                    if np.hypot(*r) > R:
                        continue
                    K = np.ceil(r @ n.T + gamma - 1e-9).astype(np.int64)
                    K[p], K[q] = Kp, Kq
                    ep = np.zeros(m, np.int64); ep[p] = 1
                    eq = np.zeros(m, np.int64); eq[q] = 1
                    corners = [vid(K), vid(K + ep), vid(K + ep + eq), vid(K + eq)]
                    rhombi.append(corners)

    K = np.array(Ks)
    lifts = K @ S
    pos = K @ par_m
    E = set()
    for c in rhombi:
        for t in range(4):
            i, j = c[t], c[(t + 1) % 4]
            E.add((min(i, j), max(i, j)))
    return dict(lifts=lifts, pos=pos, K=K, edges=sorted(E), rhombi=rhombi,
                S=S, m=m, par_m=par_m, perp_m=perp_m)


def validate(N, L=8):
    st = structure(N)
    d = dual(N, L=L)
    lifts, pos, S, m = d["lifts"], d["pos"], d["S"], d["m"]
    star = st["star"]

    # (1) every generated rhombus must close to zero under the Part-1 instrument
    worst = 0
    nonstar = 0
    for c in d["rhombi"]:
        B, ok = closure(c, lifts, star, m)
        if not ok:
            nonstar += 1
        worst = max(worst, int(np.abs(B).max()))

    # (2) all faces of the interior embedding are rhombi (drop the outer boundary)
    F = faces(len(pos), d["edges"], pos)
    sz = Counter(len(c) for c in F)
    outer = max(sz)
    bd = [c for c in F if len(c) != outer]
    quad = sum(1 for c in bd if len(c) == 4) / max(len(bd), 1)
    shapes = len(Counter(shape_key(c, pos) for c in bd if len(c) == 4))

    # (3) every face closes to zero too (independent of my rhombus bookkeeping)
    fworst = 0
    for c in bd:
        B, ok = closure(c, lifts, star, m)
        fworst = max(fworst, int(np.abs(B).max()))

    print(f"\n{NAME[N]:>9} (N={N}, m={m})  L={L}")
    print(f"   vertices {len(pos)}  edges {len(d['edges'])}  rhombi {len(d['rhombi'])}")
    print(f"   distinct rhombus shapes: {shapes}   bounded faces {len(bd)}  "
          f"quad {quad:.4%}")
    print(f"   max |closure| over generated rhombi: {worst}   non-star: {nonstar}")
    print(f"   max |closure| over traced faces    : {fworst}")
    ok = worst == 0 and fworst == 0 and nonstar == 0 and quad == 1.0
    print(f"   -> bridge holds (rhombi + zero closure): {'YES' if ok else 'NO'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=8)
    args = ap.parse_args()
    allok = True
    for N in (8, 10, 12):
        allok &= validate(N, L=args.L)
    print(f"\n{'ALL BRIDGES HOLD' if allok else 'BRIDGE FAILED'}")


if __name__ == "__main__":
    main()

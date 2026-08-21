#!/usr/bin/env python3
"""
Branch A of the recovery design (PREDICTION_recovery.md): unbiased phason-flip
dynamics, no energy, run first as the null against which any energetic recovery
must be judged.

This pilot measures the part that needs no classifier and therefore carries no
degree confound: how fast structure is lost per flip per vertex, and whether it
comes back on its own. A single unbiased trajectory is walked per seed; at each
checkpoint the current tiling is compared to the clean one by vertex and edge
Jaccard. Unbiased dynamics have no restoring force, so the prediction is a
monotone rise to a random-tiling plateau with no spontaneous return - the
structural form of "recovery needs energetics, not mobility". The plateau value
is itself the matched random-tiling scramble the full design will use as a
control.

Also reports the flippable-site fraction (mobility) per family, since unequal
admissible-move counts are the first confound to rule out (GPT's list): a family
that simply has more moves available will accrue change faster per attempted flip.
"""

import argparse
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import build_edges, generate, structure
from phason_flips_rank4 import apply_flips, flippable

NAME = {8: "silver", 10: "golden", 12: "platinum"}
CHECKS = [0.02, 0.05, 0.10, 0.15, 0.20, 0.35]


def edge_set(lifts, N, ustar):
    """Edges as a set of unordered lift-coordinate pairs, comparable across states."""
    E = build_edges(lifts, N, ustar)
    T = [tuple(r) for r in lifts]
    return {frozenset((T[u], T[v])) for u, v in E}


def jaccard(a, b):
    return len(a & b) / max(len(a | b), 1)


def trajectory(N, extent, seed):
    st = structure(N)
    star, K = st["star"], st["K"]
    lifts0, _, _, ustar0 = generate(N, extent)
    n = len(lifts0)
    V0 = {tuple(r) for r in lifts0}
    E0 = edge_set(lifts0, N, ustar0)
    mob = len(flippable(lifts0, ustar0, star, K)) / n

    rng = np.random.default_rng(seed)
    L, U = lifts0.copy(), ustar0.copy()
    prev = 0
    row = []
    for fpv in CHECKS:
        target = int(round(fpv * n))
        L, U, _ = apply_flips(L, U, star, K, target - prev, rng)
        prev = target
        V = {tuple(r) for r in L}
        vloss = 1.0 - jaccard(V0, V)
        eloss = 1.0 - jaccard(E0, edge_set(L, N, U))
        row.append((vloss, eloss))
    return n, mob, np.array(row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extent", type=int, default=10)
    ap.add_argument("--seeds", type=int, default=3)
    args = ap.parse_args()

    print(f"Branch A pilot - unbiased flips, extent {args.extent}, "
          f"{args.seeds} seeds\n")
    for N in (8, 10, 12):
        res = [trajectory(N, args.extent, s) for s in range(args.seeds)]
        n = res[0][0]
        mob = np.mean([r[1] for r in res])
        curves = np.stack([r[2] for r in res])          # seeds x checks x 2
        vm, vs = curves[:, :, 0].mean(0), curves[:, :, 0].std(0, ddof=1)
        em = curves[:, :, 1].mean(0)
        print(f"{NAME[N]:>9} ({N:>2}-fold)  {n} vertices   mobility {mob:.1%}")
        print(f"    {'flips/vtx':>10} " +
              " ".join(f"{c:>7.2f}" for c in CHECKS))
        print(f"    {'vertex loss':>10} " +
              " ".join(f"{v:>7.3f}" for v in vm))
        print(f"    {'  +- sd':>10} " +
              " ".join(f"{v:>7.3f}" for v in vs))
        print(f"    {'edge loss':>10} " +
              " ".join(f"{v:>7.3f}" for v in em))
        # loss per flip per vertex, from the first checkpoint (near-origin slope)
        slope = vm[0] / CHECKS[0]
        print(f"    loss per flip per vertex (near origin): {slope:.3f}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Continuation-volume engine for the sealed intrinsic-drift test
(PREREG_intrinsic_drift.md).

A state is a tiling; its configuration-space neighbours are the tilings one
simpleton flip away. Omega_r(x) is the number of DISTINCT states reachable within
r flips (excluding the start); S_r = log Omega_r. States are deduplicated by their
vertex set (frozenset of lift coordinates), which identifies the tiling; ustar is
carried for the kernel-aware flip rule but is not part of the identity key.

The branch quantities (the "tip") are computed over a state's immediate legal
moves A(x): the distribution {Omega_r(y) : y in A(x)}, its dispersion V_r and
contrast C_r, and the mean drift Delta S_r. Omega_1(y) = d(y) is the immediate
mobility of the neighbour and is cheap; Omega_{>=2} is a bounded BFS and blows up
fast, so it is horizon-local by necessity (see the prereg's caveat).
"""

import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import generate, structure
from phason_flips_rank4 import flippable


def state_key(lifts):
    return frozenset(map(tuple, lifts.tolist()))


def one_step(lifts, ustar, star, K):
    """All one-flip neighbour states as (lifts, ustar)."""
    out = []
    for i, tgt, utgt in flippable(lifts, ustar, star, K):
        L = lifts.copy()
        U = ustar.copy()
        L[i] = np.array(tgt, dtype=L.dtype)
        U[i] = utgt
        out.append((L, U))
    return out


def omega_r(lifts, ustar, star, K, r):
    """Number of distinct states reachable within r flips, excluding the start."""
    seen = {state_key(lifts)}
    frontier = [(lifts, ustar)]
    for _ in range(r):
        nxt = []
        for L, U in frontier:
            for L2, U2 in one_step(L, U, star, K):
                k = state_key(L2)
                if k not in seen:
                    seen.add(k)
                    nxt.append((L2, U2))
        frontier = nxt
        if not frontier:
            break
    return len(seen) - 1


def flippable_local(lifts, ustar, star, K, par4, center, radius):
    """Flip sites whose vertex lies within `radius` of `center` in parallel space."""
    P = lifts @ par4
    return [(i, t, u) for (i, t, u) in flippable(lifts, ustar, star, K)
            if np.linalg.norm(P[i] - center) <= radius]


def one_step_local(lifts, ustar, star, K, par4, center, radius):
    out = []
    for i, t, u in flippable_local(lifts, ustar, star, K, par4, center, radius):
        L = lifts.copy()
        U = ustar.copy()
        L[i] = np.array(t, dtype=L.dtype)
        U[i] = u
        out.append((L, U))
    return out


def omega_local(lifts, ustar, star, K, par4, center, radius, r):
    """Distinct configurations reachable within r flips restricted to a local disk.

    Only vertices inside the disk ever move, so this counts the local future
    volume accessible from the current tiling around `center` -- the physically
    local 'future behind the doors', and computationally bounded, so r can go
    deeper than the whole-patch BFS allows."""
    seen = {state_key(lifts)}
    frontier = [(lifts, ustar)]
    for _ in range(r):
        nxt = []
        for L, U in frontier:
            for L2, U2 in one_step_local(L, U, star, K, par4, center, radius):
                k = state_key(L2)
                if k not in seen:
                    seen.add(k)
                    nxt.append((L2, U2))
        frontier = nxt
        if not frontier:
            break
    return len(seen) - 1


def main():
    print("Engine test: Omega_1 should equal mobility d(x); Omega_2 sane.\n")
    print(f"{'':>9} {'verts':>6} {'d=Omega_1':>10} {'Omega_2':>9}")
    for N, nm in ((8, "silver"), (10, "golden"), (12, "platinum")):
        st = structure(N)
        star, K = st["star"], st["K"]
        lifts, _, _, ustar = generate(N, 3)
        d = len(flippable(lifts, ustar, star, K))
        o1 = omega_r(lifts, ustar, star, K, 1)
        o2 = omega_r(lifts, ustar, star, K, 2)
        flag = "OK" if o1 == d else "*** Omega_1 != d ***"
        print(f"{nm:>9} {len(lifts):>6} {d:>10} {o2:>9}   {flag}")


if __name__ == "__main__":
    main()

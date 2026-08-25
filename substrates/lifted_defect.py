#!/usr/bin/env python3
"""
Lifted-Burgers audit (sealed PREREG_lifted_defect.md) — Part 1: the closure
functional and its validation on the defect-free tilings.

Each tiling edge is a unit step e_k in the parent lattice Z^m (its physical form is
the star vector star[k]). The lifted Burgers charge of a closed loop is the signed
sum of those unit steps around it, an element of Z^m, split into b_par (its image in
the parallel plane) and b_perp (its perpendicular/phason image). For a defect-free
tiling every loop closes to zero; a dislocation makes a loop around its core close to
a nonzero B. This part builds the functional and confirms it reads exactly zero on the
perfect cut-and-project tilings (instrument calibration before Gate 0 construction).
"""

import sys
from collections import Counter

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import build_edges, frame, generate, structure
from tile_audit import faces

NAME = {8: "silver", 10: "golden", 12: "platinum"}


def edge_step(a_i, a_j, star):
    """(k, sign) such that a_j - a_i = sign * star[k], or None if not a star edge."""
    d = a_j - a_i
    for k, s in enumerate(star):
        if np.array_equal(d, s):
            return k, 1
        if np.array_equal(d, -s):
            return k, -1
    return None


def closure(cycle, lifts, star, m):
    """Lifted Burgers charge (in Z^m) summed around a cycle of vertex indices."""
    B = np.zeros(m, dtype=np.int64)
    ok = True
    for t in range(len(cycle)):
        i, j = cycle[t], cycle[(t + 1) % len(cycle)]
        step = edge_step(lifts[i], lifts[j], star)
        if step is None:
            ok = False
            continue
        k, s = step
        B[k] += s
    return B, ok


def split(B, N):
    """b_par (2-vec) and b_perp (2-vec) of a Z^m charge."""
    m, par_m, perp_m = frame(N)
    return B @ par_m, B @ perp_m


def main():
    for N in (8, 10, 12):
        st = structure(N)
        star = st["star"]
        m = st["m"]
        lifts, par, perp, ustar = generate(N, 8)
        E = build_edges(lifts, N, ustar)
        F = faces(len(par), E, par)
        outer = max(F, key=len)
        bounded = [c for c in F if c is not outer]

        # every bounded (rhombus) face must close to zero
        worst = 0
        nonstar = 0
        for c in bounded:
            B, ok = closure(c, lifts, star, m)
            if not ok:
                nonstar += 1
            worst = max(worst, int(np.abs(B).max()))
        # the outer boundary loop must also close to zero
        Bout, _ = closure(outer, lifts, star, m)
        bpar, bperp = split(Bout, N)

        print(f"{NAME[N]:>9} ({N}-fold): {len(bounded)} bounded faces, "
              f"outer loop {len(outer)} edges")
        print(f"   max |closure| over faces: {worst}   non-star-edge faces: {nonstar}")
        print(f"   outer-loop B = {Bout.tolist()}  "
              f"b_par={np.round(bpar,3).tolist()}  b_perp={np.round(bperp,3).tolist()}")
        print(f"   -> defect-free: {'YES' if worst == 0 and np.all(Bout == 0) else 'NO'}\n")


if __name__ == "__main__":
    main()

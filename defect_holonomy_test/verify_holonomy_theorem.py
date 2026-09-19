#!/usr/bin/env python3
"""
Verification of the rigid-edge holonomy theorem (regular-interface Claude's claim):

  On any structure whose vertices lie on the ideal projected lattice with exact
  star-vector edges, perp holonomy of every closed loop is identically zero,
  because the integer loop-sum m = sum(s*e_j) has pi_par(m) = 0, and
    - AB:      ker(pi_par) on Z^4 is {0}          -> m = 0        -> pi_perp(m)=0
    - Penrose: ker(pi_par) on Z^5 is Z*(1,1,1,1,1) -> pi_perp(that)=0 -> pi_perp(m)=0

Checks:
  (a) brute-force integer kernel of pi_par, |m_i| <= RANGE, both substrates
  (b) pi_perp((1,1,1,1,1)) ~ 0 for Penrose
  (c) corollary: v2 tight-loop integer sums m are exactly 0 (AB) / multiples of
      (1,1,1,1,1) (Penrose)
"""

import sys, itertools
sys.path.insert(0, "../reverse_loop_test")
import numpy as np
from geometry import Patch
from lift_metric import LiftMetric, positions_of_path
from defect import ring_loop
from defect_v2 import TerminatingLineDefect

RANGE = 20


def brute_kernel(par_star, rng=RANGE, chunk_axis0=True):
    """Integer vectors m with |m_i|<=rng and ||m @ par_star|| < 1e-9."""
    N = par_star.shape[0]
    axis = np.arange(-rng, rng + 1)
    kernel = []
    if N == 4:
        grids = np.stack(np.meshgrid(*([axis] * N), indexing="ij"), -1).reshape(-1, N)
        proj = grids @ par_star
        hit = np.linalg.norm(proj, axis=1) < 1e-9
        kernel = grids[hit]
    else:  # N == 5, chunk over the first coordinate to bound memory
        sub = np.stack(np.meshgrid(*([axis] * (N - 1)), indexing="ij"), -1).reshape(-1, N - 1)
        for m0 in axis:
            full = np.column_stack([np.full(len(sub), m0), sub])
            proj = full @ par_star
            hit = np.linalg.norm(proj, axis=1) < 1e-9
            if hit.any():
                kernel.append(full[hit])
        kernel = np.vstack(kernel) if kernel else np.zeros((0, N), int)
    return kernel


def is_multiple_of_ones(v):
    return len(set(v.tolist())) == 1


def loop_lift_sum(lm, positions):
    """Integer edge-type sum m = sum(s*e_j) around a physical path."""
    P = np.asarray(positions, float)
    N = lm.N
    m = np.zeros(N, int)
    for a, b in zip(P[:-1], P[1:]):
        k, _ = lm.classify(b - a)
        j = k % N
        s = 1 if k < N else -1
        m[j] += s
    return m


def main():
    for sub in ["ammann_beenker", "penrose"]:
        p = Patch(sub, radius=20.0)
        par_star, perp_star = p.par_star, p.perp_star
        N = p.N
        print(f"\n=== {sub} (Z^{N}) ===")

        # (a) integer kernel of pi_par
        ker = brute_kernel(par_star)
        nonzero = ker[np.any(ker != 0, axis=1)]
        print(f"(a) |m_i|<={RANGE}: kernel has {len(ker)} vectors "
              f"({len(nonzero)} nonzero)")
        if N == 4:
            print(f"    AB kernel trivial (only 0): {len(nonzero) == 0}")
        else:
            allmult = all(is_multiple_of_ones(v) for v in nonzero)
            print(f"    Penrose nonzero kernel all multiples of (1,1,1,1,1): "
                  f"{allmult}  (e.g. {nonzero[np.argmax(np.abs(nonzero).sum(1) > 0)] if len(nonzero) else None})")
            ones = np.ones(N, int)
            print(f"(b) ||pi_perp((1,1,1,1,1))|| = "
                  f"{np.linalg.norm(ones @ perp_star):.2e}")

        # (c) corollary: v2 tight-loop integer sums
        lm = LiftMetric(par_star, perp_star)
        d = TerminatingLineDefect(p, j_star=1)
        sums = []
        for radius in [4, 6, 8, 10]:
            loop = ring_loop(d, radius)
            if loop is None:
                continue
            m = loop_lift_sum(lm, positions_of_path(d, loop))
            w = d.winding_number(positions_of_path(d, loop))
            perp_norm = np.linalg.norm(m @ perp_star)
            sums.append((radius, round(w, 2), m.tolist(), perp_norm))
        print("(c) v2 tight-loop integer sums m (should be 0 / multiple of ones):")
        for radius, w, m, pn in sums:
            tag = ("ZERO" if all(x == 0 for x in m)
                   else ("MULT_OF_ONES" if is_multiple_of_ones(np.array(m))
                         else "OTHER!"))
            print(f"    r={radius} w={w}: m={m}  ->{tag}  ||pi_perp(m)||={pn:.2e}")


if __name__ == "__main__":
    main()

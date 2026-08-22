#!/usr/bin/env python3
"""
Demonstration for GPT's point 2: a rigorous coarse phason field w(r) from the
rank-4 representation, and the offset-vs-strain distinction.

In cut-and-project the perpendicular coordinate h(a) = a @ perp4 IS the phason
degree of freedom. The coarse phason field is its local spatial average,

    w(r) = < h(a) >_{vertices near r},

coarse-grained over cells large compared to a tile edge. A UNIFORM perpendicular
offset (a shifted window) is w(r) = const != 0: a different but equally ideal
tiling, NOT strain. PHASON STRAIN is the spatial variation of w, i.e. grad w. So
the strain magnitude must be measured on w with its global mean removed (offset
subtracted), on the coarse field, never on raw per-vertex h differences.

The claims to demonstrate, all cheap:
  (a) clean tilings read ~0 strain, and it shrinks as the coarse-graining cell
      grows -> it is finite-cell sampling noise, not real strain;
  (b) that reading is invariant to the perpendicular offset (offset != strain);
  (c) phason flips inject real strain: flipped tilings read strain well above the
      clean finite-size floor, growing with flip damage.
"""

import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import generate, structure
from phason_flips_rank4 import apply_flips

NAME = {8: "silver", 10: "golden", 12: "platinum"}


def coarse_strain(par, perp, cell, minpop=8):
    """RMS deviation of the offset-subtracted coarse phason field w(r).

    Bin parallel positions into square cells of side `cell`, average the
    perpendicular coordinate per cell, subtract the global mean (removes uniform
    offset), and return the population-weighted RMS of the cell-mean deviations.
    Only cells with at least `minpop` vertices contribute."""
    cells = defaultdict(list)
    for i, p in enumerate(par):
        cells[(int(np.floor(p[0] / cell)), int(np.floor(p[1] / cell)))].append(i)
    gm = perp.mean(0)
    devs, wts = [], []
    for idxs in cells.values():
        if len(idxs) < minpop:
            continue
        devs.append(np.linalg.norm(perp[idxs].mean(0) - gm))
        wts.append(len(idxs))
    if not devs:
        return np.nan
    devs, wts = np.array(devs), np.array(wts)
    return float(np.sqrt(np.average(devs ** 2, weights=wts)))


def main():
    print("Coarse phason strain from w(r) = <h>_cell, offset removed\n")
    for N in (8, 10, 12):
        st = structure(N)
        star, K, par4 = st["star"], st["K"], st["par4"]

        # (a)+(b): clean, two offsets, two cell sizes.
        print(f"{NAME[N]:>9} ({N}-fold)")
        for off in ([0.1123, 0.0847], [0.5, 0.3]):
            row = []
            lifts, par, perp, _ = generate(N, 12, offset=np.array(off))
            for cell in (4.0, 8.0):
                row.append((cell, coarse_strain(par, perp, cell)))
            print("   clean  offset {:>14}:  ".format(str(off)) +
                  "   ".join(f"cell {c:>3.0f} -> strain {s:.4f}" for c, s in row))

        # (c): clean vs flipped at the larger cell.
        lifts, par, perp, ustar = generate(N, 12)
        base = coarse_strain(par, perp, 8.0)
        rng = np.random.default_rng(0)
        line = [f"clean {base:.4f}"]
        for fpv in (0.05, 0.10, 0.20):
            L, U, _ = apply_flips(lifts, ustar, star, K,
                                  int(round(fpv * len(lifts))), rng)
            pf = L @ par4
            hf = L @ st["perp4"]
            line.append(f"{fpv:.2f}f/v {coarse_strain(pf, hf, 8.0):.4f}")
        print("   strain vs flip damage (cell 8):  " + "   ".join(line))
        print()


if __name__ == "__main__":
    main()

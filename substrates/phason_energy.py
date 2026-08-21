#!/usr/bin/env python3
"""
The Branch B energy (PREDICTION_recovery.md) and its ground-state gate.

Energy E = sum_v -log f*(type(v)), where type(v) is the cyclic sequence of edge
directions around vertex v and f* is the distribution of those vertex types in
the clean patch. Rare-in-the-ideal configurations cost more, so the energy is
lowest when every vertex sits in a common ideal type.

The known failure mode, stated in the pre-registration and checked here BEFORE
any recovery is measured: this energy is minimised by whatever tiling maximises
the commonest vertex types, which may be a periodic approximant, not the
quasicrystal. If a low-temperature relaxation started from the clean tiling drifts
away from it, the energy does not fix the ideal as its ground state and Branch B
is withdrawn. A recovery result from an energy that does not fix the clean tiling
is worthless, so this gate comes first.
"""

import sys
from collections import Counter

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import generate, structure
from phason_flips_rank4 import apply_flips, neighbours_by_star


def vertex_types(lifts, ustar, star, K, par4):
    """Canonical vertex type per vertex: the cyclic sequence of incident edge
    directions (by angle in parallel space), reduced to its minimal rotation."""
    _, nbr = neighbours_by_star(lifts, ustar, star, K)
    m = len(star)
    ang = {}
    for k in range(m):
        for s in (1, -1):
            d = (s * star[k]) @ par4
            ang[(k, s)] = np.arctan2(d[1], d[0])
    out = []
    for steps in nbr:
        if not steps:
            out.append(())
            continue
        order = sorted(steps, key=lambda ks: ang[ks])
        seq = tuple(k if s > 0 else k + m for k, s in order)
        rots = [seq[r:] + seq[:r] for r in range(len(seq))]
        out.append(min(rots))
    return out


def clean_frequencies(types, interior_only=True):
    """f*: frequency of each vertex type. Boundary vertices (degree < 3) dropped
    so the ideal statistics are read from the bulk."""
    c = Counter(t for t in types if not interior_only or len(t) >= 3)
    tot = sum(c.values())
    return {t: n / tot for t, n in c.items()}


def energy(types, freq, floor=1e-6):
    """Total energy over bulk vertices; unseen types pay -log(floor)."""
    return float(sum(-np.log(freq.get(t, floor)) for t in types if len(t) >= 3))


def bulk_mask(types):
    return np.array([len(t) >= 3 for t in types])


def main():
    print("Sanity: does phason damage raise the Branch B energy?\n")
    print(f"{'':>9} {'types':>6} {'E_clean/bulk':>13} {'E_dmg/bulk':>12} "
          f"{'rises?':>7}")
    for N, nm in ((8, "silver"), (10, "golden"), (12, "platinum")):
        st = structure(N)
        star, K, par4 = st["star"], st["K"], st["par4"]
        lifts, _, _, ustar = generate(N, 10)
        t0 = vertex_types(lifts, ustar, star, K, par4)
        freq = clean_frequencies(t0)
        b0 = bulk_mask(t0)
        e0 = energy(t0, freq) / b0.sum()

        rng = np.random.default_rng(0)
        L, U, _ = apply_flips(lifts, ustar, star, K,
                              int(round(0.10 * len(lifts))), rng)
        t1 = vertex_types(L, U, star, K, par4)
        b1 = bulk_mask(t1)
        e1 = energy(t1, freq) / b1.sum()
        print(f"{nm:>9} {len(freq):>6} {e0:>13.4f} {e1:>12.4f} "
              f"{'yes' if e1 > e0 else 'NO':>7}")


if __name__ == "__main__":
    main()

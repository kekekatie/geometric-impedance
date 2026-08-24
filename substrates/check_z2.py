#!/usr/bin/env python3
"""
Fable's Point 4, checked (not built): is there an inversion Z2 in the window that
silver lacks, is it conserved or swapped under a legal flip, and is it the source
of golden's degree-independent address richness?

Inversion a -> -a sends the congruence class c -> (mod - c) mod mod, so it pairs
classes into inversion orbits and negates the perpendicular centroid. A flip moves
a vertex's class by a fixed lattice increment; whether any function of the class
survives every such increment says whether there is a conserved discrete charge.
"""

import sys
from collections import Counter

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from generate_rank4 import build_edges, classes_of, generate, structure
from phason_flips_rank4 import flippable

NAME = {8: "silver", 10: "golden", 12: "platinum"}


def main():
    for N in (8, 10, 12):
        st = structure(N)
        star, K, par4, perp4, mod = (st["star"], st["K"], st["par4"],
                                     st["perp4"], st["mod"])
        lifts, par, perp, ustar = generate(N, 10)
        cl = classes_of(lifts, N)
        hstar = lifts @ perp4                      # offset-free perp
        occ = sorted(set(cl.tolist()))
        print(f"=== {NAME[N]} ({N}-fold): classes={st['classes']}, occupied={occ} ===")

        # inversion pairing shows up as EQUAL class sizes (a<->-a partners have
        # equal-area window pieces); the arithmetic partner of class c is (-c) mod.
        sizes = {c: int((cl == c).sum()) for c in occ}
        print(f"   class sizes: {sizes}")

        # flip class transitions: is any function of class conserved?
        sites = flippable(lifts, ustar, star, K)
        trans = Counter()
        for i, tgt, _ in sites:
            c_after = int(classes_of(np.asarray(tgt, dtype=np.int64)[None, :], N)[0])
            trans[(int(cl[i]), c_after)] += 1
        if st["classes"] > 1:
            print(f"   flip class transitions (before->after): {dict(trans)}")
            deltas = sorted({(b - a) % int(np.prod(mod)) for (a, b) in trans})
            print(f"   distinct class increments under flips: {deltas}  "
                  f"(mod {int(np.prod(mod))})")
        print()


if __name__ == "__main__":
    main()

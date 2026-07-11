#!/usr/bin/env python3
"""Paper-and-pencil check: is the faithful Penrose approximant actually periodic
under a CLASS-PRESERVING period (sum(m) == 0 mod 5), even though it looks
non-periodic under the class-shifting P_a, P_b the validator used?

If yes: the approximant was periodic all along; the validator just used the
wrong (too-small, class-shifting) period cell. The true cell is 5x larger --
which IS the physical meaning of the four-class structure.
"""
import sys, os, itertools
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reverse_loop_test"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "approximant"))
from scipy.spatial import cKDTree
from phason_shear import PhasonShearApproximant

def periodicity_under(ap, m_lift, tree, interior):
    """Fraction of interior vertices whose image under +pi_par(m_lift) lands on a
    vertex (within 1e-6)."""
    P = m_lift @ ap.par_star
    ok = tot = 0
    for i in interior:
        tgt = ap.par[i] + P
        if np.linalg.norm(tgt) < ap.radius - 1.0:
            d, _ = tree.query(tgt)
            tot += 1; ok += (d < 1e-6)
    return (ok / tot if tot else float("nan")), tot

def shortest_classpreserving(M_a, M_b, N, span=6):
    """Smallest two independent integer combos a*M_a+b*M_b with sum==0 mod N."""
    cands = []
    for a, b in itertools.product(range(-span, span+1), repeat=2):
        if a == 0 and b == 0:
            continue
        m = a*M_a + b*M_b
        if int(m.sum()) % N == 0:
            cands.append((np.linalg.norm(m @ np.eye(N)), a, b, m))
    cands.sort(key=lambda t: t[0])
    basis = []
    for _, a, b, m in cands:
        if not basis:
            basis.append((a, b, m)); continue
        # independence from first
        a0, b0, _ = basis[0]
        if a0*b - b0*a != 0:
            basis.append((a, b, m)); break
    return basis

for sub, oi, radius in [("penrose", 0, 26.0), ("penrose", 1, 30.0),
                        ("ammann_beenker", 1, 22.0)]:
    ap = PhasonShearApproximant(sub, oi, radius=radius)
    N = ap.N
    tree = cKDTree(ap.par)
    r = np.linalg.norm(ap.par, axis=1)
    interior = np.where(r < 0.45*ap.radius)[0]
    sa, sb = int(ap.M_a.sum()) % N, int(ap.M_b.sum()) % N
    print(f"\n=== {sub} order {ap.order} ({ap.convergent}) ===")
    print(f"  class-shift of P_a = +{sa},  P_b = +{sb}")
    base_a, na = periodicity_under(ap, ap.M_a, tree, interior)
    base_b, nb = periodicity_under(ap, ap.M_b, tree, interior)
    print(f"  periodicity under P_a (class-shift +{sa}): {100*base_a:5.1f}%  (n={na})")
    print(f"  periodicity under P_b (class-shift +{sb}): {100*base_b:5.1f}%  (n={nb})")
    basis = shortest_classpreserving(ap.M_a, ap.M_b, N)
    for a, b, m in basis:
        pct, n = periodicity_under(ap, m, tree, interior)
        print(f"  periodicity under class-PRESERVING {a:+d}*M_a{b:+d}*M_b "
              f"(shift +{int(m.sum())%N}): {100*pct:5.1f}%  (n={n})")

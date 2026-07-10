#!/usr/bin/env python3
"""Verify the candidate fix (Penrose sum(gamma) -> integer) is a faithful P3
and that AB is unaffected. Checks: max coord, connectivity, size-stability,
residue classes."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reverse_loop_test"))
from geometry import Patch

def build(name, target_sum, radius):
    seed = np.array([0.2, 0.13, 0.37, 0.06, 0.29])
    N = 5 if name == "penrose" else 4
    base = seed[:N].copy()
    base = base - base.sum()/N + target_sum/N
    return Patch(name, radius=radius, gammas=base)

def report(name, tsum, radii=(10.0, 16.0, 22.0)):
    print(f"\n### {name}  sum(gamma)={tsum}")
    for R in radii:
        p = build(name, tsum, R)
        degs = np.array([len(a) for a in p.adj])
        r = np.linalg.norm(p.par, axis=1)
        im = r <= 0.75*R
        comp = p.largest_component()
        idh = np.bincount(degs[im], minlength=11)
        # degree distribution as fractions (interior), for size-stability
        frac = np.round(idh[3:8] / max(im.sum(),1), 4)
        print(f"  R={R:5.1f} n={p.n:5d} int={im.sum():5d} "
              f"maxcoord={degs[im].max():2d} "
              f"largest_comp={len(comp)}/{p.n} "
              f"rc={np.unique(p.residue_class).tolist()}")
        print(f"          interior degree frac [3,4,5,6,7]={frac.tolist()}  "
              f"mean_deg={degs[im].mean():.3f}")

print("="*70); print("CANDIDATE FIX VERIFICATION"); print("="*70)
report("penrose", 0.0)
report("penrose", 0.5)   # current (broken)
print("\n" + "-"*70)
report("ammann_beenker", 0.5)  # current
report("ammann_beenker", 0.0)  # does AB change?

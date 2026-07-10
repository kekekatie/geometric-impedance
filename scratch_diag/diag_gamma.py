#!/usr/bin/env python3
"""Decisive test: is the Penrose over-coordination caused by sum(gamma)!=integer
(generalized Penrose tiling) rather than by the acceptance window?

We sweep the gamma-sum target and report interior degree histograms.
For a true de Bruijn Penrose (P3), sum(gamma) must be an integer.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reverse_loop_test"))
from geometry import Patch

np.set_printoptions(precision=4, suppress=True)

def build_with_gamma_sum(name, target_sum, radius=16.0, seed_base=None):
    """Reproduce geometry.py's gamma recipe but force a chosen sum."""
    if seed_base is None:
        seed_base = np.array([0.2, 0.13, 0.37, 0.06, 0.29])
    N = 5 if name == "penrose" else 4
    base = seed_base[:N].copy()
    # shift so the sum equals target_sum, keeping individual offsets generic
    base = base - base.sum()/N + target_sum/N
    p = Patch(name, radius=radius, gammas=base)
    return p

def interior_mask(p, frac=0.75):
    r = np.linalg.norm(p.par, axis=1)
    return r <= frac * p.radius

for name in ["penrose"]:
    print("="*70); print(name.upper()); print("="*70)
    for tsum in [0.0, 0.5, 1.0, 2.0, 0.25, 1e-4]:
        p = build_with_gamma_sum(name, tsum)
        degs = np.array([len(a) for a in p.adj])
        im = interior_mask(p)
        idh = np.bincount(degs[im], minlength=11)
        # residue-class values present
        rc = np.unique(p.residue_class)
        print(f"  sum(g)={tsum:6.4f}  n={p.n:4d} int={im.sum():4d}  "
              f"maxcoord={degs[im].max():2d}  hist={idh.tolist()}  rc_present={rc.tolist()}")

#!/usr/bin/env python3
"""Does a TORUS Penrose control pass Stage-D gate #1 (degree-histogram match)?

The planar phason-shear approximant has a systematic degree-5/7 deficit vs ideal
(~0.08-0.12 TVD). Two hypotheses:
  (H-boundary) it's open-patch boundary / finite-size contamination -> a torus
     (no boundary, all bulk) should match the ideal much better.
  (H-intrinsic) it's a real property of the rational approximant -> the torus,
     being the SAME rational approximant, keeps the same bulk deficit.

A valid Penrose torus must wrap by a PERIOD -- i.e. the class-PRESERVING cell
(sum(m)==0 mod 5), the 5x cell we found. Wrapping by the naive class-shifting
{M_a,M_b} would glue wrong-class vertices at the seam. We build the torus on the
class-preserving generators and read its (boundary-free) degree histogram.
"""
import sys, os, json, itertools
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reverse_loop_test"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "defect_holonomy_test"))
from geometry import Patch, star_vectors, SUBSTRATES
from torus_holonomy import build_torus

def class_preserving_basis(M_a, M_b, N, par_star, span=8):
    sa, sb = int(M_a.sum()) % N, int(M_b.sum()) % N
    cands = []
    for a in range(-span, span + 1):
        for b in range(-span, span + 1):
            if a == 0 and b == 0:
                continue
            if (a * sa + b * sb) % N == 0:
                m = a * M_a + b * M_b
                cands.append((float(np.linalg.norm(m @ par_star)), a, b, m))
    cands.sort(key=lambda t: t[0])
    a0 = b0 = None; basis = []
    for _, a, b, m in cands:
        if not basis:
            a0, b0 = a, b; basis.append(m)
        elif a0 * b - b0 * a != 0:
            basis.append(m); break
    return basis

def ideal_bulk_hist(substrate, radius=26.0, frac=0.6):
    p = Patch(substrate, radius=radius)
    r = np.linalg.norm(p.par, axis=1)
    degs = np.array([len(a) for a in p.adj])[r < frac * radius]
    h = np.bincount(degs, minlength=9)[2:9].astype(float)
    return h / h.sum()

def torus_degree_hist(substrate, g1, g2, radius):
    tor = build_torus(substrate, g1, g2, radius=radius)
    adj = tor["adj"]; cell = tor["cell"]
    degs = np.array([len(adj.get(int(i), [])) for i in cell])
    degs = degs[degs > 0]  # drop any unlinked (shouldn't be, on a torus)
    h = np.bincount(degs, minlength=9)[2:9].astype(float)
    return h / h.sum(), len(cell), degs

def tvd(a, b):
    return 0.5 * np.abs(a - b).sum()

reg = json.load(open(os.path.join(os.path.dirname(__file__), "..",
                     "defect_holonomy_test", "phase0_registration.json")))
cfg = SUBSTRATES["penrose"]; ps, _ = star_vectors(5, cfg["par_step"], cfg["perp_step"])
ideal = ideal_bulk_hist("penrose")
print("ideal Penrose bulk degree hist [3..8]:", np.round(ideal, 3).tolist())
print()
for oi in [0, 1]:
    o = reg["penrose"]["orders"][oi]
    M_a = np.array(o["M_a"]); M_b = np.array(o["M_b"])
    g = class_preserving_basis(M_a, M_b, 5, ps)
    # radius must cover the (long) class-preserving cell
    side = max(np.linalg.norm(g[0] @ ps), np.linalg.norm(g[1] @ ps))
    radius = 1.4 * side + 5.0
    th, ncell, degs = torus_degree_hist("penrose", g[0], g[1], radius)
    print(f"order {o['order']} ({o['convergent']}): torus cell vertices={ncell} "
          f"maxdeg={degs.max()} meandeg={degs.mean():.2f}")
    print(f"   torus bulk degree hist [3..8]: {np.round(th,3).tolist()}")
    print(f"   TVD(torus vs ideal) = {tvd(th, ideal):.3f}   "
          f"(planar approximant was ~0.08-0.12)")
    print()

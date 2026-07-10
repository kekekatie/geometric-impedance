#!/usr/bin/env python3
"""Why is the Penrose phason-shear approximant only ~50% periodic?
Hypothesis: per-residue-class windows are inconsistent under the residue shift
the period vector induces (some classes map to class 0, which has no window).
Instrument the periodicity check to see WHY each interior vertex passes/fails."""
import sys, os
import numpy as np
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "reverse_loop_test"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "approximant"))
from scipy.spatial import cKDTree
from phason_shear import PhasonShearApproximant

for sub, oi in [("penrose", 0), ("penrose", 1), ("ammann_beenker", 1)]:
    ap = PhasonShearApproximant(sub, oi, radius=14.0)
    N = ap.N
    rc = (ap.K.sum(1) % N)
    tree = cKDTree(ap.par)
    r = np.linalg.norm(ap.par, axis=1)
    Rp = 0.55 * ap.radius
    sM_a = int(ap.M_a.sum() % N)
    sM_b = int(ap.M_b.sum() % N)
    classes_present = sorted(set(rc.tolist()))
    fail_by_class = Counter(); pass_by_class = Counter()
    fail_target_class = Counter()
    for i in np.where(r < Rp)[0]:
        for P, dS in ((ap.P_a, sM_a), (ap.P_b, sM_b)):
            tgt = ap.par[i] + P
            if np.linalg.norm(tgt) < ap.radius - 1.0:
                d, _ = tree.query(tgt)
                src_c = int(rc[i]); tgt_c = (src_c + dS) % N
                if d < 1e-6:
                    pass_by_class[src_c] += 1
                else:
                    fail_by_class[src_c] += 1
                    fail_target_class[tgt_c] += 1
    tot = sum(pass_by_class.values()) + sum(fail_by_class.values())
    nfail = sum(fail_by_class.values())
    print(f"\n== {sub} order {ap.order} ({ap.convergent}) ==")
    print(f"  classes present in tiling: {classes_present}   "
          f"period class-shifts: +{sM_a}(P_a) +{sM_b}(P_b)")
    print(f"  periodicity = {100*(tot-nfail)/max(tot,1):.1f}%  ({nfail}/{tot} fail)")
    print(f"  FAIL count by SOURCE class: {dict(sorted(fail_by_class.items()))}")
    print(f"  PASS count by SOURCE class: {dict(sorted(pass_by_class.items()))}")
    print(f"  FAIL count by TARGET class (where the arrow sends them): "
          f"{dict(sorted(fail_target_class.items()))}")
    print(f"  (target class 0 = nonexistent-in-true-Penrose -> guaranteed miss)")

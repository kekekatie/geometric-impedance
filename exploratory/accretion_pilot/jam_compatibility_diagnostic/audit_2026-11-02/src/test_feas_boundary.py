#!/usr/bin/env python3
"""
test_feas_boundary.py -- focused FAILURE / BOUNDARY tests for the feasibility
certifier, added by the 2026-11-02 audit (Part 2). Complements the study's
tests/test_feas.py (polygon / segment / point / empty), which is retained and
still passes. Exits non-zero on failure.

Run (from this dir, with EFP_SNAPSHOT set):  python3 test_feas_boundary.py
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
import feas

FAILS = []


def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    # 1. Solver failure must become 'unresolved', never feasible.
    orig = feas.linprog
    class _Res:
        status = 4; x = None; message = "simulated"
    try:
        feas.linprog = lambda *a, **k: _Res()
        r = feas.classify_rows([((1, 0), -1), ((0, 1), -1)])
        check(r["cls"] == "unresolved", f"LP failure -> 'unresolved' (got {r['cls']})")
        check(r["cls"] not in ("positive_area", "lower_dimensional"),
              "LP failure never silently becomes feasible")
    finally:
        feas.linprog = orig

    # 2. A clearly-infeasible opposing pair is stable and box-independent in margin.
    opp = [((1, 0), 1.0), ((-1, 0), 1.0)]   # x>=1 and -x>=1  => infeasible, gap 2, r*=-1
    r = feas.classify_rows(opp)
    check(r["cls"] == "infeasible" and abs(r["r"] + 1.0) < 1e-6,
          f"anti-parallel opposing pair -> infeasible r~-1 (got {r['cls']}, r={r['r']:.3g})")

    # 3. BOX BLIND SPOT: a genuinely feasible unit box centred at (1000,1000) is
    #    MISREAD as infeasible by the fixed BOX=50 certifier -- a documented scope
    #    limit. With a large box it is correctly positive-area.
    far = [((1, 0), 999.0), ((-1, 0), -1001.0), ((0, 1), 999.0), ((0, -1), -1001.0)]
    rbox = feas.classify_rows(far)
    check(rbox["cls"] == "infeasible",
          "fixed BOX=50 misreads a feasible region at (1000,1000) as infeasible (documented limitation)")
    res = feas.chebyshev_rows(feas._unit(far), box=1e6)
    check(res["x"] is not None and res["x"][2] > 0.5,
          f"with a large box the far region is correctly feasible (r={res['x'][2] if res['x'] else None})")

    # 4. Near-zero margin: a thin feasible slab (r* just above tol) is positive_area,
    #    and an identical slab squeezed to negative width flips to infeasible.
    slab_pos = [((1, 0), -1e-6), ((-1, 0), -1e-6), ((0, 1), -1), ((0, -1), -1)]  # |x|<=1e-6
    slab_neg = [((1, 0), 1e-6), ((-1, 0), 1e-6), ((0, 1), -1), ((0, -1), -1)]    # |x|<=-1e-6 (empty)
    rp, rn = feas.classify_rows(slab_pos), feas.classify_rows(slab_neg)
    check(rp["cls"] in ("positive_area", "lower_dimensional") and rn["cls"] == "infeasible",
          f"thin positive slab feasible ({rp['cls']}), negative slab infeasible ({rn['cls']})")

    # 5. Empty constraint set -> feasible full box (degenerate input handled).
    r = feas.classify_rows([])
    check(r["cls"] == "positive_area", f"no constraints -> positive_area (got {r['cls']})")

    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)}"); sys.exit(1)
    print("ALL BOUNDARY/FAILURE CHECKS PASSED.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Controlled-example validation of the feasibility certifier (feas.classify_rows),
per PROTOCOL.md Part 2: a polygon, a segment, a point, and an empty intersection,
plus a numerical sensitivity note. Exits non-zero on failure.

Run (from this dir, with EFP_SNAPSHOT set):  python test_feas.py
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import feas

FAILS = []


def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


# half-planes as n.t >= c
SQUARE = [((1, 0), -1), ((-1, 0), -1), ((0, 1), -1), ((0, -1), -1)]   # |x|<=1,|y|<=1
SEGMENT = [((1, 0), 0), ((-1, 0), 0), ((0, 1), -1), ((0, -1), -1)]    # x=0, y in [-1,1]
POINT = [((1, 0), 0), ((-1, 0), 0), ((0, 1), 0), ((0, -1), 0)]        # (0,0)
EMPTY = [((1, 0), 1), ((-1, 0), 1)]                                   # x>=1 and x<=-1


def main():
    r = feas.classify_rows(SQUARE)
    check(r["cls"] == "positive_area" and r["dim"] == 2 and abs(r["r"] - 1.0) < 1e-6,
          f"unit square -> positive_area dim2 r~1 (got {r['cls']}, r={r['r']:.3g})")

    r = feas.classify_rows(SEGMENT)
    check(r["cls"] == "lower_dimensional" and r["dim"] == 1,
          f"segment -> lower_dimensional dim1 (got {r['cls']}, dim={r.get('dim')}, r={r['r']:.2e})")

    r = feas.classify_rows(POINT)
    check(r["cls"] == "lower_dimensional" and r["dim"] == 0,
          f"point -> lower_dimensional dim0 (got {r['cls']}, dim={r.get('dim')}, r={r['r']:.2e})")

    r = feas.classify_rows(EMPTY)
    check(r["cls"] == "infeasible" and abs(r["r"] + 1.0) < 1e-6,
          f"empty -> infeasible r~-1 (got {r['cls']}, r={r['r']:.3g})")

    # sensitivity: a full-dimensional region and a clearly-infeasible one are STABLE
    # under small perturbation; a degenerate (point/segment) region is FRAGILE.
    def sens(rows, eps=1e-6):
        seen = set()
        for sgn in (+1, -1):
            seen.add(feas.classify_rows([(n, c + sgn * eps) for n, c in rows])["cls"])
        seen.add(feas.classify_rows(rows)["cls"])
        return seen
    check(sens(SQUARE) == {"positive_area"}, "square classification stable under +/-1e-6")
    check(sens(EMPTY) == {"infeasible"}, "empty classification stable under +/-1e-6")
    frag = sens(POINT)
    check(len(frag) > 1,
          f"point classification is correctly FRAGILE under +/-1e-6 (saw {sorted(frag)}) "
          "-> lower-dimensional feasibility needs exact care, reported as such")

    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)}")
        sys.exit(1)
    print("ALL FEASIBILITY-CERTIFIER CHECKS PASSED.")


if __name__ == "__main__":
    main()

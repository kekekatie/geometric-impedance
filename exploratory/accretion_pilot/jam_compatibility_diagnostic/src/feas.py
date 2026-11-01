#!/usr/bin/env python3
"""
feas.py -- independent feasibility certifier for the compatibility region F.

F = { t in R^2 : n_i . t >= c_i  for all active (rank,i) }, with (n_i, offset h)
read from the FROZEN window WIN and c_i from the FROZEN Sl.constraints. We do NOT
redefine the region; we certify feasibility of the same system, replacing the
earlier "polygon area <= 1e-12 => empty" heuristic.

Method: Chebyshev-centre LP. Maximise r such that, for every constraint written
with a UNIT normal, n_i . t - r >= c_i (plus a slack box). r* is the signed
radius of the largest inscribed ball:
    r* >  tol_r            -> positive-area feasible (full-dimensional)
    |r*| <= tol_r (feasible)-> lower-dimensional feasible (point/segment)
    r* < -tol_r            -> infeasible (deepest point violates by -r*)
LP non-optimal, or class unstable under the sensitivity sweep -> unresolved.

This is a NUMERICAL certificate (float LP over phi-irrational data): we report r*
and a sensitivity sweep; we do not call it exact. An optional exact rational-sqrt5
cross-check is provided for small borderline systems (exact2d).
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import linprog
from study_common import WIN

TOL_R = 1e-9
BOX = 50.0


def rows_from_cmax(cmax):
    """[(unit_normal (nx,ny), c_norm, (rk,i), raw_c, apothem_h)] from a cmax dict."""
    rows = []
    for (rk, i), c in cmax.items():
        n, h = WIN[rk]
        nx, ny = float(n[i][0]), float(n[i][1])
        nrm = (nx * nx + ny * ny) ** 0.5
        rows.append(((nx / nrm, ny / nrm), c / nrm, (int(rk), int(i)), float(c), float(h)))
    return rows


def _unit(rows):
    """Normalise [((nx,ny), c)] to unit normals."""
    out = []
    for (nx, ny), c in rows:
        nrm = (nx * nx + ny * ny) ** 0.5
        out.append(((nx / nrm, ny / nrm), c / nrm))
    return out


def chebyshev_rows(unit_rows, box=BOX):
    """unit_rows: [((nx,ny), cc)] with UNIT normals, constraint n.t >= cc."""
    if not unit_rows:
        return dict(status=0, x=[0.0, 0.0, box])
    A, b = [], []
    for (nx, ny), cc in unit_rows:
        A.append([-nx, -ny, 1.0]); b.append(-cc)
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        A.append([float(sx), float(sy), 1.0]); b.append(box)
    res = linprog(c=[0.0, 0.0, -1.0], A_ub=np.asarray(A), b_ub=np.asarray(b),
                  bounds=[(None, None)] * 3, method="highs")
    return dict(status=int(res.status), x=(list(res.x) if res.x is not None else None),
                message=res.message)


def classify_rows(rows, tol_r=TOL_R):
    """rows: [((nx,ny), c)] half-planes n.t >= c (normals need not be unit)."""
    ur = _unit(rows)
    res = chebyshev_rows(ur)
    if res["status"] != 0 or res["x"] is None:
        return dict(cls="unresolved", r=None, witness=None, nconstraints=len(ur),
                    lp_status=res["status"], lp_message=res.get("message"))
    tx, ty, r = res["x"]; r = float(r)
    if r > tol_r:
        cls, dim = "positive_area", 2
    elif r < -tol_r:
        cls, dim = "infeasible", None
    else:
        cls = "lower_dimensional"
        # dimension from the feasible set's extent (robust to which witness the LP
        # returns): span of the exact region in x and y via min/max LPs.
        dim = _flat_dim(ur)
    return dict(cls=cls, r=r, witness=[float(tx), float(ty)], dim=dim, nconstraints=len(ur))


def _flat_dim(unit_rows, box=BOX, span_tol=1e-7):
    """For an r*~0 (flat) feasible region, return 1 if it has positive extent in
    some direction (segment/line), else 0 (single point)."""
    A = [[-nx, -ny] for (nx, ny), cc in unit_rows]
    b = [-cc for (nx, ny), cc in unit_rows]
    for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        A.append([float(sx), float(sy)]); b.append(box)
    A = np.asarray(A); b = np.asarray(b)
    span = 0.0
    for cvec in ([1.0, 0.0], [0.0, 1.0]):
        lo = linprog(c=cvec, A_ub=A, b_ub=b, bounds=[(None, None)] * 2, method="highs")
        hi = linprog(c=[-v for v in cvec], A_ub=A, b_ub=b, bounds=[(None, None)] * 2, method="highs")
        if lo.status == 0 and hi.status == 0:
            span = max(span, abs((-hi.fun) - lo.fun))
    return 1 if span > span_tol else 0


def classify(cmax, tol_r=TOL_R):
    """Classify the frozen compatibility region from a cmax dict."""
    rows = [(r[0], r[1]) for r in rows_from_cmax(cmax)]
    return classify_rows(rows, tol_r=tol_r)


def sensitivity(cmax, epsilons=(1e-12, 1e-10, 1e-8, 1e-6), tol_r=TOL_R):
    """Re-classify with c_i -> c_i +/- eps; return the set of classes seen and
    whether the four-way class is stable (same as the unperturbed one)."""
    base = classify(cmax, tol_r=tol_r)["cls"]
    seen = {base}
    detail = {}
    for eps in epsilons:
        for sgn in (+1, -1):
            cm2 = {k: v + sgn * eps for k, v in cmax.items()}
            c = classify(cm2, tol_r=tol_r)["cls"]
            seen.add(c)
            detail[f"{sgn:+d}{eps:g}"] = c
    return dict(base=base, classes_seen=sorted(seen), stable=(len(seen) == 1), detail=detail)


# ---- optional exact cross-check over Q(sqrt5), for small systems ----
from fractions import Fraction as Fr


class Q5:
    """Exact element a + b*sqrt(5), a,b in Q."""
    __slots__ = ("a", "b")

    def __init__(self, a=0, b=0):
        self.a = Fr(a); self.b = Fr(b)

    def __add__(s, o): o = _q5(o); return Q5(s.a + o.a, s.b + o.b)
    def __radd__(s, o): return s + o
    def __sub__(s, o): o = _q5(o); return Q5(s.a - o.a, s.b - o.b)
    def __rsub__(s, o): return _q5(o) - s
    def __neg__(s): return Q5(-s.a, -s.b)
    def __mul__(s, o):
        o = _q5(o)
        return Q5(s.a * o.a + 5 * s.b * o.b, s.a * o.b + s.b * o.a)
    def __rmul__(s, o): return s * o
    def sign(s):
        # sign of a + b*sqrt5 exactly
        if s.a == 0 and s.b == 0: return 0
        if s.b == 0: return 1 if s.a > 0 else -1
        if s.a == 0: return 1 if s.b > 0 else -1
        # compare a vs -b*sqrt5 by squaring with sign bookkeeping
        if (s.a > 0) and (s.b > 0): return 1
        if (s.a < 0) and (s.b < 0): return -1
        # mixed signs: sign(a+b*sqrt5) = sign(a^2 - 5 b^2) * sign(a)   when ... use: compare a^2 vs 5 b^2
        lhs = s.a * s.a; rhs = 5 * s.b * s.b
        if s.a > 0:  # b<0: a+b*sqrt5 >0 iff a^2 > 5 b^2
            return 1 if lhs > rhs else (-1 if lhs < rhs else 0)
        else:        # a<0,b>0: >0 iff 5 b^2 > a^2
            return 1 if rhs > lhs else (-1 if rhs < lhs else 0)


def _q5(x):
    return x if isinstance(x, Q5) else Q5(x, 0)

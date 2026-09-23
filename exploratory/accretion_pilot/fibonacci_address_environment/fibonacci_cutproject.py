#!/usr/bin/env python3
"""
fibonacci_cutproject.py -- one standard Fibonacci model set (1D cut-and-project), with
EXACT algebraic arithmetic in Z[tau], and the local-environment <-> acceptance-window
correspondence.  Static geometry only; no dynamics.

Construction (stated exactly):
  tau  = (1+sqrt5)/2,  tau' = 1 - tau = (1-sqrt5)/2   (Galois conjugate / star).
  Lattice of addresses:  Z[tau] = { m + n*tau : m,n in Z }.
  Physical  projection:  pi_par(m,n) = m + n*tau         (position on the line).
  Internal  projection:  pi_perp(m,n) = m + n*tau'        (the "perpendicular address";
                          equivalently the star map  (m+n*tau)^* = m + n*tau').
  Acceptance window:      W = [0, tau)   half-open (left-closed, right-open) -- ENDPOINT
                          CONVENTION fixed here.  |W| = tau.
  Model set:              Lambda = { m+n*tau : (m,n) in Z^2, pi_perp(m,n) in W }.
  Length normalisation:   consecutive positions differ by exactly tau (long tile L) or
                          exactly 1 (short tile S). So L = tau, S = 1 (verified exactly).

Everything decisive (window membership, gap = tau vs 1, window-region boundaries, and the
predicted environment) is computed with EXACT Z[tau] comparisons (sign of a + b*sqrt5).
Reference framing: Baake-Gaehler-Mazac (arXiv:2311.05387).
"""
from __future__ import annotations
import os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "fib_report.txt")
LINES, FAILS = [], []
SQRT5 = 5 ** 0.5
TAU_F = (1 + SQRT5) / 2


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


# --------------------------------------------------- exact Z[tau] (a + b*tau, a,b in Q)
def _sgn5(p: Fr, q: Fr) -> int:
    """sign of p + q*sqrt5 for rationals p,q."""
    if q == 0:
        return (p > 0) - (p < 0)
    if p == 0:
        return (q > 0) - (q < 0)
    if p > 0 and q > 0:
        return 1
    if p < 0 and q < 0:
        return -1
    d = p * p - 5 * q * q            # compare |p| vs sqrt5*|q|
    if p > 0 and q < 0:              # p + q*sqrt5 > 0  <=>  p > -q*sqrt5  <=>  p^2 > 5q^2
        return 1 if d > 0 else (-1 if d < 0 else 0)
    return -1 if d > 0 else (1 if d < 0 else 0)   # p<0,q>0


class Z:
    __slots__ = ("a", "b")

    def __init__(self, a, b=0):
        self.a = Fr(a); self.b = Fr(b)      # value = a + b*tau

    def __add__(s, o): return Z(s.a + o.a, s.b + o.b)
    def __sub__(s, o): return Z(s.a - o.a, s.b - o.b)
    def __neg__(s): return Z(-s.a, -s.b)
    def __eq__(s, o): return s.a == o.a and s.b == o.b
    def __hash__(s): return hash((s.a, s.b))

    def sign(s):
        # a + b*tau = (a + b/2) + (b/2) sqrt5
        return _sgn5(s.a + s.b / 2, s.b / 2)

    def __lt__(s, o): return (s - o).sign() < 0
    def __le__(s, o): return (s - o).sign() <= 0
    def star(s): return Z(s.a + s.b, -s.b)          # (a+b tau)^* = a + b tau' = (a+b) - b tau
    def real(s): return float(s.a) + float(s.b) * TAU_F

    def __repr__(s):
        return f"{s.a}+{s.b}t" if s.b else f"{s.a}"


TAU = Z(0, 1)          # tau
ONE = Z(1, 0)          # 1
TAUP = Z(1, -1)        # tau' = 1 - tau
S_SPLIT = Z(-1, 1)     # tau - 1  (forward split)
BWD_SPLIT = Z(1, 0)    # 1        (backward split)
ZERO = Z(0, 0)


def in_window(q: Z) -> bool:
    return (ZERO <= q) and (q < TAU)          # [0, tau)


# ------------------------------------------------------------------- generate the chain
def generate(nmax: int):
    """Return sites sorted by physical position: list of (p:Z, q:Z, (m,n))."""
    pts = []
    for n in range(-nmax, nmax + 1):
        # need q = m + n*tau' in [0,tau):  m in [ -n*tau' , tau - n*tau' )
        lo = -n * float((TAUP).real())            # approx bracket, then verify exactly
        for m in range(int(lo) - 2, int(lo) + 3):
            q = Z(m + n, -n)                      # (m + n*tau)^* = (m+n) - n*tau
            if in_window(q):
                p = Z(m, n)                       # m + n*tau
                pts.append((p, q, (m, n)))
    pts.sort(key=lambda t: t[0])                  # exact ordering by physical position
    return pts


def gaps_of(pts):
    """Exact gaps between consecutive sites; classify as 'L' (tau) or 'S' (1)."""
    g = []
    for i in range(len(pts) - 1):
        d = pts[i + 1][0] - pts[i][0]
        if d == TAU:
            g.append("L")
        elif d == ONE:
            g.append("S")
        else:
            g.append("?" + repr(d))
    return g


# ---------------------------------------------- forward / backward return maps on W
def f_step(q: Z):
    """forward: next gap + updated internal coord."""
    if q < S_SPLIT:                # q in [0, tau-1): short gap
        return "S", q + ONE
    return "L", q + TAUP           # q in [tau-1, tau): long gap  (q + tau')


def b_step(q: Z):
    """backward: previous gap + previous internal coord (inverse walk)."""
    if q < BWD_SPLIT:              # q in [0,1): previous gap L
        return "L", q - TAUP       # q - tau' = q + (tau-1)
    return "S", q - ONE            # q in [1,tau): previous gap S


def predicted_env(q: Z, r: int):
    """2r-letter environment from internal coord alone: r backward gaps then r forward."""
    fwd, qf = [], q
    for _ in range(r):
        s, qf = f_step(qf); fwd.append(s)
    bwd, qb = [], q
    for _ in range(r):
        s, qb = b_step(qb); bwd.append(s)         # bwd[0]=g[i-1], bwd[1]=g[i-2], ...
    return tuple(reversed(bwd)) + tuple(fwd)       # (g[i-r..i-1], g[i..i+r-1])


# ------------------------------------------------ derive window-region boundaries (exact)
def f_inv(y: Z):
    # invert forward map f: image [1,tau)->x=y-1 ; image [0,1)->x=y-tau'
    return (y - ONE) if (BWD_SPLIT <= y and y < TAU) else (y - TAUP)


def b_inv(y: Z):
    # invert backward map b: image [tau-1,tau)->x=y-(tau-1); image [0,tau-1)->x=y+1
    return (y - S_SPLIT) if (S_SPLIT <= y and y < TAU) else (y + ONE)


def region_boundaries(r: int):
    """Exact internal-coordinate boundaries partitioning W into environment cells:
    forward split (tau-1) pulled back r-1 times, backward split (1) pulled back r-1 times."""
    B = set()
    y = S_SPLIT
    for _ in range(r):
        B.add(y); y = f_inv(y)
    y = BWD_SPLIT
    for _ in range(r):
        B.add(y); y = b_inv(y)
    B = sorted([b for b in B if (ZERO < b and b < TAU)])
    return [ZERO] + B + [TAU]


# ------------------------------------------------------ shared example finder (r-tiles)
def examples(pts, g, N, r):
    """Return (exA, exB, exC); each = (|dq|, |dp|, i, j, env). Deterministic selection."""
    S = [(i, pts[i][0], pts[i][1], tuple(g[i - r:i + r]))
         for i in range(N) if r <= i <= N - 1 - r]

    def dpf(a, b): return abs((S[a][1] - S[b][1]).real())
    def dqf(a, b): return abs((S[a][2] - S[b][2]).real())

    a = c = None
    for u in range(len(S)):
        for v in range(u + 1, len(S)):
            if S[u][3] == S[v][3]:
                pd, qd = dpf(u, v), dqf(u, v)
                if pd > 6 and (a is None or qd < a[0]):
                    a = (qd, pd, S[u][0], S[v][0], S[u][3])
                if c is None or qd > c[0]:
                    c = (qd, pd, S[u][0], S[v][0], S[u][3])
    order = sorted(range(len(S)), key=lambda k: S[k][2].real())
    b = None
    for t in range(len(order) - 1):
        u, v = order[t], order[t + 1]
        if S[u][3] != S[v][3]:
            qd = dqf(u, v)
            if b is None or qd < b[0]:
                b = (qd, dpf(u, v), S[u][0], S[v][0], (S[u][3], S[v][3]))
    return a, b, c


# ============================================================================ main
def main():
    log("=" * 78)
    log("[0] Fibonacci model set: tau=(1+v5)/2, star (m+n tau)->(m+n tau'), W=[0,tau)")
    pts = generate(46)
    N = len(pts)
    log(f"  generated {N} sites in physical order; window |W| = tau = {TAU.real():.6f}")
    require(N > 60, "enough sites for r=5 environments")

    # --- validate: gaps are exactly {tau, 1}; Fibonacci local rules ---
    g = gaps_of(pts)
    require(all(x in ("L", "S") for x in g),
            "every gap is EXACTLY tau (L) or 1 (S) -- two-tile Fibonacci geometry")
    word = "".join(g)
    require("SS" not in word, "no SS (short tiles are isolated) -- Fibonacci signature")
    require("LLL" not in word, "no LLL (long runs are 1 or 2) -- Fibonacci signature")
    nL, nS = word.count("L"), word.count("S")
    log(f"  gap word length {len(word)}; #L={nL} #S={nS}; ratio L/S={nL/max(nS,1):.4f} "
        f"(tau={TAU_F:.4f})")
    require(abs(nL / max(nS, 1) - TAU_F) < 0.15, "L:S count ratio ~ tau (Fibonacci frequency)")

    # --- the correspondence: environment is a function of the internal coord alone ---
    for r in (2, 5):
        log("=" * 78)
        log(f"[env r={r}]  environment = {2*r}-letter word, {r} tiles each side")
        bnd = region_boundaries(r)
        log(f"  derived {len(bnd)-2} internal-window boundaries (exact); "
            f"{len(bnd)-1} environment cells")
        # check predicted (from q alone) == actual (read from chain) for all non-truncated
        ok = True; per_cell = {}
        for i in range(N):
            if i < r or i > N - 1 - r:
                continue                      # truncated neighbourhood excluded
            q = pts[i][1]
            actual = tuple(g[i - r:i + r])    # g[i-r..i+r-1]
            pred = predicted_env(q, r)
            if actual != pred:
                ok = False
            # cell index by exact comparison
            ci = max(k for k in range(len(bnd) - 1) if bnd[k] <= q)
            per_cell.setdefault(ci, set()).add(actual)
        require(ok, f"predicted environment (from internal coord) == chain-read environment "
                    f"for every non-truncated site (r={r})")
        one_per_cell = all(len(v) == 1 for v in per_cell.values())
        require(one_per_cell, f"each derived internal-window cell carries EXACTLY ONE "
                              f"environment (r={r}) -- window region <-> local patch")
        # distinct cells carry distinct environments (injective)
        envs = [next(iter(v)) for v in per_cell.values()]
        require(len(set(envs)) == len(envs),
                f"distinct cells carry distinct environments (r={r})")

    # --- the three examples (r=2) ---
    log("=" * 78)
    log("[examples] r=2 environments; report exact physical & internal separations")
    exA, exB, exC = examples(pts, g, N, 2)
    bnd2 = region_boundaries(2)

    qd, pd, x, y, ex = exA
    log(f"  (a) SAME env, close internal, far physical: |dp|={pd:.4f}, |dq|={qd:.6f}, env={ex}")
    require(exA is not None, "(a) exists: distant sites, close internal address, identical environment")

    qd, pd, x, y, ex = exB
    qx, qy = pts[x][1], pts[y][1]
    between = [b for b in bnd2 if (qx <= b <= qy) or (qy <= b <= qx)]
    log(f"  (b) DIFFERENT env, close internal: |dq|={qd:.6f}, |dp|={pd:.4f}; "
        f"boundary between at q={[round(b.real(),6) for b in between]}")
    require(len(between) >= 1, "(b) exists: near-equal internal addresses split by a "
                               "window-region boundary -> different environments")

    qd, pd, x, y, ex = exC
    ci = max(k for k in range(len(bnd2) - 1) if bnd2[k] <= pts[x][1])
    width = (bnd2[ci + 1] - bnd2[ci]).real()
    log(f"  (c) SAME env, largest internal gap: |dq|={qd:.6f} (cell width {width:.6f}), "
        f"|dp|={pd:.4f}, env={ex}")
    require(qd <= width + 1e-9, "(c) same environment => internal addresses within ONE "
                                "cell: |dq| bounded by the cell width (not arbitrary)")

    log("=" * 78)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

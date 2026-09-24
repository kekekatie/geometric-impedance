#!/usr/bin/env python3
"""
twins_mirror_feasibility.py -- the first "twins as MIRRORS" test (see DESIGN.md).

Question. Grow the accretion model directly on a Fibonacci chain, with rules that are purely
LOCAL in physical space and NEVER read the hidden (perpendicular) address. Do two far-apart
sites that are twins in the hidden window share their future anyway, and for how long?

Model (every choice below is a MODELLING ASSUMPTION, stated as such)
  substrate  a patch of the exact Fibonacci chain (../fibonacci_address_environment/); every
             site starts ACTIVE, every tile is an active bond carrying its length l in {L=tau, S=1}.
  rule       BUD at k=1 (as in the transmission paper): BUD(x,y) on an active bond x-y turns y
             quiet and adds a new active tip z with bonds x-z, y-z. Length-reading: BUD(x,y)
             fires at rate w(l_xy) = 1/l (conductance, the MOTION.md choice; 1/tau = tau-1, so
             everything stays exact in Q(tau)). New bonds inherit the parent bond's length.
             CONTINUOUS TIME (independent clocks) -- the local form of "uniform over events";
             a global lottery would couple far-apart sites through its normaliser.
  observable f = 1[the twin's own site v is still active].  u(s) = E f(X_s) = sum_n c_n s^n / n!,
             with c_n = (G^n f)(X_0), G the generator. c_n is computed EXACTLY in Q(tau).
  control    BLIND rule: w == 1 (lengths ignored).

Light-cone lemma (argued in DESIGN.md, CHECKED here): c_n depends only on the tiles within
distance n of v, i.e. on the environment E_n. So twins whose environments first disagree at
radius r* (E_{r*-1} equal, E_{r*} different) have c_n EQUAL for all n < r*.
The empirical question: does the difference actually APPEAR at n = r* (no cancellation)?

asserts + nonzero exit. Exact Q(tau) arithmetic throughout.
"""
from __future__ import annotations
import os, sys, functools
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "fibonacci_address_environment"))
import fibonacci_cutproject as F                      # exact chain + Z[tau] (no main on import)

REPORT = os.path.join(HERE, "results", "twins_mirror_feasibility_report.txt")
LINES, FAILS = [], []
N_MAX = 6                                             # highest Taylor order computed
PAD = 12


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


# ---------------- exact Q(tau): a + b*tau, tau^2 = tau + 1 (same as motion_return.Q) ----------
class Q:
    __slots__ = ("a", "b")

    def __init__(self, a, b=0):
        self.a = Fr(a); self.b = Fr(b)

    def __add__(s, o): return Q(s.a + o.a, s.b + o.b)
    def __sub__(s, o): return Q(s.a - o.a, s.b - o.b)
    def __neg__(s): return Q(-s.a, -s.b)
    def __mul__(s, o): return Q(s.a * o.a + s.b * o.b, s.a * o.b + s.b * o.a + s.b * o.b)
    def __eq__(s, o): return s.a == o.a and s.b == o.b
    def __hash__(s): return hash((s.a, s.b))
    def real(s): return float(s.a) + float(s.b) * F.TAU_F
    def __repr__(s):
        if s.b == 0:
            return f"{s.a}"
        return f"{s.a}{'+' if s.b > 0 else '-'}{abs(s.b)}t" if s.a else f"{s.b}t"


ZERO, ONE = Q(0), Q(1)
W_LEN = {"L": Q(-1, 1), "S": ONE}                     # 1/l : 1/tau = tau - 1 ; 1/1 = 1
W_BLIND = {"L": ONE, "S": ONE}

# ---------------- chain ----------------
PTS = F.generate(60)
G_ = F.gaps_of(PTS)                                   # G_[i] = tile between site i and i+1
N = len(PTS)
assert all(t in ("L", "S") for t in G_), "chain gaps must be exactly {tau, 1}"


def env(i, r):
    return tuple(G_[i - r:i + r]) if (i - r >= 0 and i + r <= N - 1) else None


def first_disagreement(i, j, rmax=40):
    for r in range(1, rmax + 1):
        a, b = env(i, r), env(j, r)
        if a is None or b is None:
            return None
        if a != b:
            return r
    return None


# ---------------- growth state: (v_active, frozenset of ((u,w), len)) over ACTIVE bonds -------
# Quiet vertices are dropped (BUD-only: no rule ever reads them). Tips are named ("z", x, y):
# BUD(x,y) can fire at most once per ordered pair (y goes quiet), so names are unique and
# commuting event orders reach the SAME state -- which is what makes memoisation effective.
def initial_state(v, R):
    bonds = frozenset(((i, i + 1), G_[i]) for i in range(v - R, v + R))
    return (True, bonds)


def events(state):
    _, bonds = state
    for (u, w), l in bonds:
        yield (u, w, l); yield (w, u, l)


def apply_bud(state, x, y, l, v):
    v_act, bonds = state
    z = ("z", x, y)
    nb = frozenset(b for b in bonds if y not in b[0])
    nb = nb | {((x, z), l)}                          # x-z active; y-z touches quiet y: dropped
    return (v_act and y != v, nb)


def taylor(v, R, W, nmax):
    """exact c_0..c_nmax of u(s) = P(v active at s), on the patch of radius R around v."""
    @functools.lru_cache(maxsize=None)
    def Gn(k, state):
        if k == 0:
            return ONE if state[0] else ZERO
        base = Gn(k - 1, state)
        tot = ZERO
        for x, y, l in events(state):
            tot = tot + W[l] * (Gn(k - 1, apply_bud(state, x, y, l, v)) - base)
        return tot
    s0 = initial_state(v, R)
    out = [Gn(k, s0) for k in range(nmax + 1)]
    Gn.cache_clear()
    return out


def onset(ci, cj):
    return next((n for n in range(len(ci)) if ci[n] != cj[n]), None)


def main():
    log("=" * 90)
    log("TWINS AS MIRRORS -- feasibility: does hidden-address depth set the shared future?")
    log("=" * 90)
    log(f"  chain: {N} sites, exact gaps; rates BUD(x,y) = 1/l (L: tau-1, S: 1); control w == 1")

    # ---- pick twin pairs with r* = 1..N_MAX, far apart physically, well padded ----
    lo, hi = PAD + N_MAX + 2, N - PAD - N_MAX - 2
    pairs = {}
    for i in range(lo, hi):
        for j in range(i + 1, hi):
            r = first_disagreement(i, j)
            if r is not None and 1 <= r <= N_MAX and r not in pairs and (j - i) >= 20:
                pairs[r] = (i, j)
    require(sorted(pairs) == list(range(1, N_MAX + 1)),
            f"found far-apart site pairs with first-disagreement radius r* = 1..{N_MAX}")

    # ---- light-cone lemma, checked: radius R = n and R = n+1 patches give the same c_n ----
    log("-" * 90)
    log("[light cone] c_n on patch radius R=n equals c_n on patch radius R=n+1 (n <= 4)")
    ok = True
    for r, (i, j) in list(pairs.items())[:3]:
        for site in (i, j):
            for n in range(0, 5):
                a = taylor(site, max(n, 1), W_LEN, n)[n]
                b = taylor(site, max(n, 1) + 1, W_LEN, n)[n]
                ok &= (a == b)
    require(ok, "c_n depends only on tiles within distance n of v (enlarging the patch never "
                "changes it) -> twins agreeing on E_{r*-1} MUST agree on c_0..c_{r*-1}")

    # ---- the test: onset of disagreement vs r*, length-reading rule and blind control ----
    log("-" * 90)
    log("[test] exact Taylor coefficients c_n of P(v active at time s), twins i vs j")
    rows = []
    blind_ok = True
    for r in sorted(pairs):
        i, j = pairs[r]
        nmax = min(N_MAX, r + 1)
        ci = taylor(i, nmax, W_LEN, nmax); cj = taylor(j, nmax, W_LEN, nmax)
        bi = taylor(i, nmax, W_BLIND, nmax); bj = taylor(j, nmax, W_BLIND, nmax)
        blind_ok &= (bi == bj)
        n_on = onset(ci, cj)
        rows.append((r, i, j, n_on))
        dq = (PTS[j][1] - PTS[i][1]).real(); dp = (PTS[j][0] - PTS[i][0]).real()
        log(f"  r*={r}: sites {i},{j}  |dp|={abs(dp):6.1f}  |dq|={abs(dq):.4f}  "
            f"E_{r - 1} equal, E_{r} differ -> first differing order n = {n_on}")
        for n in range(nmax + 1):
            mark = "" if ci[n] == cj[n] else "   <-- differ"
            log(f"      c_{n}:  {ci[n]!r:>28}   vs   {cj[n]!r:<28}{mark}")
        require(all(ci[n] == cj[n] for n in range(r)),
                f"r*={r}: twins agree EXACTLY at every order n < r* (shared future)")
    require(all(n_on == r for r, _, _, n_on in rows),
            "the difference APPEARS exactly at order n = r* for every pair (no cancellation): "
            "hidden-address depth = length of the exactly-shared future")
    require(blind_ok, "BLIND control (lengths ignored): every pair identical at every computed "
                      "order -- without a rule that reads geometry, the address is invisible")

    log("=" * 90)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

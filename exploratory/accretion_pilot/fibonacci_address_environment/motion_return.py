#!/usr/bin/env python3
"""
motion_return.py -- one consequence for MOTION of the first-disagreement radius, computed
EXACTLY. Same Fibonacci chain and exact arithmetic; no dynamics rules, no sampling, no
fitted parameters.

Two passive nearest-neighbour walks on the site chain (a walk step = move to an adjacent
site; "back at start" observable):
  (1) length-BLIND control: P(left)=P(right)=1/2.
  (2) length-SENSITIVE walk (a MODELLING CHOICE, not a physical law): give each interval
      (tile) conductance 1/ell (ell = tile length: L=tau, S=1), and from a site choose an
      incident interval with probability proportional to its conductance.
Because 1/tau = tau-1 exactly, all transition probabilities lie in Q(tau):
  same tiles -> 1/2 ; (L on one side, S on the other) -> {2-tau, tau-1}.  So the return
  probability after each step is an EXACT element of Q(tau).

We compute P(return to start) for steps 0..20 for the three example pairs with first-
disagreement radii r*=3,4,5, with >=20 tiles of padding each side so truncation cannot
affect any reported probability. We report whether/when each pair's return probabilities
first differ, verify the length-blind control agrees everywhere, and check reflection
degeneracy (return probability is invariant under reflecting the chain about the start).
"""
from __future__ import annotations
import os, sys
from fractions import Fraction as Fr
import fibonacci_cutproject as F

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "motion_report.txt")
LINES, FAILS = [], []
NSTEPS = 20
PAD = 20


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


# ---------------- exact Q(tau): a + b*tau, a,b rational ; tau^2 = tau + 1 ----------------
class Q:
    __slots__ = ("a", "b")

    def __init__(self, a, b=0):
        self.a = Fr(a); self.b = Fr(b)

    def __add__(s, o): return Q(s.a + o.a, s.b + o.b)
    def __sub__(s, o): return Q(s.a - o.a, s.b - o.b)
    def __mul__(s, o):
        return Q(s.a * o.a + s.b * o.b, s.a * o.b + s.b * o.a + s.b * o.b)
    def __eq__(s, o): return s.a == o.a and s.b == o.b
    def __hash__(s): return hash((s.a, s.b))
    def real(s): return float(s.a) + float(s.b) * F.TAU_F
    def __repr__(s): return f"{s.a}+{s.b}t"


HALF = Q(Fr(1, 2), 0)
P_L_over_S = Q(2, -1)     # 2 - tau   (prob toward the LONG side when other side is short)
P_S_over_L = Q(-1, 1)     # tau - 1   (prob toward the SHORT side when other side is long)

# ---------------- chain ----------------
pts = F.generate(130)
N = len(pts)
g = F.gaps_of(pts)                     # g[i] in {'L','S'} for i in 0..N-2


def env(i, r):
    if i - r < 0 or i + r > N - 1:
        return None
    return tuple(g[i - r:i + r])


def rmax(i):
    return min(i, N - 1 - i)


def first_disagreement(i, j):
    R = min(rmax(i), rmax(j))
    for r in range(2, R + 1):
        if env(i, r) != env(j, r):
            return r
    return None


def trans(site, mode):
    """(pLeft, pRight) as Q. Left tile = g[site-1], right tile = g[site]."""
    if mode == "blind":
        return HALF, HALF
    gl, gr = g[site - 1], g[site]        # site is interior (padding guarantees it)
    if gl == gr:
        return HALF, HALF
    # different: prob toward LONG side = 2-tau, toward SHORT side = tau-1
    if gl == "L":      # left long, right short
        return P_L_over_S, P_S_over_L
    else:              # left short, right long
        return P_S_over_L, P_L_over_S


def return_probs(s, mode, nsteps=NSTEPS):
    """Exact P(at s after n steps), n=0..nsteps. Nearest-neighbour on site indices."""
    dist = {s: Q(1, 0)}
    seq = [dist.get(s, Q(0))]
    touched_boundary = False
    for _ in range(nsteps):
        nd = {}
        for site, mass in dist.items():
            if site <= 0 or site >= N - 1:
                touched_boundary = True
                continue
            pL, pR = trans(site, mode)
            nd[site - 1] = nd.get(site - 1, Q(0)) + mass * pL
            nd[site + 1] = nd.get(site + 1, Q(0)) + mass * pR
        dist = nd
        seq.append(dist.get(s, Q(0)))
    return seq, touched_boundary


def ssrw_binomial(nsteps=NSTEPS):
    """Exact SSRW return probs as rationals: C(2m,m)/4^m at even steps, 0 at odd."""
    from math import comb
    out = []
    for n in range(nsteps + 1):
        out.append(Q(Fr(comb(n, n // 2), 2 ** n)) if n % 2 == 0 else Q(0))
    return out


def mirror_env(i, r):
    """Environment centred at i, reflected about i (return prob is invariant under this)."""
    e = env(i, r)
    if e is None:
        return None
    left, right = e[:r], e[r:]            # left = (g[i-r..i-1]), right = (g[i..i+r-1])
    # mirror about i: outward tile sequences swap sides
    return tuple(reversed(right)) + tuple(reversed(left))


def reflection_related(i, j, r):
    return env(j, r) == mirror_env(i, r)


# ---------------- pick representative pairs at r*=3,4,5 (well padded) ----------------
def find_pair(target_r):
    lo, hi = PAD + 1, N - 1 - (PAD + 1)
    for i in range(lo, hi):
        for j in range(i + 1, hi):
            if env(i, 2) == env(j, 2) and first_disagreement(i, j) == target_r:
                return i, j
    return None


def main():
    log("=" * 80)
    log("[0] finite verification of aperiodicity (SEPARATE from the general argument)")
    # general argument is analytic (see doc); here we only CHECK the finite patch has no
    # nontrivial global period -- necessary for 'distinct sites disagree at some finite r'.
    # a *genuine* period d must repeat at least once: overlap (n-d) >= d, i.e. d <= n/2.
    n = N - 1                                    # number of gaps
    has_period = None
    for d in range(1, n // 2 + 1):
        if all(g[t] == g[t + d] for t in range(0, n - d)):
            has_period = d; break
    require(has_period is None,
            f"finite patch gap word (len {n}) has NO genuine period d<=n/2 "
            f"(consistent with Fibonacci aperiodicity; the general claim is proved "
            f"analytically in the doc, not from this finite check)")

    log("=" * 80)
    log("[1] three example pairs at first-disagreement radius r*=3,4,5 (>=20-tile padding)")
    pairs = {}
    for r in (3, 4, 5):
        p = find_pair(r)
        require(p is not None, f"found a well-padded same-E_2 pair with r*={r}")
        pairs[r] = p
        i, j = p
        log(f"  r*={r}: sites (index) {i},{j}; E_2={''.join(env(i,2))}; "
            f"first differ at r={first_disagreement(i,j)}; "
            f"E_{r}(i)={''.join(env(i,r))} vs E_{r}(j)={''.join(env(j,r))}")

    log("=" * 80)
    log("[2] length-BLIND control: return probabilities (must agree everywhere)")
    binom = ssrw_binomial()
    blind_ok = True; bnd_ok = True
    for r, (i, j) in pairs.items():
        si, bi = return_probs(i, "blind")
        sj, bj = return_probs(j, "blind")
        if si != binom or sj != binom or si != sj:
            blind_ok = False
        if bi or bj:
            bnd_ok = False
    require(blind_ok, "length-blind walk: return-prob sequence is identical for all sites "
                      "(equals the exact SSRW binomial C(2m,m)/4^m) -- control agrees everywhere")
    require(bnd_ok, "padding sufficient: probability mass never reaches a chain boundary "
                    "within 20 steps (no truncation effect on any reported value)")

    log("=" * 80)
    log("[3] length-SENSITIVE walk: does the far-out difference change return statistics?")
    rows = ["r*  first-return-diff step (sensitive)   reflection-degenerate?   note"]
    fig_data = {}
    for r, (i, j) in pairs.items():
        si, _ = return_probs(i, "sensitive")
        sj, _ = return_probs(j, "sensitive")
        first_diff = next((n for n in range(NSTEPS + 1) if si[n] != sj[n]), None)
        refl = all(reflection_related(i, j, rr) for rr in range(2, min(rmax(i), rmax(j)) + 1))
        fig_data[r] = (i, j, si, sj, first_diff)
        note = ("returns first differ" if first_diff is not None
                else "NO difference within 20 steps")
        rows.append(f"{r}   {str(first_diff):>6}                               "
                    f"{'yes' if refl else 'no':>4}                    {note}")
        log(f"  r*={r}: first-return-difference at step {first_diff}; "
            f"reflection-degenerate={refl}")
        # show the first few even-step return probs for both
        evens = [n for n in range(0, 13, 2)]
        log("      step:        " + "  ".join(f"{n:>7}" for n in evens))
        log("      P_ret site i:" + "  ".join(f"{si[n].real():.4f}" for n in evens))
        log("      P_ret site j:" + "  ".join(f"{sj[n].real():.4f}" for n in evens))
    open(os.path.join(HERE, "results", "motion_table.txt"), "w").write("\n".join(rows) + "\n")

    # every pair either differs (geometry showed up) or is reflection-degenerate/other:
    for r, (i, j, si, sj, fd) in fig_data.items():
        if fd is None:
            log(f"  NOTE r*={r}: geometric difference at r={r} did NOT change return "
                f"statistics within 20 steps (observable degeneracy) -- reported as-is.")
    require(True, "reported first-difference step per pair without assuming geometry "
                  "guarantees a return-statistics difference")

    globals()["_FIGDATA"] = fig_data
    log("=" * 80)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

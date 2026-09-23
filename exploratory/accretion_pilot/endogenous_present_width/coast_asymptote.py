#!/usr/bin/env python3
"""
coast_asymptote.py -- Proposition 3: the archive-free coast CONVERGES, and its exact limit is
the total-variation distance between the two lineages' ABSORPTION distributions of a finite
Markov chain. Replaces the earlier "positive floor is a within-horizon observation".

Fable's observation (the key that makes this finite and exact):
  * BUD at k=1 has DeltaA = 0 (budding turns one active vertex quiet and adds one active tip),
    so the number of ACTIVE vertices is invariant along the coast. For this matched pair that
    number is 4.
  * By Proposition 1 (../endogenous_active_projection/) the BUD-only successor of a state's
    ACTIVE PROJECTION depends only on that projection -- so the archive-free coast is a
    time-homogeneous Markov chain on the FINITE set of 4-active-vertex projections (a single
    fixed kernel T, shared by both lineages -- this is exactly the kernel the data-processing
    inequality needs).
  * A finite chain has recurrent classes; here every recurrent class is an ABSORBING singleton
    (e.g. "two disjoint bonds": the budded vertex has active-degree 1, so ΔB = k - d_A = 0 and
    the projection returns to two disjoint bonds). So T is an absorbing chain.

Proposition 3. Let T be the BUD-only projection kernel on 4-active-vertex graphs (well-defined
  by Prop 1), an absorbing chain (all recurrent classes are absorbing singletons). For a start
  distribution mu over projections, mu T^t converges to the absorption distribution a(mu) over
  the absorbing states. Hence the coast TV(mu_i T^t, mu_j T^t) is non-increasing in t (a single
  fixed kernel applied to both -> data-processing inequality) and CONVERGES to
      L = TV(a(mu_i), a(mu_j)),
  which is POSITIVE iff the two absorption distributions differ. (mu_i, mu_j are the two
  lineages' erased-slice distributions at the erase horizon H=2.)

Proof: absorbing finite chain => mu T^t -> a(mu) (standard); the two lineages share T, so the
  approach is monotone by data-processing; TV of the limits telescopes over disjoint absorbing
  supports to TV(a(mu_i), a(mu_j)). QED.

This file: builds T exactly, verifies it is absorbing, cross-checks T^t against the full-graph
coast of present_width for t=0..3 (validating the Markov reduction), computes the exact limit L
as a rational, and confirms the coast decreases monotonically to L. asserts + nonzero exit.
Exact rationals throughout. Isolated in endogenous_present_width/; earlier folders untouched.
"""
from __future__ import annotations
import os, sys
from fractions import Fraction as Fr
import present_width as PW      # reuse the verified helpers + matched pair (import runs no main)

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "coast_asymptote_report.txt")
LINES, FAILS = [], []
H = 2                            # erase horizon (as in present_width Part 2)


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


# ---- a self-contained iso-class store for 4-vertex active projections ----
REPS, BUCKETS = [], {}


def cidx(P):
    h = PW.wl(P)
    for k in BUCKETS.get(h, ()):
        if PW.iso(P, REPS[k]):
            return k
    REPS.append(P); BUCKETS.setdefault(h, []).append(len(REPS) - 1)
    return len(REPS) - 1


def proj_after_bud(P, x, y):
    return cidx(PW.erase(PW.bud(P, x, y)))


# ---- exact linear solve over Fractions:  solve A X = B  (A square) ----
def solve(A, B):
    n = len(A); m = len(B[0])
    M = [[Fr(A[i][j]) for j in range(n)] + [Fr(B[i][j]) for j in range(m)] for i in range(n)]
    for col in range(n):
        piv = next((r for r in range(col, n) if M[r][col] != 0), None)
        assert piv is not None, "singular system (unexpected: chain should be absorbing)"
        M[col], M[piv] = M[piv], M[col]
        inv = Fr(1) / M[col][col]
        M[col] = [v * inv for v in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [M[r][k] - f * M[col][k] for k in range(n + m)]
    return [[M[i][n + j] for j in range(m)] for i in range(n)]


# ---- distribution over projection classes after `steps` extended events from G ----
def slice_dist_extended(G, steps):
    d = {}

    def rec(H_, prob, s):
        if s == steps:
            d[cidx(PW.erase(H_))] = d.get(cidx(PW.erase(H_)), Fr(0)) + prob
            return
        evs = PW.events_ext(H_); n = len(evs)
        if n == 0:
            d[cidx(PW.erase(H_))] = d.get(cidx(PW.erase(H_)), Fr(0)) + prob
            return
        for e in evs:
            rec(PW.apply_ev(H_, e), prob * Fr(1, n), s + 1)

    rec(G, Fr(1), 0)
    return d


def tvv(d1, d2):
    keys = set(d1) | set(d2)
    return sum(abs(d1.get(k, Fr(0)) - d2.get(k, Fr(0))) for k in keys) * Fr(1, 2)


def apply_T(vec, T):
    out = {}
    for s, p in vec.items():
        if p == 0:
            continue
        for s2, q in T[s].items():
            out[s2] = out.get(s2, Fr(0)) + p * q
    return out


def main():
    log("=" * 90)
    log("PROPOSITION 3 -- exact asymptote of the archive-free coast (absorbing projection chain)")
    log("=" * 90)
    fulls = PW.depth2_classes(); i, j = PW.find_pair(fulls); Gi, Gj = fulls[i], fulls[j]

    # active-vertex count invariance (DeltaA = 0 at k=1)
    nA = lambda G: sum(1 for n in G if G.nodes[n]["label"] == "A")
    require(nA(Gi) == 4 and nA(Gj) == 4, "both lineages have 4 active vertices")

    # start distributions mu_i, mu_j = erased slice at H=2
    mu_i = slice_dist_extended(Gi, H)
    mu_j = slice_dist_extended(Gj, H)
    require(sum(mu_i.values()) == 1 and sum(mu_j.values()) == 1, "start distributions normalise")
    # every projection in support has exactly 4 vertices (ΔA=0 through the pre-phase too)
    require(all(REPS[s].number_of_nodes() == 4 for s in set(mu_i) | set(mu_j)),
            "every projection in the H=2 support is a 4-active-vertex graph (ΔA=0)")

    # ---- build the BUD-only projection kernel T by closure over reachable states ----
    log("[1] build the finite BUD-only projection kernel T (Prop 1: depends only on projection)")
    T = {}
    frontier = list(set(mu_i) | set(mu_j))
    seen = set(frontier)
    while frontier:
        s = frontier.pop()
        P = REPS[s]
        evs = PW.events_bud(P)
        row = {}
        if not evs:
            row = {s: Fr(1)}                    # no active bond -> absorbing self-loop
        else:
            n = len(evs)
            for (_, x, y) in evs:
                s2 = proj_after_bud(P, x, y)
                row[s2] = row.get(s2, Fr(0)) + Fr(1, n)
        T[s] = row
        for s2 in row:
            if s2 not in seen:
                seen.add(s2); frontier.append(s2)
    # ensure every target has a row (absorbing leaves discovered last)
    for s in list(seen):
        if s not in T:
            P = REPS[s]; evs = PW.events_bud(P)
            if not evs:
                T[s] = {s: Fr(1)}
            else:
                n = len(evs); row = {}
                for (_, x, y) in evs:
                    s2 = proj_after_bud(P, x, y); row[s2] = row.get(s2, Fr(0)) + Fr(1, n)
                T[s] = row
    require(all(sum(r.values()) == 1 for r in T.values()),
            f"T is a stochastic kernel on {len(T)} reachable 4-vertex projections")

    # ---- absorbing states and the absorbing-chain structure ----
    absorbing = sorted(s for s in T if T[s] == {s: Fr(1)})
    transient = sorted(s for s in T if s not in absorbing)
    log(f"  reachable projections: {len(T)}; absorbing: {len(absorbing)}; "
        f"transient: {len(transient)}")
    for s in absorbing:
        P = REPS[s]
        log(f"    absorbing class {s}: {P.number_of_edges()} edges, "
            f"degree-seq {sorted(d for _, d in P.degree())}")

    # ---- absorption distribution N R via exact solve (I-Q) X = R ----
    idxT = {s: k for k, s in enumerate(transient)}
    if transient:
        A = [[(Fr(1) if a == b else Fr(0)) - T[transient[a]].get(transient[b], Fr(0))
              for b in range(len(transient))] for a in range(len(transient))]
        R = [[T[transient[a]].get(c, Fr(0)) for c in absorbing] for a in range(len(transient))]
        X = solve(A, R)                                   # X[a][c] = P(absorb in c | start a)
        require(all(sum(X[a]) == 1 for a in range(len(transient))),
                "every transient state absorbs with total probability 1 -> the ONLY recurrent "
                "classes are the absorbing singletons (no other recurrent class traps mass)")
    else:
        X = []

    def absorb_dist(mu):
        a = {c: Fr(0) for c in absorbing}
        for s, p in mu.items():
            if s in absorbing:
                a[s] += p
            else:
                for ci, c in enumerate(absorbing):
                    a[c] += p * X[idxT[s]][ci]
        return a

    a_i, a_j = absorb_dist(mu_i), absorb_dist(mu_j)
    require(sum(a_i.values()) == 1 and sum(a_j.values()) == 1, "absorption distributions normalise")
    L = tvv(a_i, a_j)

    # ---- cross-check T^t against the full-graph coast of present_width (t = 0..3) ----
    log("=" * 90)
    log("[2] cross-check: T^t on mu  ==  present_width full-graph coast  (validates Prop 1)")
    K = 3
    ef_i = PW.run_process(Gi, PW.events_ext, H, PW.events_bud, K, True)[1]
    ef_j = PW.run_process(Gj, PW.events_ext, H, PW.events_bud, K, True)[1]
    vi, vj = dict(mu_i), dict(mu_j)
    match = True
    for t in range(K + 1):
        coast_markov = tvv(vi, vj)
        coast_tree = PW.tv(ef_i[H + t], ef_j[H + t])
        log(f"  t={t}: coast(Markov)={coast_markov}  coast(tree)={coast_tree}  "
            f"({float(coast_markov):.6f})")
        if coast_markov != coast_tree:
            match = False
        vi, vj = apply_T(vi, T), apply_T(vj, T)
    require(match, "the finite projection chain reproduces the full-graph coast EXACTLY for "
                   "t=0..3 (the archive-free coast really is the Markov chain T)")

    # ---- monotone convergence to the exact limit ----
    log("=" * 90)
    log("[3] Proposition 3: convergence to the exact limit L = TV(absorption distributions)")
    vi, vj = dict(mu_i), dict(mu_j); prev = None; mono = True; above = True; seq = []
    for t in range(65):
        c = tvv(vi, vj); seq.append(c)
        if prev is not None and c > prev:
            mono = False
        if c < L:
            above = False                       # coast must never dip below its own limit
        prev = c
        vi, vj = apply_T(vi, T), apply_T(vj, T)
    require(mono, "coast TV is non-increasing in t (single fixed kernel T shared by both "
                  "lineages -> data-processing inequality; T well-defined only by Prop 1)")
    require(seq[0] == tvv(mu_i, mu_j) and seq[0] > L,
            f"coast starts at {seq[0]} ({float(seq[0]):.6f}) and exceeds the limit")
    require(above, "coast TV stays >= L at every step (L is a lower bound, approached from "
                   "above)")
    require(seq[-1] - L >= 0 and float(seq[-1] - L) < 1e-9,
            f"coast converges to the exact limit L: residual at t=64 is "
            f"{float(seq[-1]-L):.2e} (transient mass decays geometrically; the limit is L "
            f"exactly, computed from absorption, not from finite iteration)")
    require(L > 0,
            f"L > 0: the two lineages' absorption distributions DIFFER, so the coast converges "
            f"to a POSITIVE limit -- a permanent ENSEMBLE bias, not a per-world memory")
    log(f"  limiting coast  L = {L}  = {float(L):.6f}")
    log(f"  absorption distribution (lineage i): "
        f"{ {c: str(a_i[c]) for c in absorbing} }")
    log(f"  absorption distribution (lineage j): "
        f"{ {c: str(a_j[c]) for c in absorbing} }")

    log("=" * 90)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    log(f"Proposition 3 (exact): the archive-free coast converges monotonically to "
        f"L = {L} ({float(L):.4f}); the earlier 'positive floor' is this limit. It is the TV "
        f"between the two lineages' absorption distributions over the recurrent (absorbing) "
        f"projections -- a permanent bias in the ENSEMBLE of presents, positive iff those "
        f"distributions differ. One matched pair; a single fixed BUD-only projection kernel.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

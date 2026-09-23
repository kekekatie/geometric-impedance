#!/usr/bin/env python3
"""
bud_recurrent_lemma.py -- computational check of the LEMMA (see BUD_RECURRENT_LEMMA.md):

  Under BUD-only at k=1, every recurrent class of the coast chain (the BUD-only chain on
  active projections) is a SINGLETON, and that singleton is a matching plus isolated vertices.
  This holds for any seed.

Checked exhaustively on ALL graphs with n = 1..6 vertices (networkx graph atlas: 1+2+4+11+34+156
= 208 isomorphism classes, disconnected graphs included). For each n the chain is closed on the
n-vertex classes (DeltaA = 0 at k=1), so its full state space is exactly the atlas slice.

Coast step (as in ../endogenous_present_width/coast_asymptote.py): uniform over directed active
bonds (x,y); BUD(x,y) turns y quiet and adds an active tip z adjacent to x -- on the active
projection: delete y, add a new vertex z joined to x only. A graph with no edge has no event and
is an absorbing self-loop (the same convention as coast_asymptote.py).

Asserted for every n (exact Fractions, exact isomorphism; nonzero exit on any failure):
  (1) T is a stochastic kernel closed on the n-vertex classes;
  (2) Delta B = 1 - d_A(y) on every event, hence B is NON-INCREASING along every transition;
  (3) the recurrent classes (closed strongly connected components) are exactly the singletons
      {M} with T[M] = {M: 1}, M a matching plus isolated vertices -- one per matching size
      m = 0..floor(n/2);
  (4) conversely every matching-plus-isolated graph is absorbing;
  (5) from every class, absorption in some matching has total probability 1 (exact solve).
"""
from __future__ import annotations
import os, sys, collections
from fractions import Fraction as Fr
import warnings
import networkx as nx
warnings.filterwarnings("ignore", message="The hashes produced")
from networkx.generators.atlas import graph_atlas_g

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "bud_recurrent_lemma_report.txt")
LINES, FAILS = [], []
N_MAX = 6


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


def is_matching(G):
    return all(d <= 1 for _, d in G.degree())


def bud_proj(P, x, y):
    """BUD(x,y) on the active projection: y leaves (goes quiet), tip z joins x only."""
    H = P.copy(); H.remove_node(y)
    z = max(P.nodes) + 1; H.add_edge(x, z)
    return H


class Classes:
    def __init__(self, graphs):
        self.reps, self.buckets = [], {}
        for G in graphs:
            self.reps.append(nx.convert_node_labels_to_integers(G))
            self.buckets.setdefault(self._h(G), []).append(len(self.reps) - 1)

    @staticmethod
    def _h(G):
        return nx.weisfeiler_lehman_graph_hash(G, iterations=4)

    def idx(self, G):
        for k in self.buckets.get(self._h(G), ()):
            if nx.is_isomorphic(G, self.reps[k]):
                return k
        raise KeyError("successor not among the n-vertex classes (closure violated)")


def solve(A, B):
    n = len(A); m = len(B[0])
    M = [[Fr(A[i][j]) for j in range(n)] + [Fr(B[i][j]) for j in range(m)] for i in range(n)]
    for col in range(n):
        piv = next(r for r in range(col, n) if M[r][col] != 0)
        M[col], M[piv] = M[piv], M[col]
        inv = 1 / M[col][col]; M[col] = [v * inv for v in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]; M[r] = [M[r][k] - f * M[col][k] for k in range(n + m)]
    return [[M[i][n + j] for j in range(m)] for i in range(n)]


def check_n(n):
    atlas = [G for G in graph_atlas_g() if G.number_of_nodes() == n]
    C = Classes(atlas)
    T = {}; dB_ok = True
    for s, P in enumerate(C.reps):
        evs = [(u, v) for u, v in P.edges()] + [(v, u) for u, v in P.edges()]
        if not evs:
            T[s] = {s: Fr(1)}; continue
        row = collections.defaultdict(Fr)
        for x, y in evs:
            H = bud_proj(P, x, y)
            if H.number_of_edges() - P.number_of_edges() != 1 - P.degree(y):
                dB_ok = False
            row[C.idx(H)] += Fr(1, len(evs))
        T[s] = dict(row)
    require(all(sum(r.values()) == 1 for r in T.values()),
            f"n={n}: T is a stochastic kernel closed on all {len(C.reps)} n-vertex classes")
    nonincr = all(C.reps[t].number_of_edges() <= C.reps[s].number_of_edges()
                  for s in T for t in T[s])
    require(dB_ok and nonincr, f"n={n}: Delta B = 1 - d_A(y) on every event; B non-increasing "
                               f"on every transition")
    D = nx.DiGraph(); D.add_nodes_from(T)
    for s in T:
        for t in T[s]:
            D.add_edge(s, t)
    recurrent = [c for c in nx.strongly_connected_components(D)
                 if all(t in c for s in c for t in T[s])]
    singletons = all(len(c) == 1 for c in recurrent)
    absorbing = [next(iter(c)) for c in recurrent]
    matching_abs = all(T[s] == {s: Fr(1)} and is_matching(C.reps[s]) for s in absorbing)
    matchings = sorted(s for s in T if is_matching(C.reps[s]))
    require(singletons and matching_abs,
            f"n={n}: all {len(recurrent)} recurrent classes are absorbing singletons, each a "
            f"matching plus isolated vertices")
    require(sorted(absorbing) == matchings and len(matchings) == n // 2 + 1,
            f"n={n}: conversely every matching-plus-isolated graph is absorbing "
            f"({len(matchings)} = floor(n/2)+1 of them: matching sizes 0..{n // 2})")
    tr = [s for s in T if s not in absorbing]
    if tr:
        ix = {s: i for i, s in enumerate(tr)}
        A = [[(1 if a == b else 0) - T[tr[a]].get(tr[b], Fr(0)) for b in range(len(tr))]
             for a in range(len(tr))]
        R = [[T[tr[a]].get(c, Fr(0)) for c in absorbing] for a in range(len(tr))]
        X = solve(A, R)
        require(all(sum(X[a]) == 1 for a in range(len(tr))),
                f"n={n}: from every one of the {len(tr)} transient classes, absorption has total "
                f"probability 1 (exact) -- no other recurrent class traps mass, for any seed")
    return len(C.reps), len(recurrent)


def main():
    log("=" * 90)
    log("LEMMA -- BUD-only at k=1: every recurrent class of the coast chain is a singleton "
        "matching (+ isolated vertices)")
    log("=" * 90)
    tot = 0; rows = []
    for n in range(1, N_MAX + 1):
        k, r = check_n(n); tot += k; rows.append((n, k, r))
    require(tot == 208, f"exhaustive: {tot} isomorphism classes checked (all graphs, n=1..6)")
    log("  n  classes  recurrent(=absorbing matchings)")
    for n, k, r in rows:
        log(f"  {n}  {k:>7}  {r:>3}")
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

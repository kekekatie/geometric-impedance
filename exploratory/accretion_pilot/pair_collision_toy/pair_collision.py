#!/usr/bin/env python3
"""
pair_collision.py -- the pair-collision toy: two active bonds a-b, c-d and ONE quiet vertex q
adjacent to a and c only. BUD at k=1 plus CONTACT, one step = uniform selection over ALL
eligible events (the transmission-paper rule set of ../endogenous_local_contact/). Run until
FROZEN: no CONTACT eligible AND the active projection is a matching.

  Task 1  P(CONTACT ever fires) = 1/3, exactly.
  Task 2  P(end state = one pair + two loners), exactly-or-certified. (Monte Carlo had
          suggested ~0.1245, "possibly 1/8" -- NOT assumed here.)

Model (identical to ../endogenous_local_contact/local_contact_checks.py, cross-checked below):
  BUD(x,y)       directed active bond x-y; keeper x stays A, depositor y -> Q, new active tip z
                 with edges x-z, y-z.
  CONTACT(a,q,b) a,b distinct active neighbours of quiet q, edge a-b absent -> add a-b.
                 Pair unordered; distinct mediators q are distinct events.

The reduction (why this is computable at all)
  MENU MONOTONICITY. A quiet vertex never gains a neighbour (BUD attaches the new tip only to
  x and y; CONTACT adds only A-A edges), its active neighbours can only leave (A -> Q is
  one-way), and an A-A edge between two surviving actives is never removed. So the menu of q
  (non-adjacent pairs among its active neighbours) is monotone NON-INCREASING. Once empty it is
  empty forever, and q can be pruned without changing any future event count.
  ACTIVE COUNT. BUD at k=1 has DeltaA = 0 and CONTACT adds no vertex, so there are always
  exactly 4 actives.
  => REDUCED STATE = (active graph on 4 actives, multiset of active-neighbour sets S of the
     quiets whose menu is nonempty), canonical under the 24 relabellings of the actives.
     Eligible events = 2B + sum over kept quiets of |menu| -- exactly the full-graph count.
  This reduction is verified against brute-force full-graph enumeration (not just argued).

  The reduced chain is still INFINITE (menu-bearing quiets accumulate with multiplicity, and
  each copy is a separate CONTACT event), so Task 2 is solved by TRUNCATION at K kept quiets,
  with rigorous rational sub/super-solution certificates:
    lower bound: boundary states valued 0;  upper bound: boundary states valued 1.
  The gap hi - lo is exactly P(ever exceed K kept quiets), which -> 0 geometrically in K.

Exact Fractions for every reported number; floats only propose candidate vectors, and each
candidate is then CHECKED row by row in exact rational arithmetic. asserts + nonzero exit.
"""
from __future__ import annotations
import os, sys, itertools, collections, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "pair_collision_report.txt")
LINES, FAILS = [], []
K_TRUNC = 12                      # truncation: max number of kept (menu-bearing) quiet vertices


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg, flush=True)
    if not cond:
        FAILS.append(msg)


# ============================================================ full labelled graph model
# state = (labels: dict v->'A'/'Q', adj: dict v->set). Vertex ids are ints; new tip = max+1.
A_, B_, C_, D_, Q_ = 0, 1, 2, 3, 4


def start_full():
    labels = {A_: "A", B_: "A", C_: "A", D_: "A", Q_: "Q"}
    adj = {v: set() for v in labels}
    for u, v in ((A_, B_), (C_, D_), (Q_, A_), (Q_, C_)):
        adj[u].add(v); adj[v].add(u)
    return labels, adj


def actives(G):
    return sorted(v for v, l in G[0].items() if l == "A")


def active_edges(G):
    lab, adj = G
    return sorted((u, v) for u in adj for v in adj[u] if u < v and lab[u] == "A" and lab[v] == "A")


def menu_full(G, q):
    lab, adj = G
    an = sorted(a for a in adj[q] if lab[a] == "A")
    return [(a, b) for a, b in itertools.combinations(an, 2) if b not in adj[a]]


def events_full(G):
    lab, adj = G
    evs = []
    for u, v in active_edges(G):
        evs.append(("B", u, v)); evs.append(("B", v, u))
    for q in sorted(v for v in lab if lab[v] == "Q"):
        for a, b in menu_full(G, q):
            evs.append(("C", (a, b), q))
    return evs


def apply_full(G, ev):
    lab, adj = dict(G[0]), {v: set(s) for v, s in G[1].items()}
    if ev[0] == "B":
        _, x, y = ev
        assert lab[x] == "A" and lab[y] == "A" and y in adj[x]
        lab[y] = "Q"; z = max(lab) + 1; lab[z] = "A"; adj[z] = {x, y}
        adj[x].add(z); adj[y].add(z)
    else:
        (a, b), q = ev[1], ev[2]
        assert lab[a] == "A" and lab[b] == "A" and lab[q] == "Q" and b not in adj[a]
        adj[a].add(b); adj[b].add(a)
    return lab, adj


def is_matching_full(G):
    lab, adj = G
    return all(sum(1 for w in adj[v] if lab[w] == "A") <= 1 for v in lab if lab[v] == "A")


def contact_eligible_full(G):
    return any(e[0] == "C" for e in events_full(G))


def frozen_full(G):
    return (not contact_eligible_full(G)) and is_matching_full(G)


def key_full(G):
    lab, adj = G
    return (tuple(sorted(lab.items())),
            tuple(sorted((u, v) for u in adj for v in adj[u] if u < v)))


# ============================================================ reduced chain
PERMS = list(itertools.permutations(range(4)))


def canon(E, Qs):
    best = None
    for p in PERMS:
        e = tuple(sorted(tuple(sorted((p[u], p[v]))) for u, v in E))
        q = tuple(sorted(tuple(sorted(p[x] for x in S)) for S in Qs))
        if best is None or (e, q) < best:
            best = (e, q)
    return best


def menu_red(S, E):
    return [(a, b) for a, b in itertools.combinations(sorted(S), 2) if (a, b) not in E]


def prune(Qs, E):
    return [S for S in Qs if menu_red(S, E)]


def reduce_full(G):
    """full labelled graph -> canonical reduced state (menu-empty quiets pruned)."""
    lab, adj = G
    act = actives(G); assert len(act) == 4, "DeltaA = 0: always exactly 4 actives"
    idx = {v: i for i, v in enumerate(act)}
    E = {tuple(sorted((idx[u], idx[v]))) for u, v in active_edges(G)}
    Qs = [frozenset(idx[a] for a in adj[q] if lab[a] == "A")
          for q in lab if lab[q] == "Q"]
    return canon(E, prune(Qs, E))


def succ_red(state):
    """list of successor reduced states, one entry per eligible event (multiplicity kept)."""
    E, Qs = state
    E = set(E); Qs = [frozenset(S) for S in Qs]
    out = []
    for u, v in sorted(E):
        for x, y in ((u, v), (v, u)):                      # BUD(x,y): y -> Q, tip z in y's slot
            NA = [w for w in range(4) if w != y and tuple(sorted((w, y))) in E]
            Sy = frozenset(NA + [y])                       # y's active nbrs + the new tip z
            newQs = [S - {y} for S in Qs] + [Sy]
            E2 = {e for e in E if y not in e} | {tuple(sorted((x, y)))}
            out.append(canon(E2, prune(newQs, E2)))
    for S in Qs:
        for a, b in menu_red(S, E):
            E2 = E | {(a, b)}
            out.append(canon(E2, prune(Qs, E2)))
    return out


def n_events_red(state):
    E, Qs = state
    return 2 * len(E) + sum(len(menu_red(S, set(E))) for S in Qs)


def frozen_red(s):
    E, Qs = s
    return len(Qs) == 0 and all(sum(1 for e in E if v in e) <= 1 for v in range(4))


def one_pair(s):
    return frozen_red(s) and len(s[0]) == 1


def two_pairs(s):
    return frozen_red(s) and len(s[0]) == 2


START_RED = reduce_full(start_full())


# ============================================================ Task 1
def task1():
    log("=" * 90)
    log("TASK 1 -- P(CONTACT ever fires) = 1/3 exactly")
    log("=" * 90)
    G0 = start_full()
    evs = events_full(G0)
    require(len(evs) == 5, f"start state has exactly 5 eligible events: {evs}")
    contact = [e for e in evs if e[0] == "C"]
    neutral, kill = [], []
    for e in evs:
        if e[0] != "B":
            continue
        H = apply_full(G0, e)
        if reduce_full(H) == START_RED:
            neutral.append(e)
        elif not contact_eligible_full(H) and frozen_full(H):
            kill.append(e)
    require(len(contact) == 1 and contact[0][1] == (A_, C_) and contact[0][2] == Q_,
            "exactly 1 CONTACT event: CONTACT(a,q,c)")
    require(sorted(neutral) == [("B", A_, B_), ("B", C_, D_)],
            "2 NEUTRAL events BUD(a,b), BUD(c,d): keeper a/c stays active; the depositor's own "
            "menu {keeper, tip} is an adjacent pair -> empty; reduced state returns to START")
    require(sorted(kill) == [("B", B_, A_), ("B", D_, C_)],
            "2 KILL events BUD(b,a), BUD(d,c): a or c goes quiet, q keeps <=1 active nbr -> "
            "menu empty forever; result is FROZEN (two disjoint pairs, no CONTACT eligible)")
    # after a kill: no CONTACT can EVER fire (matching + no menus is closed under BUD)
    closed = True
    for e in kill:
        H = apply_full(G0, e)
        frontier = [H]
        for _ in range(4):
            nxt = []
            for G in frontier:
                for ev in events_full(G):
                    if ev[0] == "C":
                        closed = False
                    nxt.append(apply_full(G, ev))
            frontier = nxt
    require(closed, "after a kill, no CONTACT is eligible in any state reachable in <=4 further "
                    "events (and structurally never: BUD on a matching edge deposits a vertex "
                    "whose menu is {keeper,tip}, adjacent)")
    # exact first-step analysis on the reduced chain: p = 1/5 + 2/5 p
    succ = collections.Counter(succ_red(START_RED))
    n = sum(succ.values())
    p_stay = Fr(succ[START_RED], n)
    p_contact = Fr(1, n)
    p = p_contact / (1 - p_stay)
    log(f"  reduced-chain first step: P(CONTACT)={p_contact}, P(neutral)={p_stay}, "
        f"P(kill)={1 - p_contact - p_stay}")
    require(p == Fr(1, 3), f"P(CONTACT ever fires) = (1/5)/(1 - 2/5) = {p}  (exact)")
    # brute-force full-graph cross-check: P(CONTACT by step t) = (1/3)(1-(2/5)^t)
    ok = True
    dist = {key_full(G0): (G0, Fr(1))}
    hit = Fr(0)
    for t in range(1, 7):
        nd = {}
        for G, pr in dist.values():
            if frozen_full(G):
                continue
            evs = events_full(G)
            for e in evs:
                q = pr / len(evs)
                if e[0] == "C":
                    hit += q
                else:
                    H = apply_full(G, e); k = key_full(H)
                    nd[k] = (H, nd[k][1] + q) if k in nd else (H, q)
        dist = nd
        want = Fr(1, 3) * (1 - Fr(2, 5) ** t)
        ok &= (hit == want)
        log(f"    full graph, t={t}: P(CONTACT fired by t) = {hit}  (formula {want})")
    require(ok, "brute-force full-graph enumeration matches (1/3)(1-(2/5)^t) exactly for t=1..6")
    return p


# ============================================================ reduction validation
def validate_reduction(T_MAX=5):
    log("=" * 90)
    log(f"REDUCTION CHECK -- reduced chain == brute-force full-graph dynamics (t <= {T_MAX})")
    log("=" * 90)
    # (a) the full model reproduces the reference implementation of the transmission paper
    sys.path.insert(0, os.path.join(HERE, "..", "endogenous_local_contact"))
    try:
        import networkx as nx
        import local_contact_checks as REF
        have_ref = True
    except Exception as ex:                                   # pragma: no cover
        have_ref = False; log(f"  (reference implementation unavailable: {ex})")
    require(have_ref, "reference implementation ../endogenous_local_contact importable")

    def to_nx(G):
        H = nx.Graph()
        for v, l in G[0].items():
            H.add_node(v, label=l)
        for u in G[1]:
            for v in G[1][u]:
                H.add_edge(u, v)
        return H

    ref_ok = True
    frontier = [start_full()]
    for depth in range(3):
        nxt = []
        for G in frontier:
            mine = events_full(G); R = to_nx(G); theirs = REF.events_ext(R)
            if len(mine) != len(theirs):
                ref_ok = False
            a = [to_nx(apply_full(G, e)) for e in mine]
            b = [REF.apply_ev(R, e) for e in theirs]
            used = [False] * len(b)
            for X in a:                                        # successor multisets iso-equal
                j = next((j for j in range(len(b)) if not used[j] and REF.iso(X, b[j])), None)
                if j is None:
                    ref_ok = False
                else:
                    used[j] = True
            nxt.extend(apply_full(G, e) for e in mine)
        frontier = nxt
    require(ref_ok, "full-graph model == ../endogenous_local_contact rule set (same event counts, "
                    "same successor multisets up to labelled isomorphism) on all states reachable "
                    "in <=2 events (3 levels of states)")

    # (b) exact t-step distributions: full graph (brute force) vs reduced chain
    full = {key_full(start_full()): (start_full(), Fr(1))}
    red = {START_RED: Fr(1)}
    mono_ok = count_ok = True
    for t in range(T_MAX + 1):
        agg = collections.defaultdict(Fr)
        for G, pr in full.values():
            agg[reduce_full(G)] += pr
            if n_events_red(reduce_full(G)) != len(events_full(G)):
                count_ok = False
        eq = (dict(agg) == {k: v for k, v in red.items() if v})
        require(eq, f"t={t}: reduced-state distribution identical (full: {len(full)} labelled "
                    f"states -> {len(agg)} reduced)")
        if t == T_MAX:
            break
        nf = {}
        for G, pr in full.values():
            if frozen_full(G):
                k = key_full(G); nf[k] = (G, nf[k][1] + pr) if k in nf else (G, pr)
                continue
            evs = events_full(G)
            for e in evs:
                H = apply_full(G, e)
                for q in (v for v in G[0] if G[0][v] == "Q"):   # menu monotonicity, per quiet
                    if G[1][q] != H[1][q] or not set(menu_full(H, q)) <= set(menu_full(G, q)):
                        mono_ok = False
                k = key_full(H)
                nf[k] = (H, nf[k][1] + pr / len(evs)) if k in nf else (H, pr / len(evs))
        full = nf
        nr = collections.defaultdict(Fr)
        for s, pr in red.items():
            if frozen_red(s):
                nr[s] += pr; continue
            ss = succ_red(s)
            for s2 in ss:
                nr[s2] += pr / len(ss)
        red = nr
    require(count_ok, "every full state's eligible-event count == 2B + sum |menu| of kept quiets "
                      "(pruning menu-empty quiets loses no event)")
    require(mono_ok, "MENU MONOTONICITY on every enumerated transition: a quiet's neighbourhood "
                     "never changes and its menu only shrinks")


# ============================================================ Task 2: truncated chain + certificates
def build_truncated(K):
    """closure from START over states with <= K kept quiets; states with > K are BOUNDARY."""
    T, seen, st = {}, {START_RED}, [START_RED]
    while st:
        s = st.pop()
        if frozen_red(s) or len(s[1]) > K:
            continue
        T[s] = collections.Counter(succ_red(s))
        for s2 in T[s]:
            if s2 not in seen:
                seen.add(s2); st.append(s2)
    frozen = [s for s in seen if frozen_red(s)]
    boundary = [s for s in seen if s not in T and not frozen_red(s)]
    return T, frozen, boundary


def certified_bounds(T, frozen, boundary):
    """Return exact rationals (lo, hi) with lo <= P_true(one pair) <= hi, CERTIFIED.

    Transient set = T's keys. For boundary value beta in {0,1}:  V = P V + b_beta.
    Claim: I-P (on transient states) is a nonsingular M-matrix, so (I-P)^{-1} >= 0 and
      (I-P) l <= b_0  =>  l <= V_0 <= V_true,     (I-P) u >= b_1  =>  u >= V_1 >= V_true.
    Nonsingularity: every transient state reaches a non-transient state (checked by search).
    """
    import numpy as np
    from scipy.sparse import lil_matrix
    from scipy.sparse.linalg import spsolve
    tr = list(T); ix = {s: i for i, s in enumerate(tr)}; n = len(tr)
    # every transient state can leave the transient set (=> spectral radius of P_TT < 1)
    rev = collections.defaultdict(list)
    for s, c in T.items():
        for s2 in c:
            rev[s2].append(s)
    good, st = set(frozen) | set(boundary), list(set(frozen) | set(boundary))
    while st:
        x = st.pop()
        for y in rev[x]:
            if y not in good:
                good.add(y); st.append(y)
    require(all(s in good for s in tr),
            "every transient state can reach a frozen/boundary state -> I-P is a nonsingular "
            "M-matrix -> sub/super-solutions bound the true value")
    tgt = set(s for s in frozen if one_pair(s)); bnd = set(boundary)
    rows = {}
    for s, c in T.items():
        tot = sum(c.values())
        rows[s] = [(s2, Fr(m, tot)) for s2, m in c.items()]
    M = lil_matrix((n, n)); b0 = np.zeros(n); b1 = np.zeros(n)
    for s, row in rows.items():
        i = ix[s]; M[i, i] += 1.0
        for s2, pr in row:
            if s2 in ix:
                M[i, ix[s2]] -= float(pr)
            else:
                b0[i] += float(pr) if s2 in tgt else 0.0
                b1[i] += float(pr) if (s2 in tgt or s2 in bnd) else 0.0
    M = M.tocsc()
    x0 = spsolve(M, b0); x1 = spsolve(M, b1); tau = spsolve(M, np.ones(n))   # tau: E[steps]

    def check(vec, beta, sign):
        """exact: sign*((I-P)vec - b_beta) >= 0 on every transient row."""
        for s, row in rows.items():
            lhs = vec[ix[s]]
            for s2, pr in row:
                if s2 in ix:
                    lhs -= pr * vec[ix[s2]]
                elif s2 in tgt or (beta == 1 and s2 in bnd):
                    lhs -= pr
            if sign * lhs < 0:
                return False
        return True

    Ftau = [Fr(float(t)) for t in tau]
    lo = hi = None
    for e in range(15, 3, -1):                                 # smallest slack that certifies
        d = Fr(1, 10 ** e)
        if lo is None:
            l = [Fr(float(v)) - d * t for v, t in zip(x0, Ftau)]
            if check(l, 0, -1):
                lo = l[ix[START_RED]]
        if hi is None:
            u = [Fr(float(v)) + d * t for v, t in zip(x1, Ftau)]
            if check(u, 1, +1):
                hi = u[ix[START_RED]]
        if lo is not None and hi is not None:
            break
    require(lo is not None and hi is not None,
            "exact rational sub-solution and super-solution found and verified row by row")
    return lo, hi, float(x0[ix[START_RED]]), float(x1[ix[START_RED]]), float(tau[ix[START_RED]])


def simplest_rational_in(lo, hi):
    """the rational with the smallest denominator in the closed interval [lo, hi] (lo < hi)."""
    q = 1
    while True:
        p = -(-lo.numerator * q // lo.denominator)             # ceil(lo*q)
        if Fr(p, q) <= hi:
            return Fr(p, q)
        q += 1


def task2():
    log("=" * 90)
    log("TASK 2 -- P(frozen end state = one pair + two loners)")
    log("=" * 90)
    log("  end states: every BUD leaves the active edge keeper-tip, so B >= 1 after any event;")
    log("  4 actives => a frozen matching is ONE pair + two loners (B=1) or TWO pairs (B=2).")
    table = []
    lo = hi = None
    for K in range(1, K_TRUNC + 1):
        t0 = time.time()
        T, frozen, boundary = build_truncated(K)
        require(all(one_pair(s) or two_pairs(s) for s in frozen),
                f"K={K}: every reachable frozen state is one-pair or two-pairs")
        lo, hi, flo, fhi, tau = certified_bounds(T, frozen, boundary)
        table.append((K, len(T) + len(frozen) + len(boundary), lo, hi))
        log(f"  K={K:>2}  states={len(T) + len(frozen) + len(boundary):>6}  "
            f"certified [{float(lo):.15f}, {float(hi):.15f}]  width={float(hi - lo):.2e}  "
            f"E[events]~{tau:.3f}  ({time.time() - t0:.1f}s)")
        if len(table) > 1:
            require(table[-2][2] <= lo + Fr(1, 10 ** 13) and hi <= table[-2][3] + Fr(1, 10 ** 13),
                    f"K={K}: interval nested in K={K - 1}'s (up to certificate slack)")
    require(hi - lo < Fr(1, 10 ** 12), f"final certified width {float(hi - lo):.2e} < 1e-12")
    require(not (lo <= Fr(1, 8) <= hi) and hi < Fr(1, 8),
            "1/8 is EXCLUDED: the certified upper bound is below 1/8")
    s = simplest_rational_in(lo, hi) if hi - lo < Fr(1, 10 ** 6) else None
    log(f"  certified:  {lo}")
    log(f"          <= P(one pair + two loners) <=")
    log(f"              {hi}")
    log(f"  decimal:    {float(lo):.15f} <= P <= {float(hi):.15f}")
    log(f"  conditional on the collision: P(one pair | CONTACT fired) in "
        f"[{float(3 * lo):.15f}, {float(3 * hi):.15f}]")
    if s is not None:
        log(f"  smallest-denominator rational in the interval: {s} "
            f"(so if P is rational its denominator is >= {s.denominator})")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    with open(os.path.join(HERE, "results", "certified_intervals.txt"), "w") as f:
        f.write("K\tstates\tlower\tupper\twidth\tlower_exact\tupper_exact\n")
        for K, n, l, h in table:
            f.write(f"{K}\t{n}\t{float(l):.17f}\t{float(h):.17f}\t{float(h - l):.3e}\t{l}\t{h}\n")
    return lo, hi, s


def main():
    p = task1()
    validate_reduction()
    lo, hi, s = task2()
    log("=" * 90)
    log(f"SUMMARY  P(CONTACT ever fires) = {p}")
    log(f"         P(one pair + two loners) in [{float(lo):.15f}, {float(hi):.15f}]  (certified; "
        f"!= 1/8)")
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
graft_experiment.py -- the bounded GRAFT experiment (frozen spec, exact enumeration).

Register: speculative exploration. A *mechanism test*, not a representative sample of
growing worlds. Isolated under exploratory/accretion_pilot/endogenous_graft_experiment/;
earlier work preserved. No merges/publishing/sealed-study access. No weighting sweep, no
additional seeds, no automatic extension. Exact rational path probabilities; asserts +
nonzero exit (printed text is not a gate).

------------------------------------------------------------------------------------------
FROZEN SPECIFICATION (fixed BEFORE any probability is computed)
------------------------------------------------------------------------------------------
Rules (as defined in the prior folders, unchanged):
  * BUD(x,y) at k=1 -- DIRECTED active bond. Requires an active-active edge x-y. Effect:
    y -> Q, create one fresh active tip z with edges x-z and y-z. Directed: (x,y) and (y,x)
    are distinct events.
  * CONTACT(a,q,b) -- a,b DISTINCT active neighbours of a quiet q with the active edge a-b
    ABSENT. Effect: add only a-b. Endpoint pair {a,b} UNORDERED. DISTINCT quiet mediators q
    are DISTINCT events (even if they would add the same edge).
  * GRAFT(q,a,w) -- q:Q, a:A adjacent to q, w:A adjacent to a, edge q-w ABSENT, w != q.
    Effect: add only q-w. DISTINCT bridges a for the same (q,w) are DISTINCT events.

Scheduler: one step = UNIFORM selection among INDIVIDUAL eligible events (NOT uniform among
  the three rule families). Each individual eligible event carries weight 1. This relative
  weighting is a modelling assumption, stated as such.
Control: BUD + CONTACT, with GRAFT absent (same uniform-over-individual-events scheduler).

Horizon: report cumulative outcomes after 0,1,2,3,4 events. Exact enumeration of the full
  path tree (no state merging -- so the designated q and all eligibility history are trivially
  preserved). A node-visit guard reports completed horizons if a resource limit is hit; we do
  NOT substitute sampling or pick the horizon by outcome.

Seed (frozen): all-active seed A0 = the path  y - x - q0  on vertices {2,0,1} (2=y,0=x,1=q0),
  edges 0-1, 0-2, all labelled A. Apply the single BUD(x=0, q0=1): vertex 1 -> Q, fresh tip
  3 (A) with edges 0-3, 1-3. The resulting state S is the frozen seed:
      nodes: 0:A, 1:Q, 2:A, 3:A ;  edges: 0-1, 0-2, 0-3, 1-3.
  DESIGNATED quiet trace: q = vertex 1. Its active neighbours are {0,3}; edge 0-3 is present,
  so C_q(S) = {} (EMPTY menu -- no delayed-consultation opportunities exist by construction).
  Active neighbour 0 can bud further (active edges 0-2, 0-3), so a wedge can form. This is a
  deliberately selected mechanism test.

------------------------------------------------------------------------------------------
OUTCOMES (about the DESIGNATED q = 1 only; cumulative = "has occurred by step t")
------------------------------------------------------------------------------------------
  O1  q gains a CONTACT pair it has NEVER previously had (a "newly enabled" eligibility).
      Because C_q starts empty and, once a pair leaves the menu it can never return (edges are
      never deleted; labels never go Q->A), every pair that ever appears at q is newly enabled
      the one time it appears. Kept DISTINCT from:
  O0  q merely gains a new active NEIGHBOUR (a GRAFT adding q-w) -- which need not create a
      new pair.
  O2  a subsequently selected CONTACT THROUGH THIS SAME q consumes such a newly-enabled pair
      (renew-then-consult).
  Also reported separately: the distribution of the current menu size |C_q| at each horizon
      (a menu can gain a new pair even if its total size does not increase).
Control must give O0=O1=O2=0 at every horizon (the menu-monotonicity theorem); asserted.
"""
from __future__ import annotations
import os, sys, itertools
from collections import defaultdict
from fractions import Fraction as Fr
import networkx as nx
from networkx.algorithms.isomorphism import categorical_node_match

NM = categorical_node_match("label", None)
HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "graft_report.txt")
TABLE = os.path.join(HERE, "results", "outcome_tables.txt")
LINES, FAILS = [], []
HORIZON = 4
NODE_GUARD = 4_000_000            # abort enumeration if exceeded; report completed horizons


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


# ----------------------------------------------------------------- graph helpers / rules
def _fresh(G):
    return max([n for n in G.nodes if isinstance(n, int)] + [-1]) + 1


def bud(G, x, y):
    assert G.has_edge(x, y) and G.nodes[x]["label"] == "A" and G.nodes[y]["label"] == "A"
    H = G.copy(); H.nodes[y]["label"] = "Q"
    z = _fresh(H); H.add_node(z, label="A"); H.add_edge(x, z); H.add_edge(y, z)
    return H


def active_bonds(G):
    return [(u, v) for u, v in G.edges()
            if G.nodes[u]["label"] == "A" and G.nodes[v]["label"] == "A"]


def active_neighbours(G, q):
    return sorted(a for a in G.neighbors(q) if G.nodes[a]["label"] == "A")


def C_q(G, q):
    """CONTACT menu at quiet q: unordered active-neighbour pairs with the edge absent."""
    an = active_neighbours(G, q)
    return {frozenset((a, b)) for a, b in itertools.combinations(an, 2)
            if not G.has_edge(a, b)}


# ---- individual eligible events --------------------------------------------------------
def events_bud(G):
    out = []
    for u, v in active_bonds(G):
        out.append(("B", u, v)); out.append(("B", v, u))     # directed
    return out


def events_contact(G):
    out = []
    for q in [n for n in G if G.nodes[n]["label"] == "Q"]:
        an = active_neighbours(G, q)
        for a, b in itertools.combinations(an, 2):           # unordered pair
            if not G.has_edge(a, b):
                out.append(("C", frozenset((a, b)), q))       # distinct mediators distinct
    return out


def events_graft(G):
    out = []
    for q in [n for n in G if G.nodes[n]["label"] == "Q"]:
        for a in active_neighbours(G, q):
            for w in active_neighbours(G, a):
                if w != q and not G.has_edge(q, w):
                    out.append(("G", q, a, w))                # distinct bridges distinct
    return out


def events_control(G):                # BUD + CONTACT  (GRAFT absent)
    return events_bud(G) + events_contact(G)


def events_extended(G):               # BUD + CONTACT + GRAFT
    return events_bud(G) + events_contact(G) + events_graft(G)


def apply_ev(G, ev):
    if ev[0] == "B":
        return bud(G, ev[1], ev[2])
    if ev[0] == "C":
        a, b = tuple(ev[1]); H = G.copy(); H.add_edge(a, b); return H
    if ev[0] == "G":
        _, q, a, w = ev; H = G.copy(); H.add_edge(q, w); return H
    raise ValueError(ev)


# --------------------------------------------------------------------- the frozen seed
def all_active_seed():
    A0 = nx.Graph()
    for n in (0, 1, 2):
        A0.add_node(n, label="A")
    A0.add_edges_from([(0, 1), (0, 2)])       # path  y(2) - x(0) - q0(1)
    return A0


def frozen_seed():
    return bud(all_active_seed(), 0, 1)        # BUD(x=0, q0=1)


QID = 1                                         # designated quiet trace


# ------------------------------------------------------ exact cumulative enumeration
def enumerate_process(seed, evfn, qid, horizon=HORIZON, guard=NODE_GUARD):
    """Full path-tree enumeration with exact rational probabilities. Tracks, per path:
       seen  = set of pairs ever present in C_q ; ne = pairs ever newly-enabled at q ;
       flags o0 (q gained a new neighbour), o1 (q gained a never-before pair),
       o2 (a CONTACT via q consumed a newly-enabled pair). Returns aggregate dicts and a
       'completed' horizon (== horizon unless the node guard tripped)."""
    agg = {d: {"o0": Fr(0), "o1": Fr(0), "o2": Fr(0), "total": Fr(0),
               "menu": defaultdict(lambda: Fr(0))} for d in range(horizon + 1)}
    visits = [0]
    aborted = [False]

    def record(d, prob, o0, o1, o2, menusz):
        a = agg[d]
        a["total"] += prob
        if o0: a["o0"] += prob
        if o1: a["o1"] += prob
        if o2: a["o2"] += prob
        a["menu"][menusz] += prob

    def rec(G, prob, seen, ne, o0, o1, o2, d):
        if aborted[0]:
            return
        visits[0] += 1
        if visits[0] > guard:
            aborted[0] = True; return
        record(d, prob, o0, o1, o2, len(C_q(G, qid)))
        if d == horizon:
            return
        evs = evfn(G); n = len(evs)
        if n == 0:                                   # halted path: carry flags forward
            for dd in range(d + 1, horizon + 1):
                record(dd, prob, o0, o1, o2, len(C_q(G, qid)))
            return
        step = Fr(1, n)
        for e in evs:
            # o2 is decided on the PRE-event state/event (a CONTACT via q consuming ne pair)
            no2 = o2 or (e[0] == "C" and e[2] == qid and e[1] in ne)
            no0 = o0 or (e[0] == "G" and e[1] == qid)
            G2 = apply_ev(G, e)
            cq2 = C_q(G2, qid)
            new = cq2 - seen
            no1 = o1 or (len(new) > 0)
            rec(G2, prob * step, seen | cq2, ne | new, no0, no1, no2, d + 1)

    seen0 = set(C_q(seed, qid))
    rec(seed, Fr(1), seen0, set(), False, False, False, 0)
    completed = horizon if not aborted[0] else (
        max(d for d in range(horizon + 1) if agg[d]["total"] == 1))
    return agg, completed, visits[0], aborted[0]


# ----------------------------------------------------------------- invariants / hygiene
def invariants_ok(G):
    return (not any(True for _ in nx.selfloop_edges(G))
            and all(G.nodes[n]["label"] in ("A", "Q") for n in G)
            and nx.is_connected(G))


def q_incident(G, qonly=None):
    """(Q-labels ; set of Q-incident edges) under the identity vertex correspondence."""
    qs = [n for n in G if G.nodes[n]["label"] == "Q"] if qonly is None else [qonly]
    labels = {n: "Q" for n in qs}
    edges = frozenset(frozenset((u, v)) for u, v in G.edges()
                      if (G.nodes[u]["label"] == "Q" or G.nodes[v]["label"] == "Q"))
    return labels, edges


def check_transition_invariants(seed, evfn, depth=HORIZON):
    """Walk every reachable state up to `depth` events; check per-rule preservation and
    global graph invariants. Uses subgraph (NOT induced-subgraph) embedding for GRAFT."""
    ok = {"inv": True, "graft": True, "contact": True, "bud": True}
    seen_states = 0

    def walk(G, d):
        nonlocal seen_states
        seen_states += 1
        if d == depth:
            return
        for e in evfn(G):
            H = apply_ev(G, e)
            if not invariants_ok(H):
                ok["inv"] = False
            if e[0] == "G":
                _, q, a, w = e
                # GRAFT: labels, vertices, ALL existing edges preserved; exactly one new edge
                # q-w, previously absent, incident to the quiet q and an active w (a Q-A edge).
                labels_same = all(H.nodes[n]["label"] == G.nodes[n]["label"] for n in G)
                verts_same = (set(H.nodes) == set(G.nodes))
                edges_kept = all(H.has_edge(u, v) for u, v in G.edges())   # SUBGRAPH embed
                added = set(map(frozenset, H.edges())) - set(map(frozenset, G.edges()))
                one_new = (added == {frozenset((q, w))}) and not G.has_edge(q, w)
                qa_edge = (G.nodes[q]["label"] == "Q" and G.nodes[w]["label"] == "A")
                if not (labels_same and verts_same and edges_kept and one_new and qa_edge):
                    ok["graft"] = False
            elif e[0] == "C":
                # CONTACT: Q labels and Q-incident edges preserved EXACTLY (identity map)
                if q_incident(G) != q_incident(H):
                    ok["contact"] = False
                a, b = tuple(e[1])
                added = set(map(frozenset, H.edges())) - set(map(frozenset, G.edges()))
                if added != {frozenset((a, b))} or H.number_of_nodes() != G.number_of_nodes():
                    ok["contact"] = False
            else:  # BUD
                if not (H.number_of_nodes() == G.number_of_nodes() + 1):
                    ok["bud"] = False
            walk(H, d + 1)

    walk(seed, 0)
    return ok, seen_states


# ----------------------------------------------------------------- relabelling invariance
def relabel(G, shift):
    return nx.relabel_nodes(G, {n: (n + shift if isinstance(n, int) else n) for n in G})


# ----------------------------------------------------------------- formatting
def fmt_menu(md):
    return "{" + ", ".join(f"{k}:{md[k]}" for k in sorted(md)) + "}"


def pct(fr):
    return f"{float(fr)*100:6.2f}%"


# ============================================================================= MAIN
def main():
    log("=" * 88)
    log("BOUNDED GRAFT EXPERIMENT  (exact; frozen spec; mechanism test, not a sample)")
    log("=" * 88)

    # ---- [0] seed construction + BUD-only history from an all-active seed ----
    log("[0] frozen seed S and a legal BUD-only history producing it from all-active A0")
    A0 = all_active_seed()
    S = frozen_seed()
    log(f"  A0 (all active): nodes {dict(A0.nodes(data='label'))}  "
        f"edges {sorted(map(tuple,(frozenset(e) for e in A0.edges())))}")
    log(f"  history: BUD(x=0, q0=1)  ->  vertex 1 becomes Q; fresh active tip 3 (edges 0-3,1-3)")
    log(f"  S (seed): nodes {dict(S.nodes(data='label'))}  "
        f"edges {sorted(map(tuple,(frozenset(e) for e in S.edges())))}")
    log(f"  designated quiet trace q = {QID}; active neighbours {active_neighbours(S,QID)}; "
        f"C_q(S) = {sorted(map(tuple, C_q(S,QID)))}")
    require(all(d == "A" for _, d in A0.nodes(data="label")), "A0 is all-active")
    require(nx.is_isomorphic(bud(A0, 0, 1), S, node_match=NM),
            "S is produced from the all-active seed by the single legal BUD(0,1)")
    require(S.nodes[QID]["label"] == "Q", "designated q is quiet in the seed")
    require(C_q(S, QID) == set(), "seed menu C_q(S) is EMPTY (no delayed-consultation pairs)")
    require(len(active_neighbours(S, QID)) == 2 and
            any(active_bonds(S)), "q has active neighbours and the seed can bud further")

    # ---- [1] eligible events at the seed (both schedulers) ----
    log("=" * 88)
    log("[1] individual eligible events at the seed")
    log(f"  BUD (directed):   {events_bud(S)}")
    log(f"  CONTACT:          {events_contact(S)}")
    log(f"  GRAFT:            {events_graft(S)}")
    require(events_contact(S) == [], "no CONTACT eligible at the seed (empty menu everywhere "
                                     "relevant to q)")
    require(("G", 1, 0, 2) in events_graft(S),
            "GRAFT(q=1, bridge=0, w=2) is eligible at the seed (bounded wedge 2-0-1)")

    # ---- [2] invariants + per-rule preservation over the reachable-in-<=HORIZON set ----
    log("=" * 88)
    log(f"[2] invariants & per-rule preservation over every state reachable in <= {HORIZON} "
        f"extended events")
    ok, nstates = check_transition_invariants(S, events_extended, depth=HORIZON)
    log(f"  visited {nstates} reachable states")
    require(ok["inv"], "every reachable state is a simple, connected, A/Q-labelled graph")
    require(ok["bud"], "every BUD adds exactly one vertex")
    require(ok["contact"], "every CONTACT preserves Q labels and Q-incident edges EXACTLY "
                           "and adds exactly one A-A edge (no vertex, no label change)")
    require(ok["graft"], "every GRAFT preserves all labels, all vertices and all existing "
                         "edges (SUBGRAPH embedding, not induced) and adds exactly one "
                         "previously-absent Q-A edge q-w")

    # ---- [3] the experiment: exact cumulative outcome probabilities, extended vs control --
    log("=" * 88)
    log("[3] exact cumulative outcome probabilities by horizon (extended vs control)")
    ext, ext_done, ext_vis, ext_ab = enumerate_process(S, events_extended, QID)
    ctl, ctl_done, ctl_vis, ctl_ab = enumerate_process(S, events_control, QID)
    log(f"  extended: enumerated full tree to horizon {ext_done} "
        f"({ext_vis} node-visits{', GUARD TRIPPED' if ext_ab else ''})")
    log(f"  control : enumerated full tree to horizon {ctl_done} "
        f"({ctl_vis} node-visits{', GUARD TRIPPED' if ctl_ab else ''})")

    # normalisation: every horizon's path probabilities sum to exactly 1
    norm_ok = all(ext[d]["total"] == 1 for d in range(ext_done + 1)) and \
              all(ctl[d]["total"] == 1 for d in range(ctl_done + 1))
    require(norm_ok, "path probabilities sum to exactly 1 at every completed horizon "
                     "(normalisation)")

    rows = []
    rows.append("EXTENDED rule set (BUD + CONTACT + GRAFT)")
    rows.append("  step |  O0 new-neighbour |  O1 new-pair(newly enabled) |  O2 renew-then-"
                "consult |  menu-size dist  (P over |C_q|)")
    for d in range(ext_done + 1):
        a = ext[d]
        rows.append(f"   {d}   |  {a['o0']}  ({pct(a['o0'])}) |  {a['o1']}  ({pct(a['o1'])}) "
                    f"|  {a['o2']}  ({pct(a['o2'])}) |  {fmt_menu(a['menu'])}")
    rows.append("")
    rows.append("CONTROL rule set (BUD + CONTACT ; GRAFT absent)")
    rows.append("  step |  O0 |  O1 |  O2 |  menu-size dist")
    for d in range(ctl_done + 1):
        a = ctl[d]
        rows.append(f"   {d}   |  {a['o0']} |  {a['o1']} |  {a['o2']} |  {fmt_menu(a['menu'])}")
    with open(TABLE, "w") as f:
        f.write("\n".join(rows) + "\n")
    for r in rows:
        log("  " + r)

    # ---- primary assertions ----
    log("=" * 88)
    log("[4] primary results")
    # control: the menu-monotonicity theorem => the designated q never gains a pair, a
    # neighbour, or a consult -- exactly zero at every horizon.
    ctl_zero = all(ctl[d]["o0"] == 0 and ctl[d]["o1"] == 0 and ctl[d]["o2"] == 0
                   for d in range(ctl_done + 1))
    require(ctl_zero, "CONTROL: O0=O1=O2=0 at every horizon (menu monotone non-increasing; "
                      "an empty menu stays empty without GRAFT)")
    require(ext[ext_done]["o1"] > 0,
            f"EXTENDED: P(O1 newly-enabled pair by step {ext_done}) = {ext[ext_done]['o1']} "
            f"({pct(ext[ext_done]['o1'])}) > 0 -- renewal OCCURS in reachable dynamics")
    require(ext[ext_done]["o2"] > 0,
            f"EXTENDED: P(O2 renew-then-consult by step {ext_done}) = {ext[ext_done]['o2']} "
            f"({pct(ext[ext_done]['o2'])}) > 0 -- the renewed pair is actually CONSULTED")
    require(ext[3]["o2"] > 0, "EXTENDED: renew-then-consult already possible by step 3 "
                              "(BUD/GRAFT then CONTACT, or GRAFT-at-seed then CONTACT)")
    # O1 and O0 are genuinely distinct quantities (both reported); O1 <= O0 need NOT hold in
    # general, but every new pair here arrives with a new neighbour, so O1 <= O0 pathwise.
    require(all(ext[d]["o1"] <= ext[d]["o0"] for d in range(ext_done + 1)),
            "EXTENDED: on this seed every newly-enabled pair arrives via a new neighbour "
            "(O1 <= O0 at each horizon), yet the two are reported separately")

    # ---- [5] an explicit witnessing renew-then-consult path (exact probability) ----
    log("=" * 88)
    log("[5] one explicit renew-then-consult path with its exact probability")
    # BUD(0,2) -> GRAFT(1,0,4) -> CONTACT({3,4},1)
    p = Fr(1)
    G = S
    for ev in [("B", 0, 2), ("G", 1, 0, 4), ("C", frozenset((3, 4)), 1)]:
        evs = events_extended(G)
        assert ev in evs, f"witness event {ev} not eligible; eligible={evs}"
        p *= Fr(1, len(evs))
        G = apply_ev(G, ev)
    log(f"  path  BUD(0,2) ; GRAFT(1,0,4) ; CONTACT({{3,4}},1)  has exact probability {p} "
        f"= {pct(p)}")
    log(f"  after it: q={QID} consumed the newly-enabled pair {{3,4}} that did NOT exist at "
        f"the seed (newly enabled relevance, not delayed consultation)")
    require(p > 0, "the witnessing renew-then-consult path has positive exact probability")

    # ---- [6] relabelling invariance ----
    log("=" * 88)
    log("[6] nontrivial relabelling invariance of the outcome probabilities")
    Sr = relabel(S, 100)
    extr, r_done, *_ = enumerate_process(Sr, events_extended, QID + 100)
    rel_ok = all(ext[d]["o0"] == extr[d]["o0"] and ext[d]["o1"] == extr[d]["o1"]
                 and ext[d]["o2"] == extr[d]["o2"] and
                 dict(ext[d]["menu"]) == dict(extr[d]["menu"])
                 for d in range(ext_done + 1))
    require(rel_ok, "outcome probabilities and menu-size distributions are unchanged under a "
                    "nontrivial vertex relabelling (identities used for measurement only, "
                    "never for selection)")

    log("=" * 88)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    log("Interpretation: adding GRAFT changes BOTH the available transitions AND the "
        "scheduler's allocation of events; equal event counts are NOT matched physical time "
        "nor equal BUD counts. A positive result demonstrates renewal + consultation under a "
        "DESIGNED coupling on a DELIBERATELY chosen seed -- not that renewal is typical or "
        "inevitable.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

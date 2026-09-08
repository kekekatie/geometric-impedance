#!/usr/bin/env python3
"""
local_contact_checks.py -- corrected checks + one bounded exact test of an AUTONOMOUS,
asynchronous, LOCAL CONTACT event competing in the scheduler (no global sweep).

Corrections over ../endogenous_latent_relevance/ (see that folder's dated clarification):
  C1 compare exact RATIONAL successor probability distributions, not raw multiplicity
     dicts (fixture: proportional multiplicities -> equal distributions).
  C2 CONTACT's reported additions are ACTUAL new edges (already-present A-A excluded).
  C3 assert exact preservation of Q labels and Q-incident edges under the identity vertex
     correspondence (not merely up to isomorphism).
  C4 the leaf-adding comparison is an "archive-blind alternative intervention", NOT a
     matched coupling-off ablation (the genuine coupling-off is BUD-only M1).
  C5 the archive is unchanged; information about its relationships is re-expressed in new
     ACTIVE connections.
  C6 distinguish local-neighbourhood dependence from an externally timed global sweep.

Autonomous extended rule set (a modelling assumption, stated as such):
  - BUD(x,y) at k=1 (directed active bond), unchanged.
  - CONTACT(a,q,b): eligible iff a,b are DISTINCT active neighbours of quiet q AND the
    active edge a-b is ABSENT. Effect: add only a-b. The endpoint pair {a,b} is UNORDERED
    (swap does not duplicate). DISTINCT quiet mediators q are DISTINCT eligible events even
    if they would add the same edge.
  - one step = uniform selection over the UNION of directed BUD events and CONTACT events
    (each event weight 1 -- a modelling assumption). No global sweep; no external timing.
    "Autonomous" = selection follows the fixed rules only.

Exact isomorphism (A/Q matched); WL only buckets; Fraction probabilities; asserts +
nonzero exit (printed text is not a gate).
"""
from __future__ import annotations
import os, sys, itertools
from fractions import Fraction
import networkx as nx
from networkx.algorithms.isomorphism import categorical_node_match

NM = categorical_node_match("label", None)
HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "local_contact_report.txt")
TABLE = os.path.join(HERE, "results", "transition_tables.txt")
LINES, FAILS = [], []


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


# ------------------------------------------------------------------- graph + M1
def wl(G):
    return nx.weisfeiler_lehman_graph_hash(G, node_attr="label", iterations=5)


def iso(G, H):
    return nx.is_isomorphic(G, H, node_match=NM)


def active_bonds(G):
    return [(u, v) for u, v in G.edges()
            if G.nodes[u]["label"] == "A" and G.nodes[v]["label"] == "A"]


def _fresh(G):
    return (max([n for n in G.nodes if isinstance(n, int)] + [-1]) + 1)


def bud(G, x, y):
    assert G.has_edge(x, y) and G.nodes[x]["label"] == "A" and G.nodes[y]["label"] == "A"
    H = G.copy(); H.nodes[y]["label"] = "Q"
    z = _fresh(H); H.add_node(z, label="A"); H.add_edge(x, z); H.add_edge(y, z)
    return H


def path(n):
    G = nx.Graph()
    for i in range(n):
        G.add_node(i, label="A")
    for i in range(n - 1):
        G.add_edge(i, i + 1)
    return G


def proj(G):
    P = G.subgraph([n for n in G if G.nodes[n]["label"] == "A"]).copy()
    for n in P:
        P.nodes[n]["label"] = "A"
    return P


def class_reps(graphs):
    buckets = {}
    for G in graphs:
        buckets.setdefault(wl(G), []).append(G)
    reps = []
    for gs in buckets.values():
        local = []
        for G in gs:
            if not any(iso(G, R) for R in local):
                local.append(G)
        reps.extend(local)
    return reps


def cidx(G, reps):
    for i, R in enumerate(reps):
        if iso(G, R):
            return i
    raise ValueError("projection class not in pcls (build pcls to cover reachable set)")


# ------------------------------------------------- events: BUD (directed) + CONTACT
def events_bud(G):
    out = []
    for u, v in active_bonds(G):
        out.append(("B", u, v)); out.append(("B", v, u))
    return out


def events_contact(G):
    """CONTACT(a,q,b): distinct active a,b adjacent to quiet q, edge a-b absent.
    Unordered pair (combinations, not permutations); one event per (mediator q, pair)."""
    out = []
    for q in [n for n in G if G.nodes[n]["label"] == "Q"]:
        anbrs = sorted(a for a in G.neighbors(q) if G.nodes[a]["label"] == "A")
        for a, b in itertools.combinations(anbrs, 2):        # unordered, no duplicate swap
            if not G.has_edge(a, b):                          # C2: actual new edge only
                out.append(("C", frozenset((a, b)), q))
    return out


def events_ext(G):
    return events_bud(G) + events_contact(G)


def apply_ev(G, ev):
    if ev[0] == "B":
        return bud(G, ev[1], ev[2])
    a, b = tuple(ev[1])
    H = G.copy(); H.add_edge(a, b); return H            # both endpoints active


# --------------------------------------------- exact projected successor distributions
def dist1(G, evfn, pcls):
    evs = evfn(G); n = len(evs); d = {}
    for e in evs:
        c = cidx(proj(apply_ev(G, e)), pcls)
        d[c] = d.get(c, 0) + Fraction(1, n)
    return d


def dist2(G, evfn, pcls):
    evs = evfn(G); n1 = len(evs); d = {}
    for e1 in evs:
        G1 = apply_ev(G, e1); evs2 = evfn(G1); n2 = len(evs2)
        for e2 in evs2:
            c = cidx(proj(apply_ev(G1, e2)), pcls)
            d[c] = d.get(c, 0) + Fraction(1, n1) * Fraction(1, n2)
    return d


def collect_projs(G, evfn):
    out = [proj(G)]
    for e1 in evfn(G):
        G1 = apply_ev(G, e1); out.append(proj(G1))
        for e2 in evfn(G1):
            out.append(proj(apply_ev(G1, e2)))
    return out


def fmt(d):
    return "{" + ", ".join(f"{c}:{d[c]}" for c in sorted(d)) + "}"


# ---------------------------------------------------------- the matched pair (reachable)
def depth2_classes():
    seed = path(4); states = []
    for e1 in events_bud(seed):
        G1 = bud(seed, e1[1], e1[2])
        for e2 in events_bud(G1):
            states.append(bud(G1, e2[1], e2[2]))
    return class_reps(states)


def q_sig(G):
    return tuple(sorted(sum(1 for _ in G.neighbors(n))
                        for n in G if G.nodes[n]["label"] == "Q"))


def find_pair(fulls):
    for i in range(len(fulls)):
        for j in range(i + 1, len(fulls)):
            if iso(proj(fulls[i]), proj(fulls[j])) and not iso(fulls[i], fulls[j]):
                return i, j
    return None


def q_incident(G):
    """(node->label for Q and their neighbours; set of Q-incident edges) under identity."""
    labels = {n: G.nodes[n]["label"] for n in G if G.nodes[n]["label"] == "Q"}
    edges = frozenset(frozenset((u, v)) for u, v in G.edges()
                      if G.nodes[u]["label"] == "Q" or G.nodes[v]["label"] == "Q")
    return labels, edges


def relabel(G, shift):
    return nx.relabel_nodes(G, {n: n + shift for n in G})


def invariants_ok(G):
    return (not any(True for _ in nx.selfloop_edges(G))
            and all(G.nodes[n]["label"] in ("A", "Q") for n in G)
            and nx.is_connected(G))


# ============================================================================ MAIN
def main():
    # ---- C1 fixture: proportional multiplicities -> equal distributions ----
    log("=" * 78)
    log("[C1] rational distributions, not raw multiplicity dicts")
    m1 = {0: 2, 1: 2}; m2 = {0: 3, 1: 3}                 # different dicts, tot 4 vs 6
    p1 = {c: Fraction(v, sum(m1.values())) for c, v in m1.items()}
    p2 = {c: Fraction(v, sum(m2.values())) for c, v in m2.items()}
    log(f"  multiplicities {m1} (tot 4) vs {m2} (tot 6);  probs {fmt(p1)} vs {fmt(p2)}")
    require(m1 != m2 and p1 == p2,
            "proportional multiplicities give EQUAL distributions "
            "(compare probabilities, not multiplicity dicts)")

    # ---- CONTACT semantics fixtures (C2, unordered, distinct mediators) ----
    log("=" * 78)
    log("[events] CONTACT semantics")
    # two quiets q1,q2 each mediating the same absent pair {a,b}
    F = nx.Graph()
    for n, l in [("a", "A"), ("b", "A"), ("q1", "Q"), ("q2", "Q")]:
        F.add_node(n, label=l)
    F.add_edges_from([("a", "q1"), ("b", "q1"), ("a", "q2"), ("b", "q2")])  # a-b absent
    ce = events_contact(F)
    require(len(ce) == 2 and all(set(e[1]) == {"a", "b"} for e in ce),
            "distinct quiet mediators are DISTINCT CONTACT events for the same edge (mult 2)")
    require(len({(e[1], e[2]) for e in ce}) == 2,
            "the two events differ only by mediator q (pair unordered, not duplicated by swap)")
    F2 = F.copy(); F2.add_edge("a", "b")
    require(len(events_contact(F2)) == 0, "once a-b present, CONTACT on {a,b} is ineligible (C2)")

    # ---- matched pair ----
    log("=" * 78)
    log("[pair] reachable matched pair: iso active projection, different archive")
    fulls = depth2_classes(); i, j = find_pair(fulls); Gi, Gj = fulls[i], fulls[j]
    require(iso(proj(Gi), proj(Gj)) and not iso(Gi, Gj) and q_sig(Gi) != q_sig(Gj),
            f"pair (classes {i},{j}): iso active proj, archives {q_sig(Gi)} vs {q_sig(Gj)}")

    # ---- C3: archive preserved exactly under identity correspondence during CONTACT ----
    log("=" * 78)
    log("[C3] CONTACT preserves Q labels and Q-incident edges EXACTLY (identity map)")
    c3_ok = True; newedge_ok = True
    for G in (Gi, Gj):
        for e in events_contact(G):
            H = apply_ev(G, e)
            if q_incident(G) != q_incident(H):
                c3_ok = False
            a, b = tuple(e[1])
            added = set(H.edges()) - set(G.edges())
            if added != {(a, b)} and added != {(b, a)}:   # exactly one actual new A-A edge
                newedge_ok = False
            if not (H.nodes[a]["label"] == "A" and H.nodes[b]["label"] == "A"):
                newedge_ok = False
            if H.number_of_nodes() != G.number_of_nodes():
                newedge_ok = False
    require(c3_ok, "Q labels + Q-incident edge SET identical before/after each CONTACT "
                   "(exact, identity correspondence -- not merely isomorphic)")
    require(newedge_ok, "each CONTACT adds exactly ONE actual new A-A edge, no vertices, "
                        "no label change (C2/C5: archive unchanged; its relations re-expressed "
                        "as active edges)")

    # ---- legality + invariants over the reachable-in-2 set ----
    log("=" * 78)
    log("[invariants] legal events + graph invariants over reachable-in-2 (extended)")
    inv_ok = True
    for G in (Gi, Gj):
        for e1 in events_ext(G):
            G1 = apply_ev(G, e1)
            if not invariants_ok(G1):
                inv_ok = False
            for e2 in events_ext(G1):
                if not invariants_ok(apply_ev(G1, e2)):
                    inv_ok = False
    require(inv_ok, "every reachable state (<=2 extended events) is a simple, connected, "
                    "A/Q-labelled graph")

    # ---- the bounded experiment: distributions after 1 and 2 events ----
    log("=" * 78)
    log("[experiment] projected active successor distributions: BUD-only vs extended")
    pcls = class_reps(collect_projs(Gi, events_ext) + collect_projs(Gj, events_ext))
    rows = ["rule       state  step  distribution over projected active successor classes"]
    res = {}
    for name, evfn in (("BUD-only", events_bud), ("extended", events_ext)):
        for lab, G in ((str(i), Gi), (str(j), Gj)):
            d1 = dist1(G, evfn, pcls); d2 = dist2(G, evfn, pcls)
            assert sum(d1.values()) == 1 and sum(d2.values()) == 1, "distributions must sum to 1"
            res[(name, lab, 1)] = d1; res[(name, lab, 2)] = d2
            rows.append(f"  {name:<9} {lab:>3}   1    {fmt(d1)}")
            rows.append(f"  {name:<9} {lab:>3}   2    {fmt(d2)}")
        rows.append("")
    with open(TABLE, "w") as f:
        f.write("\n".join(rows) + "\n")
    for r in rows:
        log("  " + r)

    # BUD-only: the two archives are indistinguishable (control / coupling-off)
    require(res[("BUD-only", str(i), 1)] == res[("BUD-only", str(j), 1)]
            and res[("BUD-only", str(i), 2)] == res[("BUD-only", str(j), 2)],
            "BUD-only (coupling off): identical distributions at 1 and 2 events "
            "(archive inert -- the genuine matched control)")

    diff1 = res[("extended", str(i), 1)] != res[("extended", str(j), 1)]
    diff2 = res[("extended", str(i), 2)] != res[("extended", str(j), 2)]
    log(f"  extended rule set: distributions differ at 1 event = {diff1}; at 2 events = {diff2}")
    if diff1 or diff2:
        require(True, "EXTENDED rule set: archive-dependent active evolution "
                      "(the two archives now yield different projected successor distributions)")
    else:
        require(True, "EXTENDED rule set: NO projected difference on this pair "
                      "(reported as-is; no rule search or rate tuning)")

    # ---- relabelling invariance (nontrivial permutation) ----
    log("=" * 78)
    log("[relabel] invariance under nontrivial vertex relabelling")
    rel_ok = True
    for G in (Gi, Gj):
        Gr = relabel(G, 100)
        pl = class_reps(collect_projs(G, events_ext) + collect_projs(Gr, events_ext))
        if dist1(G, events_ext, pl) != dist1(Gr, events_ext, pl) or \
           dist2(G, events_ext, pl) != dist2(Gr, events_ext, pl):
            rel_ok = False
    require(rel_ok, "extended distributions unchanged under nontrivial relabelling")

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

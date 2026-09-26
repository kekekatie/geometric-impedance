#!/usr/bin/env python3
"""
legality_fixture.py -- LEGALITY check only for the recommended renewal rule GRAFT
(design task; NOT the experiment). One tiny hand fixture, no outcome search.

GRAFT(q, a, w) -- "graft new active structure onto an existing quiet trace":
  Local motif (bounded, radius 2 from q): q:Q, a:A, w:A, edges q-a and a-w present,
  edge q-w ABSENT.  Effect: add edge q-w (q gains a new active neighbour w).
  Append-only: no label changed, no edge deleted, no vertex created.

This breaks CONTACT-menu monotonicity by ADDING an active neighbour to an old quiet
vertex (option 1). We verify on a fixture: an existing quiet q with EMPTY CONTACT menu
before GRAFT and a NONEMPTY menu after, with the archive preserved in the append-only
sense. Asserts + nonzero exit; printed text is not a gate.
"""
from __future__ import annotations
import os, sys, itertools
import networkx as nx
from networkx.algorithms.isomorphism import categorical_node_match

NM = categorical_node_match("label", None)
HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "legality_report.txt")
LINES, FAILS = [], []


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


def active_neighbours(G, q):
    return sorted(a for a in G.neighbors(q) if G.nodes[a]["label"] == "A")


def C_q(G, q):
    an = active_neighbours(G, q)
    return {frozenset((a, b)) for a, b in itertools.combinations(an, 2)
            if not G.has_edge(a, b)}


def graft_eligible(G):
    """All GRAFT(q,a,w): q:Q, a:A adjacent to q, w:A adjacent to a, q-w absent, w!=q."""
    out = []
    for q in [n for n in G if G.nodes[n]["label"] == "Q"]:
        for a in [n for n in G.neighbors(q) if G.nodes[n]["label"] == "A"]:
            for w in [n for n in G.neighbors(a)
                      if G.nodes[n]["label"] == "A" and n != q and not G.has_edge(q, n)]:
                out.append(("G", q, a, w))
    return out


def apply_graft(G, q, a, w):
    assert G.nodes[q]["label"] == "Q" and G.nodes[a]["label"] == "A" \
        and G.nodes[w]["label"] == "A"
    assert G.has_edge(q, a) and G.has_edge(a, w) and not G.has_edge(q, w)
    H = G.copy(); H.add_edge(q, w); return H


def archive_appendonly(G, H):
    """Record preserved (append-only): every G-vertex keeps its label; every G-edge
    still present in H; only additions allowed. Returns (labels_ok, edges_ok)."""
    labels_ok = all(n in H and H.nodes[n]["label"] == G.nodes[n]["label"] for n in G)
    edges_ok = all(H.has_edge(u, v) for u, v in G.edges())
    return labels_ok, edges_ok


def main():
    log("=" * 74)
    log("[fixture] GRAFT legality: empty CONTACT menu -> nonempty, archive append-only")
    # triangle apex q (quiet) with active neighbours x,z joined by x-z (so C_q empty),
    # plus a new active tip w grown on x (wedge w-x-q); q-w absent, w-z absent.
    G = nx.Graph()
    for n, l in [("x", "A"), ("q", "Q"), ("z", "A"), ("w", "A")]:
        G.add_node(n, label=l)
    G.add_edges_from([("x", "q"), ("q", "z"), ("x", "z"), ("x", "w")])
    log(f"  state: nodes {dict(G.nodes(data='label'))}")
    log(f"  edges {sorted(map(tuple, (frozenset(e) for e in G.edges())))}")

    before = C_q(G, "q")
    log(f"  C_q(before) = {sorted(map(tuple, before))}  (active nbrs of q: "
        f"{active_neighbours(G,'q')}; x-z present so pair edged)")
    require(before == set(), "q has an EMPTY CONTACT menu before GRAFT")

    elig = graft_eligible(G)
    log(f"  GRAFT-eligible events: {elig}")
    require(("G", "q", "x", "w") in elig,
            "GRAFT(q,x,w) is eligible via the bounded wedge w-x-q (radius 2, local)")
    require(all(ev[1] == "q" for ev in elig) and all(not G.has_edge(ev[1], ev[3]) for ev in elig),
            "every eligible GRAFT targets a real absent q-w with an active bridge")

    H = apply_graft(G, "q", "x", "w")
    after = C_q(H, "q")
    log(f"  C_q(after)  = {sorted(map(tuple, after))}  (q now also neighbours w; z-w absent)")
    require(after == {frozenset(("z", "w"))},
            "after GRAFT, C_q is NONEMPTY: {z,w} is a NEW opportunity (menu monotonicity broken)")
    require(before < after,
            "the new menu strictly contains the old: an opportunity was ADDED, not consulted")

    lab_ok, edge_ok = archive_appendonly(G, H)
    require(lab_ok, "record preserved (labels): q still Q; no label overwritten")
    require(edge_ok, "record preserved (edges): every prior edge still present; none deleted")
    require(H.number_of_nodes() == G.number_of_nodes(),
            "no vertex created (GRAFT only adds one edge incident to the quiet trace)")
    added = set(map(frozenset, H.edges())) - set(map(frozenset, G.edges()))
    require(added == {frozenset(("q", "w"))},
            "exactly one edge added, and it is incident to the quiet vertex q "
            "(archive AUGMENTED, not 'unchanged' -- claim relaxed honestly)")

    # 'newly enabled' vs 'delayed consultation': the new pair involves w, which was NOT a
    # neighbour of q before, so {z,w} could not have been in C_q at q's deposition.
    require(frozenset(("z", "w")) not in before,
            "the new opportunity was NOT already present -> this is newly-enabled relevance, "
            "not delayed consultation of an already-eligible trace")

    log("=" * 74)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("LEGALITY OK: GRAFT is local, append-only, and turns an empty menu nonempty.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

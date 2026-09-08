#!/usr/bin/env python3
"""
active_projection_checks.py -- EXACT test of whether the ACTIVE PROJECTION of M1 carries
a closed transition rule, independent of the quiet archive, under uniform selection among
directed active-active bonds.

Active projection  pi(G) = induced subgraph on A vertices keeping only A-A edges,
                           isolated A vertices retained.

Claims checked (asserts; nonzero exit on any failure -- printed text is not a gate):
  L1 selection is pi-measurable: directed eligible events of G  <->  directed edges of pi(G).
  L2 effect commutes with projection: pi(BUD(x,y) G)  ==  budpi(x,y) pi(G),  where
     budpi = "delete y (and its active edges); keep x; add k leaves on x".  (No Q input.)
  =>  the distribution of the next ACTIVE state depends only on pi(G) (closed rule),
      NOT on Q vertices or A-Q / Q-Q edges, UNDER THIS SCHEDULER.
  Bounded: reuse the 11 depth-2 full-state classes from path(4), k=1; project each; build
  the projected directed-event successor distribution (exact rationals); verify full
  classes with isomorphic projections share the projected successor distribution; exhibit
  a pair with different quiet archive but isomorphic active projection.

Isomorphism: full states use state-preserving (A/Q) match; active projections are all-A so
plain graph iso suffices. WL only buckets; every bucket resolved exactly.
"""
from __future__ import annotations
import os, sys
from fractions import Fraction
import networkx as nx
from networkx.algorithms.isomorphism import categorical_node_match

NM = categorical_node_match("label", None)
HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "projection_report.txt")
TABLE = os.path.join(HERE, "results", "projection_successor_table.txt")
LINES, FAILS = [], []
K = 1


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    (LINES.append(f"  [PASS] {msg}") if cond else
     (LINES.append(f"  [FAIL] {msg}"), FAILS.append(msg)))
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)


# ------------------------------------------------------------------- M1 core
def wl(G):
    return nx.weisfeiler_lehman_graph_hash(G, node_attr="label", iterations=5)


def iso_full(G, H):
    return nx.is_isomorphic(G, H, node_match=NM)


def iso_active(G, H):
    # active projections are all-label-A; plain graph iso (label match is redundant)
    return nx.is_isomorphic(G, H, node_match=NM)


def active_bonds(G):
    return [(u, v) for u, v in G.edges()
            if G.nodes[u]["label"] == "A" and G.nodes[v]["label"] == "A"]


def directed_events(G):
    out = []
    for u, v in active_bonds(G):
        out.append((u, v)); out.append((v, u))
    return out


def _fresh(G):
    return (max(G.nodes) + 1) if len(G.nodes) else 0


def bud(G, x, y, k=K):
    assert G.has_edge(x, y) and G.nodes[x]["label"] == "A" and G.nodes[y]["label"] == "A"
    H = G.copy(); H.nodes[y]["label"] = "Q"
    n = _fresh(H)
    for i in range(k):
        z = n + i; H.add_node(z, label="A"); H.add_edge(x, z)
        if i == 0:
            H.add_edge(y, z)
    return H


def path(n):
    G = nx.Graph()
    for i in range(n):
        G.add_node(i, label="A")
    for i in range(n - 1):
        G.add_edge(i, i + 1)
    return G


# ---------------------------------------------------- active projection + closed rule
def proj(G):
    """Induced subgraph on A vertices, A-A edges only, isolated A vertices retained."""
    A = [n for n in G if G.nodes[n]["label"] == "A"]
    P = G.subgraph(A).copy()
    for n in P:                      # normalise labels (all A)
        P.nodes[n]["label"] = "A"
    return P


def budpi(P, x, y, k=K):
    """Closed rule on the ACTIVE graph: delete y (+its edges); keep x; add k leaves on x.
    Reads only the active graph P and the event (x,y). No quiet input."""
    assert P.has_edge(x, y)
    Q = P.copy(); Q.remove_node(y)
    n = _fresh(Q)
    for i in range(k):
        z = n + i; Q.add_node(z, label="A"); Q.add_edge(x, z)
    return Q


# -------------------------------------------- exact class machinery (WL bucket + exact)
def class_reps(graphs, isof):
    buckets = {}
    for G in graphs:
        buckets.setdefault(wl(G), []).append(G)
    reps = []
    for gs in buckets.values():
        local = []
        for G in gs:
            if not any(isof(G, R) for R in local):
                local.append(G)
        reps.extend(local)
    return reps


def cidx(G, reps, isof):
    for i, R in enumerate(reps):
        if isof(G, R):
            return i
    return -1


# ==================================================================== 1. analytic lemmas
def check_lemmas():
    log("=" * 74)
    log("[L1/L2] selection is pi-measurable, and the effect commutes with projection")
    # reachable states to test on: seed path(4) plus all depth-1,2,3 descendants
    frontier = [path(4)]
    pool = list(frontier)
    for _ in range(3):
        nxt = []
        for G in frontier:
            for (x, y) in directed_events(G):
                nxt.append(bud(G, x, y))
        pool += nxt; frontier = nxt
    log(f"  testing on {len(pool)} reachable states (depth 0..3 from path(4))")

    l1 = all(len(directed_events(G)) == 2 * proj(G).number_of_edges() for G in pool)
    require(l1, "L1: #directed eligible events == 2 * (#edges of active projection) "
                "(eligible set is a function of pi(G) alone)")
    # also the event *identities* are exactly the directed edges of pi(G)
    l1b = True
    for G in pool:
        de = set(directed_events(G))
        pe = set()
        for u, v in proj(G).edges():
            pe.add((u, v)); pe.add((v, u))
        if de != pe:
            l1b = False
    require(l1b, "L1': directed events == directed edges of pi(G) exactly")

    l2 = True
    for G in pool:
        P = proj(G)
        for (x, y) in directed_events(G):
            lhs = proj(bud(G, x, y))          # project THEN nothing
            rhs = budpi(P, x, y)              # rule ON the projection
            if not iso_active(lhs, rhs):
                l2 = False
    require(l2, "L2: pi(BUD(x,y) G) ~= budpi(x,y) pi(G)  for every reachable state & event "
                "(effect is closed on active graphs; Q never consulted)")
    log("  => Under uniform selection over directed active bonds, the distribution of the")
    log("     NEXT ACTIVE state is a function of pi(G) alone: a CLOSED transition rule,")
    log("     independent of Q vertices and A-Q/Q-Q edges.")
    log("  NOTE (scope): this uses a scheduler that reads ONLY pi (uniform over directed")
    log("     active bonds). A scheduler weighting by TOTAL degree or any quiet context")
    log("     would break L1 and the closure would NOT hold.")


# ==================================================== 2. the 11 depth-2 classes, projected
def depth2_full_classes():
    seed = path(4)
    states = []
    for (x1, y1) in directed_events(seed):
        G1 = bud(seed, x1, y1)
        for (x2, y2) in directed_events(G1):
            states.append(bud(G1, x2, y2))
    return class_reps(states, iso_full), states


def check_projection_table():
    log("=" * 74)
    log("[2] 11 depth-2 full classes -> active-projection classes + projected successors")
    fulls, _ = depth2_full_classes()
    require(len(fulls) == 11, f"exact depth-2 full-state classes == 11 (got {len(fulls)})")

    # global list of ACTIVE-projection classes appearing at depth 2 and depth 3
    projset = [proj(R) for R in fulls]
    succ_projs = [proj(bud(R, x, y)) for R in fulls for (x, y) in directed_events(R)]
    pcls = class_reps(projset + succ_projs, iso_active)

    def proj_class(R):
        return cidx(proj(R), pcls, iso_active)

    def proj_succ_dist(R):
        des = directed_events(R); tot = len(des); mult = {}
        for (x, y) in des:
            ci = cidx(proj(bud(R, x, y)), pcls, iso_active)
            mult[ci] = mult.get(ci, 0) + 1
        probs = {c: Fraction(m, tot) for c, m in mult.items()}
        return tot, dict(sorted(mult.items())), probs

    rows = ["full  activeProj  B  #dirEv  ->  {projSuccClass: multiplicity}  (exact probs)"]
    info = []
    for i, R in enumerate(fulls):
        pc = proj_class(R); tot, mult, probs = proj_succ_dist(R)
        nA = sum(1 for n in R if R.nodes[n]["label"] == "A")
        B = len(active_bonds(R))
        pstr = "{" + ", ".join(f"{c}:{probs[c]}" for c in sorted(probs)) + "}"
        rows.append(f"  {i:>2}      P{pc:<2}    {B}    {tot:>2}    -> {mult}   probs {pstr}")
        info.append((i, pc, tot, tuple(sorted(mult.items()))))
    for r in rows:
        log("  " + r)
    with open(TABLE, "w") as f:
        f.write("\n".join(rows) + "\n")

    n_proj_classes = len({pc for (_, pc, _, _) in info})
    log(f"  => 11 full classes collapse onto {n_proj_classes} active-projection classes.")

    # group full classes by active-projection class; within a group the projected
    # successor distribution MUST match (that's the closure, checked exactly)
    groups = {}
    for (i, pc, tot, mult) in info:
        groups.setdefault(pc, []).append((i, tot, mult))
    same = True; shared_groups = []
    for pc, members in groups.items():
        if len(members) > 1:
            shared_groups.append((pc, [m[0] for m in members]))
            dists = {(m[1], m[2]) for m in members}   # (total, multiplicity-tuple)
            # multiplicities are keyed by GLOBAL proj-class id, so equality is meaningful
            if len(dists) != 1:
                same = False
    log(f"  full-class groups sharing an active projection: "
        f"{[(f'P{pc}', ids) for pc, ids in shared_groups] or 'none'}")
    require(same, "full classes with isomorphic active projections share IDENTICAL "
                  "projected successor distributions (closure confirmed by enumeration)")
    return fulls, pcls, shared_groups


# ================================================= 3. archive-different / projection-same
def check_archive_independence(fulls, pcls, shared_groups):
    log("=" * 74)
    log("[3] a pair: DIFFERENT quiet archive, SAME active projection")
    found = None
    for i in range(len(fulls)):
        for j in range(i + 1, len(fulls)):
            Gi, Gj = fulls[i], fulls[j]
            if iso_active(proj(Gi), proj(Gj)) and not iso_full(Gi, Gj):
                found = (i, j); break
        if found:
            break
    if found:
        i, j = found
        Gi, Gj = fulls[i], fulls[j]
        qi = _archive_signature(Gi); qj = _archive_signature(Gj)
        log(f"  found among the 11 depth-2 classes: full classes {i} and {j}")
        log(f"    full states non-isomorphic: {not iso_full(Gi, Gj)}")
        log(f"    active projections isomorphic: {iso_active(proj(Gi), proj(Gj))}")
        log(f"    quiet archive (Q-degree multiset within full graph): {i}:{qi}  {j}:{qj}")
        require(not iso_full(Gi, Gj) and iso_active(proj(Gi), proj(Gj)),
                "exhibited a real pair: distinguishable in the FULL present, "
                "NOT in the ACTIVE present")
        # and their projected successor distributions coincide (already covered, re-assert)
        require(_same_proj_succ(Gi, Gj, pcls),
                "the pair's projected successor distributions coincide "
                "(archive is causally inert for the active rule)")
    else:
        log("  none found among the 11 depth-2 classes; using a labelled constructed fixture")
        require(_fixture_archive_independent(),
                "constructed fixture: two states, same active projection, different quiet "
                "archive -> identical projected successor distribution")


def _archive_signature(G):
    return tuple(sorted(sum(1 for _ in G.neighbors(n))
                        for n in G if G.nodes[n]["label"] == "Q"))


def _same_proj_succ(Gi, Gj, pcls):
    def dist(R):
        des = directed_events(R); tot = len(des); m = {}
        for (x, y) in des:
            ci = cidx(proj(bud(R, x, y)), pcls, iso_active); m[ci] = m.get(ci, 0) + 1
        return (tot, tuple(sorted(m.items())))
    return dist(Gi) == dist(Gj)


def _fixture_archive_independent():
    # Two hand-built states with the SAME active projection (a single A-A bond a-b)
    # but different quiet archives, checked for identical projected successor behaviour.
    def mk(narch):
        G = nx.Graph()
        G.add_node("a", label="A"); G.add_node("b", label="A"); G.add_edge("a", "b")
        for t in range(narch):
            q = f"q{t}"; G.add_node(q, label="Q"); G.add_edge("a", q)   # archive on a
        return G
    G1, G2 = mk(1), mk(3)
    if not iso_active(proj(G1), proj(G2)):
        return False
    if iso_full(G1, G2):
        return False
    pcls = class_reps([proj(bud(G1, x, y)) for (x, y) in directed_events(G1)]
                      + [proj(bud(G2, x, y)) for (x, y) in directed_events(G2)], iso_active)
    return _same_proj_succ(G1, G2, pcls)


def main():
    check_lemmas()
    fulls, pcls, shared = check_projection_table()
    check_archive_independence(fulls, pcls, shared)
    log("=" * 74)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
active_latent_checks.py -- bounded EXACT test of:
   "a subsequent local structural change can make a latent (quiet) trace matter again."

Background (proved earlier, endogenous_active_projection/): under uniform selection over
directed active bonds, M1's active projection pi(G) is a CLOSED transition rule -- the
quiet archive is causally inert. So two states with isomorphic active projections but
different archives have identical projected active successor distributions.

This module adds ONE extension rule (an explicit MODELLING ASSUMPTION, not emergent):

  CONTACT-sweep  (selected candidate R_bridge):
    a controlled intervention applied synchronously at every active vertex.
    For each active vertex a, each QUIET neighbour q of a, and each active neighbour
    b != a of q, ADD the active bond a-b.  (Promote every latent  a - q - b  path to an
    active edge a-b.)  Read-only on the archive: it never changes a Q label, never
    changes a Q-incident edge, and creates no vertices. It only adds A-A edges among
    pre-existing active vertices.  No creation IDs / history labels / coordinates are
    read; eligibility = "a is active with a quiet neighbour that has another active
    neighbour"; location = all active sites (symmetric, no anchor choice); randomness =
    none (deterministic).

Claim: BEFORE CONTACT the matched pair has identical projected active successor
distributions (archive inert); AFTER CONTACT they differ (the latent trace became
relevant). Controls: original M1 (no contact) shows no archive effect; a coupling-
DISABLED intervention (adds active leaves, never reads Q) shows no archive effect;
relabelling-invariant; and the dormant trace is verified NOT rewritten.

Exact isomorphism (A/Q labels matched); WL only buckets; rational probabilities.
Asserts + nonzero exit; printed text is not a gate.
"""
from __future__ import annotations
import os, sys
from fractions import Fraction
import networkx as nx
from networkx.algorithms.isomorphism import categorical_node_match

NM = categorical_node_match("label", None)
HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "latent_report.txt")
TABLE = os.path.join(HERE, "results", "transition_table.txt")
LINES, FAILS = [], []
K = 1


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    (LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg))
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


# ------------------------------------------------------------------- M1 core
def wl(G):
    return nx.weisfeiler_lehman_graph_hash(G, node_attr="label", iterations=5)


def iso(G, H):
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
    return (max([n for n in G.nodes if isinstance(n, int)] + [-1]) + 1)


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


def proj(G):
    A = [n for n in G if G.nodes[n]["label"] == "A"]
    P = G.subgraph(A).copy()
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
    return -1


# ------------------------------------------------- the extension rule (assumption)
def contact_sweep(G):
    """R_bridge: promote every active-quiet-active path a-q-b to an active bond a-b.
    Read-only on the archive; adds only A-A edges among pre-existing active vertices."""
    H = G.copy()
    A = {n for n in G if G.nodes[n]["label"] == "A"}
    Qs = [n for n in G if G.nodes[n]["label"] == "Q"]
    add = set()
    for q in Qs:
        anbrs = sorted(a for a in G.neighbors(q) if a in A)
        for i in range(len(anbrs)):
            for j in range(i + 1, len(anbrs)):
                add.add((anbrs[i], anbrs[j]))
    for a, b in add:
        H.add_edge(a, b)                      # both endpoints active; no label change
    return H, add


def contact_blind(G):
    """Coupling-DISABLED control: same 'intervene now' timing, but archive-blind --
    add a fresh active leaf to each currently-active vertex; never reads Q."""
    H = G.copy()
    n = _fresh(H)
    for a in [x for x in G if G.nodes[x]["label"] == "A"]:
        z = n; n += 1
        H.add_node(z, label="A"); H.add_edge(a, z)
    return H


# ---------------------------------------------- projected active successor distribution
def proj_succ_dist(S, pcls):
    des = directed_events(S); tot = len(des); mult = {}
    for (x, y) in des:
        ci = cidx(proj(bud(S, x, y)), pcls)
        mult[ci] = mult.get(ci, 0) + 1
    probs = {c: Fraction(m, tot) for c, m in mult.items()}
    return tot, dict(sorted(mult.items())), probs


def _global_pcls(states):
    projs = []
    for S in states:
        projs.append(proj(S))
        for (x, y) in directed_events(S):
            projs.append(proj(bud(S, x, y)))
    return class_reps(projs)


def dists_equal(S1, S2):
    pcls = _global_pcls([S1, S2])
    _, m1, p1 = proj_succ_dist(S1, pcls)
    _, m2, p2 = proj_succ_dist(S2, pcls)
    return (m1 == m2), (m1, m2), pcls


# ------------------------------------------------------------------ the matched pair
def depth2_classes():
    seed = path(4); states = []
    for (x1, y1) in directed_events(seed):
        G1 = bud(seed, x1, y1)
        for (x2, y2) in directed_events(G1):
            states.append(bud(G1, x2, y2))
    return class_reps(states)


def q_archive_sig(G):
    return tuple(sorted(sum(1 for _ in G.neighbors(n))
                        for n in G if G.nodes[n]["label"] == "Q"))


def basic_counts(G):
    return (G.number_of_nodes(), G.number_of_edges(),
            sum(1 for n in G if G.nodes[n]["label"] == "A"),
            sum(1 for n in G if G.nodes[n]["label"] == "Q"))


def find_pair(fulls):
    for i in range(len(fulls)):
        for j in range(i + 1, len(fulls)):
            if iso(proj(fulls[i]), proj(fulls[j])) and not iso(fulls[i], fulls[j]):
                return i, j
    return None


def relabel(G, shift=1000):
    return nx.relabel_nodes(G, {n: (n + shift if isinstance(n, int) else n) for n in G})


# ======================================================================= checks
def main():
    log("=" * 76)
    log("[0] MATCHED PAIR from the reachable depth-2 states (path(4), k=1)")
    fulls = depth2_classes()
    require(len(fulls) == 11, f"11 exact depth-2 full classes (got {len(fulls)})")
    pr = find_pair(fulls)
    require(pr is not None, "found a reachable pair: iso active projection, non-iso full")
    i, j = pr; Gi, Gj = fulls[i], fulls[j]
    log(f"  pair = full classes {i},{j}")
    log(f"  active projections isomorphic: {iso(proj(Gi), proj(Gj))}")
    log(f"  full graphs non-isomorphic:    {not iso(Gi, Gj)}")
    log(f"  quiet archives (Q-degree multiset): {i}:{q_archive_sig(Gi)}  {j}:{q_archive_sig(Gj)}")
    log(f"  basic counts (V,E,#A,#Q): {i}:{basic_counts(Gi)}  {j}:{basic_counts(Gj)}")
    require(iso(proj(Gi), proj(Gj)) and not iso(Gi, Gj)
            and q_archive_sig(Gi) != q_archive_sig(Gj)
            and basic_counts(Gi) == basic_counts(Gj),
            "pair: iso active proj, different archive, matching basic counts")

    log("=" * 76)
    log("[1] BEFORE the change: identical projected active successor distributions")
    eq_before, (mb1, mb2), _ = dists_equal(Gi, Gj)
    log(f"  successor multiplicities {i}:{mb1}   {j}:{mb2}")
    require(eq_before, "BEFORE contact: distributions identical (archive inert -- original M1)")

    log("=" * 76)
    log("[2] APPLY CONTACT-sweep (the extension); THEN compare active successors")
    Ci, addi = contact_sweep(Gi); Cj, addj = contact_sweep(Gj)
    log(f"  promoted latent bonds  {i}: {sorted(addi)}   {j}: {sorted(addj)}")
    log(f"  post-contact active projections isomorphic? {iso(proj(Ci), proj(Cj))}")
    eq_after, (ma1, ma2), pcls = dists_equal(Ci, Cj)
    log(f"  successor multiplicities {i}:{ma1}   {j}:{ma2}")
    require(not eq_after,
            "AFTER contact: projected active successor DISTRIBUTIONS DIFFER "
            "(the latent trace became relevant)")

    log("=" * 76)
    log("[3] CONTROL a -- original archive-blind M1 (no contact): no archive effect")
    require(eq_before, "no-contact control: identical distributions (re-assert)")

    log("[4] CONTROL b -- coupling DISABLED (archive-blind intervention): no effect")
    Bi, Bj = contact_blind(Gi), contact_blind(Gj)
    require(iso(proj(Bi), proj(Bj)), "coupling-disabled: post-intervention active "
                                     "projections still isomorphic")
    eq_blind, _, _ = dists_equal(Bi, Bj)
    require(eq_blind, "coupling-disabled: projected successor distributions stay identical "
                      "(effect requires reading the archive, not merely intervening)")

    log("[5] CONTROL c -- vertex relabelling invariance")
    Ri, Rj = relabel(Gi, 100), relabel(Gj, 500)
    CRi, _ = contact_sweep(Ri); CRj, _ = contact_sweep(Rj)
    eq_rel, _, _ = dists_equal(CRi, CRj)
    require((eq_rel == eq_after) and iso(Ci, CRi) and iso(Cj, CRj),
            "relabelling: identical outcome (post-contact states iso to unrelabelled)")

    log("[6] CONTROL d -- the dormant trace was NOT rewritten into a new record")
    def q_subgraph(G):
        Qn = [n for n in G if G.nodes[n]["label"] == "Q"]
        # Q vertices + ALL edges incident to any Q vertex, with endpoint labels
        H = nx.Graph()
        for n in G:
            if G.nodes[n]["label"] == "Q" or any(G.nodes[m]["label"] == "Q"
                                                 for m in G.neighbors(n)):
                H.add_node(n, label=G.nodes[n]["label"])
        for u, v in G.edges():
            if G.nodes[u]["label"] == "Q" or G.nodes[v]["label"] == "Q":
                H.add_edge(u, v)
        return H
    same_arch_i = iso(q_subgraph(Gi), q_subgraph(Ci))
    same_arch_j = iso(q_subgraph(Gj), q_subgraph(Cj))
    no_new_verts = (Ci.number_of_nodes() == Gi.number_of_nodes()
                    and Cj.number_of_nodes() == Gj.number_of_nodes())
    only_AA = all(Ci.nodes[u]["label"] == "A" and Ci.nodes[v]["label"] == "A"
                  for (u, v) in addi) and all(
                  Cj.nodes[u]["label"] == "A" and Cj.nodes[v]["label"] == "A"
                  for (u, v) in addj)
    require(same_arch_i and same_arch_j,
            "archive (Q vertices + Q-incident edges) UNCHANGED by contact (read-only)")
    require(no_new_verts, "contact created no new vertices (no fresh record built)")
    require(only_AA, "contact added only A-A edges among pre-existing actives "
                     "(latent relation made active; trace not transcribed)")

    log("=" * 76)
    log("[7] EXACT TRANSITION TABLE (rational probs; multiplicities retained)")
    rows = ["stage            state  #dirEv  ->  {activeSuccClass: mult}   probs"]
    for tag, Si, Sj in [("before-M1", Gi, Gj), ("after-CONTACT", Ci, Cj)]:
        pcl = _global_pcls([Si, Sj])
        for lab, S in ((f"{i}", Si), (f"{j}", Sj)):
            tot, mult, probs = proj_succ_dist(S, pcl)
            pstr = "{" + ", ".join(f"{c}:{probs[c]}" for c in sorted(probs)) + "}"
            rows.append(f"  {tag:<14} {lab:>3}    {tot:>2}    -> {mult}   {pstr}")
        rows.append("")
    with open(TABLE, "w") as f:
        f.write("\n".join(rows) + "\n")
    for r in rows:
        log("  " + r)

    log("=" * 76)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED: latent trace made conditionally relevant by a local "
            "read-only structural change; archive-blind controls show no effect.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

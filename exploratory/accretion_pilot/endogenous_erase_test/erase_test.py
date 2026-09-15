#!/usr/bin/env python3
"""
erase_test.py -- the ERASE test (Fable's proposal): after the archive has influenced the
active layer, DELETE the whole archive and ask whether the two lineages still differ in
their ARCHIVE-FREE future active law -- i.e. did the past leave a DURABLE mark on the active
"slice of now", or did its influence live only in the quiet record that erasure destroys?

Register: speculative exploration. Exact rational enumeration on ONE matched pair; a
mechanism test, not a sample of growing worlds. Isolated under
exploratory/accretion_pilot/endogenous_erase_test/; earlier work preserved. No merges /
publishing / sealed-study access. asserts + nonzero exit (printed text is not a gate).

Relation to prior work (stated honestly):
  * ../endogenous_active_projection/ : under BUD only, the active front is a CLOSED
    transition system; the quiet archive is causally INERT.
  * ../endogenous_local_contact/ : adding CONTACT (which reads a quiet mediator) makes the
    archive INFLUENCE the active layer -- the same "projected active successor distribution"
    that this file calls the ERASED slice already DIFFERS between the two matched lineages at
    1 and 2 events, WHILE the archive is present.
  * THIS file adds the part local_contact did not do: it actually DELETES the archive at a
    chosen horizon and then runs the future FORWARD with no archive (BUD only, so CONTACT is
    inert -- there are no quiet mediators left). Two questions, kept distinct:
      (Q1 durable mark)  With the archive deleted, do the two lineages STILL differ in the
                         active slice and hence in all archive-free future active law?
      (Q2 redundancy)    Is the archive REDUNDANT for the active future -- i.e. does deleting
                         it leave the future active-law distribution unchanged vs KEEPING it?
    Q1 tests Fable's "baked into the slice of now". Q2 tempers the stronger "the archive is
    redundant": if deleting the archive changes the future, the archive is NOT redundant --
    the durable mark and the still-live influence coexist.

THE MATCHED PAIR (reconstructed exactly as in ../endogenous_local_contact/): two classes
reachable by two BUDs from an all-active path of 4, with ISOMORPHIC active projections but
DIFFERENT archives (quiet-degree signatures (3,3) vs (2,3)). Verified below.

Rules & scheduler (unchanged): BUD(x,y) directed at k=1; CONTACT(a,q,b) with unordered
endpoint pair and distinct quiet mediators distinct; one step = uniform over INDIVIDUAL
eligible events. "extended" = BUD+CONTACT; "bud-only" = BUD alone. ERASE(G) deletes every
quiet vertex (keeps the active vertices and the active-active edges = the active projection).
"""
from __future__ import annotations
import os, sys, itertools
from collections import defaultdict
from fractions import Fraction as Fr
import networkx as nx
from networkx.algorithms.isomorphism import categorical_node_match

NM = categorical_node_match("label", None)
HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "erase_report.txt")
TABLE = os.path.join(HERE, "results", "erase_tables.txt")
LINES, FAILS = [], []

ERASE_H = 2      # evolve (pre-phase) this many events, then ERASE
FUT_K = 2        # then run the future this many events (archive-free for the ERASE process)


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


# --------------------------------------------------------------- graph helpers / rules
def wl(G):
    return nx.weisfeiler_lehman_graph_hash(G, node_attr="label", iterations=5)


def iso(G, H):
    return nx.is_isomorphic(G, H, node_match=NM)


def active_bonds(G):
    return [(u, v) for u, v in G.edges()
            if G.nodes[u]["label"] == "A" and G.nodes[v]["label"] == "A"]


def active_neighbours(G, q):
    return sorted(a for a in G.neighbors(q) if G.nodes[a]["label"] == "A")


def _fresh(G):
    return max([n for n in G.nodes if isinstance(n, int)] + [-1]) + 1


def bud(G, x, y):
    assert G.has_edge(x, y) and G.nodes[x]["label"] == "A" and G.nodes[y]["label"] == "A"
    H = G.copy(); H.nodes[y]["label"] = "Q"
    z = _fresh(H); H.add_node(z, label="A"); H.add_edge(x, z); H.add_edge(y, z)
    return H


def erase(G):
    """ERASE: delete every quiet vertex; keep active vertices + active-active edges."""
    P = G.subgraph([n for n in G if G.nodes[n]["label"] == "A"]).copy()
    for n in P:
        P.nodes[n]["label"] = "A"
    return P


proj = erase       # the active projection IS the erased slice


def path(n):
    G = nx.Graph()
    for k in range(n):
        G.add_node(k, label="A")
    for k in range(n - 1):
        G.add_edge(k, k + 1)
    return G


# ---- individual eligible events ----
def events_bud(G):
    out = []
    for u, v in active_bonds(G):
        out.append(("B", u, v)); out.append(("B", v, u))
    return out


def events_contact(G):
    out = []
    for q in [n for n in G if G.nodes[n]["label"] == "Q"]:
        an = active_neighbours(G, q)
        for a, b in itertools.combinations(an, 2):
            if not G.has_edge(a, b):
                out.append(("C", frozenset((a, b)), q))
    return out


def events_ext(G):
    return events_bud(G) + events_contact(G)


def apply_ev(G, ev):
    if ev[0] == "B":
        return bud(G, ev[1], ev[2])
    a, b = tuple(ev[1]); H = G.copy(); H.add_edge(a, b); return H


# --------------------------------------------------------------- matched pair (as before)
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
    for a in range(len(fulls)):
        for b in range(a + 1, len(fulls)):
            if iso(proj(fulls[a]), proj(fulls[b])) and not iso(fulls[a], fulls[b]):
                return a, b
    return None


# ----------------------------------------------- shared active-slice class index (growing)
REPS = []                    # master list of active-slice iso-class representatives


def cidx(P):
    for k, R in enumerate(REPS):
        if iso(P, R):
            return k
    REPS.append(P); return len(REPS) - 1


# --------------------------------- one process: pre-phase, (optional) ERASE at H, future
def run_process(G0, pre_ev, H, post_ev, K, do_erase):
    """Exact distribution over the ERASED-slice iso-class at every step 0..H+K.
    Steps 0..H-1 -> H use pre_ev; the ERASE (if do_erase) happens between step H and H+1;
    steps H..H+K-1 -> H+K use post_ev on the (possibly erased) graph."""
    dist = {s: defaultdict(lambda: Fr(0)) for s in range(H + K + 1)}

    def rec(G, prob, step):
        dist[step][cidx(proj(G))] += prob
        if step == H + K:
            return
        Gw = proj(G).copy() if (step == H and do_erase) else G
        ev = (pre_ev if step < H else post_ev)(Gw)
        n = len(ev)
        if n == 0:                                   # halted: carry current slice forward
            pk = cidx(proj(Gw))
            for s in range(step + 1, H + K + 1):
                dist[s][pk] += prob
            return
        for e in ev:
            rec(apply_ev(Gw, e), prob * Fr(1, n), step + 1)

    rec(G0, Fr(1), 0)
    return dist


def dist_eq(d1, d2):
    keys = set(d1) | set(d2)
    return all(d1.get(k, 0) == d2.get(k, 0) for k in keys)


def fmt(d):
    return "{" + ", ".join(f"{k}:{d[k]}" for k in sorted(d)) + "}"


def relabel(G, s):
    return nx.relabel_nodes(G, {n: (n + s if isinstance(n, int) else n) for n in G})


# ============================================================================ MAIN
def main():
    log("=" * 90)
    log("THE ERASE TEST -- delete the archive, then compare archive-free future active law")
    log("=" * 90)

    # ---- [0] reconstruct + verify the matched pair ----
    fulls = depth2_classes(); i, j = find_pair(fulls); Gi, Gj = fulls[i], fulls[j]
    log("[0] matched pair (same construction as ../endogenous_local_contact/)")
    log(f"  Gi: {dict(Gi.nodes(data='label'))}  edges "
        f"{sorted(map(tuple,(frozenset(e) for e in Gi.edges())))}")
    log(f"  Gj: {dict(Gj.nodes(data='label'))}  edges "
        f"{sorted(map(tuple,(frozenset(e) for e in Gj.edges())))}")
    require(iso(proj(Gi), proj(Gj)), "active projections are ISOMORPHIC (matched active layer)")
    require(not iso(Gi, Gj), "full graphs are NON-isomorphic (the archives differ)")
    require({q_sig(Gi), q_sig(Gj)} == {(3, 3), (2, 3)},
            "archives differ exactly as in local_contact: quiet-degree sigs (3,3) vs (2,3)")

    # ---- [1] ERASE is inert on its own, and inert under BUD-only ----
    log("=" * 90)
    log("[1] erasing by itself introduces no difference; under BUD-only the archive is inert")
    require(iso(erase(Gi), erase(Gj)),
            "ERASE(Gi) and ERASE(Gj) are isomorphic -- deleting the archive at step 0 leaves "
            "the two lineages identical (no difference is manufactured by erasure)")
    # BUD-only, erase at H, future BUD-only  ==  BUD-only, keep, future BUD-only (projected)
    null_erase_i = run_process(Gi, events_bud, ERASE_H, events_bud, FUT_K, True)
    null_keep_i = run_process(Gi, events_bud, ERASE_H, events_bud, FUT_K, False)
    require(all(dist_eq(null_erase_i[s], null_keep_i[s]) for s in null_erase_i),
            "under BUD-only, deleting vs keeping the archive gives the SAME active-slice "
            "distribution at every step (erasing an inert archive changes nothing)")

    # ---- [2] the three processes for each lineage ----
    log("=" * 90)
    log(f"[2] three processes (pre-phase = {ERASE_H} events, then future = {FUT_K} events):")
    log("    NULL   : BUD-only, ERASE at H, BUD-only future   (archive never mattered)")
    log("    ERASE  : extended, ERASE at H, BUD-only future    (archive deleted; Q1 durable?)")
    log("    KEEP   : extended, no erase, extended future      (archive retained; Q2 redundant?)")
    P = {}
    for lab, G in (("i", Gi), ("j", Gj)):
        P[("NULL", lab)] = run_process(G, events_bud, ERASE_H, events_bud, FUT_K, True)
        P[("ERASE", lab)] = run_process(G, events_ext, ERASE_H, events_bud, FUT_K, True)
        P[("KEEP", lab)] = run_process(G, events_ext, ERASE_H, events_ext, FUT_K, False)

    # normalisation
    norm_ok = all(sum(P[key][s].values()) == 1 for key in P for s in P[key])
    require(norm_ok, "every distribution sums to exactly 1 (normalisation) at every step")

    rows = ["process  lineage  step  distribution over ERASED-slice iso-classes"]
    for proc in ("NULL", "ERASE", "KEEP"):
        for lab in ("i", "j"):
            for s in range(ERASE_H + FUT_K + 1):
                tag = "  <-ERASE here" if (s == ERASE_H and proc in ("NULL", "ERASE")) else ""
                rows.append(f"{proc:<7}  {lab}       {s}    {fmt(P[(proc,lab)][s])}{tag}")
            rows.append("")
    with open(TABLE, "w") as f:
        f.write("\n".join(rows) + "\n")
    for r in rows:
        log("  " + r)

    # ---- [3] Q1: durable mark -- with the archive DELETED, do the lineages still differ? --
    log("=" * 90)
    log("[3] Q1 (durable mark): archive deleted at H, then archive-free (BUD-only) future")
    require(dist_eq(P[("NULL", "i")][ERASE_H + FUT_K], P[("NULL", "j")][ERASE_H + FUT_K]),
            "NULL control: lineages are IDENTICAL at every step (BUD-only never lets the "
            "archive matter, so erasure has nothing to reveal) -- the matched null")
    require(dist_eq(P[("ERASE", "i")][0], P[("ERASE", "j")][0]),
            "ERASE at step 0: lineages identical (matched active layer)")
    # first step at which the archive-deleted lineages diverge
    first_div = next((s for s in range(ERASE_H + FUT_K + 1)
                      if not dist_eq(P[("ERASE", "i")][s], P[("ERASE", "j")][s])), None)
    log(f"  ERASE process: first step at which lineages i,j DIVERGE = {first_div}")
    require(first_div is not None and first_div <= ERASE_H,
            f"the erased SLICE already differs by the erase horizon H={ERASE_H} "
            f"(divergence first at step {first_div}) -- the archive's influence is "
            f"transcribed into the active layer BEFORE deletion")
    require(not dist_eq(P[("ERASE", "i")][ERASE_H + FUT_K],
                        P[("ERASE", "j")][ERASE_H + FUT_K]),
            f"AFTER deleting the archive, the two lineages STILL differ at the final step "
            f"{ERASE_H+FUT_K} under archive-free (BUD-only) future evolution -- Q1: the past "
            f"left a DURABLE mark on the active slice; future active law differs with NO "
            f"archive present")

    # ---- [4] Q2: redundancy -- does DELETING the archive change the active future? ----
    log("=" * 90)
    log("[4] Q2 (redundancy): compare ERASE (archive deleted) vs KEEP (archive retained)")
    # at step H the two agree (ERASE = proj(KEEP)); after H they may diverge
    agreeH = all(dist_eq(P[("ERASE", lab)][ERASE_H], P[("KEEP", lab)][ERASE_H])
                 for lab in ("i", "j"))
    require(agreeH, "at the erase horizon H, ERASE and KEEP agree per lineage "
                    "(ERASE(state) = active projection of the kept state)")
    redundant = all(dist_eq(P[("ERASE", lab)][s], P[("KEEP", lab)][s])
                    for lab in ("i", "j") for s in range(ERASE_H, ERASE_H + FUT_K + 1))
    log(f"  archive redundant for the active future (ERASE == KEEP after H)? {redundant}")
    require(not redundant,
            "deleting the archive DOES change the active-future distribution (ERASE != KEEP "
            "after H) -- Q2: the archive is NOT redundant; a retained archive keeps feeding "
            "the active layer via CONTACT. (Durable mark and still-live influence coexist.)")

    # ---- [5] relabelling invariance ----
    log("=" * 90)
    log("[5] nontrivial relabelling invariance of the ERASE-process distributions")
    rel_ok = True
    for lab, G in (("i", Gi), ("j", Gj)):
        base = P[("ERASE", lab)]
        rel = run_process(relabel(G, 200), events_ext, ERASE_H, events_bud, FUT_K, True)
        if not all(dist_eq(base[s], rel[s]) for s in base):
            rel_ok = False
    require(rel_ok, "ERASE-process distributions unchanged under a nontrivial relabelling "
                    "(vertex identities used for measurement/erasure only, never for selection)")

    log("=" * 90)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    log("Reading: (Q1) the archive's influence is written into the active slice via CONTACT "
        "and SURVIVES total deletion of the archive -- the two lineages differ in their "
        "archive-free future active law, so the past is (partly) baked into the 'slice of "
        "now'. (Q2) BUT deleting the archive still changes the active future vs keeping it, "
        "so the archive is NOT redundant. One matched pair, small horizon, a designed CONTACT "
        "coupling, uniform-over-events scheduler -- a mechanism test, not a claim about "
        "generic worlds.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

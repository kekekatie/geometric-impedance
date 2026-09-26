#!/usr/bin/env python3
"""
contact_timing_checks.py -- delayed consultation vs newly enabled relevance, under the
UNCHANGED extended rule set (BUD at k=1  ∪  local CONTACT), uniform selection over the
union. No model change.

ANALYTIC CLAIM (proved below, asserted on all enumerated transitions):
  For a quiet vertex q (deposition complete), let
     C_q(G) = { {a,b} : a,b distinct ACTIVE neighbours of q in G, edge a-b ABSENT }.
  Then for every single event G -> G' (BUD or CONTACT):   C_q(G') ⊆ C_q(G).
  I.e. an existing quiet vertex's CONTACT menu is monotone non-increasing.

Why (present rules): (i) once q is quiet its incident edges are frozen, so q's neighbour
SET is fixed; a neighbour can only lose active status (A->Q via BUD), never gain it (no
Q->A), so q's ACTIVE-neighbour set only shrinks; (ii) edges are only ever added, so an
absent a-b can only become present. Both conditions defining membership in C_q can only
fail, never newly hold. Hence no new pair enters C_q. QED.

Persistent vertex identities are used ONLY to track this observable -- never as inputs to
event selection (uniform over the event union) and never as a memory decoder.

Exact rationals; asserts + nonzero exit (printed text is not a gate).
"""
from __future__ import annotations
import os, sys, itertools
from fractions import Fraction
import networkx as nx
from networkx.algorithms.isomorphism import categorical_node_match

NM = categorical_node_match("label", None)
HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "timing_report.txt")
TABLE = os.path.join(HERE, "results", "timing_table.txt")
LINES, FAILS = [], []
HORIZON = 3


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


# --------------------------------------------------------------- graph + events
def iso(G, H):
    return nx.is_isomorphic(G, H, node_match=NM)


def active_bonds(G):
    return [(u, v) for u, v in G.edges()
            if G.nodes[u]["label"] == "A" and G.nodes[v]["label"] == "A"]


def _fresh(G):
    return (max([n for n in G.nodes if isinstance(n, int)] + [-1]) + 1)


def bud(G, x, y):
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


def active_neighbours(G, q):
    return sorted(a for a in G.neighbors(q) if G.nodes[a]["label"] == "A")


def C_q(G, q):
    """CONTACT menu mediated by quiet q: unordered active-neighbour pairs lacking an edge."""
    an = active_neighbours(G, q)
    return {frozenset((a, b)) for a, b in itertools.combinations(an, 2)
            if not G.has_edge(a, b)}


def events_bud(G):
    out = []
    for u, v in active_bonds(G):
        out.append(("B", u, v)); out.append(("B", v, u))
    return out


def events_contact(G):
    out = []
    for q in [n for n in G if G.nodes[n]["label"] == "Q"]:
        for a, b in itertools.combinations(active_neighbours(G, q), 2):
            if not G.has_edge(a, b):
                out.append(("C", frozenset((a, b)), q))
    return out


def events_ext(G):
    return events_bud(G) + events_contact(G)


def apply_ev(G, ev):
    if ev[0] == "B":
        return bud(G, ev[1], ev[2])
    a, b = tuple(ev[1]); H = G.copy(); H.add_edge(a, b); return H


def quiets(G):
    return [n for n in G if G.nodes[n]["label"] == "Q"]


# --------------------------------------------------------------- matched pair
def depth2_classes():
    seed = path(4); reps = []
    for e1 in events_bud(seed):
        G1 = bud(seed, e1[1], e1[2])
        for e2 in events_bud(G1):
            G2 = bud(G1, e2[1], e2[2])
            if not any(iso(G2, R) for R in reps):
                reps.append(G2)
    return reps


def find_pair(reps):
    def proj(G):
        P = G.subgraph([n for n in G if G.nodes[n]["label"] == "A"]).copy()
        for n in P:
            P.nodes[n]["label"] = "A"
        return P
    for i in range(len(reps)):
        for j in range(i + 1, len(reps)):
            if iso(proj(reps[i]), proj(reps[j])) and not iso(reps[i], reps[j]):
                return i, j
    return None


# --------------------------------------------------------------- path enumeration
def paths(G, h):
    if h == 0:
        yield [], G, Fraction(1)
        return
    evs = events_ext(G); n = len(evs)
    for e in evs:
        G1 = apply_ev(G, e)
        for seq, Gf, p in paths(G1, h - 1):
            yield [e] + seq, Gf, Fraction(1, n) * p


def classify(seq, Gf, initial_Q):
    """consulted: a CONTACT with mediator in initial_Q fired; else waiting/gone by whether
    any initial-Q vertex still has a nonempty menu."""
    consulted = any(e[0] == "C" and e[2] in initial_Q for e in seq)
    if consulted:
        return "consulted"
    remaining = any(len(C_q(Gf, q)) > 0 for q in initial_Q)
    return "waiting" if remaining else "gone"


# --------------------------------------------------------------- checks
def check_monotonicity():
    log("=" * 76)
    log("[A] MONOTONICITY  C_q(G') ⊆ C_q(G)  on all enumerated transitions (<=3 events)")
    reps = depth2_classes(); i, j = find_pair(reps)
    ok = True; n_trans = 0; n_q = 0
    for G0 in (reps[i], reps[j]):
        for seq, Gf, p in paths(G0, HORIZON):
            G = G0
            for e in seq:
                G1 = apply_ev(G, e)
                for q in quiets(G):                 # q already quiet in G (deposition done)
                    n_q += 1
                    if not C_q(G1, q).issubset(C_q(G, q)):
                        ok = False
                n_trans += 1
                G = G1
    require(ok, f"C_q(G')⊆C_q(G) for every (transition, pre-existing quiet q): "
                f"{n_q} checks over {n_trans} transitions")
    return reps, i, j


def timing_table(reps, i, j):
    log("=" * 76)
    log("[B] EXACT TIMING (next 3 events; uniform BUD∪CONTACT; initial archive tracked)")
    rows = ["state  horizon   P(consulted)      P(waiting)        P(gone)          sum"]
    per_state = {}
    for lab, G0 in ((str(i), reps[i]), (str(j), reps[j])):
        initial_Q = set(quiets(G0))
        menus = {q: C_q(G0, q) for q in initial_Q}
        n_opp = sum(len(m) for m in menus.values())
        log(f"  state {lab}: initial quiet vertices {sorted(initial_Q)}; "
            f"initial menus { {q: sorted(map(tuple, m)) for q, m in menus.items()} } "
            f"({n_opp} opportunity/ies)")
        per_state[lab] = {}
        for h in (1, 2, 3):
            acc = {"consulted": Fraction(0), "waiting": Fraction(0), "gone": Fraction(0)}
            for seq, Gf, p in paths(G0, h):
                acc[classify(seq, Gf, initial_Q)] += p
            s = acc["consulted"] + acc["waiting"] + acc["gone"]
            per_state[lab][h] = (acc, s)
            rows.append(f"  {lab:>3}     {h}       {str(acc['consulted']):<16} "
                        f"{str(acc['waiting']):<16} {str(acc['gone']):<15} {s}")
        rows.append("")
    with open(TABLE, "w") as f:
        f.write("\n".join(rows) + "\n")
    for r in rows:
        log("  " + r)
    # normalisation
    norm_ok = all(s == 1 for lab in per_state for (_, s) in per_state[lab].values())
    require(norm_ok, "the three categories partition probability 1 at every horizon")
    # consulted mass is non-decreasing in horizon (delayed consultation accumulates)
    mono_c = all(per_state[lab][1][0]["consulted"] <= per_state[lab][2][0]["consulted"]
                 <= per_state[lab][3][0]["consulted"] for lab in per_state)
    require(mono_c, "P(consulted) is non-decreasing in the horizon")
    return per_state


def check_removal_modes(reps, i, j):
    log("=" * 76)
    log("[C] REMOVAL MODES of an initial opportunity (endpoint-quieting vs edge-added)")
    # A BUD can only add edges to NEW tips, so a pre-existing pair's edge is only ever
    # added by a CONTACT (through SOME mediator). Endpoint quieting is only via BUD.
    log("  (structural: BUD never adds an edge between two pre-existing actives, so an")
    log("   opportunity's a-b edge can be added only by a CONTACT; endpoint quieting is")
    log("   only by BUD. A CONTACT via a DIFFERENT mediator removes it without selecting")
    log("   the original mediator.)")
    modes = {"quiet": None, "edge_other": None}
    for lab, G0 in ((str(i), reps[i]), (str(j), reps[j])):
        initial_Q = set(quiets(G0))
        init_opps = {(q, fp) for q in initial_Q for fp in C_q(G0, q)}
        for seq, Gf, p in paths(G0, HORIZON):
            if any(e[0] == "C" and e[2] in initial_Q for e in seq):
                continue                     # consulted paths excluded
            # walk, watch each initial opportunity vanish and why
            G = G0
            for e in seq:
                G1 = apply_ev(G, e)
                for (q, fp) in init_opps:
                    a, b = tuple(fp)
                    was = fp in C_q(G, q); now = fp in C_q(G1, q)
                    if was and not now:
                        if G1.nodes[a]["label"] == "Q" or G1.nodes[b]["label"] == "Q":
                            if modes["quiet"] is None:
                                modes["quiet"] = (lab, seq, (a, b), "endpoint quieted")
                        elif e[0] == "C":
                            if modes["edge_other"] is None:
                                modes["edge_other"] = (lab, seq, (a, b),
                                                       f"edge added by CONTACT via mediator {e[2]}")
                G = G1
    for name, m in modes.items():
        if m:
            lab, seq, ab, why = m
            log(f"  mode '{name}': state {lab}, opportunity {ab} removed -- {why}; "
                f"path { [ (e[0], (tuple(e[1]) if e[0]=='C' else (e[1],e[2])), (e[2] if e[0]=='C' else '')) for e in seq] }")
        else:
            log(f"  mode '{name}': not observed within {HORIZON} events (reported as-is)")
    require(modes["quiet"] is not None or modes["edge_other"] is not None,
            "at least one removal-without-consultation mode is exhibited (or reported absent)")


def check_relabel(reps, i, j):
    log("=" * 76)
    log("[D] relabelling invariance of the timing partition")
    def timing(G0):
        initial_Q = set(quiets(G0)); out = {}
        for h in (1, 2, 3):
            acc = {"consulted": Fraction(0), "waiting": Fraction(0), "gone": Fraction(0)}
            for seq, Gf, p in paths(G0, h):
                acc[classify(seq, Gf, initial_Q)] += p
            out[h] = acc
        return out
    ok = True
    for G0 in (reps[i], reps[j]):
        Gr = nx.relabel_nodes(G0, {n: n + 100 for n in G0})
        if timing(G0) != timing(Gr):
            ok = False
    require(ok, "timing partition unchanged under nontrivial vertex relabelling "
               "(identities used only for tracking, not selection)")


def main():
    reps, i, j = check_monotonicity()
    timing_table(reps, i, j)
    check_removal_modes(reps, i, j)
    check_relabel(reps, i, j)
    log("=" * 76)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

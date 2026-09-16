#!/usr/bin/env python3
"""
present_width.py -- "how much of the past survives in the present, and for how long?"

Katie's reframing: only the PRESENT moment actually exists; it rides a moving expansion front
and carries an inherited MOMENTUM from its history -- the past itself need not still exist.
The ERASE test (../endogenous_erase_test/) showed the ENSEMBLE of presents stays biased by
lineage after the archive is deleted. IMPORTANT -- this is an ENSEMBLE (distribution)
statement, never a per-world record: a single active graph is a class BOTH lineages produce;
what differs is the probability DISTRIBUTION over presents (a bias, the same status as AUC in
Study A). "The present does not remember; the present is biased." This study QUANTIFIES that
bias:

  Part 1 -- HOW MUCH survives.  At each horizon, how much of the historically-distinguishing
    information is readable from the PRESENT ALONE (active slice) versus from the FULL state
    (active + archive)?  rho(h) = D_slice(h) / D_full(h) in [0,1] is the surviving fraction.
    (Also in bits, via Jensen-Shannon / mutual information of the lineage label.)

  Part 2 -- FADE or SET, and the WIDTH of "now".  Imprint history to horizon H (archive
    present), then DELETE the archive and let the present coast (BUD-only future). The coasting
    law is a single fixed Markov kernel on PROJECTIONS -- well-defined only by Proposition 1
    (../endogenous_active_projection/) -- applied to BOTH lineages, so the DATA-PROCESSING
    INEQUALITY forces the lineage distinguishability to be NON-INCREASING in the archive-free
    future: the ensemble bias can only FADE or HOLD, never grow. It converges to the EXACT
    positive limit of Proposition 3 (coast_asymptote.py) -- so a positive bias PERSISTS with no
    past at all. With KEEP (archive retained) distinguishability instead stays >= the coast at
    every TESTED step -- keeping the past holds the distinction ABOVE the floor over the tested
    interval (not "sustains" it; the floor is self-sustaining). The archive-free
    decay-to-a-limit is the temporal "width of now".

Register: speculative exploration; exact rational distributions on ONE matched pair (the same
as ../endogenous_local_contact/ and ../endogenous_erase_test/), a mechanism test not a sample.
Isolated; earlier work preserved; no merges/publishing/sealed-study access. asserts + nonzero
exit. Distributions are EXACT rationals; only the bit-valued entropies are floating readouts
of those exact numbers (clearly marked).
"""
from __future__ import annotations
import os, sys, math, itertools
from collections import defaultdict
from fractions import Fraction as Fr
import networkx as nx
from networkx.algorithms.isomorphism import categorical_node_match

NM = categorical_node_match("label", None)
HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "present_width_report.txt")
TABLE = os.path.join(HERE, "results", "present_width_tables.txt")
LINES, FAILS = [], []


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


# ------------------------------------------------------------- graph helpers / rules
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
    P = G.subgraph([n for n in G if G.nodes[n]["label"] == "A"]).copy()
    for n in P:
        P.nodes[n]["label"] = "A"
    return P


def path(n):
    G = nx.Graph()
    for k in range(n):
        G.add_node(k, label="A")
    for k in range(n - 1):
        G.add_edge(k, k + 1)
    return G


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


# ------------------------------------------------------------- matched pair
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
            if iso(erase(fulls[a]), erase(fulls[b])) and not iso(fulls[a], fulls[b]):
                return a, b
    return None


# ------------------------------------------- shared iso-class indices (full & slice)
# Each store is (reps_list, wl_buckets): WL-hash buckets first, exact iso only within a
# bucket (exactness preserved; avoids an O(#classes) iso scan per node).
REPS_FULL = ([], {})
REPS_SLICE = ([], {})


def cidx(store, X):
    reps, buckets = store
    h = wl(X)
    for k in buckets.get(h, ()):
        if iso(X, reps[k]):
            return k
    reps.append(X); buckets.setdefault(h, []).append(len(reps) - 1)
    return len(reps) - 1


# ------------------------------------------- one process -> full & slice distributions
def run_process(G0, pre_ev, H, post_ev, K, do_erase):
    """Distributions over FULL-state and ERASED-slice iso-classes at every step 0..H+K."""
    full = {s: defaultdict(lambda: Fr(0)) for s in range(H + K + 1)}
    slice_ = {s: defaultdict(lambda: Fr(0)) for s in range(H + K + 1)}

    def rec(G, prob, step):
        full[step][cidx(REPS_FULL, G)] += prob
        slice_[step][cidx(REPS_SLICE, erase(G))] += prob
        if step == H + K:
            return
        Gw = erase(G).copy() if (step == H and do_erase) else G
        ev = (pre_ev if step < H else post_ev)(Gw)
        n = len(ev)
        if n == 0:
            fk, sk = cidx(REPS_FULL, Gw), cidx(REPS_SLICE, erase(Gw))
            for s in range(step + 1, H + K + 1):
                full[s][fk] += prob; slice_[s][sk] += prob
            return
        for e in ev:
            rec(apply_ev(Gw, e), prob * Fr(1, n), step + 1)

    rec(G0, Fr(1), 0)
    return full, slice_


# ------------------------------------------------------------- distinguishability measures
def tv(d1, d2):
    keys = set(d1) | set(d2)
    return sum(abs(d1.get(k, Fr(0)) - d2.get(k, Fr(0))) for k in keys) * Fr(1, 2)


def _H_bits(d):
    s = 0.0
    for v in d.values():
        p = float(v)
        if p > 0:
            s -= p * math.log2(p)
    return s


def jsd_bits(d1, d2):
    """Jensen-Shannon divergence in bits = mutual information I(lineage; observation) for a
    uniform prior over the two lineages. In [0,1]. Exact inputs, floating readout."""
    keys = set(d1) | set(d2)
    m = {k: (d1.get(k, Fr(0)) + d2.get(k, Fr(0))) * Fr(1, 2) for k in keys}
    return _H_bits(m) - 0.5 * _H_bits(d1) - 0.5 * _H_bits(d2)


def relabel(G, s):
    return nx.relabel_nodes(G, {n: (n + s if isinstance(n, int) else n) for n in G})


# ============================================================================ MAIN
def main():
    log("=" * 92)
    log("PRESENT WIDTH -- how much of the past survives in the present, and for how long")
    log("=" * 92)
    fulls = depth2_classes(); i, j = find_pair(fulls); Gi, Gj = fulls[i], fulls[j]
    require(iso(erase(Gi), erase(Gj)) and not iso(Gi, Gj)
            and {q_sig(Gi), q_sig(Gj)} == {(3, 3), (2, 3)},
            "matched pair: iso active projections, different archives (3,3) vs (2,3)")

    # ================= PART 1: how much survives (present vs full) =================
    log("=" * 92)
    log("[Part 1] surviving fraction rho(h) = present-only / full-state distinguishability")
    H1 = 3
    fi, si = run_process(Gi, events_ext, H1, events_ext, 0, False)
    fj, sj = run_process(Gj, events_ext, H1, events_ext, 0, False)
    rows1 = ["h  D_full(TV)  D_slice(TV)  rho=slice/full   I_full(bits)  I_slice(bits)  "
             "bit-frac"]
    part1 = {}
    for h in range(H1 + 1):
        Df, Ds = tv(fi[h], fj[h]), tv(si[h], sj[h])
        If, Is = jsd_bits(fi[h], fj[h]), jsd_bits(si[h], sj[h])
        rho = (Ds / Df) if Df != 0 else Fr(0)
        bitfrac = (Is / If) if If > 1e-12 else 0.0
        part1[h] = (Df, Ds, rho, If, Is)
        rows1.append(f"{h}  {float(Df):.4f}      {float(Ds):.4f}      "
                     f"{float(rho):.4f}          {If:.4f}        {Is:.4f}        "
                     f"{bitfrac:.4f}")
    for r in rows1:
        log("  " + r)
    # present carries no more than the full state; and at h=0 the present carries NOTHING
    require(all(part1[h][1] <= part1[h][0] for h in range(H1 + 1)),
            "present-only distinguishability <= full-state distinguishability at every horizon "
            "(the present can never carry MORE memory than active+archive together)")
    require(part1[0][1] == 0 and part1[0][0] == 1,
            "at h=0 the present carries NONE of the distinction (identical slices) while the "
            "full state carries ALL of it (rho=0): the memory starts entirely in the archive")
    require(part1[H1][1] > 0 and part1[H1][2] > 0,
            f"by h={H1} the present alone carries a POSITIVE share of the distinguishing bias "
            f"(rho={float(part1[H1][2]):.3f}): CONTACT progressively transcribes the past into "
            f"the present")
    require(part1[H1][2] < 1,
            "rho < 1: the lineages stay only PARTLY separable from the present alone -- some of "
            "the distinction is legible only WITH the archive (consistent with 'archive not "
            "redundant')")

    # ================= PART 2: fade or set / width of now =================
    log("=" * 92)
    log("[Part 2] imprint to H, then DELETE the past and coast (BUD-only) vs KEEP (extended)")
    H, K = 2, 3
    # archive-free future (ERASE at H, BUD-only): the present coasts on inherited momentum
    ef_i = run_process(Gi, events_ext, H, events_bud, K, True)[1]
    ef_j = run_process(Gj, events_ext, H, events_bud, K, True)[1]
    # archive-retained future (KEEP, extended throughout)
    kp_i = run_process(Gi, events_ext, H, events_ext, K, False)[1]
    kp_j = run_process(Gj, events_ext, H, events_ext, K, False)[1]

    rows2 = ["step  archive-free D_slice (coasting)   archive-kept D_slice (KEEP)"]
    coast = {}; kept = {}
    for s in range(H + K + 1):
        coast[s] = tv(ef_i[s], ef_j[s]); kept[s] = tv(kp_i[s], kp_j[s])
        marker = "   <- archive deleted here" if s == H else ""
        rows2.append(f"{s}     {float(coast[s]):.4f}                          "
                     f"{float(kept[s]):.4f}{marker}")
    for r in rows2:
        log("  " + r)
    with open(TABLE, "w") as f:
        f.write("\n".join(rows1) + "\n\n" + "\n".join(rows2) + "\n")

    # (a) provable: coasting distinguishability is NON-INCREASING (data-processing inequality)
    nonincreasing = all(coast[s + 1] <= coast[s] for s in range(H, H + K))
    require(nonincreasing,
            "archive-free future: lineage distinguishability is NON-INCREASING after deletion "
            "(a single fixed BUD-only kernel on PROJECTIONS -- well-defined only by Proposition "
            "1 -- applied to both lineages -> data-processing inequality; the archive-free "
            "ensemble bias can only FADE or HOLD, never grow)")

    # (b) width of now within the horizon: does the coast fade, or set (hold)?
    drop = coast[H] - coast[H + K]
    verdict = ("HOLDS (no measurable fade within horizon)" if drop == 0
               else f"fades by {float(drop):.4f} over {K} archive-free steps")
    log(f"  width-of-now (archive-free): D_slice at deletion = {float(coast[H]):.4f}; "
        f"after {K} coasting steps = {float(coast[H+K]):.4f} -> {verdict} "
        f"(exact positive limit L = 4321/44100 ~= 0.0980 by Proposition 3, coast_asymptote.py)")
    require(coast[H] > 0, "at deletion the ensemble of presents is already biased by lineage "
                          "(nonzero distinguishability with the past gone)")

    # (c) sustaining the bias REQUIRES the past: KEEP stays at or above the archive-free coast
    keep_ge = all(kept[s] >= coast[s] for s in range(H + K + 1))
    require(keep_ge,
            "archive-retained future stays >= the archive-free coast at every TESTED step "
            "(steps 0..H+K) (KEEP >= ERASE; KEEP is non-monotone here -- "
            "0.147->0.151->0.151->0.147, one uptick then decline; >= is NOT established for all "
            "future times). The archive-free coast persists at its positive floor with NO past; "
            "keeping the past holds the distinction ABOVE that floor over the tested interval")

    # (d) NULL: without CONTACT nothing to measure
    nf_i = run_process(Gi, events_bud, H, events_bud, K, True)[1]
    nf_j = run_process(Gj, events_bud, H, events_bud, K, True)[1]
    require(all(tv(nf_i[s], nf_j[s]) == 0 for s in range(H + K + 1)),
            "NULL (BUD-only throughout): distinguishability is 0 at every step -- no CONTACT, "
            "no momentum to inherit (matched null)")

    # ---- relabelling invariance of the coast curve ----
    ef_ir = run_process(relabel(Gi, 300), events_ext, H, events_bud, K, True)[1]
    require(all(tv(ef_ir[s], ef_j[s]) == coast[s] for s in range(H + K + 1)),
            "coasting distinguishability unchanged under nontrivial relabelling")

    log("=" * 92)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    log("Reading: this is an ENSEMBLE statement -- a single active graph is a class BOTH "
        "lineages produce; only the DISTRIBUTION over presents differs (a bias, like AUC in "
        "Study A, never a per-world record; the present does not remember, the present is "
        "biased). (1) At h=0 the ensemble of presents is UNbiased by lineage (rho=0); rho rises "
        "as CONTACT transcribes the archive into active structure but stays < 1 (the present is "
        "only partly separable; the rest of the distinction is still in the past). (2) Once the "
        "past is deleted the archive-free bias can only fade or hold (data-processing on the "
        "projection kernel, Prop 1), converging to the exact positive limit of Proposition 3 "
        "-- so a positive bias PERSISTS with no past at all; with the archive kept, "
        "distinguishability stays >= the coast at every tested step (keeping the past holds the "
        "distinction ABOVE the floor over the tested interval). One matched pair, small "
        "horizon, a designed CONTACT coupling "
        "-- a mechanism test, not a claim about generic worlds.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

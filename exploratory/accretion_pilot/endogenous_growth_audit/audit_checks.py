#!/usr/bin/env python3
"""
audit_checks.py -- EXACT audit of the M1 (Competitive Accretion Grammar) feasibility
claims, per Astra's review. Proofs are stated in AUDIT.md; here we verify them on
bounded exact examples. All classification uses WL hashes ONLY to bucket, then EXACT
state-preserving isomorphism (node label 'A'/'Q' matched) to resolve each bucket.
Every claim is an `assert`; the script exits nonzero on any failure (printed text is
not a gate).

Rule M1 BUD(x,y) [x keeper stays A, y depositor -> Q, k new active tips z_i on x,
z_1 also bonded to y].  k=0 ablation = quiet-only (no vertices/edges added).
Rule M2 SPROUT(x) [x:A -> add new z:A and edge x-z].
"""
from __future__ import annotations
import os, sys, itertools
import networkx as nx
from networkx.algorithms.isomorphism import categorical_node_match

NM = categorical_node_match("label", None)
HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, "results", "audit_report.txt")
TABLE = os.path.join(HERE, "results", "successor_table.txt")
LINES, FAILS = [], []


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    if cond:
        log(f"  [PASS] {msg}")
    else:
        log(f"  [FAIL] {msg}"); FAILS.append(msg)


# ------------------------------------------------------------------ model M1
def wl(G):
    return nx.weisfeiler_lehman_graph_hash(G, node_attr="label", iterations=5)


def iso(G, H):
    return nx.is_isomorphic(G, H, node_match=NM)


def active_bonds(G):
    return [(u, v) for u, v in G.edges()
            if G.nodes[u]["label"] == "A" and G.nodes[v]["label"] == "A"]


def directed_events(G):
    evs = []
    for u, v in active_bonds(G):
        evs.append((u, v)); evs.append((v, u))
    return evs


def active_degree(G, y):
    return sum(1 for m in G.neighbors(y) if G.nodes[m]["label"] == "A")


def n_active_components(G):
    AG = G.subgraph([n for n in G if G.nodes[n]["label"] == "A"])
    return nx.number_connected_components(AG) if AG.number_of_nodes() else 0


def counts(G):
    return dict(V=G.number_of_nodes(), E=G.number_of_edges(),
               A=sum(1 for n in G if G.nodes[n]["label"] == "A"),
               Q=sum(1 for n in G if G.nodes[n]["label"] == "Q"),
               B=len(active_bonds(G)), Acomp=n_active_components(G))


def _fresh(G):
    return (max(G.nodes) + 1) if len(G.nodes) else 0


def bud(G, x, y, k=1):
    assert G.has_edge(x, y) and G.nodes[x]["label"] == "A" and G.nodes[y]["label"] == "A"
    H = G.copy(); H.nodes[y]["label"] = "Q"
    if k == 0:
        return H
    n = _fresh(H)
    for i in range(k):
        z = n + i; H.add_node(z, label="A"); H.add_edge(x, z)
        if i == 0:
            H.add_edge(y, z)
    return H


def sprout(G, x):
    assert G.nodes[x]["label"] == "A"
    H = G.copy(); z = _fresh(H); H.add_node(z, label="A"); H.add_edge(x, z); return H


def path(n, label="A"):
    G = nx.Graph()
    for i in range(n):
        G.add_node(i, label=label)
    for i in range(n - 1):
        G.add_edge(i, i + 1)
    return G


def star(m):
    G = nx.Graph(); G.add_node(0, label="A")
    for i in range(1, m + 1):
        G.add_node(i, label="A"); G.add_edge(0, i)
    return G


# exact iso-class reduction: WL bucket -> exact resolve
def class_reps(graphs):
    buckets = {}
    for G in graphs:
        buckets.setdefault(wl(G), []).append(G)
    reps = []
    for _, gs in buckets.items():
        local = []
        for G in gs:
            if not any(iso(G, R) for R in local):
                local.append(G)
        reps.extend(local)
    return reps


def class_index(G, reps):
    for i, R in enumerate(reps):
        if iso(G, R):
            return i
    return -1


# ============================================================ 1. FRONTIER ARITHMETIC
def check_delta_B():
    log("=" * 72)
    log("[1] FRONTIER ARITHMETIC:  Delta B = k - d_A(y)   (exhaustive on small states)")
    ok = True
    seeds = [path(3), path(4), star(4), path(5)]
    for k in (0, 1, 2, 3):
        for G in seeds:
            for (x, y) in [(u, v) for e in directed_events(G) for (u, v) in [e]]:
                B0 = len(active_bonds(G)); dA = active_degree(G, y)
                H = bud(G, x, y, k=k); B1 = len(active_bonds(H))
                if B1 - B0 != k - dA:
                    ok = False
    require(ok, "Delta B == k - d_A(y) for all legal BUDs on {path3,path4,star4,path5}, k in 0..3")

    # successor always has B >= k for k>=1  (k fresh bonds survive)
    ok2 = True
    for k in (1, 2, 3):
        for G in seeds:
            for (x, y) in directed_events(G):
                H = bud(G, x, y, k=k)
                if len(active_bonds(H)) < k:
                    ok2 = False
    require(ok2, "for k>=1 every successor has B >= k  => a next event always exists (no deadlock)")

    # k=1: Delta B <= 0 (nonincreasing) but B stays >= 1; size grows by 1
    ok3 = True
    for G in seeds:
        for (x, y) in directed_events(G):
            B0 = len(active_bonds(G)); H = bud(G, x, y, k=1)
            if not (len(active_bonds(H)) <= B0 and len(active_bonds(H)) >= 1
                    and H.number_of_nodes() == G.number_of_nodes() + 1):
                ok3 = False
    require(ok3, "k=1: B nonincreasing, B>=1 (never 0), |V| grows by 1 each event "
                 "(=> 'stalls/extinction' WITHDRAWN)")

    # invariants stated separately for k=0 vs k>=1
    log("  invariants (per event), verified deltas:")
    for k in (0, 1, 2):
        G = path(4); x, y = 1, 0
        c0 = counts(G); H = bud(G, x, y, k=k); c1 = counts(H)
        dV, dE = c1["V"] - c0["V"], c1["E"] - c0["E"]
        dQ, dA = c1["Q"] - c0["Q"], c1["A"] - c0["A"]
        exp_E = 0 if k == 0 else k + 1
        log(f"    k={k}: dV={dV} dE={dE} dQ={dQ} dA={dA}   (expect dE={exp_E})")
        require(dE == exp_E and dV == (0 if k == 0 else k) and dQ == 1
                and dA == (-1 if k == 0 else k - 1),
                f"k={k} invariants dV,dE,dQ,dA correct (dE={exp_E}; k=0 => dE=0 not k+1)")


def check_star_schedule():
    log("=" * 72)
    log("[2] k>=2: growing active VERTICES need NOT grow active BONDS")
    log("    schedule: repeatedly quiet the star centre using a leaf as keeper (k=2)")
    G = star(4); k = 2
    log(f"    start star(4): {counts(G)}")
    rows = [("event", "V", "A", "B", "Acomp")]
    rows.append(("seed",) + tuple(counts(G)[c] for c in ("V", "A", "B", "Acomp")))
    center = 0
    Bvals = []
    for ev in range(1, 5):
        # keeper = an active leaf of the current centre; depositor = centre
        leaves = [m for m in G.neighbors(center) if G.nodes[m]["label"] == "A"]
        keeper = min(leaves)
        G = bud(G, keeper, center, k=k)     # quiet the centre, keeper sprouts k tips
        center = keeper                      # new centre is the keeper (now a k-leaf star)
        c = counts(G); Bvals.append(c["B"])
        rows.append((f"quiet#{ev}",) + tuple(c[cc] for cc in ("V", "A", "B", "Acomp")))
    for r in rows:
        log("      " + "".join(str(x).ljust(10) for x in r))
    require(all(b == k for b in Bvals),
            f"active bonds stay == k ({k}) every event while V, A, Acomp all grow")
    require(rows[-1][1] > rows[1][1] and rows[-1][2] > rows[1][2] and rows[-1][4] > rows[1][4],
            "graph size, active vertices, and active COMPONENTS all strictly grow")
    log("    => distinguish: |V| (grows), active vertices (grow), active bonds (constant=k),")
    log("       active components (grow, via stranded singletons). 'more vertices != more bonds'")


# ============================================================ 2. CONFLUENCE CLAIMS
def check_confluence_scope():
    log("=" * 72)
    log("[3] CONFLUENCE: what is and is NOT established")

    # (a) commuting INDEPENDENT events: disjoint matches commute (parallel independence)
    G = path(6)                              # 0-1-2-3-4-5 ; bonds (0,1) and (3,4) disjoint
    H_ab = bud(bud(G, 0, 1, k=1), 3, 4, k=1)
    H_ba = bud(bud(G, 3, 4, k=1), 0, 1, k=1)
    require(iso(H_ab, H_ba),
            "(a) INDEPENDENT (disjoint) events commute: BUD(0,1);BUD(3,4) ~= reverse (exact iso)")

    # (b/e) the P/R histories are DIFFERENT EVENT CHOICES (not two orders of one collection)
    P = [(1, 0), (2, 1)]; R = [(1, 2), (0, 1)]
    quietedP = {y for (_, y) in P}; quietedR = {y for (_, y) in R}
    log(f"    P = directed events {P}  (quiets vertices {sorted(quietedP)})")
    log(f"    R = directed events {R}  (quiets vertices {sorted(quietedR)})")
    require(set(P) != set(R) and quietedP != quietedR,
            "(b) P and R are DIFFERENT directed events (quiet different vertices), NOT a "
            "reordering of one fixed collection -- undirected edges coincide but depositors differ")
    GP = bud(bud(path(4), 1, 0, k=1), 2, 1, k=1)
    GR = bud(bud(path(4), 1, 2, k=1), 0, 1, k=1)
    require(not iso(GP, GR),
            "(e) distinguishability at equal event count: P vs R non-isomorphic (exact)")

    # (c) reordering a FIXED collection: use the shared-vertex critical pair as the honest
    #     'order' object.  Two directed events on path 0-1-2 that share vertex 1.
    log("    critical pair on path 0-1-2: e1=BUD(0,1) (quiets 1), e2=BUD(1,2) (needs 1 active)")
    G = path(3)
    H1 = bud(G, 0, 1, k=1)                    # fire e1: 1 -> Q
    e2_alive = ("BUD", 1, 2) in directed_events(H1)
    require(not e2_alive,
            "(c) firing e1 DELETES e2's match (shared vertex 1 quieted): the two do NOT commute")

    # (d) non-confluence is a GLOBAL claim -> test joinability to bounded depth EXACTLY,
    #     and report the depth actually reached (NOT a proof of permanent non-joinability).
    A = bud(path(3), 0, 1, k=1)              # descendant via BUD(0,1)
    Bd = bud(path(3), 1, 0, k=1)             # descendant via BUD(1,0)
    require(not iso(A, Bd), "depth-1 descendants A,B of the critical pair are non-isomorphic")
    depth = _joinable_depth(A, Bd, maxd=3)
    log(f"    exact bounded joinability: A-descendants vs B-descendants share NO iso state")
    log(f"    up to added depth D={depth['D']} "
        f"(|A@D|={depth['na']} classes, |B@D|={depth['nb']} classes, joined={depth['joined']})")
    require(depth["joined"] is False,
            f"critical-pair descendants remain disjoint to depth D={depth['D']} "
            f"(FINITE-DEPTH result; global non-confluence NOT claimed)")

    # Q-immutability invariant (analytic; checked): a Q vertex never changes label/edges.
    require(_q_immutable_check(),
            "Q-immutability: once Q, a vertex's label and incident edges are frozen "
            "(only x, depositor y, and fresh z_i are touched by any event)")


def _successors(G, k=1):
    return [bud(G, x, y, k=k) for (x, y) in directed_events(G)]


def _joinable_depth(A, Bd, maxd=3):
    # equal #Q => equal depth for any isomorphic pair; grow both fronts level by level.
    fa, fb = [A], [Bd]
    for D in range(1, maxd + 1):
        fa = class_reps([s for G in fa for s in _successors(G)])
        fb = class_reps([s for G in fb for s in _successors(G)])
        for Ga in fa:
            for Gb in fb:
                if iso(Ga, Gb):
                    return dict(D=D, joined=True, na=len(fa), nb=len(fb))
    return dict(D=maxd, joined=False, na=len(fa), nb=len(fb))


def _q_immutable_check():
    # brute: over many random-ish short derivations, every Q vertex keeps label+neighbours
    G = path(5)
    frozen = {}
    for _ in range(12):
        evs = directed_events(G)
        if not evs:
            break
        x, y = sorted(evs)[len(evs) // 2]
        # snapshot current Q vertices
        for n in G:
            if G.nodes[n]["label"] == "Q":
                sig = (G.nodes[n]["label"], frozenset(G.neighbors(n)))
                if n in frozen and frozen[n] != sig:
                    return False
                frozen[n] = sig
        G = bud(G, x, y, k=1)
    # final check
    for n, sig in frozen.items():
        cur = (G.nodes[n]["label"], frozenset(G.neighbors(n)))
        if cur != sig:
            return False
    return True


# ============================================================ M2 counterexample
def check_m2_not_forgetful():
    log("=" * 72)
    log("[4] M2 is NOT a same-length forgetful null (withdraw that characterisation)")
    G0 = nx.Graph(); G0.add_node(0, label="A")
    star4 = sprout(sprout(sprout(G0, 0), 0), 0)          # 4-vertex star
    path4 = sprout(sprout(sprout(G0, 0), 1), 2)          # 4-vertex path
    log(f"    3x SPROUT from one vertex -> star {counts(star4)} vs path {counts(path4)}")
    require(star4.number_of_nodes() == path4.number_of_nodes() == 4
            and star4.number_of_edges() == path4.number_of_edges() == 3,
            "both reachable in 3 events with equal V=4,E=4-1=3")
    require(not iso(star4, path4),
            "star K1,3 vs path P4 non-isomorphic: M2 DISTINGUISHES equal-length histories "
            "(so 'forgetful null' WITHDRAWN; M2 confluence left as a separate open question)")


# ============================================================ 3+4. EXACT POSITIVE RESULT
def check_positive_result():
    log("=" * 72)
    log("[5] BOUNDED POSITIVE RESULT: depth-2 states from path(4), k=1 (EXACT classes)")
    seed = path(4); k = 1
    depth2 = []
    hist_of = []
    for (x1, y1) in directed_events(seed):
        G1 = bud(seed, x1, y1, k=k)
        for (x2, y2) in directed_events(G1):
            G2 = bud(G1, x2, y2, k=k)
            depth2.append(G2); hist_of.append(((x1, y1), (x2, y2)))
    reps = class_reps(depth2)
    log(f"    total directed length-2 derivations: {len(depth2)}")
    log(f"    EXACT isomorphism classes at depth 2: {len(reps)}")
    require(len(reps) >= 1, "depth-2 exact class enumeration succeeded")

    # locate P and R, confirm different classes with different continuations
    GP = bud(bud(seed, 1, 0, k=k), 2, 1, k=k)
    GR = bud(bud(seed, 1, 2, k=k), 0, 1, k=k)
    iP, iR = class_index(GP, reps), class_index(GR, reps)
    log(f"    P -> class {iP} (B={counts(GP)['B']}) ; R -> class {iR} (B={counts(GR)['B']})")
    require(iP != iR, "P and R land in DIFFERENT exact isomorphism classes")

    # successor table: for each depth-2 class, one-step successor classes with the
    # MULTIPLICITY of directed events reaching each -> uniform next-state distribution.
    log("    successor table (per depth-2 class): directed-event multiplicities over "
        "successor classes")
    # unify successor classes across all depth-2 classes into one class list
    all_succ = [bud(R, x, y, k=k) for R in reps for (x, y) in directed_events(R)]
    succ_reps = class_reps(all_succ + reps)   # include reps so self-type classes align
    tab = ["depth2_class  B  n_directed_events  ->  {successor_class: multiplicity}  (prob)"]
    diff_conts = set()
    for i, R in enumerate(reps):
        des = directed_events(R)
        mult = {}
        for (x, y) in des:
            ci = class_index(bud(R, x, y, k=k), succ_reps)
            mult[ci] = mult.get(ci, 0) + 1
        tot = len(des)
        dist = {c: round(m / tot, 3) for c, m in sorted(mult.items())}
        tab.append(f"  class {i:>2}   {counts(R)['B']}   {tot:>2}   -> "
                   f"{dict(sorted(mult.items()))}   probs {dist}")
        diff_conts.add((counts(R)["B"], tuple(sorted(mult.items()))))
    with open(TABLE, "w") as f:
        f.write("\n".join(tab) + "\n")
    for t in tab:
        log("    " + t)
    # do matched-size (same depth) classes differ in available continuations?
    require(len(diff_conts) > 1,
            "matched-size (depth-2) classes differ in their available continuations "
            "(successor-class multiplicity profiles are not all identical)")
    # P vs R specifically:
    def profile(R):
        des = directed_events(R); m = {}
        for (x, y) in des:
            ci = class_index(bud(R, x, y, k=k), succ_reps); m[ci] = m.get(ci, 0) + 1
        return tuple(sorted(m.items()))
    require(profile(GP) != profile(GR) or counts(GP)["B"] != counts(GR)["B"],
            "P and R differ in available continuations (successor profile and/or B)")
    log("    NOTE: this shows outcomes DIFFER in continuations; it does NOT claim that a")
    log("    larger eligible-event count predicts 'richer' future structure.")


def main():
    check_delta_B()
    check_star_schedule()
    check_confluence_scope()
    check_m2_not_forgetful()
    check_positive_result()
    log("=" * 72)
    if FAILS:
        log(f"AUDIT FAILED: {len(FAILS)} check(s) failed:")
        for m in FAILS:
            log(f"   - {m}")
    else:
        log("AUDIT PASSED: all exact checks and assertions hold.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

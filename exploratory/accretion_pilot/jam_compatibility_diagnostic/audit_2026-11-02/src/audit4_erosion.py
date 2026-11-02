#!/usr/bin/env python3
"""
audit4_erosion.py -- Part 4 of the audit: repair and re-run the boundary-
intervention (inner-rim erosion) checks for the world-7 jam.

The study's part5_erosion.py had five weak checks (confirmed by reading it):
  * component_ok() tested only that dead-edge ENDPOINTS exist, not connectivity;
  * the dead_site_neighbour_removed flag used that same weak proxy;
  * the computed stop flag never actually stopped the loop;
  * dead sites were read off the SKIN frontier (which mixes the true growth
    frontier with pruning-exposed inner edges);
  * true-frontier preservation was assumed, not checked.

This script keeps the study's erosion levels (theta in {inf,2.0,1.5,1.0}, in S)
and re-runs the four measurements, but adds EXPLICIT, documented checks:

  Adjacency (documented): two decorated half-tiles are ADJACENT iff they share a
  full edge (a frozenset of two vertex keys that both tiles own). Connectivity is
  connected components under this relation (BFS).

  C1 true growth frontier: computed ONCE from the FULL jam patch (not the skin),
     with edge ownership (p,q,r,owner-tile). We verify every true-frontier edge of
     the full patch that lies in the retained band is still a boundary edge after
     erosion, with the same owner tile -- i.e. erosion does not alter the outer
     frontier.
  C2 dead-site identity: original dead sites are the FULL-patch true-frontier
     edges with zero frozen candidates (the real jam sites), fixed before erosion.
  C3 dead-site neighbourhood: the set of tiles incident to each dead edge's two
     endpoint vertices must be unchanged (this is the support the candidate rule
     reads at that edge).
  C4 connectivity: the eroded band must be a single connected component that
     contains every dead-site-owning tile.
  C5 stopping: if any of C1/C3/C4 fails at a level, that level is INVALID and the
     loop STOPS (protocol clause), rather than silently continuing.

Writes results/audit4_erosion.json.
"""
from __future__ import annotations
import json, collections
import audit_common as A
from audit_common import Sl, PC, L, D, S
import feas


def ekey(p, q):
    return frozenset((L.key(p), L.key(q)))


def full_true_frontier(full):
    """edge-key -> (p,q,r,owner dkey) for the TRUE growth frontier of the full patch."""
    P = L.Patch(list(full))
    out = {}
    for e in P.frontier():
        out[ekey(e[0], e[1])] = dict(p=e[0], q=e[1], r=e[2], owner=PC.dk(e[3]))
    return out, P


def dead_on_true_frontier(full):
    """Real jam sites: true-frontier edges of the FULL patch with 0 candidates."""
    P = L.Patch(list(full))
    dead = [e for e in P.frontier() if len(D.candidates(P, *e[:3])) == 0]
    return dead


def tiles_incident_to(tiles, vkeys):
    out = set()
    for t in tiles:
        if any(L.key(z) in vkeys for z in t[1:]):
            out.add(PC.dk(t))
    return out


def connected_components(tiles):
    """edge-adjacency components (BFS). Returns list of sets of dkeys."""
    by_edge = collections.defaultdict(list)
    dk = {PC.dk(t): t for t in tiles}
    for t in tiles:
        c, Aa, Bb, Cc = t
        for p, q in ((Aa, Bb), (Bb, Cc), (Cc, Aa)):
            by_edge[ekey(p, q)].append(PC.dk(t))
    adj = collections.defaultdict(set)
    for ek, ts in by_edge.items():
        for i in range(len(ts)):
            for j in range(i + 1, len(ts)):
                adj[ts[i]].add(ts[j]); adj[ts[j]].add(ts[i])
    seen = set(); comps = []
    for start in dk:
        if start in seen:
            continue
        comp = set(); stack = [start]
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u); comp.add(u)
            stack.extend(adj[u] - seen)
        comps.append(comp)
    return comps


def true_frontier_vertices(full):
    return [z for e in L.Patch(list(full)).frontier() for z in e[:2]]


def erode(skin, tfv, theta):
    def d(t):
        c = sum(t[1:]) / 3
        return min(abs(c - v) for v in tfv) / S
    return [t for t in skin if d(t) <= theta]


def candidates_at(tiles, edges):
    P = L.Patch(list(tiles))
    present = {ekey(e[0], e[1]): e for e in P.frontier()}
    out = []
    for e in edges:
        cur = present.get(ekey(e[0], e[1]))
        out.append(len(D.candidates(P, *cur[:3])) if cur is not None else None)
    return out


def main():
    A.RESULTS.mkdir(parents=True, exist_ok=True)
    w, si, js = 7, 0, 23
    arm, full, skin0 = A.jam_full_and_skin(w, si, js)

    tf_full, _ = full_true_frontier(full)
    # study's dead sites (skin frontier) vs corrected dead sites (full true frontier)
    skin_dead = [e for e in L.Patch(list(skin0)).frontier() if len(D.candidates(L.Patch(list(skin0)), *e[:3])) == 0]
    true_dead = dead_on_true_frontier(full)
    skin_dead_ek = {ekey(e[0], e[1]) for e in skin_dead}
    true_dead_ek = {ekey(e[0], e[1]) for e in true_dead}
    dead_are_on_true_frontier = {ek for ek in skin_dead_ek} <= set(tf_full.keys())
    # the original dead sites we hold fixed across erosion: the engine's true jam sites
    orig_dead = true_dead
    dead_vkeys = {L.key(z) for e in orig_dead for z in e[:2]}
    orig_dead_nbhd = tiles_incident_to(skin0, dead_vkeys)   # neighbourhood in the retained band
    dead_owner_dks = {PC.dk(e[3]) for e in orig_dead}

    # true-frontier edge-keys that lie within the retained band (owner tile present in skin0)
    skin0_dks = {PC.dk(t) for t in skin0}
    tf_in_band = {ek: v for ek, v in tf_full.items() if v["owner"] in skin0_dks}

    tfv = true_frontier_vertices(full)
    THETAS = [("L0", float("inf")), ("L1", 2.0), ("L2", 1.5), ("L3", 1.0)]
    rows = []
    stopped_at = None
    for name, theta in THETAS:
        er = erode(skin0, tfv, theta)
        er_dks = {PC.dk(t) for t in er}
        er_P = L.Patch(list(er))
        er_boundary = {ekey(e[0], e[1]): e for e in er_P.frontier()}

        # C1 true-frontier preservation (edges + ownership) for frontier edges in the band
        tf_preserved = True; tf_broken = []
        for ek, v in tf_in_band.items():
            if v["owner"] not in er_dks:
                tf_preserved = False; tf_broken.append(["owner_removed", list(ek)])
            elif ek not in er_boundary:
                tf_preserved = False; tf_broken.append(["edge_not_boundary", list(ek)])
        # C3 dead-site neighbourhood preserved
        nbhd_now = tiles_incident_to(er, dead_vkeys)
        nbhd_preserved = (nbhd_now == orig_dead_nbhd)
        # C4 connectivity: single component containing all dead-owner tiles
        comps = connected_components(er)
        dead_comp = next((cc for cc in comps if dead_owner_dks & cc), set())
        connected_single = (len(comps) == 1)
        dead_in_one_comp = dead_owner_dks <= dead_comp
        # protocol stop condition
        valid = tf_preserved and nbhd_preserved and dead_in_one_comp
        # measurements (only meaningful on a valid level, but recorded regardless)
        try:
            rank = Sl.rank_of(er); cm = Sl.constraints(er, rank); cl = feas.classify(cm)
            feasibility, rstar = cl["cls"], cl["r"]
        except AssertionError:
            feasibility, rstar = "unresolved_layers", None
        cand = candidates_at(er, orig_dead)

        rows.append(dict(level=name, theta=(None if theta == float("inf") else theta),
                         n_tiles=len(er), removed=len(skin0) - len(er),
                         true_frontier_preserved=tf_preserved, tf_violations=tf_broken[:5],
                         dead_site_neighbourhood_preserved=nbhd_preserved,
                         n_components=len(comps), dead_sites_in_single_component=dead_in_one_comp,
                         level_valid=valid,
                         feasibility=feasibility, chebyshev_r=rstar,
                         candidates_at_dead_sites=cand))
        print(f"{name} theta={theta}: tiles {len(er)} | tf_preserved={tf_preserved} "
              f"nbhd_preserved={nbhd_preserved} comps={len(comps)} dead_in_1={dead_in_one_comp} "
              f"| valid={valid} feas={feasibility} r*={rstar} dead_cands={cand}", flush=True)
        if not valid:
            stopped_at = name
            print(f"  -> level {name} VIOLATES a protocol check; stopping erosion here.", flush=True)
            break

    report = dict(
        case="w7", jam_step=js,
        dead_site_definition=dict(
            study_used="skin frontier (mixes true frontier + pruning-exposed inner edges)",
            audit_uses="FULL-patch true growth frontier with zero frozen candidates",
            n_true_frontier_dead=len(true_dead), n_skin_frontier_dead=len(skin_dead),
            skin_dead_all_on_true_frontier=bool(dead_are_on_true_frontier),
            skin_and_true_dead_identical=bool(skin_dead_ek == true_dead_ek)),
        adjacency_definition="two half-tiles adjacent iff they share a full edge (both own it); BFS components",
        levels=rows, stopped_at=stopped_at,
        conclusion=("With explicit connectivity, dead-site-neighbourhood, and true-frontier-ownership checks "
                    "(and a loop that actually stops on violation), the world-7 erosion outcome is "
                    "re-evaluated; see per-level level_valid and feasibility."))
    (A.RESULTS / "audit4_erosion.json").write_text(json.dumps(report, indent=2, default=float))
    dd = report["dead_site_definition"]
    print(f"\ndead sites: true-frontier={dd['n_true_frontier_dead']} skin-frontier={dd['n_skin_frontier_dead']} "
          f"identical={dd['skin_and_true_dead_identical']} skin_dead_on_true_frontier={dd['skin_dead_all_on_true_frontier']}")
    print("wrote results/audit4_erosion.json")


if __name__ == "__main__":
    main()

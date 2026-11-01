#!/usr/bin/env python3
"""
part5_erosion.py -- bounded inner-rim erosion experiment (world 7).

Preserve the engine's distinction between the TRUE growth frontier (outer) and
edges merely exposed by pruning (inner). Hold the outer growth boundary and
retained geometry fixed; remove ONLY inner-rim tiles, in nested levels fixed
before outcomes. The dead sites lie on the outer true frontier, so inner erosion
never removes a dead-site neighbour (checked).

Erosion levels (keep tiles with min distance to any true-frontier vertex <= theta):
  L0 theta=inf (full skin), L1 theta=2.0, L2 theta=1.5, L3 theta=1.0  (in S).
(Deviation from the protocol's (radius-L)*S formula, which over-erodes a radius-2
skin; recorded in PROTOCOL_DEVIATIONS.md.)

At each level, measured SEPARATELY:
  1. compatibility-region feasibility (feas.classify);
  2. candidate counts at the ORIGINAL dead sites (frozen D.candidates);
  3. legality of the previously-tested single-hex flip alternatives whose full
     support remains (frozen engine);
  4. whether the frozen A/B reader still operates, and its result.
No growth is resumed. Outputs ../results/part5_erosion.json + report.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import study_common as SC
from study_common import Sl, PC, L, D, S, HF
import feas
import phase4_readout as RD   # frozen-reader payload + runner (pilot)

OUT = Path(__file__).resolve().parent.parent / "results"
THETAS = [("L0", float("inf")), ("L1", 2.0), ("L2", 1.5), ("L3", 1.0)]


def true_frontier_vertices(full):
    return [z for e in L.Patch(full).frontier() for z in e[:2]]


def dist_to_tf(t, tfv):
    c = sum(t[1:]) / 3
    return min(abs(c - v) for v in tfv) / S


def erode(skin, tfv, theta):
    return [t for t in skin if dist_to_tf(t, tfv) <= theta]


def dead_edges(skin):
    P = L.Patch(skin)
    return [e for e in P.frontier() if len(D.candidates(P, *e[:3])) == 0]


def component_ok(tiles, dead):
    """dead-site endpoints still present and their tiles connected into the patch."""
    keys = {L.key(z) for t in tiles for z in t[1:]}
    for e in dead:
        if L.key(e[0]) not in keys or L.key(e[1]) not in keys:
            return False
    return True


def candidates_at(tiles, edges):
    P = L.Patch(tiles)
    present = {frozenset((L.key(e[0]), L.key(e[1]))) for e in P.frontier()}
    out = []
    for e in edges:
        ek = frozenset((L.key(e[0]), L.key(e[1])))
        if ek in present:
            # find the edge as currently owned (same p,q,r)
            cur = next(x for x in P.frontier()
                       if frozenset((L.key(x[0]), L.key(x[1]))) == ek)
            out.append(len(D.candidates(P, *cur[:3])))
        else:
            out.append(None)   # edge no longer on the boundary
    return out


def surviving_flip_legal(tiles, dead_vkeys):
    """Among three-rhombus flip hexagons near the dead sites whose 6 tiles still
    remain, count how many have a fully-legal in-context alternative."""
    dmids = None
    P = L.Patch(tiles)
    deads = [e for e in P.frontier() if len(D.candidates(P, *e[:3])) == 0]
    if not deads:
        return dict(n_hex=0, n_legal=0, note="no dead site present")
    mids = [(e[0] + e[1]) / 2 for e in deads]
    nbhd = [t for t in tiles if any(abs(HF.tile_centroid(t) - m) < 6 * S for m in mids)]
    hexes = HF.find_flip_hexagons(nbhd)
    tilekeys = {HF.dkey(t) for t in tiles}
    n_legal = 0; n_checked = 0
    for h in hexes:
        if not all(HF.dkey(t) in tilekeys for t in h["tiles"]):
            continue
        n_checked += 1
        sdk = {HF.dkey(u) for u in h["tiles"]}
        hc = sum(complex(*k) for k in HF._hexagon_boundary(h["tiles"])[1]) / 6
        surr = [t for t in tiles if HF.dkey(t) not in sdk and abs(HF.tile_centroid(t) - hc) < 4 * S]
        sols, _ = HF.enumerate_hexagon_fillings(h["tiles"], surr, legality="engine", max_solutions=4)
        if any(s != tuple(sorted(sdk)) for s in sols):
            n_legal += 1
    return dict(n_hex=n_checked, n_legal=n_legal)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    w, si, js = 7, 0, 23
    forks = SC.P3.load_forks()
    Sstar = forks[w]["Sstar"]; cs = forks[w]["cs"]; B = cs[1]
    stream = PC.streams_for(w)[si]
    arm = PC.grow(Sstar, B, stream, 44)
    full = arm["snaps"][-1]
    skin0, _ = PC.skin_of(full)
    tfv = true_frontier_vertices(full)
    orig_dead = dead_edges(skin0)
    dead_vkeys = {L.key(z) for e in orig_dead for z in e[:2]}

    # IIS origin vertices (from Part 4) and their erosion depth
    prov = json.loads((OUT / "part4_provenance.json").read_text())
    iis_vk = [tuple(p["origin_vertex"]) for p in prov[f"w{w}-jam_trigger_skin@{js}"]["prov"]]

    rows = []
    for name, theta in THETAS:
        er = erode(skin0, tfv, theta)
        stop = not component_ok(er, orig_dead)
        # (1) feasibility
        try:
            rank = Sl.rank_of(er); cm = Sl.constraints(er, rank)
            cl = feas.classify(cm)
            feasibility = cl["cls"]; rstar = cl["r"]
        except AssertionError:
            feasibility = "unresolved_layers"; rstar = None
        # which IIS vertices are still present
        erkeys = {L.key(z) for t in er for z in t[1:]}
        iis_present = sum(1 for v in iis_vk if tuple(map(float, v)) in
                          {tuple(map(float, k)) for k in erkeys}) if iis_vk else None
        # (2) candidate counts at original dead sites
        cand = candidates_at(er, orig_dead)
        # (3) surviving flip legality
        flip = surviving_flip_legal(er, dead_vkeys)
        # (4) reader
        payload = RD.build_payload(Sstar, cs, er)
        rres = RD.run_reader(payload)
        routcome, rdetail = RD.classify(rres)
        rows.append(dict(level=name, theta=(None if theta == float("inf") else theta),
                         n_tiles=len(er), removed=len(skin0) - len(er),
                         dead_site_neighbour_removed=stop,
                         feasibility=feasibility, chebyshev_r=rstar,
                         iis_origin_vertices_present=iis_present, iis_total=len(iis_vk),
                         candidates_at_dead_sites=cand,
                         flip_hexagons_checked=flip["n_hex"], flip_legal=flip["n_legal"],
                         reader_outcome=routcome, reader_detail=rdetail,
                         reader_status=rres.get("status")))
        print(f"{name} theta={theta}: tiles {len(er)} feas={feasibility} "
              f"r*={rstar} dead_cands={cand} flip_legal={flip['n_legal']}/{flip['n_hex']} "
              f"reader={routcome} IIS_present={iis_present}/{len(iis_vk)}", flush=True)

    (OUT / "part5_erosion.json").write_text(json.dumps(rows, indent=2, default=float))

    lines = ["Part 5 -- bounded inner-rim erosion (world 7 jam skin)",
             "Inner-rim tiles removed in nested levels; outer growth boundary + dead sites held fixed.", ""]
    lines.append(f"{'level':>5} {'theta':>6} {'tiles':>6} {'feasible':>16} {'r*':>10} "
                 f"{'dead_cands':>12} {'flip_legal':>10} {'reader':>18}")
    for r in rows:
        lines.append(f"{r['level']:>5} {str(r['theta']):>6} {r['n_tiles']:>6} {r['feasibility']:>16} "
                     f"{('%.3e'%r['chebyshev_r']) if r['chebyshev_r'] is not None else 'NA':>10} "
                     f"{str(r['candidates_at_dead_sites']):>12} "
                     f"{str(r['flip_legal'])+'/'+str(r['flip_hexagons_checked']):>10} "
                     f"{r['reader_outcome']:>18}")
    lines.append("")
    lines.append("Reading: feasibility (global) and candidate availability at the dead site (local) are")
    lines.append("tracked separately. Removing inner tiles alone may loosen the global constraint without")
    lines.append("restoring local candidates at a still-present dead site -- these are different things.")
    (OUT / "part5_report.txt").write_text("\n".join(lines) + "\n")
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()

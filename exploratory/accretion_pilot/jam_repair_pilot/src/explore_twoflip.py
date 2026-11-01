#!/usr/bin/env python3
"""
explore_twoflip.py -- EXPLORATION (not part of the frozen pilot protocol).

Phase 3 found no single three-rhombus flip is legal in context, because one flip
breaks a boundary-vertex star the surround holds fixed. Phase 4 found the jam's
contradiction lives *inside* the skin (F(skin)=0), not in buried tiles -- so the
obstruction is rigidity, not burial. This asks the natural follow-up: does a
COORDINATED pair of flips (the start of a Penrose 'worm') relieve what one flip
cannot?

A two-flip move = pick two tile-disjoint flip hexagons near the dead sites, apply
BOTH their (unique) phason alternatives at once, and require the combined
rearrangement to be fully legal, keep the true frontier unchanged, and give the
dead sites candidates. No matching rule is relaxed; legality is the frozen
engine's. At most one two-flip is then resumed to the step-44 horizon.

Usage: python explore_twoflip.py [world stream_idx jam_step]  (default 7 0 23)
"""
from __future__ import annotations
import sys, itertools, random
import pilot_common as PC
from pilot_common import L, D, S, SN
import phase3_repair as P3
import hexflip as HF

dkey = HF.dkey


def unique_alt(hext, skin_tiles):
    """The single phason alternative dissection of a hexagon (relaxed surround),
    as a list of 6 tiles, or None if none."""
    sdk = {dkey(u) for u in hext}
    hc = sum(complex(*k) for k in HF._hexagon_boundary(hext)[1]) / 6
    bverts = set(HF._hexagon_boundary(hext)[1])
    base = [t for t in skin_tiles if dkey(t) not in sdk
            and abs(HF.tile_centroid(t) - hc) < 4 * S
            and not any(L.key(z) in bverts for z in HF.tile_vertices(t))]
    orig = tuple(sorted(sdk))
    sols, lookup = HF.enumerate_hexagon_fillings(hext, base, legality="engine", max_solutions=8)
    alts = [s for s in sols if s != orig]
    if not alts:
        return None
    return [lookup[dk] for dk in alts[0]]


def patch_legal(newtiles, check_tiles):
    """Authoritative: every tile in check_tiles is legal against all the others."""
    idx = {dkey(t): t for t in newtiles}
    for t in check_tiles:
        rest = [u for u in newtiles if dkey(u) != dkey(t)]
        if not L.Patch(rest).legal(t):
            return False
    return True


def main():
    world = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    si = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    js = int(sys.argv[3]) if len(sys.argv) > 3 else 23
    forks = P3.load_forks()
    Sstar = forks[world]["Sstar"]; B = forks[world]["cs"][1]
    stream = PC.streams_for(world)[si]

    P, rng = P3.replay_to_trigger(Sstar, B, stream, js)
    rng_state = rng.getstate()
    skin = list(P.tris)
    deads = P3.dead_sites(P)
    dead_vkeys = set()
    for e in deads:
        dead_vkeys.add(L.key(e[0])); dead_vkeys.add(L.key(e[1]))
    true_fr = {frozenset((L.key(e[0]), L.key(e[1]))) for e in P.frontier()}
    dead_mids = [(e[0] + e[1]) / 2 for e in deads]
    nbhd = [t for t in skin if any(abs(HF.tile_centroid(t) - m) < 6 * S for m in dead_mids)]
    hexes = HF.find_flip_hexagons(nbhd)
    print(f"w{world}-B-s{si} jam {js}: skin {len(skin)}, dead sites {len(deads)}, "
          f"flip hexagons near dead sites {len(hexes)}")

    # keep only interior hexagons (6 boundary edges all interior) with a phason alt
    cand = []
    for h in hexes:
        boundary, cyc = HF._hexagon_boundary(h["tiles"])
        if any(ek in true_fr for ek in boundary):
            continue
        alt = unique_alt(h["tiles"], skin)
        if alt is None:
            continue
        touch = bool(set(cyc) & dead_vkeys)
        cand.append(dict(h=h, alt=alt, old=[dkey(t) for t in h["tiles"]],
                         bverts=set(cyc), touch=touch))
    print(f"interior hexagons with a phason alt: {len(cand)} "
          f"(of which touch a dead vertex: {sum(c['touch'] for c in cand)})")

    # pairs: at least one must touch a dead vertex, the two must be tile-disjoint,
    # and prefer pairs that share a vertex (a 'worm' segment).
    tried = 0; joint_legal = 0; joint_legal_touch = 0; unjam = 0; winners = []
    for a, b in itertools.combinations(cand, 2):
        if set(a["old"]) & set(b["old"]):
            continue                      # overlapping clusters -> not a two-flip
        tried += 1
        oldset = set(a["old"]) | set(b["old"])
        newadd = list(a["alt"]) + list(b["alt"])
        newtiles = [t for t in skin if dkey(t) not in oldset] + newadd
        # affected tiles: the new ones + existing tiles incident to any affected vertex
        affected_v = set()
        for t in list(a["h"]["tiles"]) + list(b["h"]["tiles"]) + newadd:
            for z in HF.tile_vertices(t):
                affected_v.add(L.key(z))
        check = list(newadd) + [t for t in newtiles
                                if dkey(t) not in {dkey(u) for u in newadd}
                                and any(L.key(z) in affected_v for z in HF.tile_vertices(t))]
        if not patch_legal(newtiles, check):
            continue
        joint_legal += 1
        if a["touch"] or b["touch"]:
            joint_legal_touch += 1
        # true frontier unchanged?
        newfr = {frozenset((L.key(e[0]), L.key(e[1]))) for e in L.Patch(newtiles).frontier()}
        # (compare only near the change: the two hexagons are interior, so frontier
        #  should be identical; check set equality of frontier edge keys)
        boundary_ok = (newfr == {frozenset((L.key(e[0]), L.key(e[1]))) for e in P.frontier()})
        # dead sites now have candidates?
        Pn = L.Patch(newtiles)
        dead_after = [e for e in Pn.frontier()
                      if frozenset((L.key(e[0]), L.key(e[1]))) in
                      {frozenset((L.key(d[0]), L.key(d[1]))) for d in deads}
                      and len(D.candidates(Pn, *e[:3])) == 0]
        if boundary_ok and len(dead_after) == 0:
            unjam += 1
            winners.append((a, b, newtiles))

    print(f"two-flip pairs tried (all tile-disjoint): {tried}")
    print(f"  jointly legal (any): {joint_legal}")
    print(f"  jointly legal AND >=1 touches a dead vertex: {joint_legal_touch}")
    print(f"  jointly legal AND un-jam (dead sites gain candidates, frontier intact): {unjam}")

    if not winners:
        print("\nRESULT: no legal two-flip (worm segment) un-jams this jam.")
        return

    # resume the first winner on an ActiveSkin, original scheduler + RNG, to step 44
    a, b, newtiles = winners[0]
    print(f"\nRESULT: a legal two-flip un-jams. flip vertices "
          f"{a['h']['vertex']} & {b['h']['vertex']}. Resuming...")
    # rebuild an ActiveSkin at the trigger, swap in the new tiles, keep true frontier
    Pr, rngr = P3.replay_to_trigger(Sstar, B, stream, js)
    rngr.setstate(rng_state)
    idx = L.Patch(newtiles)
    Pr.tris, Pr.edges, Pr.V = idx.tris, idx.edges, idx.V
    rejam = None; reached = False; steps = 0
    for s in range(js, PC.STEPS + 1):
        st, n, kind = SN.patient(Pr, rngr)
        if st == "JAM":
            rejam = s; break
        Pr.prune(); steps += 1
        if s == PC.STEPS:
            reached = True
    print(f"  resume: steps {steps}, rejam_at {rejam}, reached_horizon {reached}")


if __name__ == "__main__":
    main()

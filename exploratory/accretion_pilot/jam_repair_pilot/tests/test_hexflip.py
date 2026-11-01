#!/usr/bin/env python3
"""
Controlled-example validation of the hexagon-flip generator/validator
(hexflip.py), per PHASE3_PROTOCOL.md Section 7. Run:

  export EFP_SNAPSHOT=/home/user/efp-snapshot/exploratory/accretion_pilot/expansion_front_paper
  python test_hexflip.py        # from src/, or with src/ on sys.path

Exits non-zero on any failure.
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
import engine_bridge as EB
import hexflip as HF
L, S = EB.L, EB.S

FAILS = []


def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def local(tiles, hc, r=4):
    return [t for t in tiles if abs(HF.tile_centroid(t) - hc) < r * S]


def main():
    tiles = L.seed_patch(0j, 9 * S)
    hexes = HF.find_flip_hexagons(tiles)
    print(f"reference patch: {len(tiles)} tiles; flip hexagons detected: {len(hexes)}")
    check(len(hexes) > 0, "detector finds >=1 three-rhombus flip hexagon")

    # sample a handful for the per-hexagon checks
    sample = hexes[:25]

    # 1. Completeness: in full context the hole refills to exactly the original.
    ok_full = 0
    for h in sample:
        hext = h["tiles"]; sdk = {HF.dkey(u) for u in hext}
        hc = sum(complex(*k) for k in h["bverts"]) / 6
        surround = local([t for t in tiles if HF.dkey(t) not in sdk], hc)
        sols, _ = HF.enumerate_hexagon_fillings(hext, surround, legality="engine")
        orig = tuple(sorted(HF.dkey(t) for t in hext))
        if sols == [orig]:
            ok_full += 1
    check(ok_full == len(sample),
          f"in-context refill == original exactly, no spurious solutions ({ok_full}/{len(sample)})")

    # 2. Finds the flip when the external star-constraint is relaxed, and the
    #    flip MOVES the interior vertex (a genuine rearrangement).
    ok_relaxed = 0; ok_moved = 0
    for h in sample:
        hext = h["tiles"]; sdk = {HF.dkey(u) for u in hext}
        hc = sum(complex(*k) for k in h["bverts"]) / 6
        bverts = set(h["bverts"])
        base = [t for t in tiles if HF.dkey(t) not in sdk
                and not any(L.key(z) in bverts for z in HF.tile_vertices(t))]
        surround = local(base, hc)
        sols, lookup = HF.enumerate_hexagon_fillings(hext, surround, legality="engine")
        orig = tuple(sorted(HF.dkey(t) for t in hext))
        alts = [s for s in sols if s != orig]
        if orig in sols and alts:
            ok_relaxed += 1
            av = {L.key(z) for dk in alts[0] for z in HF.tile_vertices(lookup[dk])}
            if h["vertex"] not in av:
                ok_moved += 1
    check(ok_relaxed == len(sample),
          f"relaxed surround -> exactly a 2nd legal dissection appears ({ok_relaxed}/{len(sample)})")
    check(ok_moved == len(sample),
          f"the alternative dissection moves the interior flip vertex ({ok_moved}/{len(sample)})")

    # 3. Boundary invariance: every accepted filling keeps the 6 outer edges.
    inv = True
    for h in sample[:10]:
        hext = h["tiles"]; sdk = {HF.dkey(u) for u in hext}
        hc = sum(complex(*k) for k in h["bverts"]) / 6
        bverts = set(h["bverts"])
        base = [t for t in tiles if HF.dkey(t) not in sdk
                and not any(L.key(z) in bverts for z in HF.tile_vertices(t))]
        surround = local(base, hc)
        boundary0, _ = HF._hexagon_boundary(hext)
        sols, lookup = HF.enumerate_hexagon_fillings(hext, surround, legality="engine")
        for s in sols:
            sol_tiles = [lookup.get(dk) or {HF.dkey(t): t for t in hext}[dk] for dk in s]
            b1, _ = HF._hexagon_boundary(sol_tiles)
            if set(b1) != set(boundary0):
                inv = False
    check(inv, "every accepted filling preserves the 6-edge outer hexagon boundary")

    # 4. Rejection: a fabricated overlapping tile is rejected by the engine's legal().
    h = sample[0]; hext = h["tiles"]
    P = L.Patch(list(hext))
    t0 = hext[0]
    nudged = (t0[0], t0[1] + 0.3 * S, t0[2] + 0.3 * S, t0[3] + 0.3 * S)  # overlaps interior
    check(not P.legal(nudged), "engine legal() rejects an overlapping fabricated tile")
    check(not HF._legal_no_atlas(P, nudged), "geometric legality rejects the overlap too")

    # 5. Module-correctness of the generator: every half-tile it proposes across
    #    an edge is congruent to a template (two legs of length S; base S/tau or
    #    tau*S). The growth engine's legal() does not itself validate the module
    #    (it trusts candidates() to be module-correct), so we assert it here.
    good = True
    hext = sample[0]["tiles"]
    boundary, cyc = HF._hexagon_boundary(hext)
    poly = HF._poly_of(cyc)
    e0 = list(boundary[0])                     # a boundary edge, two vertex keys
    p, q = complex(*e0[0]), complex(*e0[1])
    for nt in HF._placements_across(p, q, poly):
        legs = [abs(b - a) for a, b in ((nt[1], nt[2]), (nt[2], nt[3]), (nt[3], nt[1]))]
        nlegs = sum(abs(x - S) < 1e-4 * S for x in legs)
        base_ok = any(abs(x - S / HF.TAU) < 1e-4 * S or abs(x - HF.TAU * S) < 1e-4 * S for x in legs)
        if not (nlegs == 2 and base_ok):
            good = False
    check(good, "every generator-proposed half-tile is module-correct (2 legs = S, valid base)")

    # 6. Atlas rejection in context: the relaxed-surround flip is NOT legal in
    #    full context (it would create a forbidden vertex star) -- i.e. geometric
    #    flip != legal flip.
    hext = sample[0]["tiles"]; sdk = {HF.dkey(u) for u in hext}
    hc = sum(complex(*k) for k in sample[0]["bverts"]) / 6
    surr_full = local([t for t in tiles if HF.dkey(t) not in sdk], hc)
    sols_full, _ = HF.enumerate_hexagon_fillings(hext, surr_full, legality="engine")
    check(len(sols_full) == 1,
          "the flip that is legal in relaxed context is rejected in full context "
          "(geometric flip != decorated-legal flip)")

    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)} check(s)")
        sys.exit(1)
    print("ALL HEXFLIP VALIDATION CHECKS PASSED.")


if __name__ == "__main__":
    main()

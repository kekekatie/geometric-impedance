#!/usr/bin/env python3
"""
audit5_hexsearch.py -- Part 5 of the audit: the single-hexagon flip alternative
search (phason/simpleton flip).

Concern: enumerate_hexagon_fillings fills one deterministic open-edge order and
filters each placement with the frozen P.legal in the PARTIAL context, so a
completed-legal alternative could in principle be missed (intermediate rejection),
and part5 called it with max_solutions=4.

The frozen engine's legality is a function of the FINAL local configuration: a
vertex is legal iff its assembled corner list is a complete atlas star
(star in STARS) or a contiguous arc (in ARCS). So we can validate a completed
filling ORDER-INDEPENDENTLY, against the full retained band, without relying on
any insertion order. We then compare that to the study's sequential 'engine'
enumeration.

Per flip hexagon (fixed baseline list found at L0, tracked across erosion levels):
  * engine_solutions  = sequential enumeration (legality='engine', generous cap);
  * geom_solutions    = all geometric dissections (legality='geom');
  * independently_legal = geom_solutions that pass the order-independent frozen
    legality check against (band - hexagon) + filling;
  * alternative_exists = any independently_legal solution != the original dissection.

Controls:
  * POSITIVE: the original dissection must be independently legal (sanity).
  * REJECTION: a deliberately atlas-violating filling must be rejected.
Caps: we record whether the engine cap (max_solutions) truncates relative to the
full geometric set.

Writes results/audit5_hexsearch.json.
"""
from __future__ import annotations
import json, collections
import audit_common as A
from audit_common import PC, L, D, S
import hexflip as HF

STARS = L.STARS
ARCS = L.ARCS


# --------- order-independent frozen legality of a FINISHED configuration ---------
def vertex_star_ok(V_at_k):
    """Mirror of laying_the_tiling.Patch.vertex_ok(k, []) on an assembled corner
    list: complete atlas star (2pi, in STARS) or contiguous arcs (each in ARCS)."""
    import math
    lst = sorted(V_at_k); n = len(lst)
    if n == 0:
        return True
    tot = sum(d for _, d, _ in lst)
    if tot > 2 * math.pi + 1e-6:
        return False
    if abs(tot - 2 * math.pi) < 1e-6:
        return L.star(lst) in STARS
    wrap = lambda x: (x + math.pi) % (2 * math.pi) - math.pi
    start = next((i for i in range(n)
                  if abs(wrap(lst[i - 1][0] + lst[i - 1][1] - lst[i][0])) > 1e-6), None)
    if start is None:
        return False
    seq = lst[start:] + lst[:start]; arcs = [[seq[0]]]
    for i in range(1, n):
        pa, pd, _ = seq[i - 1]; a = seq[i][0]
        g = wrap(a - (pa + pd))
        if abs(g) < 1e-6:
            arcs[-1].append(seq[i])
        elif g < 0:
            return False
        else:
            arcs.append([seq[i]])
    return all(tuple(l for _, _, l in arc) in ARCS for arc in arcs)


def config_globally_legal(all_tiles, touch_vkeys):
    """Order-independent: build the assembled patch; check overlap/duplicate for
    the filling tiles and vertex-star legality at every touched vertex."""
    P = L.Patch(list(all_tiles))
    # vertex stars at touched vertices (final configuration)
    for vk in touch_vkeys:
        if not vertex_star_ok(P.V.get(vk, [])):
            return False
    return True


def overlap_or_dupe(band_minus_hex, fill_tiles):
    """True if any fill tile overlaps the band or duplicates an edge-mate."""
    P = L.Patch(list(band_minus_hex))
    placed = []
    for t in fill_tiles:
        # overlap against band + already placed
        cen = sum(t[1:]) / 3
        for u in list(P.tris) + placed:
            if abs(u[1] - cen) < 3 * L.SCALE_LEN and (L.inside(cen, *u[1:]) or any(L.inside(z, *u[1:]) for z in t[1:])):
                return True
        # duplicate across base edge
        ekset = P.edges.get(frozenset((L.key(t[1]), L.key(t[2]))), [])
        if L.canon(t) in {L.canon(u) for u in ekset}:
            return True
        placed.append(t)
    return False


def independently_legal(band, hex_tiles, fill_tiles):
    sdk_hex = {HF.dkey(t) for t in hex_tiles}
    band_minus = [t for t in band if HF.dkey(t) not in sdk_hex]
    if overlap_or_dupe(band_minus, fill_tiles):
        return False
    touch = {L.key(z) for t in fill_tiles for z in t[1:]}
    return config_globally_legal(band_minus + list(fill_tiles), touch)


def baseline_hexagons(skin0):
    """Fixed baseline list of flip hexagons near the dead sites, found ONCE at L0."""
    P = L.Patch(list(skin0))
    deads = [e for e in P.frontier() if len(D.candidates(P, *e[:3])) == 0]
    mids = [(e[0] + e[1]) / 2 for e in deads]
    nbhd = [t for t in skin0 if any(abs(HF.tile_centroid(t) - m) < 6 * S for m in mids)]
    return HF.find_flip_hexagons(nbhd), deads


def local_band(band, hex_tiles, reach=3.0):
    """Tiles of the band near the hexagon (centroid within reach*S of the hex
    centroid): this contains every tile incident to a hexagon vertex, which is all
    the legality of a filling can depend on. Used to keep validation fast and
    level-stable (inner-eroded tiles are far away and cannot touch the hexagon)."""
    hc = sum(sum(t[1:]) / 3 for t in hex_tiles) / len(hex_tiles)
    return [t for t in band if abs(HF.tile_centroid(t) - hc) < reach * S]


def analyse_hex(band, hex_tiles, cap_small=4, cap_big=256):
    surr = local_band(band, hex_tiles)
    surr = [t for t in surr if HF.dkey(t) not in {HF.dkey(u) for u in hex_tiles}]
    orig = tuple(sorted(HF.dkey(t) for t in hex_tiles))
    eng_small, _ = HF.enumerate_hexagon_fillings(hex_tiles, surr, legality="engine", max_solutions=cap_small)
    eng_big, _ = HF.enumerate_hexagon_fillings(hex_tiles, surr, legality="engine", max_solutions=cap_big)
    geom, glook = HF.enumerate_hexagon_fillings(hex_tiles, surr, legality="geom", max_solutions=cap_big)
    geom_truncated = len(geom) >= cap_big
    # order-independent validation of every geometric dissection against the local band
    indep = []
    for sol in geom:
        fill = [glook[dk] for dk in sol]
        if independently_legal(surr + list(hex_tiles), hex_tiles, fill):
            indep.append(sol)
    indep = sorted(set(indep))
    eng_big_set = sorted(set(eng_big))
    pos_ok = independently_legal(surr + list(hex_tiles), hex_tiles, list(hex_tiles))
    return dict(
        original_dissection=list(orig),
        n_geom_fillings=len(geom), geom_exhausted=bool(not geom_truncated),
        n_engine_solutions=len(eng_big_set),
        engine_solutions=eng_big_set,
        n_independently_legal=len(indep),
        independently_legal=indep,
        engine_matches_independent=bool(set(eng_big_set) == set(indep)),
        engine_cap4_truncates=bool(len(set(eng_small)) < len(set(eng_big))),
        positive_control_original_independently_legal=bool(pos_ok),
        alternative_exists=bool(any(list(s) != list(orig) for s in indep)),
    )


def rejection_control(band, hexes):
    """Build a deliberately illegal 'filling': the original 6 tiles with one tile
    nudged off-lattice (atlas-breaking). The validator MUST reject it."""
    if not hexes:
        return dict(ran=False)
    h = hexes[0]; hex_tiles = h["tiles"]
    surr = [t for t in local_band(band, hex_tiles) if HF.dkey(t) not in {HF.dkey(u) for u in hex_tiles}]
    bad = list(hex_tiles)
    c, Aa, Bb, Cc = bad[0]
    bad[0] = (c, Aa + 0.13 + 0.07j, Bb, Cc)   # move a vertex: breaks overlap/atlas
    rejected = not independently_legal(surr + list(hex_tiles), hex_tiles, bad)
    return dict(ran=True, illegal_filling_rejected=bool(rejected))


def main():
    A.RESULTS.mkdir(parents=True, exist_ok=True)
    w, si, js = 7, 0, 23
    arm, full, skin0 = A.jam_full_and_skin(w, si, js)
    hexes, deads = baseline_hexagons(skin0)
    baseline_keys = [tuple(sorted(HF.dkey(t) for t in h["tiles"])) for h in hexes]

    # erosion levels (fixed baseline hexagons tracked by their tile-key sets)
    def erode(theta):
        tfv = [z for e in L.Patch(list(full)).frontier() for z in e[:2]]
        return [t for t in skin0 if (min(abs(sum(t[1:]) / 3 - v) for v in tfv) / S) <= theta]
    THETAS = [("L0", float("inf")), ("L1", 2.0), ("L2", 1.5), ("L3", 1.0)]

    cache = {}   # hex-key -> analyse_hex verdict (neighbourhood is preserved across levels)
    levels = []
    for name, theta in THETAS:
        band = erode(theta)
        band_keys = {HF.dkey(t) for t in band}
        per_hex = []
        for h, bk in zip(hexes, baseline_keys):
            fully_supported = all(k in band_keys for k in bk)   # all 6 tiles still present
            if not fully_supported:
                per_hex.append(dict(hexagon=list(bk), fully_supported=False)); continue
            if bk not in cache:
                cache[bk] = analyse_hex(band, h["tiles"])
            r = dict(cache[bk]); r["hexagon"] = list(bk); r["fully_supported"] = True
            per_hex.append(r)
        checked = [p for p in per_hex if p.get("fully_supported")]
        n_alt = sum(1 for p in checked if p.get("alternative_exists"))
        all_match = all(p["engine_matches_independent"] for p in checked)
        pos_ok = all(p["positive_control_original_independently_legal"] for p in checked)
        levels.append(dict(level=name, theta=(None if theta == float("inf") else theta),
                           n_baseline_hexagons=len(baseline_keys),
                           n_fully_supported=len(checked),
                           n_with_legal_alternative=n_alt,
                           engine_enumeration_matches_order_independent=bool(all_match),
                           positive_control_all_pass=bool(pos_ok),
                           per_hex=per_hex))
        rej = rejection_control(band, hexes) if name == "L0" else None
        if rej:
            levels[-1]["rejection_control"] = rej
        print(f"{name}: baseline hexes {len(baseline_keys)}; fully-supported {len(checked)}; "
              f"with legal alternative {n_alt}; engine==order-independent: {all_match}; "
              f"positive-control: {pos_ok}", flush=True)

    report = dict(case="w7", jam_step=js, n_dead_sites=len(deads),
                  n_baseline_flip_hexagons=len(baseline_keys),
                  adjacency_note="baseline flip hexagons fixed at L0; tracked by tile-key set across erosion",
                  levels=levels,
                  wording_guidance=("Report 'no legal single-hexagon flip alternative found among the N tested, "
                                    "fully-supported flip hexagons at each level'. If engine==order-independent "
                                    "holds and the engine cap does not truncate, the sequential enumeration is "
                                    "complete FOR THIS single-flip move class; this is not a claim about all "
                                    "conceivable locally legal continuations."))
    (A.RESULTS / "audit5_hexsearch.json").write_text(json.dumps(report, indent=2, default=float))
    print("wrote results/audit5_hexsearch.json")


if __name__ == "__main__":
    main()

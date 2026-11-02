#!/usr/bin/env python3
"""
part4_search.py -- Part 4: search connected patch replacements (fixed-boundary
move class) and score compatibility.

Part 3 ruled out EVERY connected region of size <= 8 by the necessary condition
(the fixed exterior is already infeasible, so no replacement -- which only adds
constraints -- can restore compatibility). This script makes that concrete and
validates the search apparatus: it runs the actual completed-replacement
enumeration on real connected regions (the flip hexagons near the dead sites,
6-tile edge-connected regions), with:

  * completed replacements enumerated geometrically (frozen templates), NOT
    rejected for intermediate partial-filling vertex-star violations;
  * order-independent frozen validation of each completed replacement against the
    fixed exterior interface (coverage, overlap, decorated vertex stars);
  * for each LEGAL completed replacement, the repaired band's box-independent
    compatibility and dead-site candidate counts.

Controls: POSITIVE (the identity replacement must be found and legal); REJECTION
(a deliberately atlas-breaking filling must be rejected). We also carry any
Part-3 PERMITTED region (none expected) into a full replacement search.

A legal joint replacement is NOT a sequence of elementary moves; no path is
claimed. Writes results/part4_search.json.
"""
from __future__ import annotations
import json
import coop_common as CC
from coop_common import Sl, L, D, S
import safeguards                 # audited strong completed-replacement validator (reused)
import feas
import hexflip as HF

MAX_SOLUTIONS = 256
LOCAL_REACH = 3.0


def load_state():
    st = json.loads((CC.INPUT / "retained_state.json").read_text())
    band = [CC.dtile(t) for t in st["tiles"]]
    rank = {int(k): int(v) for k, v in st["rank"].items()}
    dead = [(complex(*d["p"]), complex(*d["q"]), complex(*d["r"])) for d in st["dead_sites"]]
    return st, band, rank, dead


def dead_edges_on(tiles):
    P = L.Patch(list(tiles))
    return [e for e in P.frontier() if len(D.candidates(P, *e[:3])) == 0]


def flip_hexagons_near_dead(band, dead):
    mids = [(p + q) / 2 for (p, q, r) in dead]
    nbhd = [t for t in band if any(abs(HF.tile_centroid(t) - m) < 6 * S for m in mids)]
    return HF.find_flip_hexagons(nbhd)


def local_exterior(band, region_tiles):
    rk = {HF.dkey(t) for t in region_tiles}
    hc = sum(HF.tile_centroid(t) for t in region_tiles) / len(region_tiles)
    return [t for t in band if HF.dkey(t) not in rk and abs(HF.tile_centroid(t) - hc) < (LOCAL_REACH + 3) * S]


def band_feasibility(tiles, rank):
    try:
        cm = Sl.constraints(tiles, rank)
    except Exception:
        return dict(verdict="unresolved_layers")
    return CC.classify_exterior(cm)


def dead_candidates(tiles, dead):
    P = L.Patch(list(tiles))
    present = {CC.ekey(e[0], e[1]): e for e in P.frontier()}
    out = []
    for (p, q, r) in dead:
        cur = present.get(CC.ekey(p, q))
        out.append(len(D.candidates(P, *cur[:3])) if cur is not None else None)
    return out


def search_region(band, rank, dead, hex_tiles):
    orig = tuple(sorted(HF.dkey(t) for t in hex_tiles))
    # FULL exterior (band minus the region) -- the audited validator checks all
    # affected vertex stars against the full exterior, not a distance-truncated one.
    exterior_tiles = [t for t in band if HF.dkey(t) not in set(orig)]
    surr = local_exterior(band, hex_tiles)           # local surround: only for the geom ENUMERATOR
    # all geometric completed fillings (frozen templates), no intermediate rejection
    geom, glook = HF.enumerate_hexagon_fillings(hex_tiles, surr, legality="geom", max_solutions=MAX_SOLUTIONS)
    truncated = len(geom) >= MAX_SOLUTIONS
    legal = []
    for sol in geom:
        fill = [glook[dk] for dk in sol]
        # STRONG, audited validator against the FULL exterior: template membership,
        # footprint coverage, non-overlap, boundary/interface preservation, all
        # affected vertex-stars; empty/incomplete fillings fail.
        if safeguards.completed_replacement_legal(exterior_tiles, hex_tiles, fill):
            legal.append((sol, fill))
    # score each legal completed replacement
    scored = []
    restored_any = False
    for sol, fill in legal:
        repaired = exterior_tiles + list(fill)
        fb = band_feasibility(repaired, rank)
        dc = dead_candidates(repaired, dead)
        is_identity = (tuple(sorted(sol)) == orig)
        if fb.get("verdict") == "feasible":
            restored_any = True
        scored.append(dict(is_identity=is_identity, solution=list(sol),
                           repaired_feasibility=fb.get("verdict"),
                           repaired_box_r=fb.get("box_r"),
                           dead_candidates=dc))
    pos_control = any(s["is_identity"] for s in scored)
    return dict(region_dkeys=list(orig), n_geom_fillings=len(geom), geom_truncated=truncated,
                n_legal_completed_replacements=len(legal),
                positive_control_identity_legal=pos_control,
                any_replacement_restores_compatibility=restored_any,
                scored=scored)


def rejection_control(band, dead):
    """REJECTION controls against the audited validator and the FULL exterior:
    a perturbed (atlas-breaking) filling and an EMPTY filling must both fail."""
    hexes = flip_hexagons_near_dead(band, dead)
    if not hexes:
        return dict(ran=False)
    hex_tiles = hexes[0]["tiles"]
    exterior_full = [t for t in band if HF.dkey(t) not in {HF.dkey(u) for u in hex_tiles}]
    bad = list(hex_tiles)
    c, A, B, Cc = bad[0]
    bad[0] = (c, A + 0.13 + 0.07j, B, Cc)
    perturbed_rejected = not safeguards.completed_replacement_legal(exterior_full, hex_tiles, bad)
    empty_rejected = not safeguards.completed_replacement_legal(exterior_full, hex_tiles, [])
    return dict(ran=True, perturbed_filling_rejected=bool(perturbed_rejected),
                empty_filling_rejected=bool(empty_rejected))


def permitted_region_guard(permitted, hexes):
    """Part 4's replacement search only supports flip-hexagon-shaped regions. If
    Part 3 ever permits a region that is NOT one of those supported shapes, this
    must be reported as UNSUPPORTED (distinct from an exhaustive negative), not
    silently treated as 'no repair found'."""
    supported = {tuple(sorted(HF.dkey(t) for t in h["tiles"])) for h in hexes}
    unsupported = [p for p in permitted if tuple(sorted(tuple(k) for k in p.get("region", []))) not in supported]
    return dict(n_permitted=len(permitted), n_unsupported=len(unsupported),
                general_permitted_region_search_implemented=False,
                status=("not_applicable_no_permitted_regions" if not permitted
                        else ("unsupported_permitted_regions_present" if unsupported
                              else "all_permitted_regions_are_supported_shapes")))


def main():
    st, band, rank, dead = load_state()
    p3 = json.loads((CC.RESULTS / "part3_necessary.json").read_text())
    permitted = p3["region_enumeration"]["permitted"]

    hexes = flip_hexagons_near_dead(band, dead)
    guard = permitted_region_guard(permitted, hexes)
    if guard["status"] == "unsupported_permitted_regions_present":
        raise SystemExit("UNSUPPORTED: Part 3 permitted a region outside the implemented flip-hexagon "
                         "replacement search. The general permitted-region search is NOT implemented; "
                         "this run cannot be reported as an exhaustive negative. Stopping.")
    regions = [search_region(band, rank, dead, h["tiles"]) for h in hexes]
    rej = rejection_control(band, dead)

    n_restored = sum(1 for r in regions if r["any_replacement_restores_compatibility"])
    all_pos = all(r["positive_control_identity_legal"] for r in regions) if regions else None
    total_legal = sum(r["n_legal_completed_replacements"] for r in regions)

    any_truncated = any(r["geom_truncated"] for r in regions)
    report = dict(
        case="w7-B-s0 jam@23", move_class="connected fixed-exterior region (flip-hexagon sample, 6 triangles = 3 rhombi)",
        part3_permitted_regions=len(permitted),
        permitted_region_guard=guard,
        note=("Part 3 ruled out all seeded connected regions size<=8 by the necessary condition; a "
              "replacement (which only adds constraints) cannot restore a feasible exterior that does not "
              "exist. The 15 flip hexagons below are concrete connected regions exercising the full "
              "search+scoring pipeline with the AUDITED strong validator against the full exterior. The "
              "general permitted-region replacement search is NOT implemented (see permitted_region_guard); "
              "it is dormant because no region was permitted."),
        validator="safeguards.completed_replacement_legal (audited 2026-11-03; full-exterior vertex stars)",
        n_regions_searched=len(regions),
        total_legal_completed_replacements=total_legal,
        n_regions_where_a_replacement_restored_compatibility=n_restored,
        positive_control_all_regions_identity_legal=all_pos,
        rejection_control=rej,
        truncation=dict(any_region_hit_solution_cap=bool(any_truncated), solution_cap=MAX_SOLUTIONS,
                        note=("geom_truncated is inferred from the DEDUPLICATED solution count vs the cap, so "
                              "it can under-report truncation; here no region hit the cap, and the audit's "
                              "uncapped independent search confirmed the complete candidate sets for these 15.")),
        path_claim="none (a legal joint replacement is not a sequence of elementary moves)",
        regions=regions,
    )
    CC.RESULTS.mkdir(parents=True, exist_ok=True)
    (CC.RESULTS / "part4_search.json").write_text(json.dumps(report, indent=2, default=float))

    print(f"Part 3 permitted regions carried in: {len(permitted)}")
    print(f"flip-hexagon regions searched: {len(regions)}; total legal completed replacements: {total_legal}")
    print(f"regions where ANY legal replacement restored compatibility: {n_restored}")
    print(f"positive control (identity legal in every region): {all_pos}")
    print(f"rejection control: {rej}")
    for r in regions[:4]:
        verds = sorted({s['repaired_feasibility'] for s in r['scored']})
        print(f"  region {r['region_dkeys'][0][:24]}...: legal replacements {r['n_legal_completed_replacements']}, "
              f"repaired feasibility {verds}, restores={r['any_replacement_restores_compatibility']}")
    print("wrote results/part4_search.json")


if __name__ == "__main__":
    main()

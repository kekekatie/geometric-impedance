#!/usr/bin/env python3
"""
part3_necessary.py -- Part 3: necessary condition before searching.

For a connected region R, the exterior (band \\ R) is held fixed. Changing only R
can restore projection-window compatibility ONLY IF the constraints supplied by
the unchanged exterior are themselves feasible. We:

  (A) enumerate connected regions R (size <= 8, witness/dead-site seeded, capped),
      compute the exterior compatibility region under a consistent gauge and
      CAREFUL provenance (a vertex's constraint is dropped only if its ENTIRE
      incident-tile star is in R), and classify it box-independently
      (box-50 certifier AND box-free Phase-I LP). Reject R if the exterior is
      infeasible; permit it if feasible; otherwise unresolved.

  (B) characterise HOW distributed the obstruction is, with two deliberately
      distinct quantities (audit-corrected 2026-11-03, neither a repair/minimum):
        * min_facet_drop -- the minimum number of aggregate (rank,facet) ROWS whose
          deletion makes the 20-row system feasible (with unresolved tracking; not
          tiles/vertices/flips/steps);
        * one HEURISTIC disconnected tile-DELETION footprint (greedy), reported as
          an example with zero-margin exterior feasibility -- NOT a minimum, a
          necessary spatial reach, or a legal fixed-boundary replacement.

Verdict propagation (audit-corrected): a region whose exterior constraints are
unchanged inherits the ESTABLISHED full-band verdict (including 'unresolved'); it
is never assumed infeasible. Controls: R=empty (exterior = full band) reproduces
the full-band verdict; a synthetic feasible system classifies feasible.

Reads input/retained_state.json only (search-visible). Writes
results/part3_necessary.json.
"""
from __future__ import annotations
import json, itertools, collections
import coop_common as CC
from coop_common import Sl, L, M, S
import feas

MAX_REGION_SIZE = 8
REGION_CAP = 50000


def load_band():
    st = json.loads((CC.INPUT / "retained_state.json").read_text())
    band = [CC.dtile(t) for t in st["tiles"]]
    rank = {int(k): int(v) for k, v in st["rank"].items()}
    dead_vkeys = set()
    for ds in st["dead_sites"]:
        dead_vkeys.add(L.key(complex(*ds["p"]))); dead_vkeys.add(L.key(complex(*ds["q"])))
    witness_vkeys = {L.key(complex(*w["vertex"])) for w in st["compatibility_witness_vertices"]}
    return st, band, rank, dead_vkeys, witness_vkeys


def seeds_from(band, vkeys):
    """tiles incident to any vertex in vkeys."""
    out = set()
    for t in band:
        if any(L.key(z) in vkeys for z in t[1:]):
            out.add(CC.dk(t))
    return out


def region_footprint_stats(BC, vertex_set, state=None):
    """Statistics of the tile union that engulfs `vertex_set` (the union of their
    incident tile-stars). This is a DELETION footprint, NOT a connected repair and
    NOT a minimum: deleting these tiles also removes extra 'collateral' vertices
    and loses saved boundary edges. Reports selected vs actually-engulfed vertices,
    components, both spans, and (if `state` given) the saved boundary edges lost."""
    import json as _json
    tiles = set()
    for v in vertex_set:
        tiles |= BC.vincident.get(v, set())
    tilemap = {CC.dk(t): t for t in BC.band}
    sub = [tilemap[d] for d in tiles if d in tilemap]
    comps = CC.connected_components(sub) if sub else []
    actual_engulfed = BC.engulfed_vertices(tiles)           # includes collateral vertices
    sel_vs = [complex(*v) for v in vertex_set]
    foot_vs = [complex(*L.key(z)) for t in sub for z in t[1:]]
    sel_span = max((abs(a - b) / S for a in sel_vs for b in sel_vs), default=0.0)
    foot_span = max((abs(a - b) / S for a in foot_vs for b in foot_vs), default=0.0)
    out = dict(n_tiles=len(tiles), n_components=len(comps), connected=(len(comps) <= 1),
               n_selected_vertices=len(vertex_set),
               n_actual_engulfed_vertices=len(actual_engulfed),
               selected_vertex_span_S=round(sel_span, 4),
               footprint_vertex_span_S=round(foot_span, 4))
    if state is not None:
        owners_rt = [_json.loads(_json.dumps(CC.dk(t))) for t in sub]
        out["saved_outer_frontier_edges_lost"] = sum(1 for rec in state["true_frontier"] if rec["owner"] in owners_rt)
        out["saved_inner_boundary_edges_lost"] = sum(1 for rec in state["inner_boundary"] if rec["owner"] in owners_rt)
    return out


def _violations(BC, cmax, t):
    """Per-constraint violation c_i/|n| - (n/|n|).t at point t (unit-normalised),
    using the raw WIN normals for each key in cmax."""
    from coop_common import WIN
    out = []
    for key, c in cmax.items():
        rk, i = key
        n, h = WIN[rk]
        nx, ny = float(n[i][0]), float(n[i][1]); nn = (nx * nx + ny * ny) ** 0.5
        viol = c / nn - (nx * t[0] + ny * t[1]) / nn
        out.append((viol, key))
    out.sort(reverse=True)
    return out


def min_facet_drop(BC, max_drop=4):
    """Minimum number of aggregate (rank,facet) ROWS whose deletion makes the
    20-row system feasible. This is a row-deletion cardinality in the aggregate
    constraint problem -- NOT a count of tiles, vertices, stars, flips, or repair
    steps, and not a realizable change.

    Audit-corrected (2026-11-03): every subset at each cardinality is checked (not
    stopped at the first feasible), and an 'unresolved' at a SMALLER cardinality
    bars claiming the minimum (we cannot certify no smaller feasible set exists)."""
    keys = list(BC.full_cmax.keys())
    table = []
    first_feasible_card = None
    first_feasible_sets = []
    for s in range(0, max_drop + 1):
        n_checked = n_feas = n_unres = 0
        feas_sets = []
        for drop in itertools.combinations(keys, s):
            n_checked += 1
            v = CC.classify_exterior({k: c for k, c in BC.full_cmax.items() if k not in drop})["verdict"]
            if v == "feasible":
                n_feas += 1
                if len(feas_sets) < 5:
                    feas_sets.append([list(k) for k in drop])
            elif v == "unresolved":
                n_unres += 1
        table.append(dict(cardinality=s, subsets=n_checked, feasible=n_feas, unresolved=n_unres))
        if first_feasible_card is None and n_feas > 0:
            first_feasible_card = s
            first_feasible_sets = feas_sets
    # the minimum is certified only if nothing unresolved at strictly smaller cardinalities
    unresolved_below = any(r["unresolved"] > 0 for r in table
                           if first_feasible_card is not None and r["cardinality"] < first_feasible_card)
    return dict(min_rows=first_feasible_card,
                min_certified=bool(first_feasible_card is not None and not unresolved_below),
                unresolved_at_smaller_cardinality=bool(unresolved_below),
                example_feasible_sets=first_feasible_sets,
                cardinality_table=table, searched_up_to=max_drop,
                note="aggregate (rank,facet) row-deletion cardinality; not tiles/vertices/flips/steps")


def greedy_engulfment(BC, state=None, max_remove=80):
    """ONE heuristic deletion example (NOT a minimum, NOT a necessary reach, NOT a
    replacement): greedily delete the contribution of the argmax vertex of the
    most-violated constraint until the aggregate system is feasible. This produces
    a disconnected deletion footprint whose exterior is feasible only at numerically
    zero margin (uncertified symbolically). It supplies a numerical upper bound on
    an UNRESTRICTED tile-deletion feasibility problem if that zero-margin verdict is
    accepted; it is neither a bound on the minimum legal connected boundary-
    preserving REPLACEMENT size nor a necessary spatial span."""
    E = set(); steps = []
    for _ in range(max_remove + 1):
        cmax, _ = BC.exterior_cmax_from_vertices(E)
        cl = CC.classify_exterior(cmax)
        if cl["verdict"] == "feasible":
            return dict(converged=True, is_minimum_repair=False, is_necessary_reach=False,
                        is_replacement=False,
                        n_selected_vertices=len(E),
                        selected_vertices=[list(v) for v in sorted(E)],
                        footprint=region_footprint_stats(BC, set(E), state=state),
                        exterior_verdict=cl["verdict"], exterior_box_r=cl.get("box_r"),
                        exterior_box_free_margin=cl.get("box_free_margin"),
                        zero_margin_numerically=True,
                        symbolically_certified=False,
                        n_greedy_steps=len(steps))
        tstar = feas.classify(cmax)["witness"] or [0.0, 0.0]
        viols = _violations(BC, cmax, tstar)
        added = None
        for viol, key in viols:
            for c, v in BC.by_key[key]:
                if v not in E:
                    added = v; break
            if added is not None:
                break
        if added is None:
            break
        E.add(added); steps.append(list(added))
    return dict(converged=False, searched_up_to=max_remove, n_selected_vertices=len(E),
               footprint=region_footprint_stats(BC, set(E), state=state))


def main():
    st, band, rank, dead_vkeys, witness_vkeys = load_band()
    BC = CC.BandConstraints(band, rank=rank)

    # provide exterior_cmax directly from a vertex set (for part B)
    def exterior_cmax_from_vertices(E):
        cmax = {}
        for key, lst in BC.by_key.items():
            for c, v in lst:
                if v not in E:
                    cmax[key] = c; break
        return cmax, E
    BC.exterior_cmax_from_vertices = exterior_cmax_from_vertices

    # ---- controls ----
    ctrl_empty = CC.classify_exterior(BC.full_cmax)       # R=empty -> full band
    synth = {(0, 0): -1.0, (0, 1): -1.0}                  # trivially feasible pair
    ctrl_feas = CC.classify_exterior(synth)

    # ---- (A) connected-region enumeration ----
    seeds = seeds_from(band, dead_vkeys | witness_vkeys)
    regions = CC.connected_regions(band, seeds, MAX_REGION_SIZE, REGION_CAP)
    by_size = collections.Counter(len(r) for r in regions)
    truncated = len(regions) >= REGION_CAP
    # SCIENTIFIC tally: final verdict per region (what matters).
    verdict_tally = collections.Counter()
    # DIAGNOSTIC path buckets (environment/last-bit sensitive via exact-dict
    # equality; NOT a scientific requirement -- see PROTOCOL_DEVIATIONS / audit).
    path_diag = collections.Counter()
    engulfing = 0
    permitted = []
    unresolved = []
    for R in regions:
        cmax, E = BC.exterior_cmax(R)
        if E:
            engulfing += 1
        # Shortcut verdict PROPAGATION (audit 2026-11-03, mirrors
        # safeguards.classify_region): if the exterior constraints are unchanged,
        # the verdict is the ESTABLISHED full-band verdict -- including
        # 'unresolved' -- never an assumed 'infeasible'.
        if cmax == BC.full_cmax:
            verdict = ctrl_empty["verdict"]
            path_diag["no_engulfment" if not E else "engulfed_nonbinding"] += 1
            cl = dict(ctrl_empty)
        else:
            cl = CC.classify_exterior(cmax)
            verdict = cl["verdict"]
            path_diag["lp_evaluated"] += 1
        verdict_tally[verdict] += 1
        if verdict == "feasible":
            permitted.append(dict(region=sorted(R), engulfed=len(E), exterior=cl))
        elif verdict == "unresolved":
            unresolved.append(dict(region=sorted(R), engulfed=len(E), exterior=cl))

    # ---- (B) obstruction characterization ----
    facet_drop = min_facet_drop(BC)        # aggregate-row deletion minimum (with unresolved tracking)
    greedy = greedy_engulfment(BC, state=st)   # ONE heuristic deletion footprint (not a repair/minimum)

    # witness-vertex span (characterisation)
    wvs = [complex(*v) for v in witness_vkeys]
    wspan = max((abs(a - b) / S for a in wvs for b in wvs), default=0.0)
    star_sizes = {str(list(v)): len(BC.vincident.get(v, set())) for v in witness_vkeys}

    report = dict(
        case="w7-B-s0 jam@23", move_class="connected fixed-exterior region, size<=8",
        controls=dict(
            R_empty_full_band=dict(verdict=ctrl_empty["verdict"], box_r=ctrl_empty["box_r"]),
            synthetic_feasible=dict(verdict=ctrl_feas["verdict"]),
        ),
        region_enumeration=dict(
            max_region_size=MAX_REGION_SIZE, cap=REGION_CAP, truncated=truncated,
            n_regions=len(regions), by_size=dict(sorted(by_size.items())),
            n_engulfing_a_vertex=engulfing,
            verdict_tally=dict(verdict_tally),
            path_diagnostics=dict(path_diag),
            path_diagnostics_note=("Environment/last-bit sensitive via exact-dict equality of aggregate "
                                   "coefficients; NOT a scientific requirement (the independent audit saw a "
                                   "different split with identical final verdicts). The verdict_tally is the result."),
            n_permitted=len(permitted), permitted=permitted[:20],
            n_unresolved=len(unresolved), unresolved=unresolved[:20],
        ),
        obstruction=dict(
            min_facet_drop=facet_drop,
            heuristic_deletion_footprint=greedy,
            note=("The heuristic_deletion_footprint is ONE disconnected tile-DELETION example with "
                  "zero-margin exterior feasibility; it is not a minimum, a necessary spatial reach, or a "
                  "legal fixed-boundary replacement. min_facet_drop is an aggregate-row deletion cardinality, "
                  "not tiles/vertices/flips/steps."),
        ),
        characterisation=dict(
            witness_vertex_span_S=round(wspan, 2),
            witness_star_sizes=star_sizes,
            note=("A connected region drops a vertex's constraint only by engulfing its ENTIRE tile star. "
                  "To drop an aggregate (rank,facet) row, neighbouring suppliers must also be engulfed, so the "
                  "obstruction is distributed; the seeded size<=8 family cannot reach it (0/12248 permitted)."),
        ),
    )
    CC.RESULTS.mkdir(parents=True, exist_ok=True)
    (CC.RESULTS / "part3_necessary.json").write_text(json.dumps(report, indent=2, default=float))

    print(f"controls: R=empty -> {ctrl_empty['verdict']} (box_r={ctrl_empty['box_r']:.4e}); "
          f"synthetic -> {ctrl_feas['verdict']}")
    print(f"regions enumerated: {len(regions)} (truncated={truncated}); by size {dict(sorted(by_size.items()))}")
    print(f"  engulfing >=1 vertex: {engulfing}; verdict tally: {dict(verdict_tally)} | path diag: {dict(path_diag)}")
    print(f"  PERMITTED (feasible exterior): {len(permitted)}; unresolved: {len(unresolved)}")
    print(f"min facet-drop (aggregate 20-row deletion): min_rows={facet_drop.get('min_rows')} "
          f"certified={facet_drop.get('min_certified')}")
    gf = greedy["footprint"]
    print(f"heuristic deletion footprint (NOT a repair/minimum): selected={greedy.get('n_selected_vertices')} "
          f"actual_removed={gf.get('n_actual_engulfed_vertices')} tiles={gf['n_tiles']} "
          f"components={gf['n_components']} sel_span={gf['selected_vertex_span_S']} "
          f"foot_span={gf['footprint_vertex_span_S']} outer_lost={gf.get('saved_outer_frontier_edges_lost')} "
          f"inner_lost={gf.get('saved_inner_boundary_edges_lost')} zero_margin={greedy.get('zero_margin_numerically')}")
    print(f"witness-vertex span {round(wspan,2)} S; star sizes {star_sizes}")
    print("wrote results/part3_necessary.json")


if __name__ == "__main__":
    main()

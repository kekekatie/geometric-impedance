#!/usr/bin/env python3
"""
verify_supplement.py -- dated verification supplement (2026-11-04) for the
archive-free scar-continuation experiment (reviewed commit 129389d).

Strengthens the checks that the original handback's wording outran, WITHOUT
changing the retention rule, scheduler, matching rules, reader thresholds, cases,
or step-44 horizon. Per case it runs the full-patch comparator and the radius-2
ActiveSkin worker in lockstep and records:

  (A) ORDERED equivalence -- ordered placements, ordered frontier, the ACTUAL
      ordered candidate enumeration used by free choice (`SN.ordered(candidates)`,
      NOT the sorted `inventory`), and PRNG state before AND after each step --
      kept distinct from set-only `inventory` agreement.
  (B) INDEPENDENT legality -- a separate evaluator-only cumulative FULL-history
      patch, grown from the worker's actual placements in order; every worker
      addition is checked with frozen `Patch.legal` against that history BEFORE
      adding (this also tests for construction into deleted occupied space). Final
      endpoint: complete decorated vertex stars + independent convex-clipping
      overlap check.
  (C) PRE-SCAR restart alignment -- the worker state is serialized at the TOP of
      the jam step (BEFORE the first scar-tolerant batch) and aligned against the
      frozen jam checkpoint (geometry, ordered true frontier, PRNG, empty scars).
      The spawned-restart run itself is in `restart_prescar.py`.
  (D) METADATA depth -- boundary owner tiles/coords vs retained geometry; worker
      caches/indexes after pruning; no deleted-tile collection or geometry history
      in the serialized state or reachable worker data; current blocked edges vs
      cumulative scar labels; cavity edges excluded from the frontier.

The worker never consults the evaluator's history; evaluator findings never feed
back into the worker.
"""
from __future__ import annotations
import sys, json, random, math
from pathlib import Path
SRC = str(Path(__file__).resolve().parents[1] / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
import af_common as AF
from af_common import E, L, D, S, PC, SN, ordered, dk, frontier_id
import isolated_worker as IW
import scar_continuation as SCN

RESULTS = Path(__file__).resolve().parent / "results"
INPUT = Path(__file__).resolve().parent / "input"

# Test-only injection hook for the failure-stop regression (test_failstop.py). It is
# None for every scientific run, so it never touches recorded results. When set, it is
# called as hook(step, batch_position, tile, legal) -> bool and may override the
# evaluator's legality verdict to exercise the failure-stop path.
_FORCE_ILLEGAL = None


# ---- independent convex clipping (adopted verbatim from audit_2026-11-03/audit_common.py) ----
def _area(poly):
    return abs(sum((a.conjugate() * b).imag for a, b in zip(poly, poly[1:] + poly[:1]))) / 2 if len(poly) > 2 else 0.0


def _intersection(a, b):
    out = list(a); sign = 1 if sum((p.conjugate() * q).imag for p, q in zip(b, b[1:] + b[:1])) > 0 else -1
    for p, q in zip(b, b[1:] + b[:1]):
        old = out; out = []
        if not old:
            break
        f = lambda z: sign * ((q - p).conjugate() * (z - p)).imag
        for u, v in zip(old, old[1:] + old[:1]):
            fu, fv = f(u), f(v)
            if fu >= -1e-15:
                out.append(u)
            if (fu >= -1e-15) != (fv >= -1e-15):
                out.append(u + (v - u) * fu / (fu - fv))
    return out


def overlap_check(tiles):
    boxes = [(min(z.real for z in t[1:]), max(z.real for z in t[1:]),
              min(z.imag for z in t[1:]), max(z.imag for z in t[1:])) for t in tiles]
    pairs = 0; bad = []; maxarea = 0.0
    for i, a in enumerate(boxes):
        for j in range(i):
            b = boxes[j]
            if min(a[1], b[1]) - max(a[0], b[0]) <= 1e-12 or min(a[3], b[3]) - max(a[2], b[2]) <= 1e-12:
                continue
            pairs += 1
            value = _area(_intersection(list(tiles[i][1:]), list(tiles[j][1:]))); maxarea = max(value, maxarea)
            if value > 1e-12:
                bad.append([i, j, value])
    return dict(test_pairs=pairs, max_intersection_area=maxarea, positive_area_overlaps=bad, area_tolerance=1e-12)


def tile_id(t):
    return repr(dk(t))


def ordered_inventory(P):
    """The ACTUAL enumeration order the scheduler draws from (SN.ordered), per
    frontier edge -- NOT the sorted `inventory`."""
    return [(frontier_id(e), [tile_id(t) for t in ordered(D.candidates(P, *e[:3]))]) for e in P.frontier()]


def complete_star_check(patch):
    """Every vertex at angle sum 2*pi must be a valid atlas star; none over-full."""
    bad_complete = 0; overfull = 0; n_complete = 0
    for k, lst in patch.V.items():
        tot = sum(d for _, d, _ in lst)
        if tot > 2 * math.pi + 1e-6:
            overfull += 1
        elif abs(tot - 2 * math.pi) < 1e-6:
            n_complete += 1
            if L.star(lst) not in L.STARS:
                bad_complete += 1
    return dict(n_complete_vertices=n_complete, invalid_complete_stars=bad_complete, overfull_vertices=overfull)


def verify_case(world, si):
    jp = AF.jam_prep(world, si)
    Sstar, B, stream, jam_step = jp["Sstar"], jp["B"], jp["stream"], jp["jam_step"]
    full_jam, band_jam = jp["full_jam"], jp["band"]

    full = L.Patch(list(Sstar)); full.add(B)
    skin = E.ActiveSkin(list(Sstar) + [B], radius=2)
    rng_e = random.Random(stream); rng_w = random.Random(stream)
    scars_e = set(); scars_w = set()
    worker_hist = L.Patch(list(Sstar) + [B])      # independent cumulative FULL history of the worker's trajectory

    ordered_mismatch = None; set_mismatch = None; legality_fail = None
    prescar = None; prescar_state = None
    checked_steps = []; placements_validated = 0
    growth_steps = 0; validation_failed = False; arrested = False
    for s in range(1, 45):
        if s == jam_step:
            prescar_state = IW.serialize_state(skin, rng_w, scars_w)
            prescar = dict(step=s,
                           geometry_matches_frozen_jam=({dk(t) for t in skin.tris} == {dk(t) for t in band_jam}),
                           ordered_frontier_matches=([frontier_id(e) for e in skin.frontier()] ==
                                                     [frontier_id(e) for e in L.Patch(list(full_jam)).frontier()]),
                           prng_matches_evaluator=(rng_w.getstate() == rng_e.getstate()),
                           scars_empty=(len(scars_w) == 0 and len(scars_e) == 0),
                           n_worker_band=len(skin.tris), n_frozen_band=len(band_jam))

        oi_e = ordered_inventory(full); oi_w = ordered_inventory(skin)
        si_e = E.inventory(full); si_w = E.inventory(skin)
        pb_e = rng_e.getstate(); pb_w = rng_w.getstate()

        n0e = len(full.tris)
        st_e, n_e, k_e, new_e, il_e = SCN.patient_scar(full, rng_e, scars_e, verify_legal=True)
        placed_e = list(full.tris[n0e:])
        skin.additions = []
        st_w, n_w, k_w, new_w, il_w = SCN.patient_scar(skin, rng_w, scars_w, verify_legal=True)
        placed_w = list(skin.additions); skin.additions = []
        skin.prune()
        growth_steps += 1

        ord_placed = ([dk(t) for t in placed_w] == [dk(t) for t in placed_e])
        ord_front = ([frontier_id(e) for e in skin.frontier()] == [frontier_id(e) for e in full.frontier()])
        ord_cand = (oi_w == oi_e)
        set_inv = (si_w == si_e)
        pa = (rng_w.getstate() == rng_e.getstate())
        pbm = (pb_w == pb_e)
        outcome_match = ((st_w, n_w, k_w) == (st_e, n_e, k_e))
        checked_steps.append(s)
        if ordered_mismatch is None and not (ord_placed and ord_front and ord_cand and pa and pbm and outcome_match):
            ordered_mismatch = dict(step=s, ordered_placements=ord_placed, ordered_frontier=ord_front,
                                    ordered_candidate_enumeration=ord_cand, prng_before=pbm, prng_after=pa,
                                    outcome=outcome_match, set_inventory_agrees=set_inv)
        if set_mismatch is None and not set_inv:
            set_mismatch = dict(step=s)

        # Independent legality of each worker placement vs the worker's cumulative FULL
        # history. NOTE: patient_scar above already COMPUTED and placed this step's batch
        # into the worker (placed_w) BEFORE the evaluator validates it here. Validation is
        # a read-only audit of that already-computed batch; it never feeds back into the
        # worker. On the first failure the whole trial stops before the next growth step,
        # and the unvalidated remainder of the batch is NOT accepted into history.
        for idx, t in enumerate(placed_w):
            legal = worker_hist.legal(t)
            if _FORCE_ILLEGAL is not None:          # test-only injection; None in all scientific runs
                legal = _FORCE_ILLEGAL(s, idx, t, legal)
            if not legal:
                legality_fail = dict(
                    step=s, batch_position=idx, batch_size=len(placed_w), tile=repr(dk(t)),
                    # evaluator pre-state sufficient to reproduce: the validated history
                    # just before the offending add (decorated keys), plus the offending
                    # candidate and the unaccepted remainder of this already-computed batch.
                    evaluator_pre_state_keys=sorted(repr(dk(u)) for u in worker_hist.tris),
                    unvalidated_remainder=[repr(dk(u)) for u in placed_w[idx:]],
                    note=("worker batch for this step was computed by patient_scar before "
                          "evaluator validation; the remainder from batch_position onward is "
                          "NOT accepted as history and the trial stops before the next step"))
                validation_failed = True
                break
            worker_hist.add(t); placements_validated += 1

        if validation_failed:
            break      # stop the entire trial: no subsequent growth step executes
        if st_e == "total_arrest" or st_w == "total_arrest":
            arrested = True
            break

    # endpoint geometry: worker's cumulative construction history + the retained band
    stars_hist = complete_star_check(worker_hist)
    ov_hist = overlap_check(worker_hist.tris)
    ov_band = overlap_check(list(skin.tris))

    # current blocked edges vs cumulative labels at the final checkpoint
    cur_blocked = [e for e in skin.frontier() if len(D.candidates(skin, *e[:3])) == 0]

    # metadata depth
    full_keys = {dk(t) for t in full.tris}
    band_keys = {dk(t) for t in skin.tris}
    deleted = full_keys - band_keys
    band_vkeys = {L.key(z) for t in skin.tris for z in t[1:]}
    # boundary owners/coords in retained geometry
    owner_ok = all((o is None) or (dk(o) in band_keys) for (p, q, r, o) in skin.boundary.values())
    coord_ok = all(L.key(p) in band_vkeys and L.key(q) in band_vkeys for (p, q, r, o) in skin.boundary.values())
    # caches reference only retained tiles
    edges_ok = all(dk(t) in band_keys for ts in skin.edges.values() for t in ts)
    cavity_excluded = {frontier_id(e) for e in skin.frontier()} <= {frontier_id(e) for e in full.frontier()}
    # serialized PRE-SCAR state tiles must equal the frozen jam band, with no deleted-interior tile
    state_keys = {repr(dk(IW.dtile(rec))) for rec in prescar_state["tiles"]} if prescar_state else set()
    jam_band_keys = {repr(dk(t)) for t in band_jam}
    jam_deleted = {repr(dk(t)) for t in full_jam} - jam_band_keys
    state_is_jam_band = (state_keys == jam_band_keys) if prescar_state else None
    state_excludes_deleted = (len(state_keys & jam_deleted) == 0) if prescar_state else None
    meta = dict(
        boundary_owner_tiles_in_band=bool(owner_ok),
        boundary_coords_in_band=bool(coord_ok),
        caches_reference_only_retained_tiles=bool(edges_ok),
        cavity_edges_excluded_from_frontier=bool(cavity_excluded),
        n_deleted_tiles_final=len(deleted),
        serialized_fields=sorted(set(prescar_state)) if prescar_state else None,
        serialized_only_declared_fields=bool(
            prescar_state is not None and set(prescar_state) ==
            {"schema", "radius", "tiles", "boundary", "rng_state", "scars", "fields"}),
        prescar_state_equals_jam_band=state_is_jam_band,
        prescar_state_excludes_deleted_interior=state_excludes_deleted,
    )

    endpoint_status = ("validation_failure" if validation_failed
                       else "total_arrest" if arrested
                       else "horizon_complete")
    horizon_complete = (not validation_failed) and (not arrested) and (checked_steps[-1] == 44)
    rec = dict(
        case=f"w{world}-B-s{si}", world=world, si=si, jam_step=jam_step,
        steps_checked=[checked_steps[0], checked_steps[-1]],
        growth_steps_executed=growth_steps,
        endpoint_status=endpoint_status,
        horizon_complete=bool(horizon_complete),
        ordered_equivalence=(ordered_mismatch is None),
        ordered_first_mismatch=ordered_mismatch,
        set_inventory_equivalence=(set_mismatch is None),
        prescar_alignment=prescar,
        independent_legality=dict(placements_validated=placements_validated,
                                  first_failure=legality_fail,
                                  all_legal=(legality_fail is None)),
        endpoint=dict(cumulative_history_stars=stars_hist,
                      cumulative_history_overlaps=dict(max_area=ov_hist["max_intersection_area"],
                                                       positive_area_overlaps=len(ov_hist["positive_area_overlaps"]),
                                                       pairs=ov_hist["test_pairs"]),
                      band_overlaps=dict(max_area=ov_band["max_intersection_area"],
                                         positive_area_overlaps=len(ov_band["positive_area_overlaps"])),
                      n_full_tiles=len(full.tris), n_band=len(skin.tris)),
        current_blocked_edges=len(cur_blocked),
        cumulative_scar_labels=len(scars_w),
        metadata=meta,
    )
    return rec, prescar_state


def main():
    RESULTS.mkdir(parents=True, exist_ok=True); INPUT.mkdir(parents=True, exist_ok=True)
    out = []; prestates = {}
    for (w, si) in AF.B_JAMS:
        print(f"[verify] w{w}-s{si} ...", flush=True)
        rec, pre = verify_case(w, si)
        out.append(rec); prestates[f"w{w}-s{si}"] = pre
        p = rec["prescar_alignment"] or {}
        print(f"   endpoint={rec['endpoint_status']} (steps={rec['growth_steps_executed']}) "
              f"ordered_equiv={rec['ordered_equivalence']} indep_legal={rec['independent_legality']['all_legal']} "
              f"({rec['independent_legality']['placements_validated']} placements) "
              f"prescar_align(geom={p.get('geometry_matches_frozen_jam')},front={p.get('ordered_frontier_matches')},"
              f"prng={p.get('prng_matches_evaluator')}) blocked={rec['current_blocked_edges']} "
              f"labels={rec['cumulative_scar_labels']} overlaps={rec['endpoint']['cumulative_history_overlaps']['positive_area_overlaps']} "
              f"bad_stars={rec['endpoint']['cumulative_history_stars']['invalid_complete_stars']}", flush=True)
    (RESULTS / "verification.json").write_text(json.dumps(out, indent=2, default=float))
    (INPUT / "prescar_states.json").write_text(json.dumps(prestates, default=float))
    print("\nSUMMARY ordered-equivalent:", sum(c["ordered_equivalence"] for c in out), "/", len(out),
          "| indep-legal:", sum(c["independent_legality"]["all_legal"] for c in out), "/", len(out),
          "| horizon-complete:", sum(c["horizon_complete"] for c in out), "/", len(out))
    print("wrote results/verification.json, input/prescar_states.json")


if __name__ == "__main__":
    main()


def scar_adjacency_check(world, si):
    """Identify worker placements that touch a pinned-scar edge's geometry at their
    placement time, and validate each against the evaluator's cumulative FULL
    history. Zero eligible placements is 'not exercised', not a positive result."""
    jp = AF.jam_prep(world, si)
    skin = E.ActiveSkin(list(jp["Sstar"]) + [jp["B"]], radius=2)
    worker_hist = L.Patch(list(jp["Sstar"]) + [jp["B"]])
    rng = random.Random(jp["stream"]); scars = set()
    n_adj = 0; n_adj_legal = 0; n_total = 0
    for s in range(1, 45):
        skin.additions = []
        st, n, k, newly, il = SCN.patient_scar(skin, rng, scars, verify_legal=True)
        placed = list(skin.additions); skin.additions = []
        skin.prune()
        scar_vkeys = {v for ek in scars for v in ek}
        for t in placed:
            n_total += 1
            touches_scar = bool({L.key(z) for z in t[1:]} & scar_vkeys)
            legal = worker_hist.legal(t)      # independent legality vs full history
            if touches_scar:
                n_adj += 1
                if legal:
                    n_adj_legal += 1
            if legal:
                worker_hist.add(t)
        if st == "total_arrest":
            break
    return dict(n_total_placements=n_total, n_scar_adjacent=n_adj,
                n_scar_adjacent_legal=n_adj_legal, exercised=(n_adj > 0))

#!/usr/bin/env python3
"""
test_supplement.py -- corrected focused tests for the verification supplement.
Exits non-zero on failure. Run from this dir with EFP_SNAPSHOT set:
    python3 test_supplement.py

Replaces the weak originals:
  * ordered equivalence (not set-only) + independent legality;
  * REAL scar-adjacency (placements touching a pinned-scar edge at placement time,
    validated against the full history; zero eligible = 'not exercised');
  * deep retained-state check (boundary owners/coords in band, caches, no deleted
    collection, cavity excluded, pre-scar state == frozen jam band);
  * spawned restart from the ACTUAL pre-scar jam state matches both comparators.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_supplement as VS
import isolated_worker as IW

FAILS = []
def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)

_rec = None; _pre = None
def rec():
    global _rec, _pre
    if _rec is None:
        _rec, _pre = VS.verify_case(7, 0)
    return _rec


def test_ordered_and_legality():
    r = rec()
    check(r["ordered_equivalence"], "ORDERED equivalence (placements, frontier, candidate enumeration, PRNG before+after)")
    check(r["set_inventory_equivalence"], "set inventory also agrees (kept distinct from ordered)")
    il = r["independent_legality"]
    check(il["all_legal"] and il["placements_validated"] > 0,
          f"every worker placement legal vs independent full history ({il['placements_validated']} checked)")
    e = r["endpoint"]
    check(e["cumulative_history_stars"]["invalid_complete_stars"] == 0 and e["cumulative_history_stars"]["overfull_vertices"] == 0,
          "all complete decorated vertex stars valid; no over-full vertex")
    check(e["cumulative_history_overlaps"]["positive_area_overlaps"] == 0,
          f"no positive-area triangle overlaps (max {e['cumulative_history_overlaps']['max_area']:.2e})")


def test_scar_adjacency_real():
    sa = VS.scar_adjacency_check(7, 0)
    check(sa["exercised"], f"scar-adjacency actually exercised ({sa['n_scar_adjacent']} placements touch a pinned scar)")
    check(sa["n_scar_adjacent_legal"] == sa["n_scar_adjacent"],
          f"all scar-adjacent placements legal vs full history ({sa['n_scar_adjacent_legal']}/{sa['n_scar_adjacent']})")


def test_deep_retained_state():
    m = rec()["metadata"]
    check(m["boundary_owner_tiles_in_band"], "boundary owner tiles are retained band tiles")
    check(m["boundary_coords_in_band"], "boundary edge coordinates are retained vertices")
    check(m["caches_reference_only_retained_tiles"], "worker endpoint edge cache (skin.edges) references only retained tiles")
    check(m["cavity_edges_excluded_from_frontier"], "deletion-cavity edges excluded from the construction frontier")
    check(m["serialized_only_declared_fields"], "serialized state has only the declared fields")
    check(m["prescar_state_equals_jam_band"], "pre-scar serialized state equals the frozen jam band")
    check(m["prescar_state_excludes_deleted_interior"], "pre-scar serialized state excludes the deleted interior")


def test_prescar_restart():
    r = rec()
    p = r["prescar_alignment"]
    check(p["geometry_matches_frozen_jam"] and p["ordered_frontier_matches"] and p["prng_matches_evaluator"] and p["scars_empty"],
          "pre-scar state (top of jam step) aligns with frozen jam: geometry, ordered frontier, PRNG, empty scars")
    jam = r["jam_step"]
    spawned = IW.run_spawned(_pre, 44 - jam + 1)
    steps = [m for m in spawned if m.get("kind") == "step"]
    check(len(steps) == 44 - jam + 1 and all(m.get("status") != "error" for m in steps),
          f"spawned restart from pre-scar state runs steps {jam}..44 without error")
    # compare to uninterrupted worker over the same steps. uninterrupted_worker_placements
    # already returns per-step lists of repr(dk(t)) strings; the spawned worker returns raw
    # dkeys, so repr those once to match (same convention as restart_prescar.py).
    worker_per, _ = __import__("restart_prescar").uninterrupted_worker_placements(7, 0)
    worker_slice = [p2 for (s, p2) in worker_per if s >= jam]
    spawned_slice = [[repr(tuple(k)) for k in m["placed"]] for m in steps]
    check(spawned_slice == worker_slice, "spawned restart reproduces the uninterrupted worker's ordered continuation exactly")


def main():
    print("[ordered + legality]"); test_ordered_and_legality()
    print("[scar adjacency, real]"); test_scar_adjacency_real()
    print("[deep retained state]"); test_deep_retained_state()
    print("[pre-scar restart]"); test_prescar_restart()
    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)}"); sys.exit(1)
    print("ALL SUPPLEMENT CHECKS PASSED.")


if __name__ == "__main__":
    main()

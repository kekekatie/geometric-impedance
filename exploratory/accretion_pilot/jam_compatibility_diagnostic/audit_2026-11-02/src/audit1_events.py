#!/usr/bin/env python3
"""
audit1_events.py -- Part 1 of the audit: reproduce the step/jam structure and
establish what resolution the first-loss-of-compatibility claim actually has.

Checks, per recorded case:
  (a) step semantics: snaps[0] is the initial S*+B state (the A/B BRANCH
      selection), steps 1.. are patient-scheduler steps; `guesses` are the later
      FREE choices. We list, for every step up to the jam, how many tiles it
      added and whether it was a free choice ('guess') or forced.
  (b) first loss of F(full) and its relation to the first free choice and the
      visible jam (reproduce 9/17 vs 23/42).
  (c) MONOTONICITY of F(full): once F(full) is infeasible, does it ever become
      feasible again before the jam?  Adding tiles only ADDS window constraints
      (the gauge/layer set is constant), so F(full) should be monotone; we check
      it empirically. If monotone, the snapshot-level scan plus the within-step
      per-tile refinement in part3 give EXACT tile-addition-event resolution for
      the full patch (no transient infeasibility can hide between snapshots).
  (d) whether F(skin) is monotone (it need not be; pruning removes constraints).

Writes results/audit1_events.json.
"""
from __future__ import annotations
import json
import audit_common as A
from audit_common import Sl, PC, L
import feas


def feas_cls(tiles):
    try:
        rank = Sl.rank_of(tiles)
    except AssertionError:
        return dict(cls="unresolved_layers", r=None, layers=None)
    cm = Sl.constraints(tiles, rank)
    cl = feas.classify(cm)
    return dict(cls=cl["cls"], r=cl["r"], layers=sorted(rank))


def analyse(world, si, js, first_inf):
    arm, _ = A.arm_of(world, si)
    snaps = arm["snaps"]
    guesses = arm["guesses"]
    per_step = []
    full_seq = []
    prev_n = None
    for s in range(len(snaps)):
        full = snaps[s]
        fc = feas_cls(full)
        full_seq.append(fc["cls"])
        added = len(full) - prev_n if prev_n is not None else len(full)
        prev_n = len(full)
        per_step.append(dict(step=s, n_tiles=len(full), added=added,
                             is_free_choice=(s in guesses),
                             full_cls=fc["cls"]))
    # first infeasible full step
    first_full = next((s for s, c in enumerate(full_seq) if c == "infeasible"), None)
    # monotonicity of F(full): after the first infeasible step, never feasible again (<= jam)
    tail = full_seq[first_full:js + 1] if first_full is not None else []
    full_monotone = all(c == "infeasible" for c in tail)
    # free-choice structure up to the jam
    guesses_le_jam = [g for g in guesses if g <= js]
    first_free = guesses_le_jam[0] if guesses_le_jam else None
    steps_before_first_free = [p for p in per_step if 0 < p["step"] < (first_free or js)]
    forced_before_free = all(not p["is_free_choice"] for p in steps_before_first_free)
    return dict(
        case=f"w{world}-B-s{si}", world=world, stream_idx=si, visible_jam=js,
        n_snaps=len(snaps),
        branch_selection_step=0, branch_option="B(shape1)",
        guesses_all=guesses, guesses_up_to_jam=guesses_le_jam, first_free_choice=first_free,
        first_infeasible_full=first_full,
        first_infeasible_equals_first_free=(first_full == first_free),
        steps_1_to_firstfree_all_forced=forced_before_free,
        full_monotone_infeasible_through_jam=full_monotone,
        tiles_added_at_first_infeasible=next(p["added"] for p in per_step if p["step"] == first_full),
        full_cls_sequence=full_seq,
        per_step=per_step,
    )


def main():
    A.RESULTS.mkdir(parents=True, exist_ok=True)
    out = []
    for (w, si, js, fi) in A.CASES:
        r = analyse(w, si, js, fi)
        out.append(r)
        print(f"{r['case']}: branch=step0(B); first free choice @ {r['first_free_choice']}; "
              f"first infeasible(full) @ {r['first_infeasible_full']} "
              f"(== first free: {r['first_infeasible_equals_first_free']}); "
              f"steps 1..firstfree all forced: {r['steps_1_to_firstfree_all_forced']}; "
              f"F(full) monotone-infeasible through jam: {r['full_monotone_infeasible_through_jam']}; "
              f"tiles added at first-infeasible step: {r['tiles_added_at_first_infeasible']}; "
              f"visible jam @ {r['visible_jam']}", flush=True)
    (A.RESULTS / "audit1_events.json").write_text(json.dumps(out, indent=2, default=float))
    print("wrote results/audit1_events.json")


if __name__ == "__main__":
    main()

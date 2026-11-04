# Finishing patch — verification supplement

*2026-11-04 (applied after the initial supplement commit `102d928`). For Katie / Astra /
Argon. This is the finishing patch before a separate independent (Codex) execution check.*

Astra reviewed the supplement source and saved results without executing them, and flagged
**two code defects** and **several reporting inaccuracies**. This patch fixes only those
items and reruns the affected checks. No scientific policy, case list, horizon, retention
rule, or reader was changed, and **no scientific outcome changed**.

## Code defects fixed

1. **Missing prune in the uninterrupted-worker comparator.**
   `restart_prescar.uninterrupted_worker_placements()` grew the band worker without calling
   `skin.prune()` each step, so the band it *returned* accumulated the whole patch
   (e.g. w7 ≈ 1006 tiles instead of the radius-2 band's 644). It now follows the same
   lifecycle as the main verification worker (`verify_supplement.verify_case`) and the
   spawned worker (`isolated_worker._worker_proc`): capture the ordered additions, clear the
   transient addition record, then prune. **Scope of the defect:** it affected only this
   comparator's returned band; the *placement sequence* it used for the restart comparison is
   unchanged (pruning removes only off-band interior tiles and never touches the frontier,
   candidates, decisions, or placements). The main worker and spawned worker already pruned
   every step, so the missing prune did **not** affect every run. **Outcome after the fix:**
   the 11-case pre-scar restart still matches both comparators exactly
   (`restart==full 11/11`, `restart==worker 11/11`).

2. **Independent-legality failure did not stop the trial.**
   In `verify_supplement.verify_case`, a failed `worker_hist.legal(t)` broke only the inner
   placement loop; the outer growth loop continued. It now, on the **first** failure:
   records the step, batch position, offending tile, the evaluator pre-state (accepted
   history keys), and the **unvalidated remainder** of the already-computed batch, with a
   note that `patient_scar` computes and places the step's batch **before** the evaluator
   validates it; **stops the entire trial** before the next growth step (no further
   `patient_scar` runs); does **not** accept the offending tile or the remainder into
   history; and marks `endpoint_status = "validation_failure"`, `horizon_complete = False`
   (never horizon completion). No corrective information flows back to the worker. A
   regression fixture, `test_failstop.py`, injects a forced failure through the test-only
   `_FORCE_ILLEGAL` hook (`None` in every scientific run) and verifies the trial stops at the
   injected step with no later growth and the remainder unaccepted. The injected failure data
   is in-memory/test-only and is never written to `results/`.

## Reporting inaccuracies corrected (in `SUPPLEMENT_2026-11-04.md`, with pointers)

- **`n_band` column.** The per-case table's `n_band` values were the **pre-scar** (jam)
  band counts, mislabelled as final. Replaced with two columns, `band@jam` and `band@44`
  (e.g. w7: 315 at the jam, 644 at the endpoint; final band is 46.8–62.6 % of the full
  patch).
- **"Byte-for-byte identical geometry."** Replaced with the implemented claim: **equality of
  the sorted list of decorated tile keys** (`endpoint_geom.py` →
  `endpoint_sorted_list_identical`). Noted explicitly that this does **not** check raw
  coordinate bytes or on-disk serialization order.
- **Metadata coverage.** Narrowed to what the code checks: boundary owners/coordinates, the
  **endpoint edge cache** (`skin.edges`), and the listed serialized-state properties — not
  an exhaustive inspection of every cache or all reachable objects after every prune. (An
  expanded metadata audit is out of scope for this patch.)
- **Legality-check provenance.** Corrected: the evaluator history is initialized at the
  **fork state `Sstar + B`** (the fork seed, *not* the complete pre-scar jam patch) and
  replayed along the worker's trajectory. The 440–829 validated placements per case
  therefore cover the **full replay, steps 1–44**, not only post-jam additions.
- **Comparator-prune distinction.** Stated that the main and spawned workers already pruned
  every step and only the uninterrupted comparator lacked it, so the defect did not affect
  every run.

## Artifacts regenerated (previous versions retained in Git at `102d928`)

- `results/verification.json` — **changed**: three new additive fields per case
  (`endpoint_status`, `growth_steps_executed`, `horizon_complete`). Every pre-existing
  scientific field is byte-identical to `102d928` (verified by diff); all eleven are
  `endpoint_status = "horizon_complete"`.
- `results/prescar_restart.json`, `input/prescar_states.json` — regenerated and
  **byte-identical** to `102d928` (deterministic); Git records no change.
- `results/endpoint_geometry.json` — **not** rerun (unaffected by these changes); unchanged.
- `results/readout.json` and the other original experiment artifacts — untouched. The readout
  search was not rerun or enlarged (no scientific endpoint changed).

## Checks executed (this patch)

| check | command | outcome |
|---|---|---|
| Failure-stop regression | `python3 test_failstop.py` | PASS (stops at injected step 3; no later growth; remainder unaccepted) |
| 11-case pre-scar restart (corrected comparator) | `python3 restart_prescar.py` | `restart==full 11/11`, `restart==worker 11/11` |
| 11-case verification harness (failure-handling change) | `python3 verify_supplement.py` | ordered 11/11, indep-legal 11/11, **horizon-complete 11/11** |
| Focused supplement tests | `python3 test_supplement.py` | all pass |

## Did any scientific outcome change?

**No.** Ordered equivalence, independent legality, pre-scar alignment, spawned restart
agreement, endpoint stars/overlaps, blocked-vs-labels, and endpoint geometry are all
unchanged from `102d928`. The changes are two correctness fixes to the harness and corrected
reporting wording plus additive status fields.

## Remaining unverified / execution limitations

- Everything listed as unverified in `SUPPLEMENT_2026-11-04.md §7` still stands
  (construction from the original seed; growth beyond step 44; a *thin* band by count;
  physical/topological/indefinite memory; reader claims beyond the conditional,
  selected-subset, positive-area readout; the eleven cases are correlated, spanning nine
  distinct pre-scar geometries).
- The endpoint-geometry match is a **decorated-key-list** equality, not a raw-byte or
  serialization-order check.
- These results were produced in this environment; the forthcoming independent Codex
  execution check is the external reproduction. The reproduction commands are in
  `SUPPLEMENT_2026-11-04.md §6` (now including `test_failstop.py`).

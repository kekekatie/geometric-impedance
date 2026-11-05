# Independent execution audit of archive-free scar continuation

**Pinned experiment:** `e4a7503b5273dbc1fa72232de5c29b7048672b0d`. **Frozen engine/reader:** `84130b97f5044197392e72cd53e0e71f81b043f3`. **Earlier full-patch audit:** `3dc43ea844613f2b6e50647f2ffda14616281f68`. Audit branch: `audit/archive-free-scar-2026-11-05`.

This report accompanies the machine-readable execution checks, original regenerated reports, controlled defect fixtures and reproduction instructions in this directory. The audit is bounded to the eleven prescribed B-jam labels and step 44. The result table and totals are recorded in `results/summary.json` and `reproduced/verification.json`.

**Executed outcome:** 11/11 successful continuations; 484 full-replay steps and 77 spawned post-jam steps checked; 7,325 placements validated. All four regenerated artifacts agree exactly as parsed JSON. Raw jam/final coordinate differences are zero. Endpoint checks cover 6,627 full-history vertices (5,319 complete stars) and 4,254 retained-band vertices. No overlap exceeds `1e-12`; maximum numerical intersection area is `2.6107588313450947e-16`. No scientific outcome changes under the two minimal fixes.

## Findings ranked by scientific impact

### 1. The finite construction claim survives independent execution, with its augmented state explicit

The continuously pruned radius-2 worker agrees with the full-patch scar comparator, and a newly spawned worker restarted **before** the first scar batch agrees with both. The comparison distinguishes actual candidate enumeration, pre-add legality-call order, ordered placements, ordered true frontier, PRNG states before/after, scheduler outcome and persistent scar identities. The original sorted inventory check is reproduced separately. Every scientific step makes actual positive placement progress; a step counter is not the evidence of success.

`results/execution_checks.json` contains separate per-step check fields and signatures rather than one aggregate “matches” flag. For the pre-scar state, raw jam geometry and PRNG are also compared to the earlier independently generated frozen patient replay (`results/frozen_prescar_alignment.json`). Initial scars are empty. Full-patch geometry and PRNG traces are compared to the previous independently audited scar continuation, not merely to another process using the same seed.

The supported constructor state is **retained tiles plus the declared true-frontier boundary map, PRNG state and persistent scar labels**, using the frozen matching-rule atlas/templates. The conclusion is not about an unaugmented tile set. It is a finite continuation from these exported post-fork jam states, not a demonstration from the original seed or of indefinite growth.

Code: `../src/isolated_worker.py` (`serialize_state`, `rebuild_skin`, `_worker_proc`); `../supplement_2026-11-04/verify_supplement.py` (`verify_case`); `observe.py` and `analyze.py`. The scheduler is the earlier audited `../../src/scar_continuation.py:patient_scar`; both substrates use that same function.

### 2. Actual deletion survives; process separation alone is not the information-boundary argument

After each scientific worker prune, the tile, edge and vertex indexes agree with indexes freshly reconstructed from retained tiles. Boundary owners and all three stored boundary coordinates belong to retained geometry. The object field list is the expected frozen state, and the transient additions list is empty before the next step. The spawned restart is checked in the same way. Pruning does not expose the inner cavity as construction frontier: the explicit ordered frontier agrees with the full patch, while the local retained-tile index has additional cavity edges that are not presented to the scheduler.

The implementation genuinely removes interior geometry from the worker's construction indexes. The full-history evaluator and the audit's diagnostic trace cache are separate observations; neither supplies candidate choices, repairs or vetoed replacements. On a legality failure the trial stops rather than repairing the worker with evaluator knowledge. A computed batch can already exist in the worker when validation fails; that batch is not all accepted as validated history.

There is one reporting qualification about imports. `af_common -> engine_bridge -> window_retrodiction` reads `corner-response-catalogue/results/summary.json` at import time and stores its historical `stiffness` table. This is an unrelated historical aggregate, not a rule/template table. The statement that startup reads *only* static rule/template files is therefore too strong. Source inspection locates its use in retrodiction analysis, outside the constructor path. A focused w7 pre-scar restart replaces that summary with empty data, forbids all subsequent `window_retrodiction.STIFF` access, and disables fork-cache/replay APIs; all 22 original worker STEP messages remain exactly equal (`results/import_boundary_control.json`). No deleted-tile geometry, archived lifts, A/B hypotheses or evaluator decisions were found steering construction.

The worker is **not filesystem sandboxed**. Python file-open observations and this negative-access control support the executed code path, not an adversarial noninterference proof. The observer itself exports diagnostics; its output snapshot is not a worker input. File-access listings include that diagnostic write and import/configuration reads and must not all be described as reads of scientific inputs.

Code: frozen `active_skin_engine.py:ActiveSkin.add/frontier/prune`; `../src/isolated_worker.py:rebuild_skin/_worker_proc`; frozen `paired-front/window_retrodiction.py:38,115`; `test_import_boundary.py`.

### 3. Demonstrated status defect: arrest at step 44 could also report horizon completion

At the pinned commit, `verify_case` computes `endpoint_status` using the arrest flag but computes `horizon_complete` using only absence of validation failure and final step number. A controlled fixture reaches a synthetic `total_arrest` exactly at step 44 and returns:

```text
endpoint_status = total_arrest
horizon_complete = True
```

The audit adds only `and (not arrested)` to that expression. The regression checks arrests at 44 and 43 and ordinary loop completion; the contradictory flag disappears. The synthetic fixture does not demonstrate placement progress. All scientific runs are checked separately for positive additions and no arrest, so their outcomes do not change. See `results/horizon_fixture.json` and `test_horizon.py`.

Code changed: `../supplement_2026-11-04/verify_supplement.py`, the `horizon_complete` expression only.

### 4. Demonstrated diagnostic-helper retention defect: uncleared transient additions

`endpoint_geom.worker_final_band` prunes each step but originally never clears `skin.additions`. Prune rebuilds `tris`, `edges` and `V`; it does not clear that list. In a lifecycle-only replay of the independently validated w7 placement sequence, the original helper finishes with 829 tiles in `additions`, including 209 tiles absent from the final retained band. Its returned band is correct, but its live object is not restricted to retained geometry.

One line clears `skin.additions` immediately before each prune. The same fixture then has zero transient additions and the **identical ordered raw endpoint band**. This defect affects the endpoint diagnostic helper, not the corrected main verifier, uninterrupted-worker comparator or spawned worker, which already clear additions. It does not invalidate their deletion evidence or change an endpoint/readout. See `results/endpoint_lifecycle_fixture.json` and `test_endpoint_lifecycle.py`.

Code changed: `../supplement_2026-11-04/endpoint_geom.py`, one additions reset. Historical outputs are preserved.

### 5. Legality is supported by distinct checks with shared dependencies disclosed

The separate cumulative evaluator starts from `Sstar + B`, follows the worker's actual ordered additions and calls the frozen legality predicate **before** adding each tile. Counts cover steps 1–44 from that fork, not only the post-jam interval. Initial B legality is checked separately. This catches construction into already occupied deleted space using full history, which the constructor does not consult.

The original endpoint validator checks complete decorated stars and overfull vertices. It does **not** establish validity of every partial boundary star. This audit additionally invokes the actually loaded frozen `vertex_ok` on every full-history and retained-band vertex. Partial checks establish admissible local decorated arcs and nonoverlapping corner sectors under that atlas; they do not prove a globally realizable completion. Runtime source provenance identifies the transitive `soft_zone.vertex_ok_fixed` correction used by the frozen engine.

The independent convex-clipping overlap calculation is separate from the engine's centroid/vertex occupancy test. It finds no triangle intersection above the declared `1e-12` area threshold. Tiny nonzero intersections are treated as floating-point residuals, not exact symbolic certificates. The matching-rule legality and star checks share the frozen atlas and engine; describing the entire geometry validation as an independent implementation would be incorrect.

The original failure-stop test is executed with its actual injected failure. It confirms that the next growth step does not run and that the offending tile and the remainder of the computed batch are not accepted into evaluator history. There is no feedback repair. Source inspection verifies the outer-loop break, not just its final status flag.

Code: `../supplement_2026-11-04/verify_supplement.py:complete_star_check/overlap_check/verify_case`; `../supplement_2026-11-04/test_failstop.py`; `analyze.py:stars`; `results/decision_dependencies.json`.

### 6. Reader reuse is supported by raw input agreement, not by six-decimal keys alone

The historical endpoint comparator uses `repr(dk(tile))` keys. Position keys round coordinates to six decimals, substantially coarser than some reader tolerances, so key equality alone is not a sufficient numerical-input check. The audit compares decoration, ordered vertex coordinates and tile-list order directly against the pinned original jam/final exports, and compares the spawned final band to the continuous worker. These are exact Python numeric-value comparisons, not a claim of byte-identical JSON serialization or signed-zero bit patterns.

Declared reader metadata—historical physical origin, edge length, rank/layer convention, windows and both birth hypotheses—is recorded per case. It is supplied by the same unchanged frozen adapter and fork/birth inputs, outside the constructor. Thus the original bounded readout is reused; no reader search is rerun or expanded. Its 528 outcomes remain **111 B selections, 64 ambiguous, 353 incompatible, zero A selections and zero reconstruction failures**. Those totals are reused historical readout results supported by checked inputs, not newly executed reader calls in this audit.

A positive-area B selection does not in general exclude the closed A region: the selected-grid headlines retain numerical zero-area A segments for the w15/w19/w28 stream-0 family. Reader thresholds are unchanged. Endpoint selections do not establish continuous memory transport or successful readout at every intervening step.

Code: `../supplement_2026-11-04/endpoint_geom.py`; `../src/readout.py`; `../../../jam_repair_pilot/src/phase4_readout.py:build_payload/classify`; `analyze.py:coords`. Data: `results/execution_checks.json`, `results/readout_metadata_*.json`.

### 7. Frontier width, scar accounting and case dependence require precise wording

Radius 2 means the frozen distance rule from **all declared true-frontier endpoints**, including blocked components. It does not mean distance from only the advancing outer perimeter. The retained band includes scar neighbourhoods and still contains roughly 47–63% of the full patch at step 44. Boundary tags are necessary to keep pruning-created cavity edges out of the construction frontier.

Cumulative scar labels and current blocked edges are recorded independently. The w5/w21 family has two labels but five current blocked frontier edges; other cases have matching counts. Permanent pinning is a scheduler policy, not a proof of perpetual geometric unextendability.

Eleven labels are correlated. A hash of a raw serialized state is not a geometric equivalence relation: PRNG state, serialization order and floating-point coordinates can distinguish otherwise equivalent shapes. `results/case_equivalence.json` reports separate absolute raw-coordinate, absolute decorated-key and explicitly defined translation-normalized groups. It does not infer any statistical independence count, and does not normalize rotations or reflections.

In this audit, the pre-scar bands form nine absolute raw-coordinate groups but eight absolute decorated-key groups: w19-B-s1 and w29-B-s1 additionally coincide at the engine's rounded-key resolution. The specified translation-normalization procedure also gives eight groups, with different membership. These are procedure-specific groupings, not a count of distinct tilings under all rigid motions. In particular, the supplement's unqualified “nine distinct pre-scar geometries” should be narrowed to its raw representation criterion.

## Scope and delivery

Only the two demonstrated helper/status defects are changed in experimental code. Original and regenerated evidence is separated; the frozen engine, scheduler, rules, reader thresholds, case list, retention policy and horizon are preserved. The audit stops after these execution checks and bounded controls. `HANDBACK.md` gives the usable claim; `REPRODUCTION.md` provides commands, cache provenance and comparison limits. Exact publication identity is supplied with the delivery receipt.

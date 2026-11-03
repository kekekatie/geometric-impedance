# Protocol — archive-free scar continuation (frozen before new outcomes)

*2026-11-04. Written after reading the audit, the frozen hollow-band engine and
the frozen scheduler/reader, and before collecting any new continuation outcomes.
An informative negative result is an acceptable completion. No matching rule,
reader threshold, scheduler policy, or frozen file is changed. Base commit
`3dc43ea` (audit tip); frozen engine/reader `84130b9`. Deviations are dated in
`PROTOCOL_DEVIATIONS.md`.*

## Central question

Starting from the recorded jam checkpoints, can a construction worker that retains
**only** the specified boundary band continue legally toward step 44, **without
consulting deleted interior geometry** — and how does it compare with the audited
full-patch scar scheduler? This experiment starts from exported jam states; it
does **not** establish archive-free construction from the original seed.

## Retained-tile rule (the declared retained state)

The worker is the **frozen `active_skin_engine.ActiveSkin`** at **radius = 2**
(unchanged). Its retained state is:

- **Band tiles.** After each growth step the band keeps exactly the tiles within
  `2·S + 1e-12` of the *explicit true-frontier boundary points* (`ActiveSkin.prune`).
  `S` is the frozen edge length; `2·S` is the **geometric width**. Geometric width
  is reported **separately** from **retained tile count**, which is expected to
  grow around scars (see "scar tissue").
- **True-frontier boundary (disclosed metadata).** `ActiveSkin.boundary`: a dict
  `edge-key → (p, q, r, owner-tile)` built **incrementally by `ActiveSkin.add`**
  (only a newly attached tile's own edges update it; a covered edge is removed, a
  new outer edge is added). **Pruning never adds deletion-exposed cavity edges to
  this boundary.** `frontier()` returns only `boundary.values()`, sorted by the
  frozen key `(|midpoint|, key(midpoint))` — the *same* order the full-patch
  scheduler uses. Provenance: archive-free growth only. This is the augmented
  retained state; results are scoped to "construction from band + true-frontier
  tags", and the tags are audited (below) to confirm they are not an interior
  archive.
- **PRNG state.** A `random.Random` state continuing the recorded `stream`.
- **Persistent scar set.** Edge-keys of true-frontier edges found with zero
  atlas-legal candidates, pinned permanently (dormant-defect policy, identical to
  the audited full-patch scar scheduler). Scars remain boundary edges.

**True frontier vs deletion-exposed edges.** By construction: `frontier()` reads
only the explicit `boundary`; the cavity edges created by pruning live only in the
temporary local tile index used for `legal()`/`candidates()`, never in `boundary`,
so the worker **cannot grow inward into the pruned cavity**. A focused control
asserts no placement's centroid falls inside the pruned-away region.

**Blocked notches, holes, enclosed scars.** A zero-candidate true-frontier edge is
pinned and skipped for the rest of the run; it stays a boundary edge, so the band
retains material within `2·S` of it (scar tissue). A scar that later becomes
enclosed by growth remains a pinned boundary edge; its retained neighbourhood is
measured. `total_arrest` is declared only when no **non-pinned** true-frontier edge
is growable; it is reported as a scheduler-policy outcome, not a proof that every
edge is geometrically unextendable.

## Scheduler (identical to the audited full-patch scar scheduler)

A single `patient_scar(P, rng, scars)` is applied to **both** the worker
(`ActiveSkin`) and the evaluator (full patch). It mirrors the frozen
`speed_of_now.patient` exactly except for the halt rule:

- scan `P.frontier()` in frozen order; pin zero-candidate edges (scars) and skip
  already-pinned ones;
- **forced batch:** all non-pinned edges with exactly one candidate, deduplicated
  by decorated key in insertion order, each re-checked with `P.legal` before `add`
  (frozen semantics; a forced candidate invalidated by a sibling placement is
  skipped);
- **free choice:** if nothing is forced, `rng.choice(ordered(candidates))` at the
  **first** non-pinned growable frontier edge;
- marking/skipping scars consumes **no** randomness.

Because the worker's `frontier()` equals the full patch's true frontier and its
`candidates`/`legal` are computed on the band (which retains every tile within
`2·S` of the frontier, and legality interactions are `≤ 1·S` with a conservative
`3·S` overlap pre-filter that never fires on distant tiles), the worker *should*
reproduce the full-patch decisions. Whether it does under scars is the question.

## Information boundary (enforced)

- **Preparation (replay, labelled).** Deterministic frozen replay grows the
  ActiveSkin from the fork seed to the jam; the band + boundary + PRNG state + (no)
  scars are **exported once** (`input/jam-band-w{W}-s{si}.pkl`). The full patch is
  reconstructed only inside the evaluator.
- **Worker isolation.** The worker runs in a **spawned** process (`mp spawn`)
  receiving only the serialized retained state and `STEP`/`STOP`; it sends back
  only band state (tiles, frontier ids, placements, before-step candidate
  inventory, dropped count). It never receives the full patch, deleted tiles,
  archived lifts, candidate menus, future placements, or A/B hypotheses. After each
  prune, deleted geometry is removed from the worker's tile/edge/vertex indexes
  (frozen `prune` rebuilds them from kept tiles).
- **Cold restart.** A control reloads the serialized jam band into a fresh worker
  and confirms an identical continuation — proving the continuation depends only on
  the declared retained state.
- **Evaluator.** Holds the full history, runs the full-patch scar scheduler in
  lockstep, validates every worker placement's legality against the full
  construction history, and compares. Its findings **never** feed candidate
  selection, vetoes, or repairs back into the worker.
- **Metadata audit.** The worker's entire input is enumerated and shown to contain
  no full patch, deleted-tile list, archived lift, candidate menu, or hypothesis.

## Comparison, outcomes, tolerances, stopping

Begin with **w7-B-s0** as the implementation check; once controls pass, apply the
identical frozen procedure to all eleven cases, recording deviations and not
discarding unsuccessful cases. From the identical pre-scar jam checkpoint and PRNG,
compare worker vs full-patch scheduler at every step:

- true-frontier identities (ordered); candidate sets and ordered candidate lists
  (`inventory`); forced/free decisions; PRNG state before/after; placements
  (decorated keys); dropped/retained counts; current blocked edges and persistent
  labels.

Record the **first mismatch** and its cause, keeping these **distinct**:
ordering difference, candidate-set difference, frontier error, legality failure.
After a *legal* divergence, bounded independent continuation may proceed under the
frozen policy, but exact equivalence has failed and is reported as such. An
**independently-detected illegal addition** ends that trial as a failure; the
offending pre-state and candidate are saved and **not** repaired with evaluator
knowledge. Comparisons of keys/placements/inventories are **exact** (decorated
keys); PRNG by `getstate()`; legality by frozen `Patch.legal`/`vertex_ok`; overlap
by independent convex clipping with `1e-12` area cutoff.

Stopping conditions, kept separate: **horizon** (step 44 reached with progress),
**scheduler arrest** (`total_arrest`), **mismatch** (equivalence failed),
**validation failure** (illegal addition), **resource limit**. Reaching a step
index alone is **not** progress; actual placement counts are recorded. The frozen
pre-scar jam state is the additions baseline.

## Readout (secondary; reuse the audit's precommitted scan)

For valid endpoint states, apply Astra's precommitted **geometry-defined 528-window
bounded scan** (`audit_2026-11-03/SENSITIVITY_PROTOCOL.md`, 6 centres `anchor +
j·π/3`, half-widths `π/8, π/4, π/2, 3π/4`), identically at jam and final, to the
**worker's retained band only**, with historical origin/rank/windows/hypotheses
supplied to the evaluator. Selection is label-blind (positive area `> 1e-9`, then
max tile count, then declared ordering); the historical B label is never a
tie-break. Report **all** scan outcomes, hypothesis intersection areas, selected
component sizes, and choice-tile membership. Keep the frozen positive-area reader
decision **separate** from an independent box-free closed-region A-feasibility
check (zero area ≠ symbolic emptiness). Report the actual endpoint and reason for
any trial that stops early; do not call these step-44 results.

## Boundaries

Eleven recorded B-jam cases and the existing step-44 horizon only. No fresh
worlds, longer horizons, repair searches, matching-rule relaxation, or manuscript.
No inference of indefinite growth or physical/topological memory. If no defensible
bounded policy can be implemented within this scope, deliver that specific
obstruction and stop.

## Deliverables

Dated correction note (done); this protocol + dated deviations; isolated
worker/evaluator + focused tests; reproduction commands + machine-readable
per-case comparisons; first-divergence/failure witnesses; one w7 figure (retained
vs genuinely deleted space); plain-language `HANDBACK.md` answering the five
questions. Commit and push; no merge, no force-push.

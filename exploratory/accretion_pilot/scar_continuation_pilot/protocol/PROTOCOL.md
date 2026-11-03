# Protocol — scar-continuation pilot (frozen before inspecting Phase-2 outcomes)

*2026-11-03. Bounded pilot, no preferred outcome. Null, ambiguous, or full-arrest
results are equally valid. No tile-matching rule is relaxed; the frozen engine,
frozen reader and decision thresholds are unchanged. Branch
`claude/scar-continuation-pilot-2026-11-03`, directory
`scar_continuation_pilot/`. Base commit `d2e075a`.*

Terminology: "retained boundary band" / "active ring" is the study's active skin.

## Central questions

1. **Arc readout at the jam (Phase 1, no growth mutation).** Although
   F(whole band) = ∅ at the recorded jam, does historical A/B information survive
   in contiguous compatible connected sub-arcs of the jammed band?
2. **Scar-tolerant continuation (Phase 2).** If zero-candidate frontier sites are
   pinned as dormant defect "scars" (instead of halting the whole simulation) while
   the remaining growable true-frontier sites continue under the identical patient
   scheduler and PRNG stream to the step-44 horizon: does growth continue around
   the notch or cascade to total arrest; how many scars accumulate; and what do the
   global and arc readers recover afterward (Phase 3)?

## Phase 2 — scar-tolerant scheduling (defined before running)

The frozen baseline `speed_of_now.patient` returns `JAM` (global halt) the instant
**any** frontier site has zero atlas-legal candidates. The scar-tolerant variant
changes **only** that halt rule:

- **Legality stays 100% strict.** Robinson arrow matching and vertex-star
  legality are decided solely by the frozen `Patch.legal` / `D.candidates`. No
  illegal tile may be placed; no matching rule is relaxed.
- **Pin, don't halt.** At any growth step, a frontier site (edge) with **0**
  atlas-legal candidates is marked `pinned_scar` by its edge-key and removed from
  the active candidate queue for the remainder of the run (a dormant defect site).
- **Continue the identical patient logic on the rest.** Among the non-pinned
  frontier edges, the exact baseline order applies: all **forced** sites (exactly
  1 candidate) settle first (each re-checked with `Patch.legal` before placement);
  if none are forced, a single **free-choice** is made at the first non-pinned
  frontier edge via `rng.choice(ordered(candidates))` — the same deterministic
  ordering and the same `random.Random(stream)` the baseline uses.
- **PRNG / determinism.** We replay from step 0 with the baseline fork, option B,
  and the recorded stream, enabling scar-tolerance throughout. Steps before the
  original jam are therefore **bit-identical** to the baseline (no scars arise
  until the jam step); at and after the jam the stream continues into a **new,
  disclosed trajectory** (it is not "the" historical continuation — the baseline
  halted there). The stream value is recorded per case.
- **Pinning is permanent (dormant-defect semantics).** A pinned edge-key is never
  re-activated, even if later growth would make it legal. This is the conservative
  reading of "pinned/dormant"; a re-activating variant is explicitly out of scope.
- **Arrest rule.** A step ends in `total_arrest` only when
  `growable_non_pinned_frontier_sites == 0`. Otherwise growth proceeds to the
  step-44 horizon.
- **Retained band tracking.** The retained active ring is derived identically to
  the baseline: `skin_of` (the frozen prune rule) applied to the full grown patch
  at each checkpoint. Growth runs on the full patch (as the baseline `grow_arm`
  does); pruning is for readout, not for growth decisions.

**Recorded per case (Phase 2):** whether growth advances past the original jam
step; final step reached (44 vs earlier `total_arrest`); tiles added after the
original jam step; total `pinned_scar` edges, their connected-component count and
angular span around the band (localized vs proliferating); and the choice-tile
(B) departure step under ordinary pruning during the extended growth.

## Phase 3 — post-continuation readout

At the final checkpoint (step 44 or `total_arrest`): run the frozen **global**
reader on the surviving retained band; run the Phase-1 **contiguous-arc** reader
on the maximal connected compatible sub-arc(s) (connected components only, so
lifts are single-valued); track the choice-tile fate (`departed_by_pruning` vs
`still_retained`) separately; and produce 1–2 figures for `w7-B-s0` and
`w5-B-s0`.

## Boundaries

No relaxed matching rules, no new defect-core holonomy claims, no altered reader
thresholds, no new worlds, no extension beyond step 44. A compatible sub-arc that
reads B is only informative if it is large enough to discriminate B from A (a
small arc has a large F and may overlap both — reported as `ambiguous`). Scar-
tolerant growth continuing is **not** evidence that the baseline jam was unreal;
it is a different, clearly-labelled scheduler, and F(whole band) remains empty
throughout.

## Deliverables

`HANDBACK.md` (plain language first, then tables), this `PROTOCOL.md`, machine-
readable JSON/CSV under `results/`, unit tests (single-valued lift
path-independence on connected sub-arcs; strict legality of all placed tiles),
and the figures. Commit and push; no merge or force-push.

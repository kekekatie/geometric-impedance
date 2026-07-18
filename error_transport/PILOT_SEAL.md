# Pilot seal — runtime-only κ selection

**Status: SEALED before execution (three-way approved: Claude built + validated the
Stage-1 family; GPT authorised the runtime-only pilot; Katie adjudicating).**
This freezes the pilot rules. Its sole purpose is to choose one global cap `κ` in
`S_max = κ·N`. It is NOT an experiment and its trajectories never enter inference.

## Frozen rules (GPT review)
1. **Purpose (only):** choose one global `κ` large enough that censoring is
   acceptably low. **Not** to compare substrates or learn any heal/logical outcome.
2. **Dedicated seeds, permanently excluded.** Pilot uses a dedicated master seed
   `PILOT_MASTER_SEED = 20250718`, distinct from all inference seeds, with
   `numpy.random.SeedSequence` substreams keyed by (graph_id, trial). **All pilot
   trajectories are permanently discarded from inference.**
3. **One common κ for every substrate and size** — no per-graph tuning.
4. **Fixed predeclared candidate ladder:** `κ ∈ {5, 10, 20, 40, 80}`
   (the prereg §8 left κ to the pilot; this ladder is predeclared here, matching
   GPT's illustrative ladder). One pass at `κ_max = 80` yields censoring at every
   smaller candidate (censoring(κ) = fraction of trials whose annihilation step
   exceeds `κ·N`), so the ladder is evaluated from a single sealed run.
5. **Eligible graphs = the largest band of each PRIMARY family** (secondary
   bounded-rewires excluded): phason-shear AB, phason-shear Penrose, clean
   oblique-Z² grid, defect-matched grid. Cap chosen on the **worst-censoring**
   (highest-censoring) largest eligible graph — no geometry gets more runtime
   generosity than another.
6. **Selection rule:** the **smallest** candidate κ for which censoring is at or
   below **~5%** on the worst-case largest eligible graph.
7. **Inspect only:** censoring fraction, computational runtime, and the stopping-step
   distribution *solely* to confirm the cap is not absurdly small. **Do NOT inspect
   or report comparative heal-versus-logical proportions.** The pilot script computes
   only annihilation-vs-censor (a hitting-time), never the homology class — outcome
   breakdown is structurally absent from the pilot.
8. **Output** is restricted to cap-selection diagnostics:
   `κ | max censoring across eligible largest graphs | (per-graph censoring) | runtime`.
   **No P_heal / P_logical, no substrate outcome proportions.**
9. **If no candidate reaches ~5%:** STOP and return for review. **Do not improvise a
   new design mid-pilot.** Extend the ladder only through a documented runtime
   amendment.
10. **Records (below, filled after the run):** pilot trial count, exact substrates
    and sizes, seed scheme, candidate ladder, censoring at each candidate, chosen κ
    and rule, and the explicit statement that pilot data are excluded from inference.

## Pilot start rule & dynamics (from sealed prereg §3, primary)
- Start: sample one **undirected native edge uniformly**, **non-seam only**
  (winding = (0,0)); assign endpoints to A, B by a fair coin.
- Move: each step, pick one defect uniformly at random, move it across a
  uniformly-random incident native edge. **Unbiased** (no energy law, no depth).
- Stop: **annihilation** (both defects on the same node) → record step; or
  **S_max = κ_max·N** reached → censored. (Homology class is NOT computed here.)

## Pilot parameters (predeclared)
- `PILOT_TRIALS = 4000` per eligible graph.
- `κ_max = 80` (ladder top); censoring at each ladder κ read from one pass.
- Eligible largest graphs (actual N reported by the run).

*Sealed before execution. Records below filled after the single sealed run.*

---

# Records (filled after the sealed pilot run)

- **Pilot trial count:** 4000 per eligible graph (16000 trajectories total).
- **Seed scheme:** `PILOT_MASTER_SEED = 20250718`; per-graph `SeedSequence([seed,
  graph_id])` with a spawned child stream for the walk. Dedicated; distinct from all
  inference seeds. **All pilot trajectories permanently excluded from inference.**
- **Eligible largest primary graphs (secondary rewires excluded):**
  | graph_id | family | N | median annih. step |
  |----------|--------|---|--------------------|
  | 0 | phason-shear AB (17/12) | 1355 | 25 |
  | 1 | phason-shear Penrose (5/3) | 1700 | 17 |
  | 2 | clean oblique-Z² grid | 1694 | 25 |
  | 3 | defect-matched grid | 1694 | 13 |
- **Candidate ladder:** κ ∈ {5, 10, 20, 40, 80} (predeclared; evaluated in one pass).
- **Censoring at each candidate (max across eligible graphs, and per graph):**
  | κ | max censoring | AB | Penrose | clean grid | matched grid |
  |---|---------------|----|---------|-----------|--------------|
  | 5 | **5.97%** | 4.5% | 4.8% | 6.0% | 5.1% |
  | 10 | **1.43%** | 0.5% | 1.1% | 1.4% | 1.1% |
  | 20 | 0.10% | 0.0% | 0.1% | 0.1% | 0.0% |
  | 40 | 0.00% | 0.0% | 0.0% | 0.0% | 0.0% |
  | 80 | 0.00% | 0.0% | 0.0% | 0.0% | 0.0% |
- **Runtime:** 2.0 s total over 4 graphs × 4000 trials (computationally trivial).
- **Cap-not-absurdly-small check:** median annihilation 13–25 steps; S_max=10·N is
  ~700–900× the median. Not absurdly small. ✓
- **Only censoring + runtime + stopping-step median were inspected.** No heal/logical
  proportion was computed or viewed (the pilot is outcome-blind by construction).

## κ-SEAL (frozen)
Selection rule: smallest candidate κ with worst-case censoring ≤ 5% on the
worst-censoring largest eligible graph. κ=5 gives 5.97% (fails on the clean grid);
κ=10 gives 1.43% (passes). Therefore:

> **κ = 10, sealed.  S_max = 10·N for every substrate and every size.**

This one number is now frozen and does not change for inference. Pilot data are
excluded from all inferential results.

*κ-seal applied. Next: the preregistered transport trials (Stage 1) — awaiting the
three-way go-ahead for inference. Not started.*

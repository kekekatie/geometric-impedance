# The single recommended pilot (v9 → v10)

*One concrete, bounded pilot for Astra to approve or amend. Design only; not run.*

## One-line statement

Build **Penrose (quasiperiodic)** and **jittered-pentagrid (disordered)** rhombus
patches from **one de Bruijn multigrid generator** (same two rhombi, same
face-based growth rule), plus a **Fibonacci-approximant periodic** patch **iff it
passes construction validation within budget**; impose matched paired histories,
evolve under the unchanged Growing rules, and read the frozen proximity-sign one-bit
footprint — comparing memory persistence across substrates against both wall-clock
and saturation coordinates.

## Substrates (arms)

1. **Quasiperiodic — Penrose P3** (regular pentagrid). *Ordered arm A; the primary
   checkpoint is pre-registered from this arm.*
2. **Disordered — jittered pentagrid** (randomised line positions; same two rhombi),
   averaged over **3 patches**.
3. **Periodic — Fibonacci approximant** (same two rhombi, periodic supercell).
   *Included only if its construction gates pass in budget; else deferred to v10 and
   the pilot reports the two-family core.*

Patch size **~200–400 vertices**, tuned per family to comparable V/E/F counts.

## Rule (identical to v1–v8, transplanted)

- original edges = rhombus sides (`w0 = 1`); candidates = the 2 diagonals per face
  (absent, activate at weight 1); trigger = face's 4 bounding edges accumulate wear
  `Σ(w−w0) ≥ θ = 4`; reinforcement `w ← w + 0.5(6 − w)`; walk moves ∝ weight.
- graph model (length-agnostic; diagonals cross without a crossing vertex).

## Histories & reader (frozen)

- Paired histories **A, B** matched in length and endpoints; `B = σ(A)` on
  σ-symmetric patches (Penrose, approximant), disjoint matched paths on disordered
  (choice #3 in the design note).
- Frozen reader: `c(e) = sign(d_graph(e, path_B) − d_graph(e, path_A))`;
  `S_high = Σ_e c(e)·1[w_e ≥ 5.5]` over present added diagonals; A-positive; defined
  before running.
- No-memory baseline: **Fixed** model (paired difference 0 by construction).

## Controls (minimal)

- **Fixed** (no reinforcement/growth) — no-memory baseline, per substrate.
- **Growing** (reinforce + grow) — the model under test.
- *(optional)* **Reinforced** (reinforce only) — funnelling reference, if cheap.

## Measurements

- **Primary:** paired AUC of `S_high` (A vs B) over 8 checkpoints, seed-block
  bootstrap CIs; primary checkpoint pre-registered from the Penrose arm.
- **Opportunity/capacity, separately:** structural access, effective alternatives,
  fraction activated, headroom, edge/weight counts.
- **Saturation-controlled view:** memory vs (a) steps and (b) saturation coordinate
  (fraction activated / mean headroom), to separate slower saturation from stronger
  retention. Saturation-matching is descriptive.
- **Robustness:** 3–5 interior launch sites × 2–3 patches per family, reported as
  variability bands (not a sweep).

## Protocol

200 paired seeds; common-random-numbers per seed across arms; 10,000 steps;
checkpoints `{0,100,200,400,1000,2000,5000,10000}`; save full edge snapshots for
reader-only reuse.

## Validation gates (must pass before dynamics)

1. Tiling is gap-free & edge-to-edge: Euler `V − E + F = 1` for a disk patch; every
   interior edge incident to exactly 2 faces.
2. Same tile set across arms (rhombus angle multiset matches).
3. Exact σ where claimed (σ permutes vertices/edges/faces).
4. Matched-quantity report (V, E, F, budget, initial total weight) within tolerance.
5. Reader: Fixed-model paired difference = 0; zero initial high bits.
6. Degree-distribution report per arm (documented, not matched away).

## Estimated cost

Construction + validation: the bulk of the effort. Dynamics: ≈ 10–20 min
(§ Feasibility E). Whole pilot comfortably within a session.

## Explicit limitations

- Graph model, not physical transport (length/angle ignored).
- Degree distribution and vertex-config statistics cannot be matched exactly; a
  difference may ride on local geometry, not organisation — reported alongside.
- The disorder arm carries between-patch variance the ordered arms lack.
- Two-family core answers "quasiperiodic vs disorder"; the periodic arm is needed
  for the sharper "quasiperiodic vs periodic" contrast and is gated on validation.
- A null result would not prove quasiperiodicity is irrelevant; a positive result
  would not establish universality or any E8 connection (none is used).

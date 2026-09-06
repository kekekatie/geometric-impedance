# Follow-up design note (v2) — timing-matched control + run toward saturation

*Written before execution. Register: speculative exploration; not a confirmatory
study, not cosmology. Bounded follow-up to the v1 accretion pilot
(commit `cc514eed26805e8448b669c813ff30776aa049ec`). Isolated under
`exploratory/accretion_pilot/v2_saturation/`. The v1 pilot and its results are
retained untouched. Nothing here is to be merged or published.*

Requested and authorised by Katie, specified by Astra. Two changes only; the
world, histories, rules, thresholds, probe, observables and the original 200 seed
pairs are otherwise unchanged, and no parameters are tuned.

## Why this follow-up

v1 showed a readable A/B history contrast and increased route diversity coexisting
in the Growing model. It did **not** cleanly isolate *history-shaped placement* as
the cause of Growing's advantage, because the v1 matched control had a timing
confound: Growing activates diagonals **during individual steps**, but the v1
control received its additions **only at measurement checkpoints**. So the
control's edges were systematically younger and had fewer chances to influence
subsequent movement. We fix the timing, then look much further out in time.

## Change 1 — activation-time-and-count matched control

Replace checkpoint-batched matching with **event-by-event** matching.

- An *event* is one edge traversal: the 48 history traversals
  (`3 passes × 16 edges`) followed by each subsequent walk step.
- Run Growing first for each `(history, seed)` and record its number of
  activations **at every event**, separately per history and seed — including the
  imposed-history phase.
- The control replays **exactly those per-event counts** at the corresponding
  events, including during the imposed history.
- Operation order at every event is **traverse → reinforce → activate** (identical
  for Growing and control).
- Placement is chosen uniformly among currently-**inactive** candidates, drawn
  from a **canonically sorted** candidate list with a **separate, stable RNG**
  (`BASE_SEED + seed + CONTROL_PLACEMENT_OFFSET`).
- The control receives **timing and counts only** — never Growing's edge
  identities.
- After every corresponding event we **assert identical cumulative activation
  counts** in Growing and control.

We call this **activation-time-and-count matched**. What is matched: the number of
active connections at every event, and each new edge's initial weight. What is
**not** matched: positions and fully-evolved weights. Note the timing is
*inherited from Growing* and therefore can depend on history — so the control as a
whole is **not** history-independent; only its *placement* is history-blind. This
isolates placement from the age/timing confound, not from everything.

## Change 2 — run toward saturation

Extend all models to **10,000** subsequent steps. Checkpoints (measurement only):
`0, 100, 200, 400, 1000, 2000, 5000, 10000`.

Checkpoints must not affect the simulated trajectory (RNG is consumed per event,
never per checkpoint). We verify this directly on a small fixture: two different
checkpoint lists must yield an identical final state.

*(Implementation note, not a rule change: the Fixed model never modifies the graph,
so its walk is a structural no-op; its snapshots equal the initial state at every
checkpoint by construction and are filled in analytically rather than simulated.
Reinforced/Growing/Control are fully simulated.)*

## Observables

Retain all v1 observables: raw symmetry contrast `M`, paired ordering score
`frac(M_A > M_B)`, rank `AUC`, structural access (4-hop reach from the probe),
effective alternatives `exp(H)` over length-4 walks, edge count, total weight,
active-diagonal count.

Add three, defined here before execution:

- **Unused growth capacity:** fraction of the 128 candidate connections still
  inactive, `|inactive| / 128`.
- **Weight headroom:** mean over present edges of `(W_MAX − w) = (6 − w)`.
- **Normalised memory contrast:** `M_norm = M / total_weight` (total over present
  edges). Approaches 0 as the world saturates toward all-weights-6.

These are three separate quantities. `M_norm` and headroom are **not** asserted to
be a universal "novelty budget"; they are simple bookkeeping of how much of the
bounded, finite capacity remains.

## Uncertainty reporting

For **Growing vs the revised control**, and **Growing vs Reinforced**, report
paired differences with **seed-pair bootstrap** 95% CIs at key checkpoints
(`400, 2000, 10000`), resampling **whole A/B seed pairs** (the seed is the
resampling unit and carries both its A and B worlds). Statistics bootstrapped:
memory `AUC`, `|M_norm|`, effective alternatives, structural access.

## Long-run reasoning to verify (not assume)

Astra's reading: finite candidate set + bounded positive weights + no deletion +
persistent exploration ⇒ every candidate activates and every weight → 6.
Analytically this looks correct (the walk is an irreducible recurrent chain on a
finite connected graph, so every present edge is traversed infinitely often and
its weight → 6; every cell's four base edges then exceed θ, so every candidate
activates). We will **verify empirically** and separate three things that are easy
to conflate:

1. **Convergence of the structural state** (toward all-active, all-weights-6).
2. **How long a finite-precision reader can still distinguish histories** — a tiny
   *signed* residual can keep the ordering score above chance long after the
   *magnitude* `|M_norm|` has become negligible. So chance-level decoding must
   **not** be inferred merely from structural convergence, nor durable *practical*
   memory from sign alone.
3. **Numerical rounding.** With `w ← w + 0.5(6 − w)`, the gap `(6 − w)` halves per
   traversal, so after ~52 traversals an edge is exactly `6.0` in float64. Heavily
   used edges therefore round to identical saturated weights and produce **exact
   ties**. We report the tie fraction (`M_A == M_B` exactly) and treat ties as
   chance (0.5).

10,000 steps may well **not** reach saturation; we report remaining capacity
honestly and do **not** auto-extend the run.

## Wording correction carried into the report

v1 described subsequent evolution as "symmetric erosion". Corrected: the *rule* is
symmetric between the two mirror histories, but an individual walker responds to
its own history-shaped weights and can **reinforce** the existing trace rather than
only erode it (v1 already showed Growing's raw `M` *increasing* over 400 steps).

## Interpretation guards (stated up front)

- The paired ordering score is **not** single-world classification accuracy: it
  compares each seed's A-world against its own paired B-world, using known
  coordinates to define the axis. It is a *relative, coordinate-aided* readout.
- Effective alternatives (`exp(H)`, length-4 walks) measures **diversity of walks,
  including backtracking** — not the number of independent destinations and not
  useful transport performance.
- Even after fixing timing, **local placement near the probe** and **unequal
  evolved weights** remain live alternative explanations for any residual Growing
  advantage. We add **no** further control families and **no** parameter sweeps in
  this run.

## Validation gate before trusting v2

Reproduce v1's Fixed, Reinforced and Growing checkpoint results at 400 steps
(expected exact, since code paths, seeds and RNG usage are unchanged). The revised
**control is expected to differ** from v1's; the v1 control numbers are preserved
for side-by-side comparison.

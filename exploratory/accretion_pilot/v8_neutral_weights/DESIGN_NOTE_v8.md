# Design note (v8) — neutral weight background, history-shaped placement

*Written before execution. Register: speculative exploration; not a confirmatory
study, not cosmology. Bounded follow-up (chain v1 `cc514ee` → … → v7 `0c990b1`).
Isolated under `exploratory/accretion_pilot/v8_neutral_weights/`. v1–v7 retained
unchanged (a dated wording clarification is appended to
`../v7_directionality/REPORT_v7.md`, numbers preserved). No merges, publishing,
sealed-study access, dynamics changes, or parameter tuning. Intervention on initial
conditions only; movement/reinforcement/growth rules are v2's, unchanged.*

Requested by Astra (Katie has authorised Astra to steer routine steps here).

## Question

Can initial **diagonal placement** guide a later history-discriminating visitation
footprint when the **original-edge weights carry no A/B directional bias**?

## Construction

From v6's deterministic post-history Growing states, take the original-edge weight
maps `W_A`, `W_B` and diagonal sets `T_A`, `T_B`. Define a **neutral background** on
every original edge:

    W_0(e) = (W_A(e) + W_B(e)) / 2

and build two worlds, differing **only** in diagonal placement:

- `W_0 + T_A`
- `W_0 + T_B`

Initial added-diagonal weights are 1; the walker starts at the central probe
`(4,4)`; all existing Growing dynamics are retained. Diagonals are added in the
declared deterministic order (sorted edge-key), as for v6's crossed worlds.

**To verify at construction:**
- `W_0` is invariant under the transpose reflection σ (since `W_B = σ(W_A)`, so
  `W_0(σe) = W_0(e)`) — i.e. no A/B directional bias;
- `T_B = σ(T_A)` (transpose partners);
- the two worlds have matching initial **edge counts** and **total weight**, **zero**
  initial high bits, and **transpose-related full states** (`W_0+T_B = σ(W_0+T_A)`).

**Documented explicitly (not hidden):** averaging preserves the original-edge
**total** weight (`Σ W_0 = Σ W_A = Σ W_B`) but **changes its multiset** and therefore
the **local growth-trigger conditions** relative to v6 (a cell's activity is
`Σ(w−1)` over its four base edges; averaging moves individual edge weights, so
diagonals activate on a different schedule than in any v6 world). This is a
**specified neutral background**, not the removal of every historical consequence:
`W_0` still carries history-shaped *magnitude* (heavy along both staircases,
symmetrised), and the diagonal placement `T` still encodes the history. The only
thing that differs **between the two v8 worlds** is that placement.

## Run

Existing 200 seed blocks; common-random-number convention (each world
re-instantiates `default_rng(BASE_SEED + seed)`); all eight v6 checkpoints
`{0,100,200,400,1000,2000,5000,10000}` through 10,000 steps. Save full edge
snapshots. Reuse existing v6/v7 results for descriptive context; do **not** rerun the
four old conditions.

## Frozen reader and analysis

Reader unchanged from v5:

    S_high = Σ s(e)·1[w(e) ≥ 5.5]   over present added diagonals   (existing sign, A-positive)

**Primary endpoint: t = 2000** — selected from the preceding exploration (where the
footprint peaks), **not** an independently chosen confirmatory endpoint; other
checkpoints are descriptive.

Report:
- **Fixed-orientation AUC** distinguishing `T_A` from `T_B` using `S_high`
  (`T_A` positive; orientation fixed in advance, never flipped after seeing results);
- **mean signed separation** between the two conditions,
  `mean(S_high[W_0+T_A]) − mean(S_high[W_0+T_B])`;
- **seed-block bootstrap 95% intervals** for both, preserving the paired worlds;
- at **every** checkpoint: signed mean, mean absolute imbalance `|S_high|`,
  positive/zero/negative fractions, and present / high-bit diagonal counts.

We do **not** treat the 200 paired worlds as independent edge observations; all
statistics are at the world/seed level.

## Interpretation boundaries (pre-stated)

- An informative later reader would show that `T_A` vs `T_B` affects the footprint
  **under this particular symmetric `W_0` background**. It would **not** establish
  universal topology sufficiency, topology as the late storage carrier, or
  independence from reinforcement and subsequent growth.
- A result **near chance** would **not** establish absence of all recoverable
  history, nor the necessity of aligned weights. We report uncertainty either way.
- The initial **presence** pattern already distinguishes the histories (that is how
  the worlds are built); the question is whether it **guides the later thresholded
  visitation pattern**, whose bits start empty.

## Deliverables

This note; implementation; validation (construction + reproduction of the reader);
saved snapshots; result tables; one clear reader-over-time figure; concise report;
dated v7 wording clarification. Commit on the existing branch.

# Report v4 — reader decomposition

*Plain-language write-up, written after the run. Register: speculative
exploration; not a confirmatory study, not cosmology. Bounded follow-up to v3.
Rules fixed in advance in [`DESIGN_NOTE_v4.md`](DESIGN_NOTE_v4.md). We changed only
the reader. 200 seed pairs, v2 checkpoints. Reproduce: `python accretion_pilot_v4.py`.
This report deliberately separates **observations**, **algebraic identities**, and
**mechanistic hypotheses**.*

## Why this run exists (and what it corrects)

v3 concluded Growing's late memory was "topological". That was wrong. Direct count
of the v2 worlds at t=10000: **Growing has 200/200 A-worlds and 199/200 B-worlds
with all 128 diagonals present — 2 missing candidate edges in total.** Topology is
essentially identical across worlds and histories, so it cannot carry the
full-reader AUC of ~0.613. A dated correction is appended to
[`../v3_precision/REPORT_v3.md`](../v3_precision/REPORT_v3.md), withdrawing
"topological", "sub-quantum", and the dropout-confirms-topology claim (the v3
numbers are preserved). This run decomposes the readout to find where the signal
actually is.

## The readers (all use the existing coordinate sign s(e))

- **presence** `P = Σ s(e)` over present edges (weight 1 each);
- **original-edge weights** `B = Σ s(e)·q(w)` over the 144 base grid edges;
- **added-edge weights** `D = Σ s(e)·q(w)` over activated diagonals;
- **full** `M = B + D` (the v3 reader);
- **departure from saturation** `R = Σ s(e)·(q(w) − 6)` over present edges.

At Δ ∈ {0 exact, 1 whole-number}. **Verified:** M reproduces v3's full reader for
all 12,800 (model, history, seed, checkpoint) values (max |ΔM| 5e-8 at Δ=0, exactly
0 at Δ=1). Measurement consumed no dynamics RNG and changed no trajectory. Full
edge snapshots are retained in `results/edge_snapshots.npz` for future reader-only
analyses.

## Algebraic identities (checked every snapshot, not mechanisms)

`M = B + D` and `M = 6·P + R` hold exactly on every snapshot (integer arithmetic at
Δ=1). These are bookkeeping decompositions of the readout. **AUC is not additive**:
a component's standalone AUC is not its share of the full AUC, and the components
are correlated so they can reinforce or cancel.

## Observation 1 — where the discrimination lives, and that it moves over time

Growing, AUC of each reader (whole-number Δ=1; exact Δ=0 is within ~0.01):

| reader | t = 400 (early) | t = 10000 (late, near saturation) |
|---|---|---|
| presence `P` | 0.834 | **0.497 (chance)** |
| original-edge `B` | **0.947** | 0.564 |
| added-edge `D` | 0.829 | **0.616** |
| full `M` | 0.901 | 0.613 |
| departure `R` | 0.935 | 0.613 |

- **Early**, the signal is strongest in the **original-edge weights** (`B` 0.947,
  above the full reader `M` 0.901 — a clear case of AUC non-additivity, where adding
  the noisier `D` component *dilutes* the full reader), with a substantial
  **presence** contribution (`P` 0.834, because at t=400 only ~50 of 128 diagonals
  are active and *which* ones differs between A and B).
- **Late**, presence has fallen to **chance** (topology is complete/identical), the
  original-edge weights carry little (base edges have nearly all saturated to 6),
  and the surviving discrimination sits in the **added-edge weights** (`D` 0.616),
  which equals the departure-from-saturation reader `R` because near saturation
  `M ≈ 6P + R` with `P` almost constant.

So which reader component predicts **shifts over time**: from original-edge weights
+ presence early, to added-edge weights late. *This is an observation about
correlated readers, not a demonstrated mechanism.* We explicitly do **not** call it
"memory transfer" — nothing here shows a stored quantity moving from one substrate
to another; it shows which measurable component happens to carry the A/B contrast at
each stage.

## Observation 2 — the complete-topology subset settles "presence vs weights"

Restricting to the 199 Growing seed pairs whose **both** A and B worlds have all 128
diagonals present (identical topology), at t=10000 (descriptive, selected after
evolution — not a matched causal comparison):

| reader | AUC (complete-topology subset) |
|---|---|
| presence `P` | **0.500 exactly** (ties 1.00) |
| full `M` (exact) | 0.627 |
| departure `R` (exact) | 0.627 |
| full `M` (Δ=1) | 0.615 |

With topology held identical, the presence contrast is exactly chance by
construction, yet the full and departure readers discriminate at 0.627 — the **same
as the whole population**. This is the clean statement: **the late discrimination is
carried by weights, not by which edges exist.** For the matched control the same
subset gives full-`M` AUC 0.528 (near chance): with history-blind placement, even
the weights on its (identically complete) topology barely separate A from B.

## Mechanistic hypothesis (offered as hypothesis, not established)

Consistent with `D`/`R` carrying the late signal: after all diagonals are present,
the walker still treads the history-favoured side more, so the **weights on the
worn-side diagonals sit at/near the cap 6 while their mirror-side counterparts read
one bin lower** — a weight asymmetry on added edges that a whole-number reader can
still see. This is an interpretation consistent with the decomposition; the
decomposition itself is algebraic and does not prove this dynamical story.

## Interpretation limits (carried forward and honoured)

- A component's standalone AUC is **not** its unique causal contribution; `B`, `D`
  (and `6P`, `R`) are correlated and can cancel or combine. We report standalone
  AUCs and the exact identities, and equate neither with a mechanism.
- The presence contrast failing does **not** rule out every possible topology-based
  decoder — only this coordinate-signed presence sum. Conversely, within the
  complete-topology subset the topology is genuinely identical, so **no**
  topology-only reader can distinguish A from B there.
- The complete-topology subset is descriptive and selected after evolution.
- This whole series reads with known coordinates; it is memory *with external
  coordinates*, not intrinsic self-addressing.

## Bootstrap (exploratory)

Seed-pair bootstrap (whole A/B pairs) at t=10000, Δ=1:

- **added-edge reader `D`:** Growing 0.616 [0.562, 0.666] vs control 0.499
  [0.442, 0.557]; **Growing−control +0.117 [0.046, 0.195]** — the added-edge
  weights are exactly where Growing beats the matched control, and significantly.
- **full reader `M`:** Growing 0.613 [0.557, 0.666]; Growing−control +0.086
  [0.009, 0.168].
- **presence reader `P`:** Growing 0.498, control 0.503; Growing−control −0.005
  [−0.015, 0.000] — no difference, both at chance.

So the model difference that v1–v3 kept finding is, late, an **added-edge weight**
difference. Full intervals per reader and checkpoint are in
[`results/bootstrap_by_reader.csv`](results/bootstrap_by_reader.csv); all such
comparisons are treated as exploratory, not independent confirmations.

## One worthwhile next question

We now know the late carrier is *added-edge weights*, specifically the signed
departure from saturation on history-shaped diagonals. The sharp next reader
isolates exactly that: **read only the added diagonals, and only their sign of
departure from the cap** — i.e. per worn-side vs mirror-side, is this diagonal
strictly below 6 or exactly at 6? If a one-bit-per-diagonal "at-cap vs below-cap"
reader on the added edges alone reproduces the late AUC, the late memory is
literally "which shortcuts finished saturating first", a maximally simple and
testable statement. That is a reader-only follow-up on the snapshots already
retained here — no new worlds, no dynamics change.

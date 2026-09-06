# Pre-analysis note (v7) — magnitude vs direction-consistency

*Written before the analysis. Register: speculative exploration; not a confirmatory
study, not cosmology. Bounded, snapshot-only reanalysis of v6 (chain v1 `cc514ee` →
… → v6 `a3b6bc8`). Isolated under `exploratory/accretion_pilot/v7_directionality/`.
Uses v6's retained snapshots only — no new worlds, dynamics, parameter sweeps,
merges, publishing, or sealed-study access. v1–v6 retained unchanged; a dated
wording correction is appended to `../v6_intervention/REPORT_v6.md` (numbers
preserved).*

Requested by Astra (Katie has authorised Astra to steer routine steps here).

## Why — corrections to the v6 interpretation

These are appended to v6's report (numbers unchanged); the reanalysis below acts on
them:

1. The crossed worlds `W_A+T_B` and `W_B+T_A` **contain both ingredients, in
   opposition** — they are *not* "either ingredient alone". So v6's phrase "neither
   alone suffices" is withdrawn: this design never isolated an ingredient alone.
2. A **near-zero signed mean does not imply small per-world footprints.** The
   crossed worlds' per-world `S_high` standard deviation is ≈13–14 at t=2000.
3. Under transpose symmetry with the signed reader, the population means satisfy
   `μ_AA = −μ_BB` and `μ_AB = −μ_BA`, so the signed-mean interaction
   `μ_AA − μ_BA − μ_AB + μ_BB` is **zero by symmetry**. v6's finite-sample value
   (−2.26) therefore does **not** establish sub-additivity; that reading is
   withdrawn.
4. Reader saturation (`S_high → P_D → 0` late) is a **consequence of the model and
   this measurement**, not automatically an implementation artifact; v6's "artifact"
   wording is softened accordingly.

**Symmetry vs coupling (to check).** The weighted-walk *marginal* transition law
depends only on edge weights, not on neighbour/array ordering, so it is
transpose-symmetric and the population identities above hold. Neighbour ordering
(history-activation order for intact worlds, sorted-key order for crossed worlds)
affects only the **common-random-number coupling** — which seed maps to which
realised path — not the marginal law. We will verify empirically that the signed
means obey `μ_AA + μ_BB ≈ 0` and `μ_AB + μ_BA ≈ 0` (bootstrap CIs consistent with 0),
distinguishing a genuine marginal asymmetry from finite-sample / coupling residue.

## Question

Does crossing the inherited arrangements **reduce each world's directional footprint
magnitude**, or **mainly reduce the consistency of its direction across worlds**?

## Frozen analysis (v5/v6 reader, unchanged; snapshot-only)

`S_high = Σ s(e)·1[w_e ≥ 5.5]` over present added diagonals; existing coordinate
sign and threshold; A-positive orientation fixed in advance. `|S_high|` is called
**unsigned directional imbalance** — *not* memory by itself; random asymmetry can
produce it.

For all four worlds and all original checkpoints, report:

- mean signed `S_high`;
- mean `|S_high|`;
- median and interquartile range of `|S_high|`;
- fractions `S_high > 0`, `= 0`, `< 0`.

**Alignment-class comparison (checkpoints 400, 2000, 10000).** Within each seed
block define
`A_k = (|S_AA| + |S_BB|)/2` (aligned) and `C_k = (|S_AB| + |S_BA|)/2` (crossed);
report `mean(A_k − C_k)` with bootstrap CIs resampling whole four-world seed blocks,
**and** the constituent four-world `|S|` distributions (not only pooled averages).
We do **not** claim equivalence if an interval includes zero — we report the
estimate and its uncertainty.

**Descriptive counts (from snapshots).** Per world, total number of **high-bit
diagonals** (`Σ 1[w ≥ 5.5]` over present added) and **present diagonals**. These
help distinguish "directional balance" from "simply having fewer activated / high-bit
connections". They are post-intervention consequences — reported, **not** adjusted
away or treated as matched controls.

**Verification before interpretation:** reproduce `S_high` and confirm snapshot
coverage (4 worlds × 8 checkpoints × 200 seeds) against v6.

## Visualisation

One compact figure: the four **signed** `S_high` distributions at t=2000 on
identical axes (showing individual spread clearly), plus **unsigned imbalance**
`|S_high|` over time for all four worlds.

## Interpretation boundaries (pre-stated)

- Large `|S|` does **not** establish recoverable information about a particular
  initial ingredient — random asymmetry produces imbalance too.
- A low signed mean can **coexist** with large individual imbalance (the point of
  this run).
- An aligned-minus-crossed `|S|` difference concerns **this defined directional
  readout**; it is **not** uniquely evidence of nonlinear cooperation — even additive
  opposing effects change `|S|`.
- These four conditions **cannot** establish either ingredient's sufficiency in
  isolation.
- **No alignment-axis intervention** in this run.

# Follow-up design note (v3) — finite-precision readout

*Written before execution. Register: speculative exploration; not a confirmatory
study, not cosmology. Bounded follow-up to v2
(commit `cab9254b9d7713a65c314ca81f45c2d378ab60ba`). Isolated under
`exploratory/accretion_pilot/v3_precision/`. v1 and v2 are retained unchanged.
Nothing here is merged or published; no sealed-study access; no parameter tuning;
no new growth or control families.*

Requested by Katie and Astra. **We change only the reader, not the world.**

## Question

Does Growing's history-discrimination advantage survive imperfect measurement of
edge weights, particularly near saturation?

## What stays exactly v2

The graph dynamics, histories, all 200 seed pairs, parameters, checkpoints
(`0,100,200,400,1000,2000,5000,10000`), and the activation-time-and-count matched
control are **exactly** v2. v3 imports v2's dynamics code directly
(`accretion_pilot_v2.py`) and replays the identical trajectories, so the worlds
are byte-for-byte the v2 worlds. Measurement never alters weights, random streams,
movement, or growth — the reader only *copies and reads* the weight of each present
edge at a checkpoint.

**Validation gate:** for the exact reader (Δ=0) we recompute the symmetry contrast
`M` for every `(model, seed, history, checkpoint)` and require it to match v2's
saved `M` (`../v2_saturation/results/raw_metrics.csv`) within v2's CSV rounding
tolerance. This proves the replay reproduces v2 before any degraded reading is
analysed.

## The imperfect reader (one transparent model)

Deterministic weight **quantisation** — not random noise. Every present edge is
read as

    w_read = Δ · floor(w / Δ + 0.5)          (round-half-up to the nearest Δ grid)

at the fixed, pre-declared resolutions

    Δ ∈ { 0 (exact), 0.001, 0.01, 0.1, 0.5, 1.0 }

in absolute units on the existing 1–6 weight scale. For Δ=0 the original weight is
used. This grid is fixed in advance; every resolution is retained and the grid is
**not** refined around favourable results. These bin boundaries include the
saturation value 6 exactly (e.g. `6/0.5+0.5=12.5 → 12 → 6.0`), so conclusions are
conditional on a reader whose grid lands on 6.

The measured contrast is `M_meas = Σ_e sign(e)·w_read(e)` over present edges, where
`sign(e) = sign(col_mid − row_mid) ∈ {−1,0,+1}` (unchanged from v1/v2), in a
**canonical edge order** (edges sorted by key) with numerically stable summation.

**Integer bin counts (so rounding cannot manufacture a sign).** For Δ>0,
`w_read = Δ·n_e` with integer `n_e = floor(w/Δ+0.5)`, so
`M_meas = Δ · (Σ_e sign(e)·n_e)` where the bracket is an **exact integer**. We
compute that integer in exact arithmetic; the sign of `M_meas` is therefore exact
and free of float artefacts. For Δ=0 we use `math.fsum` over the canonical order.

**Scope of the reader (stated explicitly).** This tests **weight precision only**.
Topology, vertex coordinates, and edge presence remain perfectly readable; missing
edges remain missing. This is **not** a generally noisy or coordinate-free
observer, and we add **no** separate topology-only analysis in this run.

## Measurements

For each `(model, checkpoint, resolution)`:

- **AUC** of measured `M` separating A- from B-worlds (rank AUC, midrank ties).
- **Paired ordering score** `frac(M_A > M_B)`, ties worth one half.
- **Fraction of paired ties** (`M_A == M_B` exactly, at that resolution).
- **Signed history separation** `mean(M_A) − mean(M_B)`.

Absolute asymmetry is kept **separate** from history information: a large `|M|`
alone is not evidence of remembering A vs B; the signed separation and the
A-vs-B scores are what speak to history.

**Single-world decoder (fixed, fits nothing).** Using the original known
orientation, predict A if `M_meas > 0`, B if `M_meas < 0`, half credit if `= 0`.
Report **balanced accuracy** (mean of per-class recall). This complements — does
not replace — the paired score and AUC.

**Between-model comparisons.** At checkpoints `400, 2000, 10000`, report
Growing−control and Growing−Reinforced **AUC differences** with bootstrap 95%
intervals resampling whole A/B seed pairs. These comparisons are treated as
**exploratory**, not a set of independent confirmatory discoveries.

## Interpretation limits (pre-stated)

- Quantisation is *one* measurement model. Its resolution is **not** equated with
  biological, hardware, or physical noise.
- A failed readout does **not** prove the graph contains no recoverable history; a
  successful readout does **not** reconstruct the journey.
- We do **not** assume coarser measurement makes every finite-sample metric
  decrease monotonically — we report the actual curves.

## Expectations (pre-registered, not targets)

Fine Δ (0.001, 0.01) should barely change v2's picture. Coarse Δ (0.5, 1.0) should
increase ties and pull discrimination toward chance, most severely late (near
saturation, where weights cluster at/near 6 and the surviving signal is a tiny
signed residual that coarse bins erase). Whether Growing's *advantage over the
control* survives at intermediate Δ, and at which resolution ties dominate, are the
open questions. Mixed or negative outcomes are equally informative. We run once at
the declared grid and report whatever happens.

## Deliverables

Design note (this file), code + one-line reproduction command + validation of
unchanged dynamics, raw and summary tables, one compact figure (discrimination vs
weight resolution at an early and a late checkpoint, with exact-readout
references), and a plain-language report. No longer trajectories, locality
controls, or alternative noise models in this run.

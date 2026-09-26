# Report v7 — magnitude vs direction-consistency

*Plain-language write-up, written after the run. Register: speculative
exploration; not a confirmatory study, not cosmology. Bounded, snapshot-only
reanalysis of v6. Rules fixed in advance in
[`PRE_ANALYSIS_NOTE_v7.md`](PRE_ANALYSIS_NOTE_v7.md). Reproduce:
`python accretion_pilot_v7.py`. Uses v6's retained snapshots only.*

## Question

Does crossing the inherited arrangements **reduce each world's directional
footprint magnitude** (`|S_high|`), or **mainly reduce the consistency of its
direction across worlds** (sign agreement across seeds)?

## Answer — it scrambles direction, not magnitude

At t=2000 (the mid-run peak), the four worlds' one-bit footprint `S_high`:

| world | mean (signed) | mean \|S\| | sd | frac + / 0 / − | high-bit diagonals |
|---|---|---|---|---|---|
| `W_A+T_A` (intact A) | +5.99 | 11.42 | 13.0 | 0.69 / 0.04 / 0.28 | 70.4 |
| `W_A+T_B` (crossed) | +1.55 | 11.47 | 14.0 | 0.56 / 0.02 / 0.42 | 71.2 |
| `W_B+T_A` (crossed) | +0.92 | 10.60 | 13.4 | 0.52 / 0.03 / 0.46 | 71.7 |
| `W_B+T_B` (intact B) | −5.78 | 12.35 | 13.9 | 0.32 / 0.02 / 0.66 | 70.2 |

Every world — aligned **and** crossed — develops a large per-world directional
imbalance (`mean|S| ≈ 11`, `sd ≈ 13`), on a comparable number of high-bit diagonals
(~70–72). What differs is **sign consistency across seeds**: the intact worlds land
on a consistent direction (A: 69% positive; B: 66% negative), while the crossed
worlds are near a **coin-flip** (52–56% positive). The crossed worlds' near-zero
*signed* means (+1.55, +0.92) reflect this cancellation, **not** a missing footprint.

The unsigned alignment contrast confirms it. With
`A_k = (|S_AA|+|S_BB|)/2`, `C_k = (|S_AB|+|S_BA|)/2` per seed:

| checkpoint | mean(A_k − C_k) | 95% CI |
|---|---|---|
| 400 | +0.59 | [0.12, 1.07] |
| 2000 | +0.85 | [−0.32, 1.96] |
| 10000 | −0.09 | [−0.20, 0.02] |

Aligned worlds carry at most a *small* excess unsigned imbalance over crossed
(≈0.6 on a base of ~5 early; at the t=2000 peak the CI includes 0). So crossing does
**not** meaningfully shrink per-world magnitude. The large v6 gap was in the
*signed mean* — i.e. in **direction consistency**, which is exactly what alignment
governs. We report the estimate and its uncertainty and do not claim equivalence
where a CI includes 0.

## Symmetry verified (the v6 "interaction" was zero by construction)

Under transpose symmetry with the signed reader, the population means satisfy
`μ_AA = −μ_BB` and `μ_AB = −μ_BA`, so the signed-mean interaction
`μ_AA − μ_BA − μ_AB + μ_BB` is **zero by symmetry**. Empirically the residuals are
consistent with 0 at every checkpoint (bootstrap CIs, resampling seed blocks) —
e.g. at t=2000, `μ_AA+μ_BB = +0.21 [−2.45, 2.96]` and
`μ_AB+μ_BA = +2.47 [−0.30, 5.16]`. So v6's finite-sample interaction (−2.26) is
noise and does **not** establish sub-additivity (that reading is withdrawn in v6's
report). The *marginal* transition law depends only on edge weights, not
neighbour/array ordering, so it is transpose-symmetric; ordering affects only the
common-random-number coupling (which seed maps to which realised path), not these
marginal means — the two are distinguished, and the marginal symmetry is what holds.

## Late collapse is symmetric saturation, for every world

By t=10000 all four worlds have `mean|S| ≈ 0.6` and ~127 high-bit diagonals
(near-complete saturation), with `S_high → P_D → 0` on complete topology. The
directional imbalance itself fades as the world fills in symmetrically — a
consequence of the model and this reader, not an implementation artifact, and it
happens equally for aligned and crossed worlds.

## What this does and does not show (boundaries honoured)

- Large `|S|` is **unsigned directional imbalance**, not memory by itself — random
  asymmetry produces imbalance too. That every world has large `|S|` says the world
  *develops a lopsided high-bit pattern*, not that it *remembers* a particular
  ingredient.
- A low signed mean coexists with large individual imbalance — demonstrated here.
- The small aligned-minus-crossed `|S|` difference concerns **this** directional
  readout; it is **not** uniquely evidence of nonlinear cooperation (even additive
  opposing effects change `|S|`).
- These four conditions **cannot** establish either ingredient's sufficiency in
  isolation (crossed worlds hold both ingredients in opposition, not one alone).
- No alignment-axis intervention was run.

## One worthwhile next question

The reframed finding is that alignment governs **direction reproducibility** across
seeds, not per-world footprint size. A sharp, still snapshot-only next step:
quantify direction consistency directly — for each world, the seed-to-seed
**sign-agreement rate** of `S_high` (and a per-seed **direction correlation** of the
signed *per-diagonal* high-bit pattern between the paired A- and B-worlds within
each alignment class). That would measure "how reproducibly does the footprint point
the same way" as its own quantity, separate from magnitude, on the snapshots already
retained — before any alignment-axis intervention on new worlds.

---

## Wording clarification — 2026-09-07 (numbers above unchanged)

*Added while running v8. The tables and estimates above are preserved; this
tightens two categorical phrasings into estimates-with-uncertainty.*

1. **"Scrambles direction, not magnitude" / "does not meaningfully shrink per-world
   magnitude" is too categorical.** The aligned−crossed unsigned `|S|` difference is
   **positive and its CI excludes 0 early** (t=400: +0.59 [0.12, 1.07]); at the
   t=2000 peak it is +0.85 **[−0.32, 1.96]** — an interval that includes both 0 and
   sizeable positive values, so it **does not establish equivalence** of aligned and
   crossed magnitudes. The accurate statement: the magnitude difference is **small
   relative to the direction-consistency difference**, positive and resolved early,
   and **unresolved (consistent with anything from ~0 to ~2) at the peak** — whereas
   the sign-consistency gap is large and clear (aligned ~66–69% vs crossed ~52–56%).
2. **The symmetry checks are consistent with, not proof of, the analytical
   symmetry.** The residuals `μ_AA+μ_BB` and `μ_AB+μ_BA` have bootstrap CIs that
   **include 0**, which is *consistent with* the exact identities `μ_AA=−μ_BB`,
   `μ_AB=−μ_BA` (which hold analytically because the marginal transition law is
   order-independent and transpose-symmetric). A CI containing zero does **not**
   prove equality; the analytical argument is what establishes it, and the data are
   consistent with it.

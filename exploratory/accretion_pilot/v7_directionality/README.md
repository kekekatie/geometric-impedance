# Accretion pilot v7 — magnitude vs direction-consistency

Bounded, **snapshot-only** reanalysis of [v6](../v6_intervention/). No new worlds,
dynamics, or parameter sweeps: v7 loads v6's retained snapshots
(`../v6_intervention/results/edge_snapshots_v6.npz`) and applies the frozen v5/v6
reader `S_high = Σ s(e)·1[w_e ≥ 5.5]`.

**Question:** does crossing the inherited arrangements reduce each world's
directional footprint **magnitude** (`|S_high|`), or mainly reduce the
**consistency of its direction across worlds**?

> Speculative exploration; not a confirmatory study, not cosmology. Isolated; uses
> nothing from the sealed studies. Not for merge or publication. v1–v6 retained
> unchanged; a dated wording correction is appended to
> `../v6_intervention/REPORT_v6.md` (numbers preserved).

## Read in this order

1. [`PRE_ANALYSIS_NOTE_v7.md`](PRE_ANALYSIS_NOTE_v7.md) — the corrections, the
   question, the frozen analysis (written before analysis).
2. [`REPORT_v7.md`](REPORT_v7.md) — findings.
3. [`accretion_pilot_v7.py`](accretion_pilot_v7.py) — the snapshot-only analysis.

## Reproduce

```bash
python accretion_pilot_v7.py           # snapshot-only; ~5 s
```

Startup verifies snapshot coverage (4 worlds × 8 checkpoints × 200 seeds) and
reproduces v6's `S_high` means.

Outputs:

```
results/config.json                # reader, source, environment
results/validation_vs_v6.txt       # S_high reproduction check
results/frozen_readouts.csv        # per world/checkpoint: mean signed, mean|S|, median/IQR|S|, sign fractions, counts
results/alignment_unsigned.csv     # A_k=(|S_AA|+|S_BB|)/2 vs C_k=(|S_AB|+|S_BA|)/2, bootstrap CIs
results/symmetry_check.csv         # residuals mu_AA+mu_BB and mu_AB+mu_BA (bootstrap CIs)
figures/directionality_v7.png      # signed distributions at t=2000 + unsigned |S| over time
```

## Environment

- Python 3.11.15, numpy 2.4.6 (imports `numpy` and `matplotlib`; reads the v6 npz).

## One-paragraph result

Crossing scrambles **direction**, not **magnitude**. At t=2000 all four worlds —
aligned and crossed — have comparable per-world imbalance (mean|S| ≈ 11, sd ≈ 13)
on comparable high-bit counts (~70–72); the aligned−crossed unsigned difference is
small and its CI includes 0 at the peak (+0.85 [−0.32, 1.96]). What differs is sign
consistency across seeds: intact A/B are ~66–69% consistent in direction, crossed
worlds ~52–56% (near a coin-flip), so their near-zero *signed* means reflect
cancellation, not a missing footprint. The transpose-symmetry identities
`μ_AA=−μ_BB` and `μ_AB=−μ_BA` are verified (residual CIs include 0), so v6's
signed-mean "sub-additive interaction" was zero by symmetry (withdrawn). The late
collapse (`S_high → P_D → 0`) is symmetric saturation, for every world. `|S|` is
unsigned directional imbalance, **not** memory by itself. See
[`REPORT_v7.md`](REPORT_v7.md).

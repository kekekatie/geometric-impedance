# Snap-back threshold analysis v0.1

## Hypothesis
Address recovery at depth isn't gradual — it snaps. There's a critical
number of steps spent at depth below which almost no recovery happens,
and above which recovery is nearly complete.

## Setup
- Seeds: 10, Walkers/seed: 30000, Steps: 1024
- Near-return thresholds: [2.0, 3.0]
- Dip threshold: excursion > 0.15
- Linger: steps within 20% of excursion above minimum depth
- Aligned window: 200 steps before, 400 after minimum

## Linger duration bins

| substrate   |   threshold | linger_bin   |   n |   mean_residue |   median_residue |   std_residue |   mean_excursion |   mean_start_depth |
|:------------|------------:|:-------------|----:|---------------:|-----------------:|--------------:|-----------------:|-------------------:|
| AB_N30      |           2 | 1-4          |  46 |       1.02549  |         0.765367 |      0.599437 |         0.192949 |           0.212714 |
| AB_N30      |           2 | 5-9          | 105 |       1.16977  |         1.41421  |      0.551687 |         0.214444 |           0.241252 |
| AB_N30      |           2 | 10-19        | 255 |       1.13232  |         0.765367 |      0.584056 |         0.261668 |           0.291638 |
| AB_N30      |           2 | 20-39        | 519 |       1.05342  |         0.765367 |      0.552196 |         0.351948 |           0.384544 |
| AB_N30      |           2 | 40-79        | 569 |       0.954746 |         0.765367 |      0.510595 |         0.506612 |           0.53954  |
| AB_N30      |           2 | 80-159       | 304 |       0.743535 |         0.765367 |      0.385595 |         0.718263 |           0.757415 |
| AB_N30      |           2 | 160-319      |   2 |       0.382683 |         0.382683 |      0.541196 |         0.867847 |           0.93724  |
| AB_N30      |           3 | 1-4          |  67 |       1.14975  |         1.08239  |      0.594248 |         0.192422 |           0.211151 |
| AB_N30      |           3 | 5-9          | 163 |       1.31626  |         1.08239  |      0.574919 |         0.215017 |           0.241392 |
| AB_N30      |           3 | 10-19        | 389 |       1.2222   |         1.08239  |      0.563363 |         0.258088 |           0.288071 |
| AB_N30      |           3 | 20-39        | 756 |       1.1261   |         1.08239  |      0.522728 |         0.349157 |           0.381789 |
| AB_N30      |           3 | 40-79        | 822 |       1.01731  |         1.08239  |      0.459338 |         0.507083 |           0.54023  |
| AB_N30      |           3 | 80-159       | 429 |       0.846877 |         0.765367 |      0.368521 |         0.724287 |           0.762716 |
| AB_N30      |           3 | 160-319      |   4 |       0.732538 |         0.92388  |      0.510714 |         0.87278  |           0.926155 |
| Penrose_N24 |           2 | 1-4          |  99 |       1.229    |         1.17557  |      0.551239 |         0.242389 |           0.28796  |
| Penrose_N24 |           2 | 5-9          | 173 |       1.27459  |         1.17557  |      0.555536 |         0.261954 |           0.307462 |
| Penrose_N24 |           2 | 10-19        | 371 |       1.14185  |         1.17557  |      0.551243 |         0.34937  |           0.399219 |
| Penrose_N24 |           2 | 20-39        | 540 |       1.01059  |         1.17557  |      0.526258 |         0.470515 |           0.525278 |
| Penrose_N24 |           2 | 40-79        | 475 |       0.85149  |         0.618034 |      0.511322 |         0.628982 |           0.690042 |
| Penrose_N24 |           2 | 80-159       | 120 |       0.722483 |         0.618034 |      0.364963 |         0.767181 |           0.840338 |
| Penrose_N24 |           2 | 160-319      |   1 |       0.618034 |         0.618034 |    nan        |         0.784573 |           0.926885 |
| Penrose_N24 |           3 | 1-4          | 149 |       1.44224  |         1.32813  |      0.62717  |         0.241875 |           0.285006 |
| Penrose_N24 |           3 | 5-9          | 258 |       1.48089  |         1.32813  |      0.61824  |         0.262908 |           0.3077   |
| Penrose_N24 |           3 | 10-19        | 489 |       1.28305  |         1.17557  |      0.589418 |         0.340385 |           0.39073  |
| Penrose_N24 |           3 | 20-39        | 690 |       1.12046  |         1.17557  |      0.53923  |         0.473212 |           0.527093 |
| Penrose_N24 |           3 | 40-79        | 600 |       0.960203 |         1.17557  |      0.509131 |         0.629638 |           0.6906   |
| Penrose_N24 |           3 | 80-159       | 161 |       0.876717 |         0.618034 |      0.411247 |         0.767877 |           0.842105 |
| Penrose_N24 |           3 | 160-319      |   1 |       0.618034 |         0.618034 |    nan        |         0.784573 |           0.926885 |

## Snap-back threshold detection

| substrate   |   threshold | biggest_drop_from   | biggest_drop_to   |   drop_magnitude |   residue_before |   residue_after |
|:------------|------------:|:--------------------|:------------------|-----------------:|-----------------:|----------------:|
| AB_N30      |           2 | 80-159              | 160-319           |        -0.360851 |         0.743535 |        0.382683 |
| AB_N30      |           3 | 40-79               | 80-159            |        -0.170432 |         1.01731  |        0.846877 |
| Penrose_N24 |           2 | 20-39               | 40-79             |        -0.159098 |         1.01059  |        0.85149  |
| Penrose_N24 |           3 | 80-159              | 160-319           |        -0.258683 |         0.876717 |        0.618034 |

## Key results

### AB_N30

**d≤2.0** (1800 dippers across 10 seeds):
  - Spearman(linger_steps, residue): -0.2412 (p=0.0000)
  - Spearman(consecutive_linger, residue): -0.1399 (p=0.0000)
  - Shortest linger (1-4): residue = 1.0255
  - Longest linger (160-319): residue = 0.3827
  - Biggest drop: 80-159 → 160-319 (Δ = -0.3609)

**d≤3.0** (2630 dippers across 10 seeds):
  - Spearman(linger_steps, residue): -0.2491 (p=0.0000)
  - Spearman(consecutive_linger, residue): -0.1562 (p=0.0000)
  - Shortest linger (1-4): residue = 1.1497
  - Longest linger (160-319): residue = 0.7325
  - Biggest drop: 40-79 → 80-159 (Δ = -0.1704)

### Penrose_N24

**d≤2.0** (1779 dippers across 10 seeds):
  - Spearman(linger_steps, residue): -0.3245 (p=0.0000)
  - Spearman(consecutive_linger, residue): -0.1943 (p=0.0000)
  - Shortest linger (1-4): residue = 1.2290
  - Longest linger (160-319): residue = 0.6180
  - Biggest drop: 20-39 → 40-79 (Δ = -0.1591)

**d≤3.0** (2348 dippers across 10 seeds):
  - Spearman(linger_steps, residue): -0.3129 (p=0.0000)
  - Spearman(consecutive_linger, residue): -0.1964 (p=0.0000)
  - Shortest linger (1-4): residue = 1.4422
  - Longest linger (160-319): residue = 0.6180
  - Biggest drop: 80-159 → 160-319 (Δ = -0.2587)

## Interpretation rules

- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.
- Tests whether address recovery shows a phase-transition-like
  threshold in linger duration at minimum depth.
- If there IS a sharp threshold: the stable core needs a minimum
  'soak time' before the address resets — like a phase transition.
- If recovery is gradual: no threshold, just continuous improvement
  with more time at depth.

## Figures

1. fig_1_*.png — Residue vs linger duration bins (THE KEY FIGURE)
2. fig_2_*.png — Step-by-step residue trajectory aligned at minimum depth
3. fig_3_*.png — Residue at minimum vs final residue
4. fig_4_*.png — Total vs consecutive linger comparison
5. fig_5_*.png — Substrate comparison: snap-back curves overlaid
6. fig_6_*.png — Normalised recovery curve (is it a step function?)
# Brachistochrone dip profile analysis v0.1

## The hypothesis
The dip from stable/deep to unstable/shallow and back is like a brachistochrone:
fast drop, gradual return. If the shape of the dip matters for address recovery,
then the geometry is acting as an engine — the asymmetry drives reconstruction.

## Setup
- Seeds: 10, Walkers/seed: 30000, Steps: 1024
- Near-return thresholds: [2.0, 3.0]
- Dip threshold: excursion > 0.15
- Asymmetry: (ascent_steps - descent_steps) / total
  - Positive = fast descent, slow return (brachistochrone-like)
  - Negative = slow descent, fast return
  - Near zero = symmetric

## Summary (mean across seeds)

| substrate   |   threshold |   seed |   n_near_loops |   n_dippers |   mean_residue_all_dippers |   mean_residue_brachy |   mean_residue_anti_brachy |   mean_residue_symmetric |   n_brachy |   n_anti_brachy |   n_symmetric |   mean_residue_v_dip |   mean_residue_u_dip |   mean_residue_early_dip |   mean_residue_mid_dip |   mean_residue_late_dip |   n_early |   n_mid |   n_late |   spearman_asymmetry_vs_residue |   spearman_asymmetry_p |   spearman_sharpness_vs_residue |   spearman_timing_vs_residue |   spearman_recovery_vs_residue |   spearman_descent_smooth_vs_residue |   spearman_ascent_smooth_vs_residue |   spearman_excursion_vs_residue |   mean_asymmetry |   mean_sharpness |   mean_timing |   mean_excursion |   mean_recovery |
|:------------|------------:|-------:|---------------:|------------:|---------------------------:|----------------------:|---------------------------:|-------------------------:|-----------:|----------------:|--------------:|---------------------:|---------------------:|-------------------------:|-----------------------:|------------------------:|----------:|--------:|---------:|--------------------------------:|-----------------------:|--------------------------------:|-----------------------------:|-------------------------------:|-------------------------------------:|------------------------------------:|--------------------------------:|-----------------:|-----------------:|--------------:|-----------------:|----------------:|
| AB_N30      |           2 |    4.5 |          194.7 |       170.7 |                    1.00419 |              1.02042  |                   0.993315 |                  0.96993 |       89.2 |            65.2 |          16.3 |              1.13295 |             0.790376 |                  1.01932 |                1.0016  |                 0.98642 |      68.7 |    54.1 |     47.9 |                      0.0223276  |               0.526063 |                        0.224579 |                  -0.0223276  |                     -0.0979173 |                           -0.0911773 |                           -0.243687 |                       -0.254257 |         0.107758 |         0.954647 |      0.446121 |         0.439316 |         1.10189 |
| AB_N30      |           3 |    4.5 |          295.5 |       256.5 |                    1.08101 |              1.10092  |                   1.06447  |                  1.04929 |      134.4 |            96.7 |          25.4 |              1.23095 |             0.894354 |                  1.10096 |                1.07448 |                 1.0612  |     103.2 |    83.5 |     69.8 |                      0.028907   |               0.538182 |                        0.239431 |                  -0.028907   |                     -0.103892  |                           -0.0940896 |                           -0.252645 |                       -0.269602 |         0.113581 |         0.954743 |      0.443209 |         0.437853 |         1.10287 |
| Penrose_N24 |           2 |    4.5 |          196.6 |       180.3 |                    1.00584 |              0.995098 |                   1.00317  |                  1.06748 |       96.8 |            64.7 |          18.8 |              1.19654 |             0.801197 |                  0.99922 |                1.03971 |                 0.97693 |      74.6 |    57.2 |     48.5 |                     -0.00240196 |               0.612974 |                        0.268787 |                   0.00240196 |                     -0.0107969 |                           -0.14027   |                           -0.188118 |                       -0.301969 |         0.131364 |         0.966915 |      0.434318 |         0.47812  |         1.11117 |
| Penrose_N24 |           3 |    4.5 |          268.2 |       241.7 |                    1.15942 |              1.1391   |                   1.1766   |                  1.19601 |      128.4 |            87.9 |          25.4 |              1.42281 |             0.926152 |                  1.13586 |                1.1884  |                 1.16049 |      99.1 |    77.1 |     65.5 |                     -0.013187   |               0.416191 |                        0.288371 |                   0.013187   |                     -0.0852287 |                           -0.16445   |                           -0.252956 |                       -0.324286 |         0.127317 |         0.967651 |      0.436341 |         0.468509 |         1.08486 |

## Key results

### AB_N30

**d≤2.0** (171 dippers/seed):
  - Brachistochrone (fast drop): 1.0204
  - Symmetric: 0.9699
  - Anti-brachistochrone (slow drop): 0.9933
  - V-dip vs U-dip: 1.1330 vs 0.7904
  - Early vs mid vs late dip: 1.0193 / 1.0016 / 0.9864
  - Spearman(asymmetry, residue): 0.0223 (p=0.5261)
  - Spearman(recovery, residue): -0.0979

**d≤3.0** (256 dippers/seed):
  - Brachistochrone (fast drop): 1.1009
  - Symmetric: 1.0493
  - Anti-brachistochrone (slow drop): 1.0645
  - V-dip vs U-dip: 1.2310 vs 0.8944
  - Early vs mid vs late dip: 1.1010 / 1.0745 / 1.0612
  - Spearman(asymmetry, residue): 0.0289 (p=0.5382)
  - Spearman(recovery, residue): -0.1039

### Penrose_N24

**d≤2.0** (180 dippers/seed):
  - Brachistochrone (fast drop): 0.9951
  - Symmetric: 1.0675
  - Anti-brachistochrone (slow drop): 1.0032
  - V-dip vs U-dip: 1.1965 vs 0.8012
  - Early vs mid vs late dip: 0.9992 / 1.0397 / 0.9769
  - Spearman(asymmetry, residue): -0.0024 (p=0.6130)
  - Spearman(recovery, residue): -0.0108

**d≤3.0** (242 dippers/seed):
  - Brachistochrone (fast drop): 1.1391
  - Symmetric: 1.1960
  - Anti-brachistochrone (slow drop): 1.1766
  - V-dip vs U-dip: 1.4228 vs 0.9262
  - Early vs mid vs late dip: 1.1359 / 1.1884 / 1.1605
  - Spearman(asymmetry, residue): -0.0132 (p=0.4162)
  - Spearman(recovery, residue): -0.0852

## Interpretation

- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.
- Tests whether depth-dip SHAPE predicts address recovery quality.
- The brachistochrone hypothesis: fast drop + slow return = best recovery.
- If shape matters: the geometry IS the engine (asymmetry drives reconstruction).
- If shape doesn't matter: only whether you dipped matters, not how.

## Figures

1. fig_1_*.png — Brachistochrone vs anti-brachistochrone vs symmetric (KEY)
2. fig_2_*.png — V-dip vs U-dip (sharp vs broad)
3. fig_3_*.png — Dip timing (early vs mid vs late)
4. fig_4_*.png — Spearman correlation summary for all shape features
5. fig_5_*.png — Scatter: asymmetry vs residue
6. fig_6_*.png — Substrate comparison: shape sensitivity AB vs Penrose
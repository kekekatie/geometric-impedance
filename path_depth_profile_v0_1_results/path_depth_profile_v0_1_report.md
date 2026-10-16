# Path-depth profile analysis v0.1

## Core question
Do walkers that traverse a larger depth range (dip from deep to shallow
and back) accumulate more perpendicular residue than walkers that stay
at a constant depth? Is the 'curvature encountered along the path' a
better predictor than starting position alone?

## Setup
- Seeds: 10, Walkers/seed: 20000, Steps: 1024
- Near-return thresholds: [1.0, 2.0, 3.0]
- Shuffled control walkers: 5000

## Path-depth metrics computed
- **depth_range**: max depth - min depth along path
- **depth_excursion**: start depth - min depth (how far below start)
- **cum_abs_depth_change**: total absolute depth change along path
- **dip_return**: walker went >0.2 below start depth but ended near start depth
- **sign_changes**: number of depth direction reversals

## Summary (real, mean across seeds)

| substrate   |   threshold |   seed |   n_near_loops |   mean_perp_residue |   median_perp_residue |   mean_residue_high_depth_range |   mean_residue_low_depth_range |   mean_residue_high_excursion |   mean_residue_low_excursion |   mean_residue_high_cum_depth |   mean_residue_low_cum_depth |   mean_residue_dip_return |   mean_residue_no_dip |   n_dip_return |   n_no_dip |   spearman_depth_range_vs_residue |   spearman_excursion_vs_residue |   spearman_cum_depth_vs_residue |   spearman_start_depth_vs_residue |   mean_depth_range |   mean_depth_excursion |   mean_cum_abs_depth_change |
|:------------|------------:|-------:|---------------:|--------------------:|----------------------:|--------------------------------:|-------------------------------:|------------------------------:|-----------------------------:|------------------------------:|-----------------------------:|--------------------------:|----------------------:|---------------:|-----------:|----------------------------------:|--------------------------------:|--------------------------------:|----------------------------------:|-------------------:|-----------------------:|----------------------------:|
| AB_N30      |           1 |    4.5 |           23.9 |            0.777312 |              0.739104 |                        0.71828  |                       0.91772  |                      0.253994 |                     1.03387  |                      0.697456 |                     0.656688 |                  0.413114 |               1.36869 |           14.8 |        9.1 |                       -0.101774   |                       -0.294213 |                      0.0139288  |                         -0.300441 |           0.935033 |               0.379214 |                     302.898 |
| AB_N30      |           2 |    4.5 |          130.8 |            0.997701 |              0.765367 |                        0.998053 |                       1.0117   |                      0.80219  |                     1.15838  |                      1.00315  |                     0.977051 |                  0.868525 |               1.14031 |           69.7 |       61.1 |                       -0.00118541 |                       -0.263109 |                      0.0253176  |                         -0.263717 |           0.934541 |               0.399621 |                     303.224 |
| AB_N30      |           3 |    4.5 |          193.6 |            1.0837   |              1.08239  |                        1.09126  |                       1.08536  |                      0.885428 |                     1.27853  |                      1.08305  |                     1.07987  |                  0.956793 |               1.21261 |           97.9 |       95.7 |                        0.0113658  |                       -0.285219 |                      0.0126979  |                         -0.286512 |           0.934927 |               0.395186 |                     303.227 |
| Penrose_N24 |           1 |    4.5 |           21.3 |            0.614104 |              0        |                        0.517    |                       0.566312 |                      0.388328 |                     0.695755 |                      0.652607 |                     0.620246 |                  0.367268 |               1.19812 |           15.3 |        6   |                        0.0226065  |                       -0.145392 |                     -0.040871   |                         -0.156326 |           0.919262 |               0.451255 |                     287.702 |
| Penrose_N24 |           2 |    4.5 |          127.2 |            1.03129  |              1.17557  |                        0.978545 |                       1.05033  |                      0.793358 |                     1.26353  |                      1.02084  |                     1.03445  |                  0.883146 |               1.21379 |           70.2 |       57   |                       -0.0286957  |                       -0.301951 |                     -0.0270898  |                         -0.304706 |           0.915924 |               0.450107 |                     287.583 |
| Penrose_N24 |           3 |    4.5 |          168.7 |            1.18947  |              1.17557  |                        1.16541  |                       1.21091  |                      0.91647  |                     1.49902  |                      1.20761  |                     1.16904  |                  1.00955  |               1.38764 |           88.3 |       80.4 |                       -0.0124558  |                       -0.358898 |                     -0.00769608 |                         -0.364049 |           0.915974 |               0.432334 |                     287.632 |

## Shuffled control summary

| substrate   |   threshold |   seed |   n_near_loops |   mean_perp_residue |   median_perp_residue |   mean_residue_high_depth_range |   mean_residue_low_depth_range |   mean_residue_high_excursion |   mean_residue_low_excursion |   mean_residue_high_cum_depth |   mean_residue_low_cum_depth |   mean_residue_dip_return |   mean_residue_no_dip |   n_dip_return |   n_no_dip |   spearman_depth_range_vs_residue |   spearman_excursion_vs_residue |   spearman_cum_depth_vs_residue |   spearman_start_depth_vs_residue |   mean_depth_range |   mean_depth_excursion |   mean_cum_abs_depth_change |
|:------------|------------:|-------:|---------------:|--------------------:|----------------------:|--------------------------------:|-------------------------------:|------------------------------:|-----------------------------:|------------------------------:|-----------------------------:|--------------------------:|----------------------:|---------------:|-----------:|----------------------------------:|--------------------------------:|--------------------------------:|----------------------------------:|-------------------:|-----------------------:|----------------------------:|
| AB_N30      |           1 |    4.5 |            8.1 |            0.527849 |              0.359968 |                        0.902156 |                       0.615725 |                           nan |                          nan |                           nan |                          nan |                       nan |                   nan |              0 |          0 |                         0.303615  |                             nan |                             nan |                               nan |           0.930343 |                    nan |                         nan |
| AB_N30      |           2 |    4.5 |           33.5 |            0.978998 |              0.981382 |                        1.01965  |                       0.882058 |                           nan |                          nan |                           nan |                          nan |                       nan |                   nan |              0 |          0 |                         0.100601  |                             nan |                             nan |                               nan |           0.928118 |                    nan |                         nan |
| AB_N30      |           3 |    4.5 |           49.6 |            1.03683  |              1.00854  |                        1.07838  |                       0.972252 |                           nan |                          nan |                           nan |                          nan |                       nan |                   nan |              0 |          0 |                         0.117365  |                             nan |                             nan |                               nan |           0.930236 |                    nan |                         nan |
| Penrose_N24 |           1 |    4.5 |            5.1 |            0.484425 |              0.139015 |                        0.533218 |                       0.521497 |                           nan |                          nan |                           nan |                          nan |                       nan |                   nan |              0 |          0 |                        -0.0650234 |                             nan |                             nan |                               nan |           0.91432  |                    nan |                         nan |
| Penrose_N24 |           2 |    4.5 |           30.9 |            1.04738  |              1.04192  |                        1.01837  |                       1.08709  |                           nan |                          nan |                           nan |                          nan |                       nan |                   nan |              0 |          0 |                        -0.0594286 |                             nan |                             nan |                               nan |           0.917106 |                    nan |                         nan |
| Penrose_N24 |           3 |    4.5 |           40.6 |            1.08129  |              1.08534  |                        0.996817 |                       1.12328  |                           nan |                          nan |                           nan |                          nan |                       nan |                   nan |              0 |          0 |                        -0.10927   |                             nan |                             nan |                               nan |           0.917522 |                    nan |                         nan |

## Key results

### AB_N30

**d≤1.0** (24 near-loops/seed):
  - Depth range high vs low: 0.7183 vs 0.9177 (gap: -0.1994)
  - Excursion high vs low: 0.2540 vs 1.0339 (gap: -0.7799)
  - Dip-return vs no-dip: 0.4131 vs 1.3687 (gap: -0.9556)
  - Spearman(depth_range, residue): -0.1018
  - Spearman(start_depth, residue): -0.3004

**d≤2.0** (131 near-loops/seed):
  - Depth range high vs low: 0.9981 vs 1.0117 (gap: -0.0137)
  - Excursion high vs low: 0.8022 vs 1.1584 (gap: -0.3562)
  - Dip-return vs no-dip: 0.8685 vs 1.1403 (gap: -0.2718)
  - Spearman(depth_range, residue): -0.0012
  - Spearman(start_depth, residue): -0.2637

**d≤3.0** (194 near-loops/seed):
  - Depth range high vs low: 1.0913 vs 1.0854 (gap: 0.0059)
  - Excursion high vs low: 0.8854 vs 1.2785 (gap: -0.3931)
  - Dip-return vs no-dip: 0.9568 vs 1.2126 (gap: -0.2558)
  - Spearman(depth_range, residue): 0.0114
  - Spearman(start_depth, residue): -0.2865

### Penrose_N24

**d≤1.0** (21 near-loops/seed):
  - Depth range high vs low: 0.5170 vs 0.5663 (gap: -0.0493)
  - Excursion high vs low: 0.3883 vs 0.6958 (gap: -0.3074)
  - Dip-return vs no-dip: 0.3673 vs 1.1981 (gap: -0.8308)
  - Spearman(depth_range, residue): 0.0226
  - Spearman(start_depth, residue): -0.1563

**d≤2.0** (127 near-loops/seed):
  - Depth range high vs low: 0.9785 vs 1.0503 (gap: -0.0718)
  - Excursion high vs low: 0.7934 vs 1.2635 (gap: -0.4702)
  - Dip-return vs no-dip: 0.8831 vs 1.2138 (gap: -0.3306)
  - Spearman(depth_range, residue): -0.0287
  - Spearman(start_depth, residue): -0.3047

**d≤3.0** (169 near-loops/seed):
  - Depth range high vs low: 1.1654 vs 1.2109 (gap: -0.0455)
  - Excursion high vs low: 0.9165 vs 1.4990 (gap: -0.5825)
  - Dip-return vs no-dip: 1.0095 vs 1.3876 (gap: -0.3781)
  - Spearman(depth_range, residue): -0.0125
  - Spearman(start_depth, residue): -0.3640

## Interpretation rules

- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.
- This tests whether path-level depth traversal predicts address residue
  beyond what starting depth alone explains.
- If depth_range/excursion adds predictive power beyond start_depth,
  that supports 'curvature encountered along path' as the mechanism.
- If start_depth dominates and path metrics add nothing, the effect is
  positional rather than path-dependent.

## Figures

1. fig_1_*.png — Residue by depth range traversed (KEY)
2. fig_2_*.png — Residue by depth excursion
3. fig_3_*.png — Residue by cumulative depth change
4. fig_4_*.png — Dip-and-return vs non-dipping walkers
5. fig_5_*.png — Spearman correlations summary
6. fig_6_*.png — Scatter: depth range vs residue
7. fig_7_*.png — Real vs shuffled depth-range effect
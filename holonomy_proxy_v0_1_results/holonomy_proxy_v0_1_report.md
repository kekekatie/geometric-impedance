# Holonomy proxy v0.1: near-loop address residue

## Setup
- Seeds: 10
- Walkers per seed: 20000
- Max steps: 1024
- Near-return thresholds: [1.0, 2.0, 3.0]
- Interior fraction: 0.75
- Shuffled control walkers: 5000

## Core question
When a path nearly closes in physical space, how much perpendicular/address 
displacement remains? Does this scale with loop area? Is it depth-dependent? 
Does Penrose show a stronger effect than AB?

## Summary (real, mean across seeds)

| substrate   |   threshold |   n_near_loops_mean |   mean_perp_residue |   median_perp_residue |   std_perp_residue |   mean_loop_area |   spearman_area_vs_residue |   spearman_area_vs_residue_p |   spearman_start_depth_vs_residue |   spearman_min_depth_vs_residue |   mean_residue_deep_start |   mean_residue_shallow_start |   mean_residue_visited_shallow |   mean_residue_not_visited_shallow |
|:------------|------------:|--------------------:|--------------------:|----------------------:|-------------------:|-----------------:|---------------------------:|-----------------------------:|----------------------------------:|--------------------------------:|--------------------------:|-----------------------------:|-------------------------------:|-----------------------------------:|
| AB_N30      |           1 |                23.9 |            0.777312 |              0.739104 |           0.871838 |         112.411  |                -0.0468098  |                     0.397978 |                         -0.300441 |                      0.0437466  |                  0.592697 |                     0.965875 |                       0.777312 |                                nan |
| AB_N30      |           2 |               130.8 |            0.997701 |              0.765367 |           0.532052 |         106.914  |                 0.00593358 |                     0.446221 |                         -0.263717 |                     -0.0159454  |                  0.880114 |                     1.11548  |                       0.997701 |                                nan |
| AB_N30      |           3 |               193.6 |            1.0837   |              1.08239  |           0.506355 |         105.119  |                 0.0061228  |                     0.362518 |                         -0.286512 |                     -0.0182744  |                  0.955469 |                     1.2127   |                       1.0837   |                                nan |
| Penrose_N24 |           1 |                21.3 |            0.614104 |              0        |           0.774061 |          98.4414 |                 0.002553   |                     0.58999  |                         -0.156326 |                     -0.0582828  |                  0.504206 |                     0.726399 |                       0.614104 |                                nan |
| Penrose_N24 |           2 |               127.2 |            1.03129  |              1.17557  |           0.555876 |          99.6783 |                -0.0109075  |                     0.380078 |                         -0.304706 |                      0.0164042  |                  0.885501 |                     1.17787  |                       1.03129  |                                nan |
| Penrose_N24 |           3 |               168.7 |            1.18947  |              1.17557  |           0.605067 |          99.9737 |                 0.00528955 |                     0.313408 |                         -0.364049 |                     -0.00412563 |                  0.984944 |                     1.39565  |                       1.18947  |                                nan |

## Shuffled control summary

| substrate   |   threshold |   n_near_loops_mean |   mean_perp_residue |   median_perp_residue |
|:------------|------------:|--------------------:|--------------------:|----------------------:|
| AB_N30      |           1 |                 8.1 |            0.527849 |              0.359968 |
| AB_N30      |           2 |                33.5 |            0.978998 |              0.981382 |
| AB_N30      |           3 |                49.6 |            1.03683  |              1.00854  |
| Penrose_N24 |           1 |                 5.1 |            0.484425 |              0.139015 |
| Penrose_N24 |           2 |                30.9 |            1.04738  |              1.04192  |
| Penrose_N24 |           3 |                40.6 |            1.08129  |              1.08534  |

## Key comparisons

### Threshold d ≤ 1.0
- AB real: 0.7773, Penrose real: 0.6141
- AB shuffled: 0.5278, Penrose shuffled: 0.4844
- AB area-residue Spearman: -0.0468, Penrose: 0.0026
- AB deep vs shallow start: 0.5927 vs 0.9659
- Penrose deep vs shallow start: 0.5042 vs 0.7264

### Threshold d ≤ 2.0
- AB real: 0.9977, Penrose real: 1.0313
- AB shuffled: 0.9790, Penrose shuffled: 1.0474
- AB area-residue Spearman: 0.0059, Penrose: -0.0109
- AB deep vs shallow start: 0.8801 vs 1.1155
- Penrose deep vs shallow start: 0.8855 vs 1.1779

### Threshold d ≤ 3.0
- AB real: 1.0837, Penrose real: 1.1895
- AB shuffled: 1.0368, Penrose shuffled: 1.0813
- AB area-residue Spearman: 0.0061, Penrose: 0.0053
- AB deep vs shallow start: 0.9555 vs 1.2127
- Penrose deep vs shallow start: 0.9849 vs 1.3956

## Interpretation rules

- This is NOT Berry curvature.
- This does NOT prove quantum holonomy.
- This does NOT chase alpha~0.553.
- This is a classical discrete holonomy proxy: physical near-closure with hidden/address non-closure.
- If shuffled control destroys the signal: strong evidence the effect depends on actual perpendicular-space geometry.
- If the signal remains after shuffling: probably a graph/random-walk artifact, not geometric holonomy.

## Figures

1. fig_1_residue_by_substrate.png — AB vs Penrose near-loop perpendicular residue
2. fig_2_residue_by_start_depth.png — residue by start-depth group
3. fig_3_residue_by_shallow_exposure.png — residue by min-depth-visited group
4. fig_4_residue_vs_area.png — residue vs loop-area proxy
5. fig_5_real_vs_shuffled.png — real vs shuffled control
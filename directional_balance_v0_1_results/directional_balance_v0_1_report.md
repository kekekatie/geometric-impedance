# Perp-space directional balance v0.1

## Core question
The landscape test showed every edge has the same perp-space magnitude.
Does the DIRECTION of perp-space edges vary with depth? Do deep vertices
have more balanced directional options (explaining the walk cancellation effect)?

## Setup
- No walks for the main analysis (pure geometry)
- Walk validation: 5 seeds, 10000 walkers/seed, 1024 steps
- Interior vertices only (75th percentile)
- Depth bins: 50

## Directional balance metrics
- **Resultant magnitude**: |mean of unit direction vectors to neighbours|.
  0 = perfectly balanced (vectors cancel), 1 = all point same way
- **Net drift**: |mean of raw perp displacement vectors|.
  Expected perp-space displacement per random step from this vertex
- **Direction spread**: circular std of edge angles in perp-space

## Summary

| substrate   |   n_interior |   spearman_depth_vs_resultant |   spearman_depth_vs_drift |   spearman_depth_vs_spread |   mean_resultant_shallow |   mean_resultant_mid |   mean_resultant_deep |   mean_drift_shallow |   mean_drift_mid |   mean_drift_deep |
|:------------|-------------:|------------------------------:|--------------------------:|---------------------------:|-------------------------:|---------------------:|----------------------:|---------------------:|-----------------:|------------------:|
| AB_N30      |        16999 |                     -0.721217 |                 -0.721711 |                   0.703911 |                 0.779797 |             0.656012 |              0.202675 |             0.779797 |         0.656012 |          0.202675 |
| Penrose_N24 |        21539 |                     -0.781034 |                 -0.782608 |                   0.779149 |                 0.826358 |             0.667092 |              0.102585 |             0.826358 |         0.667092 |          0.102585 |

## Walk validation: predictor horse race

| substrate   |   threshold |   seed |   n_near_loops |   spearman_depth_vs_residue |   spearman_resultant_vs_residue |   spearman_drift_vs_residue |   spearman_spread_vs_residue |
|:------------|------------:|-------:|---------------:|----------------------------:|--------------------------------:|----------------------------:|-----------------------------:|
| AB_N30      |           2 |      2 |           65.8 |                   -0.295813 |                        0.342422 |                    0.332042 |                    -0.338414 |
| AB_N30      |           3 |      2 |           95   |                   -0.350065 |                        0.35402  |                    0.341401 |                    -0.350406 |
| Penrose_N24 |           2 |      2 |           63.2 |                   -0.422829 |                        0.354113 |                    0.342285 |                    -0.354707 |
| Penrose_N24 |           3 |      2 |           87.6 |                   -0.417087 |                        0.380595 |                    0.368891 |                    -0.381025 |

## Key results

### AB_N30

  - Spearman(depth, resultant) = -0.7212
  - Spearman(depth, net_drift) = -0.7217
  - Shallow resultant: 0.779797
  - Mid resultant: 0.656012
  - Deep resultant: 0.202675
  - Shallow drift: 0.779797
  - Deep drift: 0.202675

### Penrose_N24

  - Spearman(depth, resultant) = -0.7810
  - Spearman(depth, net_drift) = -0.7826
  - Shallow resultant: 0.826358
  - Mid resultant: 0.667092
  - Deep resultant: 0.102585
  - Shallow drift: 0.826358
  - Deep drift: 0.102585

## Interpretation

- If resultant decreases with depth: deep vertices have more balanced
  perp-space directions → walks from depth cancel more → less residue
- If resultant is flat: directional balance doesn't explain the depth effect
- Horse race: if balance/drift predicts walk residue better than depth,
  it's the more fundamental variable

## Figures

1. fig_1 — Depth vs directional balance (THE KEY)
2. fig_2 — Depth vs net drift
3. fig_3 — Density plot: depth vs balance
4. fig_4 — HORSE RACE: which predicts walk residue best?
5. fig_5 — Drift vectors in perp-space, coloured by depth
6. fig_6 — Substrate comparison
7. fig_7 — Degree control
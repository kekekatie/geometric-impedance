# Constraint-aware walk scout v0.1

First small check of the Gemini proposal: ordinary graph walks are replaced by depth-aware walks using perpendicular-window hull-depth as a constraint.

This is a scout, not a full validation. It uses one seed per substrate, 1,200 walkers, and depths from the existing AB_N30/Penrose_N24 lift files.

## Models
- `baseline_uniform`: ordinary nearest-neighbour random walk.
- `bias_beta_*`: transition probabilities favour inward/deeper hidden-window moves: P(i→j) ∝ exp(beta × (depth_j - depth_i)).
- `cost_lambda_*`: neighbour choice is uniform, but outward/depth-losing moves have extra waiting-time cost: τ = exp(lambda × max(0, depth_i - depth_j)).

## Summary
| substrate   | model            | x_type    |   alpha_phys_msd_64_to_1024 |   alpha_r2 |    late_x |   late_msd_phys |   late_mean_perp_mismatch |   late_near_return_frac |   late_near_return_mean_perp_mismatch |   late_near_return_n |
|:------------|:-----------------|:----------|----------------------------:|-----------:|----------:|----------------:|--------------------------:|------------------------:|--------------------------------------:|---------------------:|
| AB_N30      | baseline_uniform | steps     |                      0.9579 |     0.9997 | 1024.0000 |        830.0169 |                    1.1189 |                  0.0092 |                                0.7442 |                   11 |
| AB_N30      | bias_beta_10     | steps     |                      0.9326 |     1.0000 | 1024.0000 |        297.6752 |                    0.9673 |                  0.0175 |                                0.9350 |                   21 |
| AB_N30      | bias_beta_5      | steps     |                      0.9490 |     1.0000 | 1024.0000 |        616.2954 |                    0.9881 |                  0.0125 |                                0.8874 |                   15 |
| AB_N30      | cost_lambda_10   | cost_time |                      0.4452 |     0.9907 | 1024.0000 |         13.4256 |                    1.2824 |                  0.3667 |                                1.2927 |                  440 |
| AB_N30      | cost_lambda_5    | cost_time |                      0.8918 |     0.9987 | 1024.0000 |        146.5709 |                    1.2038 |                  0.0300 |                                1.3650 |                   36 |
| Penrose_N24 | baseline_uniform | steps     |                      0.9625 |     0.9993 | 1024.0000 |        833.2395 |                    1.1643 |                  0.0067 |                              nan      |                    8 |
| Penrose_N24 | bias_beta_10     | steps     |                      0.9469 |     0.9999 | 1024.0000 |        360.9888 |                    0.9836 |                  0.0150 |                                1.0106 |                   18 |
| Penrose_N24 | bias_beta_5      | steps     |                      0.9842 |     1.0000 | 1024.0000 |        689.6288 |                    1.0286 |                  0.0058 |                              nan      |                    7 |
| Penrose_N24 | cost_lambda_10   | cost_time |                      0.5602 |     0.9695 | 1024.0000 |         21.2973 |                    1.4045 |                  0.2183 |                                1.2984 |                  262 |
| Penrose_N24 | cost_lambda_5    | cost_time |                      0.9555 |     0.9996 | 1024.0000 |        213.2909 |                    1.2995 |                  0.0158 |                                1.1022 |                   19 |

## First read
- **AB_N30:** baseline α≈0.958; strongest inward-bias α≈0.933; strongest cost-time α≈0.445.
- **Penrose_N24:** baseline α≈0.962; strongest inward-bias α≈0.947; strongest cost-time α≈0.560.

## Interpretation
This first scout asks whether a simple depth-aware constraint can pull the physical diffusion exponent away from normal diffusion toward α≈0.553. A negative result would not kill the depth/holonomy branch; it would only say this simple classical resistance model is not enough.
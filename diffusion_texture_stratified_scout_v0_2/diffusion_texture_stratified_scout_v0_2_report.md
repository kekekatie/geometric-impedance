# Diffusion–texture stratified scout v0.2

A first stratified classical random-walk scout. It asks whether local perpendicular-space texture/depth affects physical spreading and address-space residue over many paths.

**Important:** this is not Berry curvature, not a quantum walk, and not a test of α≈0.553. It is a classical baseline for whether texture-rich regions produce larger address mismatch in ordinary graph walks.

## Setup
- Substrates: AB_N30 and Penrose_N24 full-lift graphs.
- Candidate starts: interior 75% by physical radius, then stratified by top/bottom quartiles of texture and hull-depth.
- Walks: 2,200 per group per substrate, up to 512 steps.
- Measured: physical MSD exponent, near-return address mismatch, address tortuosity, and start-metric correlations.

## Summary
| substrate   | group            |   candidate_count |   walkers |   alpha_phys_msd |   alpha_phys_r2 |   near_return_frac_t512 |   near_return_n_t512 |   near_return_mean_perp_mismatch_t512 |   median_perp_tortuosity_t512 |   p90_perp_tortuosity_t512 |   start_texture_mean |   start_depth_mean |   spearman_texture_vs_final_perp_mismatch |   spearman_depth_vs_final_perp_mismatch |
|:------------|:-----------------|------------------:|----------:|-----------------:|----------------:|------------------------:|---------------------:|--------------------------------------:|------------------------------:|---------------------------:|---------------------:|-------------------:|------------------------------------------:|----------------------------------------:|
| AB_N30      | all_interior75   |             16997 |      2200 |           0.9779 |          0.9996 |                  0.0109 |                   24 |                                0.9942 |                      471.8363 |                  1218.2760 |              -0.0065 |             0.3282 |                                    0.1940 |                                 -0.2924 |
| AB_N30      | depth_high_q25   |              4254 |      2200 |           0.9726 |          0.9994 |                  0.0091 |                   20 |                                0.7096 |                      632.7442 |                  1492.0773 |              -0.5942 |             0.6661 |                                    0.0292 |                                 -0.1010 |
| AB_N30      | depth_low_q25    |              4269 |      2200 |           0.9773 |          0.9998 |                  0.0077 |                   17 |                                1.4632 |                      388.6008 |                   874.1952 |               1.3475 |             0.0635 |                                   -0.0138 |                                 -0.0559 |
| AB_N30      | texture_high_q25 |              4251 |      2200 |           0.9728 |          0.9996 |                  0.0155 |                   34 |                                1.0455 |                      401.6057 |                   894.9183 |               1.4440 |             0.0872 |                                    0.0528 |                                 -0.0788 |
| AB_N30      | texture_low_q25  |              4250 |      2200 |           0.9798 |          0.9995 |                  0.0123 |                   27 |                                0.8929 |                      564.9671 |                  1393.5239 |              -0.7378 |             0.4790 |                                   -0.0115 |                                 -0.2313 |
| Penrose_N24 | all_interior75   |             21539 |      2200 |           0.9791 |          0.9996 |                  0.0114 |                   25 |                                0.9949 |                      469.6515 |                  1237.9408 |               0.0301 |             0.4542 |                                    0.2654 |                                 -0.4115 |
| Penrose_N24 | depth_high_q25   |              5385 |      2200 |           0.9943 |          0.9999 |                  0.0136 |                   30 |                                0.8742 |                      598.9732 |                  1492.5945 |              -0.6987 |             0.7452 |                                    0.0051 |                                 -0.1139 |
| Penrose_N24 | depth_low_q25    |              5385 |      2200 |           0.9908 |          0.9996 |                  0.0105 |                   23 |                                1.2094 |                      353.1172 |                   795.2684 |               1.1707 |             0.1656 |                                   -0.0394 |                                 -0.0843 |
| Penrose_N24 | texture_high_q25 |              5385 |      2200 |           0.9744 |          1.0000 |                  0.0100 |                   22 |                                1.0937 |                      380.0803 |                   867.0368 |               1.4580 |             0.2513 |                                    0.1582 |                                 -0.2905 |
| Penrose_N24 | texture_low_q25  |              5385 |      2200 |           0.9780 |          0.9999 |                  0.0123 |                   27 |                                0.8674 |                      535.8582 |                  1299.5807 |              -0.8890 |             0.6016 |                                    0.1560 |                                 -0.2920 |

## First read
- **AB_N30 texture split:** high-texture starts have near-return address mismatch 1.045; low-texture starts have 0.893. Physical diffusion exponents are 0.973 vs 0.980.
- **AB_N30 depth split:** deep-window starts have near-return address mismatch 0.710; shallow-window starts have 1.463.
- **Penrose_N24 texture split:** high-texture starts have near-return address mismatch 1.094; low-texture starts have 0.867. Physical diffusion exponents are 0.974 vs 0.978.
- **Penrose_N24 depth split:** deep-window starts have near-return address mismatch 0.874; shallow-window starts have 1.209.

## Interpretation
The ordinary graph walk remains close to normal diffusion in physical space across all groups, so this branch still does not show the proposed α≈0.553. The relevant scout question is narrower: does local hidden texture/depth change the address residue left by paths that nearly close in physical space?

A promising signal would be a stable Penrose high-texture > low-texture mismatch gap, especially if larger than AB's corresponding gap. A null or inconsistent signal would keep the diffusion branch as a side note rather than a trunk result.

## Next
If this contrast looks promising, the next run should be a Claude Code / external-compute version with more walkers, multiple seeds, and a stricter near-return analysis by time window.
# Controlled linger walks v0.1

## Core question
Does forced time at depth CAUSE address recovery, or is the correlation
from natural walks confounded by starting depth?

## Setup
- Seeds: 10, Walkers/seed: 5000
- Start depth band: 0.35–0.65
- Disturb phase: 100 free random walk steps
- Descend phase: 100 biased-toward-deep steps
- Linger durations tested: [0, 5, 10, 20, 40, 80, 160]
- Ascend phase: 200 biased-toward-shallow steps
- Bias: 70% pick deepest/shallowest neighbour, 30% random

## Summary (mean across seeds)

| substrate   |   linger_n |   seed |   n_walkers |   mean_start_depth |   mean_disturb_depth |   mean_descend_depth |   mean_linger_end_depth |   mean_ascend_depth |   mean_residue_after_disturb |   mean_residue_after_descend |   mean_residue_linger_start |   mean_residue_linger_end |   mean_residue_after_ascend |   median_residue_after_ascend |   std_residue_after_ascend |   mean_phys_dist_final |   frac_near_return_2 |   frac_near_return_3 |
|:------------|-----------:|-------:|------------:|-------------------:|---------------------:|---------------------:|------------------------:|--------------------:|-----------------------------:|-----------------------------:|----------------------------:|--------------------------:|----------------------------:|------------------------------:|---------------------------:|-----------------------:|---------------------:|---------------------:|
| AB_N30      |          0 |    4.5 |        5000 |           0.485139 |             0.480849 |             0.607798 |                0.607798 |            0.266055 |                      1.03058 |                     0.922192 |                    0.922192 |                  0.922192 |                     1.25393 |                       1.27161 |                   0.540489 |                12.1449 |              0.02832 |              0.04154 |
| AB_N30      |          5 |    4.5 |        5000 |           0.485139 |             0.480031 |             0.60945  |                0.607018 |            0.265347 |                      1.03082 |                     0.920135 |                    0.920135 |                  0.92064  |                     1.2551  |                       1.26429 |                   0.540825 |                12.2144 |              0.02136 |              0.04826 |
| AB_N30      |         10 |    4.5 |        5000 |           0.485139 |             0.480224 |             0.607349 |                0.608355 |            0.266297 |                      1.03    |                     0.923726 |                    0.923726 |                  0.919046 |                     1.25149 |                       1.25757 |                   0.539515 |                12.3563 |              0.0276  |              0.04102 |
| AB_N30      |         20 |    4.5 |        5000 |           0.485139 |             0.481599 |             0.609593 |                0.608886 |            0.266748 |                      1.0276  |                     0.918869 |                    0.918869 |                  0.923177 |                     1.25263 |                       1.2663  |                   0.541673 |                12.2917 |              0.02772 |              0.0409  |
| AB_N30      |         40 |    4.5 |        5000 |           0.485139 |             0.482992 |             0.60756  |                0.607425 |            0.264244 |                      1.02729 |                     0.921867 |                    0.921867 |                  0.919913 |                     1.25534 |                       1.26789 |                   0.538356 |                12.5051 |              0.02718 |              0.04102 |
| AB_N30      |         80 |    4.5 |        5000 |           0.485139 |             0.482416 |             0.60818  |                0.608385 |            0.267508 |                      1.02704 |                     0.918834 |                    0.918834 |                  0.922005 |                     1.25209 |                       1.26139 |                   0.540343 |                12.7485 |              0.02722 |              0.03962 |
| AB_N30      |        160 |    4.5 |        5000 |           0.485139 |             0.481004 |             0.609415 |                0.608631 |            0.264074 |                      1.03305 |                     0.920774 |                    0.920774 |                  0.92037  |                     1.25592 |                       1.27051 |                   0.541795 |                13.339  |              0.02456 |              0.03652 |
| Penrose_N24 |          0 |    4.5 |        5000 |           0.506821 |             0.534228 |             0.656019 |                0.656019 |            0.320842 |                      1.09929 |                     0.991662 |                    0.991662 |                  0.991662 |                     1.34033 |                       1.34349 |                   0.591445 |                12.2768 |              0.02814 |              0.03784 |
| Penrose_N24 |          5 |    4.5 |        5000 |           0.506821 |             0.533374 |             0.655477 |                0.654976 |            0.320792 |                      1.09878 |                     0.98808  |                    0.98808  |                  0.986515 |                     1.33466 |                       1.32697 |                   0.591111 |                12.3016 |              0.0178  |              0.05056 |
| Penrose_N24 |         10 |    4.5 |        5000 |           0.506821 |             0.532822 |             0.655263 |                0.656033 |            0.320843 |                      1.10085 |                     0.991613 |                    0.991613 |                  0.988226 |                     1.33507 |                       1.3396  |                   0.592418 |                12.3974 |              0.02624 |              0.0351  |
| Penrose_N24 |         20 |    4.5 |        5000 |           0.506821 |             0.531981 |             0.656787 |                0.654646 |            0.322058 |                      1.10043 |                     0.989109 |                    0.989109 |                  0.995628 |                     1.33468 |                       1.33368 |                   0.592651 |                12.4738 |              0.02774 |              0.03618 |
| Penrose_N24 |         40 |    4.5 |        5000 |           0.506821 |             0.534692 |             0.656192 |                0.654752 |            0.320964 |                      1.09723 |                     0.986007 |                    0.986007 |                  0.990799 |                     1.33901 |                       1.34072 |                   0.591674 |                12.6834 |              0.02596 |              0.03434 |
| Penrose_N24 |         80 |    4.5 |        5000 |           0.506821 |             0.533327 |             0.656059 |                0.653908 |            0.322318 |                      1.09594 |                     0.992285 |                    0.992285 |                  0.990798 |                     1.33801 |                       1.34556 |                   0.593899 |                13.0166 |              0.02498 |              0.03368 |
| Penrose_N24 |        160 |    4.5 |        5000 |           0.506821 |             0.533808 |             0.6575   |                0.656322 |            0.319986 |                      1.09376 |                     0.988424 |                    0.988424 |                  0.988526 |                     1.33782 |                       1.33797 |                   0.593483 |                13.6438 |              0.0224  |              0.02972 |

## Key results

### AB_N30

  - Linger   0: final residue = 1.2539 (linger start: 0.9222, linger end: 0.9222)
  - Linger   5: final residue = 1.2551 (linger start: 0.9201, linger end: 0.9206)
  - Linger  10: final residue = 1.2515 (linger start: 0.9237, linger end: 0.9190)
  - Linger  20: final residue = 1.2526 (linger start: 0.9189, linger end: 0.9232)
  - Linger  40: final residue = 1.2553 (linger start: 0.9219, linger end: 0.9199)
  - Linger  80: final residue = 1.2521 (linger start: 0.9188, linger end: 0.9220)
  - Linger 160: final residue = 1.2559 (linger start: 0.9208, linger end: 0.9204)

  No-linger baseline: 1.2539
  Best recovery (linger=10): 1.2515
  Improvement: 0.0024

### Penrose_N24

  - Linger   0: final residue = 1.3403 (linger start: 0.9917, linger end: 0.9917)
  - Linger   5: final residue = 1.3347 (linger start: 0.9881, linger end: 0.9865)
  - Linger  10: final residue = 1.3351 (linger start: 0.9916, linger end: 0.9882)
  - Linger  20: final residue = 1.3347 (linger start: 0.9891, linger end: 0.9956)
  - Linger  40: final residue = 1.3390 (linger start: 0.9860, linger end: 0.9908)
  - Linger  80: final residue = 1.3380 (linger start: 0.9923, linger end: 0.9908)
  - Linger 160: final residue = 1.3378 (linger start: 0.9884, linger end: 0.9885)

  No-linger baseline: 1.3403
  Best recovery (linger=5): 1.3347
  Improvement: 0.0057

## Interpretation rules

- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.
- This is a CONTROLLED EXPERIMENT: start depth is fixed, disturbance
  is standardised, the ONLY variable is linger duration.
- If linger duration predicts final residue: TIME AT DEPTH directly
  causes address recovery. The confound is ruled out.
- If linger duration doesn't matter: the natural-walk correlation was
  entirely due to starting depth, not lingering.

## Figures

1. fig_1 — CONTROLLED residue vs linger duration (THE KEY FIGURE)
2. fig_2 — Phase-by-phase residue through the walk
3. fig_3 — Hull depth through each phase (sanity check)
4. fig_4 — Substrate comparison: controlled S-curves overlaid
5. fig_5 — Residue trajectory during the linger phase itself
6. fig_6 — Fraction of disturbance recovered vs linger duration
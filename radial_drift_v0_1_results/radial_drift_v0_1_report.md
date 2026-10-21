# Radial drift alignment v0.1

## Core question
The directional balance test showed shallow vertices have biased drift
vectors. Does that bias point RADIALLY OUTWARD toward the hull boundary?
If so, the arrow-of-time gets its orientation: boundary-ward.

Also: is there chirality (handedness) in the Penrose drift structure?

## Setup
- Pure geometry, no walks
- Interior vertices only (75th percentile)
- Alignment angle: angle between vertex's perp-space position vector
  (from hull centroid) and its drift vector (mean displacement to neighbours)
- 0° = perfect radial outward, ±180° = radial inward
- Radial drift: projection of drift onto radial direction (positive = outward)
- Tangential drift: perpendicular component (signed → chirality test)

## Summary

| substrate   |   n_drifters |   frac_outward_all |   frac_outward_shallow |   frac_outward_deep |   mean_radial_shallow |   mean_radial_deep |   mean_tangential_all |   mean_tangential_shallow |   mean_tangential_deep |   spearman_depth_vs_radial |   spearman_depth_vs_abs_tangential |
|:------------|-------------:|-------------------:|-----------------------:|--------------------:|----------------------:|-------------------:|----------------------:|--------------------------:|-----------------------:|---------------------------:|-----------------------------------:|
| AB_N30      |        16500 |        6.06061e-05 |                      0 |         0.000594177 |             -0.752687 |          -0.34735  |           0.000131837 |               0.000228635 |            0.000884284 |                   0.727986 |                          -0.104067 |
| Penrose_N24 |        20450 |        0.00425428  |                      0 |         0.0283361   |             -0.776918 |          -0.251162 |          -5.97068e-05 |               0.000614956 |           -8.01891e-05 |                   0.758363 |                          -0.476611 |

## Key results

### AB_N30

  - Fraction outward (all drifters): 0.0%
  - Fraction outward (shallow <0.3): 0.0%
  - Fraction outward (deep >0.7): 0.1%
  - Mean radial drift (shallow): -0.752687
  - Mean radial drift (deep): -0.347350
  - Mean tangential (all): 0.000132
  - Spearman(depth, radial_drift) = 0.7280

### Penrose_N24

  - Fraction outward (all drifters): 0.4%
  - Fraction outward (shallow <0.3): 0.0%
  - Fraction outward (deep >0.7): 2.8%
  - Mean radial drift (shallow): -0.776918
  - Mean radial drift (deep): -0.251162
  - Mean tangential (all): -0.000060
  - Spearman(depth, radial_drift) = 0.7584

## Interpretation

- If shallow vertices point outward: the drift has a radial orientation
  → 'boundary-ward' arrow → time/decay concentrated at the edge
- If tangential drift is nonzero: chirality → handedness → reflection symmetry broken
- If both: the drift is a spiral (outward with rotation)

## Figures

1. fig_1 — THE ALIGNMENT TEST: angle distribution (KEY)
2. fig_2 — Fraction outward by depth
3. fig_3 — Radial vs tangential drift by depth
4. fig_4 — Angle vs depth density
5. fig_5 — CHIRALITY TEST: tangential drift
6. fig_6 — Polar histogram (shallow only)
7. fig_7 — Substrate comparison
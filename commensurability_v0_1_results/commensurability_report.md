# Commensurability Analysis v0.1

## Question
AB's z=8 vertices sit on an 8-fold symmetry grid — their coordination
is commensurate with the projection symmetry. Penrose's z=7 vertices
sit on a 5-fold grid — 7 and 5 are coprime, so they're incommensurate.
How much does this matter for angular regularity and directional balance?

## Method
For each vertex type in both substrates:
1. Compute angular spacings between consecutive perp-space neighbours
2. Compare to ideal regular z-gon (360/z spacing)
3. Compare to projection symmetry grid (multiples of pi/n)
4. Quantify deviation from both references

## Type-level summary

| substrate   |   degree |   count | commensurate   |   mean_abs_dev_from_regular |   std_spacing |   regularity |   mean_snap_to_grid |   max_snap_to_grid |
|:------------|---------:|--------:|:---------------|----------------------------:|--------------:|-------------:|--------------------:|-------------------:|
| AB          |        8 |     499 | YES            |                 9.33694e-10 |   1.32044e-09 |     1        |         4.66851e-10 |        1.8674e-09  |
| AB          |        7 |     207 | NO             |                11.0204      |  15.7467      |     0.693814 |         5.31246e-10 |        1.91807e-09 |
| AB          |        6 |    1004 | NO             |                24.9851      |  33.5042      |     0.441597 |         4.75495e-10 |        1.87641e-09 |
| AB          |        5 |    2395 | NO             |                43.1865      |  53.9775      |     0.250313 |         4.42531e-10 |        1.67132e-09 |
| AB          |        4 |    5840 | YES            |                67.4884      |  77.9306      |     0.134105 |         4.82845e-10 |        1.50125e-09 |
| AB          |        3 |    7047 | NO             |                99.9957      | 106.062       |     0.116152 |         5.0727e-10  |        1.29126e-09 |
| AB          |        2 |       7 | YES            |               135           | 135           |     0.25     |         5.78782e-10 |        1.15756e-09 |
| Penrose     |        7 |    1105 | NO             |                17.6327      |  17.8154      |     0.65359  |         1.36272e-09 |        3.00078e-09 |
| Penrose     |        6 |     706 | NO             |                16.0453      |  17.0264      |     0.716226 |         1.40607e-09 |        3.01013e-09 |
| Penrose     |        5 |    5477 | YES            |                45.3848      |  56.8164      |     0.210883 |         1.33883e-09 |        2.82972e-09 |
| Penrose     |        4 |    2904 | NO             |                39.4959      |  45.8916      |     0.490093 |         1.35053e-09 |        2.68108e-09 |
| Penrose     |        3 |   11175 | NO             |                98.1963      | 104.176       |     0.131863 |         1.31782e-09 |        2.34175e-09 |
| Penrose     |        2 |     172 | YES            |               109.674       | 109.674       |     0.390698 |         1.17736e-09 |        1.8957e-09  |


## Figures

1. fig_1 — Commensurability comparison (3-panel: deviation, snap, regularity)
2. fig_2 — Top-z regularity distributions
3. fig_3 — Grid snap distributions
4. fig_4 — Example vertices: actual angles vs symmetry grid (polar)
5. fig_5 — Grid commensurability vs angular irregularity (scatter)
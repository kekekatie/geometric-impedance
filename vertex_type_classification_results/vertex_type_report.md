# Vertex-Type Classification v0.1

## Connection to Jagannathan 2024

Jagannathan showed the AB acceptance window subdivides into domains
by vertex type, with coordination z=8 (centre, type A) to z=3
(boundary, type F). We classify our 22,663 AB vertices by degree
and test whether our directional balance gradient maps onto these types.

## Type-level summary

| vertex_type   |   count |   mean_degree |   mean_depth |   std_depth |   mean_balance |   std_balance |   mean_drift |   mean_perp_dist |
|:--------------|--------:|--------------:|-------------:|------------:|---------------:|--------------:|-------------:|-----------------:|
| A             |     499 |             8 |     0.852523 |   0.0647824 |     6.1247e-12 |   6.74967e-12 |  1.22494e-11 |         0.218291 |
| B             |     207 |             7 |     0.811005 |   0.0824501 |     0.142857   |   8.0516e-12  |  0.142857    |         0.279746 |
| C             |    1004 |             6 |     0.746502 |   0.0962689 |     0.307421   |   0.0098513   |  0.307421    |         0.37522  |
| D             |    2395 |             5 |     0.645831 |   0.103369  |     0.482611   |   0.00699381  |  0.482611    |         0.524231 |
| E             |    5840 |             4 |     0.424579 |   0.140942  |     0.653183   |   0.004336    |  0.653183    |         0.851723 |
| F             |    7047 |             3 |     0.279017 |   0.123544  |     0.804706   |   0.00270872  |  0.804706    |         1.06718  |


## Key statistics

- Kruskal-Wallis test (balance differs across types): H=15367.96, p=0.00e+00
- Spearman(type_rank A→F, balance): 0.9510
- Spearman(type_rank A→F, depth): -0.7618
- Monotonic A→F increase in balance: True

## Result

Directional balance increases monotonically from type A (z=8, centre)
to type F (z=3, boundary). The vertex-type classification from the
crystallographic literature maps directly onto our computational finding.
Our continuous depth gradient is the dynamical consequence of the discrete
type structure: each type occupies a depth band, and directional balance
steps up across those bands.

This confirms the prediction from the phason connection handoff:
the microscopic mechanism (directional balance) is the bridge between
Jagannathan's static type classification and our dynamical walk results.

## Figures

1. fig_1 — Acceptance window triptych (type / balance / depth)
2. fig_2 — The step function: type → balance and type → depth
3. fig_3 — Balance distribution violins within each type
4. fig_4 — Depth vs balance scatter, coloured by type
5. fig_5 — Physical-space tiling coloured by type
6. fig_6 — Continuous balance curve with type depth bands overlaid
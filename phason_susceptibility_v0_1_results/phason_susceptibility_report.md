# Phason Susceptibility v0.1 — Boundary Distance Analysis

## Question
Does distance to the acceptance-window boundary predict directional
imbalance better than (or independently of) hull depth?

## Method
1. Fit regular octagon to AB perp-space point cloud
2. For each vertex, compute signed distance to nearest octagonal edge
3. Correlate with directional balance B(v) = |mean of unit perp-space edge vectors|
4. Partial correlation controlling for hull depth
5. Drift direction alignment: does the imbalance vector point toward the nearest edge?

## Key results

- Spearman(boundary_dist, balance) = -0.7601
- Spearman(hull_depth, balance) = -0.7215
- Spearman(type_rank, balance) = 0.9510
- Partial corr(boundary_dist, balance | depth) = -0.3677
- Mean cos(drift, boundary_normal) = 0.0012

## Type-level boundary distance

| vertex_type   |   count |   mean_bd |    std_bd |   mean_balance |   mean_depth |
|:--------------|--------:|----------:|----------:|---------------:|-------------:|
| A             |     499 |  1.15926  | 0.0494454 |     6.1247e-12 |     0.852523 |
| B             |     207 |  1.06921  | 0.0159752 |     0.142857   |     0.811005 |
| C             |    1004 |  0.952782 | 0.0708029 |     0.307421   |     0.746502 |
| D             |    2395 |  0.809665 | 0.08023   |     0.482611   |     0.645831 |
| E             |    5840 |  0.465018 | 0.168825  |     0.653183   |     0.424579 |
| F             |    7047 |  0.272926 | 0.13725   |     0.804706   |     0.279017 |


## Interpretation

Boundary distance and hull depth both predict directional imbalance,
because they measure nearly the same thing: how far a vertex sits from
the edge of the acceptance window. The partial correlation tells us
whether boundary distance adds information beyond depth.

The drift alignment analysis tests whether the imbalance doesn't just
grow near the boundary but actually POINTS toward it — which would be
the geometric mechanism for phason flip susceptibility.

Claim scope: we are testing whether directional balance provides a
microscopic geometric mechanism for known phason susceptibility in
quasicrystal tilings. We are not claiming to discover phasons.

## Figures

1. fig_1 — Boundary distance vs balance (scatter + binned)
2. fig_2 — Three views of the acceptance window
3. fig_3 — Type-level box plots (boundary dist + balance)
4. fig_4 — Drift direction alignment with boundary
5. fig_5 — Predictor comparison (which metric best predicts balance?)
6. fig_6 — Octagon with drift vectors overlaid
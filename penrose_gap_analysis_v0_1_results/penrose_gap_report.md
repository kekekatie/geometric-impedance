# Penrose Vertex-Type & Coordination Gap Analysis v0.1

## Question
Does the coordination-gap mechanism found in AB (imbalance anti-aligned
with gap, gap size predicts balance) also hold for Penrose?

## Penrose type summary

| vertex_type   |   count |   mean_depth |   mean_balance |   mean_gap_deg |
|:--------------|--------:|-------------:|---------------:|---------------:|
| A             |    1105 |     0.739718 |       0.231148 |         72     |
| B             |     706 |     0.795352 |       0.16725  |         72.204 |
| C             |    5477 |     0.562141 |       0.509695 |        185.462 |
| D             |    2904 |     0.622274 |       0.375565 |        168.992 |
| E             |   11175 |     0.401463 |       0.776916 |        267.273 |


## Key statistics

- Monotonic A→E increase in balance: False
- Spearman(type_rank, balance) = 0.6146
- Spearman(type_rank, depth) = -0.5186
- Spearman(max_gap, balance) = 0.9665
- Overall cos(balance, gap) = -0.9478

## Figures

1. fig_1 — Penrose acceptance window triptych
2. fig_2 — Step function (balance and depth by type)
3. fig_3 — Gap alignment histograms
4. fig_4 — Gap size vs balance scatter
5. fig_5 — Polar plots of balance relative to gap
6. fig_6 — CROSS-SUBSTRATE COMPARISON (AB vs Penrose)
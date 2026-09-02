# Coordination Gap Analysis v0.1

## Question
The phason susceptibility analysis showed drift direction is RANDOM
relative to the nearest acceptance-window edge. But is it random
relative to the GAP in the vertex's coordination shell?

A type F vertex (z=3) has 5 'missing' directions compared to type A (z=8).
If the imbalance vector points into the angular sector where neighbours
are absent, it identifies exactly where a phason flip would add a neighbour.

## Method
1. For each vertex, compute angles to all neighbours in perp-space
2. Find the largest angular gap in the coordination shell
3. Compute the gap centre direction
4. Compute the directional imbalance vector (resultant of unit vectors)
5. Measure cos(balance_angle - gap_direction)
   1.0 = points into gap, 0.0 = random, -1.0 = away from gap

## Key results

- Overall mean cos(balance, gap) = -0.9998
- Spearman(max_gap_size, balance_mag) = 0.9821
- Spearman(cos_alignment, balance_mag) = -0.0380

## Figures

1. fig_1 — Cos alignment histograms by type
2. fig_2 — Gap size vs balance magnitude
3. fig_3 — Polar plots: balance direction relative to gap
4. fig_4 — Perp-space map with vectors and alignment
5. fig_5 — Summary: mean alignment by type
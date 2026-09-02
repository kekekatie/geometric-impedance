# Gap-to-Drift v0.1 — Closing the Mechanism Chain

## Purpose
Close the causal chain: coordination gap → directional balance → walk drift.
Previous work showed gap→balance and balance→drift separately.
This script shows gap→drift directly and provides a predictor comparison.

## Predictor comparison

| substrate   | predictor           |   spearman |     p_value |   abs_spearman |
|:------------|:--------------------|-----------:|------------:|---------------:|
| AB          | hull_depth          |  -0.253019 | 1.77384e-12 |       0.253019 |
| AB          | boundary_dist       |  -0.297697 | 6.76899e-17 |       0.297697 |
| AB          | degree              |  -0.282639 | 2.57479e-15 |       0.282639 |
| AB          | max_angular_gap     |   0.294053 | 1.66608e-16 |       0.294053 |
| AB          | directional_balance |   0.283597 | 2.05589e-15 |       0.283597 |
| Penrose     | hull_depth          |  -0.36548  | 1.15215e-22 |       0.36548  |
| Penrose     | boundary_dist       |  -0.360832 | 4.29288e-22 |       0.360832 |
| Penrose     | degree              |  -0.279882 | 1.46753e-13 |       0.279882 |
| Penrose     | max_angular_gap     |   0.33617  | 3.23577e-19 |       0.33617  |
| Penrose     | directional_balance |   0.328821 | 2.0831e-18  |       0.328821 |


## Figures

1. fig_1 — THE CLOSING LINK: gap → residue (hexbin, both substrates)
2. fig_2 — Complete chain: gap → balance → drift (3-panel)
3. fig_3 — Predictor horse race (bar chart)
4. fig_4 — Arrow convention diagram (balanced / boundary / phason flip)
5. fig_5 — Binned gap→residue curves (both substrates overlaid)
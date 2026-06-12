# Null-disc control v0.1

## Core question
Is the inward radial drift just 'bounded shapes have middles'?
Or does the quasicrystal structure add something beyond that?

## Setup
Three models compared:
1. **Real quasicrystal**: actual tiling with real perp-space coordinates
2. **Null disc**: random uniform points in same hull shape, Delaunay-connected
3. **Shuffled perp**: same tiling graph, perp coordinates randomly permuted
- 5 seeds each for null and shuffled

## Key results

### AB_N30

  - Real Spearman(depth, radial): 0.7280
  - Null disc Spearman (mean): 0.0520 (range: 0.0466–0.0556)
  - Shuffled Spearman (mean): 0.6141 (range: 0.6092–0.6167)

### Penrose_N24

  - Real Spearman(depth, radial): 0.7584
  - Null disc Spearman (mean): 0.0460 (range: 0.0434–0.0502)
  - Shuffled Spearman (mean): 0.7113 (range: 0.7074–0.7146)

## Interpretation

- If real ≈ null disc: drift is trivial boundary bookkeeping
- If real ≠ null disc: quasicrystal structure adds genuine signal
- Shuffled perp tests whether the structured arrangement of perp
  coordinates matters beyond the graph topology

## Figures

1. fig_1 — THE KEY: Real vs null disc vs shuffled (overlaid)
2. fig_2 — Residual: real minus null (what's left after subtracting boundary effect)
3. fig_3 — Spearman comparison bar chart
4. fig_4 — Drift magnitude comparison
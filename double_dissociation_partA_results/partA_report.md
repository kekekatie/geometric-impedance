# Double-Dissociation Part A: Seed-Level Variance


## Null Disc

| Substrate | Native | Mean | Std | Min | Max | Retention |
|-----------|--------|------|-----|-----|-----|-----------|
| AB | 0.7280 | 0.0520 | 0.0030 | 0.0466 | 0.0556 | 7.1% |
| Penrose | 0.7584 | 0.0460 | 0.0023 | 0.0434 | 0.0502 | 6.1% |

**Separation:** Mann–Whitney U = 24, p = 0.0159. Ranges: **OVERLAP**.

## Shuffled Perp

| Substrate | Native | Mean | Std | Min | Max | Retention |
|-----------|--------|------|-----|-----|-----|-----------|
| AB | 0.7280 | 0.6156 | 0.0041 | 0.6092 | 0.6256 | 84.6% |
| Penrose | 0.7584 | 0.7120 | 0.0030 | 0.7074 | 0.7173 | 93.9% |

**Separation:** Mann–Whitney U = 0, p = 0.0002. Ranges: **SEPARATED**.

AB retains 84.6% of native signal under shuffle.
Penrose retains 93.9% of native signal under shuffle.
Asymmetry: Penrose retains 9.3 percentage points MORE than AB.

**The AB-vs-Penrose shuffle asymmetry SURVIVES seed variation.** Ranges do not overlap.

## Kill-condition checks

1. **Null seeds cluster tightly near 0?** AB null std = 0.0030, Penrose null std = 0.0023. YES — tight cluster.
2. **AB-shuffle and Penrose-shuffle separate?** AB range [0.6092–0.6256], Penrose range [0.7074–0.7173]. YES — clean separation.
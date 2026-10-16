# Double-Dissociation Part B: Unified 2×2 Table

## Protocol
- Interior 75% subset, 10 replicates per perturbation
- Rewire: 5E degree-preserving edge swaps
- Shuffle: random permutation of perp-space coordinates
- Metric: cross-validated logistic regression AUC (identity persistence)
- Same ruler for all four cells

## 2×2 Table (Hybrid AUC)

|                | Native | Rewire | Shuffle |
|----------------|--------|--------|---------|
| **AB** | 0.9989 | 0.9904 | 0.9985 |
| **Penrose** | 0.9116 | 0.8536 | 0.9083 |

## Deltas from Native

|                | Rewire Δ | Shuffle Δ |
|----------------|----------|-----------|
| **AB** | -0.0084 | -0.0004 |
| **Penrose** | -0.0579 | -0.0032 |

## Channel-Level Detail

| Substrate | Perturbation | Address AUC | Weave AUC | Hybrid AUC |
|-----------|-------------|-------------|-----------|------------|
| AB | native | 0.9788 | 0.9985 | 0.9989 |
| AB | rewire | 0.9791 | 0.9913 | 0.9904 |
| AB | shuffle | 0.4968 | 0.9986 | 0.9985 |
| Penrose | native | 0.5527 | 0.9084 | 0.9116 |
| Penrose | rewire | 0.5687 | 0.8313 | 0.8536 |
| Penrose | shuffle | 0.4858 | 0.9089 | 0.9083 |

## Dissociation Assessment

AB drops under rewire: +0.0084, under shuffle: +0.0004
Penrose drops under rewire: +0.0579, under shuffle: +0.0032

**SINGLE DISSOCIATION (Penrose arm only):** Penrose drops more under rewire, but AB does NOT drop more under shuffle.
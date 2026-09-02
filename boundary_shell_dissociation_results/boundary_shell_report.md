# Boundary Shell Dissociation v0.1

## The question
Is the exo/endo double dissociation a boundary phenomenon?
On the interior, AB's weave is so strong (0.999) that shuffle can't hurt it.
If weave weakens at the boundary (where directions are biased), shuffle should
finally break AB, completing the double dissociation.

## Results: Interior vs Boundary

| Substrate | Subset | Native Addr | Native Weave | Native Hybrid | Rewire Hybrid | Shuffle Hybrid |
|-----------|--------|-------------|--------------|---------------|---------------|----------------|
| AB | interior 75% | 0.9788 | 0.9985 | 0.9989 | 0.9905 | 0.9985 |
| AB | boundary 25% | 0.7617 | 0.9440 | 0.9439 | 0.7762 | 0.9445 |
| AB | full patch | 0.8432 | 0.9769 | 0.9772 | 0.8415 | 0.9767 |
| Penrose | interior 75% | 0.5527 | 0.9084 | 0.9116 | 0.8532 | 0.9084 |
| Penrose | boundary 25% | 0.6395 | 0.9501 | 0.9487 | 0.6369 | 0.9501 |
| Penrose | full patch | 0.6183 | 0.9435 | 0.9512 | 0.6223 | 0.9430 |

## The key test: AB boundary weave
- Interior weave AUC: 0.9985
- Boundary weave AUC: 0.9440
- Drop: 0.0546

## Boundary shell 2×2 (hybrid)
|          | Rewire Δ | Shuffle Δ |
|----------|----------|-----------|
| AB       | -0.1677  | +0.0006  |
| Penrose  | -0.3119  | +0.0014  |

## Dissociation pattern: single
AB boundary weave still compensates for address knockout.
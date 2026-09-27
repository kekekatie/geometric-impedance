# Does the window explain which knots get stuck? Pre-registration

*Written and committed **before** any code for this test existed, while the D4 run (18 roads) was
still finishing. Katie's picture: the tiling is a shaft of light through a five-dimensional
lattice. The shaft has a width (the window). Shapes near the edge of the light flicker from one
"now" to the next; shapes near its centre hold steady.*

## Jewels picked back up (earlier work, on other branches)

- `claude/bold-ritchie-l1Mc4`, `phason_connection_handoff_summary.md`: in the phason literature,
  **phason flips happen at vertices near the boundary of the acceptance window**, and vertex
  coordination tracks window depth (Jagannathan 2024; de Bruijn 1981; Socolar & Steinhardt 1986).
  Our earlier "hull depth" measure correlated with directional balance (Spearman −0.78 on
  Penrose).
- `claude/giv-quasicrystal-phason-5syx5s`, `substrates/BOUNDARY_SENSITIVITY.md`: a patch-boundary
  contamination correction. Relevant here only as a warning: everything below uses knots well
  inside the patch.

## Measure

- **The window.** Every tiling vertex is a lattice point `K ∈ Z⁵`, with hidden coordinate
  `perp(K) = Σ K_j e_{2j}` and layer `ι = Σ K_j`. For each layer, the window is estimated as the
  convex hull of `perp(K)` over all vertices of that layer in the pristine patch (`R = 40`).
- **Signed depth** `d(K)`: the distance from `perp(K)` to that hull's boundary, positive inside,
  negative outside. If a knot vertex's layer does not occur in the pristine patch, it is counted
  as "outside, layer missing" and reported separately.
- **Knot measure** `out` = the largest distance *outside* the window among the knot's vertices
  (0 if all lie inside): how far the walker's writing pushed the hidden coordinates beyond the
  shaft of light.

## Sample

Every mid-wake knot of the D4 run (18 roads, push 0.2), classified by D4 as **stubborn** (not
healed within depth 4) or **healed**. The knots are recomputed from the same deterministic
construction and matched to D4's records by road, position and size. The original road's knots
(from `healing.py`) are included too.

## Predictions

- **Wn1 (direction pre-registered).** Stubborn knots have larger `out` than healed knots
  (one-sided Mann–Whitney, `p < 0.05`). The writing that pushed hidden coordinates furthest
  outside the window is hardest to pull back with local moves. *Honest confidence about 55%.*
  With only about 8 stubborn knots, the test's power is limited.
- **Wn2 (reported, no prediction).** How well `out`, and separately the knot size, separates
  stubborn from healed knots (AUC), so that `out` can be compared with the simpler explanation
  "bigger knots are harder".

## Changes before the first run

1. *(2026-09-27, after a partial preview run on 17/18 roads, before the final run.)* The original
   road *is* D4's road (family 0, line 0). Including "the original road's knots too" counted those
   7 knots twice, so they are now taken once, from D4. The first partial preview (with the
   duplicates) gave p = 0.0001, AUC 0.75 for `out`, and AUC 0.91 for size. It is kept in the
   commit history.

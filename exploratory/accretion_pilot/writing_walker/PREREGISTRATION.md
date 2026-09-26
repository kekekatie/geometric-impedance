# The writing walker (Gemini's "writing memory" test): pre-registration

*Written and committed **before** any code for this study existed. Katie asked to pick up
Gemini's suggestion: "let a momentum walker travel down a ribbon and see if it can physically
trigger a worm flip in its wake, i.e. does travelling energy rewrite the universe's memory as it
moves?" Results will be reported against these predictions, whichever way they fall.*

## Construction

- **The tiling.** The Penrose tiling is built by the de Bruijn pentagrid: five families of
  parallel lines `e_j·x = n + γ_j`, with `γ` = the repository's Penrose offsets (sum 0), as in
  `../penrose_address_environment/`. Every tile is dual to a crossing of two lines. A **ribbon**
  is the chain of tiles dual to one line. The momentum walkers of `../least_resistance_paths/`
  travel exactly along one line.
- **The walker writes.** A walker travels along line `(J = 0, c = 0)` in the direction
  `t = e_J^⊥·x`. It starts at `t_start = −30` and is currently at `t₀`. Behind it, it pushes its
  own line sideways by `δ`:
  - the line becomes `e_J·x = c + γ_J + δ·h(t)`;
  - `h(t) = 1` on the wake `[t_start + w, t₀ − w]`;
  - `h` ramps linearly to 0 over a width `w = 2` at both ends (the walker, and its birthplace);
  - `h = 0` elsewhere.
- **Dual tiling.** The tiling is rebuilt from this line arrangement: exact integer vertex
  addresses `K ∈ Z⁵`, with family `J`'s count corrected on the side of the bent line. Patch
  radius `R = 40`.
- **What changes.** A crossing of two other lines (families `r` and `s`) that lies between the
  straight and the bent position of line `c` swaps sides of it. The three tiles around that
  triple point rearrange: a **hexagon flip**.
- **Legality.** The **vertex atlas** is the set of vertex-star types (exact, integer, up to the
  20 symmetries) found in the unperturbed tiling's interior. A vertex whose star is not in the
  atlas is **illegal** (a defect). This is an atlas of star *shapes*, without matching arrows:
  a necessary condition for legality, not a full matching-rule check.
- **Parameters.**
  - `δ ∈ {0.05, 0.1, 0.2, 0.4}` (all `< 1`, so the line never crosses its own neighbours);
  - walker positions `t₀ ∈ {−20, −10, 0, 10, 20, 30}`;
  - only faces whose vertices lie within `R − 3` of the centre are analysed.

## Predictions

- **W1 (structure, asserted).**
  - `δ = 0` reproduces the unperturbed tiling exactly.
  - Every perturbed tiling is a valid rhombus tiling: every interior edge is shared by exactly
    two faces.
  - The changed faces are exactly the hexagon flips predicted by counting triple points between
    the straight and bent line: 3 faces removed and 3 added per flip.
- **W2 (the writing stays on the road).** Every changed face shares a vertex with a face of the
  walker's own ribbon.
- **W3 (only in the wake).** No face changes ahead of the walker (`t > t₀ + 1`) or behind its
  birthplace (`t < t_start − 1`).
- **W4 (the record grows with the journey).**
  - The number of flips grows linearly with the distance travelled (R² ≥ 0.95 over `t₀`).
  - It is proportional to the push: doubling `δ` doubles the flips, within 25%, between each
    consecutive pair of `δ` values, at `t₀ = 30`.
- **W5 (is the wake a sibling universe?).** *Genuinely uncertain; my guess, about 50%:* illegal
  vertices occur **only near the two ends** (within 3 tile-edges, in `t`, of the walker or its
  birthplace), and the middle of the wake is legal everywhere. The wake would then be a stretch
  of a sibling Penrose universe, with defects only where the writing starts and stops. If instead
  illegal vertices appear all along the wake, the walker leaves damage, not a sibling universe.
  Both outcomes are reported.

## Also reported (no prediction)

- The shape of the rewritten region (elongation, axis) against the bands that forced growth
  produced in `../laying_the_tiling/worm_test.py`.
- The illegal-vertex count per unit length of wake, against `δ`.

## Changes before the first run

*(none yet)*

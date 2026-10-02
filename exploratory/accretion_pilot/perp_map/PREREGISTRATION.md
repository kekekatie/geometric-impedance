# A perp-space map of grown worlds: where do choices live, and what does a decapod do to the window? Pre-registration

*Written and committed **before** any code for this study existed.*

*Katie's parting thought (2026-09-28) was to bring in perp space. Her paper supplies the toolkit:
K. T. Niedzwiecki, **Depth-Dependent Directional Balance and Discrete Holonomy in Projection
Tilings** (June 2026), doi:10.5281/zenodo.20695694. In a cut-and-project tiling, every vertex carries
a hidden **perp-space address** inside an acceptance window. Its **hull depth** (0 at the window's
edge, 1 at the centre) sets how balanced the available step directions are: shallow vertices have
truncated, lopsided direction sets, and deep ones are balanced. Near-closed walks keep a residue
that depends on position, not on area or time.*

*Two of our findings invite this map:*

- *Genuine choices are always 2-way ([`../gromit_check/`](../gromit_check/)): where in the window do
  they sit?*
- *A decapod seed removes all choices ([`../decapod_seed/`](../decapod_seed/)): what does it do to
  the window?*

## Construction

**Lifting.** Every rhombus edge (a half-tile leg, of length `S`) points in one of 10 directions
`±ε_j`, where `ε_j = e^{i(18° + 72°·j)}` and `j = 0 … 4`.

- Starting from one vertex, with `K = 0`, a breadth-first walk over the leg edges assigns each
  vertex an integer vector `K ∈ Z⁵`: crossing an edge `±ε_j` adds `±e_j`.
- A vertex reached twice with different `K` is a **lift conflict**, and the difference is recorded.
- **Perp address:** `z⊥ = Σ_j K_j ζ^{2j}`, with `ζ = e^{2πi/5}`.
- **Layer:** `ΣK_j`.
- Diagonals (the bases of the half-tiles) are not lattice edges and are not used.

**Hull depth.**

- For each layer, take the convex hull of that world's own perp addresses, and its centroid `c`.
- A vertex's depth is `1 − g(z⊥)`, where `g` is the hull's gauge function about `c`: the scale
  factor at which the vertex sits on the scaled hull's boundary. Depth is clipped to `[0, 1]`.
- Layers with fewer than 10 vertices are skipped.

## Checks and predictions

- **V0 (asserted: the tools work on a genuine tiling).** On the reference tiling within 10 edges of
  its centre:
  - the lift has **no conflicts**;
  - the layers take exactly **4** consecutive values.
- **M1 (choices live near the window's edge).**
  - *Worlds:* patient-scheduler growth (as `../continuation_choices` arm FAST: random guesses only
    when nothing is forced anywhere), seeds `20261070 + k`, k = 0 … 11, 1,000 half-tiles each.
  - *Edge-events:* every round, every frontier edge is recorded as **forced** (exactly 1 candidate)
    or **open** (2 or more), with its two endpoint vertices.
  - *Depth:* each world's final patch is lifted and depths are computed. An edge-event's depth is
    the mean depth of its two endpoints.
  - *Prediction:* in at least **9 of 12** runs, the median depth of open edge-events is **lower**
    (shallower) than that of forced edge-events. *Confidence about 55%.*
- **M2 (a decapod smears the window).**
  - *Worlds:* the first 8 DECAPOD seeds of `../decapod_seed/` that completed all 3 runs with zero
    guesses, against the 4 FILLABLE seeds. Each is regrown deterministically, run 0, 800 tiles.
  - *Measure:* the total perp hull area over all layers.
  - *Prediction:* every one of the 8 decapod worlds has a **larger** total hull area than the
    **median** of the 4 fillable worlds. The reason: a decapod's ten sectors should each fit a
    slightly *shifted* window, so together they smear it. *Confidence about 50%.*

## Reported without prediction

- Lift conflicts in decapod worlds: a loop around the decagon that does not close in `Z⁵`, giving
  `K` differences of the form `m·(1,1,1,1,1)`.
- The number of layers in each world.
- The depth of the 2-way guessed edges themselves (patient growth).
- A picture of one world's perp space, coloured by open/forced, if time allows.

## Limits, stated in advance

- Hulls are each world's own (finite patches), so the window is approximated from inside.
- M1's runs may repeat histories: seeds collapse onto few guesses, as found in
  `../speed_of_light/`.
- Depth is computed for the final patch and applied to edge-events from earlier rounds.

## Changes before the first run

*(none yet)*

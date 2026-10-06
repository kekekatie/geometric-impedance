# Window cells: does the local clock live in the window after all? Pre-registration

*Written and committed **before** any code for this study existed.*

## Why this study

[`../robustness_depth_clock/`](../robustness_depth_clock/) withdrew "the present lasts longer deep in
the window". The sign of ρ(depth, settling time) flipped with disc size, and at the 1-edge disc the
effect vanished within vertex type. Fable (relayed by Katie, 2026-10-07) gave a sharper reading:

- In a cut-and-project tiling, the radius-r neighbourhood of a vertex is a function of **which cell of
  a level-r partition of the window** its hidden address lies in. Vertex type is the level-1 cell.
- "Depth vanishes within type" therefore says that the scalar depth adds nothing beyond the cell. It
  does not say that the window fails to set the clock.
- The sign flips are one 1-D scalar (depth) crossing a different partition at each scale.
- Fable's prediction: test settling time against the **level-r cell** at each disc radius r.
  Within-cell variance will be small at every r, and the effect will be scale-consistent. Then
  "withdrawn" could become "re-expressed: the local clock is read off the window cell at the
  measurement scale".
- Fable also asked for R1 (`../decision_radius/`) and M1 (`../perp_map/`) to be redone with cells,
  and for M2's "ten shifted windows" to be computed rather than left as a hypothesis.

**Claude's concerns, built into the design below:**

1. A window cell and a local neighbourhood pattern are **the same information** (a one-to-one
   correspondence). "The clock is read off the cell" therefore means "the clock is read off the local
   shape". That is worth knowing, but it gives perp space no new causal role.
2. As r grows, the number of cells explodes and most hold one or two probes. Raw within-cell variance
   then becomes small **automatically**. Every cell test must beat a null with the same cells
   (shuffled labels) and must predict **across worlds**.
3. Something that *would* give the window's geometry its own role is **cell size**. A cell's area in
   the window equals how common its pattern is. If rare patterns settle differently from common ones
   at every scale, that is a geometric statement, not a relabelling.
4. M2: the true Penrose window in our perp coordinates is known. Each layer is a regular pentagon:
   circumradius 1 for the two outer layers, τ for the two middle layers, total area ≈ 17.2. The
   decapod hulls measured 15.1–16.0, which is **less** than that. So the "smeared window" may not
   put any point outside the true window at all. We test that directly, with no fitting of sector
   shapes.

## Part A: the clock against window cells

**Worlds.** The first **20** zero-guess DECAPOD seeds in `../decapod_seed/` order: the 8 of
`../structure_clock/` plus the 12 of `../robustness_depth_clock/` RA. Each is grown exactly as there
(patient scheduler, decagon wall, 2,000 half-tiles), with placement rounds recorded.

**Probes.** As in `../structure_clock/`: lifted vertices with a hull depth, at least 4 edges from the
centre and at least 2 edges from the final frontier.

**Scales.** Disc radius r ∈ {0.6, 0.8, 1.0, 1.25, 1.5, 2.0} edges. At each r:

- **T** = settling time of the disc: last round minus first round over the tiles whose centroids lie
  within r edges of the probe. This is the same T as before.
- **Cell** = the translation class of exactly those tiles: the sorted set of (tile type, its three
  corners relative to the probe, with the A/B/C decoration roles kept), rounded. Two probes share a
  cell when their discs hold the same decorated tiles in the same places. The cell is defined by the
  same tiles that T is measured on, so the cell matches the ruler, as Fable asked.
- **Residual T** = T minus the mean T of the probe's 1-edge radius bin in its own world. This removes
  the distance-from-seed trend.

**Measures.**

- **η²** = the between-cell share of residual-T variance, per world.
- **Null:** 200 shuffles of cell labels within radius bins (this keeps the cell-size distribution).
- **Adjusted η²** = (η² − null mean) / (1 − null mean).
- **Cross-world R²:** for each probe, predict residual T as the mean residual T of the same cell in
  the **other 19 worlds**, using only cells with at least 3 probes there. Report R² over the probes
  that can be predicted, and the coverage. The null for R² shuffles cell labels within radius bins in
  the training worlds (200 shuffles).

**Predictions (scales: all six).**

- **A1, Fable's strong claim (within-cell variance small).** Adjusted η² ≥ 0.5 in at least 15 of 20
  worlds, at every scale. *Claude's confidence about 15%.* At r = 1.0, vertex type explained only
  7–20% of T variance (`../robustness_depth_clock/results/vertex_type_EXPLORATORY.txt`).
- **A2, the weak claim (cells carry real information).** η² is above the null's 95th percentile in
  at least 15 of 20 worlds, at every scale. *Confidence about 60%.*
- **A3, cross-world prediction.** The pooled leave-one-world-out R² is above 0 **and** above the
  null's 95th percentile, at every scale. *Confidence about 55%.* The strong form, R² ≥ 0.5 at every
  scale, is also reported. *Confidence about 10%.*
- **A4, Fable: depth adds nothing beyond the cell.** Within cells holding at least 2 probes, centre
  depth and residual T on their cell means and take the Spearman correlation per world. Prediction:
  the median over worlds has |ρ| < 0.1 at every scale. *Confidence about 50%.*
- **A5, cell size (Claude's geometric candidate).** Cell frequency = the share of all probes, pooled
  over the 20 worlds, that lie in that cell. This estimates the cell's window area. Prediction: the
  radius-stratified Spearman(log frequency, residual T) is **< 0** (rarer patterns settle more
  slowly) in at least 15 of 20 worlds, at 5 or more of the 6 scales. *Confidence about 25%.*

**Verdict wording, fixed in advance.**

- If A2 and A3 hold, the depth-clock README may say **"re-expressed: settling time carries
  information about the local pattern (equivalently, the window cell) at every scale"**, adding
  that this is a relabelling of local shape.
- Only with A1 as well may it say "read off the cell" in Fable's strong sense.
- Only with A5 as well may it claim that the window's **geometry** (cell size) sets the clock.

## Part B: R1 and M1 redone with cells (r = 1.0)

- **B1 (M1: choices sit deeper).**
  - The 12 M1 runs of `../perp_map/` are regrown identically (deterministic seeds). Each frontier
    event is assigned the cell of its edge midpoint: the decorated tiles of the final patch with
    centroids within 1 edge.
  - Raw gap = mean depth of open events − mean depth of forced events.
  - Within-cell gap = the same difference computed inside each cell that has both kinds of event,
    averaged with weights equal to the number of events.
  - Prediction (Fable's view): the within-cell gap is less than 1/3 of the raw gap in at least 9 of
    12 runs. *Confidence about 50%.*
  - Check: the regrown runs must reproduce the saved medians in `../perp_map/results/m1_runs.json`.
- **B2 (R1: deep places need a wider ring).**
  - The 4 worlds of `../decision_radius/` are regrown and the same 100 probes reselected (same
    shuffle seed). Check: the depths must match the saved rows.
  - The saved decision radii are reused; nothing is re-completed.
  - Each probe's cell is taken at r = 1.0. Pooled over the 400 probes, within cells holding at least
    2 probes, take the Spearman correlation of cell-centred depth against cell-centred decision radius.
  - Prediction (Fable's view): |within-cell ρ| < 0.1, against a raw ρ of about 0.2. *Confidence about
    50%.*

## Part C: M2, do decapod worlds leave the true window?

**Worlds.** The 8 decapod and 4 fillable worlds of `../perp_map/` M2, regrown identically (800
half-tiles). Check: they must reproduce the saved hull areas.

**The true window.**

- Four regular pentagons, one per layer. The two outer layers have circumradius 1; the two middle
  layers have circumradius τ.
- Each pentagon's orientation (pointing one way or the opposite) is fixed **only** from the reference
  tiling `L.REF` (a perfect tiling) and then frozen.
- One shared perp translation `t` per world (the lift's origin is arbitrary).
- **Inflation s\*:** the smallest amount by which every pentagon edge must be pushed outward so that
  one translation fits all of a world's vertices. Computed with a linear program. s\* ≤ 0 means the
  world fits inside the true window.

**Checks and predictions.**

- **C0 (validation, must pass).** The reference tiling and all 4 fillable worlds have s\* ≤ 0.01. If
  this fails, C1 and C2 are not interpreted.
- **C1 (do decapod worlds exceed the true window?).** s\* > 0.01 in at least 6 of 8 decapod worlds.
  *Confidence about 50%.* The decapod hull areas are below the true window's area, so the M2 smear may
  only mean the window's corners are reached more fully.
- **C2 (Fable: ten shifted windows).**
  - Split each world's vertices into 10 wedges of 36° around the centre. Use the phase (0° or 18°)
    that gives the smaller worst-wedge s\*; the same rule is applied to the fillable controls.
  - Fit each wedge separately.
  - Prediction: in at least 6 of 8 decapod worlds, **every** wedge fits the true window
    (s\* ≤ 0.01) while the whole world does not (C1).
  - The **predicted union area** (the union of the window translated by each wedge's central
    feasible translation, per layer, summed) is reported next to the measured hull area of
    15.1–16.0. *Confidence about 30%.* C2 can only hold where C1 holds.

**Reported without prediction:** where the out-of-window vertices sit (distance from the centre;
angle), and each wedge's best translation.

## Limits, stated in advance

- Decapod worlds only for Part A. They share structure, so the cross-world test is generous.
- Cells are translation classes of *grown* patches, matched exactly. A few near-identical patterns
  differing by one decoration count as different cells.
- Part A's frequencies come from the same worlds (they do not use T).
- Pentagon orientation is fixed from the reference tiling, which assumes our tilings share its
  orientation convention. C0 tests this.

## Changes before the first run

*(none yet)*

# Following the worm lines: does a decapod keep its memory on its ten ribbons? Pre-registration

*Written and committed **before** any code for this study existed.*

*[`../decapod_memory/`](../decapod_memory/) found that the slices of a decapod world sit in
perp-space windows shifted about 1.7× more than an ordinary world's (D1 held). But fixed 18° pie
slices showed no angular pattern (D2 failed). The expected structure is this: a decapod is a decagon
with the **ten half-worms** around it flipped. A half-worm is a semi-infinite **ribbon**, a chain of
rhombs joined through parallel edges, dual to half of a pentagrid line. So the window should jump
**across those ten ribbons** and stay put **within** the wedges between them. Fixed pie slices
straddle the ribbons arbitrarily. Here we trace the ribbons themselves.*

## Construction

**Worlds.** As in `../decapod_memory/`: the 8 DECAPOD and 4 FILLABLE seeds, grown to 1,500 half-tiles
with the decagon wall, then lifted to perp space (`../perp_map/`).

**Rhombs.** Two half-tiles sharing their base (the edge that is not of length `S`) form one rhomb.

**Tracing a ribbon.**

- Start at a decagon boundary edge `e₀` and take the rhomb just outside it.
- Leave through the rhomb's **other** edge parallel to `e₀` (same direction class `j`), and enter the
  rhomb on the far side of that edge.
- Repeat until the ribbon reaches the patch boundary: a missing half-tile or a missing partner.
- Each ribbon becomes a polyline of rhomb centroids.
- There are **ten ribbons** per world, one per decagon edge.

**Wedges.**

- Only vertices at radius `ρ` between 2.5 edges and the **shortest** ribbon's reach are used.
- Each ribbon's angle at radius `ρ` is interpolated along its polyline.
- A vertex belongs to the wedge between the two consecutive ribbons (in angle) that it lies between.
- Each wedge is split into **two halves** at the angle midway between its two ribbons.

**Window offsets.**

- For each wedge-half and each layer (with at least 5 vertices in that cell, and at least 40
  vertices in the layer world-wide), take the mean perp address of the cell's vertices.
- The **distance** between two cells is the mean, over the layers both cells qualify in, of the
  distance between their means.
- **Across** = the mean distance between the two halves that touch each other **across a ribbon**
  (10 pairs).
- **Within** = the mean distance between the two halves of the **same** wedge (10 pairs).
- **Ratio** = across / within.

## Checks and predictions

- **T0 (asserted).** In every world, all 10 ribbons can be traced at least 4 edges out from the
  centre. *(If any can't, that world is reported and left out.)*
- **T1 (the memory lives on the ribbons).** The ratio is **> 1.2** in at least **7 of the 8**
  DECAPOD worlds. *Confidence about 55%.*
- **T2 (and only in decapods).** The median ratio over the 4 FILLABLE worlds is **lower** than the
  median over the DECAPOD worlds. *Confidence about 60%.*

## Reported without prediction

- How straight and how radial the ribbons are: the angle change per edge of radius.
- A picture of one DECAPOD world: the ten ribbons drawn over the tiling, with wedge-halves coloured
  by their window offset.
- Per-wedge offset vectors.

## Limits, stated in advance

- 1,500 tiles. Ribbons may stop early at the ragged patch edge, and the analysis radius is set by
  the shortest one.
- The cells are small and noisy; the FILLABLE worlds give the noise baseline.
- Ribbons and Conway's worms are taken to coincide, as dual descriptions of the same pentagrid line.
  This is the standard picture, assumed here, not tested.

## Changes before the first run

*(none yet)*

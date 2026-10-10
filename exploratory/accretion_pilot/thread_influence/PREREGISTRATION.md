# Does influence travel as fast as the thread is made? Pre-registration

*Written and committed **before** any code for this study existed.*

## Why

**Astra's guiding thought** (handover, 2026-10-10): *perhaps the process that makes the next piece of
reality definite is also the process that carries influence through it.*

What we already have:

- `../speed_of_light/`: after a changed choice, the difference spreads along the now at about 1 edge
  per slice (0.67–1.13), about 3 times faster than the now moves outward.
- `../fragility/`: over 8 slices, a choice decides a long strip lying along the now.
- `../gold_thread/`: that strip is mostly **one ribbon**, the ribbon through the chosen tile that runs
  along the front. A choice decides that ribbon's path.

**The question.** Is the spreading of influence along the now *the same thing as* the laying of that
one ribbon? Does the difference between the two alternative presents travel exactly where, and exactly
as fast as, the decided ribbon is being made?

**A trap avoided.** Influence passing between tiles that share an edge is automatically "along a
ribbon", because edge-neighbours are always ribbon-neighbours. So this study does **not** ask "does
influence follow ribbons?" It asks whether **one specific ribbon**, fixed in advance, carries the
influence's leading edges, and at its own laying speed.

## Construction

**Worlds.**

- **24** ordinary worlds. Each starts from the genuine seed patch of radius 3 edges, centred at a
  **different** vertex of the reference tiling: the 24 vertices nearest the origin, excluding the
  origin itself, ordered by distance and then angle. This gives many distinct histories rather than the
  same one repeated.
- Patient scheduler, decoration-aware candidates, random streams `20261110 + k`, 1,500 half-tiles.

**Siblings.**

- At every choice, both options are grown forced-only for up to **12 slices** (`../fragility/`
  sibling growth), recording each tile's slice.
- A sibling stops early if it needs a new choice or jams. Only slices that **both** siblings reach are
  analysed.
- Choices are de-duplicated by the patch at the moment of choice.

**Defined in advance, before looking at either sibling.**

- **Front line:** the principal axis of the frontier-edge midpoints within 2 edges of the choice edge
  (as in `../fragility/`). It passes through the choice edge's midpoint m, with direction u.
- **Decided ribbon family j\*:** of the chosen tile's two leg families, the one whose edge direction
  ε_j is most nearly *perpendicular* to u. A family-j ribbon runs across its ε_j edges, so this is the
  ribbon that lies along the front.
- In each sibling, the **decided ribbon R** is the family-j\* ribbon through that sibling's chosen
  tile.
- **Along-front coordinate** of a tile: x = Re((centroid − m)·ū)/edge.

**Measured per choice, per sibling, at each slice s after the choice.**

- **Δ_s:** tiles laid by slice s in this sibling whose centroid is covered by a different tile in the
  other sibling's patch at slice s. If the other sibling hasn't covered the point, the tile is not
  counted.
- **R_s:** tiles of R laid by slice s.
- **Leading edges of influence:** the tiles of Δ_s with the largest and smallest x.
- **Spreading speed v_Δ:** the least-squares slope of (max x − min x)/2 over Δ_s against s.
- **Making speed v_R:** the same slope over R_s.

## Predictions

- **D1 (influence is led by the thread).** Pooled over choices, siblings, both ends and every slice
  with |Δ_s| ≥ 3: the leading tile of Δ_s **belongs to R_s** in at least **70%** of cases. *Confidence
  about 55%.*
- **D2 (influence travels as fast as the thread is made).** v_Δ / v_R lies in **[0.8, 1.25]** in at
  least **70%** of choices (averaged over the two siblings; choices with at least 5 analysed slices
  and v_R > 0.1). *Confidence about 50%.*
- **D3 (the speed is the speed of light).** The median v_Δ over choices lies in **[0.67, 1.13]** edges
  per slice, the range found in `../speed_of_light/`. *Confidence about 60%.*

## Reported without prediction

- The number of distinct choices and distinct histories.
- Sibling lengths, and how often the two siblings advance at very different speeds (seen in
  `../gold_thread/`).
- **Forward leakage:** the largest distance of Δ_s from the front line (perpendicular to it), against
  s.
- The share of Δ that lies on R at all.
- One exploratory figure.

## Limits, stated in advance

- At most 12 slices; siblings stop at their next choice.
- "Influence" means the *difference* between two alternative presents, not a signal sent inside one
  world.
- The front line and j\* come from a simple rule and may misidentify the ribbon when the front is
  curved.
- One tiling family.

## Changes before the first run

*(none yet)*

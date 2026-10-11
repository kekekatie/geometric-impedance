# Slack: is each choice the reader taking in one digit? Pre-registration

*Written and committed **before** any code for this study existed.*

## Why

**Fable's horizon note** ("distance-to-the-wall is a novelty budget"). A structure sitting on the wall
of its admissible region has no further choice; one strictly inside keeps slack, i.e. several legal
futures.

**`../window_cells/` found:**

- decapod worlds fit the true Penrose window with **zero slack**, with 54–60 vertices exactly on its
  edge;
- ordinary worlds of the same size fit with room to spare.

**Katie's and Claude's picture:** a choice is the *reader* taking in one more digit of a hidden number,
namely the world's position (offset) in the hidden window.

**Katie, Gemini and Astra all voted for this test (2026-10-11).**

**Note on scope.** This tests the *bookkeeping of hidden information*: where wiggle room is lost and
where it isn't. It does **not** test whether anything is mass-like.

## The measure: the wiggle room F

- For a patch, F is the set of window offsets t that are consistent with every vertex: each vertex's
  hidden address, shifted by t, must lie in its layer's pentagon of the true window (`../window_cells/`,
  orientation signs (+, −, +, −) by layer rank, circumradius 1 / τ / τ / 1, boundary included).
- Each vertex gives one half-plane per pentagon side. So F is a convex polygon, the intersection of 10
  half-plane families, and **area(F)** is the wiggle room.
- All of a world's patches are lifted from the same starting vertex, because growth only adds tiles,
  so F is comparable across one world's history and its siblings.
- Layer ranks are fixed once per world from its seed patch.

## Worlds

- **Ordinary:** the 24 worlds of `../thread_influence/`: seed centres from one 18° symmetry wedge,
  streams `20261110 + k`, patient scheduler, 1,500 half-tiles. area(F) is recorded after every slice.
- At every two-way choice, F is computed for each option (the patch plus that option's tile): F_A and
  F_B.
- **Decapod:** the 8 decapod worlds of `../perp_map/` M2 (seeds 2–9; 800 half-tiles, decagon wall).
  area(F) is recorded for the bare ring and after every slice.

## Predictions

- **S0 (validation).** F is non-empty for every patch of every ordinary world.
- **S1 (forced growth never costs wiggle room).** Over all slices that place only forced tiles, area(F)
  is unchanged (relative change < 10⁻⁶) in at least 99% of slices. *Confidence about 75%.* Reason: a
  forced tile is the only legal continuation, so every tiling consistent with the patch must contain
  it.
- **S2 (each choice cuts the wiggle room in two).** At a two-way choice, F_A and F_B both have positive
  area, they overlap by less than 1% of area(F), and area(F_A) + area(F_B) is within 1% of area(F).
  Required in at least 90% of choices. *Confidence about 60%.*
- **S3 (golden digits).** The smaller share, min(area(F_A), area(F_B)) / area(F), lies within ±0.05 of
  **1/τ² ≈ 0.382** in at least 60% of choices. If so, a choice is a golden-ratio cut, as a Fibonacci
  structure would suggest, rather than a fair coin's half. *Confidence about 35%.*
- **S4 (decapods have no wiggle room).** area(F) = 0 (below 10⁻⁹ of the true-window scale) at the end of
  growth in all 8 decapod worlds. *Confidence about 85%.* Reported without prediction: whether the bare
  ring is already pinned, and at what slice the area reaches 0.

## Reported without prediction

- area(F) against slice for each world, and against the number of choices made.
- "Bits read" = log₂(area(F₀) / area(F)) against the number of choices.
- The distribution of split shares.
- How the main world's random choice relates to the two shares.

## Limits, stated in advance

- F uses the true window with the boundary included. Points within about 10⁻⁹ of an edge count as on
  it.
- The window orientation comes from `../window_cells/`, where it was validated on the reference
  tiling and ordinary worlds.
- One tiling family.
- S3's golden-ratio guess is a long shot.

## Changes before the first run

*(none yet)*

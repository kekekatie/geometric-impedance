# Settled in the window, built in the world: does the cut's direction name the ribbon?

*Pre-registration, written and committed before any code for this study exists.*

## Where this comes from

A two-way choice cuts the wiggle room F (the set of possible hidden-window offsets) into two pieces,
along **one straight line** (`slack/`, `golden_digits/`). In the world, a choice decides mostly **one
ribbon lying along the now** (`thread_influence/`), and that decided strip is built sideways along the
front, one click per slice (`fragility/`, `front_activation/`).

Katie and Argon's Ammann-bar picture, and my "settled vs built" thought, suggest these are the same
event seen from two sides:

- **In the window**, the cut happens at once: a line with one of only five directions (multiples of
  36°, since the window is made of pentagons).
- **In the world**, the tiling has five ribbon families, one per edge direction. A ribbon is a chain of
  tiles glued across parallel edges, and it runs roughly perpendicular to those edges.

If the cut's direction names the ribbon family that gets decided, then the window *settles* which
ribbon will be laid before the world has *built* it. Nothing outruns the front: the ribbon still gets
built one local click per slice.

## Words

- **Choice, siblings:** at a two-way choice, both options grow in lockstep with the patient scheduler
  for **20 slices** (same random stream for both).
- **Cut line:** a constraint of option A's F and one of option B's F lying on the same line with
  opposite normals (as in `golden_digits/shapes_EXPLORATORY.py`). Each is measured after that option's
  first slice. Its **direction** is the line's angle mod 180°, rounded to the nearest multiple of 36°.
  That gives 5 possible values.
- **Decided strip:** at slice 20, the tiles one sibling has and the other doesn't, *where the other
  sibling has a different tile in the same place* (the "un-made" tiles of `fragility/`).
- **Family share:** for each edge-direction family j (0–4), the share of decided-strip tiles that have
  a rhombus side in direction j. Each half-tile has two families.
- **Decided family:** the family with the largest share.
- **Distinct situation:** whole base patch identical relative to the choice point (translations only)
  counts once, as in `front_activation/`.

## Set-up

- **24 fresh ordinary worlds**, with seed centres at entries 144–167 of the 18° wedge. Random seed
  20261180 + world. Each grows with the patient scheduler to 1500 added tiles.
- Every live two-way choice (both pieces > 0) with a cut line found is used, including equal splits
  (the cut exists there too).
- **Training worlds 0–11, test worlds 12–23.** Situations already seen in training are excluded from
  the test.

## Predictions (fixed now)

**C1: One ribbon family is decided.** In at least 70% of distinct situations, the decided family's
share beats the second family's by at least 0.15. (The baseline for a random family is about 0.4.)
Confidence about 75%.

**C2: The cut's direction names the family.** In the training worlds, for each of the 5 cut
directions, take the commonest decided family. That gives a lookup table, fixed before looking at the
test worlds. In the test worlds, the table predicts the decided family in at least 80% of distinct
situations. (Chance is about 20%.) Confidence about 65%.

**C3: The table is a one-to-one matching.** The table learned in training sends the 5 cut directions
(among those seen) to *different* families: no two directions map to the same family. Confidence
about 70%.

**C4: The strip runs along its ribbon.** Among decided strips at least 3× longer than wide, the
strip's long axis is within 20° of perpendicular to the decided family's edge direction in at least
70%. Confidence about 70%.

## Reported, not tested

- **The settled/built gap:** how many slices it takes for the decided strip to be built out to
  distance d from the choice point. In other words, how long after the window "knew" it does the world
  have it.
- Whether the cut direction relates to the direction of the local front.
- Choices with no cut line found, and choices where the two siblings' strip is empty by slice 20.

## Limits I already know

- The lookup table is learned, not derived. If C2 holds, a derivation is a next step.
- 20 slices is a short window. Strips that are still growing are measured as they stand.
- Family share counts every tile in the strip, not just the single connected ribbon.

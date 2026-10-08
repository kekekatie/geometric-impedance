# Fragility: what can a choice un-make? Pre-registration

*Written and committed **before** any code for this study existed.*

## The idea (Katie, 2026-10-08)

*"Once, I was a piece of stuff that got remade over many slices. Now I find I cannot be remade in the
next slice of now... (stops being remade). Nothing is ever gone, but it will no longer be
reconstructed."*

- The past is never altered. A persisting thing is **re-made in each slice** (`../worldline_body/`).
  Decay would then be the moment when the re-making comes out differently.
- Things re-made by **forced** moves only are re-made forever. The decapod world grows with no choices
  at all (`../decapod_seed/`).
- Things whose re-making passes through a **two-way choice** can be un-made. On one side of the choice,
  they are not re-made.
- Katie's picture: the **reader** (attention) moves along and notes the hidden number one digit at a
  time, at each choice. The window does not slide.
- Why not a sliding window? A steady slide would give things a *deadline* rather than a half-life (the
  three-distance theorem allows at most three lifetimes). So any decay-like behaviour has to come from
  the choices.

This first study does not measure decay curves. It maps **what a single choice un-makes**, which is
the raw material any decay would be built from.

## Construction

**Worlds.**

- 12 ordinary worlds grown from the genuine seed patch (radius 3 edges, `L.seed_patch`).
- The patient scheduler: place every forced tile each round, and guess only when nothing anywhere is
  forced.
- Random streams `20261090 + k`; 1,500 half-tiles each.
- Decoration-aware candidates (`../decapod_seed/`). No decagon wall.

**Siblings at every choice.**

- At each guess moment, record the patch and the guess edge's candidates (expected to be exactly 2).
- For **each** candidate, copy the patch, add the candidate, then continue **forced-only** growth for
  up to **8 rounds**. A sibling stops early if:
  - a round has nothing forced (it would need a new guess), or
  - it **jams** (some frontier edge has no legal candidate at all).
- The main world then carries on with its own random choice, as usual.
- Choices are de-duplicated across worlds by the patch at the moment of choice, since seeds may share
  histories (`../speed_of_light/`).

**What a choice un-makes.**

- Compare sibling A with sibling B, using only the tiles each laid after the choice.
- A tile of A is **un-made by the choice** if B covers its centroid with a different tile.
- If B doesn't reach that point at all, the tile is not counted.
- Do the same from B's side.
- **Changed vertices:** corners of un-made tiles that are not corners of any tile present before the
  choice.
- **Exposed vertices:** corners whose vertex star is complete in a sibling, that were new after the
  choice, and whose position is reached by both siblings.
- **Vertex type:** the Penrose vertex star (`L.star`), the "kind of thing".
- **Fragility of a type** = changed / exposed, pooled over all choices and both sides.

**A priori geometry (fixed before seeing any sibling).**

- **Local front line:** the principal axis of the frontier-edge midpoints within 2 edges of the guess
  edge, at the moment of choice. It passes through the guess edge's midpoint.
- **Flip sites of a vertex type:** in the reference tiling `L.REF`, a vertex with exactly 3 rhombus
  edges is the centre of a flippable hexagon, the knife-edge of a phason flip. For each type, take the
  mean number of such degree-3 vertices within 1 edge of a vertex of that type (itself included).

## Checks and predictions

- **F0 (sanity, asserted).** Every guess has exactly 2 candidates (`../gromit_check/`), and every
  sibling's first tile is legal.
- **F1 (a choice decides a line, not a blob).** For choices with at least 6 un-made tiles, take the
  un-made region's centroids. Its spread along its main axis is **at least 3 times** its spread across
  it, in at least 70% of choices. *Confidence about 65%.* Penrose ambiguity lives on ribbons ("worms").
- **F2 ("what": kinds of corner).** Across the vertex types with at least 30 exposures, Spearman(flip
  sites, fragility) ≥ +0.5. *Confidence about 35%.*
- **F3 ("where": the line ahead of the front).** At least 80% of changed vertices lie within 1.5 edges
  of the local front line, in at least 70% of choices (those with at least 6 changed vertices).
  *Confidence about 50%.*
- **F4 (where beats what).** Pooled over exposed vertices: η² of changed (0/1) by distance band from
  the front line (0.5-edge bands) is **greater** than η² by vertex type. *Confidence about 60%.* This
  is the rule learned in `../window_cells/`.

## Reported without prediction

- The number of distinct choices.
- **Dead ends:** how often one sibling jams, the other doesn't, and both do.
- Sibling lengths (rounds until the next guess or 8).
- The number of un-made tiles per choice.
- The angle between the un-made region's axis and the front line.
- Choices per round as worlds grow: the exposure rate that any half-life would depend on.

## Limits, stated in advance

- 8 rounds is a short look ahead. Effects that land later are missed.
- Siblings stop at their next needed guess, so some see fewer rounds.
- "Un-made" compares two alternative presents. It isn't a thing vanishing over time. Decay curves
  (things meeting choice after choice) are a later study.
- One tiling family. Ordinary worlds may repeat histories.

## Changes before the first run

*(none yet)*

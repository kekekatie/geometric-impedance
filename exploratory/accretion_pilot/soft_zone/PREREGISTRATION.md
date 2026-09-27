# The soft zone: how wide is the now at a growing front? Pre-registration

*Written and committed **before** any code for this study existed. The design came out of a
conversation with Katie:*
- *the now is laid by a branching crowd of "Gromits" at an expanding front;*
- *the width of the now is local, set by how much is happening ("happening density");*
- *quiet places keep things open longer (Katie's January 2026 Temporal Echo idea: quiet,
  low-acceleration systems have long memory).*

*This study asks the plasticity side of that question: how far behind the front can the present
still change?*

## Construction

**Tiles and legality.** Built on [`../laying_the_tiling/`](../laying_the_tiling/) (unchanged,
imported):
- Robinson half-triangles, whose vertex labels carry the **full Penrose matching rules**;
- legality = no overlap, and every vertex's star (complete or partial) consistent with the learned
  atlas of Penrose stars.

**Growth by a ring of Gromits** (new: parallel rounds).
- Seed: the reference patch of radius `3·SCALE_LEN` about the origin.
- Each **round**: every frontier edge is examined against the patch as it stood at the start of the
  round. Every edge with **exactly one** legal candidate gets it (the ring of simultaneous Gromits).
  A placement that has become illegal because of an earlier placement in the same round is skipped,
  and waits for a later round.
- If no edge is forced anywhere, **one guess** is made at the innermost frontier edge (a random
  legal candidate).
- A tile's **age** is the number of rounds since it was placed. Growth stops at **400** half-tiles
  beyond the seed. A jam (an edge with no legal candidate) ends the run and is reported.
- **6 runs**, seeds `20260928 + k`.

**Holes (the disturbance).**
- Hole centres are tile centroids, binned by **distance to the front** (the nearest frontier-edge
  midpoint), in units of the tile edge `SCALE_LEN`: bins `[0,1), [1,2), [2,3), [3,4), [4,6)`.
- Up to **6 holes per bin per run**, chosen at random among eligible centroids, not closer than 4
  edges to the seed centre.
- A hole = every half-tile whose centroid lies within `ρ = 1.2` edges of the hole centre.

**Refill.**
- The hole's tiles are removed. Growth then re-lays **only inside the hole**: a placement is
  allowed only if its centroid lies within `ρ + 0.25` edges of the hole centre. It uses the same
  forced-first rule (sequential inside the hole), with random guesses.
- The refill is complete when the total area laid equals the area removed.
- **8 refill attempts** per hole, with different guess seeds.
- Outcome per attempt:
  - **same**: the identical tiles;
  - **different**: a complete legal refill that differs;
  - **jam**: no legal candidate at some hole edge, or no progress.
- **A hole is *soft* if at least one attempt gives a *different* complete legal refill.**
  **Freedom** `F(bin)` is the fraction of holes in that bin that are soft.

**Happening density** at a hole: over the half-tiles within 2 edges of the hole centre, the number
of tiles divided by the number of distinct rounds in which they were laid. That is, tiles per tick
locally. High means busy; low means quiet.

## Checks (asserted)

- **Z1.** Every tile placed during growth passes the legality check at the moment of placement.
- **Z2.** Re-adding a hole's original tiles, in their original order, is legal: the original
  refill is always available.

## Predictions

- **S1 (a soft zone exists).** Freedom at the front is high and deep inside is low:
  `F([0,1)) ≥ 0.5` **and** `F([4,6)) ≤ 0.1`. *Honest confidence about 55%.*
- **S2 (it narrows with depth).** `F` is non-increasing across the five bins, allowing at most one
  increase of at most 0.1.
- **S3 (Katie's January direction: quiet places stay open longer).** Within depth bins, softer
  holes have **lower** happening density than hardened holes. Statistic: the mean of (happening
  density of hardened holes − happening density of soft holes), averaged over the bins that
  contain both kinds. One-sided permutation test (soft/hard labels shuffled within bins, 10,000
  permutations), `p < 0.05`. *Honest confidence about 40%.*

## Reported without prediction

- **The width of the now:** the first depth bin with `F < 0.1`.
- The same freedom curve by **age** (rounds) instead of distance.
- **Jam** rates per bin.
- The number of distinct different refills found per soft hole.

## Limits, stated in advance

- One tiling family (Penrose); small holes; 400-tile patches.
- A hole is judged by *sampled* refills (8 attempts), not an exhaustive enumeration, so "not
  soft" means "no different refill found in 8 attempts".
- The ring-of-Gromits rule is one reasonable parallel rule among several.

## Changes before the first run

*(none yet)*

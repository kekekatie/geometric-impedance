# Two decapods in one world: can two centres coexist? Pre-registration

*Written and committed **before** any code for this study existed.*

## Why

- A decapod world is pinned to a **single point** in the hidden window, the centre of its bare ring's
  decagon of possibilities (`../slack/classify_EXPLORATORY.py`). It grows with no choices at all.
- In a Penrose tiling, the special "cartwheel" centre where all ten ribbons meet is unique.
- Questions from Katie, Astra and Gemini: is a decapod mass-like (a thing *in* a world) or a world's
  organising seed? Can two coexist?

**Claude's prediction:** two decapods each pin the world to *their own* centre. Two different centres
can't both hold, so **two centres of the universe cannot coexist**. Where their growths meet, the
world's wiggle room becomes **empty** and growth **jams**. A control (one decapod plus a far piece of
*its own* world) should join peacefully.

## Construction

**Rings.** The first 8 zero-guess DECAPOD rings (`../decapod_seed/`, seeds 2–9). Ring A sits at the
origin, as usual.

**Two-decapod worlds (TWO).**

- Ring A of type s, plus ring B of type s′ = the next seed in the list (cyclic), **translated** by
  v = n·(ε_j + ε_{j+1}). Here ε are unit edge vectors, so v is a lattice translation and B's tiles
  align with A's directions.
- Configurations: n ∈ {5, 7} (distance about 8.1 and 11.3 edges), direction j ∈ {0, 2}. That gives
  8 × 2 × 2 = **32 worlds**.
- **Growth:** forced moves only, never through either decagon (both walls kept), patient rounds.
  Growth stops when:
  - **JAM** (a frontier edge has no legal candidate);
  - **STUCK** (nothing forced anywhere);
  - **400 half-tiles after merging**;
  - or **3,000** half-tiles in total.
- **Merged:** the first slice at which one connected patch contains both rings.

**Control worlds (CTRL).**

- Ring A of type s, grown alone to 2,500 half-tiles, gives world W.
- Seed = ring A plus the tiles of W within **2 edges** of the point v (same v as the TWO worlds).
- Grown with the same rules (wall at A only). **32 worlds.**

**Measures.**

- Status, slice of merging, and tiles at merging.
- After merging, the kind of the merged patch's wiggle room F: empty, point, segment or polygon
  (linear-programming classifier).
- Where the jam happened: the jam edge's distance from the perpendicular bisector of A and B's centres.

## Predictions

- **T1 (two centres can't coexist).** In at least **90%** of TWO worlds that merge, the merged F is
  **empty**, and the world jams within 400 half-tiles after merging. *Confidence about 70%.*
- **T2 (one world rejoins itself).** In at least **90%** of CTRL worlds that merge, the merged F is a
  **point** and there is no jam. *Confidence about 80%.*
- **T3 (the clash happens at the seam).** Among TWO jams, the median distance of the jam edge from the
  A–B perpendicular bisector is **less than 2 edges**. *Confidence about 55%.*

## Reported without prediction

- How many worlds merge.
- STUCK cases: growth needing a choice.
- Whether TWO worlds jam *before* merging (a clash detected at a distance).
- Pictures of one TWO world and one CTRL world.

## Limits, stated in advance

- Only translations along two directions and two distances.
- Ring B is a different decapod type from A (cyclic next seed); same-type pairs are not tested.
- One tiling family.

## Changes before the first run

*(none yet)*

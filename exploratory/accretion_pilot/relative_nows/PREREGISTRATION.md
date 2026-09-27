# Relative nows: what happens when two growing fronts meet? Pre-registration

*Written and committed **before** any code for this study existed. This is the first door after the
soft-zone study ([`../soft_zone/`](../soft_zone/)). Katie's picture: there are local nows, each laid
by its own crowd of Gromits, and each crowd's guesses carry its region into a slightly **offset**
sibling universe. What happens where two such nows meet?*

## Construction

The same machinery as `../soft_zone/soft_zone.py`, imported, including its corrected vertex check:
Robinson half-tiles with the full Penrose matching rules, and growth by a **ring of Gromits**
(parallel forced placements each round, with one guess when nothing is forced).

- **Seeds.** Two genuine patches of the reference tiling (radius `3·SCALE_LEN`), centred at
  `c₁ = −8·SCALE_LEN` and `c₂ = +8·SCALE_LEN` on the real axis. Both are parts of **one**
  universe.
- **Growth.** Both crowds grow in the same patch, simultaneously, round by round, until **1,100**
  half-tiles have been added or a jam occurs. Each tile inherits the **region label** (1 or 2) of
  the tile whose frontier edge it filled. When nothing is forced, one guess is made at the frontier
  edge closest to its own seed.
- **Arms** (12 runs each; seeds `20260929 + k`):
  - **TWO-LOCAL**: both crowds guess at random among the legal candidates. These are relative
    nows.
  - **TWO-ORACLE**: whenever either crowd guesses, it picks the candidate that belongs to the
    reference tiling, if there is one. This is a shared, universal now.
  - **ONE-LOCAL** (the size control): a single seed at `c₁`, grown to the same total size.
- **Meeting.** The fronts have *met* once at least 10 edges are shared between tiles of region 1 and
  region 2.

## Measures

- **Jam**: a frontier edge with no legal candidate. The run's status is `JAM` or `ok`, and the jam
  location is recorded.
- **Merged**: the fronts met, and the run ended `ok`.
- **Offset**: the fraction of each region's tiles that belong to the reference tiling.
- **Soft repair** (for jammed runs only): remove every tile within `2·SCALE_LEN` of the jammed
  edge's midpoint, which is the soft band measured in the soft-zone study, and re-lay it with the
  soft-zone refill (8 attempts, confined within `2·SCALE_LEN + 0.25`). If any attempt completes
  and the jammed edge then has a legal candidate, the seam was repaired.

## Checks and predictions

- **M1 (control, asserted).** TWO-ORACLE never jams (0/12), and both regions agree with the
  reference tiling on 100% of tiles.
- **M2 (control).** ONE-LOCAL never jams (0/12).
- **M3 (the question).** TWO-LOCAL jams in **at least 6 of 12** runs: relative nows that made
  different guesses cannot always meet cleanly. *Honest confidence about 50%.*
- **M4 (where).** In TWO-LOCAL jams, the jam lies in the **meeting zone**: the jammed edge's
  midpoint is closer to the perpendicular bisector (`Re z = 0`) than `3·SCALE_LEN`.

## Reported without prediction

- The soft-repair success rate for jammed runs.
- Whether jams occur only in runs where the two regions ended in *different* sibling universes (by
  their agreement with the reference near the interface).
- The number of guesses per crowd.

## Limits, stated in advance

- A single tiling family.
- Two seeds on one axis, at one separation.
- Growth is capped at 1,100 tiles.
- "Same universe" is judged by agreement with the one reference tiling.

## Changes before the first run

*(none yet)*

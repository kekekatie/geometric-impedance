# Happening density: does a quiet place have a wider now? Pre-registration

*Written and committed **before** any code for this study existed. Katie asked: "If I am a point in
distant space, light years from anything, what is my local width of now?" Her January 2026 Temporal
Echo idea says that quiet places remember longer. The soft-zone study
([`../soft_zone/`](../soft_zone/)) found the now to be about 2 tile-edges wide, and **a place, not a
time**. Its happening-density test was weak, because happening density was only observed, never
manipulated. Here it is **manipulated**.*

## Construction

The same machinery as `../soft_zone/soft_zone.py` (imported, with the corrected vertex check): full
matching rules, and growth by a ring of Gromits from a single seed at the origin.

- **Throttle.** In every round, each forced placement whose frontier-edge midpoint lies in the
  **slow half** (`Re z < 0`) is carried out only with probability **0.25**, using the run's random
  stream. The **fast half** (`Re z ≥ 0`) places every forced tile. When nothing is placed anywhere,
  one guess is made at the innermost frontier edge, exactly as before.
- Growth adds **500** half-tiles. **8 runs**, seeds `20260930 + k`.
- **Happening density** per half: tiles placed per round in that half, over the whole growth.
- **Holes.** Exactly as in the soft-zone study:
  - hole radius 1.2 edges, 8 refill attempts;
  - soft means some attempt gives a different complete legal refill;
  - distance bins `[0,1), [1,2), [2,4)` tile-edges behind the front;
  - **up to 4 holes per bin per half per run**, with centres at least 4 edges from the origin
    and at least `2ρ` apart.
- **Age** of a hole = the current round minus the mean round in which its tiles were laid.

## Predictions

- **H0 (manipulation check, asserted).** The slow half's happening density is below 0.6 times the
  fast half's.
- **H1 (the spatial width does not depend on happening density).** In both halves, freedom is 0 in
  the deepest bin `[2,4)` (at most 0.05), and in each of the bins `[0,1)` and `[1,2)` the two halves'
  freedom differs by at most 0.2. *Confidence about 60%.*
- **H2 (the temporal width does).** The median age of **soft** holes in the slow half is at least
  **2×** the median age of soft holes in the fast half. A quiet place stays in the now for more
  rounds. *Confidence about 65%.*

## Reported without prediction

- Freedom by age bins, per half.
- The front's shape: how far the slow half lags.
- Guesses per run.

## Limits, stated in advance

- The throttle is imposed from outside ("fewer Gromits act here"). It is not an emergent quietness.
- It is one tiling family, with small holes and sampled refills.

## Changes before the first run

*(none yet)*

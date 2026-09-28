# Local deciders: can the now become a local front without jamming? Pre-registration

*Written and committed **before** any code for this study existed.*

*Door 2 ([`../island_lens/`](../island_lens/)) found that under the patient scheduler the world grows
**slice by slice**. Only one decision (guess) is made at a time, anywhere, and only when nothing is
forced anywhere. So the arrival of the now is ruled by a single global queue, and there is no local
geometry of time. Katie's insight (a persisting body is re-made in every slice of now) needs a real,
local now to live in. This study builds one.*

## Construction

The growth is as in `../continuation_choices` arm FAST: full matching rules, the corrected vertex
check, the usual seed patch (radius 3 edges) and no throttle. Guesses are random among the legal
candidates, using the run's random stream. The only change is **when and where guesses happen**.

**The HORIZON-h scheduler.** Each round:

1. Scan the frontier. An edge with no candidate is a **jam** (the run ends). An edge with exactly
   one candidate is **forced**.
2. Place every forced tile (re-checking legality, as before).
3. An edge with ≥ 2 candidates is **eligible** for a guess if no forced edge found in step 1 lies
   within `h` edges of it (midpoint to midpoint).
4. Go through the eligible edges innermost first (the usual frontier order). Guess at an edge (a
   random legal candidate, if its edge is still open) unless a guess was already made this round
   within `h` edges of it.
5. If nothing was placed and nothing was guessed, the round passes.

Two limits:

- `h = ∞` is exactly the patient (WAIT) scheduler: a guess only when nothing is forced anywhere, and
  one guess at a time.
- Small `h` means impatient, independent local decisions at many places at once.

- **Horizons:** `h ∈ {0.5, 1, 2, 3, 4, 6, ∞}` edges.
- **Runs:** 8 per horizon, seeds `20261040 + k`, the same seeds for every horizon.
- Growth adds **1,500** half-tiles, or stops at a jam.

## Measures

- **Jam:** whether the run jams before 1,500 tiles, and where and when.
- **Sector spread** `SS` (how un-smooth the now is):
  - take the tiles whose centroids are 7–9 edges from the origin;
  - split them into **16 angular sectors**;
  - take each sector's median placement round.
  - `SS = (largest sector median − smallest sector median) / median over all those tiles`.
  - A smooth, local front gives a small `SS`. The global queue gave large spreads.
  - `SS` is computed only for runs that complete, or that jam after every sector has tiles in the
    band. Otherwise it is reported as missing.
- Rounds to finish, and guesses per run.

## Predictions

- **H0 (asserted).** `h = ∞` reproduces `continuation_choices`' FAST growth exactly, tile for tile and
  round for round, with seed `20261040 + k` given to both, and never jams.
- **H1 (locality smooths the now).** The median `SS` over runs at `h = 2` is **less than half** the
  median `SS` at `h = ∞`. *Confidence about 65%.*
- **H2 (impatience jams).** At `h = 0.5`, **at least half** the runs jam. *Confidence about 60%.*
- **H3 (a sweet spot exists).** Some finite `h ≤ 4` has **0/8 jams** and a median `SS` less than half
  that at `h = ∞`. *Confidence about 45%.*

## Reported without prediction

- Jam rate and median `SS` for every horizon: the full curve.
- Where the jams happen: how far out, and whether near two recent guesses.
- Guesses per run, and the number of simultaneous guesses per round.

## Limits, stated in advance

- One tiling family and one size.
- `SS` is one summary of smoothness, taken in one radial band.
- Random guesses mean different horizons grow different tilings. Only the seeds are shared.
- Whether a jam could be *repaired* (the soft-repair idea) is not tried here.

## Changes before the first run

*(none yet)*

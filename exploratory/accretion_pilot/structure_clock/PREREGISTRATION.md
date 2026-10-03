# Structure and the local clock in an intact decapod world. Pre-registration

*Written and committed **before** any code for this study existed.*

*The open question (see the map at the top of `../RESUME_HERE.md`) is how **structure** and
**happenings** together make local time. Katie's rattle principle says to keep the whole system
intact: no throttled stripes, no pre-laid bodies, just a decapod world growing by itself. Such a world
needs no guesses, has no global queue, and repeats exactly
([`../decapod_seed/`](../decapod_seed/)).*

- *Structure:* each place's **hull depth** in the hidden window, from Katie's paper
  (doi:10.5281/zenodo.20695694), computed as in [`../perp_map/`](../perp_map/).
- *Local time:* how long a place takes to **settle** (be fully laid), counted two ways, as in
  [`../quiet_lasts_longer/`](../quiet_lasts_longer/) and
  [`../continuation_choices/`](../continuation_choices/):
  - in universal rounds;
  - in **local happenings**: tiles laid nearby. Earlier this was about 19, whatever the pace.

## Construction

**Worlds.** The 8 zero-guess DECAPOD seeds used in `../perp_map/` M2, grown with the patient
scheduler and the decagon wall to **2,000** half-tiles. Every tile's placement round is recorded.

**Probes.** Every vertex `v` that meets all of these:

- `|v| ≥ 4` edges;
- at least **2 edges** from the final frontier (the nearest frontier-edge midpoint), so its
  neighbourhood is complete.

**For each probe:**

- **Disc** = the tiles whose centroids lie within **1.0 edge** of `v`.
- `birth` = the earliest placement round in the disc; `full` = the latest.
- **T** = `full − birth`: settling time in rounds.
- **H** = the number of tiles within **2.0 edges** of `v` laid in rounds `birth+1 … full`: settling
  time in local happenings.
- **Depth** = `v`'s hull depth, from the world's own per-layer hulls.

**Correlation, stratified by radius.** Timing depends on the distance from the centre, so:

- Spearman correlations are computed **within radial bins 1 edge wide**, using only bins with at
  least 15 probes.
- The bins' values are averaged, weighted by their probe counts.
- This gives `ρ_T = ρ(depth, T)` and `ρ_H = ρ(depth, H)` for each world.

## Predictions

- **C1 (structure sets how long the present lasts, in rounds).** `ρ_T` has the **same sign** in at
  least **7 of 8** worlds, and the median `|ρ_T|` is **≥ 0.15**. The direction is not predicted.
  *Confidence about 40%.*
- **C2 (but the happening budget is universal).** The median `|ρ_H|` is **< 0.15**: how many local
  happenings it takes to settle does not depend on structure. *Confidence about 45%.*

The two together (C1 and C2) would say that **structure changes the pace of local time, but not the
amount of happening a present needs.**

## Reported without prediction

- Distributions of T and H, and the clock rate H/T, against depth.
- A within-world permutation baseline: depth shuffled among probes in the same radial bin,
  1,000 times, giving the share of shuffles with `|ρ|` at least as large.
- Whether the result differs between layers (the small and large windows).

## Limits, stated in advance

- Decapod worlds only, all grown deterministically.
- 8 worlds, which share some structure (their ribbons coincide near the centre;
  `../worm_lines/`).
- Depth comes from each world's own finite hull.
- The disc and neighbourhood radii (1.0 and 2.0 edges) are single choices.

## Changes before the first run

*(none yet)*

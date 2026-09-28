# Door 2: does a quiet island bend the now like gravity, and is it quietness or fullness? Pre-registration

*Written and committed **before** any code for this study existed. This is door 2 of the "relativity
and gravity" play.*

*In real physics, light passing a mass is **delayed** (the Shapiro delay) and **bent** toward it
(gravitational lensing). One classic picture of both treats space near a mass like a lens: a place
where things go more slowly. Our quiet regions are slower places. Katie asked whether the
gravity-like thing is really **quietness** (happening density) or **fullness** (accretion density:
settled past already sitting there). This study sets the two side by side.*

## Construction

The growth follows `../continuation_choices` (full matching rules, corrected vertex check, WAIT
scheduler: a guess is made only when nothing is forced anywhere), with two changes:

- **Oracle guesses.** Every guess picks the candidate that belongs to the reference tiling `L.REF`.
  So in every arm the growth lays **the same tiling** (a subset of `L.REF`). Only **when** tiles are
  laid can differ. This keeps the comparison purely about time, the way gravity changes the geometry
  of time without changing the matter.
- Growth adds **2,400** half-tiles from the usual seed patch (radius 3 edges) at the origin.

**The island** is a disc of radius `R_i = 2` edges, centred at distance **6.5 edges** from the origin
in direction `θ_k = 2πk/8 + 0.2`, for k = 0 … 7 (8 runs per arm).

**Arms:**

- **CONTROL:** no island. With oracle guesses this is one deterministic history, used as the
  reference for all runs.
- **QUIET:** a forced placement whose frontier-edge midpoint lies in the island disc is carried out
  with probability **0.25**. The draws use their own random stream (seed `20261030 + k`).
- **FULL:** the island is **pre-laid** at round 0 with the reference-tiling tiles whose centroids lie
  in the disc: settled past, already there. It is **inert until reached**:
  - Frontier edges of island tiles are not grown until any grown or seed tile shares a vertex with an
    island tile.
  - From then on the island is part of the patch.
  - Island tiles do not count toward the 2,400.

**Arrival time** `T(x)`: the round in which the tile covering point `x` was laid. This is when the
now reaches `x`. The **delay** is `Δ(x) = T_arm(x) − T_CONTROL(x)`, at the same point in the same
tiling.

**Sample points**, in each run's island frame (`u` = unit vector towards the island centre `c`, `v`
= `u` turned 90°):

- **Shadow** (behind the island): `c + u·(R_i + s) + v·w`, for `s ∈ {1.0, 1.5, …, 3.5}` and
  `w ∈ {−0.5, 0, +0.5}` edges (18 points).
- **Side** (level with the shadow, off to each side): `c + u·(R_i + s) ± v·4.0` (12 points).
- **Far** (the opposite side of the world): the shadow points mirrored through the origin
  (18 points).

A tiny fixed offset keeps points off tile edges.

**Per-run metrics:**

- `Δ_shadow`, `Δ_side`, `Δ_far`: the mean delay over each set of points.
- **Local delay** = `Δ_shadow − Δ_far`. It removes any global slowdown: under WAIT, the whole growth
  can be held up while the island lags.
- **Lens** = `Δ_shadow − Δ_side`.
  - If the now arrives later directly behind the island than off to its sides, the arriving front
    is dented inward there.
  - Since the direction of travel is perpendicular to the front, a dented front **converges** behind
    the island. That is focusing, like a lens or gravity.

## Checks and predictions

- **G0 (asserted).**
  - Every run completes without jam or stall.
  - Every laid tile belongs to `L.REF`.
  - Every sample point is covered in every arm.
- **G1 (a quiet island delays the now behind it: Shapiro-like).** In QUIET, the local delay is
  **> 0 in at least 7 of 8** runs, and its mean is **≥ 2 rounds**. *Confidence about 70%.*
- **G2 (a quiet island focuses: lensing-like).** In QUIET, the lens metric is **> 0 in at least 7 of
  8** runs. *Confidence about 55%.*
- **G3 (fullness does the opposite).**
  - Prediction: in FULL, the local delay is **< 0 in at least 7 of 8** runs. The now arrives
    **earlier** behind a full island, because settled past need not be laid again.
  - If this holds, then in our model the gravity-like property is quietness, not fullness.
  - *Confidence about 55%.*

## Reported without prediction

- FULL's lens metric.
- The global delay `Δ_far` in each arm: the patient scheduler's non-local channel.
- Delay as a function of `s` (distance behind the island).
- The number of guesses and idle rounds.
- Two cross-checks of the "quiet = slow clock" reading:
  - happening density inside and outside the island in QUIET (tiles per round, over the rounds
    while the island is being laid);
  - FULL's "wake" round.

## Limits, stated in advance

- One tiling (the reference), one island size, one distance, one throttle strength.
- The CONTROL run is a single deterministic history.
- Variation between runs comes from the island direction (and, in QUIET, from the throttle draws).
- "The now" here is the growth front's arrival, not the ~1 edge/round influence measured in
  `../speed_of_light/`. The front is the time geometry every signal must live in, but it is not
  itself a light signal.
- The patient scheduler couples distant places (hence `Δ_far`).
- FULL's inert-until-reached rule is one choice among many ways to model settled past.

## Changes before the first run

*(none yet)*

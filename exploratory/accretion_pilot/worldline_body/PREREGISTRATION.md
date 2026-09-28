# A worldline body in a decapod world: does a persisting body make a field of time around it? Pre-registration

*Written and committed **before** any code for this study existed.*

*Katie's insight (after [`../island_lens/`](../island_lens/)): in our growth model, the plane is space
and time together, and the growing edge is the now. So a persisting body is not a blob. It is a
**worldline**, a thread through every slice of now, **re-made in each one**. The island study
failed because the patient scheduler grows the world through one global queue. There was no local
geometry of time to disturb. The decapod world ([`../decapod_seed/`](../decapod_seed/)) needs **no
guesses**: every round, every forced tile everywhere is laid. It is a local now, and it is fully
repeatable, so a body's effect can be read off against the identical world without it.*

## Construction

**Worlds.**

- There are 6 decapod seeds from `../decapod_seed/`: the 6 lowest-numbered DECAPOD seeds whose 3
  runs all completed with 0 guesses.
- Growth uses the patient scheduler with decoration-aware candidates (`decapod_seed.candidates`). The
  decagon interior is never grown.
- The world grows to **2,000** half-tiles.
- **CONTROL** is grown without a body, and also to 3,500 tiles to supply FULL's pre-laid stripe.

**The body: a worldline stripe.**

- Direction `u = e^{iθ}`, with `θ ∈ {10°, 130°, 250°}`, giving 3 bodies per seed and 18 in all.
- The stripe is the set of points `z` with lateral distance `|Im(z·ū)| ≤ 0.75` edges and radial
  distance `Re(z·ū) ≥ 3.0` edges.
- **QUIET:** a forced placement whose frontier-edge midpoint lies in the stripe is carried out with
  probability **0.25**, using its own random stream (seed `20261060 + 10·seed + body`). Rounds with
  forced moves waiting pass idle, as before, and no guess is ever needed.
- **FULL:** every CONTROL tile (from the 3,500-tile growth) whose centroid lies in the stripe is laid
  at round 0, before growth begins. This is settled past along the whole line. These tiles don't
  count toward the 2,000.

**Arrival time** `T(x)`: the round in which the tile covering `x` was laid.

- The **delay** is `Δ(x) = T_arm(x) − T_CONTROL(x)`.
- The tiling is identical in every arm (asserted, W0), so the delay is purely timing.

**Sample points.**

- On circles of radius `ρ ∈ {5, 6, 7}` edges, at lateral distance `d ∈ {1, 2, 3, 4, 6}` edges
  (arc length) on **both** sides of the stripe's centre line.
- **Far** points: the same positions for the opposite direction `θ + 180°`.
- A tiny fixed offset keeps points off tile edges. Points covered by pre-laid FULL tiles are
  excluded (none are expected, since `d ≥ 1 > 0.75`).

**Per-body profile.** `Δ(d)` is the mean delay over `ρ` and both sides at each `d`, and `Δ_far` is the
mean over the far points.

## Checks and predictions

- **W0 (asserted).**
  - No arm ever guesses or jams.
  - Every tile laid in every arm belongs to CONTROL's 3,500-tile tiling (matched by the
    decoration-aware key).
  - Every sample point is covered in every arm.
- **W1 (a quiet worldline has a field).** In QUIET, the mean of `Δ(1)` and `Δ(2)` is **> 0** in at
  least **80%** of the 18 bodies. *Confidence about 75%.*
- **W2 (the field fades with distance, and the rest of the world is untouched).** In QUIET, both
  must hold:
  - `Δ(1) > Δ(6)` in at least **70%** of bodies;
  - the median of `|Δ_far|` over bodies is **≤ 1 round**.

  *Confidence about 60%.*
- **W3 (fullness is the opposite of quietness).** In FULL, the mean of `Δ(1)` and `Δ(2)` is **< 0**
  (the now arrives early) in at least **80%** of bodies. *Confidence about 60%.*

## Reported without prediction

- The whole profile `Δ(d)` for both arms. The shape of the fall-off: does `log Δ` or `Δ` fall more
  linearly against `d`, or against `log d`?
- Delay versus `ρ` (does the field grow outward, along the worldline?).
- The idle rounds and total rounds in QUIET.

## Limits, stated in advance

- One tiling family and 6 decapod worlds (whose fronts are not round).
- One stripe width and one throttle strength.
- One space dimension plus time. Real bending is not possible here, only time delay.
- "Field" is an analogy: a delay pattern in the arrival of the now, not a force.

## Changes before the first run

*(none yet)*

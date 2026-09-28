# The speed of light in a Gromit world: pre-registration

*Written and committed **before** any code for this study existed. It is door 1 of the
"relativity and gravity" play that Katie opened. Before we ask whether a quiet region bends things
like gravity, we need to know **how fast influence travels** in our world, and what shape its reach
takes.*

*Cellular automata use "speed of light" for the fastest rate at which any influence can spread; in
Conway's Life it is one cell per generation. We borrow the term in that sense only. Our world has a
special shared clock (the growth rounds), so nothing here is Lorentz invariant.*

## Construction

The growth is exactly that of `../continuation_choices/continuation_choices.py`, arm **FAST**
(imported):

- full Penrose matching rules, with the corrected vertex check;
- one genuine seed patch of radius 3 edges;
- the **WAIT** scheduler: every forced tile is placed each round, and a guess is made only when
  nothing is forced anywhere;
- 1,000 half-tiles;
- seeds `20261020 + k`, for k = 0 … 11.

**Twin histories.** For each run:

- **History A** is grown normally, recording each tile's round and every guess.
- For each guess `j` of A, and for each **alternative** candidate at that guess (every candidate A
  did not choose), a **history B** is made:
  - B replays A exactly up to guess `j`;
  - at guess `j`, B lays the alternative;
  - B then continues with the same rules.
- One such A/B pair is a **perturbation**. It is located at `p₀`, the midpoint of the guessed
  frontier edge, and happens in round `r₀`.

**The forcing epoch.** Only the rounds `r₀ … r₀ + T` are compared. `r₀ + T` is the last round
before either history makes its **next guess**, before B jams, or before either reaches the size cap.

- Within this window, every placement in both histories is *forced*, so any difference between them
  travels only through the local growth rules.
- After the window, the patient scheduler links distant places: the timing of the next guess
  depends on the whole patch. That non-local channel is reported separately and is not part of any
  prediction.

**Difference.** `D_t` is the set of tiles laid by round `r₀ + t` in exactly one of the two
histories (the symmetric difference). Its tiles are described by their centroids.

- **Reach** `R(t)`: the largest distance from `p₀` to any tile in `D_t`.
- **Sideways width** `W(t)`: the largest arc length, measured along the circle through each tile
  around the origin, between a tile of `D_t` and `p₀`'s direction. It is `|z|·|Δθ|`, in edges.
- **Local front speed** `v_f`: in history A, the change over the window in the mean radius of the
  frontier-edge midpoints within ±20° of `p₀`'s direction, divided by `T`. It is in edges per round.
- **d_max**: the longest side of any tile (the tile diameter).

## Checks and predictions

- **Z1 (asserted: a speed limit exists).** In every perturbation and every round,
  `R(t) − R(t−1) ≤ 2·d_max`, with `R(0) ≤ 2·d_max`. A tile's legality depends only on tiles
  touching its corners, so influence cannot jump further than that in one round.
- **Z2 (asserted: the past is untouched).** No tile laid before `r₀` is ever in `D_t`.
- **L1 (light-like, not diffusive).**
  - Over perturbations whose window has `T ≥ 6` and `D_T` has at least 5 tiles, fit
    `log W(t) = α·log t + c` for `t = 1 … T`, using rounds where `W(t) > 0`.
  - Prediction: the **median α ≥ 0.8**, meaning the width grows at a steady speed like a light
    front (α ≈ 1). Spreading like ink diffusing would give α ≈ 0.5.
  - *Confidence about 50%.*
- **L2 (news travels faster than the front grows).**
  - The **sideways news speed** is `W(T)/T`.
  - Prediction: its median is **at least 3×** the median local front speed `v_f`, over the same
    perturbations as L1.
  - Reasoning: in our earlier runs the front advanced only about 0.07 edges per round, yet each
    round lays several tiles. So forcing seems to run *along* the front much faster than the front
    moves *outward*.
  - *Confidence about 60%.*
- **L3 (influence travels in rays).**
  - In a Penrose tiling, changing one decision tends to change tiles along a **line** (a "worm"),
    not a round blob.
  - Measure: over perturbations with at least 10 tiles in `D_T`, compute the principal-axis
    elongation `sqrt(λ₁/λ₂)` of the centroids of `D_T`.
  - Prediction: it is **≥ 3 in at least half** of them.
  - *Confidence about 45%.*

## Reported without prediction

- The number of perturbations, and how many B histories **jam** inside the window (the alternative
  was a dead end). Where they jam, and when.
- `R(t)` and `W(t)` curves. The ratio of the fastest observed per-round spread to `d_max`: how close
  influence comes to the speed limit.
- **After the window** (exploratory): whether, and how fast, differences appear far away once the
  patient scheduler's global guess timing comes into play. This is the scheduler's non-local
  channel.

## Limits, stated in advance

- One tiling family; the FAST arm only (no quiet regions yet: that is door 2).
- There is a preferred frame (the shared rounds).
- Perturbations are only the choices the growth actually faced.
- Windows are short: they end at the next guess.

## Changes before the first run

*(none yet)*

## Noted for later (Katie, 2026-09-28)

For door 2 (a quiet region as a lens), also test **accretion density** against **happening
density**. Does a region slow and bend passing fronts because it is *quiet* (fewer events per
round), or because it is *full* (more settled past)? In real gravity, the amount of stuff bends
things, not how busy it is.

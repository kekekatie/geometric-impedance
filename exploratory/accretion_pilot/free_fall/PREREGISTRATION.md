# Does anything fall? Maximal proper time beside a worldline body. Pre-registration

*Written and committed **before** any code for this study existed.*

*[`../worldline_body/`](../worldline_body/) found that a **quiet** worldline makes a local, fading
field of **late** arrival (slow time) around itself. A **full** one makes a field of **early**
arrival. A field alone is not gravity, though. Gravity is what bodies **do** in it. To avoid
inventing a rule that decides the answer, we use Einstein's rule: **a free body travels, between two
events, along the path that accumulates the most proper time**. Proper time is time on the body's
own clock, reduced by motion through the Lorentz factor. In the weak-field limit this rule gives
Newton's falling (proper-time rate `1 + Φ`, Lagrangian `Φ − v²/2`, so `a = −∇Φ`). The path between
two events at the same place **bulges toward faster clocks**, like a ball thrown up that comes back
down.*

*Our world supplies both ingredients.*

- *A **local clock**: happenings nearby, as in `../quiet_lasts_longer/` and
  `../continuation_choices/`.*
- *A **speed of light**: about 1 edge per round, from `../speed_of_light/`.*

## Construction

**Worlds.** These are exactly the 18 QUIET bodies, 18 FULL bodies and 6 CONTROL worlds of
`../worldline_body/`: the same decapod seeds, directions, random streams and 2,000 half-tiles. They
are regrown deterministically, and every placement round is recorded.

**The now, in each body's frame.**

- Use the angle `φ` measured from the body's direction, restricted to `|φ| ≤ 40°`, in bins of
  **0.5°**.
- The **front radius** `R(φ, r)` is the largest centroid radius among tiles in bin `φ` laid by
  round `r`.
- A test body lives **on the now**. At round `r` it sits at `(φ, R(φ, r))`.

**Clock rate.**

- `h(φ, r)` is the number of tiles laid in rounds `r−1 … r+1`, divided by 3, whose centroid lies
  within **1.5 edges** of the front point `R(φ, r)·e^{iφ}` (in the body's frame).
- This is the local rate of happening, which is our local clock.

**Moving costs time.**

- Moving from `φ` to `φ'` in one round covers the arc `v = R(φ, r)·|φ' − φ|` (in edges).
- The move is allowed only if `v ≤ 1` edge per round (the speed of light).
- The proper time gained in that round is `h(φ, r)·sqrt(1 − v²)`.

**Events.**

- Event A is at round `r₁`, at lateral offset `s₀ = ±3` edges from the body's centre line, using
  `φ₀ = s₀ / R(0, r₁)`.
- `r₁` is the first round at which `R(0, r₁) ≥ 5` edges in CONTROL. The **same** `r₁` and `φ₀`
  are used in every arm for that body.
- Event B is at round `r₁ + Δ`, at the same `φ₀`, with `Δ ∈ {8, 12, 16}` rounds.

**The free path.**

- The path from A to B that maximises total proper time is found exactly, by dynamic programming
  over `φ` bins and rounds. Ties are broken toward the smaller `|φ − φ₀|`.
- Its **excursion** is the lateral displacement (in edges, at the front radius) of the point on the
  path farthest from `φ₀`. It is **signed**: positive means **away from** the body's centre line.
- The **effect** is the excursion in the arm minus the excursion in CONTROL for the same events.
- **Cases:** 18 bodies × 2 sides × 3 durations = **108 per arm**.

## Checks and predictions

- **F0 (asserted).**
  - Every free path found is valid: at most 1 edge per round, starting at A and ending at B.
  - In CONTROL, the mean effect is 0 by construction. As a real check, the mean excursion is
    reported for both sides; the prediction is that it is small, which is not asserted.
- **F1 (a quiet worldline makes bodies fall toward it).** In QUIET, the effect is **> 0** (the path
  bulges **away** from the slow-time worldline, as a thrown ball's path bulges away from the Earth)
  in **at least 65%** of the 108 cases, and the mean effect is > 0. *Confidence about 55%. The
  clock field may be noisy at the scale of single rounds.*
- **F2 (a full worldline does the opposite).** In FULL, the effect is **< 0** (the path bulges
  **toward** the fast highway) in **at least 65%** of cases, and the mean effect is < 0.
  *Confidence about 50%.*

## Reported without prediction

- The mean effect against `Δ`. For Newtonian falling, the bulge scales as `Δ²`.
- The fitted exponent.
- Paths that hit the ±40° window edge.
- Cases where the path is jagged (chasing noise) rather than a single smooth bulge.

## Limits, stated in advance

- One space dimension plus time. There is a preferred frame (the rounds).
- The clock rate is a count of tiles over 3 rounds, so it is noisy. The proper-time formula is
  borrowed from relativity, not derived from the tiling.
- The test body is abstract. Nothing in the tiling is being moved; we ask what path Einstein's rule
  picks in our world's clock field.

## Changes before the first run

*(none yet)*

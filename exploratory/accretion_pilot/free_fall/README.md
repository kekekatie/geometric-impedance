# Does anything fall? Maximal proper time beside a worldline body

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). It includes two logged changes made before the first run.*

**The question.** [`../worldline_body/`](../worldline_body/) found that a quiet worldline makes the now
arrive **late** nearby, and a full one makes it arrive **early**. Is either one gravity, meaning do
bodies fall toward it?

**The rule.** To avoid rigging the answer, we used Einstein's rule: a free body goes between two
events along the path with the **most proper time**.

- Proper time = our local clock (happenings per round at the now), reduced by motion:
  `h·sqrt(1 − v²)`, with our speed of light `c = 1` edge/round.
- In real gravity this rule produces falling: the path between two events at the same place
  **bulges away** from the mass, like a thrown ball rising and coming back down.
- Test paths were found exactly (by dynamic programming), 3 edges to each side of each of 18
  bodies, over 8, 12 and 16 rounds: 108 cases per arm.
- Each path was compared with the same events in the world without the body.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| F0 | every path valid (speed ≤ 1 edge/round, A to B) | yes | ✅ PASS |
| F1 | QUIET: paths bulge **away** (bodies fall **toward** the quiet worldline), ≥ 65% | 31/108 away, 36 toward, 41 no change; mean −0.53 edges | ❌ FAILED (no clear effect) |
| F2 | FULL: paths bulge **toward** the highway (it repels), ≥ 65% | **42/108**; the majority went the other way: **66/108 away**, mean **+1.00** edges | ❌ FAILED (the opposite happened) |

## Why: two different kinds of "slow time"

[`clock_profile_EXPLORATORY.py`](clock_profile_EXPLORATORY.py),
[`results/clock_profile_EXPLORATORY.txt`](results/clock_profile_EXPLORATORY.txt) (post hoc)

Mean happenings per round at the now, by distance from the body's line (18 bodies):

| | 0–1.5 edges | 1.5–3 edges | 3–6 edges |
|---|---|---|---|
| CONTROL | 1.63 | 1.68 | 1.66 |
| QUIET | 0.79 | 1.12 | 1.28 |
| FULL | **0.44** | **0.66** | 1.19 |

- **By the local clock, both bodies slow time nearby, and the full body slows it most.** Near a full
  worldline there is simply **less left to happen**, because the settled past already occupies the
  space. So the now, when it arrives, has less to do there.
- The worldline study measured something else: *when the now arrives*. A full body makes it arrive
  early; a quiet one makes it arrive late. **In our world these two kinds of "slow time" come
  apart.**
  - In Einstein's gravity they are the same thing: clocks run slow and signals arrive late near a
    mass.
  - Here, a full body **speeds the arrival** of the now but **slows the local clock**. A quiet body
    slows both, but its clock-slowing is spread out, with a weak gradient.
- **Einstein's rule follows the local clock.** So the path bulged **away from the full body** in
  66/108 cases: bodies fall **toward fullness**. The bulge grows with duration (+0.65, +0.81, +1.56
  edges at 8, 12, 16 rounds; exponent 1.2, where Newtonian falling would give 2). For the quiet body
  there was no clear effect.

## What it means (plainly)

- Both pre-registered predictions failed, and the second failed in the most interesting way: the
  opposite happened.
- **Katie's accretion hunch comes back.** Judged by arrival time, the gravity-like body was the
  quiet one (`../worldline_body/`). Judged by proper time (the local clock, which is what Einstein's
  rule uses), it's the **full** one: accreted, settled past. Bodies fell toward it, weakly and
  noisily (61% of cases, below our 65% bar).
- **The lesson is the split.** Our world has two notions of "slowness" that real gravity ties
  together: how late the now arrives, and how little happens when it does. Any claim about gravity
  here has to say which one it means.

## Honest limits

- The clock rate is a count of tiles over 3 rounds, so it is noisy:
  - 41 QUIET cases show no change at all;
  - 24 QUIET and 43 FULL paths zig-zag (more than 2 turns);
  - 11 QUIET and 2 FULL paths hit the edge of the ±40° window.
- The attraction toward FULL is partly **geometric**: pre-laid tiles fill part of the neighbourhood,
  so fewer new tiles *can* be laid there. That is what "full" means, but it makes the result less
  surprising.
- The proper-time formula is borrowed from relativity, not derived from the tiling.
- One space dimension plus time. The test body is abstract.

## Files

- `free_fall.py` (`--report` recomputes the report)
- `clock_profile_EXPLORATORY.py`
- `results/cases.jsonl`
- `results/free_fall_report.txt`
- `results/clock_profile_EXPLORATORY.txt`

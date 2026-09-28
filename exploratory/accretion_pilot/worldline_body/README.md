# A worldline body in a decapod world: does a persisting body make a field of time around it?

> **Read with [`../free_fall/`](../free_fall/).** "Slow time" here means the now **arrives late**. By the *local clock* (happenings per round at the now), **both** bodies slow time nearby, the full one most. Under Einstein's maximal-proper-time rule, bodies fell (weakly) toward the **full** worldline. So "the gravity-like property is quietness" below holds only for arrival time.

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md).*

**Katie's insight.** In our growth model, the plane is space and time together, and the growing edge
is the now. So a persisting body isn't a blob. It is a **worldline**, a thread re-made in every
slice of now.

**The set-up.**

- The **decapod world** ([`../decapod_seed/`](../decapod_seed/)) is local (no guesses, no global
  queue) and fully repeatable. So a body's effect can be read off against the identical world
  without it.
- The body is a stripe 1.5 edges wide, running outward from 3 edges.
- 6 decapod worlds × 3 directions = 18 bodies, in two versions:
  - **QUIET:** Gromits work at a quarter speed inside the stripe (low happening density);
  - **FULL:** the stripe is laid in advance (settled past, Katie's "accretion density").
- We measured when the now arrives at points **beside** the stripe (1–6 edges away, at radii 5–7)
  and on the **far** side of the world, compared with the identical world without a body.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| W0 | no guesses or jams; same tiling as CONTROL; all points covered | no guesses or jams ✓; but see below | ❌ FAIL (by the letter) |
| W1 | a quiet worldline has a field: near delay > 0 in ≥ 80% | **17/18** | ✅ HELD |
| W2 | it fades with distance (Δ(1) > Δ(6) in ≥ 70%), and the far side is untouched (median \|Δ_far\| ≤ 1) | **16/18**; far = **0.00 in all 18** | ✅ HELD |
| W3 | fullness is the opposite: the now arrives *early* near a full worldline (≥ 80%) | **18/18** | ✅ HELD |

**Why W0 failed, and why it doesn't undermine the rest.** Two parts of the check failed.

1. **Tiles missing from CONTROL.** In 14 of the 18 FULL bodies, some laid tiles were not in
   CONTROL's 3,500-tile tiling. A post-hoc check ([`w0_check_EXPLORATORY.py`](w0_check_EXPLORATORY.py),
   [`results/w0_check_EXPLORATORY.txt`](results/w0_check_EXPLORATORY.txt)) shows why:
   - every such tile lies **≥ 11.9 edges out**, where FULL raced ahead along its pre-laid stripe
     into regions CONTROL never grew (the sample points lie within 7.3 edges);
   - **none** conflicts with a CONTROL tile.

   So wherever both worlds exist they are the same tiling, but the check as written could not
   confirm it.
2. **Uncovered points.** 5 sample points at radius 7, in 4 FULL bodies, were never covered within
   2,000 tiles. FULL spends its tiles racing outward along the stripe. Those points are left out of
   the means.

## The profiles (mean over 18 bodies; delay in rounds; + = the now arrives late)

| distance from the worldline d (edges) | 1 | 2 | 3 | 4 | 6 | far side |
|---|---|---|---|---|---|---|
| **QUIET** (slow happening) | **+3.9** | **+4.1** | +2.0 | +1.7 | +0.8 | **0.00** |
| **FULL** (settled past) | **−16.2** | **−13.5** | −9.3 | −6.6 | −2.8 | −0.13 |

The near delay (d ≤ 2) also changes with radius, i.e. further along the worldline and later in
time:

- QUIET: +2.8 at radius 5, +3.4 at radius 6, **+5.9** at radius 7;
- FULL: −11.6, −14.1, **−18.8** at the same radii.

## What it means (plainly)

- **A quiet worldline makes a field of slow time around it.** Clocks near it (arrival of the now)
  run late. The lateness **fades with distance**, and the far side of the world is **exactly**
  unaffected: 0.00 rounds in every body. The effect is purely local.
- **The field grows along the worldline.** The further out (later), the bigger the lag. Clocks near
  a quiet body fall further behind as time goes on. That is the shape of gravitational time
  dilation: a clock near a mass loses more and more time relative to one far away.
- **Fullness does the opposite, strongly.** A pre-laid (settled) worldline acts as a **highway**. The
  now arrives up to 16 rounds *early* beside it, again fading with distance and untouched far away.
- **Katie's question, quietness or fullness, has an answer in this model.** The gravity-like
  property is **quietness** (low happening density), not fullness (accretion). Accreted structure
  speeds the now up, the opposite of gravity. Happening density was the right angle after all.
- *A speculative rhyme (not tested):* in one space dimension, Newtonian gravity's potential grows
  **linearly** with distance from a mass. FULL's profile falls off nearly linearly (−16, −14, −9,
  −7, −3). QUIET's is noisier and steeper near the body. Whether either follows a law is for a
  proper test.

## Limits

- One tiling family and 6 decapod worlds whose fronts aren't round.
- One stripe width and one throttle strength.
- One space dimension plus time: delay only, no bending.
- "Field" is an analogy: a pattern in when the now arrives, not a force on anything. Nothing yet
  *moves* in response to it; a test body that falls would be a different study.

## Files

- `worldline_body.py` (`--report` recomputes the report)
- `w0_check_EXPLORATORY.py`
- `results/runs.jsonl`
- `results/controls.json`
- `results/worldline_body_report.txt`
- `results/w0_check_EXPLORATORY.txt`

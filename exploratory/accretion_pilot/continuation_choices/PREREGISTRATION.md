# Does quietness only give more time, or does it change the choices? Pre-registration

*Written and committed **before** any code for this study existed. It is built on the repairs from
Astra's review of [`../quiet_lasts_longer/`](../quiet_lasts_longer/) (see "Astra's checks" there):*

- *The old "soft" test measured the open edge, never a rearrangement. Enclosed regions had exactly
  one filling.*
- *The old jams came from a scheduler that guessed while forced moves were waiting.*
- *Uncertainty must be judged by run, not by probe.*

*Astra's question: **does quietness only prolong the opportunity, or does it also change which
continuations are possible?***

## Construction

The tiling is grown from one genuine seed patch (radius 3 edges) with the full Penrose matching rules
and the corrected vertex check (`../soft_zone`). Growth uses a ring of Gromits with a **WAIT
scheduler**:

- Each round, every frontier edge with exactly one legal candidate is **forced**.
- Each forced placement is carried out, subject to the arm's throttle.
- **A guess is made only when there are no forced moves anywhere.** The guess is at the innermost
  frontier edge, among its candidates, using the run's random stream.
- If forced moves exist but the throttle skipped them all, the round passes idle.
- If forced moves exist but none is legal, the run is marked `STUCK`. A frontier edge with no
  candidate marks it `JAM`.

**Arms** (8 runs each; seeds `20261010 + k`, the same seeds in every arm):

- **FAST:** no throttle.
- **HALF:** the left half (`Re z < 0`) is quiet. Each forced placement there happens with
  probability 0.25.
- **SLOW:** the whole plane is throttled at 0.25. This is the uniform-slowdown control.

Every arm grows **1,000** half-tiles. The round in which each tile is laid is recorded, and so are
the rounds in which guesses are made.

### Forcing closure (what the Gromits will do without guessing)

Under WAIT, no guess happens until every forced move is exhausted. So the **closure** of the
snapshot at round `r` is the patch just before the next guess after `r`: every tile laid before
that guess round. If no guess follows, the closure is the final patch. This is exactly what the
growth rules already determine at `r`, with no further choice needed.

### Probes and their explicit target region

A probe is the centroid `c` of a final-patch tile. It must meet all of these:

- `|c| ≥ 4.5` edges;
- `|Re c| ≥ 1.5` edges;
- at least 3 edges from the final frontier.

Up to 8 probes per half per run are chosen at random, at least 2.4 edges apart.

- **Target region:** the probe's **17 sample points**:
  - `c` itself;
  - 6 points at 0.4 edges from `c`;
  - 10 points at 0.8 edges from `c`.
  - A fixed tiny offset keeps the points off tile edges.
- A region is **covered** when every sample point lies inside some tile.
- **Completion from a snapshot.** Starting from the snapshot, add tiles until every sample point is
  covered.
  - Only tiles with centroids within **1.8 edges** of `c` may be added.
  - Each step fills a forced frontier edge within reach if there is one. Otherwise it makes a random
    choice at the nearest frontier edge that has candidates.
  - At most 80 tiles are added.
  - A completion **counts** only if all 17 points end up covered and every frontier edge within
    reach still has at least one legal candidate. This one-step look-ahead rules out dead ends.
- **Signature:** the tile covering each sample point. Two completions differ if their signatures
  differ. Unlike the old test, **a completion must cover the same explicit target**, so adding area
  elsewhere cannot count.
- **Genuine alternatives at round `r`:** the distinct signatures, from 16 attempts, that agree with
  the closure at `r`. Agreeing means:
  - every sample point the closure covers is covered by the same tile;
  - no added tile overlaps a closure tile it isn't equal to (checked by centroids).

### Phases of a probe

- **Arrival** `a`: the first round in which a tile with its centroid within 1.8 edges of `c` is laid.
- **Determined** `d`: the first round at which the closure covers all 17 points. From then on the
  outcome is fixed by what already exists; it just hasn't been laid yet.
- **Covered** `v`: the first round in which the actual growth covers all 17 points.
- The two intervals:
  - **T_U** (undetermined time) = `max(0, d − a)`;
  - **T_D** (determined but not yet laid) = `v − max(a, d)`.
- **Choices** = the largest number of genuine alternatives at any round in `[a, d)`. It is 1 if
  `T_U = 0`.
- Rounds `a … v−1` are tested (16 attempts each).

## Predictions

Every ratio below is a **ratio of means**. Its uncertainty is a **bootstrap over runs** (10,000
resamples, seed 2031), never over probes.

- **Z1 (asserted).** No arm has any `JAM` or `STUCK` run.
- **Z2 (asserted: the past is fixed).**
  - In the final patch, remove every tile that covers a sample point or has its centroid within
    0.8 edges of `c`, then complete (16 attempts).
  - In at least **99%** of probes, every successful completion gives the actual signature. At least
    one attempt must succeed.
- **P1 (quietness prolongs).** In HALF, quiet-half T_D is **≥ 1.5×** busy-half T_D, and quiet exceeds
  busy in **≥ 7 of 8** runs (per-run means). *Confidence about 75%.*
- **P2 (the undetermined time is shared).**
  - Under WAIT, a guess waits for the *whole* plane to settle, so the quiet half holds everyone back
    equally.
  - Prediction: in HALF, the 95% bootstrap interval of the quiet/busy T_U ratio lies within
    **[0.67, 1.5]**. *Confidence about 40%.*
- **P3 (quietness does not change the choices).**
  - In HALF, over probes with `T_U > 0`, the 95% bootstrap interval of the quiet/busy ratio of mean
    choices lies within **[0.75, 1.33]**. *Confidence about 55%.*
  - Reasoning: under WAIT, the state at every guess is the forcing closure. That closure does not
    depend on the order or pace of forced placements, so the menu of continuations should not
    depend on pace either.
  - If either half has fewer than 10 probes with `T_U > 0`, P3 is reported as **NOT TESTABLE**.
- **P4 (the uniform slowdown only stretches the clock).**
  - SLOW/FAST ratio of mean T_D is **≥ 1.5**, **and**
  - the 95% bootstrap interval of the SLOW/FAST ratio of mean choices (probes with `T_U > 0`) lies
    within **[0.75, 1.33]**.
  - The runs are unpaired: the tilings differ.
  - The same 10-probe rule applies.
  - *Confidence about 55%.*

## Reported without prediction

- The fraction of probes with `T_U > 0`, per arm and half.
- The distributions of T_U, T_D and choices.
- **Apparent choices in the determined phase:** the largest number of *local* signatures (not
  filtered by the closure) at any round in `[d, v)`. These are options that look open locally but
  are already settled by forcing elsewhere.
- Local-clock versions of T_U and T_D: tiles laid within 2 edges of `c` during each interval.
- **Astra's exact idle-round control, computed analytically.** Stretching the FAST arm's clock by a
  factor `k` would multiply its T_U and T_D by `k` and leave choices unchanged. It is reported with
  `k` = FAST happening density / SLOW happening density, as a reference line for SLOW.
- Guesses per run, and idle rounds per run.

## Limits, stated in advance

- One tiling family, one throttle strength, one target size.
- "Determined" means determined by the Gromits' **local forcing rule** (exactly one candidate). A
  tile may be logically implied by longer chains before it is locally forced. So T_U measures
  "undetermined *to the growth process*", not undetermined in principle.
- Genuine alternatives are sampled (16 attempts) with a one-step look-ahead. Some may be dead ends
  further on, and some real alternatives may be missed.
- The HALF arm's halves share one patch and one clock, so they are not independent regions.

## Changes before the first run

*(none yet)*

# Does the now last longer where it is quiet? Pre-registration

*Written and committed **before** any code for this study existed. In the happening-density study
([`../happening_density/`](../happening_density/)) the now had the **same width in space** in a quiet
(throttled) half and a busy half: H1 held. Our prediction that it lasts longer in **time** was tested
badly, using the age of soft holes, and it failed (H2). An exploratory look suggested that the back of
the soft band is about 3× older in the quiet half. Katie asked for a proper test.*

*The earlier measure took one snapshot at the end of growth and asked how old the soft spots were.
This study follows **fixed spots through time** instead. It watches each spot from the moment it is
fully laid until it hardens, and counts how long it stayed changeable. The count is kept on two
clocks:*

- *the **universal clock**: rounds of growth, which are the same everywhere;*
- *a **local clock**: the number of tiles laid near the spot, which is Katie's happening density.*

*The picture being tested: **the now is a place of fixed width that moves at the local pace.** If so,
a quiet spot stays in the now for more universal rounds. Measured in its own local happenings,
though, it stays for the same amount.*

## Construction

The growth is exactly as in `../happening_density/happening_density.py` (imported):

- ring-of-Gromits growth with full matching rules and the corrected vertex check;
- the left half (`Re z < 0`) is throttled: each forced placement there happens with probability 0.25;
- one guess at the innermost frontier edge is made when nothing is placed.

Changes from that study:

- Growth adds **1,000** half-tiles, not 500, so that probes have room to harden behind the front.
- **Runs.** Seeds `20261001 + k`, for k = 0, 1, 2, …, until **8 runs complete without a jam**, or 24
  seeds have been used. Jammed runs are counted and reported, with their locations, but they
  contribute no probes.
- Every tile's placement round is recorded. The **snapshot** at round `r` is every tile laid at or
  before round `r`.

**Probes.** Each probe is the centroid `c` of a tile in the final patch. It must meet all of these:

- `|c| ≥ 4.5` edges, so its disc contains no seed tiles;
- `|Re c| ≥ 1.5` edges, away from the quiet/busy line;
- at least **3** edges from the final frontier (the nearest frontier-edge midpoint).

Up to **8 probes per half per run** are chosen at random, with centres at least `2ρ` apart.

- **Birth** `b`: the round in which the last tile of the probe's disc was laid. The disc is the tiles
  of the final patch whose centroids lie within `ρ = 1.2` edges of `c`.
- **Softness test at round `r`.** Take the snapshot at `r` and remove its tiles within `ρ` of `c`.
  Then re-lay the hole with the soft-zone refill: 8 attempts, seeded deterministically. The probe is
  **soft** at `r` if some attempt gives a complete legal refill that differs from the original. This
  is the same test as in the soft-zone and happening-density studies.
  - Check Z, asserted: the original tiles are a legal refill of the snapshot.
- **Schedule.** Test at `r = b, b+1, b+2, …`. Stop after **4 consecutive hard** results, or at the
  final round.
- **Lifetime in rounds**, `L_rounds`: (the last round at which the probe tested soft) − `b` + 1. It is
  0 if the probe was never soft.
- **Lifetime in local happenings**, `L_local`: the number of tiles laid within **2 edges** of `c` in
  rounds `b+1 … (the last soft round)`. It is 0 if the probe was never soft.

## Predictions

- **Q0 (the manipulation, asserted).** Over the completed runs, the quiet half's happening density
  (tiles placed per round) is below 0.6 times the busy half's.
- **Q1 (the now lasts longer where quiet, on the universal clock).** The mean `L_rounds` over
  quiet-half probes is at least **1.5×** the mean over busy-half probes. *Confidence about 55%.*
- **Q2 (but not on the local clock).** The ratio of mean `L_local` (quiet / busy) lies between
  **0.67 and 1.5**. *Confidence about 55%.*
- **Q3 (the shape of the result).** Q1 and Q2 hold together. This is the full picture: "a fixed-width
  now moving at the local pace". *Confidence about 35%.*

A one-sided permutation test for Q1 is also reported: probe labels are shuffled between the halves,
10,000 times, seed 2029. It is reported, not used as a pass/fail criterion.

## Reported without prediction

- The fraction of probes that were soft at birth, per half.
- The distribution of `L_rounds`, per half. Probes still soft at the final round are counted as
  censored.
- The local front speed per half: the change in mean frontier radius per round over the growth, in
  edges per round. Also, whether `L_rounds` × speed is similar in the two halves. That product is the
  "width in space" recovered from time.
- **Jams:** how many seeds jammed, and where, compared with 3/8 in the happening-density study. This
  is a replication count for the "unequal pace jams" surprise. It is not a test.

## Limits, stated in advance

- One tiling family, one throttle strength, and one hole size (ρ = 1.2 edges).
- Softness is sampled with 8 refills, so a probe can flicker between soft and hard. The 4-consecutive
  stopping rule and "last soft round" are chosen with this in mind.
- The phase before birth, when a spot is only partly laid, is not measured.
- The local clock counts tiles within a fixed radius. Once the front moves on, that count stops
  growing. So Q2 partly restates "the now is a place", and I say so in advance.

## Changes before the first run

*(none yet)*

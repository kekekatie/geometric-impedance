# More of the zip, or a faster zip?

*Pre-registration, written and committed before any code for this study exists. This is Astra's
suggested next test after `speed_of_now/`.*

## Where this comes from

In `speed_of_now/`, at a two-way choice, the option that keeps the **smaller** piece of the wiggle room
F usually unlocks far more forced growth. Per slice, it laid about twice the tiles. Astra pointed out
that "tiles per slice" mixes two different things:

- **more of the front is active** (more of the zip is running), or
- **each active part advances faster** (the zip runs faster).

Astra also pointed out that most fast bursts never ended within 40 slices. So "does it even out?"
needs a window that starts **after both first bursts have ended**.

`speed_of_light/` gives a prior: forced influence travels along the now at about 1 edge per slice, and
the now moves outward at about 0.3 edges per slice, roughly steadily. If that holds here, both futures
should run at the same speed, and the difference should be in how much of the front is running.

## Words

- **Choice, sibling, burst, piece kept:** as in `speed_of_now/`. A **live, unequal** choice has both
  pieces > 0 and pieces differing by at least 0.01.
- **Slice s of a sibling:** the patient scheduler (forced first; a guess only when nothing is forced).
  Slice 0 is the chosen tile.
- **Active boundary at slice s:** the total length (in edges) of the frontier edges, as they were at
  the start of slice s, that receive a tile during slice s.
- **Activity per active length:** tiles placed in slice s ÷ active boundary at slice s.
- **Outward advance at slice s:** the median distance (in edges) from the **base patch** (the patch at
  the choice) of the tiles placed in slice s, minus the same at slice s − 1. This is reported per
  slice; per sibling we use its mean over the matched slices.
- **Matched slices:** slices 1…m, where m is the smaller of the two siblings' burst lengths (both
  still forced-only). A pair needs m ≥ 3.
- **Relaxation window:** the 20 slices after the **later** of the two first bursts ends. Measured as
  **active share**: active boundary ÷ total frontier length, averaged over the window. This allows for
  the fast sibling being bigger by then.

## Set-up

- **24 fresh ordinary worlds**, with seed centres at entries 120–143 of the 18° wedge (0–119 were used
  before). Random seed 20261170 + world.
- Each main world grows with the patient scheduler to 1500 added tiles.
- At each live, unequal two-way choice, both siblings grow until both first bursts have ended plus 20
  slices, with a cap of **100 slices**. Pairs that never get there are reported, not dropped silently.
- **Unit of analysis: distinct situations.** Choices whose whole base patch is identical relative to
  the choice point (translations only) count once. The random stream for the siblings' guesses comes
  from that geometry, so identical situations really have identical futures.

## Predictions (fixed now)

**A1: More of the zip.** Over matched slices, the smaller-piece sibling has the larger mean active
boundary in at least 70% of pairs. Confidence about 75%.

**A2: Not a faster zip (density).** Over matched slices, the ratio of mean activity per active length
(smaller-piece sibling ÷ larger-piece sibling) lies between 0.8 and 1.25 in at least 70% of pairs.
Confidence about 60%.

**A3: Not a faster zip (outward).** Over matched slices, the ratio of mean outward advance
(smaller ÷ larger) lies between 0.8 and 1.25 in at least 60% of pairs. Confidence about 55%: the
"speed of light" prior says yes, but outward advance in short windows may be noisy.

**A4: It evens out afterwards.** Among pairs that reach a full relaxation window, the ratio of active
shares (smaller ÷ larger) lies between 0.8 and 1.25 in at least 60%. Confidence about 50%.

## Reported, not tested

- How many pairs reach the relaxation window, and how many hit the 100-slice cap first.
- Burst sizes and lengths (an independent replication of `speed_of_now/` S1, without the 40-slice cap).
- The active share during the burst, and its slice-by-slice profile.
- The same measures counted per choice (not per distinct situation).

## Limits I already know

- "Active boundary" counts edges that got a tile, not the edges that became *forced*. Those two can
  differ when a forced tile fails the legality check.
- Outward distance is measured from the base patch, so tiles that fill notches in the old boundary
  count as zero advance.
- Ordinary worlds only; one scheduler.

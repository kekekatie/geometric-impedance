# Causally honest local nows: patience that only uses the past light cone

*A third pre-registration for `local_nows/`, written and committed before its code (2026-10-21).*

## Why

`patience.py` found that a local now with R = 24 edges of quiet (no forced activity within 24 edges
*right now*) kept 20/24 worlds whole, against 2/24 bad for the global clock. But influence travels at
about 1 edge per slice (`speed_of_light/`: the largest step was 1.05 edges per round). So knowing
what is happening 24 edges away *right now* is **faster-than-light knowledge**.

A **causally honest** local now may only use events in its **past light cone**: forced activity at
distance d from it, k slices ago, with d ≤ c·k + r0.

There is a catch. A burst moving *towards* a region at about the speed of light stays outside that
region's past cone until it arrives. So honest patience may be unable to anticipate incoming forced
growth. If so, Penrose rules contain a hidden global constraint (the shared F) that honest local nows
cannot respect.

## Rule CONE(H)

The same as `local_nows.py`'s LOCAL scheduler, with one change. A frontier edge with ≥ 2 candidates
may make a choice only if no forced tile was placed within distance c·k + r0 of it in slice s − k,
for every k = 0, 1, …, H.

- c = 1.05 edges per slice, r0 = 1 edge.
- Simultaneous choices are at least 6 edges apart, as in the R = 3 run.
- H = 12, 24 and 48 slices; the same 24 seeds.
- **Bad** = jammed or dead at the end (F empty).

## Predictions (fixed now)

**K1: A deeper past helps.** The bad count never increases from H = 12 to 24 to 48. Confidence about
60%.

**K2: Honest patience is not enough.** CONE(48) is clearly worse than the faster-than-light-informed
R = 24 rule: at least 8 of 24 worlds bad (R = 24 had 4, GLOBAL 2). Confidence about 60%.

## Reported

- Median slices, tiles and choices for each H, and the death-to-jam lead.
- How often a CONE world's fatal choice came from simultaneous choices vs a single choice.
  (Recorded roughly: the number of choices made in the slice where F first became empty.)

## Limits

- The cone uses straight-line distance and one speed c. Activity that travels along the front may
  move differently.
- r0 = 1 edge and the 6-edge spacing are fixed by hand.
- 24 seeds.

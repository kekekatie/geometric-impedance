# How patient must a local now be?

*A second pre-registration for `local_nows/`, written and committed before its code. It follows
`local_nows.py`'s result: with a radius of patience R = 3 edges, all 24 LOCAL worlds jammed, against
2/24 GLOBAL.*

## Idea

Influence spreads along the front at about one edge per slice (`speed_of_light/`). A local now that
chooses while forced activity is still nearby often picks an option that the arriving forced tiles
rule out. So patience should help: **choose only when no forced activity is within R edges**. If some
finite R keeps worlds coherent, then local nows can work without a global clock, as long as they
respect a light-cone-like patience.

## Set-up

- The same 24 seeds and the same LOCAL rule as `local_nows.py`, with R = **6, 12 and 24** edges.
  Choices are spaced at least 2R apart.
- The R = 3 and GLOBAL results already recorded serve as the two ends of the scale.
- **Bad** = jammed or dead at the end (F empty).

## Predictions (fixed now)

**Q1: Patience helps, steadily.** Counting bad worlds out of 24, the counts never increase as R grows
(3 → 6 → 12 → 24), and R = 24 has fewer bad worlds than R = 3 (24/24). Confidence about 75%.

**Q2: Enough patience matches the global clock.** At R = 24, at most 4/24 worlds are bad (GLOBAL had
2/24). Confidence about 35%. Forced bursts run a long way along the front, so even 24 edges of quiet
may not be enough.

## Reported

- For each R: the median slices and tiles reached, choices per world, and the most choices made in a
  single slice.
- The death-to-jam lead for each R.

## Limits

- "Within R edges" is straight-line distance, not distance along the front.
- R is a fixed radius, not a true causal cone that grows with time.
- Same 24 seeds.

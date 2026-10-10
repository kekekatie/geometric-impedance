# Does influence travel as fast as the thread is made?

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). Three changes were made before the first run, and they
are recorded there: the decided family is chosen per sibling, and the seed centres come from one
symmetry wedge (two steps).*

**Astra's guiding thought:** *perhaps the process that makes the next piece of reality definite is also
the process that carries influence through it.* `../gold_thread/` showed that a choice mostly decides
**one ribbon** lying along the now.

**The test.** After each choice:

- Is the difference between the two alternative presents (the "influence") **led by** that ribbon?
- Does the difference spread **as fast as** that ribbon is being laid?

**The set-up.**

- 24 ordinary worlds, each started from a different, symmetry-free spot in the reference tiling.
- They gave 24 distinct histories and 65 distinct choices, but only about 27 distinct local situations,
  since the same configuration recurs in different places.
- At each choice, both siblings were grown up to 12 slices.

> **Corrections after Astra's review (2026-10-10):**
>
> 1. **"Speed of light reconfirmed" was too strong.** The exploratory reach speed (0.73) falls *within the range* measured in `../speed_of_light/`. That is consistency with an earlier propagation measurement, not evidence of a universal speed.
> 2. **Corner-hopping is only one candidate route.** Influence could also pass through other crossing ribbons, via chains of shared-edge constraints. Leaving the selected ribbon doesn't identify the route.
> 3. **"About 27 distinct local situations" is a rough proxy.** It groups choices by the two siblings' tile counts, and different configurations can give the same counts. It is not structural deduplication.
>
> The broad guiding thought remains *compatible* with the result, but surviving the narrower test doesn't confirm it.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| D1 | the leading edge of the difference lies on the decided ribbon (≥ 70%) | **53%** (1,566 / 2,948) | ❌ FAILED |
| D2 | the difference spreads as fast as the ribbon is laid (ratio 0.8–1.25 in ≥ 70%) | 1 / 14; ratios **1.04–2.82**, mostly 2.82 | ❌ FAILED |
| D3 | the spreading speed is the speed of light (median 0.67–1.13 edges/slice) | median **0.45** (half-width) | ❌ FAILED (see below) |

Also reported:

- the ribbon's spreading (half-width) speed, median 0.34;
- forward leakage, **0.06** edges per slice: the difference stays a thin strip along the now;
- on average 64% of the difference lies on the decided ribbon.

## How come? (exploratory: [`reach_EXPLORATORY.py`](reach_EXPLORATORY.py))

**D3 was partly my measuring mistake.** I pre-registered half the strip's *width*. `../speed_of_light/`
measured how far the difference had *reached* from the choice point. Re-measured as reach, on the same
worlds:

- the difference reaches out at **0.73 edges per slice** (quartiles 0.71–0.78), within the
  speed-of-light range found before (0.67–1.13);
- the decided ribbon reaches out at only **0.42**;
- so **influence outruns the thread by about 1.7 times**, whichever way it is measured.

D3 stays failed as registered. The reach speed is consistent with the earlier measurement (not, by itself, evidence of a universal speed).

## What it means (plainly)

- **Influence is not carried by the decided thread alone. It runs ahead of it.**
  - A choice decides which way one ribbon zig-zags along the now.
  - The *consequences* of that decision show up further along the front, at about the speed of light,
    before the ribbon itself has been laid there.
  - So the news of the decision travels faster than the thread being made.
- **One candidate route is the vertex rules.** The matching rules act where tiles meet at a corner, not
  only across shared edges. Tiles that share only a corner are *not* ribbon-neighbours. So the forcing
  can pass information to places off the decided ribbon, ahead of it. (A reading, not tested here.)
- **For Astra's guiding thought:**
  - In its simple form ("one thread is both what is made definite and what carries influence"), it is
    **not supported**.
  - In a broader form it survives: the forcing along the front makes things definite *and* carries the
    influence, at about the speed of light. But that is the whole front's forcing, not one thread.
- **The difference hugs the now.** Forward leakage is only 0.06 edges per slice, against about 0.73
  sideways. A choice's consequences race along the present and hardly reach forward at all within 12
  slices.

## Limits

- 65 distinct choices, but only about 27 distinct local situations, so the effective sample is smaller
  than it looks.
- At most 12 slices.
- The decided ribbon is identified by a simple rule (most nearly perpendicular to the front), which may
  misidentify it on curved fronts.
- One world jammed (its earlier choices are included).
- "Influence" means the difference between alternative presents, not a signal within one world.

## Files

- `thread_influence.py`: the study
- `reach_EXPLORATORY.py`: the reach re-measure
- `results/thread_influence_report.txt`, `results/run.log`, `results/worlds.json`
- `results/reach_EXPLORATORY.txt`, `results/reach_run.log`

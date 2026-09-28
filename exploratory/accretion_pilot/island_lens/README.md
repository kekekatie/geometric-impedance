# Door 2: does a quiet island bend the now like gravity? Quietness vs fullness

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). It includes one logged change before the first run: the
growth size was raised so that every sample point is reached.*

## What was done

- The same reference tiling is grown in every arm: oracle guesses and the patient scheduler.
- **CONTROL:** no island.
- **QUIET:** a disc of radius 2 edges, 6.5 edges out, where the Gromits act at a quarter of the rate.
- **FULL:** the same disc **pre-laid** as settled past, inert until the growth reaches it.
- 8 island directions per arm.
- We compare when the now arrives at points **behind** the island, **beside** it, and on the **far**
  side of the world, against CONTROL at the same points.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| G0 | no jams, all tiles in the reference tiling, all points reached | yes | ✅ PASS |
| G1 | a quiet island delays the now behind it (local delay > 0 in ≥ 7/8, mean ≥ 2) | 6/8, mean +67.9 (two huge runs) | ❌ FAILED |
| G2 | a quiet island focuses, like a lens (lens > 0 in ≥ 7/8) | 4/8 | ❌ FAILED |
| G3 | a full island makes the now arrive *earlier* behind it (≥ 7/8) | 1/8 | ❌ FAILED |

## What happened: the now in this world is not a smooth front

[`why_EXPLORATORY.py`](why_EXPLORATORY.py),
[`results/why_EXPLORATORY.txt`](results/why_EXPLORATORY.txt) (post hoc)

The delays were not small local dents. They were either about the same everywhere or enormous (+150,
+270, even −134 rounds), and **uniform across a whole region**. Looking at *when* each part of the
world is laid shows why:

- **The world grows sector by sector.** In CONTROL, the round in which the now reaches 10–12 edges
  from the centre ranges from **98 to 343**, depending on direction.
  - The patient scheduler makes one decision at a time, at the innermost open edge.
  - Each decision unlocks a burst of forced growth in one sector, while the other sectors wait their
    turn.
- **An island reshuffles the queue; it does not dent a front.**
  - In QUIET run 2, the sector at 90° is reached at round 345 instead of 196, while the sector at
    180° comes *earlier* (247 instead of 269).
  - In other runs, the order barely changes and everything is shifted by a similar 8–30 rounds.
  - FULL islands reshuffle it too, sometimes drastically (FULL run 0).
- So the arrival of the now is governed by a **global queue of decisions**, not by local geometry.
  There is no smooth front for an island to bend, and a lens effect of a round or two is swamped.

## What it means (plainly)

- **With a single, global decision-maker, there is no local geometry of time.** Everything waits in
  one queue. A quiet or full region doesn't curve the time around it. It changes the *order of the
  queue*, which can shift distant places by hundreds of rounds in either direction.
- This echoes [`../continuation_choices/`](../continuation_choices/), where "deciding is shared". A
  shared decision moment is exactly what prevents gravity-like *local* effects.
- **The gravity question needs local deciders.** Suppose each region decided on its own when
  nothing is forced *within some horizon* around it, instead of waiting for the whole world. Then
  time could get a local geometry, and an island might then delay or bend it.
  - The horizon size would be a natural new constant, perhaps tied to the ~1 edge/round speed of
    light from [`../speed_of_light/`](../speed_of_light/).
  - Care is needed: the earlier "impatient" local guessing caused jams (see "Astra's checks" in
    `../quiet_lasts_longer/`).
- **Quiet vs full is not settled.** Both islands reshuffled the queue, and neither shows a local
  signature here.

## Limits

- One tiling, one island size and distance, and oracle guesses.
- The CONTROL arm is a single history.
- The post-hoc look covers only four histories.

## Files

- `island_lens.py` (`--summary` recomputes the report)
- `results/runs.jsonl`
- `results/island_lens_report.txt`
- `why_EXPLORATORY.py`
- `results/why_EXPLORATORY.txt`

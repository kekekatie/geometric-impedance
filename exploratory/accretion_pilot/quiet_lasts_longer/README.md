# Does the now last longer where it is quiet?

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). It includes one logged change, made before the first real
run.*

It follows [`../happening_density/`](../happening_density/). There, the now had the **same width in
space** in a quiet half and a busy half. An exploratory hint suggested that it might **last longer**
in the quiet half. Katie asked for a proper test.

## What was done

- The tiling grows from one seed. The left half is made quiet: its Gromits act only a quarter of the
  time. The growth adds 1,000 half-tiles.
- In each run, 16 fixed spots (probes) are chosen, up to 8 per half. Each is followed through time,
  from the round the front first reaches it until it can no longer be laid differently (it
  **hardens**).
- At every round, the spot's disc is removed and re-laid 8 ways. The spot is **soft** (still in the
  now) if some re-laying differs from what was there.
- **Lifetime** is how long a spot stayed soft. It is counted on two clocks:
  - **universal:** rounds of growth, the same everywhere;
  - **local:** tiles laid within 2 edges of the spot, which is Katie's happening density.
- 12 seeds were needed to get 8 completed runs, because 4 jammed.
- This gave 55 quiet probes and 64 busy probes.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| Q0 | the quiet half's activity is < 0.6× the busy half's (manipulation check) | **0.69×** | ❌ FAIL |
| Q1 | the now lasts ≥ 1.5× longer where quiet, in rounds | **2.03×** (34.8 vs 17.1 rounds; permutation p = 0.0001) | ✅ HELD |
| Q2 | …but about the same on the local clock (ratio 0.67–1.5) | **1.33×** (16.1 vs 12.1 local happenings) | ✅ HELD |
| Q3 | Q1 and Q2 together | both | ✅ HELD |

**The manipulation check failed.** Over 1,000 tiles, the quiet half partly catches up: the busy half
keeps forcing tiles across the line. The quiet half was still quieter, but less than the
pre-registered strength (0.69, where < 0.6 was needed). A weaker contrast should make Q1 *harder* to
pass, not easier. Still, by the letter, the study ran under a weaker condition than planned, and I say
so.

## What it means (plainly)

- **The now lasts about twice as long in the quiet half, counted in universal rounds.** This is clear
  and far from chance (p = 0.0001).
- **Counted on the local clock, the difference mostly disappears.** A spot hardens after roughly the
  same number of nearby happenings: about 16 in the quiet half, 12 in the busy half. The ratio of 1.33
  is inside the predicted range, but not by much.
- So the picture holds, roughly: **the now is a place of about the same width everywhere. A spot
  stays in it until enough has happened around it. Where little happens, that takes longer.**

### Exploratory (post hoc, not pre-registered)

[`results/fill_vs_after_EXPLORATORY.txt`](results/fill_vs_after_EXPLORATORY.txt)

- **Almost all of a spot's time in the now is the time it takes to be laid.** From the first tile of
  its disc until the disc is complete took 38.5 rounds on average in the quiet half and 18.5 in the
  busy half.
- Once complete, a spot hardens almost at once in both halves: on average 1.5 and 0.7 extra rounds.
- So "the now lasts longer where quiet" mostly means **a quiet place takes longer to finish
  happening, and it stays open until it has.**
- The throttle makes it slower to lay tiles there, so this is partly built into the setup. The
  non-trivial part is Q2: finishing takes about the same *number of happenings* either way.
- **Spatial width recovered from time** (lifetime × front speed): 1.84 edges in the quiet half, 1.14 in
  the busy half. That these are similar in size agrees with the soft-zone width of ~2 edges. They are
  not equal. A quiet spot lasts somewhat longer than the slower front alone explains (lifetime ratio
  2.03, against a speed ratio of 1/0.79 ≈ 1.27). "Front speed" here is a crude mean radius, though, so
  I would not lean on this.

### The jams: a correction to the last study's surprise

[`results/jam_spots_EXPLORATORY.txt`](results/jam_spots_EXPLORATORY.txt)

- 4 of 12 seeds jammed, similar to the 3 of 8 before. But all 7 jams across both studies sit at
  **the same two or three spots**, together with one mirror image of them.
- Those spots are on the **rim of the seed patch**, on the quiet side, within 2 edges of the
  quiet/busy line.
- So "unequal pace jams" is too broad. It is better stated as: *particular weak spots on the seed's
  rim break when the quiet/busy line runs beside them.* That is still interesting, because
  equal-paced growth never breaks there (0/42). But it is about specific places, not a general law.

## Limits

- One tiling family, one throttle strength, one hole size.
- The manipulation was weaker than pre-registered.
- The local clock partly restates "the now is a place". This was said in advance.
- Softness is sampled with 8 refills.

## Files

- `quiet_lasts_longer.py` (`--summary` recomputes the report)
- `results/runs.jsonl`, with every probe's full soft/hard sequence
- `results/quiet_lasts_longer_report.txt`
- the two `_EXPLORATORY` files

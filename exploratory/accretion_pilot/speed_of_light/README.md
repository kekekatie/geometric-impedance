# The speed of light in a Gromit world

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). This is door 1 of the "relativity and gravity" play.*

## What was done

- The tiling is grown as usual: FAST arm, patient scheduler, 1,000 half-tiles, 12 seeds.
- For every guess the growth made, a **twin history** replays everything exactly but takes the other
  option at that one guess.
- We then watch how the difference between the twins spreads, round by round. Only the stretch
  before either twin's next guess counts, so the difference can travel **only through the local
  tile rules**.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| Z1 | a speed limit exists (≤ 2 tile diameters per round) | largest step 1.05 edges = 0.65 tile diameters | ✅ PASS |
| Z2 | the past is untouched | never touched | ✅ PASS |
| L1 | light-like (steady speed), not diffusive: median α ≥ 0.8 | **α = 0.93** (range 0.81–1.09) | ✅ HELD |
| L2 | news travels along the now ≥ 3× faster than the now moves outward | **0.95 vs 0.30 edges/round (3.2×)** | ✅ HELD (just) |
| L3 | influence travels in thin rays (elongation ≥ 3 in ≥ half) | 0.16 | ❌ FAILED |

### An honest caveat: 50 perturbations, but only 12 distinct ones

[`results/distinct_perturbations_EXPLORATORY.txt`](results/distinct_perturbations_EXPLORATORY.txt)

- With the patient scheduler and no throttle, the random stream is used only at the 3–5 guesses per
  run, each a choice between 2 options.
- So different seeds often grow **identical** histories: the 12 seeds gave 9 distinct histories and
  **12 distinct perturbations**. I did not foresee this when pre-registering.
- On the 12 distinct perturbations the verdicts are unchanged:
  - α = 0.97 (L1 held);
  - speed ratio 3.2 (L2 held);
  - elongation ≥ 3 in 0.33 (L3 failed).
- The evidence rests on 12 events, not 50.

## What it means (plainly)

- **There is a speed of light, and influence travels at it.** A changed choice spreads at a steady
  **~1 tile edge per round**: 0.67–1.13 across all 12 events, median 0.95. It never goes faster than
  about 1.05 edges per round. The spread is steady like a light front, not slowing like ink
  diffusing.
- **The now carries news sideways faster than it moves forward.** News runs along the growing edge
  at about 1 edge per round. The edge itself advances outward at about 0.3. So the edge of the now
  is like a surface along which signals race, while the now as a whole creeps forward.
- **Influence is not a thin ray. It fills a whole region.** One different choice produces a whole
  different *sibling region* spreading out from it: 85 to 709 tiles, a broad wedge that grows at
  light speed. It is not a single worm-line. The first sibling choice becomes a whole different
  world downstream.
- **The past is never touched**, again.
- *Exploratory:* after the window, when the patient scheduler's shared guess timing comes into play,
  no far-away jumps appeared (0/50). The scheduler's non-local channel did not show up here.

## Limits

- One tiling family, and the FAST arm only.
- A preferred frame: the shared rounds.
- Only 12 distinct perturbations.
- Windows end at the next guess or the size cap (19 of 50 ended at the cap).

## Next (door 2)

A **quiet blob as a lens**:

- Does light, meaning this ~1 edge/round influence, slow down and bend around a quiet region?
- Katie's question goes with it: is it **quietness** (happening density) or **fullness** (accretion
  density) that bends it?
- Door 2 will need **more distinct events**. For example, add random tie-breaking among
  simultaneous guesses, or perturb forced placements directly, so seeds don't collapse onto the same
  few histories.

## Files

- `speed_of_light.py` (`--summary` recomputes the report)
- `results/perturbations.jsonl`
- `results/speed_of_light_report.txt`
- `results/distinct_perturbations_EXPLORATORY.txt`

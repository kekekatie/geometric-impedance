# The decapod seed: does a memory-carrying defect give a world with no choices?

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). It includes one logged change before the first run: a
validation check exposed a candidate-listing bug, which was fixed. `dedup_probe.py` shows the bug
never affected ordinary growth, so earlier studies stand.*

## What was done

- **The rings.** Around a forbidden unit decagon (never filled), every legal ring of 10 half-tiles
  was enumerated. Each ring is locally fine at every corner. There are **111 rings up to rotation**.
- **The kinds.** Each ring is either:
  - **FILLABLE**: the decagon inside can be legally tiled (4 rings, each with exactly 1 filling);
  - **DECAPOD**: it can't (107 rings).
- A decagon taken from a genuine Penrose tiling was confirmed to be among the rings, and fillable.
- **The growth.** Each ring was grown outward with the patient scheduler (a guess only when nothing
  is forced anywhere), 800 tiles, 3 runs each.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| Q0 | both kinds exist | 4 FILLABLE, 107 DECAPOD | ✅ PASS |
| Q0b | a genuine decagon ring is enumerated and fillable | yes | ✅ PASS |
| Q1 | ≥ 80% of non-jamming DECAPOD seeds need **zero guesses** | **94/96** | ✅ HELD |
| Q2 | every FILLABLE seed needs ≥ 1 guess in every run | **4/4** (1–4 guesses per run) | ✅ HELD |

## What it means (plainly)

- **A world grown around a decapod needs no choices.** In 94 of 96 cases, 800 tiles were laid by
  forced moves alone: never a dead surface, never a guess, never a jam.
- A world grown around a fillable decagon (an ordinary piece of Penrose tiling) hit dead surfaces
  every time and had to guess. This reproduces, in our own code, the 1988 result of Onoda,
  Steinhardt, DiVincenzo & Socolar (known to us only from summaries).
- **Why this matters for us.** In [`../local_deciders/`](../local_deciders/) we could not get a now
  that was both local and jam-free. Guesses had to wait for the whole world, or they clashed. A
  decapod world needs no guesses at all. Every round, every forced tile everywhere is laid, with no
  queue and no global decider. **It is the first truly local now we have grown.** It also grows
  **about twice as fast**: 25–44 rounds to 800 tiles, against 63–85 for fillable seeds, because
  nothing ever waits.
- **Connection to our jewels.**
  - A decapod is where the tiling's lift fails to close. It carries **holonomy**, a memory: "perfection
    cannot remember", and this imperfection does.
  - The writing walker's stubborn knot was a bad decapod.
  - So: **a world seeded by a memory needs no choices; a perfect seed must keep choosing.**

### Exploratory (post hoc)

[`smoothness_EXPLORATORY.py`](smoothness_EXPLORATORY.py),
[`results/smoothness_EXPLORATORY.txt`](results/smoothness_EXPLORATORY.txt)

- **False decapods.** 11 of the 107 unfillable rings jammed in at least one run (7 in all 3 runs).
  They look like decapods from the inside, but their outside can't extend. Their jams happen at
  fixed distances (3.0, 4.4, 5.9, 7.0 and 9.5 edges), often after hundreds of tiles.
- Two unfillable rings grew without jamming but needed guesses (seeds 62 and 83).
- **Local, but not round.** The zero-guess growth is local (no queue), but its front is **not** a
  smooth circle. The sector spread of arrival rounds in the 5–7 edge band has a median of 1.21 over
  12 decapod seeds, against 0.8–1.56 for fillable seeds. Forced growth runs faster in some
  directions than others, presumably along the tiling's own lines. A local now that is also
  uniform would need something more, or a different way of measuring "uniform".

## Limits

- A single ring of 10 half-tiles as the seed; 800 tiles; 3 runs per seed.
- Rings count reflections separately, so 107 is not directly comparable with Conway's 62.
- Forcing is edge-level. It matched vertex-level forcing in [`../gromit_check/`](../gromit_check/).

## Files

- `decapod_seed.py` (`--report` recomputes the report)
- `dedup_probe.py`
- `smoothness_EXPLORATORY.py`
- `results/seeds.json`
- `results/runs.jsonl`
- `results/decapod_seed_report.txt`
- `results/dedup_probe.txt`
- `results/smoothness_EXPLORATORY.txt`

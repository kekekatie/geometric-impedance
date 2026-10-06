# How much of the world must weigh in? Decision radius vs depth

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). The first run couldn't test the idea, so a follow-up was
registered before it ran.*

**The idea** (Claude's proposed mechanism for `../structure_clock/`): deep places in the hidden
window keep their now open longer because **more of the world has to weigh in before they're
decided**.

**The test.** Wipe a small disc of tiles around a place. Show the rules only a ring of the world
around it, then widen the ring until the place's tiles come out uniquely. 4 intact decapod worlds,
100 places each.

## Scorecard

| | prediction | first run (all-around context) | follow-up (the world as it stood when the place finished) |
|---|---|---|---|
| R1 | deeper places need a wider ring: ρ(depth, radius) > 0 in ≥ 3/4, median ≥ 0.15 | ❌ untestable: all 400 decided by the thinnest ring | ✅ **4/4**, median **0.21** |
| R2 | places needing a wider ring take longer to settle: ρ > 0 in ≥ 3/4 | ❌ untestable | ✅ **4/4** (0.09–0.41) |

**First run.** A place surrounded on *every* side is always uniquely decided, which matches the
earlier "enclosed regions have one filling" finding. That made the measure useless, and it was my
design flaw: at the real growing edge, a place only has its **past** side.

## What it means (plainly)

Breakdown by depth third, pooled over the 4 worlds
([`results/breakdown_EXPLORATORY.txt`](results/breakdown_EXPLORATORY.txt)):

| | decided by the thinnest ring (1.25 edges) | needed the next ring (1.5) | not decided even by a 4-edge ring | mean settling time |
|---|---|---|---|---|
| shallow third | 32% | 60% | 8% | 5.3 rounds |
| middle third | 38% | 50% | 12% | 4.5 rounds |
| **deep third** | **2%** | **98%** | **0%** | **6.6 rounds** |

- **Deep places can almost never be decided by the thinnest ring of their past.** 98% need the next
  ring out, and they take the longest to settle. That's the predicted mechanism, in a modest form:
  more of the world has to weigh in, and the present lasts longer while it does.
- **Deep places are also always decidable from nearby.** None needed more than 1.5 edges.
- ~~**A surprise among shallow and middle places.**~~ **Resolved as a measurement artefact
  (2026-10-06).** About 10% could not be decided even from a 4-edge ring, yet settled fast. Gemini
  asked whether these were "zippers", places decided sideways by the active present.
  - But the context already included everything laid up to the moment the place finished, same-round
    sideways neighbours included.
  - The check ([`undecided_check_EXPLORATORY.py`](undecided_check_EXPLORATORY.py),
    [`results/undecided_check_EXPLORATORY.txt`](results/undecided_check_EXPLORATORY.txt)) found that
    **all 27** "undecided" places have a target point covered by a tile lying *outside* the 1.0-edge
    disc and laid *after* the disc finished, against 40 of 373 decided places.
  - The target (out to 0.8 edges) reaches tiles whose centroids sit up to 1.8 edges away, while
    "finished" was defined by the 1.0-edge disc. So the test asked these places to predict tiles
    that didn't exist yet.
  - They are not a special group. The R1 and R2 conclusions rest mainly on the 1.25 vs 1.5 split and
    don't depend on them.

## Limits

- Sampled completions (16) with a one-step look-ahead.
- Geometric rings, not chains of forcing.
- 4 worlds sharing structure, and modest correlations.
- The rings tested are coarse (1.25, 1.5, then 2, 2.5, 3, 4). Only the first two did most of the work.

## Files

- `decision_radius.py`
- `results/worlds.json`
- `results/decision_radius_report.txt` (follow-up)
- `results/breakdown_EXPLORATORY.txt`
- `undecided_check_EXPLORATORY.py`, `results/undecided_check_EXPLORATORY.txt`
- `results/run1_full_context/` (first run)

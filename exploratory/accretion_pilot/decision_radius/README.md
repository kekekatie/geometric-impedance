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
- **A surprise among shallow and middle places.** About 10% could *not* be decided even from a
  4-edge ring of their past, yet they settled fast (3.1 rounds on average). Either:
  - they're fixed by news from **further away** (long-range constraints), or
  - our sampled completions find alternatives that would only dead-end further out (a limit of the
    method).
  
  This is worth a closer look.

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
- `results/run1_full_context/` (first run)

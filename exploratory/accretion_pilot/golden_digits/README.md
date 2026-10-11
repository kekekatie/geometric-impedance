# Golden digits: confirmed on fresh worlds

*A pre-registered confirmation study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). No changes were made before the run.*

**Why.** `../slack/` found its best results in post hoc follow-ups. They needed confirming on **fresh
worlds** with the measures fixed in advance.

**The worlds.** 24 new starting points (the 25th–48th symmetry-free reference vertices), with fresh
random streams. 60 two-way choices in all.

> **Refinements after Astra's review (2026-10-11):**
>
> 1. **Zero area is not the same as empty.** The original code gave a segment, a point and an empty set the same answer. Re-classified with linear programming ([`../slack/classify_EXPLORATORY.py`](../slack/classify_EXPLORATORY.py), [`../slack/results/classify_EXPLORATORY.txt`](../slack/results/classify_EXPLORATORY.txt)):
>    - **decapod worlds:** the bare ring's F is a polygon. After one slice it is a single **point**, and it stays a point to the end, in all 8 worlds. They really are pinned to one offset.
>    - **the two dead-option worlds** (slack world 14, golden world 0): F was a polygon, became genuinely **empty** at the dead choice's slice, and each world **jammed 14 slices later**.
>    - So "pinned" and "impossible" are now distinguished, and both earlier readings survive.
> 2. **Wording.**
>    - "Exact splits" means **partitions within the registered numerical tolerances**. Exactness would need a geometric derivation.
>    - "Fibonacci number system / golden digits" means **a recurring family of golden-ratio area shares**. A true digit system would need a demonstrated encoding and continuation rule.
>    - "6% by chance" refers to shares spread evenly on (0, 0.5]. It is *not* a significance estimate against the tiling's actual geometry.
>    - "The choice's cut finishing" is an interpretation. What was measured is the *timing*: every forced narrowing of F came exactly one slice after a choice.
> 3. **Revealed or selected?** The growth picks between the two options **50/50** (a fair choice), even though the pieces are 38% and 62% of the possibilities. If instead a hidden offset were chosen uniformly first and then *revealed*, the pieces would be taken 38% and 62% of the time. These are two different models: *making* a world versus *discovering* a predetermined one. The present results don't decide between them.
> 4. **Picture** ([`../slack/figures/window_cut.png`](../slack/figures/window_cut.png)):
>    - *Left:* one ordinary choice. The wiggle room (a triangle) is divided by **one straight line**, a single new vertex's window-edge constraint, into option B's 14.6% and option A's 85.4%. The two options are the two sides of one line.
>    - *Right:* a bare decapod ring's wiggle room is a large decagon. After one slice it is pinned to a single point at the decagon's **centre**.
>    - Next sharp question (Astra): can the split proportions be derived from the cutting lines before measuring the areas?

## Scorecard

| | prediction | result | |
|---|---|---|---|
| G1 | ≥ 90% of choices split the wiggle room exactly in two (once both alternative presents grow on) | **59 / 59** | ✅ HELD |
| G2 | ≥ 90% of split shares lie within 0.002 of the golden family (chance ≈ 6% each) | **59 / 59**, none outside | ✅ HELD |
| G3 | the commonest share is 1/τ² = 0.382 | **36 / 59** | ✅ HELD |
| G4 | forced growth shrinks the wiggle room *only* in the slice right after a choice | **16 / 16** shrinks, 0 exceptions | ✅ HELD |
| G5 | a world whose wiggle room empties jams, and no other world jams | world 0 took the one dead option, its room emptied, and it jammed; no other world jammed | ✅ HELD |

**Smaller shares:**

| | 1/τ² (0.382) | 1/τ³ (0.236) | 1/τ⁴ (0.146) | 1/(2τ) (0.309) | (5−√5)/10 (0.276) | 1/(2τ²) (0.191) | 1/√5 (0.447) |
|---|---|---|---|---|---|---|---|
| choices | **36** | 10 | 4 | 4 | 3 | 1 | 1 |

**Reported:** in the main worlds, the random pick took the larger piece 29 times and the smaller 30
times, like a fair coin, as it should be.

## What it means (plainly)

The `../slack/` follow-ups are now **confirmed results**:

- **Forced growth reads nothing.** The world's hidden position is never narrowed by a forced tile. The
  only exceptions are a choice's own cut finishing in the next slice.
- **Each two-way choice divides the remaining hidden possibilities exactly between the two
  alternative presents.** No overlap, nothing lost.
- **The divisions are golden.** Every one of 59 splits is a golden-ratio number. The commonest is the
  classic 38 / 62 split, then 24 / 76, then smaller pieces (1/τ⁴) and a few half-golden values.
  - The hidden number is being read in **golden-ratio digits**: a choice says "the larger golden part"
    or "the smaller golden part", not "heads" or "tails".
  - That is natural for a tiling built on the golden ratio, so nothing is imported.
- **A locally legal choice can lead off every possible world,** and the wiggle room shows it at once.
  Such a world later jams.

**Katie's 1s and 0s:** they are there, as the two sides of every choice. But they are read in a
Fibonacci-style (golden) number system, where the two "digits" have unequal weights. They are not
fair binary halves.

## Limits

- One tiling family. 60 choices over 24 worlds.
- The golden family was read off the earlier study. This confirms that it **recurs**, not that it is
  the complete set.
- *Why* these particular golden pieces, and in these frequencies, is not yet explained. A natural next
  question is whether they follow the Fibonacci frequencies of the window's own geometry.

## Files

- `golden_digits.py`: the study
- `results/golden_digits_report.txt`, `results/run.log`, `results/worlds.json`

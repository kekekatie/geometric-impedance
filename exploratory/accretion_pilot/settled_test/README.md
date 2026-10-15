# Predicted, or settled? What the first choice fixes

*A pre-registered study, following Astra's three suggested steps after `cut_direction/`. The
pre-registration was committed before any code: [`PREREGISTRATION.md`](PREREGISTRATION.md).*

**Why.** `cut_direction/` found that a choice's cut in the wiggle room predicts the dominant family of
the strip where the two futures later differ. Astra raised three questions:

1. Could later guesses have shaped that strip?
2. Is it one connected ribbon, or just a family?
3. Is the strip *settled* by the first choice, or only *predicted*?

**The set-up.**

- 24 fresh worlds gave 45 distinct situations.
- Each option got an **initial burst**: forced tiles only, stopping before any guess, with a cap of 40
  slices.
- Each option also got **5 continuations**: 20 slices each with different random streams, so they
  differ only in their later guesses.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| P1 | the initial burst alone (no later choices) carries the predicted family (≥ 90%) | **45 / 45** | ✅ HELD |
| P2 | one connected chain covers ≥ 50% of a side's changed tiles (≥ 60% of sides) | **90 / 90**; median share 0.67 (IQR 0.66–0.69) | ✅ HELD |
| P3 | the family is the same across all 5 continuations (≥ 90%) | **44 / 45**, and it is the predicted family | ✅ HELD |
| P4 | core tiles built *after a later guess* are identical across continuations (≥ 80%) | **1 / 2** situations with such tiles; pooled 44/92 identical | ❌ FAILED (nearly vacuous) |

**Reported.**

- **Later guesses were rare.** In 20 slices, 380 of 450 continuations made **no guess at all**, and
  the rest made one (mean 0.16). So in windows like `cut_direction/`'s, the changed strip was almost
  always built by forced moves alone. Astra's concern was right to raise, and in this sample it rarely
  applied.
- **Most initial bursts never stalled:** 66 of 90 ran the full 40 slices on forced tiles alone.
- **Control.** Non-core changed tiles built after a later guess were identical across continuations
  only 1,208 / 2,242 times (54%). So the test *can* see disagreement: where later guesses happen,
  they do change things.
- **The cut from the choice tile alone** was visible in only 14/45 situations. It needs the first
  forced slice to show. Where it was visible, it had the same direction in 14/14.

## What it means (plainly)

- **What the first choice settles is its forced burst, and that is settled for real.**
  - A forced tile is the only tile that locally fits its spot. So *every* completed tiling that
    contains the patch must contain it, not just every continuation we tried.
  - The wiggle room stays non-empty, so such completions exist (an empty wiggle room is what goes with
    a jam; `golden_digits/`).
  - The initial burst alone carries the predicted family (45/45), and in most cases it ran for the
    whole 40 slices. So the cut's prediction is about a region the first choice genuinely **settles**,
    not just one it predicts.
- **The settled region is mostly one connected chain** of the predicted family (about two-thirds of
  the changed tiles), with neighbouring changes around it.
- **Beyond the next guess, it isn't settled.** P4 had only 2 testable situations, because later
  guesses were so rare. In those, tiles built after a later guess often differed between
  continuations. So the first choice's reach ends where the next choice begins. That fits everything
  we've seen: each choice settles its own burst.
- **For "settled vs built":**
  - *Settled* = the forced burst. It is fixed the moment the choice is made, and fixed in every
    possible completion.
  - *Built* = those tiles get laid one slice at a time.
  - That distinction now stands on firmer ground, for the burst region. (The pooled placement-time
    fit from `cut_direction/` is still not a speed limit.)

## Limits

- P4 failed as registered and was nearly vacuous: 2 situations. Settledness beyond the next guess is
  untested in any depth. The little evidence there says it is *not* settled.
- **"Settled in every completion" depends on the candidate list being complete.** It assumes
  `D.candidates` lists every locally legal tile, which all our earlier studies rely on. It also
  assumes "non-empty wiggle room ⇒ completable", which matches our observations (empty F ↔ jam) but
  isn't proven here.
- The core is the largest connected chain of the predicted family. Its stable ~0.67 share suggests it
  holds nearly all of that family's changed tiles; this wasn't checked separately.
- One kind of world, one scheduler.

## Files

- `settled_test.py`: the study. Writes `results/settled_test_report.txt`, `results/results.json`,
  `results/run.log`.

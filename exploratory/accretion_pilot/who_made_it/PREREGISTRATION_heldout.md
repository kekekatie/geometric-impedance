# Does one finished world carry evidence of how it was made? Held-out test. Pre-registration

*Written and committed **before** any code for this test existed.*

## Why (Astra's review of the who_made_it study)

- "One world can't tell" was too strong. What we actually have is a non-detection in 8 vertex-type
  frequencies.
- A single world can carry weak evidence. Taking the smaller first-choice piece favours SELECT by a
  likelihood ratio of about 1.31.
- Astra's next step: **predefine** a small set of measurements available from a **finished patch
  alone**, then test whether they identify SELECT vs REVEAL on **held-out** seed locations. Growth
  history stays a separate diagnostic.

## Measurements from the finished patch alone (fixed now)

- **M1, leftover wiggle room:** log of the area of the finished patch's F.
  - Reasoning: SELECT takes the smaller piece at a choice about half the time; REVEAL takes it only in
    proportion to its share. So SELECT worlds should keep less wiggle room.
- **M2, vertex-type frequencies:** the 8 frequencies, as in the who_made_it study.
- **M3, F's kind:** empty, point, segment or polygon (`../slack/classify_EXPLORATORY.py`, linear
  programming). This applies Astra's empty/point check.
  - **Fixed rule:** a finished patch whose F is **empty** is classified **SELECT** (a dead end; REVEAL
    cannot reach one).

## Worlds

- **Training:** the 48 seed centres of the who_made_it study (wedge entries 1–48). Each is grown in
  both modes, with fresh streams: SELECT `20261600 + k`, REVEAL `20261700 + k`.
- **Held out:** wedge entries **49–96**, both modes, streams SELECT `20261800 + k`, REVEAL
  `20261900 + k`.
- Everything else is as in `who_made_it.py`: 1,500 half-tiles, patient scheduler, REVEAL by hidden
  offset with sibling pieces.

## Classifiers (fit on training worlds only, then frozen)

- **A:** logistic regression on M1 alone.
- **B:** logistic regression on M2 (the 8 frequencies).
- **C:** M1 + M2.
- In all three, the M3 rule applies first: an empty F means SELECT.
- Worlds with empty F are excluded from fitting.

## Predictions (held-out worlds, 96)

- **H1 (leftover wiggle room carries evidence):** classifier A's held-out accuracy is above chance,
  with one-sided binomial p < 0.05 against 0.5. *Confidence about 60%.*
- **H2 (everyday counts carry little):** classifier B's held-out accuracy is **below 0.60**.
  *Confidence about 70%.* Note: this is a weak-signal statement, not proof of sameness.
- **H3 (dead ends are certain):** every held-out world with empty F is a SELECT world. *Confidence about
  95%.*

## Reported without prediction

- Classifier C's accuracy.
- The distributions of M1 by mode.
- The likelihood ratio implied by M1 for a typical world.
- M3 kinds by mode, and how many worlds jammed.

## Limits, stated in advance

- One tiling family, and 1,500 half-tiles.
- M1 depends on how many choices a world met. That is part of the signal, and it is not separated out
  here.
- Logistic regression is a simple reader. A null result for B doesn't exclude subtler signatures.

## Changes before the first run

*(none yet)*

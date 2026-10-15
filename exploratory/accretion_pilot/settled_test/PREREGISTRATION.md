# Predicted, or settled? Does the first choice fix the strip, whatever happens next?

*Pre-registration, written and committed before any code for this study exists. This follows Astra's
three suggested steps after `cut_direction/`.*

## Where this comes from

`cut_direction/` found that the direction of a choice's cut in the wiggle room predicts the dominant
edge family of the strip in which the two futures later differ. That holds in 45/45 situations, and
the strip's direction follows 108° − 2 × cut.

Astra pointed out three gaps:

1. The futures could make **further guesses** during the 20 slices, so later choices might have
   shaped the strip.
2. A dominant **family** is not one connected **ribbon**.
3. **"Predicts" is not "settles".** A feature is settled by the first choice only if it survives
   *different* later continuations.

## Words

- **Choice, options A and B, cut line:** as in `cut_direction/`. Here the cut is read at the choice,
  from each option's constraints **after its first forced slice**. As a reported check, it is also read
  from the choice tile alone.
- **Rule:** family *j* ↔ cut line at 90° − 36°·*j* (mod 180°), from `cut_direction/`'s corrected
  analysis. The **predicted family** is the family the rule gives for this cut.
- **Initial burst:** an option grown **forced-only**, stopping before its first guess (cap 40 slices).
  This involves no later choices at all.
- **Changed region:** the tiles one side has where the other side has a different tile in the same
  place (as in `fragility/`).
- **Chain:** changed tiles of one side, connected through shared edges of the predicted family, or
  through the shared diagonal of the same rhombus. The **core** is the largest chain.
- **Continuations:** each option is grown **5 times** for 20 slices with the patient scheduler, each
  with a different random stream (the same 5 streams for A and B). These differ only in their later
  guesses.

## Set-up

- **24 fresh ordinary worlds**, with seed centres at entries 168–191 of the 18° wedge (0–167 were used
  before). Random seed 20261190 + world. Each grows to 1500 added tiles.
- Every live two-way choice with a cut line found is used. Each distinct situation counts once (whole
  base patch identical relative to the choice point).
- Situations with fewer than 6 changed tiles in the initial bursts are reported but not tested.

## Predictions (fixed now)

**P1: The initial forced response alone carries the family.** Comparing the two initial bursts, the
dominant family of the changed region equals the predicted family in at least 90% of tested
situations. Confidence about 80%.

**P2: One connected chain carries most of it.** In each side's initial-burst changed region, the core
chain covers at least 50% of the changed tiles, in at least 60% of situation-sides. Confidence about
55%.

**P3: The family survives different continuations.** At slice 20, comparing continuation *c* of A with
continuation *c* of B, the dominant family of the changed region is the same for all 5 *c*, in at least
90% of tested situations. Confidence about 75%.

**P4: The strip is settled, not just predicted.**

- For each continuation of an option, take the core-chain tiles built *after* its first guess.
- Check them wherever another continuation of the **same** option has built that place.
- At least 99% must be the identical tile, in at least 80% of situations that have such tiles. This is
  measured as the worst pair of continuations.

Confidence about 60%.

**Control (reported):** the same agreement for changed-region tiles *outside* the core, built after
the first guess. If later guesses matter anywhere, they should show up there. That would show the test
is able to see disagreement.

## Reported, not tested

- How often the futures guessed within the 20 slices, which is what `cut_direction/` didn't record.
- Whether the cut read from the choice tile alone has the same direction.
- The core's share in the slice-20 changed regions, and the families of the non-core changed tiles
  (the "neighbouring changes").

## Limits I already know

- Five continuations sample the later choices; they don't exhaust them. Agreement supports
  robustness, but doesn't prove universality.
- Agreement is checked only where two continuations both built the same place.
- One kind of world, one scheduler.

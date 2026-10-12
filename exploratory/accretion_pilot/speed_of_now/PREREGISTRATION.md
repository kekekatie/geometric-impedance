# The speed of now: why do some choices make the present rush ahead?

*Pre-registration, written and committed before any code for this study exists.*

## Where this comes from

In `thread_influence/` we noticed something on the side: after a two-way choice, the two alternative
presents can advance at very different speeds. In one case, one option let **24** tiles fall into place
before the world needed another guess, and the other let **90**.

So in our growing worlds the "speed of now" (how many tiles each slice of now lays down) is not fixed. A
choice can speed it up or slow it down. This study asks:

1. **What sets the speed?** Is it the piece of wiggle room F that the option keeps?
2. **Does it last?** Does a fast present stay fast, keep a head start, or does it even out?

## Words

- **Choice:** a slice where the patient scheduler finds nothing forced on the whole frontier, and the
  first frontier edge has exactly two candidate tiles.
- **Burst:** add one option, then grow forced-only (every forced tile, every slice) until a slice has
  nothing forced. That is the **stall**. The burst is the number of tiles placed, counting the chosen
  tile. It is capped at 40 slices, and a jam ends it.
- **Piece kept:** the area of F after the burst, divided by the area of F at the choice. (We already
  know forced growth never shrinks F except in the slice right after a choice, so this is the option's
  piece of F.)
- **Long run:** after the burst, each sibling keeps growing with the patient scheduler (forced first, a
  guess only when nothing is forced) until **40 slices** after the choice. Both siblings' guesses use the
  same random stream, seeded by the choice.
- **Speed:** tiles placed per slice.

## Set-up

- **24 fresh ordinary worlds**, with seed centres at entries 96–119 of the 18° wedge of reference-tiling
  vertices (entries 0–95 were used by earlier studies). Random seed 20261160 + world.
- Each main world grows with the patient scheduler to 1500 added tiles, as in `golden_digits/`.
- At every two-way choice, both siblings get a burst and a long run.
- A choice is **live** if both pieces kept are > 0. Dead options (empty F) are reported separately.
- A choice is **unequal** if the two bursts differ by at least 10 tiles.

## Predictions (fixed now)

**S1: Smaller piece, faster now.** In live, unequal choices, the sibling keeping the **smaller** piece of
F has the **larger** burst in at least 70% of them.
*Why I expect it:* a smaller piece means more of the world's hidden position has been decided, so I'd
expect more of the frontier to be locked in. *Doubt:* forcing is checked locally, edge by edge, while F
is global. My confidence is about 55%.

**S2: The rate evens out.** Across live choices, the Spearman correlation between the burst difference
(A − B) and the **late-rate** difference (A − B tiles in slices 21–40 after the choice) lies between −0.2
and +0.2.
*Why:* the long-run speed should be set by the tiling and the size of the front, not by one choice.
Confidence about 60%.

**S3: The head start fades too.** In live, unequal choices, the gap in **total** tiles at slice 40 is
less than half of the burst gap in at least 60% of them.
*Why:* the slow sibling stalls, guesses, and its next burst should pick up the tiles the fast one got
for free, because both are filling much the same region. Confidence about 55%.

## Reported, not tested

- Bursts grouped by the golden share of the piece kept (1/τ², 1/τ³, ...).
- Slices until the stall, and the number of guesses each sibling needs in its 40 slices (the "history
  count" of `who_made_it/`).
- How dead options behave: do they burst and then jam?

## Limits I already know

- One kind of world (ordinary seeds) and one scheduler.
- Common random numbers for both siblings make the comparison fairer, but the guesses land in
  different places, so the two long runs are not perfectly paired.

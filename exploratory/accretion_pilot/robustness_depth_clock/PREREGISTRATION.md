# Robustness: does "the present lasts longer deep in the window" survive? Pre-registration

*Written and committed **before** any code for this study existed.*

*The candidate core finding for a paper ([`../structure_clock/`](../structure_clock/), C1) is this:
in intact decapod worlds, places deeper in the hidden window take longer to settle. The within-radius
Spearman correlation was ρ_T = 0.21–0.29, positive in 8/8 worlds. Those 8 worlds share structure,
use one disc size, and are all decapod worlds. This study stress-tests the finding three ways. It
uses the analysis of `../structure_clock/structure_clock.py` unchanged (probes, T, H, depth,
radius-stratified Spearman, permutation baseline), except for what each test varies.*

## Tests

**A. New decapod worlds.**

- The next **12** zero-guess DECAPOD seeds in `../decapod_seed/` order, after the 8 already used
  (those whose 3 runs all completed with zero guesses).
- 2,000 half-tiles, as before.

**B. Ordinary worlds (with choices).**

- **12** worlds grown from the usual genuine seed patch (radius 3 edges) with the patient scheduler.
  Random guesses are made when nothing is forced.
- Random streams `20261080 + k`.
- 2,000 half-tiles.
- Same probes and measures. Settling time now includes any waiting for guesses.

**C. Different measuring sizes, on the original 8 decapod worlds.**

- **C-small:** disc radius **0.8**, neighbourhood **1.5** edges.
- **C-large:** disc radius **1.25**, neighbourhood **2.5** edges.
- The original was 1.0 and 2.0.

## Predictions

- **RA:** ρ_T **> 0** in at least **10 of 12** new decapod worlds. *Confidence about 70%.*
- **RB:** ρ_T **> 0** in at least **9 of 12** ordinary worlds. *Confidence about 50%. These worlds
  make choices, and their timing is dominated by the global guess queue, so the effect may be
  swamped.*
- **RC:** ρ_T **> 0** in at least **7 of 8** worlds for **each** of C-small and C-large. *Confidence
  about 65%.*

The core finding counts as **robust** only if all of RA, RB and RC hold.

## Reported without prediction

- ρ_H (depth against local happenings) in every test.
- The depth-third means of T.
- Distinct histories among the ordinary worlds: seeds may collapse onto the same few guess
  sequences, as in `../speed_of_light/`.

## Limits, stated in advance

- One tiling family.
- The new decapod worlds may still share structure with the first 8.
- Ordinary worlds may repeat histories.

## Changes before the first run

*(none yet)*

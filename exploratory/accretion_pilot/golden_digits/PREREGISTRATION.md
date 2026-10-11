# Golden digits: a confirmation on fresh worlds. Pre-registration

*Written and committed **before** any code for this study existed.*

## Why

`../slack/` found its most interesting results in **post hoc** follow-ups, after three of its five
registered predictions failed (one because I measured too early). Before anything is built on them,
they need confirming on **fresh worlds**, with the measures fixed in advance.

The follow-up findings to confirm:

1. Once both alternative presents grow on, each choice splits the wiggle room F **exactly** in two.
2. The split proportions belong to a small **golden family**.
3. Forced growth never costs wiggle room, **except** the slice right after a choice (the cut
   finishing).
4. A world that takes a "dead" option (one consistent with no hidden number) has empty F and later
   jams.

## Construction

**Fresh worlds.**

- 24 ordinary worlds started from the **next 24** reference-tiling vertices in the same 18° symmetry
  wedge as `../thread_influence/`: the 25th to 48th nearest the origin, in the same order.
- Fresh random streams `20261140 + k`.
- Otherwise identical: seed patch radius 3 edges, patient scheduler, 1,500 half-tiles.

**Measures.** All as in `../slack/` (`slack.py` functions reused unchanged), with these additions:

- At every two-way choice, both options are grown forced-only for up to 8 slices (`../fragility/`
  sibling growth). Then F_A, F_B and their overlap are computed, as shares of F at the choice.
- A choice is **clean** if both shares are > 0, the overlap is < 1%, and the shares sum to within 1%.
- A choice is **dead-optioned** if one share is exactly 0 and the other is within 1% of 1.
- **Golden family** G (exact values):
  - 1/τ⁴ = 0.1459
  - 1/(2τ²) = 0.1910
  - 1/τ³ = 0.2361
  - (5−√5)/10 = 0.2764
  - 1/(2τ) = 0.3090
  - 1/τ² = 0.3820
  - 1/√5 = 0.4472
  - 1/2

  This is the set observed in `../slack/`, now fixed.

## Predictions

- **G1 (exact splits).** Among choices that are not dead-optioned, at least **90%** are clean.
  *Confidence about 80%.*
- **G2 (golden digits).** Among clean choices, at least **90%** have a smaller share within **0.002**
  of a member of G. *Confidence about 70%.* By chance, a share spread evenly over (0, 0.5] would land
  this close to one of the 8 values only about 6% of the time.
- **G3 (the commonest digit).** The most frequent member of G is **1/τ² = 0.382**. *Confidence about
  55%.*
- **G4 (forced growth reads nothing).** Every forced slice that shrinks F (relative change > 10⁻⁶)
  comes **exactly one slice after a choice**. Zero exceptions allowed. *Confidence about 75%.*
- **G5 (dead ends).**
  - Every world whose F becomes empty jams before reaching 1,500 tiles.
  - No world whose F stays non-empty jams.
  - *Confidence about 70%.* If no world's F empties, the first half is untestable and is reported as
    such.

## Reported without prediction

- The full distribution of smaller shares, including any outside G.
- Wiggle room kept per choice in the main world.
- The number of distinct choices.
- Whether the main world's random pick took the larger or smaller piece.

## Limits, stated in advance

- One tiling family. Up to 8 slices of sibling growth.
- G was read off the earlier data. This study tests whether it *recurs*, not whether it is the only
  possible set.

## Changes before the first run

*(none yet)*

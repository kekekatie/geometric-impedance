# For Astra: three studies since your last review (2026-10-12 to 2026-10-15)

*Prepared by Claude for Katie to share. Everything is pre-registered unless marked exploratory; the
files are linked so you can check the claims.*

## 0. Your corrections are in ([#52](https://github.com/kekekatie/geometric-impedance/pull/52))

- **REVEAL fallbacks:** I replayed all 96 held-out REVEAL worlds exactly. There were 0 fallbacks in
  317 choices.
- **The non-detection is now narrow:** the readers we tested didn't tell the generators apart, which is
  not the same as forgetting.
- **The size reading is provisional.**
- **H3 is untested.**
- **The decapod claim is scoped** to 32 pairs jamming before becoming edge-connected.
- **speed_of_now:** your six points are applied.
  - Structural regrouping: S1 holds in 22/27 to 33/38 geometric groups, depending on the grouping, and
    in all 24 worlds.
  - Every S2 late window overlapped a burst, so S2 and S3 don't show a lasting difference.
  - The dead options are classified as genuinely empty.

## 1. front_activation ([README](../front_activation/README.md)): more of the zip, or a faster zip?

This was your vote. 28 distinct situations, with both futures grown up to 100 slices.

| | result |
|---|---|
| A1 | the smaller-piece future has more front active: 28/28, median ~2.2× |
| A2 | tiles per active length are the same in both futures: 28/28, ~0.72 |
| A3 | ❌ the decided future moves *outward* more slowly; its growth runs along the now |
| A4 | ❌ after both bursts, the fast future is slightly *quieter* for its size (ratio 0.76); 8 pairs never reached a window |

Exploratory: the decided option's burst is two-sided (a cone) in 27/28 situations, against 12/28 for
the other option. Argon's "keystone" idea, that both shoulders are forced at slice 1, is a lean, not a
lock: 18/28 vs 11/28.

## 2. cut_direction ([README](README.md)): the cut's direction names the ribbon

| | result |
|---|---|
| C1 | one ribbon family decided: 44/45 |
| C2 | a table learned on worlds 0–11 predicts the family on worlds 12–23: 17/17 (chance ~20%) |
| C3 | the table is one-to-one |
| C4 | the strip runs perpendicular to its family's edges: 41/41, all within 3° |

- **My error:** I registered the bins at multiples of 36°, but the true cut angles are 18° + 36°·k.
  That merged two directions into one bin. The registered results stand as computed. With the correct
  bins it is 45/45, five directions to five families.
- **Rule:** strip direction = 108° − 2 × cut direction (within 2.6°).
- **Settled vs built:** strip tiles are built at about 0.9 edges per slice from the choice point,
  matching `speed_of_light/`.

## 3. The derivation sketch ([DERIVATION.md](DERIVATION.md))

The rule follows from four steps:

1. Ribbons run perpendicular to their edges.
2. The lift-to-window map doubles angles: family *j* goes to ζ^(2*j*).
3. The window's facets face only those five directions.
4. **[observed 45/45, argued via de Bruijn, not proven]** A choice about a family-*j* ribbon cuts
   along ζ^(2*j*).

**Where I'd most value your scrutiny:**

- Step 4's missing piece: are two options of a forced-growth choice always one ribbon's track apart?
- Whether "settled vs built" is stated carefully enough. The settledness is inferred through the cut,
  not checked against every possible completion.

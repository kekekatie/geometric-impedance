# Slack: is each choice the reader taking in one digit?

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). Voted for by Katie, Gemini and Astra; the idea comes from
Fable's horizon note ("distance-to-the-wall is a novelty budget").*

**The measure.** A world's **wiggle room** F is the set of positions (offsets) in the hidden window
that are consistent with every vertex the world has laid. It is the part of the "hidden number" not
yet read. Its area shrinks as the reader learns more.

**The data.**

- 24 ordinary worlds (`../thread_influence/` set-up), with F tracked every slice and at every two-way
  choice.
- 8 decapod worlds (`../perp_map/` M2).

## Scorecard

| | prediction | result | |
|---|---|---|---|
| S0 | F is never empty in ordinary worlds | 14 empty records, **all in world 14** (see below) | ❌ FAILED |
| S1 | forced growth never costs wiggle room (≥ 99% of forced slices unchanged) | **2,581 / 2,599 (99.3%)** | ✅ HELD |
| S2 | each choice cuts F cleanly in two (≥ 90%), measured right after the option's single tile | 18 / 67 | ❌ FAILED (measured too early; see below) |
| S3 | the cut is golden: smaller share within 0.05 of 0.382 in ≥ 60% | 11 / 67 as registered | ❌ FAILED |
| S4 | decapod worlds end with zero wiggle room | **8 / 8: exactly 0** (0 guesses) | ✅ HELD |

## What the follow-ups showed (exploratory: [`followup_EXPLORATORY.py`](followup_EXPLORATORY.py), [`results/followup_EXPLORATORY.txt`](results/followup_EXPLORATORY.txt), [`results/timing_EXPLORATORY.txt`](results/timing_EXPLORATORY.txt))

1. **S2 failed because I measured too early.** A single half-tile adds few corners, so it barely
   constrains anything. The typical record was "option B keeps 100%, option A keeps 62%".
   - With each option grown on for up to 8 slices of forced growth, **65 of 67 choices cut F cleanly
     in two**: zero overlap, and the two pieces add up to 100%.
   - **The two alternative presents divide the hidden possibilities between them exactly.**
2. **All 18 of S1's exceptions came exactly one slice after a choice.** They are the choice's own cut
   being completed as its neighbours are forced. **Forced growth by itself never costs wiggle room.**
3. **The cuts are golden.** The smaller piece's share:

   | share | 0.382 (1/τ²) | 0.236 (1/τ³) | 0.309 (1/(2τ)) | 0.276 | 0.146 (1/τ⁴) | 0.5 | 0.191 | 0.447 (1/√5) |
   |---|---|---|---|---|---|---|---|---|
   | choices | **25** | **17** | 11 | 6 | 2 | 2 | 1 | 1 |

   - A fair coin's half appeared only twice.
   - In the real growing world, the wiggle room kept per choice was 0.382, 0.618, 0.691, 0.724 or
     0.764 in almost every case. The median is 0.53 bits per choice.
   - S3 as registered (≥ 60% at 0.382) still fails. But the hidden number is plainly being read in
     **golden-ratio proportions**, not in binary halves.
4. **Two choices had a dead option.** In 2 of 67 choices, one option was consistent with **no**
   position in the window at all: it belongs to no perfect Penrose tiling.
   - **World 14 took one** (slice 15). Its wiggle room became empty (the 14 S0 records), and **it
     jammed 14 slices later**, the only one of 24 worlds to jam.
   - So a locally legal choice can lead off every possible world. This is a Penrose "deception", and
     the wiggle room detects it the moment it happens, long before the jam.
5. **Decapods are pinned almost at once.** The bare decapod ring has a *large* wiggle room (0.59–0.67,
   about ten times an ordinary seed). After **one slice** of growth it is exactly zero, and stays
   there. The decapod world's hidden position is fully fixed from the start. That's why it never needs
   to guess.

## What it means (plainly)

- **"A choice is the reader taking in a digit of the hidden number" now has a measurement behind it.**
  - Forced growth reads nothing new: it costs no wiggle room.
  - Each two-way choice splits the remaining possibilities between the two alternative presents,
    exactly, with no overlap and nothing left over.
- **The digits are golden, not binary.** The splits come in golden-ratio proportions (0.382 / 0.618
  most often). In plain terms, the hidden number is read the way a Fibonacci-based number system reads
  numbers. This fits a tiling built on the golden ratio, so nothing is imported. *(Interpretation; S3
  as registered failed.)*
- **The decapod is a world whose hidden number is already fully read.** Zero wiggle room after one
  slice, so nothing is left to guess. This is the measured version of "on the wall, no choices".
- **A wrong turn is visible immediately.** A choice that is legal *locally* can still leave no
  consistent hidden number. Wiggle room zero means that world is doomed, and it jams later.
- **What this does *not* show:** anything about mass or decay. The decapod's zero slack belongs to the
  *whole* world, not to a small local knot.

## Limits

- Only 67 choices, in shared-history worlds.
- The window and its orientation come from `../window_cells/`.
- The boundary of the window is included. Areas below 10⁻⁹ count as zero.
- Follow-ups 1–5 are post hoc.

## Files

- `slack.py`: the study
- `followup_EXPLORATORY.py`: grown-sibling cuts, empties, cost per choice
- `results/slack_report.txt`, `results/run.log`, `results/worlds.json`
- `results/followup_EXPLORATORY.txt`, `results/followup_run.log`, `results/timing_EXPLORATORY.txt`

# The cut's direction in the window predicts the ribbon family of what the world builds

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). It grew out of Katie and Argon's Ammann-bar picture, and
Katie's rule that nothing outruns the now.*

**Why.** A two-way choice cuts the wiggle room F along one straight line. In the world, a choice
decides mostly one ribbon lying along the now. Are these the same event seen from two sides? If so, the
window *settles* which ribbon will be laid before the world has *built* it.

**The set-up.**

- 24 fresh worlds gave 67 live two-way choices, which are 45 distinct situations.
- For each choice:
  - the cut line between the two options' pieces of F, read right after the choice;
  - both futures grown 20 slices;
  - the **decided strip**: tiles one future has where the other has a different tile.
- The lookup table "cut direction → ribbon family" was learned on worlds 0–11 and tested on 12–23.

> **Corrections after Astra's review (2026-10-15).** The results stand; these notes change what they
> show.
>
> 1. **A family is not a single ribbon.** C1 counts how many changed tiles have an edge of each family.
>    It does not trace one connected ribbon, and the top family's share is about two-thirds. So the
>    finding is: *in all 45 sampled configurations, the separating window facet identifies the
>    dominant edge family of the changed region that is observed later.* Whether a single connected
>    ribbon organises that difference is **untested**.
> 2. **"Predicts", not yet "settles".** During the 20 slices, each sibling could make further guesses.
>    These weren't recorded, and the same random seed doesn't guarantee equivalent later choices. Also,
>    the cut was read after the first forced slice, not from the choice tile alone. What's shown: *an
>    early window constraint predicts the orientation of a difference that is built over the following
>    slices.* Showing that it *settles* that difference needs alternative continuations within each
>    branch.
> 3. **The 0.9 edges per slice is not a measured speed limit.** It is a pooled regression of when
>    changed-strip tiles were placed against their distance from the choice point (4,331 tile
>    observations, so bigger strips weigh more). It is a characteristic distance–time relationship in
>    these runs, not an earliest-arrival front. Comparing it with `speed_of_light/` would need matching
>    definitions. ("Nothing outruns the front" remains true by construction, since tiles only attach
>    at the frontier, and `speed_of_light/` measured it directly. This fit just isn't evidence for it.)
> 4. **A better baseline for C2.** The 17 held-out cases contain only three families (0: 11, 2: 3,
>    4: 3), so always guessing family 0 would already score 11/17. The table's 17/17 beats that. The
>    five-direction correspondence comes from the corrected analysis of all 45 cases, *including*
>    training. The registered scorecard and the corrected analysis are kept separate.
> 5. **"Perpendicular by construction" was too strong.** Gluing across parallel edges makes a ribbon
>    connected. It does not force every finite zigzag to have an exactly perpendicular axis (that
>    holds on average, with bounded wiggle). The close agreement of the finite strips (C4) is an
>    **observation**.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| C1 | each choice decides mainly **one** ribbon family (top family beats the next by ≥ 0.15, in ≥ 70%) | **44 / 45**; top share ~0.67 (baseline ~0.4) | ✅ HELD |
| C2 | the cut's direction predicts the family in held-out worlds (≥ 80%; chance ~20%) | **17 / 17** (always-family-0 would score 11/17; see correction 4) | ✅ HELD |
| C3 | the learned table is one-to-one | 4 directions → 4 different families | ✅ HELD |
| C4 | the strip runs perpendicular to its family's edges (within 20°, in ≥ 70% of elongated strips) | **41 / 41**, all within 3° | ✅ HELD |

> **A binning mistake, reported openly.**
>
> - I registered cut directions as "rounded to the nearest multiple of 36°". The real cut lines sit at
>   **18°, 54°, 90°, 126° and 162°** (18° + multiples of 36°).
> - So my bins merged 126° and 162° into one bin, "144°". That is why training saw that bin split
>   between two families (5 and 3).
> - The registered results still stand as computed. C2's test cases happened to fall in unmixed bins.
> - With the correct bins ([`figure_EXPLORATORY.py`](figure_EXPLORATORY.py),
>   [`results/corrected_EXPLORATORY.txt`](results/corrected_EXPLORATORY.txt)):
>   - all **five** directions appear;
>   - each names exactly **one** family, all five families are used, and that holds in **45 / 45**
>     situations.

![cut direction](figures/cut_direction.png)

*Left: every situation's cut direction in the window against its decided strip's direction in the
world, coloured by ribbon family. All the elongated strips sit on one rule (dotted). Right: when each
changed-strip tile was placed, against its distance from the choice point. The cut is read right after
the choice, and the strip is built over the following slices. (Pooled over tiles; not a speed limit.
See correction 3.)*

## What it means (plainly)

- **The window's cut predicts the dominant ribbon family.** Each of the five possible cut directions
  in the wiggle room goes with exactly one of the five families (45/45, corrected bins): family *j* ↔
  cut line at 90° − 36°·*j*.
  - The changed strip then runs perpendicular to that family's edges, as a ribbon of that family
    would. Whether it *is* one connected ribbon is untested.
  - In physical directions, for every elongated strip (within 2.6°):
    **strip direction = 108° − 2 × cut direction**.
  - The factor of −2 comes from the map between the world and the window, which doubles angles (see
    `DERIVATION.md`). The arithmetic is exact. The steps behind it are partly observed.
- **Known early, built later, with "settled" still to be shown.**
  - Right after the choice, the cut in the window already predicts which family the changed strip
    will belong to, and which way it will run.
  - In the world, the strip's tiles are placed over the following slices. Pooled, the placement slice
    ≈ 2.4 + 1.1 × distance (a characteristic relationship, not a speed limit; correction 3).
  - Whether the cut *settles* the strip (the same strip under any later continuation) or only
    *predicts* it is the next test (correction 2).
- **This connects Argon's Ammann-bar picture to our data,** with Katie's correction built in: the
  strip is laid one click per slice, inside the world, along the now.

## The derivation

[`DERIVATION.md`](DERIVATION.md) sketches why the rule holds: ribbons run across their edges,
the lift-to-window map doubles angles, the window's facets face only five directions, and a choice
about a family-*j* ribbon cuts along that family's window direction. The last step is observed in
45/45 situations and argued from de Bruijn's picture, but not yet proven. Numerical checks:
[`derivation_check_EXPLORATORY.py`](derivation_check_EXPLORATORY.py).

## Limits

- 45 distinct situations; the 54° and 162° directions are rare (1 and 3 situations).
- Lookup table learned, not derived; the −2 rule is a strong hint, not a proof.
- 20-slice window; strips still growing were measured as they stood.
- Four strips were not elongated, and two of those sit 62° off the rule. Their "axis" isn't
  meaningful.
- "Built at slice s" uses each future's own growth, including any later guesses (not recorded).
  Settledness is not shown; see correction 2.

## Files

- `cut_direction.py`: the study. Writes `results/cut_direction_report.txt`, `results/worlds.json`,
  `results/run.log`.
- `figure_EXPLORATORY.py`: corrected binning, the rule, and the figure. Writes
  `results/corrected_EXPLORATORY.txt` and `figures/cut_direction.png`.

# Carry the disagreement forward: what if a world never jams?

*Pre-registration, written and committed before any code for this study exists. From Katie's doozy
(2026-10-20): "a real universe never jams; it carries the disagreement forward: more now, more now".
This tests the campfire gods #5 (allow mistakes, and see whether they heal) and #6 (the unhealed
mistakes *are* the stuff).*

## Where this comes from

In `local_nows/`, every world with impatient local nows (R = 3) jammed, at a median of 16 slices.
A jam is a frontier edge where no tile passes the rules:

- it must not overlap anything;
- every corner it touches must still look like part of a legal Penrose vertex, including the
  decorations (arrows).

## The rule: carry on instead of jamming

At an edge where no tile passes the rules, place a **least-bad** tile:

- among tiles that fit **geometrically** (no overlap; no corner over 360°), choose the one that
  turns the fewest currently-legal corners into illegal ones;
- break ties at random;
- corners that are already illegal don't count again.

A **defect** is a vertex whose surrounding tiles don't form a legal Penrose arrangement (`vertex_ok`
fails). Everything else is unchanged: the LOCAL scheduler of `local_nows/` with R = 3, the same 24
seeds, grown to 1500 added tiles or 300 slices. A world stops early only if even a least-bad tile is
impossible.

## Measures

- **Defects over time:** total number, and how many sit on the frontier (where growth is still
  happening).
- **Carried forward:** at the end, at least one frontier vertex is a defect. The disagreement is
  still at the front, being re-made, not left behind in the interior.
- **Shape of the defect set:** for worlds with ≥ 10 defect vertices, the elongation (square root of
  the ratio of the principal variances of defect positions).

## Predictions (fixed now)

**M1: No more jams.** With least-bad placement, at least 20 of 24 worlds reach 1500 added tiles.
Confidence about 70%.

**M2: The disagreement is carried, not healed.** In at least 50% of worlds that place any least-bad
tile, the defect set still touches the frontier at the end. Confidence about 50%.

**M3: Scars are lines, not blobs.** Among worlds with ≥ 10 defect vertices, the elongation is ≥ 3
in at least 50%. Confidence about 45%.

## Reported, not tested

- Least-bad placements per world, and the share of all tiles they make up.
- Whether frontier defects stay roughly constant in number (a scar re-made at a steady size) or
  keep growing.
- The same rule under the GLOBAL scheduler, which rarely needs it, for comparison.

## Limits I already know

- "Least-bad" is one choice of repair rule. Others, such as removing tiles, could behave
  differently.
- A defect vertex can never become legal again (tiles are never removed). So "healing" can only mean
  defects stop being *added* and get left behind in the interior, not that they disappear.
- Same 24 seeds as `local_nows/`.

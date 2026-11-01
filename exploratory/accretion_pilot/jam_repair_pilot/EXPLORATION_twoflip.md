# Exploration — does a coordinated two-flip un-jam, where one flip cannot?

*2026-11-01, follow-up to the pilot. Exploratory, not part of the frozen
protocol. One free question chased for its own sake.*

## Why this question

Phase 3 found no single three-rhombus flip is legal in the surrounding skin.
Phase 4 found the jam's contradiction lives *inside* the skin itself
(`F(skin)=0`), not in the buried tiles the repair worker can't see. So the
obstruction to repair looked like **rigidity**, not burial: one flip is vetoed
because it would break a single boundary-vertex star the surround holds fixed.
The natural follow-up: can a **coordinated pair** of flips — two hexagons sharing
the stuck vertex, the beginning of a Penrose "worm" — relieve what one cannot?

## What I ran

On the jam skins for `w7-B-s0` (jam 23) and `w5-B-s0` (jam 42), with the frozen
engine and no relaxed rules (`src/explore_twoflip.py`):

- enumerate interior three-rhombus flip hexagons near the dead sites, each with
  its unique phason alternative;
- form every tile-disjoint **pair** and apply both flips at once;
- check the combined rearrangement is **fully legal** (every affected tile legal
  against the rest, authoritative — verified the checker returns True on the
  unchanged skin and on original dissections), keeps the **true frontier**
  unchanged, and gives the **dead sites candidates**.

## What happened

| | w7-B-s0 | w5-B-s0 |
|---|---|---|
| flip hexagons near dead sites | 15 | 20 |
| interior hexagons with a phason alt | 10 | 15 |
| tile-disjoint two-flip pairs tried | 41 | 95 |
| **jointly legal (any)** | **0** | **0** |
| jointly legal AND un-jam | 0 | 0 |

Not a single pair of hexagon flips is even **jointly legal** — let alone
un-jamming. This sits alongside: **0 legal single flips** in the jam skins
(0/40 tested) and **0 legal single flips in the perfect reference tiling**
(0/240, from the Phase-3 validation).

## Reading it

The consistent picture, across the jam skins *and* a perfect Penrose patch, is
that **no legal local hexagon flip exists under the engine's strict decorated
atlas** — single or paired. A simpleton/phason flip, applied to a fixed patch
with its surroundings held, always forces a forbidden vertex star somewhere. The
retained skin is **locally rigid**.

So the obstruction to single-move repair is not where the jam sits, and not that
the broken part is buried — it is this rigidity. Two independent flips only
compound two independent violations, so a disjoint pair is, if anything, *more*
constrained than one. The very strictness that lets the surviving ring provably
remember the deleted A/B choice (the closure's headline) is the same strictness
that forbids a legal local reconfiguration. **Memory and un-repairability look
like two faces of the same rigidity** — which rhymes with this repo's
"imperfection must remember, at a quantum equal to its misfit": a phason flip
here *is* a misfit, i.e. itself a defect, so "repair by a legal flip" is close to
a contradiction in terms.

## Honest limits

- Two jams, one move family. Not a theorem.
- I tested single flips and **tile-disjoint** pairs. A genuine coordinated
  **chain-worm** (overlapping hexagons flipped as one move, sharing tiles) is a
  larger move class I did **not** implement; "disjoint pairs fail" does not by
  itself close the worm question. The fact that even a perfect Penrose tiling
  admits no legal single flip here suggests the strict atlas forbids isolated
  phason moves generally, but a chained worm is a separate, explicit test.
- No claim about real-quasicrystal elasticity, phason energetics, or the infinite
  ensemble (where phason flips do exist as degrees of freedom). This is strictly
  about legal local moves in the engine's finite, strict-matching model.

Reproduce: `python src/explore_twoflip.py 7 0 23` and `... 5 0 42`.

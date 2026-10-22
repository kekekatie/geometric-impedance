# A local response: one neighbour settles an open option

We returned to the alternative-at-29 history. The fixed target edge has two candidates after slice 44, one after slice 45, and receives the surviving candidate during slice 46.

## What the intervention tests found

Slice 45 adds 19 half-tiles. Exactly one of these—the second in the recorded placement order—is sufficient on its own, when added to the preceding patch, to remove the rejected candidate while retaining the survivor. This addition is itself legal on the preceding patch.

Omitting that tile while retaining the other 18 restores both candidates. Omitting any other single addition leaves the final one-candidate state unchanged. Thus this tile is sufficient and necessary within the tested set of observed additions. We did not search all possible alternative growth histories.

The actual sequence also agrees: after the first addition both options remain; after the second, only the survivor remains. The candidate is not rejected for overlap or duplication. It fails the historical engine's vertex-compatibility check at one corner, at rounded physical coordinates (0.383516, 0.145898). No claim is made that this is a physical force or an interaction law for matter.

The before/full outcomes and all 19 singleton-addition outcomes also match when queried using only whole tiles with a vertex within 2*S of the original edge's midpoint. These 21 local checks support a nearby-geometry explanation for this event. They are fixed-edge diagnostic queries, not new autonomous skin simulations, and newly exposed artificial edges are never queried.

## How to read the illustration

Purple outline: the candidate later ruled out. Blue outline: the surviving candidate. Orange: observed added tiles. Both outlines are alternatives, not two simultaneously placed tiles. The middle panel adds only the decisive neighbouring tile; it is a legal partial construction step, not a separately simulated scheduler history. Omission patches are diagnostic altered states, not established alternative legal histories.

## Why this is useful

It identifies the mechanism behind the earlier phrase “local possibility settled by its surroundings.” The change is carried by a specific local corner constraint, rather than by all the distant construction completed in that slice. It does not demonstrate a persistent object, mass, a new dimension or a universal response pattern.

This is one targeted case. A sensible next question is whether the same decorated corner configuration repeatedly produces the same option change elsewhere, and how often different neighbouring arrangements leave alternatives open. That would turn a single event into a response catalogue with explicit controls.

## Reproduction

LOCAL_RESPONSE_PLAN.md records the scope chosen before running. local_response.py uses the saved ancestry-test/alternative.pkl and choice-tracking/inventory.json with the original engine through figures.py. measurements.json records every singleton and omission, sequential prefixes, rejection reasons and local checks. Pair tests were unnecessary because a singleton sufficed; no claim of exhaustive multi-tile interactions is made.

Case 180fb0b920bb845b, original continuation 1 with the slice-29 alternative swapped. Original baseline d4e00c5d4396c38bd69b265907b5f3d6c5bc030a. This observer analysis does not alter any growth rule or earlier result. The source script requires the established research checkout and Python environment.

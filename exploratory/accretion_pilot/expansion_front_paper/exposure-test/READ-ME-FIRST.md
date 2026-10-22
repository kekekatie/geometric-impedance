# What exposes the next choice?

Open OPEN-EXPOSURE-TEST.html for two three-panel illustrations. Each compares the preceding patch, a diagnostic addition of just one tile, and the actual completed construction step.

## Findings

Both examined sites are in continuation 1 of the existing case.

| Selected choice | Exposing forced tile added | First observed open | Selected |
|---|---:|---:|---:|
| Newly appearing site | During slice 43 | Before slice 44 | Slice 44 |
| Waiting site | During slice 19 | Before slice 20 | Slice 29 |

In both cases:

- The target edge is absent from the preceding patch's frontier.
- Exactly one of the newly added tiles supports that edge after the step.
- That exposing tile was already a unique candidate on an existing frontier edge before the step, and passed the engine's legality check.
- Adding only that tile to the preceding patch exposes the target edge with exactly the same two candidate identities as after the complete step.
- Omitting the exposing tile from the completed patch removes the target frontier edge. Omitting each other tile added in that step, one at a time, leaves the two alternatives unchanged.

Slice 43 added two tiles in total; slice 19 added five. The pre-existing tile supporting the exposing tile's unique-candidate edge was added at slice 42 and slice 18, respectively. These are immediate geometric support links; they do not identify every constraint that made a placement forced.

## Interpretation

This supports a concrete local statement: a forced placement can expose a new edge with multiple alternatives. It happens for both the immediately selected and the waiting opportunity. The earlier inventory showed that the waiting site's alternatives stayed unchanged until selection at slice 29.

Creation and selection are distinct events. Selection depends on the original patient scheduler: forced placements have priority, and guessing chooses the frontier edge nearest the coordinate origin. The waiting period should not be interpreted as a measured physical lifetime.

The one-tile additions are verified legal diagnostic partial steps; they are not complete scheduler steps. Omission patches are structural diagnostic tests, not newly simulated legal histories. Removing the sole supporting tile necessarily removes its frontier edge; the more informative check is that adding it alone suffices to recover the exact candidate set.

These tests do not show that the earlier choice uniquely caused the exposing tile, nor establish a moving question, a knot, or any physical particle. They also do not exclude equivalent alternatives reachable through other edges. The claim concerns the particular selected edge in these saved states.

## Reproduction

exposure_test.py uses the existing choice-tracking/replay.pkl and inventory.json plus the original engine through figures.py. It runs in the expansion_front_paper folder; the packaged script is a provenance record rather than a standalone installation. measurements.json records candidate identities, support tiles, singleton certificates and every omission result.

Case 180fb0b920bb845b, B continuation 1, stream 20810350027; original baseline d4e00c5d4396c38bd69b265907b5f3d6c5bc030a. This is a targeted exploratory test of two sites, not a population study.

The next stronger test would trace the exposing tiles' dependencies further backwards, checking what changes when an earlier admissible choice is altered. Adjacent support alone is insufficient to claim complete causal ancestry.

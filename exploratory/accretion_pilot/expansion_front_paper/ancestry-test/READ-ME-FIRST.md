# Following the support backwards

The 16-tile attachment-support graph reaches the chosen tile at slice 29. It branches and rejoins before arriving at the exposing tile at slice 43. Each arrow records that the earlier tile supports an edge on which the later tile was the sole candidate in its actual pre-placement patch. Several incoming arrows can represent alternative singleton certificates, not necessarily jointly required inputs. This is not a complete constraint or causal graph.

## The paired test

We reproduced the original trajectory through slice 28 exactly, consumed the same random draw at slice 29 but placed the other of the two legal candidates, then used the unchanged original scheduler and continued to slice 60. There were no subsequent guesses or jams in the alternative run. Thus no later random choice explains the difference before the target opportunity is resolved.

| Observation | Original option at 29 | Alternative option at 29 |
|---|---|---|
| Exposing tile added | During slice 43 | During slice 44 |
| Same target edge has the same two alternatives | Before slice 44 | Before slice 45 |
| What happens next | Selected as a guess at 44 | Forced growth continues elsewhere during 45 |
| Following state | Already selected | Only one candidate before 46; that tile is added during 46 |

The alternative therefore changes timing and whether this site needs a guess. It does not eliminate the site or its brief two-option state. This is a causal effect of the intervention under this scheduler, in this one paired case; it does not establish scheduler-independent behaviour, a physical particle, or a unique propagating question.

## Constraint check

For the exposing tile at 43, we retained its attaching support tile and separately omitted each of the other 267 pre-existing tiles. None of those single omissions changed the sole candidate at that fixed attachment edge. This does not establish absence of other constraints: several tiles may constrain redundantly, and joint removals were not tested. These are diagnostic altered patches, not valid alternative growth histories.

## What this suggests testing next

Inspect the additions during alternative slice 45 that reduce the target's two candidates to one. The clean question is which new constraint removes the other option, and whether this effect requires one tile or several. That can be tested with the same fixed-site addition and omission method, without assuming a moving object.

## Reproduction

ancestry_test.py runs in expansion_front_paper alongside the existing figures.py, choice_tracking.py and exposure_test.py, using their saved caches. ancestry_package.py verifies that the remaining candidate is actually added during slice 46 and writes this report. Packaged scripts are provenance records, not a standalone installation. measurements.json includes the full support graph, omission count and alternative trajectory observations; alternative.pkl stores geometry. Case 180fb0b920bb845b, continuation 1, stream 20810350027, original research baseline d4e00c5d4396c38bd69b265907b5f3d6c5bc030a. Two-history exploratory test through slice 60.

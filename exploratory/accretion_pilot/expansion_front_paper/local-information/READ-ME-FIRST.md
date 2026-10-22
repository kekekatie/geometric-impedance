# Local information and the proposed present

We keep two roles separate: an observer may retain a history for analysis, while the simulated rule must be audited for the information it actually uses. These tests concern the latter, at fixed sites in saved states.

## Result

All 841 frontier-edge observations matched the full patch's exact decorated candidate sets at every tested radius: 1, 2, 3, 4 and 6 in the engine's S length units (4,205 comparisons total). At radius 1, the neighbourhood retained an average 8.64 half-tiles, averaging 2.71% of the corresponding complete patch. There were no extra or missing candidate tiles at any tested radius.

## What was tested

Fifteen saved states: continuations 1 and 3 after slices 11, 19, 28, 42, 44 and 59, plus the changed-slice-29 history after slices 43, 44 and 45. Every original frontier edge in each state was queried. These are repeated observations in related histories, not 841 independent worlds. The list of states and radii was fixed in the script before inspecting results.

A neighbourhood retains each whole tile with any vertex within R*S of the queried edge's midpoint. Retained tiles can extend beyond that circle. This is a lateral spatial neighbourhood around a site, not a layer count measured backwards from the front. Smaller radii were not tested, so no minimum width is established.

Only original frontier edges are queried, with their original orientation/support information. Artificial edges exposed by cutting away tiles are never queried or grown. This prevents the earlier hole-refill problem, but means we have not demonstrated that a truncated patch can autonomously maintain its own frontier. Membership in the neighbourhood is selected using the recorded full geometry.

## Interpretation boundary

Supported here: the full engine's local candidate decisions at these sites can be reproduced from nearby retained geometry. A whole archive was unnecessary for these particular queries.

Not established: a physical thickness of now; globally extendible choices; a theorem for all patches; evolution using only a bounded moving band; or a scheduler that operates without global coordination. The original scheduler still waits until no forced site remains anywhere before making a guess, and prioritises by distance from a global origin. This test does not change that rule.

Future ancestry and propagation reports should identify whether a finding concerns local admissibility, scheduler selection, or an observer's reconstruction. The recent waiting times belong partly to scheduler selection and should not be interpreted as local physical lifetimes.

## Next useful test

Before changing scheduling, maintain an explicit active boundary with enough incident-tile information, keeping the archive available only to an independent verifier. Compare candidates and updates against the reference throughout growth. This would test whether the neighbourhood result can be turned into a working present-state representation. Scheduling locality remains a separate experiment.

## Reproduction

local_information_test.py and local_information_package.py run in expansion_front_paper with figures.py and the existing replay caches. Included scripts are records, not a standalone installation. measurements.json records all comparisons including retained sizes and candidate-set discrepancies. Original case 180fb0b920bb845b; baseline d4e00c5d4396c38bd69b265907b5f3d6c5bc030a. Exploratory finite-state audit.

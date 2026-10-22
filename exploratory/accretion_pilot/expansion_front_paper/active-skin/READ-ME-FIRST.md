# Active skin: a self-maintaining retained-state engine

Open WATCH-ACTIVE-SKIN.html. Choose a history and scrub the checkpoints. The verifier's archived interior is pale grey on the left; the engine's actual retained tiles are blue on both panels. Pink marks the true frontier. The engine has no stored discarded interior geometry in its maintained state.

## Result

All 310 steps passed: 21185 pre-step frontier-edge candidate-set comparisons, all step outcomes and ordered placements, and every post-step frontier. Retained tiles were also checked against the verifier's archive. Both original histories reproduce the earlier cached states through slice 20. See results.json for jams/status and per-step counts.

| History | Steps checked | Final retained half-tiles | Full archive | Retained fraction |
|---|---:|---:|---:|---:|
| continuation-1 | 70 | 456 | 883 | 51.6% |
| continuation-3 | 120 | 497 | 1056 | 47.1% |
| alternative-29 | 120 | 538 | 1180 | 45.6% |

The radius was fixed at 2*S before the run. No mismatch was repaired from the archive and no radius adjustment was made. This is a finite replay test on three related histories, not a universal guarantee.

**Continuation 1 jams at step 70 in both engines.** The other histories reach 120 without a jam. Agreement includes reproducing this failure, not solving it. The continuation-1 viewer's last illustrated checkpoint is 60, before the jam; its table records the actual stopping state at 70. A locally legal guess need not permit indefinite consistent growth.

## What the engine keeps

- Whole tiles with at least one vertex within 2*S of a true-frontier vertex, recomputed from retained state after each step. Whole tiles extend beyond the retention radius.
- An explicit true-frontier map, updated by the edges of newly placed tiles. It is never reconstructed from a cropped patch's exposed edges.
- Vertex/overlap indexes rebuilt from retained tiles, fixed matching-rule templates, a random generator and the step number.

The initial seed is supplied once. The growing engine runs in a separate process and accepts only STEP or STOP after initialization. It sends its decisions out, but receives no verifier results, geometric corrections or replacement tiles. This is an inspected program architecture, not an operating-system security sandbox. Fixed template tables are part of the rules, not a record of this history.

## What the verifier does

In the controller process, the full patch evolves independently using the historical candidate rules and patient scheduler. It compares candidate identities, step status/kind/count, exact ordered tile additions and frontier identities. Comparisons stop the experiment on mismatch; they cannot repair the worker. The checker shares the historical legality implementation, so it tests retained-state equivalence, not independent mathematical correctness of those rules.

## What this does and does not establish

In these runs, the retained representation maintained its frontier and matched full-history decisions throughout growth. This goes beyond extracting a local neighbourhood from a full archive at every query. Discarding happened in the worker; only the verifier kept the history.

The engine still coordinates across the whole frontier: forced growth anywhere has priority before a guess, and origin-distance ordering selects the guessed edge. Thus it is not yet an autonomous local scheduler. The skin's thickness is an engineering choice, not a measured physical present. Total memory can grow with frontier length; it is not fixed-size memory. Unexpected future geometries may expose failures, so a universal bound is not claimed.

No particles, physical time, or a physical expanding universe are identified by this experiment. Historical interpretation may use the archive, but the growth worker's decisions cannot.

## Reproduction and next step

ACTIVE_SKIN_PLAN.md records the protocol. active_skin_engine.py contains the state and worker; active_skin_verify.py runs comparisons; active_skin_present.py creates observer visuals. Run inside expansion_front_paper with its earlier figures.py and results/geometry.pkl, using the established Python environment. Packaged scripts are records, not a standalone installation. Original case 180fb0b920bb845b, continuations 1 and 3, plus the altered slice-29 history; horizon 120.

Next, test restart from a serialized skin-only state and broaden seeds/shapes before reducing the radius. Investigate scheduling locality as a separately labelled experiment; do not silently change scheduling to support an interpretation.

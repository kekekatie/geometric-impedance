# Verification handback: archive-free post-prune readout
27 October 2026. Post-review verification, not a new preregistered result.

## Answer
**Yes, for all 49 previously scored continuations at step 44, under the declared common coordinate convention.** A fresh-process reader reconstructs the compatibility constraints from surviving skin geometry without deleted tiles or retained per-vertex lift labels. Its regions and hypothesis intersections agree with the historical full-patch-lift calculation within the fixed tolerance.

This establishes the first of the requested claims within a bounded numerical reconstruction: present geometry plus a common coordinate convention and two historical hypotheses suffice in these cases. It does not establish reconstruction from unanchored geometry, blind local decoding, arbitrary future states, or a universal exact theorem.

## Provenance and scope
- Source commit: `a96c88b83a1d80f915dc29e0ffa193a6164f6e77`.
- Verification branch: `codex/archive-free-retrodiction`.
- Result commit: the commit containing this note and its companion code/results; the exported handback and chat record its exact ID.
- Historical source files and results were not changed.
- No closure checkpoints existed in the source directory. Regenerated only the original scored world/option/stream combinations using the original algorithms.
- Regeneration matched saved patch sizes, run lengths, stop reasons, guess steps, choice-departure brackets and areas. Largest saved-area residual: 1.11e-16.
- Original coverage: 22 forks, 88 continuations; 49 scored from 20 forks, 39 censored. No reconstruction failure was reclassified as censoring.

## Results
| Check | Result |
|---|---|
| Scored continuations checked | 49/49 at step 44 |
| Correct / wrong / ambiguous / unreconstructible | 49 / 0 / 0 / 0 |
| Constraint-key sets and reconstructed integer lifts | All identical to restricted reference |
| Largest constraint-bound residual | 2.34e-15 |
| Largest region/intersection area residual | 1.17e-15 |
| Largest polygon-boundary distance | 8.43e-15 |
| Largest physical projection residual | 6.67e-13 rhombus-edge units |
| Hypothesis-order swap | 49/49 passed |
| Consistent nontrivial lift-gauge change | 49/49 passed |
| Omitted vertices, reader and reference | 0 |
| Actual scored-skin components | One per case |
| Synthetic separated surviving pieces | Two components reconstructed without historical bridges |
| Reader input size | 42,331–89,382 bytes (ordinary JSON serialization) |

The declared comparison tolerance was 1e-10 for constraints, areas and polygon boundaries; candidate-area threshold 1e-9 and nonempty-region threshold 1e-12 follow the original scoring. Physical inverse tolerance was 1e-7 edge units. The coefficient search bound was fixed at 128 before the pilot; the maximum normalized coefficient actually reconstructed was 16.

The original data contain ten positive alternative intersections, at most 5.55e-17. The reader's largest alternative intersection is 2.36e-16, still far below the 1e-9 threshold; its smallest selected intersection is 0.003302. Report **zero within numerical tolerance**, not symbolic exact zero. Raw numbers are retained in the JSON outputs.

## Inputs, reference information and interpretation
The payload supplies surviving decorated tiles in current physical coordinates, edge length, fixed projection/window definitions, both hypothesis constraint sets, and:
1. one physical coordinate origin assigned lift zero by the common pre-fork convention;
2. the pre-fork four-layer rank map shared by both branches.

The origin can refer to a now-deleted position. Its two coordinates are explicit reference metadata, not recovered from the present skin. No shape or tile at that origin is supplied. Both it and the rank map are fixed before the A/B commitment. The hypotheses themselves are historical information provided to the analyst.

The reader obtains relative integer lifts solely from current skin edges, separately per connected component. A bounded exhaustive physical-coordinate inverse aligns each component to the common origin. A unique all-ones shift into the declared four-layer slab fixes the layer convention. It rejects ambiguous, out-of-domain or incompatible components rather than consulting the answer or silently omitting vertices.

The reader therefore needs **no retained vertex lift labels**, but does require the declared anchored frame and slab. All 49 cases had zero out-of-slab omissions; extension to skins not fitting that slab is not demonstrated.

## Isolation and checks
The reader is standard-library-only and invoked with `python -I -S` in an empty temporary directory. It receives the payload through stdin. After imports an audit hook blocks file opens, sockets and subprocess execution. No repository engine or archive module is imported. This is auditable process/data separation rather than an OS security sandbox.

Eight meaningful checks passed: unexpected branch-label rejection, missing-origin rejection, off-module geometry rejection, input-tile-order invariance, disconnected-component reconstruction, common physical translation, blocked archive-file access, and ambiguous output for identical compatible hypotheses. Candidate-order and lift-gauge checks additionally run for every scored continuation.

The analyst controller retains reference lifts for comparison, outside the reader. Case envelopes contain a `payload` and a `reference`; only the former is sent to the child process.

## Reporting corrections confirmed
- 49 scored continuations are from **20**, not all 22, forks.
- Two original forks have no scored continuation.
- All scored last steps are 44.
- The original robustness loop samples departure, midpoint and last valid step, not every intervening step.
- This verification compares step 44 only; it does not extend the temporal claim.
- All 39 original censored continuations remain excluded by the original criteria and visible in the source record and summary.
- Numerical zero is not exact symbolic exclusion.

## Reproduce
From repository root, using Python with the parent requirements installed only if regeneration is needed:

```sh
cd exploratory/accretion_pilot/expansion_front_paper/archive-free-reader
python verify_reader.py --verify-only
python test_reader.py
```

Those commands use the saved present-skin inputs and analyst references; **only Python's standard library is needed**. They invoke a fresh archive-free reader for every comparison. No growth is rerun.

For original-case regeneration in a disposable checkout, move `results/cases/` aside, install `../requirements.txt`, then run:

```sh
python verify_reader.py --pilot
python test_reader.py
python verify_reader.py
```

Only original scored cases/streams are regenerated; no new worlds are sampled. The local run used Python 3.12 and the repository's pinned scientific packages.

## Proposed manuscript sentence
> In a post-review verification of the 49 previously scored continuations from 20 forks at step 44, a fresh-process reader using only surviving skin geometry, a declared common coordinate frame and layer convention, and the two supplied historical candidate regions reconstructed the reference compatibility constraints and selected the recorded branch in every case within numerical tolerance, without accessing deleted tiles or retained vertex lift labels; the 39 originally censored continuations remained outside this comparison.

## Deliverables
`skin_reader.py`, `verify_reader.py`, `test_reader.py`, the fixed protocol and README; saved case payloads/references, raw reader outputs, pilot and full comparisons, summary, and check results. This completes the requested bounded verification.

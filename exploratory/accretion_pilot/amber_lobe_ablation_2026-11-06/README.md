# Amber-lobe retention ablation — reproduction

Read `HANDBACK.md` for findings and `protocol/PROTOCOL.md` for the committed pre-outcome definitions and bounds. New experiment only: no frozen scar or referee-check file is modified.

## Provenance and environment

- New clean worktree, base `41a9952edfbe350abfd9e2807e6cb6871d9f4881` (latest fetched referee-check tip at setup).
- Pre-registration commit `62cd04b`; its exact local history is preserved in the delivery bundle.
- Audited continuation baseline: `19981c2b75a76da1787dfab04cfc1a381ec4d68e`.
- Frozen whole-repository engine worktree: `84130b97f5044197392e72cd53e0e71f81b043f3`, unchanged.
- Existing isolated CPython 3.12.16, NumPy 2.2.6, SciPy 1.16.0, Matplotlib 3.10.6 on Windows. Actual paths, versions, dependency hashes and every reused per-case input hash are in `results/provenance.json`.
- Reused independently generated fork cache SHA-256: `b0d8e0d48d4272f943867c0d9c7382423deea88e903080c7a4d09be14a71a879`.

The pre-scar states and full-patch traces are **reused inputs** from the previous independent execution audit, not freshly regenerated baseline growth. Every live-only constructor trial is newly executed in a spawned process. The paired original-band and primary live-only reader grids are newly evaluated, with deterministic exact-payload caching and memoized coordinate inversion. No outcome was inferred from a plot or source inspection alone.

No applicable tracked AGENTS.md/CLAUDE.md was present. Existing parent-workspace instructions from the audit remain applicable. The latest referee source supplies the two conventions; the separate literature handback and canonical `check2_conventions.py` were not required or silently substituted. This run uses the concrete Test-1 prompt and checked referee code.

## Run

Set these environment variables to absolute paths, then use the isolated Python executable:

```powershell
$env:EFP_SNAPSHOT='<frozen-repo>/exploratory/accretion_pilot/expansion_front_paper'
$env:AMBER_BASE_CACHE='<prior-independent-audit-cache>'
$env:AMBER_CACHE='<new-output-cache>'
$env:AMBER_FORK_CACHE='<verified-forks.pkl>'
$env:MPLBACKEND='Agg'
$env:PYTHONUTF8='1'
python src/run_continuation.py
python src/readout_check.py
python tests/test_policy.py
python src/summarize.py
python src/make_figure.py
```

The base cache contains `jam-W-S.pkl`, `verify-W-S.pkl` and `trace-W-S.pkl` for each prescribed case. If absent, regenerate it using the prior audit's `audit_2026-11-05/observe.py` against a disposable checkout of `e4a7503b5273dbc1fa72232de5c29b7048672b0d`, with `AF_REPRO`, `AF_CACHE` and `EFP_SNAPSHOT` configured as documented there and the verified fork cache at its expected path. This is a potentially expensive baseline replay, not part of the live-only intervention. The exact cache hashes used here are recorded; do not silently substitute differently generated data.

The drivers are resumable. Use a fresh experiment output/cache when changing source, dependencies or policy; existing per-case results are otherwise reused as completed trials. `readout_check.py` can run alongside continuation and waits for completed primary trials. `summarize.py` runs after all 33 fixed trials. No restoration continuation ran because the primary completed exactly in all eleven cases.

## Implementation and information boundary

`src/worker.py:LiveSkin.thin` changes only retention. It evaluates non-pinned growable edges on current available geometry, keeps tiles using the frozen vertex-to-endpoint distance convention, rebuilds local indexes, clears additions and removes every boundary owner-tile reference. Incremental true-frontier tags remain; the artificial cavity edges in the local index are never used as construction frontier. Oriented p/q/r records are geometry-bearing metadata and can include coordinates outside retained tiles; their counts are reported.

`run_continuation.prepare` performs the explicit pre-scar zero-candidate reconnaissance before thinning. It asserts that these initial pins equal the original scheduler's first newly pinned set, and preserves PRNG state. At radius3 only, preparation starts from the existing full pre-scar checkpoint to form the wider initial band; a live constructor never recovers previously deleted tiles. Radius1/2 preparation starts from the audited radius2 band.

The spawned `constructor` receives only the resulting serialized state, its fixed collar parameter (zero in every scientific run) and STEP/STOP. Common imports contain paths to caches but do not load those caches in the constructor. Frozen transitive imports retain the previously audited incidental historical-stiffness summary; construction does not consult it. This is process separation and an inspected data flow, not filesystem isolation.

The parent receives actual ordered placements, retained bands and observational query records. It validates each placement against cumulative full history before adding it, stops after the first failure before another worker step, and never supplies repairs or choices. There were no failures. Actual candidate enumeration is compared at decorated-key resolution; actual placements are compared as raw tuples. All recorded step checks are separate booleans, with first mismatches recorded by category. Exact agreement excludes the deliberately moved initial scan's newly-pinned count, and compares normalized post-step scar identities instead.

The post-prune scar monitoring schedule is new and observational. The frozen scheduler does not re-query pinned edges. `query_diagnostics.json` contains only bounded evaluator-copy tests; tile and vertex-summary witnesses never steer any scientific run. Single-deletion minimality is verified for the recorded first-query tile witnesses. A one-vertex summary is sufficient for each recorded first-query diagnostic, but no global minimal summary policy was implemented or claimed.

## Validation and numerical conventions

- 33 finite continuation trials: three radii times eleven correlated labels, 231 post-jam steps. World7/stream0 starts each radius batch.
- Candidate enumeration, outcome, ordered placements/frontier, PRNG transitions and scar identities match; positive progress is separately checked.
- Shared frozen matching-rule engine validates actual placements and full-history complete/partial vertex stars. This is separate evaluator history, not an independently implemented matching-rule oracle.
- Convex clipping provides a separate overlap implementation (adopted by the prior audit/supplement); failure threshold `1e-12` area and clipping-side tolerance `1e-15`. Floating-point residuals are not symbolic certificates.
- Policy controls exercise an all-dormant, zero-retained-tile state: edge guards survive serialization, the scheduler arrests without calling the candidate generator on pinned edges, and cavity edges are not promoted to true frontier.
- Open reader uses native `1e-9` positive hypothesis area and `1e-12` F-area cutoffs. Closed scoring imports referee `check4b_arc_scores.closed_compatible` unchanged: normalized halfplanes, [-50,50] coordinate bounds, SciPy HiGHS default feasibility tolerances. It is a numerical feasibility convention, not exact arithmetic or a newly implemented strict-radius predicate.
- The original full-band native grid reproduces 111 B / 64 ambiguous / 353 empty / 0 A before the live-only grid is scored. Both grids contain exactly 528 requested windows. Original absolute jam-notch anchors remain fixed; each target band has its own centroid. Selection is geometry-only with deterministic largest-component tie-breaking. The same sparse grid, not all connected subsets, is tested.
- No reader scan is performed on radius1/3 or a restoration variant. No A-only witness occurred in either convention. Empty selections, reconstruction failures and unavailable endpoints are kept as explicit zero-count categories.

The illustrative figure was rendered and visually checked. Grey tiles are evaluator history only; amber denotes tiles removed by primary live-only retention, and red denotes retained scar tags.

## Files

`results/w*-r*-c*.json`: complete trial metrics and first differences.
`results/readout-*.json`: every requested window with tile keys, areas, constraints and both verdicts.
`results/retention_summary.json`, `readout_summary.json`, `query_diagnostics.json`, `policy_tests.json`, `provenance.json`: compact evidence and provenance.
`figures/w7_retention.png`: descriptive retention comparison.

Runtime pickle caches remain outside Git. Original logs are included under `logs/`. The delivery receipt records the exact remote commit and verifies its repository tree against the local committed tree. Historical source/results are preserved; no merge or force-push.

# Reproduction — independent archive-free execution audit

Audit date: 2026-11-05 (Australia/Adelaide). The experiment is pinned to `e4a7503b5273dbc1fa72232de5c29b7048672b0d`, branch `claude/scar-archive-free-2026-11-04`. Remote branch lookup at setup returned that same commit. The previous full-patch audit is `3dc43ea844613f2b6e50647f2ffda14616281f68`; frozen engine/reader is `84130b97f5044197392e72cd53e0e71f81b043f3`. No applicable tracked AGENTS.md or CLAUDE.md was found, nor an AGENTS.md in the workspace ancestors checked.

## Isolation and input provenance

Two worktrees were created from the pin: a detached disposable reproduction checkout and branch `audit/archive-free-scar-2026-11-05`. Original scripts write only in the disposable checkout. The audit branch contains additive evidence and two small demonstrated-defect fixes; historical result files are not overwritten there. The frozen worktree is unchanged. The scheduler and jam-replay/reader-adapter source directories have no differences between the previous audit anchor and this experiment pin.

The fork cache is **reused**, not regenerated in this audit. It was independently generated for the earlier audit and reused in the full-patch scar audit. SHA-256:

`b0d8e0d48d4272f943867c0d9c7382423deea88e903080c7a4d09be14a71a879`

It is copied into the expected `exploratory/accretion_pilot/jam_repair_pilot/results/baseline/forks.pkl` location in both new worktrees. All jam replays, full-patch/continuously pruned verification runs, and spawned restarts in this audit are newly executed. The earlier full-patch trace cache is used only as an additional comparison target, never to choose worker placements. Raw trace caches stay outside Git; committed per-step signatures, comparison records and source identify what was checked.

## Environment

Existing isolated CPython 3.12.16 on Windows, NumPy 2.2.6, SciPy 1.16.0, Matplotlib 3.10.6. `results/environment.json` records exact runtime versions, actual loaded module paths and SHA-256 hashes. `results/decision_dependencies.json` includes the runtime functions and their source locations, including the transitive partial-star correction actually installed by the frozen import graph.

The previous audit's isolated `work/scar-venv/Scripts/python.exe` was reused. No engine dependency was upgraded. Git fetch initially failed without network access; after the session network permission was granted, fetching the exact commit succeeded.

## Commands and order

Create the worktrees and set the environment (substitute local absolute paths):

```powershell
git fetch origin e4a7503b5273dbc1fa72232de5c29b7048672b0d
git worktree add --detach <reproduction> e4a7503b5273dbc1fa72232de5c29b7048672b0d
git worktree add -b audit/archive-free-scar-2026-11-05 <audit> e4a7503b5273dbc1fa72232de5c29b7048672b0d
$env:EFP_SNAPSHOT='<frozen-worktree>/exploratory/accretion_pilot/expansion_front_paper'
$env:AF_REPRO='<reproduction>'
$env:AF_CACHE='<new-empty-audit-cache>'
$env:MPLBACKEND='Agg'
$env:PYTHONUTF8='1'
```

Use the audit scripts in this directory with the isolated Python executable:

```powershell
python observe.py
python reproduce_remaining.py
python test_horizon.py
python test_endpoint_lifecycle.py
python test_import_boundary.py
python analyze.py
python finish.py
```

`observe.py` starts with w7-B-s0 and executes the pinned `verify_supplement.verify_case`, then its original `main()` over the eleven prescribed cases. It memoizes only completed same-run verification/jam results. The observer calls the original scheduler, candidate generator, legality predicate and add/prune methods unchanged; it records actual enumeration, legality calls, placements, frontier, PRNG and scars. No cached candidate result is supplied to a constructor.

`reproduce_remaining.py` executes the original `restart_prescar.main()`, `endpoint_geom.main()`, `test_supplement.main()` and `test_failstop.main()`. Repeated full-patch/uninterrupted-worker/endpoint growth helpers are supplied from the newly captured deterministic traces. Thus these report entry points are reproduced with explicit replay-cache reuse, not falsely described as five wholly uncached command-line runs. The same worker lifecycle is exercised directly in the verifier; the original endpoint helper is separately exercised by the lifecycle regression. The scar-adjacency test performs its own bounded original check. The failure-stop test always invokes the real verifier with its injected failure, never a cached success.

Spawned restarts execute the **original** `isolated_worker._worker_proc`, each initialized from a freshly reconstructed pre-scar state. An observational wrapper exports reduced per-step signatures, checks pruned indexes, and overwrites a current retained-state snapshot. It does not receive evaluator geometry or candidate menus. Temporary diagnostic geometry is discarded before the next growth command; the observation log is never read by the worker. The controller sends only STEP/STOP after initialization. Its tag selects an output log filename, not scientific state. The original STEP messages are preserved and compared by the original restart report.

The execution allowed the restart/analysis drivers to wait for each completed verification cache, overlapping bookkeeping with computation. The single-case restart driver temporarily writes one pre-state/result, then restores the complete eleven-case files in original case order. Run `finish.py` only after both drivers finish. No scientifically unsuccessful case is excluded.

## Defect fixtures and affected reruns

`test_horizon.py` first confirms the original contradictory status for a synthetic arrest exactly at step 44. It then runs the corrected verifier with arrest at 44, arrest at 43 and ordinary loop completion. These are status fixtures with synthetic zero-placement steps, explicitly **not** evidence of growth. Actual scientific progress is checked separately at every step.

`test_endpoint_lifecycle.py` feeds the already validated w7 ordered placement transcript to the original and corrected endpoint helpers. This is a lifecycle-only fixture, not a new candidate search. It executes actual ActiveSkin add/prune operations, demonstrates retained deleted tiles in the original additions list, and asserts unchanged raw endpoint tiles after clearing the list. The test intentionally failed against the uncorrected helper, then passed after the one-line fix.

`test_import_boundary.py` repeats only the existing w7 pre-scar restart as a focused information-access control. It replaces the unrelated imported stiffness summary with an empty summary, forbids subsequent stiffness lookups, and disables historical fork/replay APIs. Original worker messages must equal the ordinary restart exactly. An initial version targeted `_STIFF`; source inspection found the relevant name was `window_retrodiction.STIFF`, so the final fixture instruments that name and asserts a consumer was found before claiming coverage.

The two fixes do not change any growth decision. The corrected status is derived from observed endpoint arrest/validation flags, and the endpoint fix discards only an unused transient list. Scientific status/geometry equivalence is established from the freshly executed records; no eleven-case growth repeat or readout rescan was needed.

The original failure-stop test was additionally executed against the corrected verifier and passed. Private observer snapshots named `final_state`/`spawn-state` are used only for geometry: their serializer uses placeholder RNG/scar arguments. Actual RNG/scar transitions are recorded separately from the running scheduler; restart inputs always use the real `prescar_state`, never those diagnostic endpoint snapshots.

## Comparison and validation limits

`results/artifact_comparison.json` separates raw byte agreement, agreement after CRLF/LF normalization, parsed JSON agreement, and every differing numerical/categorical leaf for the four regenerated artifacts. `reproduced/` contains the three regenerated result reports. Pre-scar serialization is compared and hashed without duplicating that large historical file in the audit directory.

Ordered signatures preserve the actual per-edge candidate enumeration used inside the scheduler, each pre-add legality call, placement order, frontier order, PRNG transitions and scar sets. Candidate ordering is not inferred from a sorted inventory. These signatures are compared separately for full-patch vs continuously pruned worker and pre-scar spawned vs continuously pruned worker.

Legality is validated against a separate cumulative evaluator from Sstar+B, before accepting each worker tile. This shares the frozen matching-rule engine and atlas; it is **not an independently implemented matching-rule oracle**. Endpoint complete and partial stars are also checked against that atlas. Convex triangle clipping is a distinct geometry implementation adopted from the prior audit, with positive-area failure threshold `1e-12` and clipping-side tolerance `1e-15`. It is a floating-point check, not symbolic certification.

Decorated position keys round coordinates to six decimal places. Raw coordinate and tile-order checks therefore supplement key equality before reader reuse. The reader thresholds remain unchanged (`1e-9` positive hypothesis area; adapter empty-area cutoff `1e-12`). No reader scan was rerun or enlarged. Declared reader metadata is saved per case; it is computed from the same frozen adapter, fork, birth options, origin/layer conventions and windows as the historical reader inputs.

The fixed experiment scope remains eleven correlated B labels, their prescribed streams and step 44. No fresh worlds, alternative retention policies, longer runs, repair searches or manuscript were added.

# Reproducing this bounded verification

Target: outcome commit `804542e41fbdddecb5a3003fe730d91bd7f24dc8`, experiment `amber_lobe_ablation_2026-11-06`. Audit branch: `audit/amber-lobe-verification-2026-11-07`. All new files are in this audit directory. Original experiment, scar and referee files are unchanged.

## What was executed

Fresh spawned constructor runs for all eleven recorded cases at radii 2, 1 and 3 (33 trials), with the original horizon of 44. The frozen experiment functions are imported without editing their source. The wrapper redirects `common.RESULTS` to `regenerated/` in both parent and spawned imports and uses an initially empty external audit cache. It explicitly enumerates the prescribed 33 trials, so it cannot trigger the original driver's optional restoration-policy expansion. No alternative retention policy, new world or extra reader grid is introduced.

The original/full-band and live-only/2S reader grids were freshly evaluated, with memoization only within this audit's new cache. The reader ran concurrently with continuation, waiting for each completed primary case. Policy controls and original query-summary generation were rerun. A separate diagnostic independently locates the first w7-s0 primary mismatch, tests the reported tile, derives the one-vertex corner record directly from tile coordinates, and guards a diagnostic step36 against pinned-edge queries. A separate instrumented replay of the unchanged w7-s0 constructor to44 observes local variables and runtime file opens; it supplies no restored geometry.

This is separate execution and independent diagnostic logic, **not a separately implemented growth engine or reader**. The prior independently executed baseline traces/checkpoints are hash-verified and reused, as permitted by the original reproduction procedure. Full baseline growth from the seed was not regenerated. The matching-rule evaluator uses the same frozen engine with independent cumulative history; convex clipping is a separate overlap implementation. Do not interpret the word independent as a second formal implementation of all mathematical rules or a different human reviewer.

## Environment and inputs

See `preflight.json`: CPython 3.12.16, NumPy 2.2.6, SciPy 1.16.0, Matplotlib 3.10.6; Windows 11. Frozen whole repository: `84130b97f5044197392e72cd53e0e71f81b043f3`. Five loaded dependency hashes, all 33 reused baseline cache hashes, and the fork checksum match the committed experiment provenance. The frozen worktree was clean. The reader resides in that frozen snapshot; referee code comes from the target outcome tree.

Applicable ancestor `AGENTS.md` paths were checked from the workspace to the filesystem root; none existed. The target tracked repository contains no AGENTS.md/CLAUDE.md. An initial overly broad workspace search hit unrelated inaccessible dependency directories; the targeted ancestor and repository checks resolved the applicable scope. Initial network fetch failed before session network permission was granted; the exact outcome fetch and worktree creation then succeeded.

External inputs (not duplicated into Git):

- `EFP_SNAPSHOT`: frozen repository's `exploratory/accretion_pilot/expansion_front_paper`.
- `AMBER_BASE_CACHE`: previous audit's `jam-W-S.pkl`, `verify-W-S.pkl`, `trace-W-S.pkl`, with exact hashes in `preflight.json`.
- `AMBER_FORK_CACHE`: verified fork pickle, SHA-256 `b0d8e0d48d4272f943867c0d9c7382423deea88e903080c7a4d09be14a71a879`.
- `AMBER_CACHE`: new empty directory for regenerated restart/worker states and reader memoization. This audit used `work/amber-audit-cache`; it never pointed at the prior experiment's cache.

To regenerate missing baseline inputs, follow the original experiment README's documented prior `audit_2026-11-05/observe.py` procedure against its pinned checkout. This verification does not silently replace those inputs or ship the entire historical dependency repository.

## Exact commands and restart

From the original workspace, `src/launch.ps1 PHASE` sets the paths shown in `preflight.json` and calls the isolated Python through `src/execute.py`. Each phase has a complete stdout/stderr log and an `*-execution.json` recording actual argv, UTC start/end, and exit code.

```powershell
& ./src/launch.ps1 preflight
& ./src/launch.ps1 continuation
& ./src/launch.ps1 reader
& ./src/launch.ps1 policy
& ./src/launch.ps1 query
& ./src/launch.ps1 inventory
& ./src/launch.ps1 summary
& ./src/launch.ps1 compare
```

The original commands used the full audit-directory prefix from the workspace root; `logs/*-execution.json` records those absolute paths. Continuation and reader may run concurrently; summary and comparison must wait for both. Query and inventory require the completed fresh w7-s0 primary case. The query and inventory phases are diagnostics of existing cases, not additional scientific trials.

For a new reproduction, create an isolated checkout of the audit branch, choose a **fresh** `regenerated/` output location by copying only the audit harness/docs into a new sibling audit directory, and set the four environment variables above. Then invoke the intended Python executable on `src/execute.py PHASE` directly; `launch.ps1` is a convenience for the recorded workspace layout. Set `PYTHONUTF8=1` and `MPLBACKEND=Agg`. `preflight` requires an empty cache and verifies the target outcome is an ancestor with frozen scientific trees unchanged. Its ancestry check permits the final audit commit; the original run executed while HEAD was exactly the outcome commit.

For an interrupted run, **do not rerun preflight against a populated cache**. Resume `continuation`/`reader` using the same untouched dependencies and outputs. Completed per-case JSONs are skipped by the frozen drivers. Preserve failed logs/results under a new name before rerunning a phase: `execute.py` otherwise replaces that phase's log. Do not reuse existing result JSONs as evidence of a fresh execution.

## Evidence and comparison

- `regenerated/`: complete new per-case, per-window, retention, query and policy results.
- `comparison.json`: strict recursive JSON comparison, preserved discrepancies if any, independent raw-trace comparison/recount and reader tallies. No comparison tolerance is applied. File checksums are also retained; JSON equality is distinguished from byte equality.
- `independent_query.json`: separate first-query and guarded-scheduler evidence.
- `worker_inventory.json`: observed local-state accounting at steps35 and44, and scope of file-open observation.
- `preflight.json`, `logs/`: input/environment provenance and actual executions.

Open scoring retains the original positive-area cutoffs (hypothesis area `1e-9`, F area `1e-12`). Closed scoring uses the unchanged referee HiGHS feasibility test, default solver tolerances and [-50,50] bounds. Overlap reporting retains the original `1e-12` area threshold and `1e-15` clipping-side tolerance. No tolerance was loosened. These are numerical conventions, not exact symbolic open/closed predicates.

Original and regenerated provenance necessarily differ in module paths because the audit is isolated. The summary driver also repeats the original historical protocol/base identifiers; `preflight.json` and this document identify the audit's actual target and run. This administrative path difference is separated from scientific-result comparisons.

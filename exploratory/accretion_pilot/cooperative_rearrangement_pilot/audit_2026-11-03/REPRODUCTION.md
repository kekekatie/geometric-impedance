# Reproduction record

Date: 3 November 2026, Australia/Adelaide. Scope: one pinned pilot and material supporting checks only. Audit branch: `audit/cooperative-rearrangement-2026-11-03`. Final commit/push receipt is supplied with the delivered files and in the handback message; a commit cannot contain its own hash.

## Exact sources and isolation

| Role | Commit |
|---|---|
| Pilot anchor | `fea9554d8626334b09c4744a2f71897a862923cc` |
| Preceding audit | `53692c20c68a03a96b1e682ad8c90e60b764df21` |
| Original diagnostic | `9b3daefe50b250c93c795fbb9cfae089d180c1a4` |
| Frozen engine/reader | `84130b97f5044197392e72cd53e0e71f81b043f3` |

The full frozen identity was resolved by `git rev-parse 84130b9` and matched `engine_bridge.SNAPSHOT_COMMIT`, pilot README and protocol. The freshly fetched `origin/claude/cooperative-rearrangement-pilot` still pointed at the anchor; `git log -5 --all` showed no subsequent commit newer than the pilot among fetched refs. Only that remote branch contained the anchor at inspection. No newer code was substituted.

A fresh `git clone --no-checkout` was made under `work/geometric-impedance`. The pilot was checked out detached and initially clean. Separate detached worktrees were created at `work/efp-snapshot` and `work/reproduction`. The latter is disposable: the original scripts write their usual paths there. The audit branch was created in the primary checkout, where **all historical tracked files remain unchanged**. Results are copied into this audit directory's `reproduced/` subtree. The engine worktree remained clean.

Repository/ancestor `AGENTS.md` checks found none applicable; the pinned tree also contained no `CLAUDE.md` or instruction-named files. The pilot README, frozen protocol, deviations, relevant earlier audit, and source documentation were read. The top-level `THREE_COMMANDMENTS.md` was read as a project origin note. Network access was granted for the session to fetch/push. GitHub connector reads and the cloned repository agreed on the anchor.

## Environment

- Windows reported by Python: `Windows-10-10.0.26200-SP0`.
- Python `3.11.3`, MSC v.1934, 64-bit AMD64.
- Executable: `C:\Users\Karen\AppData\Local\Programs\Python\Python311\python.exe`.
- NumPy `2.2.6`; SciPy `1.16.0`; Matplotlib `3.10.6`.
- Git `2.52.0.windows.1`; `core.autocrlf=true`.
- `MPLBACKEND=Agg`.
- Solver: SciPy `linprog(method='highs')`. Historical defaults retained. Independent margin checks set primal/dual feasibility tolerances to `1e-9`.
- No new Python package installation was needed. Shapely was unavailable; independent geometry checks use the audit's explicit convex polygon clipping instead.
- The pilot recommends Python 3.12/3.13; the available `python` was 3.11.3 and `py -0p` reported no registered installations. This is an explicit environment deviation, not a claim to reproduce its original runtime bit-for-bit.

## Commands

Commands below are PowerShell, from the projectless workspace unless `Set-Location` changes it. Paths are shown explicitly to make the execution reproducible. Git's initial clone can take several minutes.

```powershell
git clone --no-checkout https://github.com/kekekatie/geometric-impedance.git work/geometric-impedance
git -C work/geometric-impedance checkout --detach fea9554d8626334b09c4744a2f71897a862923cc
git -C work/geometric-impedance worktree add --detach ../efp-snapshot 84130b97f5044197392e72cd53e0e71f81b043f3
git -C work/geometric-impedance worktree add --detach ../reproduction fea9554d8626334b09c4744a2f71897a862923cc
git -C work/geometric-impedance switch -c audit/cooperative-rearrangement-2026-11-03
$env:EFP_SNAPSHOT='C:\Users\Karen\Documents\Codex\2026-11-03\g\work\efp-snapshot\exploratory\accretion_pilot\expansion_front_paper'
$env:MPLBACKEND='Agg'
Set-Location work/reproduction/exploratory/accretion_pilot/cooperative_rearrangement_pilot/src
python ../tests/test_coop.py
python export_state.py
python part3_necessary.py
python part4_search.py
python part5_score.py
```

The first `export_state.py` attempt failed with `FileNotFoundError: .../jam_repair_pilot/results/baseline/forks.pkl`. The README documents cache regeneration when absent; this is a setup dependency, not an undisclosed scientific failure. Part 3/4/5 then ran against the committed saved input. The cache was separately regenerated with:

```powershell
# From work/reproduction/exploratory/accretion_pilot/jam_repair_pilot/src
python -u build_fork_cache.py
```

This generated the 22 original fork inputs only; it did not run the 88 continuation arms. The export was then rerun successfully. The original focused tests were repeated against regenerated input, and Part 3 was rerun because exported metadata had last-bit differences. Its count breakdown was unchanged from the saved-input run. Part 4/5 had already run successfully; their saved-input outputs are retained. The regenerated tile geometry, evaluator data, dead sites, rank and boundaries agree exactly, and the independent supplemental replay verifies the same case.

```powershell
# From reproduction .../cooperative_rearrangement_pilot/src
python -u export_state.py
python ../tests/test_coop.py
python ../../jam_compatibility_diagnostic/tests/test_feas.py
python ../../jam_compatibility_diagnostic/audit_2026-11-02/src/test_feas_boundary.py
python -u part3_necessary.py
python make_figure.py
```

Audit commands, from the primary checkout root, with the same environment:

```powershell
python -u exploratory/accretion_pilot/cooperative_rearrangement_pilot/audit_2026-11-03/verify.py
python -u exploratory/accretion_pilot/cooperative_rearrangement_pilot/audit_2026-11-03/supplement.py
python -u exploratory/accretion_pilot/cooperative_rearrangement_pilot/audit_2026-11-03/verify_hex.py
python exploratory/accretion_pilot/cooperative_rearrangement_pilot/audit_2026-11-03/test_regressions.py
python exploratory/accretion_pilot/cooperative_rearrangement_pilot/audit_2026-11-03/compare_reproduction.py ../reproduction
```

The first `verify_hex.py` pass completed all fifteen geometry checks but failed while serializing its corrected frontier result: the audit helper compared a tuple tile key to its JSON list representation. This audit-only serialization bug was corrected by normalizing the key through JSON; the complete script then reran successfully. Two ancillary `git -C work/reproduction diff ...` calls were accidentally issued from inside a deeper working directory and returned “No such file or directory”; the requested read was repeated from the workspace. Neither error changed historical code or scientific outputs.

## Comparison results

`results/comparison.json` records SHA-256 hashes and every structured difference against **original Git blobs**, not a possibly normalized checkout. Windows text writing adds CRLF, so none of these raw output bytes equals the LF Git blob. Distinguish that from normalized/structured equality:

| File | Equal after CRLF normalization? | Structured result |
|---|---|---|
| `input/evaluator_historical.json` | Yes | Exact |
| `results/part4_search.json` | Yes | Exact |
| `results/part5_score.json` | Yes | Exact |
| `input/retained_state.json` | No | Three float fields differ, maximum `1.1102230246251565e-16` |
| `results/part3_necessary.json` | No | Two internal shortcut-count fields differ by 69 |

The retained-input numeric comparison uses absolute tolerance `1e-12`. No discrete difference is treated as a numerical-tolerance match. Part 3's count changes are explicitly not exact agreement: unchanged-binding rejections 2,724 → 2,793; explicit LP rejections 394 → 325. The total, counts by size, no-engulfment count, all final verdicts, facet result, greedy selected vertices and footprint statistics agree exactly. The regenerated metadata does not change this run's count breakdown. Independently reconstructed constraint coefficients agree within `1.333e-15`; use `1e-12` as their comparison threshold.

The figure command is ancillary visualization reproduction. Its output does not supply evidence for the numerical conclusions; no byte-identical image claim is made.

## Tests and decisive outputs

All original focused checks passed: seven pilot checks, seven original feasibility checks, and seven earlier audit boundary/failure checks. The prior box blind-spot test intentionally verifies the known limitation of the box-only classifier; the combined pilot classifier and independent box-free checks address the actual systems.

Audit checks passed:

- Identical 12,248-region family under a separately implemented enumeration and independent adjacency; brute-force small-graph comparison in 3,297 cases.
- Independent lift with no conflicts; every exterior vertex and aggregate contribution checked, including fallback suppliers.
- Box-free unaggregated LPs for representatives of each independently identical aggregate system; all margins negative. Original aggregate systems also checked with widened boxes and perturbations.
- Exhaustive 20-row deletion problem through cardinality four: 1 + 20 + 190 + 1,140 + 4,845 systems; zero unresolved, minimum four, five feasible four-row sets.
- Actual 41-tile union verified separately from selected-row deletion; 12 vertices removed, 10 footprint components, zero-margin feasible exterior, boundaries changed.
- Fifteen independent uncapped hex searches; 1,920 decorated candidates match exactly; stronger validator leaves only identities; 13,440 final-star comparisons agree.
- Empty, incomplete, duplicate, shifted, malformed, and crossing-overlap controls; identity control. No nonidentity legal positive example claimed.
- Injected failure of each principal feasibility solver yields unresolved; corrected no-change shortcut preserves unresolved. True-frontier owner mutation rejected.
- One recorded continuation replayed: world 7/B/stream 20262655433, feasibility transition 8→9, jam detection 23; saved retained tile set and dead sites confirmed.
- Frozen reader baseline: reconstructed, area 0, selection null, `empty_incompatible`, B tile absent.

No continuation after repair, extra worlds, larger-region search, boundary-moving repair, matching-rule relaxation, manuscript work, merge, or force push was performed.

## Artifacts and residual limitations

- `verify.py`, `supplement.py`: independent enumeration, constraints, deletion and supporting checks.
- `verify_hex.py`: independent coverage enumeration and complete-patch checks.
- `audit_tools.py`: isolated hardened helpers; historical modules untouched.
- `test_regressions.py`: focused regression checks and corrected baseline artifact.
- `compare_reproduction.py`: immutable Git-blob comparison and preserved rerun outputs.
- `results/`: machine-readable verification, exact differences, corrected baseline.
- `reproduced/`: uncorrected original implementation outputs, clearly separated.

The independent checks share the frozen legality atlas, template-placement primitive, numerical LP implementation and original current-state data; independence is stated at the algorithmic level, not as a completely separate geometric engine or solver. The exact field/symbolic certification work remains undone. Zero-margin greedy feasibility especially requires caution. Repeatability across every Python/NumPy/libm version has not been established. No audit claim rests on byte-identical floating-point arithmetic.

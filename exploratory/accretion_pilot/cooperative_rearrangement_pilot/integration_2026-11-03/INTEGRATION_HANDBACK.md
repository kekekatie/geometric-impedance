# Integration handback — cooperative rearrangement pilot

*2026-11-03. A bounded maintenance task: integrate the independent Codex audit's
corrections (`audit/cooperative-rearrangement-2026-11-03`, commit `e7ff8ff`) into
the maintained pilot. Integration branch
`claude/cooperative-rearrangement-integration-2026-11-03`, based on the audit
commit. Historical results, frozen engine, frozen reader, and audit artifacts are
preserved; integration re-runs are under `integration_2026-11-03/` (separate from
historical `results/`). No merge, no force-push. This is not a new experiment.*

## 1. Which fixes are now used by the maintained pilot?

The audited, tested implementations are reused as the single source of truth via a
thin shim, `src/safeguards.py` → `audit_2026-11-03/audit_tools.py`:

- **Completed-replacement validator** (`safeguards.completed_replacement_legal`,
  used by `part4_search` and `tests/test_coop`): checks frozen-template membership,
  footprint coverage (total area), boundary/interface preservation, general
  polygon-intersection non-overlap, and all affected old/new vertex stars against
  the **full exterior**. **Empty or incomplete fillings now fail.** The historical
  weak validator in `coop_common.completed_replacement_legal` is marked deprecated
  (and minimally hardened to reject empties) and is no longer used for validation.
- **True-frontier scoring** (`safeguards.true_frontier_counts`, used by
  `part5_score`): counts candidates only on the **saved** true growth-frontier
  edges with owner checks, excluding the 30 pruning-exposed inner-boundary edges.
  Output is now **73 edges / 71 growable / 2 blocked** (histogram {0:2, 1:28, 2:43}),
  replacing the combined-skin 103 / 101.
- **Shortcut verdict propagation** (`part3_necessary`, mirroring
  `safeguards.classify_region`): a region whose exterior constraints are unchanged
  inherits the **established full-band verdict** — including `unresolved` — instead
  of assuming `infeasible`.
- **Minimum-row-deletion with unresolved tracking** (`part3_necessary.min_facet_drop`):
  checks every subset at each cardinality and will not claim a minimum past an
  `unresolved` smaller-cardinality check. Output renamed to `min_rows` with
  `min_certified` (here: 4, certified).
- **Corrected descriptions in code** (`part3_necessary`): the greedy footprint is
  reported as `heuristic_deletion_footprint` with explicit flags
  (`is_minimum_repair=False`, `is_necessary_reach=False`, `is_replacement=False`,
  `zero_margin_numerically=True`, `symbolically_certified=False`) and the audited
  facts (selected 11 / **actually removed 12** vertices, 41 triangles, 10
  components, spans 12.4757 / 14.0494, 8 outer + 4 inner boundary edges lost).
- **Documentation**: `permitted_region_guard` reports the dormant general
  permitted-region search as **unsupported** and stops clearly if ever reached;
  the Part-4 `truncation` block states the deduplicated-count limitation; the
  frozen `PROTOCOL.md` is unchanged, with the real caps/ordering/truncation
  reconciled in `protocol/PROTOCOL_DEVIATIONS.md` (dated 2026-11-03).

## 2. Which results were rechecked and remained unchanged?

Re-run with the corrected code into `integration_2026-11-03/results/`; **no
scientific conclusion changed**.

| Rechecked quantity | Historical | Integration (corrected) | Status |
|---|---|---|---|
| Seeded connected regions, size ≤ 8 | 12,248 | 12,248 | unchanged |
| Permitted (feasible-exterior) regions | 0 | 0 | unchanged |
| Final region verdicts | all infeasible | all infeasible | unchanged |
| 15 hexagons, legal completed replacements | identity only | identity only (strong validator) | unchanged |
| Any replacement restoring compatibility | 0 | 0 | unchanged |
| min aggregate-row deletion | 4 | 4 (certified, unresolved-tracked) | unchanged value |
| Heuristic deletion footprint | 41 tiles | 41 tiles, 12 removed, 10 comp, 12.48/14.05, 8+4 edges, zero-margin | **described correctly** |
| Reader baseline | empty_incompatible | empty_incompatible (reconstructed, area 0, B absent) | unchanged |
| True-frontier count | 103 / 101 (combined skin) | **73 / 71 / 2** (saved identities) | **corrected (reporting)** |

Tolerances / differences (not forced to byte agreement): the path-diagnostic
split is environment-sensitive (this run 9130 / 2724 / 394; the audit's Windows
run 9130 / 2793 / 325) — a last-bit artefact of exact-dict equality, now labelled
diagnostic; **all final verdicts agree**. No safeguard changed a scientific
conclusion, so no stop/expansion-halt condition was triggered.

Tests: `tests/test_coop.py` (9 checks, incl. empty-filling rejection) passes;
`audit_2026-11-03/test_regressions.py` (unresolved-shortcut guard, full-verdict
reuse, true-frontier 73/2/71, owner-mutation rejection) passes.

## 3. Which capabilities remain unsupported?

- **General permitted-region replacement search** is not implemented — only the
  flip-hexagon shape is. It is dormant (0 permitted regions); a future permitted
  region outside the implemented shapes now raises a clear **UNSUPPORTED** stop,
  never a spurious exhaustive negative. Building it was out of scope.
- **Symbolic / exact-field certification** is not done. The decisive LPs
  (including the zero-margin deletion example) remain floating-point; "infeasible"
  is robust numerical evidence, not an exact certificate.
- **No elementary-move path**: only completed joint legality was tested; no
  sequence of elementary legal moves was constructed or claimed.
- Out of scope and not attempted: unseeded regions, regions larger than 8
  triangles, boundary-moving repairs, other worlds, construction resumption,
  post-repair readout recovery.

## 4. Where should future work begin reading?

1. This file, then the audit's `audit_2026-11-03/HANDBACK.md` and
   `AUDIT_REPORT.md` (findings ranked by impact) and `REPRODUCTION.md` (exact
   commands, environment, comparison limits).
2. The corrected central-result wording in the top-of-file notes of `README.md`
   and `HANDBACK.md`, and the reconciliation in `protocol/PROTOCOL_DEVIATIONS.md`.
3. `integration_2026-11-03/results/` (corrected machine-readable outputs) beside
   the preserved historical `results/`.
4. The smallest sensible next step (from the audit): if the zero-margin 41-tile
   deletion example matters, **certify that existing example** before treating it
   as a feasibility bound — no expanded repair search is justified by this audit
   alone.

## Status

Maintained code uses the audited safeguards; historical outputs, frozen engine,
frozen reader, and audit artifacts preserved; integration outputs separate.
Integration branch and commit are reported in the delivery message. Stop after
integration and validation, per the brief — no new worlds, larger searches,
boundary-moving experiments, relaxed rules, exact-arithmetic project, or
manuscript.

# Implementation conformance report — sealed radius-saturation suite

**Implementation commits:** `17d65f3` (low-level helpers) + `8444b5d` (executable workflows, strict
invariants, e2e/leakage tests). This report is committed as their child on `gpt/workbench`.
**Design seal:** `4ec0536` (reviewed parent `e3d7af3`). **Scope:** implementation + non-scientific
conformance testing only. **The confirmatory study run was NOT performed and is NOT wired.**

## Seal verification (Step 1)
`4ec0536` confirmed present on `origin/gpt/workbench`; all five normative artifacts verified
hash-identical (git-blob SHA-1 and SHA-256) to `SEAL_RECORD.md`, before and after this work. **No
sealed artifact was edited.**

## Verdict: **CONFORMANT (implementation & synthetic conformance)**
All sealed procedures are now implemented as **executable, synthetic-tested workflows** on supplied
data objects — not merely low-level helpers (the gap Work-GPT/Sol's audit correctly flagged). Every
frozen invariant is enforced and tested. **Standing boundary:** final conformance *on study data*
requires the confirmatory run, which is unauthorized and deliberately not wired; that is the only
reason this is not an unqualified end-of-line verdict.

## Workflow → implementation map (Sol audit items 1–8)
| Audit item | Module · function | Synthetic test |
|---|---|---|
| 1. Leakage-safe residual-orthogonal (6 outer LOO; 4 inner PCA-slab folds pooled over 5 training offsets; cross-fitted train residuals; outer residualiser applied once to unseen offset; per-radius) | `workflows.residual_increment`, `_crossfit_train_residuals`, `_outer_residualiser_apply` | leakage test + determinism |
| 2. Generic six-offset orchestrator (fixed M₉=9 / M_perm,7=7; plain/residual/parity/capacity/permutation; G0–G8 inputs + routing; no outcome-dependent cell removal; **no study-data entry point**) | `workflows.orchestrate` | 3 predetermined routes |
| 3. Parity workflow ((deg, padded-Voronoi) field; scaler on pooled 5 training offsets applied unchanged to held-out; zero-variance/unavailable rule; exact 11-col `_m4_cols`) | `workflows.parity_block`, `parity_increment` | scaler-invariance + zero-variance |
| 4. Capacity workflow (exactly 200 keyed Gaussian blocks, parity-block dim; full 6×9 held-out increments per draw; `δ_cap` from the 200 M₉) | `workflows.capacity_delta_cap`, `capacity_increment_draw` | 200-draw + percentile + refuse≠200 |
| 5. Permutation workflow (training-only standardisation; train & held-out permutations separate; raw 2-component address permuted then `_m4_cols` recomputed; exact B=1000; synchronized rep indexing; q_ref on M_perm,7) | `workflows.permutation_stress`, `_perm_fold_blocks`, `_permuted_address_block` | shapes + q_ref + refuse≠1000 |
| 6. Production geometry (padded super-patch; explicit core correspondence; restrict Voronoi to core; Δ/ring; convergence; common-set/count floors) | `substrate.padded_core_voronoi_areas`, `restrict_voronoi_to_core`, `assert_pad_params`, `pad_convergence`, `assert_floors` | correspondence + Δ/ring + convergence + floors |
| 7. MSD workload (frozen 200 launches; strip mask + ΔP_strip; global earliest crossing over all launches/configs/offsets/both engines; batch 50; reduce-on-the-fly, no T×V×L; β on all 48 snapped points with frozen nonpositive-MSD failure route; per-(config,engine) median R²_fit) | `msd.select_launches`, `run_patch`, `global_t_bound_star`, `beta_with_failure_route`, `g1_median_r2_per_config_engine` | selection/crossing/β-failure/R²_fit |
| 8. Strict invariants (q_ref exactly 1000; WY (7,1000); time/grid correspondence; undefined-denominator & quality-failure routes) | `constants.q_ref_strict`, `assert_grid_correspondence`; `aggregation.westfall_young`; `gates.*` | invariant-raise tests |

## Adversarial leakage confirmation
`test_workflows.t_residual_leakage`: perturbing a **held-out** offset's `y` and address by large
amounts leaves the fold's **training** cross-fitted residuals **bit-identical** (`np.allclose`), while
the held-out residuals legitimately change. `t_parity_scaler_invariance`: perturbing held-out
`(degree, Voronoi area)` leaves the training-fitted parity scaler `(mean, std)` **unchanged**. Both
confirm training-fitted objects never see held-out data.

## End-to-end fixture with predetermined routes
A synthetic six-offset × nine-labelled-config dataset drives the orchestrator to **known routes**:
**survives-stress-controls** (address carries orthogonal signal; M₉>δ_cap, residual>δ_cap,
q_ref<0.05), **compression** (X_r(16) already captures the address so the r16 increment fades below
δ_cap while r2 is strong, ρ<ρ*), and **mixed/undetectable** (no signal). Exactly 7 of the 9 configs
are permutation-feasible (platinum e16/e18 infeasible), enforcing the M₉/M_perm,7 split.

## Tests and results (synthetic only)
`python -m gpt_workbench.impl.tests.test_all` → **56/56**; `... test_workflows` → **36/36**;
**total 92/92**. Highlights beyond the 56 low-level checks: leakage-safety (train residuals &
scalers invariant to held-out perturbation); three predetermined orchestrator routes; capacity uses
exactly 200 keyed draws and refuses otherwise; permutation runs at exactly B=1000 with obs_matrix
(7,6), null_Mperm7 (1000,), null_T7 (7,1000), and refuses B≠1000; Westfall–Young consumes exactly
(7,1000); MSD launch selection (200, 50/slab, deterministic), global crossing, β nonpositive-failure
route; production geometry core-correspondence, Δ/ring, convergence, floor assertions.

## Frozen-constant enforcement
As before, plus: `q_ref_strict` (exactly 1000 nulls), `westfall_young` shape `(7,1000)`,
`assert_grid_correspondence` at import (48 snapped times snap to grid), `capacity_delta_cap` requires
exactly 200 draws, `permutation_stress` requires exactly B=1000 and 7 feasible cells, `orchestrate`
requires exactly 9 configs and 7 feasible (no dropping). `impl/frozen_constants.json` mirrors the
registry (manifests authoritative).

## Prohibited-data-access confirmation
No study address values, targets, LDOS, β, outcome curves, scores, or family-result curves were
accessed or produced. No propagation on the nine sealed study configs; no exploratory family
comparisons; no tuning on observed study behaviour. Every fixture is hand-built with a known answer;
the orchestrator has **no study-data entry point** (it consumes supplied arrays only). Production
geometry generation (`substrate.generate_geometry`, `padded_core_voronoi_areas`) is geometry-only,
lazy, and **not invoked** by the test-suite.

## Intentional boundaries (not deviations)
- **No confirmatory launcher.** No function assembles a real dataset from generated geometry and runs
  the orchestrator on it — that is the prohibited scientific run. Every workflow is executable and
  synthetic-tested; wiring a study launcher is explicitly out of scope and unauthorized.
- The heavy real-data paths (200-draw capacity and B=1000 permutation with the frozen HGBR) are
  proven at their exact sealed counts using a fast deterministic surrogate `r2_fn` for orchestration,
  with the frozen HGBR separately confirmed to integrate; the surrogate is a test-only injection and
  the production default is the frozen regressor.

## Ambiguities / free implementation choices (documented, not silent protocol changes)
- Internal `physical_extra` column order (invariant under the frozen HGBR/R²) — unchanged from the
  prior report.
- Test orchestration injects `r2_fn`/`reg_factory` (default = frozen HGBR) purely to make
  known-answer synthetic tests deterministic and fast; production uses the frozen defaults.

## Unresolved blockers / remaining gaps
**None blocking.** The only remaining step is the confirmatory run itself, which is unauthorized.
When authorized, the production entry point is a thin adapter: generate geometry → build the feature
pipeline into the supplied-data schema → call `orchestrate` / the MSD workload. That adapter is
deliberately not written here.

*Not part of the scientific record until reviewed and merged. This authorizes no confirmatory run.*

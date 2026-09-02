# Traceability matrix — clean-room Stage 1

**Status: RECONCILED SPECIFICATION / AMENDMENT 2 RATIFIED / NOT IMPLEMENTED / NOT RUN**

Authority precedence: seal `4ec0536319b531e8ad04dbfbbd0cd0e19ac57f55`, ratified Amendment 1
at `d574fde530b9d033a898e03e532bfb30e9835caf`, ratified Amendment 2 at
`0d365bd26683feaa833739af15091cc1955d6935`, then these reconciled specifications.

Proposed modules are names only, not implementations. `test_*` entries are future test targets.

| Requirement IDs | Exact sealed source | Proposed future module | Proposed future tests |
|---|---|---|---|
| NR-GEO-001..004 | Physical v7 §1 | `constants.py`, `geometry.py` | `test_constants.py`, `test_radius_units.py` |
| NR-GEO-005..008 | Seal §3; Physical v7 §8; MSD v8.1 §13; Concordance preamble | `config_registry.py` | `test_registry_exact_order.py` |
| NR-GEO-009..012 | Physical v7 §1, §5, §8 | `geometry.py`, `folds.py`, `diagnostics.py` | `test_common_population.py`, `test_morphology_reporting.py` |
| NR-GEO-013..014 | Physical v7 §3a | `voronoi.py` | `test_padding_convergence.py` |
| NR-FEA-001..006 | Physical v7 §2; Conditional v4.1 §0–1; inspected `substrates/transport_run.py` functions `build_features`, `assemble` | `baseline_features.py`, `dedup.py` | `test_m3_contract.py`, `test_dedup.py` |
| NR-FEA-007..015 | Physical v7 §3–3a | `physical_features.py`, `voronoi.py` | `test_physical_columns.py`, `test_moments.py`, `test_nested_rungs.py` |
| NR-FEA-016..017 | Physical v7 §2; Conditional v4.1 §0, §3; inspected `_m4_cols`, `hull_depth` | `address_features.py` | `test_m4_exact_reference.py`, `test_m4_operator_wiring.py` |
| NR-FEA-018..020 | Physical v7 §4 | `parity.py` | `test_parity_scaler_leakage.py`, `test_parity_infeasible.py` |
| NR-CV-001..006 | Physical v7 §5 | `folds.py` | `test_outer_inner_fold_contract.py`, `test_tie_breaks.py` |
| NR-CV-007..011 | Physical v7 §1–2; Conditional v4.1 §1–2 | `regression.py`, `residual_null.py` | `test_paired_increment.py`, `test_residual_crossfit_leakage.py` |
| NR-CV-012..013 | MSD v8.1 §8; inspected `assemble` | `controls.py` | `test_shuffle_composition.py`, `test_position_far_controls.py` |
| NR-DYN-001..005 | MSD v8.1 §1–4, §10 | `propagation.py`, `launches.py` | `test_generators.py`, `test_batch_reference.py`, `test_launches.py` |
| NR-DYN-006..009 | MSD v8.1 §5; snapped-time file | `time_grid.py`, `boundary.py` | `test_exact_time_grid.py`, `test_boundary_gate_order.py` |
| NR-DYN-010..017 | MSD v8.1 §6–7, §9–11 | `endpoint.py`, `numerics.py`, `diagnostics.py` | `test_beta_reference.py`, `test_conservation.py`, `test_no_dynamic_cull.py` |
| NR-RNG-001..005 | Conditional v4.1 §3 | `local_permutation.py` | `test_assignment_law.py`, `test_raw_then_m4.py`, `test_escalation.py` |
| NR-RNG-006..008 | Seal §3; Conditional v4.1 §5 | `seed_registry.py`, `capacity.py` | `test_seed_identity.py`, `test_iteration_invariance.py` |
| NR-AGG-001..005 | Conditional v4.1 §4–6; Concordance preamble | `aggregation.py`, `multiplicity.py` | `test_m9_order.py`, `test_qref.py`, `test_westfall_young.py` |
| NR-GATE-000..009 | MSD v8.1 §12; Concordance table | `gates.py` | `test_g0_to_g8_truth_table.py`, `test_undefined_routes.py` |
| NR-ROUTE-001..005 | Physical v7 §7; Conditional v4.1 §7; MSD v8.1 §12; Concordance closing paragraph | `routing.py` | `test_route_truth_table.py`, `test_no_subset_recompute.py` |
| NR-CLAIM-001..003 | Seal §3; MSD v8.1 §12; Conditional v4.1 §7 | `reporting.py` | `test_claim_boundaries.py` |
| NR-FAIL-001..003 | All manifests’ explicit flag/stop/no-silent-use rules | every boundary validator | `test_malformed_inputs.py`, `test_fail_loudly.py` |

## Ratified Amendment 2 traceability

The retained amendment filename is historical. Exact source anchors below refer to ratified
`SYNTHETIC_CONFORMANCE_PROTOCOL_AMENDMENT_2_DRAFT.md` blob
`cba719b07f9d3365a39d708a7438ccb74024a4bd`. Module boundaries name production ownership or
conformance instrumentation; they do not claim implementation.

| Requirement | Exact Amendment-2 source | Exact module boundaries | Falsifying test identifiers |
|---|---|---|---|
| NR-SCP-001 | §3 Layer A; §6 TP-E2E-003 boundary | `geometry.py`, `features.py`, `regression.py`, `residual_null.py`, `controls.py`, `local_permutation.py`, `capacity.py`, `aggregation.py`, `multiplicity.py`, `propagation.py`, `endpoint.py`, `gates.py`, `routing.py`; independent `reference_*` fixtures | TP-SCP-A-001, TP-SCP-A-002, TP-SCP-CONC-001 |
| NR-SCP-002 | §3 Layer B | `production_workflow.py` raw-input boundary; `preflight.py`, `motif_registry.py`, `dedup.py`, `features.py`, `folds.py`, `launches.py`, `regression.py`, `residual_null.py`, `controls.py`, `local_permutation.py`, `capacity.py`, `aggregation.py`, `multiplicity.py`, `gates.py`, `routing.py` | TP-SCP-B-001, TP-SCP-B-002, TP-SCP-B-003 |
| NR-SCP-003 | §3 Layer C | `config_registry.py`, `seed_registry.py`, `local_permutation.py`, `capacity.py`, `provenance.py` identity-graph enumerator/validator | TP-SCP-C-001, TP-SCP-C-002, TP-SCP-CONC-001 |
| NR-SCP-004 | §3 Layer D | `gates.py`, `routing.py`, controlled routing-fixture boundary | TP-SCP-D-001, TP-SCP-CONC-001 |
| NR-SCP-005 | §3 Layer E | `production_workflow.py`, `boundary.py`; downstream beta/regression/control/null/capacity spies | TP-SCP-E-001 |
| NR-SCP-006 | §3 Layer F | `production_workflow.py`, `scheduler.py`, keyed result registry | TP-SCP-F-001, TP-SCP-CONC-001 |
| NR-SCP-007 | §3 Layer G | `conformance_report.py`, production invocation ledger, identity ledger | TP-SCP-G-001, TP-SCP-CONC-001 |
| NR-SCP-008 | §4 | production boundaries in `features.py`, `residual_null.py`, `controls.py`, `local_permutation.py`, `capacity.py`, `aggregation.py`, `multiplicity.py`; `production_workflow.py` | TP-SCP-MUT-001, TP-SCP-B-003 |
| NR-SCP-009 | §5 | `regression.py` fit-cache key/validator, `provenance.py`, `numerics.py` | TP-SCP-CACHE-001, TP-SCP-CACHE-002 |
| NR-SCP-010 | §6; §3 Layers A–G | `conformance_report.py`, `reporting.py`, evidence-kind validator | TP-SCP-CLAIM-001, TP-SCP-CONC-001 |

### Amendment 2 supersession and publication ledger

| Event or affected clause | Reconciliation status | Normative effect |
|---|---|---|
| TP-E2E-001 | Superseded only insofar as it required all 54 numerical patches, all 1000 null fixtures and all 200 capacity fixtures in one synthetic run; Layers A–G now govern evidence. | Every frozen axis, identity, production constant and eventual confirmatory computation remains unchanged. |
| Test Acceptance | Two real iteration orders and two real parallelism settings apply to layered evidence, not four complete confirmatory-scale workloads. | Genuine four-mode paths, keyed equality, no primary-gate waiver and no scientific-outcome description remain required. |
| TP-AMD-030 | Superseded only insofar as all composition evidence had to arise from one full-scale numerical run. | Every AC-01..AC-25 marker, exact axis/order/provenance and production constant remains mandatory. |
| `77e2552bba0383fbd3784e92b827fea4f66fa440` | Accidental empty administrative publication event, immediately superseded by `0d365bd26683feaa833739af15091cc1955d6935`. | None; it did not alter the ratified proposal text or any scientific requirement. |
| `0d365bd26683feaa833739af15091cc1955d6935` | Controlling ratification commit; blob `cba719b07f9d3365a39d708a7438ccb74024a4bd`. | Ratifies synthetic-conformance evidence changes only; authorizes neither implementation nor scientific execution. |

## Permitted dependency ledger

Only the following baseline functions were inspected, at the seal commit, because sealed requirements
explicitly named their behavior. No later commit and no `gpt_workbench/impl/` path was inspected.

| File at seal | Exact function inspected | Reason |
|---|---|---|
| `substrates/transport_run.py` | `hull_depth` | `d_bound` and `_m4_cols` hull-depth definition |
| `substrates/transport_run.py` | `build_features` | M3 field definitions, geometry/generator outputs and motif construction |
| `substrates/transport_run.py` | `_m4_cols` | exact sealed 11-column address/parity transform |
| `substrates/transport_run.py` | `assemble` | M3 ordering and explicitly inherited shuffle/position/far controls |
| `substrates/transport_run.py` | `held_out_r2` | referenced held-out regression contract; superseded where manifests specify nested folds |

The inspected baseline is a dependency definition only. Manifest text takes precedence on conflicts.

## Ratified Amendment 1 clause traceability

Every clause has a sealed anchor, one-to-one appended requirement, module boundary and falsifying
synthetic/conformance test. Existing IDs remain stable.

| Amendment | Sealed source anchor | Reconciled requirements | Proposed module boundary | Synthetic/conformance tests |
|---|---|---|---|---|
| AC-01 | Physical §5; Conditional §2,§4; MSD §8 | NR-AMD-001; NR-CV-001..011 | `folds.py`, `regression.py` | TP-AMD-001 retained-fold/non-nested rejection |
| AC-02 | Physical §1,§5,§8; MSD §1–2 | NR-AMD-002; NR-GEO-004..010 | `geometry.py`, `config_registry.py` | TP-AMD-002 lift/edge canonicalization and generator signature |
| AC-03 | Physical §2; Conditional §0,§3 | NR-AMD-003; NR-FEA-005 | `motif_registry.py` | TP-AMD-003 pooled registry/order/unseen failure |
| AC-04 | Physical §2; Conditional §1 | NR-AMD-004; NR-FEA-006 | `dedup.py` | TP-AMD-004 pooled fixed-schema multi-match |
| AC-05 | Physical §3 | NR-AMD-005; NR-FEA-007..014 | `physical_features.py` | TP-AMD-005 strict-prefix serialization |
| AC-06 | Physical §5; MSD §2 | NR-AMD-006; NR-CV-003..006 | `folds.py` | TP-AMD-006 covariance/sign/eigen-tie failure |
| AC-07 | MSD §8,§12 G4; baseline `assemble` | NR-AMD-007; NR-CV-012 | `shuffle_control.py`, `seed_registry.py` | TP-AMD-007 canonical JSON/hash; TP-AMD-008 replay/consumption |
| AC-08 | MSD §8 | NR-AMD-008; NR-CV-013 | `controls.py`, `reporting.py` | TP-AMD-009 mandatory descriptive/no-gate mutation |
| AC-09 | MSD §2 | NR-AMD-009; NR-DYN-003 | `launches.py` | TP-AMD-010 exact 50-index formula |
| AC-10 | MSD §6–7,§9,§12 | NR-AMD-010; NR-DYN-011..012 | `endpoint.py`, `routing.py` | TP-AMD-011 nonpositive/nonfinite invalidation, no epsilon/cull |
| AC-11 | MSD §7 | NR-AMD-011; NR-DYN-013 | `diagnostics.py` | TP-AMD-012 pooled-SD zero/infinity cases |
| AC-12 | Conditional §3–5 | NR-AMD-012; NR-RNG-003..006 | `local_permutation.py`, `seed_registry.py` | TP-AMD-013 canonical JSON/hash; TP-AMD-014 row-major replay |
| AC-13 | Physical §6; Conditional §6 | NR-AMD-013; NR-AGG-003 | `capacity.py` | TP-AMD-015 NumPy linear quantile golden fixture |
| AC-14 | Conditional §4; MSD §12 G8 | NR-AMD-014; NR-AGG-005 | `multiplicity.py` | TP-AMD-016 stable ties and cumulative-max step-down |
| AC-15 | Physical §6; Conditional §5–6 | NR-AMD-015; NR-RNG-007 | `capacity.py`, `seed_registry.py` | TP-AMD-017 spawn tree; TP-AMD-018 axes; TP-AMD-019 fields/reuse |
| AC-16 | Conditional §3 | NR-AMD-016; NR-RNG-002 | `local_permutation.py` | TP-AMD-020 training-only population-SD scaler |
| AC-17 | Conditional §3 | NR-AMD-017; NR-RNG-003..005 | `local_permutation.py` | TP-AMD-021 escalation self-exclusion/order/tie failure |
| AC-18 | Conditional §2; Physical §1 | NR-AMD-018; NR-CV-007,009..011 | `residual_null.py` | TP-AMD-022 eleven scalar topology and once-only provenance |
| AC-19 | Physical §2,§5; Conditional §1–2 | NR-AMD-019; NR-CV-008 | `regression.py` | TP-AMD-023 direct R2 undefined/finite reference |
| AC-20 | All sealed threshold clauses | NR-AMD-020; NR-GATE-000..009 | `thresholds.py`, `gates.py` | TP-AMD-024 literal inequalities/margins/nonfinite routes |
| AC-21 | MSD §7,§12; Concordance G1 | NR-AMD-021; NR-GATE-002 | `gates.py` | TP-AMD-025 all-nine coherent/classical reductions |
| AC-22 | Physical §7; Conditional §7; MSD §12 | NR-AMD-022; NR-ROUTE-001..005 | `routing.py` | TP-AMD-026 suite route and no cell dropping |
| AC-23 | Physical §3a,§5,§8; Conditional §9; `PREFLIGHT_GEOMETRY_REPORT_V2.md` §1–§6 blob `1c2995cc16bb5b8c0b8777550a461d4593966b48`; `SIX_OFFSET_AUDIT_REPORT.md` per-patch/Appendix blob `2470997bf70c16c1ee6af6f13784b4212d56a291` | NR-AMD-023; NR-GEO-011..014; `GeometryReferenceRegistry` | `preflight.py` | TP-AMD-027 typed hard/exact/rounded roles, mismatch stop and fixed membership |
| AC-24 | Physical §1,§3 Group B | NR-AMD-024; NR-FEA-010..011 | `physical_features.py` | TP-AMD-028 sigma-floor three-zero result |
| AC-25 | Physical §3 Group E,§3a | NR-AMD-025; NR-GEO-013..014 | `voronoi.py`, `preflight.py` | TP-AMD-029 exact join/ring/convergence/loud failures |

## Authorized geometry-provenance source ledger

| Seal-commit source | Git blob | Permitted use | Comparison roles |
|---|---|---|---|
| `gpt_workbench/PREFLIGHT_GEOMETRY_REPORT_V2.md` | `1c2995cc16bb5b8c0b8777550a461d4593966b48` | Materialize AC-23 outcome-free geometry provenance only | hard thresholds remain sealed; rounded size/morphology and aggregate padding figures are provenance-only expectations |
| `gpt_workbench/SIX_OFFSET_AUDIT_REPORT.md` | `2470997bf70c16c1ee6af6f13784b4212d56a291` | Materialize exact 54-patch r16/singleton registry and frozen local-null membership | exact discrete identity check; singleton >5% disables only local null; M9 unchanged |

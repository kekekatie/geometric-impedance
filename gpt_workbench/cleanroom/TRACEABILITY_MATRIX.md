# Traceability matrix — clean-room Stage 1

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

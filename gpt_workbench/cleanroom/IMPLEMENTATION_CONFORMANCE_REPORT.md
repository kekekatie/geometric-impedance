# Stage 2B implementation conformance report

**Status:** STAGE 2B.1 SYNTHETIC WORKFLOW CONFORMANCE PASS / PENDING INDEPENDENT RATIFICATION / STUDY NOT RUN  
**Original implementation commit:** `58c018820e40d09bd957dd63a33157dff4e06607`  
**Original conformance commit:** `e755de99e48b2f5418afcc0629e9b57437ab2fd3`  
**Stage 2B.1 workflow-wiring repair:** `83ed8e199454a2eb2c4614bd2706b3d3274f22b4`  
**Repair parent:** `e755de99e48b2f5418afcc0629e9b57437ab2fd3`  
**Authority:** seal `4ec0536319b531e8ad04dbfbbd0cd0e19ac57f55`; ratified Amendment 1
at `d574fde530b9d033a898e03e532bfb30e9835caf`; reconciled specifications at the
implementation parent.

## Verdict

Work-GPT/Sol's independent audit did not ratify the original Stage 2B conformance claim because
`synthetic_workflow.py` fabricated floor counts and already-aggregated arrays instead of traversing
the production workflow. It also identified a non-executable G0 barrier, superficial traversal-mode
claims, label validation based only on lengths, ranged rather than exact test traceability, missing
adversarial wiring tests, and a non-installable `python==...` requirements entry.

Repair `83ed8e199454a2eb2c4614bd2706b3d3274f22b4` resolves those findings. The new
`orchestrator.run_protocol` executes phased geometry/features/PCA/launch/dual-engine propagation,
then a hard global G0 barrier, then beta/regression/mandatory controls/randomisation/aggregation/
G0–G8/routing. All 73 collected tests pass. Forward/reverse traversals and one/two-worker scheduling
are materially different executions with identical keyed outputs. The exact 92-obligation ledger is
machine validated. There is no expected-failure waiver. This revised verdict is submitted for new
independent ratification; it does not retroactively describe the original audit as a pass.

This verdict is not a scientific result. No study-data entry point exists. No nine-configuration
study geometry, study address, target, LDOS, beta, score, outcome curve, confirmatory propagation,
ablation or exploratory run was loaded or executed.

## Reproducible environment

Installable packages are recorded in `gpt_workbench/cleanroom_impl/requirements-lock.txt`; the
interpreter is recorded separately in `interpreter-version.txt`:

| Dependency | Version |
|---|---:|
| Python | 3.12.13 |
| NumPy | 2.3.5 |
| SciPy | 1.18.1 |
| scikit-learn | 1.9.0 |
| pytest | 9.1.1 |

Requirements lock SHA-256: `a7504136bbd3d0b93f2c1efc44bb3ba9279158a988d1839a025529f55b3ae5d8`.
Interpreter record SHA-256: `11d6e3677cf7336044ee34c4bb599fa03b3988dfa31210d42f3ca7a2f7a6d3f3`.

## Exact commands and results

With repository root as the working directory and `PYTHONPATH` set to that root:

```powershell
C:\Users\Karen\Documents\Codex\2026-09-01\o\work\stage2b-venv\Scripts\python.exe `
  -m pytest gpt_workbench\cleanroom_impl\tests -q
```

Result: `73 passed in 29.35s` on the recorded final implementation-verification run. The module-scoped
full-axis fixture runs `(forward,1)`, `(forward,2)`, `(reverse,1)` and `(reverse,2)`. `TP-RNG-001` additionally launches
two clean child Python processes and requires byte-identical PCG64 replay.

Independent dynamics-reference command used the irregular synthetic adjacency
`[[0,1,1,0],[1,0,1,1],[1,1,0,0],[0,1,0,0]]`, a localised launch at vertex zero and times
`0, 0.25, 1.5`. Production Krylov calls were compared with independent dense `scipy.linalg.expm`
calculations:

| Engine | Maximum state/probability error | Required |
|---|---:|---:|
| coherent, `exp(-i t H)` | `3.3306690738754696e-16` | `<=1e-10` |
| classical, `exp(t Q)` | `4.4408920985006262e-16` | exact-reference agreement |

## RNG golden vectors

`golden_vectors.json` SHA-256 is
`6aca2bb44967e104a982cb644127249afed469d086f514b491c7441f122269d5`.
The production derivation is checked against a second direct implementation that constructs ordered
JSON, invokes `hashlib.blake2b` itself, splits digest bytes itself and instantiates NumPy
`SeedSequence`/`PCG64` directly.

| Vector | Frozen result |
|---|---|
| shuffle personalisation | ASCII `GIV-SHUFFLE-v1` |
| shuffle digest / u0 / u1 | `ed9ec0e3c61e6fec` / `3986604259` / `3323883500` |
| address personalisation | ASCII `GIV-ADDRPERM-v1` |
| address digest / u0 / u1 | `9d70af0b3b41cf37` / `2641407755` / `994168631` |
| address repetitions | exact float64 vectors frozen for `b=0,1,999` |
| capacity spawn tree | exactly 200 root children and one 54-child call per draw |
| capacity representative fields | SHA-256 frozen at `(draw,patch)=(0,0),(0,53),(199,0),(199,53)` |

Representative capacity hashes are respectively
`9566b3f8f33fa404b42fc71442c287713b43dde44f48b12183ca6ed89592e8c8`,
`db62a132829114c52d9563f753658dc0a4d8c5c5ca0886d0c4fcefbb288fae70`,
`e24aa18fed22f8e2a13e897f668814446b022973cbcb111f47719e7e3f2d1021`, and
`1726401457db652ac4d704b85a65e936a2d3d5f772f5bcde3db5ffe32697dad0`.

## Synthetic full-workflow results

The production orchestrator receives only an injected, invented backend and contains no study-data
loader. Each successful mode executes 54 geometry calls, 54 feature calls, 54 coherent and 54
classical propagation calls, 108 beta fits, 108 leakage-safe regression/control calls, 42,000 keyed
local-null calls and 10,800 capacity calls. Every patch has 400 common rows, four 100-row PCA slabs
and 200 actual launch identities. Exact-label validators cover the frozen general, permutation, G8,
capacity-draw and family-major capacity-child axes.

| Traversal | Workers used | First/last keyed patch | Keyed result SHA-256 |
|---|---:|---|---|
| forward | 1 | `(0,0)` / `(8,5)` | `45a5fd38e3ed3c9f321fd3043c4363affefd4e3c6cae3aa07b6da2eb64f02648` |
| forward | 2 | `(0,0)` / `(8,5)` | `45a5fd38e3ed3c9f321fd3043c4363affefd4e3c6cae3aa07b6da2eb64f02648` |
| reverse | 1 | `(8,5)` / `(0,0)` | `45a5fd38e3ed3c9f321fd3043c4363affefd4e3c6cae3aa07b6da2eb64f02648` |
| reverse | 2 | `(8,5)` / `(0,0)` | `45a5fd38e3ed3c9f321fd3043c4363affefd4e3c6cae3aa07b6da2eb64f02648` |

The exact-at-8 G0 adversary executes all 54 geometry/feature and 108 propagation calls, observes
`t_bound=8.0`, then records beta `0`, regression/control `0`, local-null `0` and capacity `0` calls.
Only G0 and the `finite-size-limited` route are emitted. These invented results test workflow and
routing semantics only; they are not estimates, findings or scientific outcomes.

## Normative traceability

The machine-readable exact 92-obligation ledger is `cleanroom_impl/test_inventory.json` (SHA-256
`0cd3784be8c6bc2c94cd871f66a00b960be9e2c40754cc0cec8055b505254f8f`). Each original TP identifier
and TP-AMD-001…030 has an exact pytest file/function node, asserted behavior and pass result; a test
checks all 92 IDs, their order, uniqueness, nonempty behavior and node existence. The following table
provides the required authority-to-result path. “Seal” abbreviates the exact parent source sections
already recorded in `TRACEABILITY_MATRIX.md`; Amendment clauses are ratified AC identifiers.

| Sealed source | Amendment | Requirements | Module/function | Principal test IDs | Result |
|---|---|---|---|---|---|
| Physical §5; Conditional §2,§4; MSD §8 | AC-01 | NR-CV-001..011, NR-AMD-001 | `folds.outer_training_offsets`, `residual_null.cross_fitted_residuals`, labelled aggregation | TP-LEAK-001..003, TP-WIRE-003..006, TP-AMD-001 | pass |
| Physical §1,§5,§8; MSD §1–2 | AC-02 | NR-GEO-004..010, NR-AMD-002 | `geometry.generate_adapter`, `canonicalize_geometry`, `identity.RowId` | TP-REG-001, TP-GEO-002, TP-NEG-003, TP-AMD-002 | pass |
| Physical §2; Conditional §0,§3 | AC-03 | NR-FEA-002,005, NR-AMD-003 | `features.motif_registry`, `motif_one_hot` | TP-FEA-006, TP-LEAK-007, TP-AMD-003 | pass |
| Physical §2; Conditional §1 | AC-04 | NR-FEA-006, NR-AMD-004 | `features.build_dedup_schema`, `apply_dedup` | TP-FEA-007, TP-LEAK-008, TP-AMD-004 | pass |
| Physical §3 | AC-05 | NR-FEA-007..015, NR-AMD-005 | `features.physical_features` | TP-FEA-001..003, TP-WIRE-010, TP-AMD-005 | pass |
| Physical §5; MSD §2 | AC-06 | NR-CV-003..006, NR-AMD-006 | `folds.pca_slabs` | TP-LEAK-006, TP-NEG-005, TP-AMD-006 | pass |
| MSD §8,§12 G4; sealed `assemble` | AC-07 | NR-CV-012, NR-AMD-007 | `controls.stratified_shuffle`, `seed_registry.shuffle_rng` | TP-RNG-001..002, TP-WIRE-005, TP-AMD-007..008 | pass |
| MSD §8 | AC-08 | NR-CV-013, NR-AMD-008 | `controls.position_control`, `far_control`; `gates` excludes controls | TP-WIRE-010, TP-AMD-009 | pass |
| MSD §2 | AC-09 | NR-DYN-003, NR-AMD-009 | `folds.launch_positions`, `select_launches` | TP-REG-002, TP-NEG-001, TP-AMD-010 | pass |
| MSD §6–7,§9,§12 | AC-10 | NR-DYN-011..012, NR-AMD-010 | `endpoint.beta_fit` | TP-DYN-005, TP-NEG-002,007, TP-AMD-011 | pass |
| MSD §7 | AC-11 | NR-DYN-013, NR-AMD-011 | `endpoint.admission_smd` | TP-FEA-002, TP-NEG-002, TP-AMD-012 | pass |
| Conditional §3–5 | AC-12 | NR-RNG-003..006, NR-AMD-012 | `seed_registry.address_key/address_rng`, `controls.local_assignment` | TP-RNG-001..005, TP-AMD-013..014 | pass |
| Physical §6; Conditional §6 | AC-13 | NR-AGG-003, NR-AMD-013 | `aggregation.capacity_floor` | TP-AGG-002, TP-GATE-001, TP-AMD-015 | pass |
| Conditional §4; MSD §12 G8 | AC-14 | NR-AGG-005, NR-AMD-014 | `aggregation.westfall_young` | TP-AGG-003, TP-REG-001, TP-AMD-016 | pass |
| Physical §6; Conditional §5–6 | AC-15 | NR-RNG-007, NR-AMD-015 | `seed_registry.CapacityRegistry` | TP-RNG-001..002,005, TP-AGG-002, TP-AMD-017..019 | pass |
| Conditional §3 | AC-16 | NR-RNG-002, NR-AMD-016 | `regression.PopulationScaler` | TP-LEAK-005, TP-RNG-003, TP-AMD-020 | pass |
| Conditional §3 | AC-17 | NR-RNG-003..005, NR-AMD-017 | `controls.local_assignment` | TP-RNG-003..004, TP-NEG-006, TP-AMD-021 | pass |
| Conditional §2; Physical §1 | AC-18 | NR-CV-007,009..011, NR-AMD-018 | `residual_null.cross_fitted_residuals` | TP-LEAK-002..003, TP-WIRE-003, TP-AMD-022 | pass |
| Physical §2,§5; Conditional §1–2 | AC-19 | NR-CV-008, NR-FAIL-002, NR-AMD-019 | `regression.direct_r2`, `paired_increment` | TP-WIRE-004, TP-NEG-002, TP-AMD-023 | pass |
| All sealed threshold clauses | AC-20 | NR-GEO/DYN/GATE thresholds, NR-AMD-020 | `gates.threshold_gate`, geometry/endpoint validators | TP-GATE-001, TP-AMD-024 | pass |
| MSD §7,§12; Concordance G1 | AC-21 | NR-DYN-014, NR-GATE-002, NR-AMD-021 | `gates.evaluate_gates` | TP-WIRE-011, TP-ROUTE-002, TP-AMD-025 | pass |
| Physical §7; Conditional §7; MSD §12 | AC-22 | NR-ROUTE-001..005, NR-AMD-022 | `routing.route` | TP-ROUTE-001..002, TP-AMD-026 | pass |
| Physical §3a,§5,§8; Conditional §9 | AC-23 | NR-GEO-011..014, NR-AMD-023 | `preflight.GeometryReferenceSource`, `validate_exact_patch_registry` | TP-AMD-027, TP-E2E-001 | pass |
| Physical §1,§3 Group B | AC-24 | NR-FEA-010..011, NR-AMD-024 | `features.population_moments` | TP-FEA-002, TP-AMD-028 | pass |
| Physical §3 Group E,§3a | AC-25 | NR-GEO-013..014, NR-AMD-025 | `voronoi.bounded_core_cells`, `geometry.validate_padding` | TP-VOR-001, TP-AMD-029 | pass |
| MSD §1–7,§10 | — | NR-DYN-001..017 | `propagation` distinct types/interfaces and streaming reducer; `endpoint` | TP-DYN-001..006, TP-WIRE-008..009, TP-NEG-007 | pass |
| Conditional §4–6; Concordance | — | NR-AGG-001..005 | `aggregation.LabelledArray`, `m9`, `mperm7`, `capacity_m9`, `q_ref` | TP-AGG-001..003, TP-WIRE-006 | pass |
| MSD §12; Concordance | — | NR-GATE-000..009 | `gates.evaluate_gates` | TP-GATE-001, TP-WIRE-005,008,011,012 | pass |
| Seal/manifest claim boundaries | — | NR-CLAIM-001..003, NR-FAIL-001..003 | `routing.validate_claim`, all boundary validators | TP-ROUTE-002, TP-NEG-001..007 | pass |

TP-AMD-030 is satisfied by `test_tp_e2e_001_amd_030_full_axes`, parameterised over two iteration
orders and two parallelism settings. TP-E2E-003's tiny exact references are used only for component
agreement; only the floor-preserving full-axis fixture is called a workflow conformance pass.

## Geometry provenance and rounding note

`preflight.py` embeds the typed source identities
`PREFLIGHT_GEOMETRY_REPORT_V2.md` blob `1c2995cc16bb5b8c0b8777550a461d4593966b48`
and `SIX_OFFSET_AUDIT_REPORT.md` blob `2470997bf70c16c1ee6af6f13784b4212d56a291`.
Exact r16/singleton integers control the local-null availability check. The three provenance-only
singleton display-rounding differences remain non-normative; displayed four-decimal fractions are
never decision inputs. Rounded morphology and aggregate padding expectations are returned only as
side-by-side provenance and cannot gate or re-tier a configuration.

## Free implementation choices

No free scientific choice was made. Non-scientific engineering choices were: immutable dataclasses
for typed boundary objects; JSON files for frozen registries; SHA-256 for audit payloads; an in-memory
capacity-field cache enforcing reuse; and explicit exceptions derived from `ConformanceError`.
`stream_reduce` exposes batch size for equivalence testing, while the sealed production default is
50. Synthetic fixture values are invented and chosen only to traverse routing truth-table branches.

## Unimplemented requirements and blockers

None within the authorised Stage 2B synthetic-conformance boundary. Real geometry preflight,
study-data execution, confirmatory propagation, ablation and scientific exploration remain
deliberately absent and require separate authorisation. That absence is a governance boundary, not a
conformance waiver or blocker.

## Normative byte-identity proof

`normative_hashes.json` freezes the Git blob identities and `test_tp_reg_004_normative_bytes_exact`
re-resolves every path from the committed tree. All passed:

| Artifact group | Git blobs unchanged |
|---|---|
| six sealed normative sources | `3d840769…`, `e3c32a2d…`, `95814aac…`, `d88b91e5…`, `a6cff0dd…`, `57be2925…` |
| ratified amendment | `a480bf7a…` |
| five reconciled documents | `381850da…`, `59efcd4c…`, `d31256c5…`, `2a6e878f…`, `572dae21…` |

The implementation commit adds only `gpt_workbench/cleanroom_impl/`. This report is the sole intended
addition in its separate report commit. No seal, amendment or reconciled specification was edited.

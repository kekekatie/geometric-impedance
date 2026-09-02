# Ambiguities and blockers — clean-room Stage 1

**Status: RECONCILED SPECIFICATION / AMENDMENT 2 RATIFIED / NOT IMPLEMENTED / NOT RUN**

Authority precedence: seal `4ec0536319b531e8ad04dbfbbd0cd0e19ac57f55`, ratified Amendment 1
at `d574fde530b9d033a898e03e532bfb30e9835caf`, ratified Amendment 2 at
`0d365bd26683feaa833739af15091cc1955d6935`, then these reconciled specifications.

The table immediately below is preserved historical Stage-1 text. Its former severity and proposed
resolution language is not operative after ratification; the reconciled resolution ledger following
it supplies the controlling clause, requirement and status for each item.

| ID | Severity | Unresolved point | Why consequential / required resolution |
|---|---|---|---|
| BLK-001 | BLOCKER | The manifests say the pipeline is “identical `transport_run.py` nested M0→M4” but the sealed baseline’s `held_out_r2` averages six fold scores and has no nested CV, while the manifests require six retained folds and four inner slabs. | Specify which baseline behaviors are inherited and which are superseded; aggregation cannot safely copy the old runner. |
| BLK-002 | BLOCKER | The production substrate/generator mapping for family names silver/golden/platinum, extents and offsets is not fully defined in the six artifacts. | A clean-room implementation cannot uniquely construct the 54 patches without an authorised generator API contract. Provide exact functions, parameters, coordinate/lift conventions and stable vertex/edge ordering. |
| BLK-003 | BLOCKER | “Shared motif codebook across offsets” does not state ordering, whether sharing is per config/family or global across all 54 patches, or whether held-out offset motif discovery may enter the codebook. The inspected baseline uses encounter order over all six offsets. | Column identity and leakage differ. Freeze scope, ordering, unknown-category behavior and training/test policy. |
| BLK-004 | clarification | Dedup does not say whether comparison is per patch, pooled config, outer-training set, all offsets, or global; nor which physical column is dropped when it duplicates multiple M3 columns. | Different folds could have different feature schemas or leak held-out geometry. Freeze scope and deterministic multi-match rule. |
| BLK-005 | BLOCKER | Physical v7 defines group contents and dimensions but not an unequivocal overall column serialization: all A then all B/D/E, or blocks interleaved by s. | Models can change with column order only indirectly, but schema identity, dedup and traceability require an exact order. |
| BLK-006 | clarification | PC1 sign rule is incomplete when `PC1[0]==0`; “else PC1[1]>=0” does not state the transformation if both components are zero/tied, and eigensolver/tied-eigenvalue behavior is not fixed. | Slab membership and launches must be reproducible. Freeze PCA solver and complete tie rule. |
| BLK-007 | BLOCKER | The sealed stratified-shuffle control is invoked by MSD v8.1 but not self-contained in the manifests. Inspected `assemble` uses rank-based degree deciles, one mutable RNG, encounter-order groups and no declared stable per-patch/per-fold seed. | G4 is a primary gate. Freeze exact binning, raw-field permutation, singleton behavior, and stable per-draw/per-patch identity. |
| BLK-008 | BLOCKER | MSD §8 lists `M3pos/M4pos/M3far/M4far` controls, but no gate, required statistic, radius, reporting rule or failure route is assigned. | They cannot be correctly wired or interpreted from the seal. Clarify whether mandatory and exactly how results affect claims. |
| BLK-009 | BLOCKER | “Take evenly-spaced indices” for 50 launches per slab has no exact integer-index formula or collision/tie behavior. | Different standard formulas select different vertices and targets. Freeze the formula. |
| BLK-010 | BLOCKER | `log(MSD)` is undefined for zero/nonpositive MSD at any snapped time, yet every admitted launch must yield beta and no dynamics culling is allowed. | Freeze a loud-failure route or a mathematically specified treatment; no epsilon may be guessed. |
| BLK-011 | clarification | Standardised mean difference for admission diagnostic has no denominator convention (pooled SD, admitted SD, overall SD), ddof, or zero-variance handling. | Descriptive values will differ. Freeze formula. |
| BLK-012 | BLOCKER | Stable permutation RNG is allowed as `hash64(...)` “or equivalent”, but hash algorithm, byte encoding, component normalization, SeedSequence spawn-key word widths, edge ordering and consumption order are unspecified. | The task explicitly requires stable per-draw/per-patch/per-offset identities; independent implementations will not reproduce costs. Freeze a canonical derivation. |
| BLK-013 | BLOCKER | “95th percentile” of 200 values does not specify quantile estimator/interpolation. | `delta_cap` feeds G3, G4, G5, G6 and routing; values near the threshold can change outcomes. Freeze the estimator. |
| BLK-014 | clarification | Westfall–Young does not fully define observed-statistic tie ordering or the exact monotonisation operation. | Adjusted extremeness values should be reproducible. Freeze stable config tie order and cumulative-max direction. |
| BLK-015 | BLOCKER | Capacity Gaussian blocks are “same dimensionality as parity” but scale/distribution parameters, row independence, whether generated separately per fold/config/offset/engine, and training/test realization sharing are not specified. | `delta_cap` is a primary detection floor. Freeze standard normal parameters and full identity/reuse graph. |
| BLK-016 | BLOCKER | Matching-feature scaler says “training-only”, but it is unclear whether one scaler is pooled across five offsets per config, per motif, per patch, or per fold, and how the held-out patch’s candidate distances use it. | Candidate neighborhoods and permutation law change. Freeze fit scope and zero-variance behavior. |
| BLK-017 | BLOCKER | Minimum-cost “perfect assignment” is called a derangement, but the candidate graph excludes self while escalation to “full same-motif group” does not explicitly preserve self exclusion; cost-tie resolution is unspecified. | Fixed points beyond singletons and platform-dependent assignments can result. Freeze graph at each escalation and tie-breaking. |
| BLK-018 | BLOCKER | Residualiser GBT hyperparameters appear to inherit the common regressor, but this is not explicit; address scaling and multi-output versus 11 independent fits are partly described but not completely typed. | G6 is primary. Confirm one scalar GBT per address column using the frozen hyperparameters and exact residual feature scaling. |
| BLK-019 | BLOCKER | `R2` convention for pooled outer training/test scoring is not explicit for constant targets or nonfinite predictions; scikit-learn’s `force_finite` behavior is not frozen. | Increment and gate values can silently become finite constants. Freeze exact scoring and failure rules. |
| BLK-020 | clarification | The boundary strip uses `d_bound<2*ell` while admission uses `>=16*ell`; treatment of hull-depth numerical tolerance and points exactly on thresholds is not specified beyond mathematical inequalities. | Cross-platform near-boundary membership may differ. Freeze computation precision/tolerance or require exact float behavior plus audit. |
| BLK-021 | BLOCKER | G1 prose alternates between “a coherent config failure downgrades/fails global claim” and the final conjunction “coherent G1”; it does not name whether `coherent G1` means all nine cells pass. The natural reading is all nine, but guessing is prohibited. | Freeze the Boolean reduction across nine per-config G1 states, and likewise classical G1 for the modifier. |
| BLK-022 | BLOCKER | Physical routing speaks of “a cell” but compression/survival criteria use global `M9`; exact output granularity (one global route versus per-config routes) is inconsistent. | Freeze routing scope and labels for individual cells versus the global study. |
| BLK-023 | BLOCKER | The manifests give measured r16 feasibility results but governance forbids accessing study geometry/data in this stage. It is unclear whether Stage 2 must recompute and gate feasibility or treat the sealed membership as fixed facts. | Specify whether geometry-only preflight values are normative inputs, mandatory recomputations, or diagnostics. |
| BLK-024 | clarification | Moment sigma `<1e-9` rule says “three higher moments” after listing variance, skewness, kurtosis, which could mean set variance too; Group B needs exact behavior. | Freeze outputs explicitly; this spec currently interprets variance as computed and skew/kurtosis as zero. |
| BLK-025 | BLOCKER | The padded Voronoi construction names extent+Delta and a ring-width constraint but not how core vertices are matched to padded vertices or how unbounded/Qhull degeneracies fail. | Group E and parity area require a stable row mapping and loud-failure contract. |

## Ratified resolution ledger

Each item is marked resolved only after structural verification that `NORMATIVE_REQUIREMENTS.md`,
`DATA_FLOW_SPEC.md`, `TRACEABILITY_MATRIX.md` and `CLEANROOM_TEST_PLAN.md` carry its executable rule,
typed transformation, trace and falsifying test.

| Historical item | Ratified resolution clause | Reconciled requirement IDs | Status |
|---|---|---|---|
| BLK-001 | AC-01 | NR-AMD-001; NR-CV-001..011 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-002 | AC-02 | NR-AMD-002; NR-GEO-004..010 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-003 | AC-03 | NR-AMD-003; NR-FEA-005 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-004 | AC-04 | NR-AMD-004; NR-FEA-006 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-005 | AC-05 | NR-AMD-005; NR-FEA-007..014 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-006 | AC-06 | NR-AMD-006; NR-CV-003..006 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-007 | AC-07 | NR-AMD-007; NR-CV-012 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-008 | AC-08 | NR-AMD-008; NR-CV-013 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-009 | AC-09 | NR-AMD-009; NR-DYN-003 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-010 | AC-10 | NR-AMD-010; NR-DYN-011..012 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-011 | AC-11 | NR-AMD-011; NR-DYN-013 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-012 | AC-12 | NR-AMD-012; NR-RNG-003..006 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-013 | AC-13 | NR-AMD-013; NR-AGG-003 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-014 | AC-14 | NR-AMD-014; NR-AGG-005 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-015 | AC-15 | NR-AMD-015; NR-RNG-007 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-016 | AC-16 | NR-AMD-016; NR-RNG-002 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-017 | AC-17 | NR-AMD-017; NR-RNG-003..005 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-018 | AC-18 | NR-AMD-018; NR-CV-007,009..011 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-019 | AC-19 | NR-AMD-019; NR-CV-008 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-020 | AC-20 | NR-AMD-020; NR-GATE-000..009 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-021 | AC-21 | NR-AMD-021; NR-GATE-002 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-022 | AC-22 | NR-AMD-022; NR-ROUTE-001..005 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-023 | AC-23 | NR-AMD-023; NR-GEO-011..014 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-024 | AC-24 | NR-AMD-024; NR-FEA-010..011 | RESOLVED BY RATIFIED AMENDMENT 1 |
| BLK-025 | AC-25 | NR-AMD-025; NR-GEO-013..014 | RESOLVED BY RATIFIED AMENDMENT 1 |

## Ratified Amendment 2 reconciliation ledger

This separate ledger does not rewrite the historical blocker table or Amendment-1 resolution
ledger. Amendment 2 resolves an evidentiary feasibility problem, not a scientific ambiguity.

| Reconciliation item | Ratified resolution | Requirement IDs | Status |
|---|---|---|---|
| Exact component evidence and TP-E2E-003 distinction | Layer A and §6 | NR-SCP-001, NR-SCP-010 | RECONCILED; NOT IMPLEMENTED / NOT RUN |
| Six-offset production-wired compliant slice with exact floors, axes, controls and representative `b={0,1,999}`, capacity `{0,199}` | Layer B | NR-SCP-002 | RECONCILED; NOT IMPLEMENTED / NOT RUN |
| Complete 54/42,000/10,800 identity graph, seeds, synchronization and reuse without fit claims | Layer C | NR-SCP-003 | RECONCILED; NOT IMPLEMENTED / NOT RUN |
| Seven-case routing coverage | Layer D | NR-SCP-004 | RECONCILED; NOT IMPLEMENTED / NOT RUN |
| Exact-`t=8` hard G0 stop with zero downstream calls | Layer E | NR-SCP-005 | RECONCILED; NOT IMPLEMENTED / NOT RUN |
| Forward/reverse × one/two-worker layered determinism | Layer F | NR-SCP-006 | RECONCILED; NOT IMPLEMENTED / NOT RUN |
| Enumerated/executed/not-executed scale categories | Layer G | NR-SCP-007 | RECONCILED; NOT IMPLEMENTED / NOT RUN |
| Production-bypass mutations | §4 | NR-SCP-008 | RECONCILED; NOT IMPLEMENTED / NOT RUN |
| Byte-identical five-part fit-cache key and cached/uncached equivalence | §5 | NR-SCP-009 | RECONCILED; NOT IMPLEMENTED / NOT RUN |
| Prohibited conformance claims | §6 | NR-SCP-010 | RECONCILED; NOT IMPLEMENTED / NOT RUN |
| TP-E2E-001, Test Acceptance and TP-AMD-030 | §2 and §7 concordance | NR-SCP-001..010 | SUPERSEDED ONLY TO RATIFIED EVIDENTIARY EXTENT; SCIENTIFIC CONSTANTS UNCHANGED |
| Accidental empty commit `77e2552bba0383fbd3784e92b827fea4f66fa440` | Superseded by controlling ratification commit `0d365bd26683feaa833739af15091cc1955d6935` | none | ADMINISTRATIVE PUBLICATION EVENT; NO NORMATIVE EFFECT |

No new scientifically consequential ambiguity or blocker is introduced by this reconciliation.
Implementation conformance under NR-SCP-001..010 remains unimplemented and unrun, so no conformance
pass or scientific claim is recorded.

## Seal-internal observations that are not blockers

- Manifest end markers say “Nothing sealed” although headers and `SEAL_RECORD.md` say SEALED. This
  is stale change-log boilerplate; the seal record and status headers control.
- The checked-out files use Windows line-ending conversion. Identity verification was therefore
  performed against immutable Git blob bytes, not worktree bytes; all five normative hashes match.
- `SEAL_RECORD.md` is a seal/provenance record; its table identifies five normative protocol files.
  The user separately authorised it and the snapped-time companion as Stage 1 read inputs.

## Stage 2B implementation entry conditions

Implementation may begin only if all 25 historical blockers are resolved and traced; no contradiction
remains; all five reconciled documents agree on axes, populations, RNG identities, failure routes,
gates and NR-SCP-001..010 evidence boundaries; and no study data or outcomes have been accessed. This
reconciled ledger meets the documentary conditions only. Ratification/reconciliation authorizes
neither resumption of preserved Stage 2B.2 work nor scientific execution; either still requires
separate authorization from Work-GPT/Sol and Katie.

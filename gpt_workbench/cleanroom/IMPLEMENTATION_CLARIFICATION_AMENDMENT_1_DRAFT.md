# Implementation Clarification Amendment 1 — DRAFT

**Status: PROPOSED / NOT RATIFIED / NOT IMPLEMENTED / NOT RUN**

**Date:** 2026-09-01  
**Parent design seal:** `4ec0536319b531e8ad04dbfbbd0cd0e19ac57f55`  
**Parent clean-room specification:** `1a75925677c95d55be3773857b54dbadb8753bdd`  
**Authority/source:** Work-GPT/Sol design adjudication relayed by Katie  
**Purpose:** outcome-blind clarification proposal resolving, where the adjudication is complete,
the 25 items in `AMBIGUITIES_AND_BLOCKERS.md`. This draft has no normative force until explicitly
ratified under the seal’s post-seal amendment policy.

No study address values, targets, LDOS, beta values, scores, outcome curves, propagation results or
later prototype/audit branches were accessed. No scientific code was implemented and nothing was run.

## Prominent unresolved blockers in this proposal

Textual concordance found no direct contradiction between the adjudications below and explicit sealed
wording. However, three adjudications remain insufficient for independent bitwise reproduction:

1. **AC-07 / BLK-007:** the shuffle root and semantic key are fixed, but the canonical key encoding,
   hash/SeedSequence derivation and within-group RNG consumption order are not. “Stably keyed” is not
   itself an executable derivation.
2. **AC-12 / BLK-012:** the required BLAKE2b personalisation string is described as fixed but its
   literal byte value is absent. Canonical JSON also needs exact field names/order and numeric/string
   encodings. No value is invented here.
3. **AC-15 / BLK-015:** capacity semantics are fixed, but the exact deterministic derivation of each
   `(draw, configuration, offset)` patch substream is not stated. The draw child versus patch child
   `spawn_key` layout or equivalent canonical hash must be supplied.

These three blockers prevent a fully reproducible implementation even if this draft is otherwise
ratified. Ratification should either supply their missing literals/algorithms or expressly leave the
implementation blocked. They do not prevent completion of this proposal.

## Proposed clarification clauses

### AC-01 — Pipeline inheritance

**Resolves:** BLK-001.  
**Affected sealed sections:** Physical v7 §5; Conditional-null v4.1 §2, §4; MSD v8.1 §8.  
**Clean-room links:** NR-CV-001..011; TP-LEAK-001..003; TP-WIRE-003..004; TP-WIRE-006.

The manifests supersede the orchestration in the sealed-parent `transport_run.py`. Inherit only
primitives explicitly named by sealed documents. Retain all six outer leave-one-offset-out fold
values and use the four simultaneous PCA-slab inner folds. Do not inherit the old mean/std return
from `held_out_r2`, its non-nested evaluation, or any old runner-level averaging.

**Rationale:** prevents obsolete orchestration from overriding the later self-contained manifests.
**Concordance:** clarification of an obsolete named dependency; no contradiction.

### AC-02 — Generator calls and stable geometry identities

**Resolves:** BLK-002.  
**Affected sealed sections:** Physical v7 §1, §5, §8; MSD v8.1 §1–2.  
**Clean-room links:** NR-GEO-004..010; NR-CV-005; NR-DYN-003; TP-REG-001; TP-GEO-002; TP-NEG-003.

Map silver/golden/platinum to `N=8/10/12`. Use the nine sealed extents and six sealed offsets.
The permitted sealed-parent definitions have these exact interfaces:

```text
structure(N) -> dict(m, star, par4, perp4, K, Kb, G, chi, mod, A, b, classes)
generate(N, extent, offset=None, disorder=0.0, seed=0, extra_offset=None,
         disorder_extra=False)
  -> (lifts, par, perp, ustar)
build_edges(lifts, N, ustar=None) -> sorted list[(vertex_index, vertex_index)]
```

The clean call fixes `offset` to the sealed pair and otherwise uses the displayed generator defaults;
no disorder or extra offset is introduced. Vertex identity is the exact integer lift-coordinate tuple.
Sort vertices lexicographically by identity and remap all row-aligned arrays. Canonicalise each edge
as its sorted pair of endpoint identities, then sort edges lexicographically. Missing, duplicate or
reordered identities are loud failures.

**Rationale:** makes geometry joins and all downstream randomisation identities stable.
**Concordance:** transcribes the explicitly referenced sealed rank-4 primitive; no later code used.

### AC-03 — Motif codebook

**Resolves:** BLK-003.  
**Affected sealed sections:** Physical v7 §2; Conditional-null v4.1 §0, §3.  
**Clean-room links:** NR-FEA-002, NR-FEA-005; TP-FEA-006; TP-LEAK-007.

For each family×tier configuration, construct one geometry-only motif registry pooled across all six
offsets before outcome access. Canonical motif tuples and the registry are lexicographically sorted.
The resulting one-hot schema is shared unchanged by all six outer folds. A motif not in the completed
registry is a loud error; there is no unknown bucket.

**Rationale:** fixes column order without outcome leakage or fold-dependent schemas.
**Concordance:** resolves the sealed phrase “shared codebook across offsets”; no contradiction.

### AC-04 — Bit-identical deduplication

**Resolves:** BLK-004.  
**Affected sealed sections:** Physical v7 §2; Conditional-null v4.1 §1.  
**Clean-room links:** NR-FEA-006; TP-FEA-007; TP-LEAK-008.

Determine deduplication once per configuration and radius using pooled common-set rows from all six
offsets and only physical/M3 values. Drop a physical-extra column if it matches at least one M3 column
with `max(abs(delta)) < 1e-12`; always retain M3. Record the dropped physical column and every matching
M3 column. Apply the resulting schema unchanged to all outer folds.

**Rationale:** fixes scope and multi-match bookkeeping while remaining geometry-only.
**Concordance:** preserves the sealed strict inequality and M3 precedence.

### AC-05 — `physical_extra(r)` serialization

**Resolves:** BLK-005.  
**Affected sealed sections:** Physical v7 §3.  
**Clean-room links:** NR-FEA-007..015; TP-FEA-001..003; TP-WIRE-010.

Serialize by successive scale. At each newly admitted scale `s`, append in order: newly admitted
Group-A annuli, `B_s`, `D_s`, `E_s`. Within groups retain the sealed order: B mean/variance/skewness/
excess-kurtosis; D `psi_(N/2), psi_N, psi_(2N)`; E mean/variance. This must yield dimensions
11/22/35/48/61 and exact column-prefix nesting for r=2/4/8/12/16.

**Rationale:** turns dimensional nesting into an exact schema contract.
**Concordance:** chooses a serialization where the seal specified content and strict nesting but not
cross-group order; no contradiction.

### AC-06 — PCA/slab determinism

**Resolves:** BLK-006.  
**Affected sealed sections:** Physical v7 §5; MSD v8.1 §2.  
**Clean-room links:** NR-CV-003..006; TP-LEAK-006; TP-NEG-005.

Use float64 population covariance and a symmetric eigensolver. Orient PC1 by making the first component
whose absolute magnitude exceeds `1e-15` positive. If the leading eigenvalue is tied within
`1e-12*max(1,abs(lambda_max))`, or no component clears the orientation tolerance, slab construction is
infeasible and stops. Break projection ties by lexicographic lift identity; assign remainder rows to
lowest-index slabs as sealed.

**Rationale:** removes eigensolver sign/tie nondeterminism.
**Concordance:** completes the existing sign and tie rules without changing the four-slab design.

### AC-07 — Stratified-shuffle control

**Resolves in part:** BLK-007; deterministic key derivation remains blocked above.  
**Affected sealed sections:** MSD v8.1 §8, §12 G4; sealed-parent baseline `assemble`.  
**Clean-room links:** NR-CV-012; NR-GATE-005; TP-RNG-002; TP-WIRE-005, TP-WIRE-010.

Permute each raw two-component perpendicular-address row jointly, then recompute `_m4_cols`. Group by
the exact sealed-parent formula:

```text
rank = deg.argsort().argsort()
degree_decile = clip(rank * 10 // n, 0, 9)
group = motif_code * 10 + degree_decile
```

Use one patch-level shuffle shared across folds and engines. Singletons remain fixed. Use separate root
`SeedSequence(20260901)`, stably keyed by configuration and offset, with no mutable global RNG.

**Rationale:** preserves paired G4 input while separating it from address and capacity registries.
**Concordance:** the degree-decile and joint raw-field behavior are exactly recoverable and compatible;
the baseline’s mutable RNG is superseded. Exact stable-key derivation still requires ratification.

### AC-08 — Position/far controls

**Resolves:** BLK-008.  
**Affected sealed sections:** MSD v8.1 §8; inspected sealed-parent `assemble`.  
**Clean-room links:** NR-CV-013; TP-WIRE-010.

`M3pos/M4pos` and `M3far/M4far` are mandatory descriptive robustness diagnostics at r=16 for both
engines. They have no threshold, gate, routing or earned-claim role. Their feature definitions remain
the sealed-parent definitions already traced in Stage 1.

**Rationale:** specifies why the named controls run without adding an unsealed decision gate.
**Concordance:** upgrades baseline “exploratory” language to mandatory reporting but not inference;
compatible with MSD §8’s inclusion of these controls.

### AC-09 — Launch indices

**Resolves:** BLK-009.  
**Affected sealed sections:** MSD v8.1 §2.  
**Clean-room links:** NR-DYN-003; TP-REG-002; TP-NEG-001.

Within each deterministically sorted slab of size `n`, select indices
`floor(j*(n-1)/49)` for integer `j=0..49`. The sealed `n>=100` floor prevents duplicates. Any duplicate,
out-of-range index or launch count other than 50 per slab is a loud failure.

**Rationale:** fixes one exact interpretation of “evenly spaced”.
**Concordance:** no contradiction.

### AC-10 — Nonpositive MSD

**Resolves:** BLK-010.  
**Affected sealed sections:** MSD v8.1 §6–7, §9, §12.  
**Clean-room links:** NR-DYN-011..012, NR-FAIL-002; TP-DYN-005; TP-NEG-002, TP-NEG-007.

Do not add epsilon and do not cull launches. Any admitted launch with nonfinite or nonpositive MSD at
any of the 48 fit times invalidates that configuration-engine endpoint. An invalid coherent endpoint
makes coherent G1 unsatisfied and the global coherent primary result unavailable/downgraded; an invalid
classical endpoint makes the cross-engine modifier inconclusive. Never shorten the fit grid.

**Rationale:** makes the logarithm domain failure explicit while preserving the no-culling rule.
**Concordance:** supplies the loud route implied by “every admitted launch yields beta” and numerical
flagging; no epsilon or rescue contradicts the seal.

### AC-11 — Admission SMD

**Resolves:** BLK-011.  
**Affected sealed sections:** MSD v8.1 §7.  
**Clean-room links:** NR-DYN-013; TP-FEA-002; TP-NEG-002.

Use pooled population SD `sqrt((var_admitted+var_excluded)/2)`. If it is below `1e-12`, report zero
when means agree within `1e-12`; otherwise report signed infinity. The diagnostic remains descriptive
with no threshold or gate.

**Rationale:** fixes denominator and zero-variance behavior.
**Concordance:** no inferential role is added.

### AC-12 — Address-permutation RNG

**Resolves in part:** BLK-012; literal encoding/personalisation remains blocked above.  
**Affected sealed sections:** Conditional-null v4.1 §3–5.  
**Clean-room links:** NR-RNG-003..006; TP-RNG-001..005.

Canonical semantic fields are family, tier, extent, offset index, canonical motif tuple and repetition.
Encode the fields excluding repetition as canonical UTF-8 JSON. Hash with BLAKE2b `digest_size=8` and
a fixed protocol personalisation string; split the digest big-endian into uint32 `u0,u1`. Repetition
`b` uses `SeedSequence(20260829,spawn_key=(u0,u1,b))`. Sort source and destination rows by lift identity
and draw edge costs in row-major order. Synchronise repetition indices across engines and comparisons.

**Rationale:** removes traversal and scheduling dependence.
**Concordance:** compatible with the seal’s stable keyed derivation and synchronized repetitions.
The literal personalisation and canonical JSON schema must be added before ratification can close BLK-012.

### AC-13 — `delta_cap` quantile

**Resolves:** BLK-013.  
**Affected sealed sections:** Physical v7 §6; Conditional-null v4.1 §6; Concordance.  
**Clean-room links:** NR-AGG-003; TP-AGG-002; TP-GATE-001.

Compute the float64 0.95 quantile of the 200 complete aggregate M9 capacity draws using NumPy
`method="linear"`.

**Rationale:** fixes interpolation at the primary detection floor.
**Concordance:** preserves the sealed percentile and population.

### AC-14 — Westfall–Young ordering

**Resolves:** BLK-014.  
**Affected sealed sections:** Conditional-null v4.1 §4; MSD v8.1 §12 G8.  
**Clean-room links:** NR-AGG-005; TP-AGG-003; TP-REG-001.

Use fixed seven-cell order silver small/medium/large, golden small/medium/large, platinum large. Sort
observed statistics descending stably so this order breaks ties. Apply the sealed signed, one-sided,
raw-null step-down max-T calculation and enforce adjusted-value monotonicity with a cumulative maximum
along that descending order.

**Rationale:** removes tie and monotonisation ambiguity.
**Concordance:** no contradiction; set membership remains the sealed seven.

### AC-15 — Capacity fields

**Resolves in part:** BLK-015; exact patch-substream derivation remains blocked above.  
**Affected sealed sections:** Physical v7 §6; Conditional-null v4.1 §5–6.  
**Clean-room links:** NR-RNG-007; NR-AGG-003; TP-RNG-002, TP-RNG-005; TP-AGG-002.

Each capacity block has 11 independent standard-normal columns. One draw is a complete field over every
configuration×offset×vertex row. Derive patch substreams from capacity root `SeedSequence(20260830)`,
draw index, configuration and offset. Store and reuse that draw across outer folds and both engines;
never regenerate held-out fields under another identity. Apply no address-derived scaling.

**Rationale:** fixes distribution, dimensionality, reuse and scientific independence.
**Concordance:** compatible with 200 indexed children and full-M9 calibration. The exact hierarchical
spawn/hash layout is still required for bitwise identity.

### AC-16 — Matching scaler

**Resolves:** BLK-016.  
**Affected sealed sections:** Conditional-null v4.1 §3.  
**Clean-room links:** NR-RNG-002; TP-LEAK-005; TP-RNG-003.

For each configuration and outer fold, fit mean and population SD on pooled common-set rows from the
five training offsets. Apply unchanged to all training and held-out patches in that fold. If a training
feature SD is below `1e-12`, standardise that feature to zero in training and held-out representations,
so it contributes no matching distance.

**Rationale:** fixes fit scope and prevents held-out geometry leakage.
**Concordance:** instantiates the sealed training-only scaler.

### AC-17 — Matching candidates and ties

**Resolves:** BLK-017.  
**Affected sealed sections:** Conditional-null v4.1 §3.  
**Clean-room links:** NR-RNG-003..005; TP-RNG-003..004; TP-NEG-006.

Exclude self destinations at k=32, k=64 and full-group escalation. Order candidates by
`(distance,destination lift tuple)`. If two complete assignments have exactly equal total cost after
the stochastic term, fail loudly as a reproducibility failure; do not accept library-dependent
tie-breaking.

**Rationale:** preserves derangement and removes ambiguous solver ties.
**Concordance:** completes the sealed bijection/derangement rule.

### AC-18 — Residualiser

**Resolves:** BLK-018.  
**Affected sealed sections:** Conditional-null v4.1 §2; Physical v7 §1.  
**Clean-room links:** NR-CV-007, NR-CV-009..011; TP-LEAK-002..003; TP-WIRE-003.

Fit 11 independent scalar HGBR models, one per raw M4 column, using the frozen common regressor
hyperparameters. Do not scale or jointly transform address columns. Execute the sealed inner
cross-fitting for training residuals and outer-fold application to held-out rows exactly once.

**Rationale:** fixes model count, hyperparameters and transformation topology.
**Concordance:** matches the manifest’s per-column `g_j^(a)` notation.

### AC-19 — R-squared

**Resolves:** BLK-019.  
**Affected sealed sections:** Physical v7 §2, §5; Conditional-null v4.1 §1–2.  
**Clean-room links:** NR-CV-008; NR-FAIL-002; TP-WIRE-004; TP-NEG-002.

Compute float64 `R2=1-SSE/SST` directly on exact held-out pooled rows. If `SST<=0`, or any input or
prediction is nonfinite, R2 is undefined and follows the sealed mixed/inconclusive route. Do not use
forced-finite library behavior.

**Rationale:** prevents library defaults from manufacturing a finite increment.
**Concordance:** defines the named held-out R2 statistic without changing its population.

### AC-20 — Numeric thresholds

**Resolves:** BLK-020 as broadened by adjudication.  
**Affected sealed sections:** all explicit thresholds and inequalities, especially Physical v7 §1,
§3a, §7 and MSD v8.1 §5, §7, §9, §12.  
**Clean-room links:** NR-GEO-010..014; NR-DYN-007..016; NR-GATE-000..009; TP-GATE-001.

Apply every sealed inequality literally in float64 with no hidden tolerance. Record the signed numeric
margin to each threshold. Any nonfinite value is a loud failure or enters the explicitly defined
undefined route. This includes exact membership behavior at `d_bound=2*ell` and `16*ell`.

**Rationale:** exposes rather than conceals threshold sensitivity.
**Concordance:** preserves all sealed strict/non-strict operators.

### AC-21 — G1 Boolean scope

**Resolves:** BLK-021.  
**Affected sealed sections:** MSD v8.1 §7, §12; Concordance G1 and claim conjunction.  
**Clean-room links:** NR-DYN-014; NR-GATE-002; NR-ROUTE-001..002; TP-WIRE-011; TP-ROUTE-002.

`coherentG1` means all nine coherent configuration-level G1 checks pass. `classicalG1` means all nine
classical checks pass for the cross-engine modifier. A classical failure does not erase an otherwise
valid coherent primary result. M9 membership never changes.

**Rationale:** converts per-cell checks into the sealed global conjunction.
**Concordance:** resolves a Boolean-reduction silence; matches the frozen claim split.

### AC-22 — Routing scope

**Resolves:** BLK-022.  
**Affected sealed sections:** Physical v7 §7; Conditional-null v4.1 §7; MSD v8.1 §12.  
**Clean-room links:** NR-ROUTE-001..005; TP-ROUTE-001..002.

Compression, survives-controls and mixed/undetectable are one global suite-level classification.
Per-cell values are descriptive except for explicitly sealed secondary G8 reporting. Never drop or
reclassify cells silently.

**Rationale:** aligns route granularity with M9/M_perm,7 global statistics.
**Concordance:** clarifies the manifest’s occasional “cell” wording without changing memberships.

### AC-23 — Geometry preflight

**Resolves:** BLK-023.  
**Affected sealed sections:** Physical v7 §3a, §5, §8; Conditional-null v4.1 §9.  
**Clean-room links:** NR-GEO-011..014; TP-GEO-002; TP-VOR-001; TP-RNG-004.

Before dynamics, recompute every geometry-only feasibility check in the clean implementation and
compare it with sealed provenance ranges. Any mismatch stops execution. M9 and M_perm,7 memberships
remain fixed; recomputation cannot select a more favorable membership.

**Rationale:** treats provenance as a conformance check, not an outcome-adaptive selector.
**Concordance:** preserves fixed membership and mandatory preflight.

### AC-24 — Sigma-floor moments

**Resolves:** BLK-024.  
**Affected sealed sections:** Physical v7 §1, §3 Group B.  
**Clean-room links:** NR-FEA-010..011; TP-FEA-002.

If sigma `<1e-9`, emit the mean normally and set variance, skewness and excess kurtosis—the three
higher moments after the mean—to exactly zero.

**Rationale:** disambiguates “three higher moments”.
**Concordance:** adopts the literal four-moment ordering in the seal.

### AC-25 — Padded/core correspondence and convergence

**Resolves:** BLK-025.  
**Affected sealed sections:** Physical v7 §3 Group E and §3a.  
**Clean-room links:** NR-GEO-013..014; NR-FEA-013; TP-VOR-001; TP-WIRE-001.

Match core vertices to padded vertices by exact lift tuple, exactly once each. Missing or duplicate
matches stop. Define padding-ring width as the minimum padded-hull depth of a core vertex divided by
ell and require it to be at least 3. For Delta=4 versus Delta=6, compare every matched core-cell area
and perimeter using relative denominator `max(abs(value_Delta6),1e-15)`; the maximum relative difference
must be `<=1e-6`. Any Qhull failure, unbounded cell, nonfinite geometry or correspondence failure stops.

**Rationale:** fixes row identity, ring metric, relative error and geometry failures.
**Concordance:** makes the sealed padding and convergence requirements executable without weakening them.

## Effect on scientific design

### True normative clarifications

AC-01, AC-03, AC-04, AC-06, AC-09..11, AC-13..25 specify previously unresolved populations,
failure routes, fitted-object scopes, statistics, Boolean reductions and geometry conformance. They
are outcome-blind but would become normative only after explicit ratification.

### Deterministic serialization and RNG choices

AC-02 and AC-05 fix stable geometry/schema serialization. AC-07, AC-12 and AC-15 propose separate
shuffle/address/capacity registries, while retaining the prominent missing-literal blockers above.
AC-14 fixes deterministic multiplicity ordering. These choices are reproducibility machinery, not
new scientific hypotheses or thresholds.

### Descriptive controls with no gate role

AC-08 makes the position and far-physical controls mandatory descriptive diagnostics at r=16 for both
engines. It gives them no gate, route, threshold or earned-claim role. AC-11 remains descriptive.

### Matters unchanged

The endpoint, radius ladder, six offsets, nine M9 cells, seven M_perm cells, propagation engines,
frozen HGBR hyperparameters, time grids, launch count, B=1000, 200 capacity draws, all G0–G8 thresholds,
claim conjunction, maximum claim language and prohibition on perpendicular-space ontology remain
unchanged. No outcome has been accessed and no study has been run.

## Old-item to proposed-clause map

| Old item | Clause | Resolution state |
|---|---|---|
| BLK-001 pipeline inheritance | AC-01 | proposed complete |
| BLK-002 generator contract | AC-02 | proposed complete |
| BLK-003 motif codebook | AC-03 | proposed complete |
| BLK-004 deduplication | AC-04 | proposed complete |
| BLK-005 physical serialization | AC-05 | proposed complete |
| BLK-006 PCA determinism | AC-06 | proposed complete |
| BLK-007 shuffle control | AC-07 | partial; stable-key derivation missing |
| BLK-008 position/far controls | AC-08 | proposed complete |
| BLK-009 launch indices | AC-09 | proposed complete |
| BLK-010 nonpositive MSD | AC-10 | proposed complete |
| BLK-011 SMD | AC-11 | proposed complete |
| BLK-012 address RNG | AC-12 | partial; literals/schema missing |
| BLK-013 quantile | AC-13 | proposed complete |
| BLK-014 Westfall–Young | AC-14 | proposed complete |
| BLK-015 capacity fields | AC-15 | partial; patch-substream derivation missing |
| BLK-016 matching scaler | AC-16 | proposed complete |
| BLK-017 matching ties | AC-17 | proposed complete |
| BLK-018 residualiser | AC-18 | proposed complete |
| BLK-019 R2 | AC-19 | proposed complete |
| BLK-020 numeric thresholds | AC-20 | proposed complete |
| BLK-021 G1 scope | AC-21 | proposed complete |
| BLK-022 routing scope | AC-22 | proposed complete |
| BLK-023 geometry preflight | AC-23 | proposed complete |
| BLK-024 sigma moments | AC-24 | proposed complete |
| BLK-025 padded/core matching | AC-25 | proposed complete |

## Ratification boundary

This document is a proposal only. It does not amend the seal by existing, and it must not be treated
as permission to implement or run the protocol. Ratification requires an explicit authority action
that also resolves the three remaining deterministic RNG blockers or knowingly keeps implementation
stopped. Until then: **NOT RATIFIED / NOT IMPLEMENTED / NOT RUN**.

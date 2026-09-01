# Implementation Clarification Amendment 1

**Status: RATIFIED / NOT IMPLEMENTED / NOT RUN**

**Ratification date:** 2026-09-01  
**Parent design seal:** `4ec0536319b531e8ad04dbfbbd0cd0e19ac57f55`  
**Parent clean-room specification:** `1a75925677c95d55be3773857b54dbadb8753bdd`  
**Proposal commit:** `ee4f7719109af9cc771c9a333e0fdcbe1c71834a`  
**Ratification authority:** Katie, human principal  
**Scientific review:** Work-GPT/Sol  
**Purpose:** outcome-blind clarification resolving the 25 items in `AMBIGUITIES_AND_BLOCKERS.md`.
This amendment has normative force as a companion to the parent seal under its post-seal amendment
policy, within the implementation boundary stated at the end of this document.

No study address values, targets, LDOS, beta values, scores, outcome curves, propagation results or
later prototype/audit branches were accessed. No scientific code was implemented and nothing was run.

## Deterministic-completion resolution record

Textual concordance found no direct contradiction between these adjudications and explicit sealed
wording. Ratification supplies the previously missing deterministic details for AC-07, AC-12 and
AC-15: canonical JSON and hash rules, literal BLAKE2b personalisations, exact NumPy generator
construction and consumption order, and the complete capacity spawn tree. All 25 clarification
clauses are therefore ratified complete.

For AC-07 and AC-12, canonical JSON is UTF-8 encoded with `ensure_ascii=True`, `allow_nan=False`,
separators exactly `(",",":")`, `sort_keys=False`, and fields inserted in each clause's exact stated
order. Family is exactly `"silver"`, `"golden"` or `"platinum"`; tier is exactly `"small"`,
`"medium"` or `"large"`; extent and offset index are base-10 JSON integers; offset index is 0..5
in the frozen offset order; and motif tuples are represented recursively as JSON arrays containing
JSON integers only. Each keyed RNG uses BLAKE2b with `digest_size=8`; split its digest big-endian as
`u0=int.from_bytes(digest[0:4],"big")` and `u1=int.from_bytes(digest[4:8],"big")`. Use NumPy
`Generator(PCG64(seed_sequence))`, never `default_rng`, and pin and record the exact NumPy version.

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

**Resolves:** BLK-007.  
**Affected sealed sections:** MSD v8.1 §8, §12 G4; sealed-parent baseline `assemble`.  
**Clean-room links:** NR-CV-012; NR-GATE-005; TP-RNG-002; TP-WIRE-005, TP-WIRE-010.

Permute each raw two-component perpendicular-address row jointly, then recompute `_m4_cols`. Group by
the exact sealed-parent formula:

```text
rank = deg.argsort().argsort()
degree_decile = clip(rank * 10 // n, 0, 9)
group = motif_code * 10 + degree_decile
```

Use one patch-level shuffle shared across folds and engines. The canonical JSON object has fields in
this exact order: `family`, `tier`, `extent`, `offset_index`. Hash it under the shared canonical rules
with BLAKE2b personalisation literal `b"GIV-SHUFFLE-v1"`, and construct
`SeedSequence(20260901,spawn_key=(u0,u1))` and `Generator(PCG64(seed_sequence))`.

Both degree-ranking `argsort` operations use stable sorting. Process groups in ascending
`(motif_code,degree_decile)` order. Within each group, order members by exact lift identity. For each
nonsingleton group, call the patch generator's permutation operation exactly once and jointly permute
the raw two-component perpendicular-address rows. Singletons consume no random draw and remain fixed.
Store this one patch shuffle and reuse it across all folds and both engines. No mutable global RNG is
permitted.

**Rationale:** preserves paired G4 input while separating it from address and capacity registries.
**Concordance:** the degree-decile and joint raw-field behavior are exactly recoverable and compatible;
the baseline’s mutable RNG is superseded by the ratified deterministic derivation.

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

**Resolves:** BLK-012.  
**Affected sealed sections:** Conditional-null v4.1 §3–5.  
**Clean-room links:** NR-RNG-003..006; TP-RNG-001..005.

The canonical JSON object, excluding repetition, has fields in this exact order: `family`, `tier`,
`extent`, `offset_index`, `motif`. Encode it under the shared canonical rules and hash with BLAKE2b
personalisation literal `b"GIV-ADDRPERM-v1"`. For repetition `b=0..999`, construct
`SeedSequence(20260829,spawn_key=(u0,u1,b))` and `Generator(PCG64(seed_sequence))`.

Within each motif group, order sources and destinations by exact lift identity. Candidate destinations
retain AC-17's deterministic order. Generate stochastic uniform edge-cost terms as one float64
row-major stream in source-row then candidate-column order. Synchronise the same repetition number
across engines and comparisons; configuration/motif keys keep their streams distinct.

**Rationale:** removes traversal and scheduling dependence.
**Concordance:** compatible with the seal’s stable keyed derivation and synchronized repetitions; the
ratified literal, schema, generator and consumption order make the derivation executable.

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

**Resolves:** BLK-015.  
**Affected sealed sections:** Physical v7 §6; Conditional-null v4.1 §5–6.  
**Clean-room links:** NR-RNG-007; NR-AGG-003; TP-RNG-002, TP-RNG-005; TP-AGG-002.

Construct `draw_children=SeedSequence(20260830).spawn(200)` exactly once. For each draw child `b`,
construct exactly 54 patch children with the single call `patch_children=draw_children[b].spawn(54)`.
Patch order is family-major: silver small/medium/large, golden small/medium/large, platinum
small/medium/large; within every configuration, use the six offsets in frozen order.

Within a patch, order rows by exact lift identity and use `Generator(PCG64(patch_child))` to generate
one float64 C-order `(n_vertices,11)` array of independent standard normals. Store and reuse that exact
patch array across all outer folds and both engines for the draw. No other spawning or regeneration is
permitted and no address-derived scaling is applied.

**Rationale:** fixes distribution, dimensionality, reuse and scientific independence.
**Concordance:** compatible with 200 indexed children and full-M9 calibration; the complete spawn tree,
patch order, generator, shape, dtype and reuse graph are ratified.

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

AC-02 and AC-05 fix stable geometry/schema serialization. AC-07, AC-12 and AC-15 establish complete,
separate shuffle/address/capacity registries. AC-14 fixes deterministic multiplicity ordering. These
choices are reproducibility machinery, not new scientific hypotheses or thresholds.

### Descriptive controls with no gate role

AC-08 makes the position and far-physical controls mandatory descriptive diagnostics at r=16 for both
engines. It gives them no gate, route, threshold or earned-claim role. AC-11 remains descriptive.

### Matters unchanged

The endpoint, radius ladder, six offsets, nine M9 cells, seven M_perm cells, propagation engines,
frozen HGBR hyperparameters, time grids, launch count, B=1000, 200 capacity draws, all G0–G8 thresholds,
claim conjunction, maximum claim language and prohibition on perpendicular-space ontology remain
unchanged. No outcome has been accessed and no study has been run.

## Old-item to ratified-clause map

| Old item | Clause | Resolution state |
|---|---|---|
| BLK-001 pipeline inheritance | AC-01 | ratified complete |
| BLK-002 generator contract | AC-02 | ratified complete |
| BLK-003 motif codebook | AC-03 | ratified complete |
| BLK-004 deduplication | AC-04 | ratified complete |
| BLK-005 physical serialization | AC-05 | ratified complete |
| BLK-006 PCA determinism | AC-06 | ratified complete |
| BLK-007 shuffle control | AC-07 | ratified complete |
| BLK-008 position/far controls | AC-08 | ratified complete |
| BLK-009 launch indices | AC-09 | ratified complete |
| BLK-010 nonpositive MSD | AC-10 | ratified complete |
| BLK-011 SMD | AC-11 | ratified complete |
| BLK-012 address RNG | AC-12 | ratified complete |
| BLK-013 quantile | AC-13 | ratified complete |
| BLK-014 Westfall–Young | AC-14 | ratified complete |
| BLK-015 capacity fields | AC-15 | ratified complete |
| BLK-016 matching scaler | AC-16 | ratified complete |
| BLK-017 matching ties | AC-17 | ratified complete |
| BLK-018 residualiser | AC-18 | ratified complete |
| BLK-019 R2 | AC-19 | ratified complete |
| BLK-020 numeric thresholds | AC-20 | ratified complete |
| BLK-021 G1 scope | AC-21 | ratified complete |
| BLK-022 routing scope | AC-22 | ratified complete |
| BLK-023 geometry preflight | AC-23 | ratified complete |
| BLK-024 sigma moments | AC-24 | ratified complete |
| BLK-025 padded/core matching | AC-25 | ratified complete |

## Implementation boundary

This ratified amendment has normative force as a companion to the parent seal. It authorizes
specification reconciliation and synthetic implementation only. It does not authorize confirmatory
execution or access to address values, targets, LDOS, beta values, outcome curves or study propagation.
Status remains **RATIFIED / NOT IMPLEMENTED / NOT RUN** until separately authorized stages occur.

# Data-flow specification — clean-room Stage 1

**Status: RECONCILED SPECIFICATION / NOT IMPLEMENTED / NOT RUN**

Authority precedence: seal `4ec0536319b531e8ad04dbfbbd0cd0e19ac57f55`, ratified Amendment 1
at `d574fde530b9d033a898e03e532bfb30e9835caf`, then the reconciled Stage-1 specifications.

This is a typed, side-effect-free contract. “Ordered” means order is data, not presentation.

## Core types

```text
Family := Literal["silver","golden","platinum"]
Tier := Literal["small","medium","large"]
Engine := Literal["coherent","classical"]
Radius := Literal[2,4,8,12,16]
OffsetId := Int[0..5]
ConfigId := Int[0..8]
PatchKey := (ConfigId, OffsetId)
LiftId := exact integer lift-coordinate tuple
VertexId := LiftId within a patch
RowId := (PatchKey, LiftId) globally

Offsets[6,2] := ordered float64 constants
Configs[9] := ordered (Tier,Family,Extent)
PermutationConfigs[7] := ordered subset of Configs

PatchGeometry := {
  key: PatchKey, lifts: int64[n,d], par: float64[n,2], perp: float64[n,2],
  edges: int64[m,2], adjacency: CSR/bounded-list[n], ell: finite float>0,
  d_bound: float64[n], motif_key: canonical tuple[n]
}
```

All cross-patch arrays, populations, launches, paired rows, joins and fitted-object provenance carry
explicit `RowId`. A patch-local array may use `VertexId=LiftId`. Integer row positions are derived
array indices only and never scientific identities; positional coincidence is never a valid join.

## Geometry to populations

```text
generate(Config, Offset) -> CorePatch + PaddedSuperPatch
validate_edges_and_units(CorePatch) -> PatchGeometry
common_mask(PatchGeometry) -> bool[n] where d_bound>=16*ell
common_population(PatchGeometry) -> ordered RowId[n_common]
slab_registry(common RowIds) -> Map[RowId,slab_id in {0,1,2,3}]
launch_registry(common RowIds, slabs) -> ordered RowId[200]
```

Generation must not read targets. Padded geometry may contribute Voronoi cells only; rows are
restricted back to core stable IDs. The common mask is computed once and reused at all rungs,
controls, engines, and paired fits.

```text
GeometryPreflightState := Pass | FailCommonCount | FailSlabCount | FailGeometryConformance
LocalNullState[PatchKey] := Available | UnavailableSingletonFraction
```

Common count `<400`, slab count `<100`, or a required geometry-conformance failure stops geometry
preflight. Singleton fraction `>0.05` changes only `LocalNullState` for that patch/configuration: it
does not remove the configuration from M9 or invalidate plain, residual, parity or capacity results.
Platinum-e16/e18 are expected M9 members and expected M_perm,7 absences on all offsets; their frozen
local-null unavailability is not an accidental whole-suite preflight failure.

## Feature construction

```text
baseline_features(PatchGeometry, shared_codebook) -> M3[n,p3]
physical_features(PatchGeometry, padded_cells, Radius) -> Phys[n,p_r]
address_operator(PatchGeometry, raw_field[n,2]) -> Address11[n,11]
parity_raw(PatchGeometry,padded_cells) -> float64[n,2]  # degree, area
MotifRegistry[ConfigId] := pooled six-offset geometry-only registry frozen before outcomes
DedupSchema[ConfigId,Radius] := pooled six-common-set geometry-only schema frozen before outcomes
apply_dedup(DedupSchema, M3, Phys) -> X_r[n_common,p]
```

`p_r=(11,22,35,48,61)`. Feature schemas contain ordered names, source units, fitted-state provenance,
and a hash. `address_operator` is one shared operator for observed address, permuted raw address and
scaled parity raw fields. Calling it before raw-field permutation is a workflow error.

## Fold and fitted-object graph

For outer fold `o`, training patches have the other five offsets and test patches have offset `o`.
Within every training patch, slab j is held out simultaneously for inner fold j.

```text
OuterFoldInput := rows for all 9 configs x 6 offsets with immutable RowId
FitArtifact[T] := {value:T, fitted_patch_keys:set[PatchKey], fitted_row_ids:set[RowId],
                   outer_fold:OffsetId, inner_fold:optional Int, schema_hash:bytes}

Training-only fitted objects:
  parity scaler per outer fold,
  matching-feature scaler per outer fold/config,
  four address residualisers per address column and inner fold,
  outer address residualiser per address column,
  every outcome regressor.

Authorized geometry-only precomputed objects (not training-only fitted objects):
  MotifRegistry[ConfigId], pooled over all six offsets before outcome/address access,
  DedupSchema[ConfigId,Radius], pooled over all six common sets before outcome/address access,
  patch-local deterministic PCA/slab/launch registries computed without outcome/address access.
```

Every fitted `transform`/`predict` checks that held-out PatchKeys and RowIds are absent from the
artifact’s fit provenance.

## Dynamics and endpoint

```text
coherent_generator(PatchGeometry) -> sparse complex H[n,n]
classical_generator(PatchGeometry) -> sparse float Q[n,n]
propagate(generator, launches[<=50], times[161])
  -> stream TimeSlice[time, launch, state_or_probability]
reduce(TimeSlice, par, strip_mask)
  -> MSD[launch,161], P_strip[launch,161], conservation diagnostics
boundary_scan(all patches, both engines) -> CrossingRecord, G0
beta_fit(MSD[:, snapped_index[48]]) -> Beta[launch], R2Fit[launch]
```

Boundary scan is a hard workflow barrier: no beta values may enter regression until global G0 passes.
Batch outputs are keyed and reordered to the immutable launch registry before concatenation.

## Observed and control feature branches

```text
Observed:      X_r + address_operator(perp)
Baseline:      X_r
Parity:        X_r + address_operator(parity_scaler.transform(degree,area))
Residual:      X_r + cross_fitted_address_residuals
Capacity draw: X_r + gaussian[n,11]
Shuffle:       X_r + address_operator(stratified_permute(perp))
Position:      M3 + (x,y,r) [+ address for paired control]
Far physical:  M3 + six far descriptors [+ address for paired control]
Local null:    X_16 + address_operator(local_assignment(perp))
```

Each branch emits paired held-out `R2(base)`, `R2(augmented)`, `DeltaR2`, fold/config/offset IDs,
feature schema hashes, population hash and fit-provenance hashes.

## Randomisation identities

```text
AddressIdentity := {
  family: Family, tier: Tier, extent: Int, offset_index: OffsetId,
  motif: recursive integer-array canonical motif, repetition: Int[0..999]
}
AddressStream := PCG64(SeedSequence(20260829,spawn_key=(u0,u1,repetition)))
  where (u0,u1) derives from the exact AC-12 canonical object and b"GIV-ADDRPERM-v1"

CapacityIdentity := {
  draw_index: Int[0..199], patch_child_index: Int[0..53],
  patch_key: (family,tier,extent,offset_index) at that family-major child position
}
CapacityStream := PCG64(SeedSequence child at DrawChildren[draw_index].spawn(54)[patch_child_index])

PatchRandomisation := (AddressIdentity|CapacityIdentity, population_hash, feature_schema_hash)
```

No array traversal index may substitute for an identity. The same address repetition label across
configurations is a synchronized comparison index, not an identical stream: configuration and motif
fields keep streams distinct. A draw is complete only after all required offset/config/engine cells
are present. Partial draws cannot enter aggregation.

## Aggregation

```text
fold_increment[measure, engine, radius, config=9, offset=6]
per_offset = median_config(fold_increment)       # first axis reduction
M9 = median_offset(per_offset)                   # second reduction

perm_increment[draw=1000, engine, config=7, offset=6]
Mperm7[draw] = median_offset(median_config(perm_increment[draw]))

capacity_increment[draw=200, engine, config=9, offset=6]
capacity_M9[draw] = median_offset(median_config(capacity_increment[draw]))
delta_cap = percentile95(capacity_M9)
```

Axis names and exact memberships must be validated before every reduction. Reversing the two median
operations is forbidden even when a particular synthetic example happens to give the same number.

## Gates and final routing

```text
G0 <- global crossing record
G1 <- pooled per-(config,engine) median R2Fit
G2 <- observed coherent Mperm7 and 1000 complete null Mperm7 values
G3 <- coherent address M9, delta_cap
G4 <- fold/config paired reductions before M9 aggregation
G5 <- coherent and classical address M9 plus both G1 states
G6 <- residual M9, delta_cap
G7 <- address/parity M9 difference (report-only)
G8 <- seven signed config statistics and synchronized null matrix

route_physical <- feasibility, r2/r16 M9, sign vector, delta_cap, rho, G2/G3/G6
route_transport <- G0, coherent G1, G2, G3, G4, G6
modifier <- classical G1 and G5
report <- gates + routes + diagnostics + fixed claim-boundary vocabulary
```

No route may mutate configuration membership or discard an undefined cell. Final output includes
all six offset effects, all nine configuration identities, seven permutation identities, all gate
states (pass/fail/undefined/inconclusive/descriptive as applicable), and a machine-readable audit log.

## Ratified Amendment 1 executable contracts

This section resolves the earlier `BLK-*` annotations. The historical notes remain in the blocker
ledger, but none is operative after reconciliation.

### Identities, axes and schemas

```text
LiftId := exact integer lift-coordinate tuple    # identical to Core types
VertexTable := rows sorted lexicographically by LiftId, unique and complete
EdgeId := (min(LiftId_a,LiftId_b), max(...))      # endpoint-identity order
EdgeTable := unique EdgeId rows sorted lexicographically

GeneralConfigAxis[9] := tier-major [
  silver-small, golden-small, platinum-small,
  silver-medium, golden-medium, platinum-medium,
  silver-large, golden-large, platinum-large]

CapacityConfigAxis[9] := family-major [
  silver-small, silver-medium, silver-large,
  golden-small, golden-medium, golden-large,
  platinum-small, platinum-medium, platinum-large]

OffsetAxis[6] := exact frozen offset order; OffsetIndex := 0..5
CapacityPatchAxis[54] := product(CapacityConfigAxis, OffsetAxis), offset-fast
```

Every generator output array is rekeyed by `LiftId`. Missing, duplicate or reordered identities and
noncanonical/duplicate edges fail before feature construction. Generator call contract is
`generate(N,extent,offset=sealed_offset,disorder=0.0,seed=0,extra_offset=None,
disorder_extra=False)->(lifts,par,perp,ustar)`, followed by `build_edges(lifts,N,ustar)`.

```text
MotifRegistry[ConfigId] := sort_lex(unique(motif tuples over all six geometry-only patches))
MotifSchema := immutable one-hot order; unseen motif -> LoudFailure

DedupSchema[ConfigId,Radius] := {
  pooled_population_hash, retained_phys_columns, dropped_phys_columns,
  matches: Map[PhysColumn,List[M3Column]]
}
```

Motif registries and dedup schemas are computed before outcome access. Dedup pools all six common
sets per configuration/radius, uses `<1e-12`, retains M3, and is reused unchanged across folds.

`physical_extra` serialization is a scale stream:

```text
for s newly admitted in (2,4,8,12,16):
  append newly admitted A annuli
  append B_s(mean,var,skew,excess_kurtosis)
  append D_s(psi_N/2,psi_N,psi_2N)
  append E_s(voronoi_mean,voronoi_var)
```

Each emitted r2/r4/r8/r12 vector is an exact column prefix of r16 with widths 11/22/35/48/61.

### PCA, slabs and launches

```text
PCAInput := float64 par[n_common,2] centred by population mean
Cov := (X.T @ X) / n_common
(eigenvalues,eigenvectors) := symmetric_eigensolve(Cov)
tie_tol := 1e-12 * max(1,abs(lambda_max))
```

If the largest two eigenvalues differ by no more than `tie_tol`, return `SlabInfeasible`. Otherwise
orient PC1 by the first component with magnitude `>1e-15`; no such component also returns
`SlabInfeasible`. Sort projections with lift identity as the tie key, create four equal-count slabs
with remainder to lowest indices, and in each slab select indices `floor(j*(n-1)/49)`, j=0..49.
Duplicate/out-of-range indices or counts other than 50 per slab/200 per patch are loud failures.

### Canonical keyed RNG objects

```text
CanonicalJSON := UTF8(JSON(ensure_ascii=True,allow_nan=False,
                           separators=(",",":"),sort_keys=False))
Digest8(person,key_bytes) := blake2b(key_bytes,digest_size=8,person=person)
u0 := int.from_bytes(digest[0:4],"big")
u1 := int.from_bytes(digest[4:8],"big")
RNG(seed_sequence) := Generator(PCG64(seed_sequence))
```

Pin and record NumPy version. Family/tier strings and integer/motif representations are exactly
NR-AMD-007/012; NaN and non-integer motif content cannot serialize.

```text
ShuffleKey := ordered JSON object {
  family, tier, extent, offset_index
}
ShuffleSeed := SeedSequence(20260901,spawn_key=(u0,u1))
ShuffleDigestPerson := b"GIV-SHUFFLE-v1"

AddressKey := ordered JSON object {
  family, tier, extent, offset_index, motif
}
AddressSeed[b] := SeedSequence(20260829,spawn_key=(u0,u1,b)), b=0..999
AddressDigestPerson := b"GIV-ADDRPERM-v1"
```

Shuffle degree ranks use two stable argsorts. Groups are ascending `(motif_code,degree_decile)`;
members are lift-sorted. Each nonsingleton makes exactly one `permutation` call and jointly permutes
raw address rows; a singleton makes none. The stored patch permutation is shared across folds/engines.

Address sources/destinations are lift-sorted, candidates ordered by
`(distance,destination_lift_tuple)`, and uniform float64 costs are consumed source-row then
candidate-column. A repetition is synchronized across engines/comparisons. Assignment-total equality
after stochastic terms is `ReproducibilityFailure`.

### Capacity spawn tree

```text
CapacityRoot := SeedSequence(20260830)
DrawChildren[200] := CapacityRoot.spawn(200)             # exactly one call
PatchChildren[b,54] := DrawChildren[b].spawn(54)         # exactly one call per b
CapacityField[b,patch] := C-contiguous float64 result of
  RNG(PatchChildren[b,patch]).standard_normal(size=(n_vertices,11),dtype=float64)
```

The patch axis is `CapacityPatchAxis`, not `GeneralConfigAxis`. Rows are lift-sorted. Each field is
stored once and reused across all outer folds and engines; regeneration, extra spawning and
address-derived scaling fail provenance validation.

### Fitted objects, endpoint and statistics

```text
MatchingScaler[ConfigId,OuterFold] := population mean/SD fitted on five training offsets
if train_SD < 1e-12: transformed train and held-out column := 0

Residualiser[OuterFold,InnerFold,AddressColumn=0..10] := scalar frozen HGBR
OuterResidualiser[OuterFold,AddressColumn=0..10] := scalar frozen HGBR
```

Residualisers are unscaled and independent; inner cross-fitted training residuals and one outer-held
application occur exactly once. Provenance rejects reuse or joint/multi-output transformation.

```text
R2Result := Defined(float64) | Undefined(reason)
R2 := 1 - SSE/SST on exact pooled held-out rows
Undefined iff SST<=0 or inputs/predictions are nonfinite

EndpointState := Valid(Beta,R2Fit) | InvalidNonpositiveMSD | InvalidNonfiniteMSD
```

Any nonpositive/nonfinite MSD at one of 48 fit times invalidates the entire configuration-engine
endpoint. No epsilon, launch culling or window shortening exists. Coherent invalidity makes global
`coherentG1=false` and the coherent result unavailable/downgraded; classical invalidity makes the
modifier inconclusive.

`coherentG1=all(G1[coherent,config] for config in GeneralConfigAxis)` and likewise classical G1.
The global suite route consumes all fixed M9/M_perm cells; no per-cell drop/reclassification exists.
Position/far controls are mandatory r16 reports for both engines but are absent from every gate input.
All threshold functions operate literal float64 inequalities and return threshold margins.

### Padded/core correspondence

```text
CoreToPadded := exact one-to-one join on LiftId
ring_width := min(padded_hull_depth[core_ids]) / ell
relative_delta := abs(value_D4-value_D6) / max(abs(value_D6),1e-15)
```

Require every core ID exactly once, `ring_width>=3`, finite bounded cells and maximum per-cell area
and perimeter relative delta `<=1e-6`. Missing/duplicate join, Qhull error, unbounded/nonfinite cell
or convergence failure returns `GeometryPreflightFailure` and stops before dynamics.

```text
GeometryReferenceSource := {
  path, git_blob, section, scope, quantity, units,
  value_status: ExactDiscrete|ExactThreshold|ReportedRange|RoundedExpectation,
  role: HardFeasibility|FrozenMembership|ExactIdentityCheck|ProvenanceOnly
}
```

The self-contained values and roles are in `NORMATIVE_REQUIREMENTS.md::GeometryReferenceRegistry`.
Exact-threshold failure and exact-discrete identity mismatch stop; frozen membership fixes M9/M_perm,7;
rounded/aggregate expectations are reported side-by-side with no invented equality tolerance or gate.
Sources are seal blobs `PREFLIGHT_GEOMETRY_REPORT_V2.md`
`1c2995cc16bb5b8c0b8777550a461d4593966b48` and `SIX_OFFSET_AUDIT_REPORT.md`
`2470997bf70c16c1ee6af6f13784b4212d56a291`. Required physical-size matching remains a frozen
pre-seal tier-selection fact and cannot change fixed M9/M_perm membership.

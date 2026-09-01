# Data-flow specification — clean-room Stage 1

This is a typed, side-effect-free contract. “Ordered” means order is data, not presentation.

## Core types

```text
Family := Literal["silver","golden","platinum"]
Tier := Literal["small","medium","large"]
Engine := Literal["coherent","classical"]
Radius := Literal[2,4,8,12,16]
OffsetId := Int[0..5]
ConfigId := Int[0..8]
VertexId := stable patch-local integer
PatchKey := (ConfigId, OffsetId)

Offsets[6,2] := ordered float64 constants
Configs[9] := ordered (Tier,Family,Extent)
PermutationConfigs[7] := ordered subset of Configs

PatchGeometry := {
  key: PatchKey, lifts: int64[n,d], par: float64[n,2], perp: float64[n,2],
  edges: int64[m,2], adjacency: CSR/bounded-list[n], ell: finite float>0,
  d_bound: float64[n], motif_key: canonical tuple[n]
}
```

All arrays carry explicit row `VertexId`; positional coincidence is never sufficient for a join.

## Geometry to populations

```text
generate(Config, Offset) -> CorePatch + PaddedSuperPatch
validate_edges_and_units(CorePatch) -> PatchGeometry
common_mask(PatchGeometry) -> bool[n] where d_bound>=16*ell
slab_registry(common rows) -> slab_id[n_common] in {0,1,2,3}
launch_registry(common rows, slabs) -> ordered VertexId[200]
```

Generation must not read targets. Padded geometry may contribute Voronoi cells only; rows are
restricted back to core stable IDs. The common mask is computed once and reused at all rungs,
controls, engines, and paired fits.

## Feature construction

```text
baseline_features(PatchGeometry, shared_codebook) -> M3[n,p3]
physical_features(PatchGeometry, padded_cells, Radius) -> Phys[n,p_r]
address_operator(PatchGeometry, raw_field[n,2]) -> Address11[n,11]
parity_raw(PatchGeometry,padded_cells) -> float64[n,2]  # degree, area
dedup(M3_common, Phys_common) -> (X_r[n_common,p], DedupRecord)
```

`p_r=(11,22,35,48,61)`. Feature schemas contain ordered names, source units, fitted-state provenance,
and a hash. `address_operator` is one shared operator for observed address, permuted raw address and
scaled parity raw fields. Calling it before raw-field permutation is a workflow error.

## Fold and fitted-object graph

For outer fold `o`, training patches have the other five offsets and test patches have offset `o`.
Within every training patch, slab j is held out simultaneously for inner fold j.

```text
OuterFoldInput := rows for all 9 configs x 6 offsets with immutable PatchKey/VertexId
FitArtifact[T] := {value:T, fitted_patch_keys:set[PatchKey], fitted_vertex_ids:set[VertexId],
                   outer_fold:OffsetId, inner_fold:optional Int, schema_hash:bytes}

Training-only fitted objects:
  shared motif codebook (scope must be clarified by BLK-003),
  parity scaler per outer fold,
  matching-feature scaler per outer fold/config,
  four address residualisers per address column and inner fold,
  outer address residualiser per address column,
  every outcome regressor,
  PCA/slab objects where applied outside an independently defined patch-local transform.
```

Every `transform`/`predict` checks that held-out PatchKeys and row identities are absent from the
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
PermutationDrawKey := (root=20260829, b[0..999], Family, Tier, OffsetId, MotifKey)
CapacityDrawKey := (root=20260830, child_index[0..199])
PatchRandomisation := (DrawKey, PatchKey, population_hash, feature_schema_hash)
```

No array traversal index may substitute for a key. A draw is complete only after all required
offset/config/engine cells are present. Partial draws cannot enter aggregation.

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

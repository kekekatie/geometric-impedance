# Normative requirements — clean-room Stage 1

**Status: RECONCILED SPECIFICATION / AMENDMENT 2 RATIFIED / NOT IMPLEMENTED / NOT RUN**

Normative authority, in precedence order: parent seal commit
`4ec0536319b531e8ad04dbfbbd0cd0e19ac57f55`; ratified companion
`IMPLEMENTATION_CLARIFICATION_AMENDMENT_1_DRAFT.md` at
`d574fde530b9d033a898e03e532bfb30e9835caf`; ratified
`SYNTHETIC_CONFORMANCE_PROTOCOL_AMENDMENT_2_DRAFT.md` at
`0d365bd26683feaa833739af15091cc1955d6935`; then these reconciled clean-room specifications.
No study dynamics or outcomes have been run or accessed.

## Sources and precedence

The normative sources are the five artifacts named by `SEAL_RECORD.md`, read at seal commit
`4ec0536319b531e8ad04dbfbbd0cd0e19ac57f55`, plus the frozen 48-time companion list. Requirement
IDs are stable: clarification appends IDs rather than renumbering existing ones. All historical
BLK-001..025 annotations are resolved by ratified NR-AMD-001..025; the ledger preserves their history.
Ratified Amendment 2 appends NR-SCP-001..010 and changes synthetic-conformance evidence only. It
does not change any scientific constant, production requirement or confirmatory-run computation.

## Geometry, configurations and populations

- **NR-GEO-001** Define `ell` per patch as the median edge length.
- **NR-GEO-002** Interpret radius `r` as Euclidean parallel-space distance `<= r*ell`.
- **NR-GEO-003** Use radius ladder, in order, `S=(2,4,8,12,16)` and reference radius 16.
- **NR-GEO-004** Use offsets, in order: `(0.13,0.37)`, `(0.29,0.11)`, `(0.41,0.23)`,
  `(0.05,0.47)`, `(0.19,0.31)`, `(0.37,0.09)`.
- **NR-GEO-005** Use nine configurations, in order: silver-e14, golden-e18, platinum-e16,
  silver-e16, golden-e20, platinum-e18, silver-e18, golden-e22, platinum-e20 (tier-major:
  small, medium, large; family order silver, golden, platinum).
- **NR-GEO-006** `M9` always contains all nine configurations and is never altered by observed fit
  quality or permutation feasibility.
- **NR-GEO-007** `M_perm,7` contains, in order inherited from NR-GEO-005: silver-e14, golden-e18,
  silver-e16, golden-e20, silver-e18, golden-e22, platinum-e20.
- **NR-GEO-008** Platinum-e16 and platinum-e18 remain in `M9` but are infeasible for the local
  permutation control and cannot pass G2.
- **NR-GEO-009** Define `d_bound(i)=hull_depth(par)[i]`, the signed distance to the convex hull of
  parallel-space points; positive values are interior depths.
- **NR-GEO-010** Use the common evaluated population `{i:d_bound(i)>=16*ell}` at every radius rung.
- **NR-GEO-011** An r16 common set with fewer than 400 rows, an inner slab with fewer than 100 rows,
  or failure of a required geometry conformance check is a geometry preflight failure. A singleton
  fraction greater than 5% makes only that patch/configuration's local-permutation control unavailable;
  it does not remove the configuration from M9 or invalidate plain, residual, parity or capacity
  results. Platinum-e16/e18 remain expected M9 members and expected M_perm,7 absences. Required
  physical-size matching is a frozen tier-selection fact, never permission to re-tier.
- **NR-GEO-012** Retain golden aspect-ratio morphology as a mandatory descriptive diagnostic; add
  no regression feature or extra control for it.
- **NR-GEO-013** For Voronoi descriptors generate a super-patch at core extent plus `Delta>=4`,
  with padding-ring width at least `3*ell`; flag inability rather than reducing padding.
- **NR-GEO-014** Require relative agreement between Delta=4 and Delta=6 padded-cell area and
  perimeter within `1e-6` on core cells before Stage 2 use.

## Baseline and physical features

- **NR-FEA-001** Define `X_r=[M3,physical_extra(r)]`; retain all M3 columns at every rung.
- **NR-FEA-002** M3 order is `dens, deg, edge_len_mean, edge_len_var, shared motif one-hot,
  g(1.6),g(2.6),psi_N,psi_(N/2),psi_(2N),g(4.0),g(6.0)`.
- **NR-FEA-003** Counts `dens=g(2.0)` and `g(rho)` include the query point, matching the inspected
  sealed baseline `cKDTree.query_ball_point(...,return_length=True)` contract.
- **NR-FEA-004** Define `psi_n(i)=abs(mean(exp(i*n*theta)))` over incident bonds.
- **NR-FEA-005** Define motif key as the canonical sorted multiset of incident `(star-line,sign)`;
  build one shared codebook across offsets. Registry scope/order is resolved by NR-AMD-003 (BLK-003).
- **NR-FEA-006** Drop a physical-extra column only when `max(abs(delta))<1e-12` against an M3
  column on the evaluated set; never drop M3. Multi-match and fold scope are resolved by
  NR-AMD-004 (BLK-004).
- **NR-FEA-007** `physical_extra(r)` consists of Group A annuli and, for each `s in S` with `s<=r`,
  Group B degree moments, Group D coarse psi values and Group E Voronoi moments. Exact prefix
  serialization is resolved by NR-AMD-005 (BLK-005), which controls any earlier ordering ambiguity.
- **NR-FEA-008** Group A bin index is `ceil(d/ell-1e-9)`, centre excluded, bins 1..r,
  corresponding to left-open/right-closed annuli; emit r columns.
- **NR-FEA-009** For each permitted s, define `Nb(i,s)={j!=i:||par[j]-par[i]||<=s*ell}`.
- **NR-FEA-010** Group B emits the mean and, when sigma `>=1e-9`, ordinary population variance
  (`ddof=0`), skewness and excess kurtosis of neighbour degrees; if empty use `{deg[i]}`.
- **NR-FEA-011** For any moment sample with sigma `<1e-9`, emit the mean normally and set variance,
  skewness and excess kurtosis exactly to zero. At sigma `>=1e-9`, compute ordinary population
  variance, skewness and excess kurtosis. This boundary is identical to NR-AMD-024.
- **NR-FEA-012** Group D emits means over `{i} union Nb(i,s)` for `psi_(N/2),psi_N,psi_(2N)`.
- **NR-FEA-013** Group E emits mean and population variance of bounded padded-Voronoi cell areas in
  `Nb(i,s)`; if none are bounded, use `(area[i],0)`.
- **NR-FEA-014** Physical-extra dimensions at r=(2,4,8,12,16) are (11,22,35,48,61), respectively,
  and the blocks must be strictly nested.
- **NR-FEA-015** Exclude edge-length moments from physical-extra.
- **NR-FEA-016** Address is the raw two-component perpendicular field transformed by the exact
  11-column `_m4_cols` dependency: for graph shells 2,4,8 emit two shell means and scalar summed
  component variance per shell; then a local linear-gradient Frobenius norm and convex-hull depth.
- **NR-FEA-017** `_m4_cols` graph shells include the centre (`distance=0`); the local gradient uses
  all parallel points within radius 3.0 and is zero with fewer than four points.
- **NR-FEA-018** Parity raw field is `(graph degree,padded Voronoi-cell area)` transformed through
  the same `_m4_cols` operator.
- **NR-FEA-019** Fit the parity z-score scaler per outer fold on pooled r16 common-set rows from the
  five training offsets; apply unchanged to the held-out offset.
- **NR-FEA-020** If either parity component has within-set std `<1e-9` on a patch, mark parity
  unavailable/infeasible and report it; do not substitute capacity.

## Folds, regressions and increments

- **NR-CV-001** Outer validation leaves one entire offset out, yielding six correlated fold values.
- **NR-CV-002** Never treat the six folds as independent replicates; always report all six values
  and signs. At least 5/6 positive is supporting, not a standalone test.
- **NR-CV-003** In every patch, centre r16 common-set parallel coordinates, compute PC1, and use its
  projections to form four contiguous equal-count slabs.
- **NR-CV-004** Fix PC1 orientation and degeneracy handling under NR-AMD-006 (BLK-006), which
  reconciles the earlier component-sign shorthand.
- **NR-CV-005** Break projection ties by lexicographic integer lift coordinates and assign remainder
  rows to lowest-index slabs.
- **NR-CV-006** Inner fold j simultaneously holds out slab j from every outer-training patch.
- **NR-CV-007** Use `HistGradientBoostingRegressor(max_depth=3,max_iter=250,learning_rate=0.06,
  l2_regularization=1.0,random_state=0)` for all rungs and controls.
- **NR-CV-008** Every increment is held-out `DeltaR2=R2(X_r+block)-R2(X_r)` with identical fold
  populations and target rows in the paired fits.
- **NR-CV-009** Residual-address training rows must be generated by four-fold inner cross-fitting;
  each row is predicted by a residualiser that did not train on its slab.
- **NR-CV-010** Fit the outer residualiser on all five training offsets and apply it to the unseen
  offset; fit one residualiser per address column.
- **NR-CV-011** Residual-address increments are deterministic lower-bound diagnostics, not
  randomisation tests, and are evaluated at every radius.
- **NR-CV-012** The exact sealed stratified-shuffle control permutes raw perpendicular coordinates
  inside motif x degree-decile groups, recomputes `_m4_cols`, and computes paired plain/shuffle
  increments. Degree-decile and RNG identities are resolved by NR-AMD-007 (BLK-007).
- **NR-CV-013** Position and far-physical controls inherit the inspected sealed baseline definitions:
  position `(x,y,hypot(x,y))`; far block `g(8),g(12), neighbour-degree means at 5 and 9,
  coarse psi_N means at 5 and 9`. Their descriptive-only role is resolved by NR-AMD-008 (BLK-008).

## Propagation and endpoint

- **NR-DYN-001** Coherent generator is adjacency `H=A`, with uniform hopping, `hbar=J=1`.
- **NR-DYN-002** Classical generator is column-stochastic `Q=A*D^-1-I`, unit exit rate, and
  `p(t)=exp(Qt)e_v0`; use the same Krylov method and time grid.
- **NR-DYN-003** Select 200 launches per patch, 50 per PCA slab, by sorting on `(PC1 projection,
  lift lexicographic)` and using the exact NR-AMD-009 formula (BLK-009). The reconciled n>=100
  feasibility floor controls; a wrong count fails loudly.
- **NR-DYN-004** Use exactly localised initial states at selected vertices and the full spectrum.
- **NR-DYN-005** Use sparse/block `scipy.sparse.linalg.expm_multiply`, launch batches of 50, and
  reduce each time slice to MSD and strip mass without materialising a T x V x L tensor.
- **NR-DYN-006** Use boundary grid `linspace(0,8,161)` and the 48 frozen snapped times, in their
  companion-file order, asserting uniqueness and membership in the boundary grid.
- **NR-DYN-007** Define boundary strip `{v:d_bound(v)<2*ell}` and excess strip mass relative to t=0.
- **NR-DYN-008** A launch/engine crosses at the earliest grid time, including 8, with excess strip
  mass `>=0.01`; global `t_bound*` is the earliest across all launches, patches and both engines.
- **NR-DYN-009** Compute G0 before beta inference. Proceed to beta only when no crossing is observed
  through t=8 (`t_bound*=+infinity`, strictly greater than 8); otherwise route finite-size-limited.
- **NR-DYN-010** Compute coherent MSD with probability `abs(psi)^2` and classical MSD with p, using
  squared parallel distance from the launch.
- **NR-DYN-011** Fit OLS of `log(MSD)` on `log(t)` at all 48 snapped times; beta is half the slope
  and `R2_fit` is recorded. Domain/failure handling is resolved by NR-AMD-010 (BLK-010).
- **NR-DYN-012** Do not cull admitted launches using R2, curvature, beta or any dynamics-derived
  property; every admitted launch must yield beta or fail loudly.
- **NR-DYN-013** Report per-M4-column admitted-versus-excluded mean, SD and standardised mean
  difference; no threshold or gate. The SMD convention is resolved by NR-AMD-011 (BLK-011).
- **NR-DYN-014** Per `(config,engine)`, pool admitted launches over all offsets and require median
  `R2_fit>=0.90` for G1; never change M9 membership.
- **NR-DYN-015** Validate Krylov against exact diagonalisation on synthetic graphs at common grid
  times with max state error `<=1e-10`.
- **NR-DYN-016** Require coherent norm error `<=1e-8`; classical mass error `<=1e-8` and every
  probability `>=-1e-10`; flag violations and never silently use them.
- **NR-DYN-017** The mid-band endpoint and edge-weighted Hamiltonian are outside the primary sealed
  protocol; do not introduce them into Stage 2 production execution.

## Randomisation, capacity and aggregation

- **NR-RNG-001** Local permutation operates only at r=16 within `(family,tier,offset,exact motif)`.
- **NR-RNG-002** Standardise the continuous matching features `dens=g(2),deg,g(1.6),g(2.6),
  g(4),g(6),psi_N,psi_(N/2),psi_(2N)` using a training-only scaler.
- **NR-RNG-003** Construct the 32-nearest same-motif, self-excluded candidate graph in standardised
  feature distance and solve a minimum-cost perfect assignment with cost `distance+U(0,1)`.
- **NR-RNG-004** Escalate deterministically 32 -> 64 -> full group when no perfect assignment exists,
  flagging escalation; never choose k from outcomes and never use `distance*U`.
- **NR-RNG-005** Permute the raw two-component address, then recompute `_m4_cols`; construct train
  and held-out permutations separately. Singletons remain fixed in observed and null populations.
- **NR-RNG-006** Use `B=1000` repetitions from address root `SeedSequence(20260829)` and stable keys,
  independent of traversal order and synchronised where pairing and max-T require it. Exact key,
  hash, generator and consumption semantics are resolved by NR-AMD-012 (BLK-012).
- **NR-RNG-007** Capacity uses separate root `SeedSequence(20260830)` with 200 child streams indexed
  0..199, one iid-Gaussian block per child having the parity block dimensionality.
- **NR-RNG-008** Parity is deterministic and has no seed.
- **NR-AGG-001** For any ordinary measure, first take the equal-weight median across nine configs
  within each offset, then the median across six offsets to obtain `M9`.
- **NR-AGG-002** Build `M_perm,7` identically using exactly the seven ordered feasible configs.
- **NR-AGG-003** Define `delta_cap` as the 95th percentile of the 200 complete capacity-draw M9
  values using the NR-AMD-013 quantile method (BLK-013).
- **NR-AGG-004** Define `q_ref=(1+count(M_null>=M_obs))/(B+1)` and describe it only as extremeness
  under the constrained algorithmic stress reference, not a significance p-value.
- **NR-AGG-005** For G8 use signed one-sided config medians, raw uncentred null increments,
  Westfall-Young step-down max-T over seven cells, synchronized repetitions and monotonised
  adjusted extremeness values under NR-AMD-014 tie/order mechanics (BLK-014).

## Gates, routing and claims

- **NR-GATE-000** Evaluate G0 before any beta inference. Gate membership and thresholds below are
  immutable and any undefined denominator routes to mixed/undetectable.
- **NR-GATE-001** G0 passes iff `t_bound*>8`; otherwise route finite-size-limited and stop endpoint
  inference.
- **NR-GATE-002** G1 passes per `(config,engine)` iff pooled median `R2_fit>=0.90`; coherent failure
  downgrades/fails the global primary claim, while classical failure makes G5 inconclusive.
- **NR-GATE-003** G2 passes iff `q_ref<0.05` for coherent `M_perm,7,address`.
- **NR-GATE-004** G3 passes iff coherent `M9,address>delta_cap`.
- **NR-GATE-005** For each config/fold form `red=(plain-shuf)/plain`, then aggregate by the M9 order;
  G4 passes iff `R_kill>=0.70`. If any required plain value is `<=delta_cap` or `<=0`, global G4 is
  undefined and routes mixed; never drop that cell.
- **NR-GATE-006** G5 passes iff classical `M9,address <= 0.2*coherent M9,address`; it is undefined
  when coherent M9 is `<=delta_cap` or `<=0` and inconclusive on classical G1 failure.
- **NR-GATE-007** G6 passes iff deterministic residual `M9>delta_cap`; it is a lower-bound detection
  check, not a randomisation test.
- **NR-GATE-008** G7 reports address M9, parity M9 and their difference qualitatively; it has no
  threshold, no pass/fail, and delta_cap must not be applied to the difference.
- **NR-GATE-009** G8 is secondary/descriptive only and covers seven feasible cells.
- **NR-ROUTE-001** The primary coherent transport claim is earned iff G0, every coherent G1, G2,
  G3, G4 and G6 pass; G5 is not required.
- **NR-ROUTE-002** Add the cross-engine non-reproduction modifier only when every classical G1 and
  G5 pass; failure does not erase a coherent result.
- **NR-ROUTE-003** Compression requires r2 address M9 positive, >=5/6 positive, `>delta_cap`; r16
  address M9 `<delta_cap`; and `rho=r16/r2<0.25`. If the r2 prerequisite fails, rho is undefined and
  routes mixed, not infeasible.
- **NR-ROUTE-004** “Survives frozen stress controls” requires G3, G6 and G2; parity is descriptive
  and never part of this route.
- **NR-ROUTE-005** Any feasible result satisfying neither exact compression nor exact survives route
  is mixed/undetectable; do not invent a config-disagreement rule.
- **NR-CLAIM-001** Maximum claim wording: “The address representation predicts heterogeneity in
  full-spectrum wavepacket spreading beyond the frozen physical descriptions and controls.”
- **NR-CLAIM-002** Do not claim literal perpendicular-space physics, irreducibility, exchangeable-null
  significance, family ordering, or isolation of coherence from generator choice.
- **NR-CLAIM-003** Authorised non-positive labels include multiscale-geometry reading when shuffle
  is not killed, finite-size-limited on G0 failure, and no surfaced spreading signal when the stress
  reference is non-extreme.

## Failure discipline

- **NR-FAIL-001** Validate shapes, identities, ordering, finiteness, uniqueness, population equality,
  fold separation, scaler provenance and seed-key completeness at every workflow boundary.
- **NR-FAIL-002** Any malformed input, missing configuration/offset/draw, population drift, leakage,
  infeasible assignment, numerical-tolerance breach, undefined required value or hash/version mismatch
  must fail loudly or enter its explicitly named route; no silent row/cell dropping or fallback.
- **NR-FAIL-003** Stage 2 must not begin until every scientifically consequential blocker marked in
  `AMBIGUITIES_AND_BLOCKERS.md` is resolved by an authorised seal amendment or binding clarification.

## Ratified Amendment 1 requirements

These requirements append, without renumbering or redefining any prior ID, the executable substance
of AC-01 through AC-25. Each `NR-AMD-nnn` maps one-to-one to `AC-nn`.

- **NR-AMD-001 (AC-01 — pipeline inheritance).** The manifests supersede sealed-parent runner
  orchestration. Inherit only explicitly named primitives. Retain six outer leave-one-offset-out fold
  values and use four simultaneous PCA-slab inner folds; never inherit old held-out averaging,
  non-nested evaluation or runner-level averaging.
- **NR-AMD-002 (AC-02 — generators and identities).** Map silver/golden/platinum to N=8/10/12 and
  use the nine sealed extents and six sealed offsets. Call sealed rank-4 `structure(N)`,
  `generate(N,extent,offset=sealed_offset,disorder=0.0,seed=0,extra_offset=None,
  disorder_extra=False)` returning `(lifts,par,perp,ustar)`, then
  `build_edges(lifts,N,ustar)`. Vertex identity is the exact integer lift tuple. Sort vertices by that
  tuple, canonicalise each edge by sorted endpoint identities, then sort edges lexicographically.
  Missing, duplicate or reordered identities fail loudly.
- **NR-AMD-003 (AC-03 — motif registry).** Construct one geometry-only motif registry per
  family×tier configuration, pooled across all six offsets before outcome access. Sort canonical
  motif tuples lexicographically and use the resulting fixed one-hot order in every outer fold.
  An unseen motif is a loud error; no unknown bucket exists.
- **NR-AMD-004 (AC-04 — deduplication).** Determine dedup once per configuration/radius on pooled
  six-offset common-set physical/M3 rows. Drop a physical-extra column when it matches one or more
  M3 columns with `max(abs(delta))<1e-12`; retain M3 and record the dropped column plus every match.
  Apply the fixed schema to every fold.
- **NR-AMD-005 (AC-05 — physical serialization).** Serialize by successive scale. At each newly
  admitted `s`, append newly admitted A annuli, then B_s, D_s and E_s, with sealed within-group order.
  Require dimensions 11/22/35/48/61 and byte-for-byte column-prefix nesting across r=2/4/8/12/16.
- **NR-AMD-006 (AC-06 — PCA/slabs).** Use float64 population covariance and a symmetric eigensolver.
  Orient PC1 so its first component with magnitude `>1e-15` is positive. If the leading eigenvalue
  is tied within `1e-12*max(1,abs(lambda_max))`, or no component clears the orientation floor,
  declare slab construction infeasible and stop. Break projection ties by lift-tuple order.
- **NR-AMD-007 (AC-07 — stratified shuffle).** Canonical JSON fields are inserted exactly as
  `family,tier,extent,offset_index`, UTF-8 encoded with `ensure_ascii=True`, `allow_nan=False`,
  separators `(",",":")`, `sort_keys=False`, exact enumerated strings, base-10 integer extent/index,
  and frozen offset indices 0..5. Hash with BLAKE2b `digest_size=8`, personalisation
  `b"GIV-SHUFFLE-v1"`; split big-endian into uint32 `u0,u1`; use
  `Generator(PCG64(SeedSequence(20260901,spawn_key=(u0,u1))))` and pin/record NumPy version.
  Both degree `argsort`s are stable. Process `(motif_code,degree_decile)` groups ascending, members
  by lift identity; call permutation exactly once per nonsingleton, jointly permute raw address rows,
  consume nothing for singletons, recompute `_m4_cols`, and reuse the stored patch shuffle across
  folds and engines. No mutable global RNG.
- **NR-AMD-008 (AC-08 — position/far controls).** Run M3pos/M4pos and M3far/M4far as mandatory
  descriptive r16 diagnostics for both engines. They have no threshold, gate, route or earned-claim
  role; changing them must not change G0–G8 or final routing.
- **NR-AMD-009 (AC-09 — launches).** In a sorted slab of size n select exactly
  `floor(j*(n-1)/49)` for j=0..49. Require n>=100, 50 unique in-range indices per slab and 200 total;
  any duplicate or wrong count fails loudly.
- **NR-AMD-010 (AC-10 — MSD domain).** Add no epsilon and cull no launch. A nonfinite or nonpositive
  MSD at any of 48 fit times invalidates that configuration-engine endpoint. Coherent invalidity
  makes coherent G1 unsatisfied and the global coherent result unavailable/downgraded; classical
  invalidity makes the cross-engine modifier inconclusive. Never shorten the grid.
- **NR-AMD-011 (AC-11 — admission SMD).** Use pooled population SD
  `sqrt((var_admitted+var_excluded)/2)`. If below `1e-12`, return 0 when means agree within `1e-12`,
  otherwise signed infinity. This remains descriptive only.
- **NR-AMD-012 (AC-12 — address RNG).** Canonical JSON fields, excluding repetition, are exactly
  `family,tier,extent,offset_index,motif`; use the shared JSON rules, representing motif recursively
  as integer-only arrays. Hash with BLAKE2b `digest_size=8`, personalisation
  `b"GIV-ADDRPERM-v1"`, split big-endian to `u0,u1`, and for b=0..999 use
  `Generator(PCG64(SeedSequence(20260829,spawn_key=(u0,u1,b))))`, with pinned NumPy version.
  Order sources/destinations by lift identity, candidates by AC-17 order, and consume one float64
  uniform stream in source-row/candidate-column order. Synchronise b across engines/comparisons;
  distinct configuration/motif keys have distinct streams.
- **NR-AMD-013 (AC-13 — capacity quantile).** Compute float64 quantile 0.95 over exactly 200 complete
  capacity M9 draws using NumPy `method="linear"`.
- **NR-AMD-014 (AC-14 — Westfall–Young).** Use fixed seven-cell order silver small/medium/large,
  golden small/medium/large, platinum large. Stably sort observed statistics descending with that
  order breaking ties; use sealed signed one-sided raw-null step-down max-T and cumulative maximum
  along that ordering.
- **NR-AMD-015 (AC-15 — capacity fields).** Create
  `draw_children=SeedSequence(20260830).spawn(200)` once; for each b call
  `patch_children=draw_children[b].spawn(54)` exactly once. Capacity patch-child order is
  **family-major**: silver small/medium/large, golden small/medium/large, platinum
  small/medium/large, each followed by six frozen offsets. This is distinct from the general
  **tier-major** `Configs[9]` registry in NR-GEO-005. Within each patch, sort rows by lift identity
  and generate one float64 C-order `(n_vertices,11)` independent-standard-normal array with
  `Generator(PCG64(patch_child))`. Store/reuse it across all outer folds and both engines; no other
  spawn, regeneration or address scaling is permitted.
- **NR-AMD-016 (AC-16 — matching scaler).** Per configuration/outer fold fit mean and population SD
  on pooled common rows from five training offsets, apply unchanged to training and held-out patches,
  and map a feature with training SD `<1e-12` to zero in both representations.
- **NR-AMD-017 (AC-17 — matching candidates).** Exclude self at k=32, k=64 and full escalation.
  Order candidates by `(distance,destination_lift_tuple)`. Exact equality between complete assignment
  totals after stochastic cost is a loud reproducibility failure, never library tie-breaking.
- **NR-AMD-018 (AC-18 — residualisers).** Fit 11 independent scalar HGBRs with frozen common
  hyperparameters, one per raw M4 column. Do not scale or jointly transform address. Perform inner
  cross-fitting for training residuals and outer application to held-out rows exactly once.
- **NR-AMD-019 (AC-19 — R2).** Compute float64 `1-SSE/SST` directly on exact pooled held-out rows.
  If SST<=0 or any input/prediction is nonfinite, R2 is undefined and follows the sealed
  mixed/inconclusive route. Never invoke forced-finite library behavior.
- **NR-AMD-020 (AC-20 — thresholds).** Apply every sealed inequality literally in float64 without
  hidden tolerance, record signed margin to threshold, and send nonfinite values to a loud failure
  or explicitly defined undefined route. Exact `d_bound` boundary comparisons are included.
- **NR-AMD-021 (AC-21 — G1).** `coherentG1` is true iff all nine coherent configuration G1 checks
  pass. `classicalG1` is true iff all nine classical checks pass for the modifier. Classical failure
  cannot erase a valid coherent result; M9 membership never changes.
- **NR-AMD-022 (AC-22 — route scope).** Compression, survives-controls and mixed/undetectable are
  single global suite-level classifications. Per-cell values are descriptive except sealed G8.
  Never drop or reclassify cells.
- **NR-AMD-023 (AC-23 — geometry preflight).** Before dynamics, recompute all geometry-only
  feasibility checks and compare them under the typed roles in `GeometryReferenceRegistry` below.
  Failure of an explicit hard threshold or mismatch of an exact discrete generator/provenance record
  stops. Rounded descriptive expectations are reported side-by-side and never converted into equality
  tests or thresholds. M9 and M_perm,7 memberships remain fixed and cannot be outcome- or
  preflight-selected; the frozen physical-size match cannot authorize re-tiering.
- **NR-AMD-024 (AC-24 — sigma floor).** When sigma `<1e-9`, emit mean normally and set variance,
  skewness and excess kurtosis exactly to zero.
- **NR-AMD-025 (AC-25 — padded/core).** Match core to padded vertices one-to-one by exact lift tuple;
  missing/duplicate matches stop. Define ring width as minimum padded-hull depth of a core vertex
  divided by ell and require >=3. Compare each matched Delta=4/6 core-cell area and perimeter using
  denominator `max(abs(value_Delta6),1e-15)` and require maximum relative difference <=1e-6.
  Qhull failure, unbounded cell, nonfinite geometry or failed correspondence stops.

## Ratified Amendment 2 synthetic-conformance requirements

These requirements append stable IDs without renumbering or redefining any prior requirement.
TP-E2E-001, Test Acceptance and TP-AMD-030 are superseded only to the precise evidentiary extent
recorded in `CLEANROOM_TEST_PLAN.md`; their scientific constants and production requirements remain
in force. The retained `_DRAFT.md` filename is historical.

- **NR-SCP-001 (Layer A — exact component evidence).** Establish every production geometry,
  feature, regression, residualiser, matching, capacity, aggregation, dynamics and routing component
  with an independent reference, invariant, negative test and applicable mutation. A precomputed
  stage result or callback count is not evidence that a production component executed. Test both
  production dynamics engines independently against their exact references. A clearly identified
  synthetic dynamics adapter may control workflow runtime but is never evidence of coherent or
  classical scientific propagation.
- **NR-SCP-002 (Layer B — production-wired compliant slice).** Execute one frozen
  permutation-feasible configuration across all six offsets, with at least 400 common rows per
  offset, four slabs of at least 100 rows, exactly 200 launches per patch, both engine-labelled
  branches, all five radii, all six leakage-safe outer folds and the frozen inner-fold structure,
  plus observed, parity, shuffle, residual, position, far, local-null and capacity branches. The
  production orchestrator—not a high-level backend stub—owns and calls common-population validation,
  motif registry, deduplication, feature construction, slabs, launches, regressions, controls,
  matching, recomputed address features, capacity, aggregation, Westfall–Young, gates and routing.
  Execute address repetitions exactly `b={0,1,999}` and capacity draws exactly `{0,199}` as the
  representative numerical identities; every remaining frozen identity is covered by NR-SCP-003.
- **NR-SCP-003 (Layer C — full identity graph).** Enumerate and validate, without claiming numerical
  fitting, all 54 patch identities, 42,000 local-null identities, 10,800 capacity identities, every
  engine/fold axis, exact frozen labels/membership/order, seeds, keyed provenance, RNG consumption,
  synchronization and permitted reuse. Independently golden-verify identity and seed values.
- **NR-SCP-004 (Layer D — routing truth table).** Exercise and assert exactly seven final cases:
  coherent claim earned, modifier withheld, G0 failure, G4 undefined, compression, survives frozen
  stress controls and mixed/undetectable. Controlled gate ingredients establish routing only and
  never establish upstream numerical execution.
- **NR-SCP-005 (Layer E — hard G0 barrier).** For an exact first crossing at `t=8`, require zero
  calls to beta, regression, residualisation, shuffle and other controls, local-null, matching and
  capacity computations. No shortened window or recovery path is permitted.
- **NR-SCP-006 (Layer F — four-mode layered scheduling).** Run the layered workflow under genuinely
  distinct forward/reverse traversal and one/two-worker scheduling paths and require identical keyed
  results in all four modes. This proves scheduling determinism without requiring four repetitions
  of the complete confirmatory-scale fit workload or treating enumeration as execution.
- **NR-SCP-007 (Layer G — three-category scale reporting).** Report separately and exactly:
  enumerated identities; executed production-function invocation counts by function/layer, including
  actual fits and controls; and confirmatory-scale computations not executed. No category may be
  inferred from another and no enumerated identity may be described as an executed computation.
- **NR-SCP-008 (production-bypass mutations).** Require workflow failures when any production
  feature, residualiser, shuffle, matching, capacity, aggregation or Westfall–Young function is
  bypassed or replaced. Applicable mutants include fixed result, wrong width, wrong membership,
  wrong label order and omitted call. A spy proves invocation; a mutation proves that the workflow
  depends on the production output rather than merely counting a callback.
- **NR-SCP-009 (fit-cache identity and equivalence).** Permit fit caching only for byte-identical
  training matrix, target, fold identity, schema identity and provenance identity; bind all five in
  the cache key and reject each single-field difference. Before scientific use, cached and uncached
  predictions must be bit-identical or equal within one predeclared frozen numerical tolerance,
  comparison domain and software environment. No reuse may cross a non-identical identity.
- **NR-SCP-010 (prohibited conformance claims).** Layers A–F cannot establish full-scale runtime
  feasibility, complete 9×6/`B=1000`/capacity-200 synthetic numerical execution, execution of a fit
  represented only by enumeration, scientific propagation by a synthetic adapter, or any scientific
  outcome. TP-E2E-003 remains controlling: component references, production-wired workflow evidence,
  identity enumeration and controlled routing evidence must remain separately labelled.

All production constants remain unchanged: nine configurations by six offsets, five radii, six
outer folds, four slabs, exactly 200 launches per patch, `B=1000` and 200 capacity draws. The eventual
confirmatory run remains responsible for every frozen production computation.

## GeometryReferenceRegistry

This registry materializes AC-23's comparison inputs without creating new scientific thresholds.
Sources are exact seal-commit blobs:

- `PREFLIGHT_GEOMETRY_REPORT_V2.md`, blob `1c2995cc16bb5b8c0b8777550a461d4593966b48`
  (sections §1–§6; nine family/extent cells at extents 18/20/22, six frozen offsets where stated).
- `SIX_OFFSET_AUDIT_REPORT.md`, blob `2470997bf70c16c1ee6af6f13784b4212d56a291`
  (per-patch table and Appendix exact 54-row audit; all nine selected configurations×six offsets).

### Typed comparison roles

| Registry quantity | Units/scope | Value status | Source section/blob | Comparison role |
|---|---|---|---|---|
| common-set count floor | vertices; every selected patch | exact threshold `>=400` | Physical v7 §5, `e3c32a2df760627fd9b009929c24423a51522e9f` | hard geometry preflight threshold |
| PCA slab count floor | vertices; every slab | exact threshold `>=100` | Physical v7 §5, `e3c32a2df760627fd9b009929c24423a51522e9f` | hard geometry preflight threshold |
| singleton ceiling | fraction; each selected patch | exact threshold `>0.05` | Conditional v4.1 §3, `d88b91e519288a68f7bb5740d3b82cdbdef26964`; audit Appendix `2470997bf70c16c1ee6af6f13784b4212d56a291` | local-null availability only; never removes M9/plain/residual/parity/capacity |
| padded ring width | multiples of ell; each padded patch | exact threshold `>=3` | Physical v7 §3a, `e3c32a2df760627fd9b009929c24423a51522e9f` | hard geometry preflight threshold |
| Delta4/Delta6 cell convergence | relative per-cell area/perimeter | exact threshold max `<=1e-6` | Physical v7 §3a, `e3c32a2df760627fd9b009929c24423a51522e9f` | hard geometry preflight threshold |
| r16 and singleton-count records below | vertices; exact configuration×offset | exact discrete integers | audit Appendix, `2470997bf70c16c1ee6af6f13784b4212d56a291` | exact generator/provenance identity check; mismatch stops |
| singleton-fraction display below | fraction; exact configuration×offset | rounded to four decimals | audit Appendix, `2470997bf70c16c1ee6af6f13784b4212d56a291` | provenance display only; recompute threshold decision from exact counts/r16 |
| seven/two local-null membership | configuration identity | frozen exact fact | audit Conclusions, `2470997bf70c16c1ee6af6f13784b4212d56a291` | M_perm,7 availability only; M9 unchanged |
| n/area/diameter/usable-area table below | vertices or ell²/ell; family×extent means | rounded reported means | preflight v2 §2, `1c2995cc16bb5b8c0b8777550a461d4593966b48` | provenance-only side-by-side report; no equality tolerance/gate |
| monotone growth at extents 18→20→22 | family aggregate | reported integer/rounded aggregate | preflight v2 §1, `1c2995cc16bb5b8c0b8777550a461d4593966b48` | provenance-only expectation; cannot select tiers |
| padding recovery table below | cells; family×extent aggregate | exact integers as reported, not per-offset registry | preflight v2 §5, `1c2995cc16bb5b8c0b8777550a461d4593966b48` | provenance-only expectation plus sealed bounded-cell hard check on recomputation |
| matching escalation summary below | patch counts/ranges by configuration | reported range/qualitative frequency | audit per-patch table, `2470997bf70c16c1ee6af6f13784b4212d56a291` | provenance-only expectation; runtime follows deterministic escalation and records actual tier |

### Exact selected-patch registry

Arrays are in frozen offset order `(0.13,0.37)`, `(0.29,0.11)`, `(0.41,0.23)`, `(0.05,0.47)`,
`(0.19,0.31)`, `(0.37,0.09)`. `r16` and singleton counts are exact integers; singleton fractions
are the audit's rounded four-decimal display values and never replace `singleton_count/r16` for the
5% comparison. `local` is the frozen availability role.

| configuration | r16[6] | singleton_count[6] | singleton_fraction[6] | local |
|---|---|---|---|---|
| silver e14 | 668,655,653,653,671,658 | 8,8,7,5,2,2 | .0120,.0122,.0107,.0077,.0030,.0030 | feasible |
| silver e16 | 1120,1120,1120,1102,1120,1120 | 4,4,4,4,4,4 | .0036,.0036,.0036,.0036,.0036,.0036 | feasible |
| silver e18 | 1698,1718,1698,1723,1723,1723 | 3,0,2,3,2,1 | .0018,.0000,.0012,.0017,.0012,.0006 | feasible |
| golden e18 | 581,597,600,590,585,596 | 18,24,14,15,18,25 | .0310,.0402,.0233,.0254,.0308,.0420 | feasible |
| golden e20 | 1025,1013,1012,1020,1024,1027 | 19,16,11,13,10,18 | .0185,.0158,.0109,.0127,.0098,.0175 | feasible |
| golden e22 | 1535,1545,1559,1537,1547,1539 | 18,9,14,12,15,9 | .0117,.0058,.0090,.0078,.0097,.0059 | feasible |
| platinum e16 | 726,727,730,728,725,735 | 65,67,66,66,70,72 | .0895,.0922,.0904,.0907,.0965,.0980 | local-null unavailable; remains M9 |
| platinum e18 | 1170,1168,1171,1165,1167,1170 | 60,61,68,61,65,73 | .0513,.0522,.0581,.0524,.0557,.0624 | local-null unavailable; remains M9 |
| platinum e20 | 1719,1719,1704,1716,1704,1718 | 51,58,61,58,71,65 | .0297,.0337,.0358,.0338,.0417,.0378 | feasible |

The exact local-null membership is silver e14/e16/e18, golden e18/e20/e22 and platinum e20;
platinum e16/e18 are the two expected exclusions from M_perm,7 only.

The audit's matching provenance is: silver e14/e16 all k32; silver e18 mostly k32 with at most four
patches escalating to k64; golden e18/e20 mostly k32 with one k64 escalation each; golden e22 mostly
k32 with rare k64/full escalation; platinum e16/e18/e20 all k32. Because the report does not enumerate
an exact escalation tier for every offset, this is a reported-range expectation, not an equality gate.

### Rounded physical-size/morphology expectations

These values are rounded means from `PREFLIGHT_GEOMETRY_REPORT_V2.md` §2 and are not exact
comparison targets. Units are vertices for n, ell² for hull/usable area, and ell for diameter.

| family/extent | n | hull area | diameter | usable r16 area |
|---|---:|---:|---:|---:|
| silver e18/e20/e22 | 5463/6719/8100 | 4478/5522/6667 | 78.8/87.4/96.1 | 1370/1976/2690 |
| golden e18/e20/e22 | 3999/4913/5920 | 3272/4032/4840 | 95.9/106.5/116.7 | 452/794/1210 |
| platinum e18/e20/e22 | 4604/5660/6806 | 3726/4554/5489 | 88.6/99.9/108.3 | 921/1345/1879 |

The report does not enumerate these rounded physical-size means for silver e14/e16 or platinum e16;
their pre-seal tier selection remains frozen and no equality comparison or inferred value is allowed.

### Padded-cell recovery provenance

`PREFLIGHT_GEOMETRY_REPORT_V2.md` §5 reports core-only invalid/recovered/remain-invalid counts by
family for extents 18/20/22: silver `150/148/162`, golden `79/74/92`, platinum `57/66/62`, with
the same counts recovered and `0/0/0` remaining for each family. These are provenance-only aggregate
expectations because the report does not type them as per-offset values. The clean preflight instead
applies AC-25's exact per-patch correspondence, bounded-cell and convergence requirements. The report's
platinum core-e22 padding used Delta=4 (not 6) due slowness, with reported ring width 10.1 ell; this
is provenance, not permission to weaken Delta/convergence requirements or reselect a tier.

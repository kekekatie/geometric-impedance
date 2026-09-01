# Normative requirements — clean-room Stage 1

Status: specification only; no study dynamics or outcomes have been run or accessed.

## Sources and precedence

The normative sources are the five artifacts named by `SEAL_RECORD.md`, read at seal commit
`4ec0536319b531e8ad04dbfbbd0cd0e19ac57f55`, plus the frozen 48-time companion list. Requirement
IDs are stable: later clarification must append IDs, not renumber existing ones. Where this document
says **BLOCKED**, Stage 2 must not guess; see `AMBIGUITIES_AND_BLOCKERS.md`.

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
- **NR-GEO-011** A cell is infeasible if its r16 common set has fewer than 400 rows, any inner slab
  has fewer than 100 rows, a required physical-size match is unmet, or a patch has more than 5%
  singleton rows for the local null.
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
  build one shared codebook across offsets. Codebook ordering is **BLOCKED** by BLK-003.
- **NR-FEA-006** Drop a physical-extra column only when `max(abs(delta))<1e-12` against an M3
  column on the evaluated set; never drop M3. Multi-match and fold scope are **BLOCKED** by BLK-004.
- **NR-FEA-007** `physical_extra(r)` consists, in order, of Group A annuli then, for each
  `s in S` with `s<=r`, Group B degree moments, Group D coarse psi values, and Group E Voronoi
  moments. Exact cross-group serialization is **BLOCKED** by BLK-005.
- **NR-FEA-008** Group A bin index is `ceil(d/ell-1e-9)`, centre excluded, bins 1..r,
  corresponding to left-open/right-closed annuli; emit r columns.
- **NR-FEA-009** For each permitted s, define `Nb(i,s)={j!=i:||par[j]-par[i]||<=s*ell}`.
- **NR-FEA-010** Group B emits population mean, variance (`ddof=0`), skewness and excess kurtosis
  of neighbour degrees; if empty use `{deg[i]}`.
- **NR-FEA-011** For any moment sample with sigma `<1e-9`, set variance-normalised skewness and
  excess kurtosis to zero; population variance remains zero.
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
- **NR-CV-004** Fix PC1 sign using `PC1[0]>=0`, otherwise `PC1[1]>=0`; the zero/tie case is
  **BLOCKED** by BLK-006.
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
  increments. Degree-decile and RNG identities are **BLOCKED** by BLK-007.
- **NR-CV-013** Position and far-physical controls inherit the inspected sealed baseline definitions:
  position `(x,y,hypot(x,y))`; far block `g(8),g(12), neighbour-degree means at 5 and 9,
  coarse psi_N means at 5 and 9`. Their normative decision role is **BLOCKED** by BLK-008.

## Propagation and endpoint

- **NR-DYN-001** Coherent generator is adjacency `H=A`, with uniform hopping, `hbar=J=1`.
- **NR-DYN-002** Classical generator is column-stochastic `Q=A*D^-1-I`, unit exit rate, and
  `p(t)=exp(Qt)e_v0`; use the same Krylov method and time grid.
- **NR-DYN-003** Select 200 launches per patch, 50 per PCA slab, by sorting on `(PC1 projection,
  lift lexicographic)` and taking evenly spaced indices. The exact index formula is **BLOCKED** by
  BLK-009. If fewer than 200 common rows exist, use all (though planned patches exceed this).
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
  and `R2_fit` is recorded. Handling of nonpositive/nonfinite MSD is **BLOCKED** by BLK-010.
- **NR-DYN-012** Do not cull admitted launches using R2, curvature, beta or any dynamics-derived
  property; every admitted launch must yield beta or fail loudly.
- **NR-DYN-013** Report per-M4-column admitted-versus-excluded mean, SD and standardised mean
  difference; no threshold or gate. SMD convention is **BLOCKED** by BLK-011.
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
- **NR-RNG-006** Use `B=1000` repetitions from address root `SeedSequence(20260829)` and stable keys
  `(family,tier,offset,motif-key,b)`, independent of traversal order and synchronised where pairing
  and max-T require it. Exact stable hash encoding is **BLOCKED** by BLK-012.
- **NR-RNG-007** Capacity uses separate root `SeedSequence(20260830)` with 200 child streams indexed
  0..199, one iid-Gaussian block per child having the parity block dimensionality.
- **NR-RNG-008** Parity is deterministic and has no seed.
- **NR-AGG-001** For any ordinary measure, first take the equal-weight median across nine configs
  within each offset, then the median across six offsets to obtain `M9`.
- **NR-AGG-002** Build `M_perm,7` identically using exactly the seven ordered feasible configs.
- **NR-AGG-003** Define `delta_cap` as the 95th percentile of the 200 complete capacity-draw M9
  values; quantile interpolation is **BLOCKED** by BLK-013.
- **NR-AGG-004** Define `q_ref=(1+count(M_null>=M_obs))/(B+1)` and describe it only as extremeness
  under the constrained algorithmic stress reference, not a significance p-value.
- **NR-AGG-005** For G8 use signed one-sided config medians, raw uncentred null increments,
  Westfall-Young step-down max-T over seven cells, synchronized repetitions, and monotonised
  adjusted extremeness values. Tie/order mechanics are **BLOCKED** by BLK-014.

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

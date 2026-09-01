# Clean-room test plan — independently derived

**Status: RECONCILED SPECIFICATION / NOT IMPLEMENTED / NOT RUN**

Authority precedence: seal `4ec0536319b531e8ad04dbfbbd0cd0e19ac57f55`, ratified Amendment 1
at `d574fde530b9d033a898e03e532bfb30e9835caf`, then these reconciled specifications.

No test in this plan uses study addresses, targets, beta values, scores or outcomes. Synthetic fixtures
must use invented coordinates, graphs, fields and targets. Tests assert both numbers and wiring.

## Identity and registry tests

1. **TP-REG-001 Exact registries.** Assert byte-for-byte ordered equality of five radii, six offsets,
   nine tier-major configurations and seven feasible configurations. Assert platinum-e16/e18 are in
   M9 and absent only from M_perm,7.
2. **TP-REG-002 Axis refusal.** Shuffle config or offset axes while retaining values; aggregation
   must reject mislabeled arrays rather than silently calculate.
3. **TP-REG-003 Companion times.** Assert 48 unique ordered values, all on the 161 grid, endpoints
   2 and 8, and exact equality to `snapped_beta_times.txt`.
4. **TP-REG-004 Seal identity.** Recompute Git blob and SHA-256 identities from the seal object;
   reject CRLF-transformed or otherwise altered normative bytes as seal inputs.

## Synthetic low-level and invariant tests

5. **TP-GEO-001 Hull depth.** Convex square plus interior points: compare analytic signed distances;
   verify translation/rotation invariance and loud failure on degenerate hulls.
6. **TP-GEO-002 Common population.** Use vertices just below, exactly at and above `16*ell`; assert
   the exact inequality and unchanged IDs at all five rungs.
7. **TP-FEA-001 Annuli.** Place neighbors below/at/above integer radii and tau boundaries; verify
   centre exclusion, right-closed bins and no point beyond r.
8. **TP-FEA-002 Moments.** Compare mean, ddof=0 variance, skew and excess kurtosis to hand arithmetic;
   exercise empty neighborhood and sigma below/equal/above `1e-9`.
9. **TP-FEA-003 Physical dimensions/nesting.** Assert 11/22/35/48/61 and exact prefix equality from
   one rung to the next after BLK-005 is resolved.
10. **TP-FEA-004 M4 exact reference.** On a tiny connected graph, calculate shell membership, shell
    means/variances, local least-squares gradient and field-hull depth independently; compare all 11
    ordered columns. Exercise fewer-than-four gradient neighbors.
11. **TP-FEA-005 Raw-then-transform.** Construct a nonlinear field where permuting existing M4 columns
    differs from permuting raw coordinates then recomputing M4; require the latter.
12. **TP-FEA-006 Parity operator identity.** Spy on the shared address operator and prove observed,
    parity and permuted branches invoke the same implementation with different raw fields.
13. **TP-FEA-007 Dedup.** Test exact duplicate, `0.5e-12`, `1e-12`, `1.5e-12`, duplicate of two M3
    columns and duplicates visible only in held-out data; expected behavior awaits BLK-004.
14. **TP-VOR-001 Padding.** Synthetic lattice with known cell areas: compare Delta=4/6, core mapping,
    empty bounded-neighbor fallback and failure below the ring-width requirement.

## Fold and leakage tests for every fitted object

15. **TP-LEAK-001 Outer outcome regressor.** Encode offset ID into held-out targets; instrument fit
    row IDs and prove the held-out offset never enters any fit.
16. **TP-LEAK-002 Inner residualisers.** For each training row, assert residual prediction provenance
    excludes its slab; corrupt an inner-held slab and prove its own fitted model parameters do not move.
17. **TP-LEAK-003 Outer residualiser.** Perturb held-out address values and prove fitted outer
    residualiser parameters remain identical while held-out transformations change.
18. **TP-LEAK-004 Parity scaler.** Give held-out parity fields extreme mean/scale; training scaler
    statistics must remain unchanged and transformed held-out values must reflect training statistics.
19. **TP-LEAK-005 Matching scaler.** Repeat TP-LEAK-004 for local matching features and assert candidate
    distances use only the resolved training-fit scaler.
20. **TP-LEAK-006 PCA/slabs.** Record fit provenance and verify the resolved patch-local/outer policy;
    no target/address value may influence PC1, ties, slabs or launches.
21. **TP-LEAK-007 Motif codebook.** Introduce a motif only in the held-out offset; require the exact
    unknown-category behavior resolved under BLK-003 and prove no silent column-set drift.
22. **TP-LEAK-008 Dedup schema.** Change only held-out geometry; verify training schema cannot be
    selected using it after BLK-004 resolution.
23. **TP-LEAK-009 Capacity and null draws.** Fit-provenance audit must show no target used to construct
    Gaussian blocks, match candidates, costs, escalations or singleton feasibility.

## Randomisation identity and law tests

24. **TP-RNG-001 Stable identity.** Golden vectors for every `(draw,patch,offset,motif)` key after
    BLK-012 resolution; rerun under reversed dictionaries, thread counts and process scheduling.
25. **TP-RNG-002 Separation/pairing.** Assert capacity and address roots never collide; parity consumes
    no RNG; same b is synchronized across engines/configs while distinct patch/motif keys differ.
26. **TP-RNG-003 Assignment law.** Hand-built cost matrix proves additive `distance+U`, self exclusion,
    bijection and deterministic 32->64->full escalation; a deliberate `distance*U` mutant must fail.
27. **TP-RNG-004 Singleton threshold.** Test exactly 5%, just above 5%, fixed singleton populations,
    and unchanged observed/null row identities.
28. **TP-RNG-005 Complete draws.** Delete one offset/config result from a draw; q_ref and max-T must
    reject the entire incomplete draw rather than shrink a denominator.

## Operator-composition and incorrect-wiring tests

29. **TP-WIRE-001 Geometry-to-feature rows.** Permute padded-to-core mapping while preserving shapes;
    Voronoi and parity invariants must catch the wrong join.
30. **TP-WIRE-002 Population-to-fold rows.** Use correct slabs on wrong patch IDs; provenance and
    population hashes must fail.
31. **TP-WIRE-003 Residual composition.** Compare correct inner cross-fitted train residuals plus
    outer-held residuals against mutants using one all-training residualiser or in-sample residuals.
32. **TP-WIRE-004 Paired increments.** Make baseline and augmented scores individually correct but
    swap one fold before subtraction; keyed pairing must fail.
33. **TP-WIRE-005 G4 order.** Fixture where paired-reduction-then-M9 differs from difference-of-medians;
    require the sealed order and undefined-global behavior from one bad denominator.
34. **TP-WIRE-006 M9 order.** Fixture where median-config-then-offset differs from median-offset-then-
    config; require the former for all ordinary, residual, parity and capacity branches.
35. **TP-WIRE-007 Permutation population.** Correct assignment on the wrong offset must fail even when
    shapes and motif counts match.
36. **TP-WIRE-008 Boundary barrier.** A crossing only at t=8 must prevent beta/regression calls;
    a no-crossing fixture must permit them. Spy assertions verify G0 executes first.
37. **TP-WIRE-009 Engine alignment.** Swap coherent/classical launch order in one batch; stable launch
    IDs must catch it before G5.
38. **TP-WIRE-010 Control identity.** Position/far/shuffle feature builders can be numerically correct
    yet attached to the wrong baseline/radius; schema contracts must reject them.
39. **TP-WIRE-011 G1 membership.** Force one coherent and one classical config below 0.90; M9 must
    retain nine cells, coherent claim must downgrade, and G5 must become inconclusive as specified.
40. **TP-WIRE-012 G7 isolation.** Vary parity so Delta_ap crosses delta_cap; no gate or route may change.

## Propagation, reduction and exact-reference agreement

41. **TP-DYN-001 Generators.** Tiny irregular graph: assert H=A, Q columns sum to zero, diagonal -1,
    off-diagonal `A_vw/deg_w`, and stationary distribution proportional to degree.
42. **TP-DYN-002 Exact propagation.** Compare Krylov state/probability at all shared times against
    eigendecomposition/matrix exponential on tiny graphs; coherent max state error <=1e-10.
43. **TP-DYN-003 Conservation.** Exercise exact pass, boundary equality and violations of norm, mass
    and negative-probability tolerances; violations must be flagged and excluded only by explicit route.
44. **TP-DYN-004 Batch/reduced agreement.** For a small graph and 7 launches, compare batches of
    1/3/7 and streaming MSD/strip reductions against a fully materialised exact tensor. Require exact
    launch ordering and tolerance agreement.
45. **TP-DYN-005 Beta hand reference.** Generate positive `MSD=c*t^(2*beta)` on the 48 points and
    recover beta/R2; add a non-power-law curve and verify diagnostics without culling.
46. **TP-DYN-006 Strip crossing.** Test no crossing, first crossing at 0, 7.95 and 8.0, and equality
    to 0.01 for both engines; global earliest must be correct.

## Aggregation, gates and routing truth tables

47. **TP-AGG-001 q_ref.** Hand-count null ties (`>=`), zero exceedances and all exceedances with
    denominator 1001.
48. **TP-AGG-002 Capacity.** After BLK-013/015 resolution, compare delta_cap to a hand-sorted 200-draw
    reference and verify one complete M9 per draw.
49. **TP-AGG-003 Westfall-Young.** Seven-cell, synchronized small reference matrix; hand-calculate
    signed raw max-T steps, ties and monotonic adjustment.
50. **TP-GATE-001 G0–G8 tables.** Exhaustively test equality boundaries: 8, 0.90, 0.05, delta_cap,
    0.70, 0.2 ratio, plus undefined denominators and classical-inconclusive state.
51. **TP-ROUTE-001 Physical routes.** Truth table for infeasible, compression, survives-controls,
    mixed and undefined rho; test rho exactly 0.25 and signs 4/6 versus 5/6.
52. **TP-ROUTE-002 Claim routes.** Coherent conjunction excludes G5; modifier requires classical G1
    and G5; G7/G8 never alter primary claim. Forbidden ontology/significance/irreducibility phrases
    must be rejected by report validation.

## Malformed and negative inputs that fail loudly

53. **TP-NEG-001** Missing/duplicate offset, config, radius, draw, vertex ID, launch or snapped time.
54. **TP-NEG-002** NaN/Inf coordinates, features, costs, state, probability, MSD, beta, predictions or R2.
55. **TP-NEG-003** Asymmetric adjacency, self-edge where forbidden, zero-degree classical column,
    noncanonical motif key or inconsistent lift/edge identity.
56. **TP-NEG-004** Physical block wrong width/order, nonnested rung, changed M3 width, mismatched
    codebook/schema, or dedup removing an M3 column.
57. **TP-NEG-005** Held-out IDs in any fitted-object provenance, train/test population mismatch,
    changed row order without IDs, or different rows in paired baseline/augmented fits.
58. **TP-NEG-006** Assignment without perfect matching after full escalation, non-singleton fixed point,
    duplicate destination or mismatched raw/permuted population.
59. **TP-NEG-007** Attempt to calculate beta after G0 failure, silently shorten time window, cull by
    R2, recompute M9 on surviving configs, or substitute capacity for unavailable parity.

## Complete synthetic end-to-end execution

60. **TP-E2E-001 Nine-by-six miniature.** Invent 54 small labelled graphs with synthetic positive
    power-law dynamics, invented perpendicular fields and targets. Run geometry -> common population ->
    physical/address/parity -> folds -> both propagation engines -> beta -> all regression/control
    branches -> 1000 lightweight deterministic null fixtures and 200 capacity fixtures -> M9/Mperm7 ->
    G0–G8 -> final routing/report. No study generator or data is used.
61. **TP-E2E-002 Route variants.** Parameterise the synthetic fixture to earn the coherent claim,
    withhold only the modifier, fail G0, make G4 undefined, produce compression, produce survives,
    and fall through to mixed. Assert exact membership and claim language each time.
62. **TP-E2E-003 Exact small reference.** Independently calculate a reduced 9x6 fixture using direct
    matrix exponentials, fully materialised tensors, explicit OLS, exhaustive keyed joins and hand
    median/gate code. Compare every intermediate artifact to the batch/reduced production path.

## Test acceptance

Stage 2 conformance requires all applicable tests passing on at least two iteration orders and two
parallelism settings, no expected-failure waiver for a primary gate, and explicit resolution tests
for every blocker. Synthetic test outputs must never be described as scientific outcomes.

## Ratified Amendment 1 falsification tests

These extend, rather than replace, TP-REG/TP-GEO/TP-FEA/TP-LEAK/TP-RNG/TP-WIRE/TP-DYN/TP-AGG/
TP-GATE/TP-ROUTE/TP-NEG/TP-E2E. Golden values are generated in Stage 2B only by a tiny isolated
fixture helper and independently checked by a second direct implementation or external standard
tool; no production or test code is written in Stage 2A.

63. **TP-AMD-001 AC-01 orchestration.** Instrument six synthetic outer folds and four slab folds;
    assert every fold value survives to keyed aggregation. Deliberate old-runner mean/std output,
    non-nested fitting or averaging before M9 must fail schema validation.
64. **TP-AMD-002 AC-02 identities.** Assert exact N/family/extent/offset calls; feed unsorted,
    duplicated and missing lift tuples and reversed/duplicate edges. Require canonical vertex/edge
    tables or loud failure, never positional joining.
65. **TP-AMD-003 AC-03 registry.** Pool invented motifs over six offsets, verify lexicographic fixed
    one-hot order across every outer fold, and require an unseen seventh-offset motif to fail.
66. **TP-AMD-004 AC-04 dedup.** Use pooled six-offset fixtures containing zero, one and multiple M3
    matches at distances below/equal/above `1e-12`; verify one fixed per-config/radius schema, complete
    match records and invariant retention of M3.
67. **TP-AMD-005 AC-05 strict prefix.** Build hand-labelled A/B/D/E columns at all scales; assert
    widths 11/22/35/48/61 and exact schema/value prefix equality. An interleaved-by-group mutant and
    a correct-width wrong-order mutant must fail.
68. **TP-AMD-006 AC-06 PCA.** Compare float64 population covariance/eigenvectors to an analytic
    fixture; test sign orientation by first component above `1e-15`, exact projection/lift ties,
    eigenvalue gaps just below/equal/above the relative tie tolerance and no-orientable-component stop.
69. **TP-AMD-007 AC-07 canonical JSON/hash.** Freeze canonical-JSON byte fixtures for ASCII and
    escapable family/tier validation cases in exact field order. Independently compute golden
    BLAKE2b digest/u0/u1 vectors for `b"GIV-SHUFFLE-v1"`; reject sorted keys, spaces, NaN, wrong
    integer/string types, alternate personalisation and `default_rng`.
70. **TP-AMD-008 AC-07 replay/consumption.** Pin a NumPy version and independently verify PCG64
    replay. Reverse input dictionaries and parallel schedule; stable double-argsort, ascending group
    order and lift-member order must reproduce exactly. Count one permutation call per nonsingleton
    and zero for singleton; assert the stored patch permutation is identical across folds/engines.
71. **TP-AMD-009 AC-08 descriptive controls.** Assert r16 position/far controls execute and report
    for both engines. Perturb their values from extreme low to high and prove no G0–G8 input, route or
    earned claim changes; omitting a report is nevertheless a conformance failure.
72. **TP-AMD-010 AC-09 launches.** For n=100,101 and larger slabs, hand-calculate all 50
    `floor(j*(n-1)/49)` indices; assert endpoints, uniqueness, count and lift-tie ordering. Mutants
    using linspace-round, ceil or denominator 50 must fail.
73. **TP-AMD-011 AC-10 MSD validity.** Put zero, negative, NaN and infinity independently at every
    fit-time position. Require whole config-engine invalidation, no epsilon/culling/window shortening,
    coherent global downgrade versus classical modifier inconclusive, and unchanged launch registry.
74. **TP-AMD-012 AC-11 SMD.** Hand-check pooled population-SD formula, ordinary signed SMD, denominator
    just below/equal/above `1e-12`, equal means -> 0 and unequal means -> signed infinity. Prove no gate
    consumes the result.
75. **TP-AMD-013 AC-12 canonical JSON/hash.** Freeze exact bytes for nested integer motif arrays in
    field order `family,tier,extent,offset_index,motif`; independently calculate BLAKE2b digest/u0/u1
    golden vectors for `b"GIV-ADDRPERM-v1"`. Reject tuple strings, floats, reordered keys, NaN,
    alternate escaping/personalisation and unpinned NumPy.
76. **TP-AMD-014 AC-12 PCG64 stream.** For selected b=0,1,999, independently replay
    `SeedSequence(20260829,spawn_key=(u0,u1,b))`. Assert exact float64 row-major source/candidate cost
    stream under reversed group iteration and concurrency; column-major, per-row generator and extra
    draw mutants must fail. Verify synchronization and key separation across engines/configs/motifs.
77. **TP-AMD-015 AC-13 quantile.** Use 200 hand-sorted values for which NumPy linear differs from
    nearest/lower/higher/midpoint; require float64 `quantile(...,0.95,method="linear")` exactly.
78. **TP-AMD-016 AC-14 step-down.** Create tied observed statistics in all seven fixed cells; verify
    stable descending order, family order tie break, raw signed nulls, each suffix maximum and
    cumulative-maximum adjusted values against a hand table.
79. **TP-AMD-017 AC-15 spawn tree.** Independently generate identity metadata for exactly 200 draw
    children and 54 children from one spawn call per draw. Assert no duplicate state and fail extra,
    repeated, nested-per-fold or differently batched spawning.
80. **TP-AMD-018 AC-15 axis distinction.** Label patch children and prove capacity uses family-major
    configuration order with offset-fast sixes while ordinary study arrays remain sealed tier-major.
    A test that accidentally shares one ordering for both must fail even when shapes match.
81. **TP-AMD-019 AC-15 fields/reuse.** For small synthetic lift-sorted patches, independently replay
    PCG64 float64 C-contiguous `(n,11)` standard normals. Require the exact stored object/hash across
    all six outer folds and both engines; reject address scaling, row reorder or regeneration.
82. **TP-AMD-020 AC-16 scaler.** Inject extreme held-out values and zero/nearly-zero training SDs;
    verify pooled-five population statistics, unchanged fit state, both train/held-out zero mapping
    below `1e-12`, and no held-out leakage.
83. **TP-AMD-021 AC-17 candidates/ties.** Assert self exclusion at every escalation, exact
    `(distance,lift)` order, and loud failure for equal total stochastic assignment costs. Candidate
    reorder and library-default tie mutants must fail.
84. **TP-AMD-022 AC-18 residual topology.** Spy fixture requires exactly 11 scalar frozen HGBRs per
    required fold/application, no scaler/multi-output model, inner out-of-slab predictions and one
    outer held-out application. Duplicate application must fail provenance.
85. **TP-AMD-023 AC-19 R2.** Compare direct float64 SSE/SST to hand arithmetic. Exercise SST
    positive, zero and negative plus nonfinite inputs/predictions; require `Undefined(reason)` rather
    than forced finite, and exact mixed/inconclusive propagation.
86. **TP-AMD-024 AC-20 thresholds.** Parameterize every sealed threshold with predecessor/equality/
    successor float64 values. Assert literal operator, signed margin and nonfinite failure/undefined
    route; forbid hidden epsilons, including d_bound membership.
87. **TP-AMD-025 AC-21 G1.** Exhaustively toggle each of nine coherent and nine classical cells.
    `coherentG1`/`classicalG1` pass only for all-nine true; classical failure with coherent pass keeps
    the coherent result and withholds only the modifier; M9 always retains nine cells.
88. **TP-AMD-026 AC-22 routing.** Feed nine labelled cells through global compression/survives/mixed
    truth tables. Missing, undefined or unfavorable cells must not be dropped/reclassified; per-cell
    values remain descriptive except G8.
89. **TP-AMD-027 AC-23 preflight.** Compare synthetic geometry metrics inside and outside each sealed
    provenance range. Any mismatch stops before a propagation spy can run; feasible-set recomputation
    cannot alter the fixed nine/seven memberships.
90. **TP-AMD-028 AC-24 sigma floor.** At sigma below/equal/above `1e-9`, verify mean remains normal
    and variance, skewness and excess kurtosis are all exactly zero only below the threshold; a mutant
    leaving variance nonzero must fail.
91. **TP-AMD-029 AC-25 correspondence.** Exercise exact lift one-to-one mapping, missing/duplicate
    identities, ring width below/equal/above 3, Qhull failure, unbounded/nonfinite cells and per-cell
    area/perimeter ratios around `1e-6` with denominator `max(abs(D6),1e-15)`.
92. **TP-AMD-030 Amendment-wide composition.** Run a labelled synthetic 9×6 miniature through both
    general tier-major and capacity family-major axes, all keyed RNG provenance, fitted objects,
    endpoint validity, global G1/routing and descriptive controls. Compare to a separate exact
    reference and require every AC-01..AC-25 trace marker before Stage 2B conformance can pass.

# Clean-room test plan — independently derived

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

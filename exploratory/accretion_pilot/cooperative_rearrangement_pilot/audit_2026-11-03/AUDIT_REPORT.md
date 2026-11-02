# Independent bounded audit — 3 November 2026

The pilot's principal bounded negative result survives independent execution and checks: all **12,248 seeded connected regions of one to eight triangular implementation tiles** leave an incompatible exterior under the fixed projection-window convention. The fifteen sampled hexagons each admit only the original decorated filling under the frozen legality rules. No qualifying repair, continuation, or post-repair historical readout exists in this study.

Several interpretations and implementation safeguards need correction. In particular, **41 tiles is not a minimum repair size**; it is one disconnected deletion footprint, with numerically marginal feasibility and changed boundaries. The baseline's advertised true-frontier counts include 30 inner-boundary edges. The standalone replacement validator accepts an empty filling. These findings do not overturn the bounded null after the checks below.

Audit anchor: `fea9554d8626334b09c4744a2f71897a862923cc`. Frozen engine: `84130b97f5044197392e72cd53e0e71f81b043f3`. No historical code or results were edited. All changes and corrected artifacts are in this directory. Paths below are relative to `cooperative_rearrangement_pilot/`, unless explicitly qualified.

## Findings ranked by scientific impact

### 1. The greedy footprint does not bound a minimum connected repair

**Impact: high if interpreted as a minimum or necessary repair size; core bounded null unchanged.**

`src/part3_necessary.py::greedy_engulfment`, its module docstring, and `main`'s `characterisation.note` mix a greedy construction with language about a minimum and what any connected region would need. The code greedily deletes selected vertex contributions. It does not optimize over tile regions, vertex sets, or connected replacements.

Independent reconstruction of the **actual union of incident tile-stars** gives:

| Quantity | Verified value |
|---|---:|
| Selected vertices | 11 |
| Union of triangular tiles | 41 |
| Edge-connected components of this union | 10 |
| Actual vertices disappearing from the exterior | 12 |
| Collateral vertex | `(0.567541, -0.086105)` |
| Maximum separation of selected vertices | 12.4757486811 edge units |
| Maximum separation of all footprint vertices | 14.0494445711 edge units |
| Saved outer-boundary edges lost by deletion | 8 |
| Saved inner-boundary edges lost by deletion | 4 |
| Exterior signed margin | numerically zero |

The unchanged exterior after deleting these actual 41 tiles is numerically feasible and lower-dimensional. This confirms a sufficient **deletion** example, including collateral removal; it does not establish a replacement. The result is fragile: tightening or loosening all right-hand sides by `1e-8` changes the numerical classification to infeasible or positive-area, respectively. It is not independently symbolically certified.

Safe description: one heuristic, disconnected, 41-tile deletion footprint with numerical boundary feasibility. It supplies a numerical upper bound of 41 on an **unrestricted tile-deletion feasibility problem** if the boundary-feasible verdict is accepted. It is neither a lower bound nor an upper bound on the minimum legal connected boundary-preserving **replacement** size. The selected-vertex span is not a minimum necessary span. See `results/independent.json` and `results/supplement.json`.

### 2. The exclusion covers the seeded family, not every band region

**Impact: scope correction; all counts and verdicts survive.**

`src/coop_common.py::connected_regions` covers exactly the connected nonempty subsets of at most eight tiles that contain at least one of **21 seed tiles**. Seeds are tiles incident to endpoints of the two saved dead edges or to either of the two saved witness vertices (`src/part3_necessary.py::load_band`, `seeds_from`). The third owner-triangle vertex at a dead edge is not independently added as a dead-site seed. Witnesses are selected witnesses, not all possible witnesses.

Adjacency means sharing both keyed endpoints of a full triangle edge. The implementation deduplicates frozensets and performs breadth-first expansion. Independent pairwise vertex-intersection adjacency and an include/exclude frontier DFS produce the identical complete family. Both enumerators also agree with brute-force subset connectivity on **3,297 graph/seed cases**, covering all simple graphs through five vertices with three seed configurations (including repeated configurations where they coincide), up to size four.

| Region size | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Count | 21 | 37 | 84 | 200 | 499 | 1,230 | 2,978 | 7,199 |

There are no duplicates or out-of-family regions. All 12,248 are rejected. The actual cap is 50,000, so it does not bind. No runtime cutoff is implemented in this enumeration. The frozen protocol instead lists 200,000; the deviations document calls 50,000 frozen. This inconsistency has no effect here. The order is size-first but **not the promised lexicographic order within size**. No candidate was permitted, so that ordering deviation affects neither selection nor the conclusion here.

The README and some result prose omit the seeded restriction. They must not be read as an exhaustive whole-band size-eight theorem. This audit did not enumerate unseeded regions or larger regions.

### 3. Exterior infeasibility is independently supported, including disconnected exteriors

**Impact: decisive argument verified, conditional on the stated fixed coordinate/layer model.**

`src/coop_common.py::BandConstraints` correctly retains a vertex whenever any unchanged tile supplies it. Its descending contribution lists include formerly nonbinding contributors; removal can reveal the next supplier. For every region, the audit constructs the vertex set directly from the remaining tiles and aggregates all their constraints. Engulfed vertex sets agree exactly. Independently lifting the original band with a different traversal and nearest physical edge-direction selection gives the same integer lift after one common gauge translation, with **209 vertices and no conflicts**. The audit uses the exported window data, not the imported window arrays, for its independent coefficients. Maximum disagreement with the historical aggregation is `1.3323e-15`.

The independent coefficients produce five distinct aggregate systems; the original arithmetic produces twelve because of last-bit distinctions. Each independent system is checked using **unaggregated surviving-vertex rows**, a box-free signed-margin LP, and tighter `1e-9` HiGHS primal/dual tolerances. All margins are approximately `-0.081559480312316`. Every original aggregate system also agrees under box 50, box `1e6`, box-free feasibility, and right-hand-side perturbations through `±1e-6`. This is numerical evidence, not an exact certificate.

There are **6,197 tile-edge-disconnected exteriors**: component counts are 6,051 with one, 5,246 with two, 898 with three, and 53 with four components. Tile-edge connectivity is not the same as lift connectivity: the unit-leg vertex graph is connected for 12,140 exteriors and has two components for 108.

The fixed-lift convention matters. `perp_map.lift` starts each disconnected component at zero, so calling `Sl.constraints` on a disconnected remainder without alignment would not independently reconstruct the same exterior. The audit instead reconstructs the full current-state lift and restricts it to surviving vertices, then independently checks every surviving contribution.

Why a lawful replacement in the stated class must keep those relative lifts: in the exact five-direction module, physical displacement is proportional to `sum(k_j*zeta**j)`. The only integer relation among these five directions is a multiple of `(1,1,1,1,1)`, since the fifth cyclotomic polynomial is `1+x+x²+x³+x⁴`. This relation also has zero perpendicular projection, but changes the integer layer sum by five. The fixed rank map admits only four consecutive layers `[-1,0,1,2]`, so no nonzero such shift preserves the permitted layers. Thus fixed physical coordinates and this common four-layer convention fix each exterior vertex's perpendicular address and admissible layer, even across disconnected components. A common change of origin translates the whole gauge; arbitrary independent component origins or layer reassignment are not the same problem. Replacements must use the frozen edge directions/templates and retain the same footprint/interface; allowing floating component gauges would invalidate this necessary-condition application.

This reasoning concerns the exact template model. The recorded coordinates and LPs remain floating-point computations; it is not an exact arithmetic certification of the saved numbers.

### 4. Completed-patch validator is incomplete as a standalone interface; sampled results survive hardening

**Impact: real validator defect; no changed outcome on the fifteen recorded regions.**

`src/coop_common.py::completed_replacement_legal` ignores `region_tiles`, checks only vertices touched by the filling, and does not itself verify footprint coverage or frozen-template membership. In particular, **an empty filling returns true**. Its overlap helper uses the frozen point-containment heuristic rather than a general intersection-area check. Identity and one perturbed-filling control alone do not establish a complete validator.

The historical search provides additional guarantees outside the validator: `jam_repair_pilot/src/hexflip.py::enumerate_hexagon_fillings` generates template placements along open edges, keeps vertices within the hexagon, and terminates on area agreement. Therefore the standalone counterexample does not by itself show a bad recorded filling was accepted.

The audit's separate `audit_tools.py::completed_replacement_legal` checks template congruence, boundary edges, total area, coverage inside the original triangle union, pairwise intersection area, exterior overlap, and all old/new affected vertex stars using the assembled frozen `Patch.vertex_ok`. It uses the full exterior rather than a distance-truncated exterior.

`verify_hex.py::independent_fillings` independently searches geometric coverings with polygon clipping and overlap area, no node/solution/depth caps, then enumerates decorations using template congruence. It shares the frozen template-placement primitive (not a second implementation of the template atlas). This is bounded verification of the same fifteen regions, not new repair discovery. It recovers **two geometric dissections and 128 decorated fillings per hexagon**, exactly the historical candidate sets. Stronger full-exterior validation agrees on all **1,920 fillings**: only each identity is legal. The local historical exterior includes every tile incident to all affected vertices in these sets. All fifteen identity fillings preserve both saved boundaries and the region interface by identical tile keys.

Regression controls reject empty, incomplete, duplicated, shifted-footprint and malformed-template fillings; a crossing-overlap unit control passes. Frozen assembled-star checks are compared at all affected vertices of every candidate. No appropriate nonidentity legal positive control exists among these exact sampled regions under their fixed exteriors; that limitation remains explicit. No relaxed rules or new worlds were introduced to manufacture one.

Historical cap reporting is not generally reliable: the hex search caps its raw solution list but returns deduplicated solutions, and Part 4 infers truncation from the returned count. There is also a hardcoded depth cutoff of eight, not the protocol's `2 × region size`, and no implemented 200,000-node limit. The independent uncapped search reaches at most depth seven and confirms the complete candidate sets for this sample, so these weaknesses did not omit an alternative here. Part 4 uses 256 solutions, whereas the protocol lists 2,000. It reads the permitted list but does not implement its advertised general permitted-region search. Since the actual permitted list is empty, this dormant gap does not change this study.

### 5. Four is the minimum in the abstract 20-row deletion problem

**Impact: reproduced, with precise interpretation.**

`src/part3_necessary.py::min_facet_drop` permits deletion of any of the 20 aggregated `(rank, facet)` rows. Independent exhaustive enumeration finds:

| Rows deleted | Subsets checked | Numerically feasible | Unresolved |
|---|---:|---:|---:|
| 0 | 1 | 0 | 0 |
| 1 | 20 | 0 | 0 |
| 2 | 190 | 0 | 0 |
| 3 | 1,140 | 0 | 0 |
| 4 | 4,845 | 5 | 0 |

The best margin after three deletions is approximately `-0.0237987356`, well away from zero. Therefore four is numerically established as the minimum **whole-row deletion cardinality**, not merely the first success of a greedy procedure. The original routine stops at its first feasible four-row set; the independent audit checks the entire defined cardinality range.

A row represents the maximum of all suppliers for one rank/facet. Deleting it removes that inequality entirely; engulfing a binding vertex usually only weakens it by exposing another supplier. One vertex contributes several rows. Four rows is not four vertices, stars, tiles, hexagons, or legal moves. Under fixed normals/gauge, at least four original aggregate right-hand sides must be weakened or removed to make this system feasible: otherwise dropping just those changed rows would leave a feasible subsystem of cardinality less than four, contradicting the deletion check. There is no direct realizability result for the row-drop solution.

### 6. Baseline true-frontier counts include the inner boundary

**Impact: reporting/scoring defect; reader outcome unchanged.**

`src/part5_score.py::frontier_candidate_counts` calls `Patch.frontier()` on the retained band, which includes pruning-exposed edges. The reported 103 edges / 101 growable are the **combined exposed boundary**, not the true growth frontier.

| Boundary | Edges | Zero candidates | One candidate | Two candidates | Growable |
|---|---:|---:|---:|---:|---:|
| True outer frontier | 73 | 2 | 28 | 43 | 71 |
| Inner boundary | 30 | 0 | 30 | 0 | 30 |
| Combined (historical output) | 103 | 2 | 58 | 43 | 101 |

The corrected scorer uses saved true-frontier identities and checks owners. `results/corrected_part5_score.json` preserves the independently reproduced reader outcome and corrects this count plus the unwarranted generic phrase “the jam gives F=0.” In this specific baseline the frozen reader reconstructs successfully, area is zero, selected option is null, outcome is `empty_incompatible`, and the B tile is absent. This is not a general equivalence between local jamming and global incompatibility, nor a demonstration of memory erasure.

### 7. Numerical shortcut counts do not reproduce exactly; failure propagation has a latent gap

**Impact: reproducibility detail and defensive correctness; decisive verdict unchanged.**

Saved Part 3 counts are 9,130 no-engulfment rejections, 2,724 unchanged-binding rejections, and 394 explicit LP rejections. This environment gives **9,130 / 2,793 / 325**, on both the saved and regenerated input. Only 12 regions change an aggregate coefficient by more than `1e-12`; many exact-equality changes are about `1e-16`. The exported input also differs in two window components by `1.1102e-16` and edge length by `3.4694e-18`. This supports last-bit sensitivity of exact dictionary equality, but the precise source of all 69 classification-path differences is not separately isolated across the historical runtime. No expected numbers were forced by changing the code. All scientific verdict totals agree.

The combined classifier correctly returns unresolved when either principal solver is forced to fail. However `part3_necessary.main`'s no-engulfment/unchanged-binding paths unconditionally label regions infeasible, even if the full-band control were unresolved. `audit_tools.classify_region` fixes this by reusing the actual full verdict; an injected-unresolved regression test passes. In the actual reproduction the full-band infeasibility is established, so this latent defect changes no verdict. Likewise, the original minimum-row routine does not retain unresolved lower-cardinality checks; the audit's explicit exhaustive result has none.

## Current-state sufficiency and supporting history

The search reads the ordered retained tiles, rank map, dead sites and witness locations from `retained_state.json`; window geometry is also exported, although the pilot actually uses the frozen imported `WIN`. The audit verifies those agree within `1.2e-16`. The original band is connected, so a common lift can be reconstructed without deleted interior tiles. The retained ordered serialization supplies the implicit lift origin used by the implementation. Rank, windows, and boundary labels are current-state model metadata; their provenance should remain visible rather than being described as geometry without any metadata.

Exporting those labels originally uses the full replay to distinguish true and pruning-exposed boundaries and identify dead sites. Once exported, Part 3/4 do not need that deleted geometry. Both saved dead sites also have zero candidates recomputed on the retained band. World/stream provenance is present; historical branch choice, fork hypotheses and archived `Sstar` are confined to the evaluator file for scoring. Search modules do not read `evaluator_historical.json`. The frozen code/atlas remains a dependency, so “self-contained input” does not mean a standalone executable with no code dependency.

The exact case is world 7, canonical B = option index 1 = shape 1, stream index 0 = **20262655433**, detected jam step 23. Regeneration of the documented fork cache and export succeeds. A selected replay of this one original continuation verifies full-patch feasibility at step 8, infeasibility after the single tile added at step 9, and the same 417-tile state at steps 22 and jam detection 23. No full 88-continuation programme was run. The 22-fork cache rebuild is documented setup, not continuation research.

## Safe claim and stopping point

For the recorded world-7/B/stream-0 jam, **every seed-containing edge-connected region of at most eight triangular tiles in the enumerated family** has a numerically incompatible unchanged exterior under the specified fixed physical-coordinate, four-layer projection-window convention. Thus no fixed-footprint replacement in that family can restore compatibility in that model. The fifteen tested six-triangle hexagons (three rhombi each) have no nonidentity completed legal filling under the frozen rules. Completed joint legality and reachability by elementary legal moves remain different questions; no path is claimed.

This does not rule out every conceivable continuation, unseeded regions, larger connected regions, changed boundaries, or other models. None of those were investigated. Construction was not resumed and historical readout recovery was not tested. The smallest next step is to review/adopt these scoped reporting and validator corrections; if the zero-margin deletion example matters, certify that existing example before treating it as a robust feasibility bound. The audit stops here.

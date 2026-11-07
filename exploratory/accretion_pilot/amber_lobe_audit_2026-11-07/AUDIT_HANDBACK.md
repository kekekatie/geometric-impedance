# Verification of the amber-lobe experiment

**The bounded continuation/readout claims reproduce, and the separate dormant-scar diagnostic supports the stated distinction.** The builder can continue on these cases with less retained tile material while keeping oriented frontier records and the permanent skip policy. That does not mean it can reconsider a dormant scar using the same reduced tile information, or that every trace of deleted geometry has disappeared.

Target outcome: `804542e41fbdddecb5a3003fe730d91bd7f24dc8`. Audit branch: `audit/amber-lobe-verification-2026-11-07`. The audit adds only `amber_lobe_audit_2026-11-07/`; the original experiment, scar pilot, referee checks and frozen engine are unchanged. No merge, force-push, scheduler change, relaxed tolerance, expanded policy, extra seed, longer horizon or paper draft.

## What reproduced

All **33 fresh trials** completed exactly: **11/11 at each of 1S, 2S and 3S**, through the prescribed step44. Across **231 post-jam steps and 6,771 placements**, ordered live menus, forced/free outcomes, raw ordered placements, frontier identities/order, PRNG transitions and normalized scar sets agree. Full-history placement validation and endpoint complete/partial decorated-star checks pass; no overlap exceeds the unchanged `1e-12` area threshold. The largest floating-point intersection residual is `2.6107588313450947e-16`.

World7's primary final retained tiles reproduce **644 → 485**, or **62.65% → 47.18%** of the 1,028-tile full patch. This removes 159 tiles, 24.69% of the original band. Its post-step23 band is **327 → 313** out of 439 tiles. Other cases' counts and their not-yet-intervened step23 status reproduce as recorded.

| Primary grid, 528 windows in each row | B-only | Ambiguous | Incompatible | A-only |
|---|---:|---:|---:|---:|
| Original / open | 111 | 64 | 353 | 0 |
| Live-only / open | 131 | 67 | 330 | 0 |
| Original / closed | 86 | 94 | 348 | 0 |
| Live-only / closed | 89 | 115 | 324 | 0 |

No requested windows were unavailable, empty selections or reconstruction failures. The frozen positive-area and referee LP conventions were used unchanged. The increase in open B-only count is **not a matched-subset information gain**: deleting tiles changes band centroids and selected components.

`comparison.json` compares 59 regenerated scientific JSON files against the committed results, including every per-window tile selection and numerical constraint. All parsed structure and numerical values agree exactly; no comparison tolerance or corrective rewrite is used. Administrative provenance paths change with the isolated worktree and are reported separately. Exact floating-point reproduction on this environment is not an exact-arithmetic certificate.

## Claim-by-claim verification

| Claim | Verdict and evidence |
|---|---|
| Eleven exact continuations at each radius | Reproduced by fresh spawned runs; every recorded check passes. `regenerated/w*.json`, `comparison.json`. |
| Identical menu order, decisions, placements, frontier, RNG and normalized scars | Reproduced and independently re-compared from new worker-message caches to pinned baseline traces. Initial moved reconnaissance is explicitly normalized, not silently counted as identical timing. |
| Legal continuation and endpoint geometry | Passes full-history validation, complete/partial decorated-star checks and separate convex-clipping overlap checks. Matching-rule validation shares the frozen engine; it is not an independently implemented rule oracle. |
| w7 primary band 644 → 485 | Reproduced, with unchanged full-patch denominator. |
| All four reader tallies, zero A-only | Reproduced, all 528 windows per band/convention; no 1S/3S scan. |
| First primary dormant-scar mismatch at step35 | Reproduced in both w7 streams by the original monitoring harness; separately located for w7-s0 after 120 pinned-edge comparisons through the first mismatch. |
| One deleted tile restores the first query | Independently tested: tile belongs to full history, is absent from the reduced band, and changes its nonempty menu to the full-history empty menu. |
| One-vertex corner summary restores that query | Independently derived from tile coordinates; adding only that record to a diagnostic vertex index restores the empty menu while tiles and edge occupancy remain unchanged. |
| The scheduler does not reconsider pinned edges | Source inspection, original all-dormant control and separate guarded diagnostic step36 agree: 87 candidate calls, zero on pre-existing pinned edges, expected placements. |
| No restoration fed back to scientific construction | Spawn arguments and STEP/STOP channel inspected. Restoration runs only on diagnostic copies; actual 33 trials use collar0 and no summaries. |
| Single-query one-tile minimality | Supported in tile count for this query: zero added context fails and one tile succeeds. Does not establish global minimal state, minimal bits or future sufficiency. |
| Complete erasure / tiles-only memory | Not supported and not needed for the declared result. Boundary metadata, skip labels, static rules and diagnostic telemetry remain. |

## Separate local diagnostic

The first independently located edge is `[(0.628274, -0.079527), (0.640786, -0.062306)]`. At step35, the reduced band permits one decorated candidate and full history permits none. The reported missing tile restores the empty menu. Its corner at **(0.640786, -0.062306)** alone also restores rejection: the diagnostic independently computes its angular record and decoration from the tile, rather than trusting the original summarizer's boolean.

The next-step scheduler guard operates on a diagnostic reconstruction whose true frontier is checked against the worker message. It never re-queries an already pinned edge and reproduces step36 placements. The full-history boundary used to assemble that diagnostic copy is **not** sent to a scientific worker. See `independent_query.json` and `src/independent_query.py`.

## What information is actually retained

| Information | Origin and use | Information about material absent from retained tiles? |
|---|---|---|
| Retained decorated tiles | Prepared initial band, then actual additions and thinning; used by legality/occupancy | No extra deleted-tile collection in this field. At w7/2S/44: 485 tiles. |
| Edge and vertex caches | Rebuilt exclusively from retained tiles after pruning; legality and duplicate/vertex checks | No historical occupancy archive in these caches. Instrumented steps35/44 equal fresh rebuilds exactly; at44: 812 edge entries, 327 vertex entries. |
| Oriented true-boundary p/q/r records | Preserved incrementally across deletion; frontier order and occupied-side orientation | **Yes.** At44: 114 edges, 153 unique coordinates, 20 coordinates outside retained tiles. Every owner-tile reference is None. |
| Permanent scar labels | Zero-candidate reconnaissance before initial thinning, then frozen scheduler | **Yes.** Endpoint identities plus remembered rejection/skip status survive loss of the rejecting context; 12 labels at w7/44. |
| PRNG state and radius | Serialized restart state, then ordinary transitions; tie choices and retention | Historical random-stream state, but not a geometric occupancy archive. Initial states/RNG are checked against the baseline. |
| Initial reconnaissance | External preparation evaluates candidates before deleting context; marks initial dead edges without placement or RNG draw | Retains the result of earlier geometric tests in scar labels. At3S, initial preparation uses the full pre-scar checkpoint to form the wider band. |
| Serialized input | Schema, radius, tiles, oriented boundary, RNG and scars only; rebuilt at cold restart | Boundary/scar information remains; no deleted-tile list or repair summary. All 33 schemas and owner fields checked. The worker deletes its input-state local after rebuild. |
| Previous-step diagnostic locals | Candidate key strings, monitor strings, previous frontier IDs, placement list and RNG snapshot, generated within the worker | Some refer to possible geometry outside retained tiles. At44: 112 of 155 candidate keys and all 96 monitor keys are absent from retained tile keys; this does not mean they were all previously placed tiles. They persist until overwritten and are not consulted to choose the next step. All 35 last-step placements are still retained; the same placement-containment check passes across all 231 scientific steps. |
| Fixed rule/reference globals | Frozen engine generates the atlas/templates from a reference patch; imported modules retain them | Includes 15,970 reference tiles and associated rule/reference structures, not an archive of this trial's deleted tiles. The transitive historical STIFF dictionary has 175 entries and is not used by the constructor path. |
| Full-history evaluator and baseline caches | Parent controller loads them for comparison and legality checks | **Yes, in the evaluator.** Not serialized or sent back. Runtime file-open observation of a separate unchanged-worker replay records no opens after imports; this is not an OS sandbox or a complete heap-erasure proof. |

Deletion-cavity edges exist in the rebuilt local occupancy index but do not become construction frontier: `ActiveSkin.frontier()` consults the separately preserved true-boundary map. The original policy control also reproduces 30 cavity edges excluded from that frontier. A parent sends only STEP/STOP after initial preparation; it does not send choices, witness tiles, corner summaries or legality corrections.

## Defects and limitations, ranked by effect

1. **Conclusion-changing defects: none found in the tested finite claims.** No failed scientific check or output discrepancy required a baseline repair.
2. **Wording risk, material for stronger memory claims:** the tile fraction is not a measurement of the entire Python worker's information footprint. Oriented metadata is already disclosed; this audit additionally inventories transient candidate/monitor strings and fixed reference geometry. Avoid “all deleted-neighbourhood information disappears,” “metadata-free,” or literal process-memory erasure. These observations do not invalidate exact continuation under the declared skip policy.
3. **Reproduction/provenance limits:** this is a new execution using the same frozen implementation and hash-verified prior baseline traces, not a new seed-to44 baseline replay or a second rule implementation. Module-path differences are administrative. The original protocol was committed locally before outcomes; its remote mirror was created later, so the remote timestamp alone is not preregistration evidence. The original local history bundle preserves that distinction.
4. **Numerical and horizon limits:** open means positive-area thresholds; closed means bounded numerical LP feasibility with default tolerances. Exact rerun equality does not remove these qualifications. The eleven labels are correlated; the grid is sparse and ends at44. No indefinite-growth, universal-memory, physical-matter or irreducible-minimum conclusion is verified.

No scientific harness failure required a before/after repair. The audit wrapper changes only output/cache routing and fixed task enumeration. Its preflight HEAD test was generalized from exact HEAD equality to verified ancestry plus unchanged scientific paths so that the published audit commit can itself be reproduced; the original preflight ran at the exact outcome commit. Original source and tolerances were never changed.

## Factual starting point for a manuscript

In eleven recorded correlated B-jam cases, a live-frontier-only retention rule with preserved oriented true-boundary metadata and permanent scar-skip status reproduced the audited full-patch continuation through step44 at each tested radius of 1S, 2S and 3S. At the primary radius2S, world7's final retained band decreased from 644 to 485 tiles, and the fixed 528-window endpoint readout retained zero A-only selections under both specified numerical conventions. Nevertheless, the reduced state first disagreed with full-history legality at a dormant world7 edge at step35; one deleted neighbouring tile, or its single-vertex corner information in a diagnostic copy, restored that query's original rejection. The evidence therefore separates information sufficient for the scheduled continuation from information needed to reconsider that particular skipped scar, without establishing a global memory minimum or a result beyond the tested cases and horizon.

All requested bounded checks were executed. What remains unverified is explicitly outside their reach: a new mathematical rule implementation, seed-to44 baseline regeneration, complete process-memory erasure, all future dormant queries, other policies/cases/horizons and global minimum information. See `README.md` for exact commands, restart procedure and logs.

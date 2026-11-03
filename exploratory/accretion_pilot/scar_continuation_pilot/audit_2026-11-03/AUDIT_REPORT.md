# Independent scar-continuation audit — 3 November 2026

**The recorded finite continuations and original reader decisions reproduce. Several headline interpretations do not.** All eleven runs make actual progress to step 44 with legal additions. Whole-band readers return `empty_incompatible`, while the subsets selected by the original scans select B. These are full-patch construction runs followed by readout of extracted subsets, not archive-free construction.

The strongest corrections are: B selection does not always mathematically exclude A; the reported world-7 increase in readable fraction is confounded by changing the scan centre; cumulative scar labels can miss newly blocked frontier edges; and the original “maximal arc” is only the largest compatible connected subset found in one limited scan. No original reader threshold, matching rule, scheduler policy or historical file was changed.

Anchor: `98cfaa6ff24a805b846bcdffa6af0c6896e21305`; integrated predecessor `d2e075a5ff65a61c04d4f55adf2cf37de6bc8723`; frozen engine/reader `84130b97f5044197392e72cd53e0e71f81b043f3`. File references below are relative to `scar_continuation_pilot/` except where stated.

## 1. Reader selection of B is not always exclusion of the closed A region

**Scientific impact: high; reader outputs survive, stronger geometric interpretation changes.**

`src/arc_tools.py::score_arc` delegates to the frozen reader and adapter. The frozen `skin_reader.read` treats a hypothesis as compatible only if its intersection area exceeds **1e-9**; it selects a unique positive-area hypothesis only when the subset's own area exceeds **1e-12**. This is a positive-area decision rule. `phase4_readout.classify` calls an empty/near-zero subset or one with no positive-area hypothesis intersection `empty_incompatible`.

All 22 original headline selections (eleven cases, two endpoints) reproduce as B. But an independent box-free feasibility LP on the **same closed A-intersection constraints** finds:

| Cases, at both endpoints | A intersection | B intersection |
|---|---|---|
| w5-s0, w21-s0, w21-s1 | numerically a point | positive area |
| w15-s0, w19-s0, w28-s0 | numerically a segment | positive area |
| w7-s0, w7-s1, w19-s1, w28-s1, w29-s1 | numerically infeasible | positive area |

Thus **12 of 22** headline subsets have a numerically feasible zero-area intersection with A. The point witnesses violate normalized constraints by at most `2.23e-16`. The segment family has y-span about `0.0655122989` and x-span at rounding scale. This is numerical evidence about boundary intersections, not symbolic certification. The other ten A intersections have clearly negative signed margins, approximately -0.0238 to -0.0729.

Safe wording: “the frozen positive-area reader selects B.” For the six boundary-intersection cases, “overlaps B but not A” or “A is excluded” is too strong if it means disjoint closed geometric regions. Nonempty birth regions do not repair that logical gap. Both birth areas were checked in the representative controls. See `results/boundary_intersections.json` for witnesses, spans and feasibility statuses, and `results/readout_verification.json` for intersection areas and margins.

## 2. The world-7 32%→50% comparison changes its selection procedure

**Scientific impact: high; no demonstrated increase in a common readable fraction or transport of one trace.**

`src/phase1_arc_readout.py::maximal_compatible_scan` uses 48 half-widths centred opposite the jam notch. `src/phase3_post_readout.py::maximal_compatible` uses 32 half-widths centred opposite the cumulative-scar midpoint centroid at the final state. The centre and grid both change.

A comparison fixed in advance, using only the same two world-7/s0 states, gives:

| Fixed centre direction | Width resolution | Jam: tiles / band fraction | Final: tiles / band fraction |
|---|---:|---:|---:|
| Original jam-notch opposite | 32 | 100 / 31.75% | 136 / 21.12% |
| Original jam-notch opposite | 48 | 100 / 31.75% | 145 / 22.52% |
| Original final-scar opposite | 32 | 182 / 57.78% | 321 / 49.84% |
| Original final-scar opposite | 48 | 182 / 57.78% | 296 / 45.96% |

The original headline compares the first centre at jam with the second centre at final. Holding either direction and resolution fixed gives a **decrease in the fraction**, although absolute selected tile counts can increase. The headline increase therefore cannot be attributed to new B-consistent accretion from these scans alone. This does not prove that every better-defined readable fraction decreases; only these declared comparisons were made.

An endpoint-selected subset can differ in membership, direction and extent from the other endpoint's subset. No selected-subset lineage or B readout at every intermediate step was tested. Withdraw “B stays readable the whole way” and “one trace is carried continuously” as conclusions of this pilot. Whole-band feasibility was checked at intermediate cached checkpoints, but that is a different measurement.

## 3. “Maximal arc” and “each arc is B-consistent” are unsupported

**Scientific impact: high for generality; existence of selected B-reading subsets survives.**

The original scan chooses the greatest tile count with area >1e-9 at one fixed centre. It does not search all connected subsets or even all angular windows. The original saved secondary windows already exceed its headline:

- World 7/s0: headline **100**; the clockwise notch half contains a connected **151-tile** B-selecting subset.
- World 5/s0: headline **90**; the clockwise notch half contains a connected **222-tile** B-selecting subset.

Those component counts and decisions reproduce. For example, world 7's quarter-sector request has 70 tiles in components of 69 and 1; only the 69-tile component is scored. World 5's three-quarter-sector has components of 335 and 1. “Contiguous arc” therefore means an angular centroid selection reduced to its largest full-edge-connected component, not a proven single interval of boundary edges or a topological arc.

Selection itself is label-blind with respect to B: the scan tests only compatibility area and component size. A/B intersections and choice-tile retention are computed for reporting, not used to choose the best window. Width ties retain the first encountered width. Components are enumerated from sorted minimum tile keys; equal-size components select the first. The audit makes this explicit with lexicographically sorted component keys and sorted tile serialization. No favourable hypothesis label is used as a tie-breaker.

### Precommitted static sensitivity

Before new grid outcomes, `SENSITIVITY_PROTOCOL.md` was committed as **`f1b893b964a40f59b705cafc6679cf40e640d97e`**. The main grid has six geometry-defined centres and four widths, identically applied to each of the eleven cases at jam and final: **528 requested windows**. A separately fixed world-7 centre/resolution diagnostic adds 320, for **848 total**. The budget was not enlarged.

| Main grid | B selected | A selected | Ambiguous | Reader `empty_incompatible` | Reconstruction failure |
|---|---:|---:|---:|---:|---:|
| Jam (264 windows) | 49 | 0 | 37 | 178 | 0 |
| Final (264 windows) | 62 | 0 | 27 | 175 | 0 |
| Total | **111** | **0** | **64** | **353** | **0** |

The largest positive-area subset found in this new fixed grid selects B for every case at both endpoints. That supports existence under another bounded selection procedure. It does not make B discrimination universal: 417/528 requested windows do not yield a unique B selection. All B-selecting and ambiguous main-grid subsets exclude the original B tile; 30 reader-incompatible windows include it. Presence of the tile is therefore not itself the reader's rule.

The 353 reader-incompatible outcomes divide further under the independent subset-feasibility LP:

- **265** have clearly negative margin: numerical geometric infeasibility.
- **50** have zero/boundary margin: do not call these mathematically empty solely because the reader area is zero.
- **38** have positive subset margin but no positive-area overlap with either original birth hypothesis.

The latter two categories particularly invalidate a blanket “every arc is individually B-consistent; only the between-arc combination fails” interpretation. No A selections were found, but these are selected, correlated, all-B cases, not a general accuracy estimate for a local memory reader. All requested outcomes, component sizes, fractions, hypothesis areas/margins and selection indices are retained in `results/sensitivity.json`. The 320-window diagnostic yields 127 B, 18 ambiguous, 175 reader-incompatible, zero A and zero failures; these counts are not pooled into an independent-trial statistic.

## 4. Cumulative scar labels are not all currently blocked sites

**Scientific impact: medium/high for localization; finite continuation survives.**

`src/scar_continuation.py::patient_scar` scans the full patch's actual frontier, permanently adds labels for zero-candidate edges, then places a batch. Newly blocked edges created by that batch are not labelled until the next scan. A run stopping at step 44 can therefore finish with unlabelled blocked edges.

The audit checks every cached post-step full-patch frontier, separately counting cumulative labels, labelled edges still current, current zero-candidate edges, labelled-but-extendable edges and disappeared labels. In these recorded runs **no labelled edge disappears or becomes extendable at a checkpoint**. Permanent skipping is nevertheless a policy, not a theorem of persistent obstruction; a regression fixture shows that an extendable pinned edge remains skipped and can produce scheduler-specific `total_arrest`.

At the final checkpoint:

| Cases | Cumulative/current labels | Current blocked edges | Current blocked components | Current blocked span |
|---|---:|---:|---:|---:|
| w5-s0, w21-s0, w21-s1 | 2 | **5** | **2** | **2.6553 rad** |
| w7-s0, w7-s1 | 12 | 12 | 2 | 2.9022 rad |
| w15-s0, w19-s0, w28-s0 | 12 | 12 | 2 | 1.2920 rad |
| w19-s1, w28-s1, w29-s1 | 4 | 4 | 2 | 1.9002 rad |

Connectivity here is **edges connected through a shared endpoint key**, not tile adjacency. Span is the shortest angular cover of edge midpoints about the triangle-vertex-averaged current band centroid: `2*pi - largest circular gap`. The original label-only w5 result is one component and 0.0224 rad; that does not describe its final five blocked sites. Applying the original pi/2 localization threshold to current blocked sites changes that family from localized to not localized. The current blocked set still has at most two components at every checked checkpoint; this finite observation does not establish that a cascade can never happen later.

Corrected figures distinguish already-labelled blocked edges from current blocked edges not yet labelled. No labels were reactivated and no scheduler policy was changed.

## 5. Added-tile figures need a common baseline

`src/scar_continuation.py::main` subtracts `_tiles_at(res, jam_step)`, which is the state **after** the scar-tolerant batch at that step. `src/make_figures.py::figure` subtracts the frozen jam patch, which is the state **before** that batch. Both arithmetic results are reproducible; the caption “after jam” is ambiguous.

| Cases | Frozen jam full tiles | First scar-step additions | Later additions (old table) | Total added from frozen jam |
|---|---:|---:|---:|---:|
| w7-s0, w7-s1 | 417 | 22 | 589 | **611** |
| w5-s0, w21-s0, w21-s1 | 846 | 34 | 79 | **113** |
| w15-s0, w19-s0, w28-s0 | 875 | 22 | 140 | **162** |
| w19-s1, w28-s1, w29-s1 | 1,228 | 34 | 36 | **70** |

For world 7, step 23 starts at 417 tiles, the scar scheduler adds 22 to reach 439, and step 44 has 1,028. Hence `1028-417=611`, while `1028-439=589`. All corrected tables and captions use the frozen-jam baseline and separately display the first batch. No step beyond 44 was run.

## 6. Scheduler semantics, progress and legality verified

`patient_scar` was compared with frozen `speed_of_now.patient`. Both use `Patch.frontier()` order, insertion-ordered deduplication of forced candidates by decorated key, sequential sibling legality rechecks, and `rng.choice(ordered(...))` for the first available free site. The scar version reuses the candidate list obtained earlier in the same unchanged scan; the baseline recomputes it at the free-choice edge. With this pure candidate function and unchanged patch those agree. Marking/skipping scars consumes no randomness.

“Only the halt rule changed” is acceptable shorthand for these recorded pre-jam trajectories, but not the full policy definition: the new routine also permanently removes labelled sites from consideration and defines arrest by **non-pinned** growability. It is not a reactivating scheduler, and its `total_arrest` would not prove that every frontier edge is geometrically unextendable. Its forced branch can syntactically return `ok,0`; no zero-placement step occurred in these runs, and with a deterministic candidate list the first forced candidate starts legal. `reached_44` alone should never substitute for checking progress.

For every case and every step before the original jam, the complete ordered tile list, patient result, and PRNG state before/after the step agree **exactly** with the independently replayed frozen baseline. The pre-state at the first scar-marking step equals the frozen jam state. This was checked directly, not inferred from seed reuse.

All **7,325 scheduled additions** at steps 1–44 pass frozen `Patch.legal` immediately before their actual `add`; the **eleven initial B placements** also pass. The original illegal counter alone is weak evidence—it increments only for an invalid guess and does not itself validate final stars. The audit additionally checks every assembled final decorated vertex star using `Patch.vertex_ok`, covering 6,627 vertices counted across case records, and checks all bounding-box-overlapping final triangle pairs using independent convex intersection-area clipping. No positive-area overlap exceeds `1e-12`; the largest residual intersection area is `2.611e-16`. Final full patches contain all earlier tiles, so this also checks for persistent overlap among all actual additions. No matching/decorated-star rule was relaxed.

All eleven runs make at least one placement on every recorded step and reach 44 without total arrest or zero-progress steps. Whole-band constraints independently reconstructed in the historical gauge have negative box-free margin at every post-scar checkpoint. This supports finite strict-local-legal continuation despite whole-band model incompatibility. It does not imply indefinite growth or a compatible global projection-window tiling.

## 7. Gauge alignment and declared readout inputs verified

`arc_tools.score_arc` calls `jam_repair_pilot/src/phase4_readout.py::build_payload`. The adapter uses the historical fork to derive:

- a physical origin (first qualifying unit-leg endpoint of `Sstar`);
- the four-consecutive-layer rank convention;
- the frozen windows;
- both original birth-hypothesis constraint systems.

The reader payload contains exactly `schema`, selected `tiles`, `edge_length`, `origin`, `rank`, `windows`, `hypotheses`. It does **not** contain archived interior triangles or archived vertex lifts as readout evidence. The evaluator still has the historical fork to construct the declared reference/hypotheses; this is conditional geometric readout, not inference without historical metadata. `B` is used outside the reader for retention bookkeeping and naming the correct index; it is not a hidden input field to `skin_reader.read`.

The frozen reader propagates relative integer lifts from a component root, inverts that root's physical coordinate relative to the supplied origin within its coefficient bound 128, and resolves the all-ones kernel using the four-layer slab. The origin vertex need not be in the subset. That absolute reconstruction—not merely path independence—aligns the sampled subsets to the hypotheses.

All endpoint whole bands are connected and are scored in full; the largest-component reduction does not silently discard whole-band tiles in these cases. The audit makes **1,813 successful absolute-alignment checks**, including repeated requested selections: every reconstructed vertex lift equals the independently propagated full-patch lift after alignment to the historical origin. Eight representative whole/selected states (worlds 5 and 7, jam and final) pass:

1. Reversed tile/edge traversal and a separately executed frozen reader variant with reverse root traversal.
2. Translation of both tile coordinates and origin by `0.125+0.0625i`.
3. Nontrivial lift-gauge change `k'=k+e0`: origin becomes `origin-S*PHYS[0]`, layer keys increase by one, and every hypothesis RHS gains `n·PERP[0]`; windows and rank assignments are otherwise unchanged. Recovered lifts shift by exactly e0 and decisions/areas agree numerically.
4. Swapped hypothesis order: intersection order and selected indices swap consistently.
5. Direct versus isolated `-I -S` reader: raw result dictionaries agree exactly for these payloads.

Several controls omit the reference vertex, including all world-5 states and world-7 final states. Maximum area change across traversal/translation/gauge controls is `1.12e-16`; comparison tolerance is `1e-11`. No threshold or original hypothesis was silently changed. The audit root-order variant is a control only; the historical reader is untouched.

All feasibility checks are numerical over irrational template data. Point/segment assertions remain numerical, not exact certificates. The inherited reader has a finite inverse domain, coordinate tolerances and a clipping box; no sampled control or selection exceeded them. Zero-area reader decisions are not used as proofs of infeasibility.

## 8. Choice-tile fate and case dependence

The B tile is absent from every original headline selected subset. At the jam, it remains elsewhere in the band only in **w15-s0, w19-s0 and w28-s0**, departing at step 41 after their step-39 jam. The other eight cases lost it before scar continuation began: w7 at step 17, w5/w21 at step 29, and w19-s1/w28-s1/w29-s1 at step 30. At final, B is absent from every band but **still present in every full construction archive**. “All depart during continuation” and “B was already absent from every jam band” are both incorrect.

The two w7 streams produce the same full trajectory, as do the two w21 streams. There are **nine distinguishable full trajectories** under the checked translation normalization, not eleven independent trials. Eight distinct exact jam geometries occur; w19-s1 and w29-s1 share the same jam geometry but later diverge in full geometry. Four repeated scalar outcome patterns do not establish only four full trajectories. No exhaustive rotation/reflection equivalence classification or statistical independence claim is made.

The corrected figures explicitly colour archive interior (retained during construction), analysed boundary tiles and selected subsets separately, mark the B tile, and distinguish current blockage from the accumulated labels. A grey interior is not deleted geometry. The historical figures were reproduced separately and not overwritten on the audit branch.

## Reproduction, limits and safe conclusion

Original Phase 2 JSON agrees structurally exactly and after newline normalization; its CSV is byte-identical. Phase 1 JSON differs in 36 numeric leaves by at most `6.662e-15`; Phase 3 JSON differs in two numeric leaves by at most `3.470e-17`. No outcome, selected tile count, scar count, step, or discrete field differs. The original data do not serialize every final tile or every scar-edge identity, so those cannot be claimed byte-identical to unavailable historical arrays. This audit records exact replay hashes, stepwise states in a reusable local cache, and machine-readable scar bookkeeping for future comparison. See `REPRODUCTION.md` for cache, interpreter and harness limitations.

Safely: these recorded **full-patch** scar-tolerant runs progress legally to the finite step-44 horizon; the specified whole-band model remains numerically incompatible; some geometry-selected connected boundary subsets select the original B hypothesis under the frozen **positive-area** rule. Selection matters, A can retain a zero-area intersection, and endpoint readout does not establish a continuously transported trace or a universally reliable reader.

A separate archive-free continuation experiment is a reasonable **next question**, because this audit has verified the full-patch baseline and exposed precisely what was not tested. It is not already established or predicted by these results. It would need its own preregistered retained-state/frontier policy and comparison, without importing deleted interior geometry into growth decisions. None was implemented here. The audit and its bounded static sensitivity checks stop here.

# Implementation conformance report — sealed radius-saturation suite

**Implementation commit:** `17d65f3` (this report is committed as its child on `gpt/workbench`).
**Design seal:** `4ec0536` (reviewed parent `e3d7af3`). **Scope:** implementation + non-scientific
conformance testing only. **The confirmatory study run was NOT performed.**

## Seal verification (Step 1)
- `4ec0536` confirmed present on `origin/gpt/workbench`.
- All five normative artifacts verified **hash-identical** (git-blob SHA-1 **and** SHA-256) to
  `SEAL_RECORD.md`: `PHYSICAL_RADIUS_MANIFEST_DRAFT.md` (v7), `MSD_ENDPOINT_MANIFEST_DRAFT.md`
  (v8.1), `CONDITIONAL_NULL_MANIFEST_DRAFT.md` (v4.1), `DECISION_GATE_CONCORDANCE.md`,
  `snapped_beta_times.txt`.
- **No sealed artifact was edited.** They remain hash-identical after implementation (the
  implementation adds only new files under `gpt_workbench/impl/`).

## Verdict: **CONFORMANT**
All normative requirements exercised are implemented and pass synthetic conformance tests (56/56).
No contradiction or missing decision was found that would require a post-seal amendment. The only
un-wired element is the top-level **confirmatory driver**, deliberately withheld because running it
requires study targets (prohibited) — see "Intentional boundaries" below. If the manifests and this
code ever disagree, the manifests win.

## Requirement → implementation map
| Sealed requirement | Module · function |
|---|---|
| Six frozen offsets | `constants.OFFSETS` |
| Nine family×tier configs; tiers | `constants.CONFIGS_9`, `constants.TIERS` |
| `M₉`=9 (fixed, no drop) vs `M_perm,7`=7 | `constants.FEASIBLE_7`; `aggregation.M9` / `M_perm7` |
| Platinum e16/e18 cannot pass G2 | `constants.PLATINUM_INFEASIBLE`; `matching.cell_permutation_feasible` |
| Common-set admission `d_bound ≥ 16ℓ` | `substrate.common_set_r16`, `median_edge_length` |
| Exact 11-col `_m4_cols` (address & parity fields) | `substrate.m4_cols` (**bit-identical** to baseline) |
| Moment conventions (ddof=0, σ-floor) | `features.moments` |
| M3 (full) + continuous match-family | `features.m3_full`, `features.match_features` |
| `physical_extra(r)` Groups A/B/D/E, dims r+9m(r) | `features.physical_extra` (+ `group_A/B/D/E`) |
| Padded-Voronoi + empty-neighbourhood convention | `features.voronoi_areas`, `features.group_E` |
| `X_r` = [M3, extra]; bit-identical dedup; M3 kept | `features.build_Xr` |
| Held-out increment ΔR²; frozen HGBR | `regression.increment`, `make_regressor`, `gbt_r2` |
| PC1-slab inner CV (sign rule, lex ties, remainder) | `regression.pc1_slabs` |
| Matching law: motif groups, k=32, DW cost, Policy A | `matching.*` (`build_permutation`, `policy_A_k`, `assign`) |
| Stable keyed seeds (no salted hash) | `seeds.*` (blake2b) |
| `q_ref` (constrained-reference tail) | `constants.q_ref` |
| Capacity control, `δ_cap` = 95th pct of 200-draw M₉ | `aggregation.delta_cap` |
| Paired shuffle-kill `R_kill` (undefined→mixed) | `aggregation.R_kill` |
| Westfall–Young step-down over 7 | `aggregation.westfall_young` |
| Coherent `H=A` Krylov; CTMC `Q=A D⁻¹−I` | `engines.coherent_states`, `ctmc_generator`, `classical_states` |
| MSD, strip mass, boundary crossing, β(48 snapped) | `engines.msd_curve`, `strip_mass`, `boundary_crossing_time`, `beta_from_msd` |
| G0–G8; primary vs cross-engine modifier; routing | `gates.*` |

## Frozen-constant enforcement map
Enforced at import by `constants._self_check()` and per-call assertions: 6 offsets; 9 configs;
**FEASIBLE_7 == 7**; `phys_extra_dim(r) ∈ {11,22,35,48,61}`; boundary grid 161 pts / Δt=0.05;
**48 unique** snapped β-times (loaded from the sealed artifact, asserted unique & increasing);
k=32, λ=1.0, Policy A; B=1000; 200 capacity draws. Runtime assertions: `physical_extra` dimension;
`M9` refuses any input not spanning exactly nine configs (no cell-dropping); `M_perm7` requires
exactly seven; `delta_cap` requires 200 draws; `m4_cols` is 11 columns; capacity child index ∈ 0..199.
A machine-readable mirror is `impl/frozen_constants.json` (manifests remain authoritative).

## G0–G8 implementation map
| Gate | Function | Rule enforced |
|---|---|---|
| G0 boundary | `gates.G0` | admissible iff `t_bound* > 8` (strict) |
| G1 quality | `gates.G1` | `R²_fit ≥ 0.90`; fail is descriptive, **never** changes `M₉` |
| G2 permutation stress | `gates.G2` | `q_ref < 0.05` on `M_perm,7` |
| G3 capacity | `gates.G3` | `M₉,address > δ_cap` |
| G4 shuffle-kill | `gates.G4` + `aggregation.R_kill` | `R_kill ≥ 0.70`; any undefined required reduction → global undefined → mixed |
| G5 cross-engine non-reproduction | `gates.G5` | denominator undefined (coherent ≤ δ_cap or ≤0) → mixed; else `classical ≤ 0.2×coherent`; **not** "coherence-specific" |
| G6 residual null | `gates.G6` | `M₉(ΔR²_resid) > δ_cap` (lower-bound) |
| G7 vs parity | `gates.G7` | **descriptive only** — no threshold, no `δ_cap` comparison |
| G8 per-config secondary | `gates.G8` + `aggregation.westfall_young` | WY q̃ over 7 feasible cells |
| **Primary coherent** | `gates.primary_coherent_transport` | `G0 ∧ coherentG1 ∧ G2 ∧ G3 ∧ G4 ∧ G6` (**G5 excluded**) |
| **Cross-engine modifier** | `gates.cross_engine_modifier` | `classicalG1 ∧ G5`; **G5 failure does not erase the coherent result** |

## Tests run and results (synthetic only)
`python -m impl.tests.test_all` → **56 / 56 PASS**. Highlights:
- `m4_cols` **BIT-IDENTICAL** to sealed `transport_run._m4_cols` (maxdiff **0.0**); `hull_depth` matches.
- coherent Krylov vs exact diagonalisation **3.6e-14** (≤ 1e-10 tol); norm/probability conservation.
- β recovered from a synthetic power law to 1e-6; boundary-crossing logic.
- seed replay determinism; distinct keys → distinct streams.
- `physical_extra` exact dims for all rungs; Group-E empty-neighbourhood convention; dedup drops only
  bit-identical extra columns and never M3.
- Policy-A matching is a deterministic derangement/bijection; singleton>5% → infeasible.
- `M9` refuses ≠9 configs (no-drop); `δ_cap` = 95th pct of 200-draw M₉; `R_kill` undefined→None(mixed);
  Westfall–Young monotone.
- gate routing (compression / survives-stress-controls / mixed / infeasible); primary excludes G5;
  G5 failure does not erase primary; PC1 slabs equal-count with remainder to lowest-index slabs.

## Prohibited-data-access confirmation
No study address values, targets, LDOS, β estimates, outcome curves, scores, or family-result curves
were accessed or produced. No confirmatory propagation was run on the nine sealed study
configurations; no exploratory family comparisons; no tuning on observed study behaviour. Every test
fixture is a hand-built array or tiny toy graph with a pre-known answer. A static scan of `impl/` for
outcome-bearing symbols returned only a docstring disclaimer. The one place real geometry generation
is wired (`substrate.generate_geometry`) is production-only, lazy, geometry-only, and is **not**
invoked by the test-suite.

## Intentional boundaries (not deviations)
- **No confirmatory driver.** The end-to-end orchestrator that would run the six-offset LOO across the
  nine study configs to produce increments/β is deliberately **not wired to study data**, because
  executing it is the prohibited scientific run. All of its components are implemented and unit-tested
  on synthetic fixtures; the confirmatory run awaits explicit authorization.
- **Padded-super-patch generation** (Δ≥4, ring≥3ℓ) is a generation-time wiring; `voronoi_areas`
  computes bounded-cell areas on whatever padded set the production path supplies, and `group_E`
  applies the sealed empty-neighbourhood convention. Convergence-tolerance checking is a production
  step, tested here only for the convention logic.

## Ambiguities / free implementation choices (documented, not silent protocol changes)
- **Internal column order within `physical_extra`** (A → B-per-s → D-per-s → E-per-s) is not pinned by
  the manifest. Because the frozen regressor (HGBR) and the sealed statistic (R²) are invariant to
  feature-column order, this choice cannot affect any sealed outcome. Documented here for
  transparency; it is a free engineering choice, **not** a protocol decision.

## Unresolved blockers
**None.** No contradiction or missing decision blocked faithful implementation.

*Not part of the scientific record until reviewed and merged. This authorizes no confirmatory run.*

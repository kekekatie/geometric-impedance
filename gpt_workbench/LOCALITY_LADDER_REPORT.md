# Constrained-permutation locality ladder — reproducibility repair (geometry/feature only)

**Date 2026-08-31. Geometry/feature/combinatorics only — no address values, no targets, no LDOS, no
β, no study dynamics.** `gpt_workbench/locality_ladder.py`; machine-readable `locality_ladder.csv`
(588 rows = 7 feasible configs × 6 offsets × 7 `k` × 2 laws), `locality_final.csv` (336 rows =
7 × 6 × 4 `λ` × 2 policies), `singleton_54.csv` (54 rows). This supersedes the first ladder pass with
Work-GPT/Sol's nine reproducibility repairs applied; **not part of the scientific record until
reviewed.**

## Repairs applied (Sol's list)
1. **Stable seed registry (no salted `hash()`).** Every RNG is addressed by an explicit key tuple
   through `rng(*key)`, seeded by `blake2b(SEED_ROOT | key) → int` with `SEED_ROOT = 20260829`.
   Python's process-salted `hash()` is used **nowhere** — motif keys are the canonical sorted
   `(star-line, sign)` tuple (identical to `transport_run.py`), and every draw is keyed by
   `(family, extent, offset, k, law, ⌊1000·λ⌋, rep, policy, purpose)`. Fully reproducible across
   processes/machines.
2. **Real λ-sweep `{0.25, 0.5, 1.0, 2.0}`**, executed in committed code → `locality_final.csv`.
3. **Replicated, paired unrestricted derangements.** For each repetition `b` the *same* rep index
   drives both the constrained DW matching and an unrestricted within-motif derangement; the locality
   ratio is formed **per rep (paired)** then aggregated — never a single reference draw.
4. **Frozen infeasibility policy** for movable vertices with no perfect assignment at `k=32`. **No
   silent dropping.** **Policy A (frozen; matches conditional-null §3):** deterministic escalation
   `k=32 → 64 → full same-motif group` (a derangement always exists at full for group size ≥ 2).
   **Policy B (reported for contrast):** hold such groups as fixed points. Both computed.
5. **`partner_turnover`** = mean over consecutive rep pairs of the fraction of movable vertices
   assigned a **different partner** between the two repetitions (renamed from the ambiguous
   "dest-change").
6. **Final candidate confirmed with `REPS = 40`** stable-seeded repetitions.
7. **Absolute standardised move distances (median / p95 / max)** reported **alongside** the paired
   ratios (both in standardised-feature units).
8. **Features reconciled exactly to the conditional-null M3 continuous physical family** (§ below).
9. **Aggregation defined explicitly** (§ below) — pooled-vs-patch ambiguity removed.

## Method
On the r16 common set of each permutation-feasible config × offset: exact-motif groups; the
**reconciled continuous physical features** (item 8) standardised (z-score) on that set. For each
`k`, **self forbidden**, each `k` tested **independently** (structural feasibility, rng-free):
does a perfect derangement exist in the k-NN same-motif candidate graph? Diversity/locality then use
`REPS` independent stable-seeded matchings. Two cost laws: **U** = uniform `U(0,1)` on allowed edges;
**DW** = additive `cost = feature_distance + λ·U(0,1)` (`distance × U` rejected — it can make a distant
edge artificially near-free).

**Feature reconciliation (item 8).** The matching operates on the **non-degenerate continuous M3
physical features**, verified against `transport_run.py`:
`[dens = g(2.0), deg, g(1.6), g(2.6), g(4.0), g(6.0), ψ_N, ψ_{N/2}, ψ_{2N}]` (9 features). The
earlier script's `g(2.0)` **is** `dens` (`transport_run.py: dens = gcount(2.0)`), renamed for clarity.
Edge-length moments are excluded (degenerate on unit-rhombus edges — physical manifest §3); the motif
one-hot is excluded (constant within an exact-motif group). No address, LDOS, or dynamics feature enters.

**Aggregation (item 9).** Within a `(patch, rep)`: pool standardised move distances over **all**
movable vertices → median / p95 / max. Across the 40 reps (within a patch): median of each → the CSV
row. **Headline across patches = the nested median** (median over the 6 offsets, then over the 7
configs — the `M_perm,7` construction); a **pooled** figure is reported alongside and labelled.

## Result 1 — uniform vs distance-weighted across the k-ladder (reproducible)
Nested-median over `M_perm,7`. Feasibility is a candidate-graph property, so it is **identical** for
U and DW at every `k`; only the *locality* differs.

| k | movable-feasible (U=DW) | distinct (DW) | **U abs p95** | **DW abs p95** |
|---|---|---|---|---|
| 2 | 0.059 | 0.959 | 1.634 | 1.578 |
| 4 | 0.329 | 1.000 | 1.803 | 1.414 |
| 6 | 0.678 | 1.000 | 2.151 | 1.461 |
| 8 | 0.828 | 1.000 | 2.370 | 1.599 |
| 12 | 0.934 | 1.000 | 2.610 | 1.633 |
| 16 | 0.973 | 1.000 | 3.001 | 1.633 |
| **32** | **1.000** | **1.000** | **3.387** | **1.624** |

Silver's large motif groups force `k=32` for broad bijectivity (silver e18 DW movable-feasible:
k8=0.30, k16=0.73, **k32=0.96**). And the key contrast: as `k` grows the **uniform** law's moves
lengthen monotonically (abs p95 1.63 → **3.39**, approaching the unrestricted 4.81), while the
**distance-weighted** law stays flat and local (abs p95 ≈ **1.6** at every `k`). Same candidate graph,
same feasibility — only the cost law makes the matching local. **No single uniform-`k` law is both
broadly bijective and local.**

## Result 2 — final candidate: DW, k=32, λ-sweep, 40 reps (reproducible)
Nested-median over `M_perm,7`, Policy A (escalation), `REPS=40`:

| λ | movable-feasible | partner-turnover | abs p95 (constr.) | abs p95 (unrestr.) | **paired p95 ratio** | paired median ratio |
|---|---|---|---|---|---|---|
| 0.25 | 1.000 | 0.420 | 1.624 | 4.809 | **0.370** | 0.000 |
| 0.5 | 1.000 | 0.474 | 1.624 | 4.809 | **0.372** | 0.000 |
| **1.0** | **1.000** | **0.541** | **1.624** | **4.809** | **0.375** | 0.000 |
| 2.0 | 1.000 | 0.677 | 1.739 | 4.809 | **0.413** | 0.265 |

**Absolute move distances (λ=1.0, standardised-feature units):** constrained median **0.000**,
p95 **1.624**, max **3.146**; unrestricted median **1.934**, p95 **4.809**, max **6.160**. The
constrained (local) matching moves vertices to a **feature-identical partner at the median** (ratio 0
— a consequence of duplicate integer-count features), and its p95 move is **~⅓** of an unrestricted
shuffle (1.62 vs 4.81). **The p95 ratio (0.375) is the informative locality statistic.** Every
replicate is distinct (diversity 1.000) and ~54% of movable vertices change partner between reps.

**λ robustness:** p95 ratio **0.37–0.41** across the whole sweep — the conclusion does not hinge on λ.

## Infeasibility policy (item 4) — exact, no dropping
Fraction of movable vertices with no perfect assignment at `k=32` (nested-median **0.0000**): the
shortfall is confined to **silver e18 (3.96%)** and **golden e22 (4.88%)**; **max over any patch
10.44%**; all other feasible configs 0%. (Pooled over movable vertices this is ≈ 1.3%, i.e. the
"≈1.4%" flagged in the first pass — now precisely located.) **Policy A** escalates those groups
deterministically to k=64/full → **movable-feasible 1.000 with no silent dropping**. **Policy B**
(hold fixed) gives essentially the same locality (p95 ratio 0.376 vs Policy A's 0.375), so the
outcome is **robust to the policy choice**. Policy A is frozen because it attains full feasibility
without discarding any vertex.

## Conclusion (reproducible; RATIFIED by Work-GPT/Sol 2026-08-31, commit `be929df`)
The final matching law meets the ladder's aim under fully reproducible, stable-seeded computation:
**distance-weighted additive stochastic assignment, candidate graph `k=32`, `cost = feature_distance
+ λ·U(0,1)`, `λ=1.0`, Policy-A escalation, at r=16.** It is broadly bijective (movable-feasible
1.000), genuinely diverse (distinct 1.000; partner-turnover 0.541), and materially local (p95 move
0.375× unrestricted; absolute p95 1.62 vs 4.81), robustly across `λ∈{0.25,0.5,1,2}` and across the
infeasibility policy. It genuinely conditions on the continuous physical descriptors, not motif alone.
**`λ = 1.0` is RATIFIED by Work-GPT/Sol (2026-08-31, commit `be929df`)** — the predeclared
one-standardised-unit candidate in a flat robustness region (p95 ratio 0.370/0.372/0.375/0.413),
chosen over the marginally-smaller `λ=0.25` to avoid after-the-fact result-shopping since the
conclusion is unchanged across the whole sweep; `k=32` is fixed as the smallest broadly-bijective
single k; Policy-A escalation and the 40-rep stable-seeded diagnostic are ratified with it.

*Source: run by the `gpt/workbench` Claude collaborator; geometry/feature/synthetic only; not part
of the scientific record until reviewed.*

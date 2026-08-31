# Constrained-permutation locality ladder (geometry/feature only)

**Date 2026-08-31. Geometry/feature/combinatorics only — no address values, no targets, no
dynamics.** `gpt_workbench/locality_ladder.py`; machine-readable `locality_ladder.csv` (588 rows =
7 feasible configs × 6 offsets × 7 `k` × 2 laws) and `singleton_54.csv` (exact 54 rows). Purpose:
find the smallest matching law that is **broadly bijective, genuinely diverse, and materially more
local than an unrestricted within-motif shuffle** — or, honestly, conclude none exists.

## Method
For each permutation-feasible config × offset, on the r16 common set: exact-motif groups; standardised
continuous physical features (degree, `g(2.0/1.6/2.6/4.0/6.0)`, ψ_{N/2,N,2N}). For each
`k ∈ {2,4,6,8,12,16,32}`, **self forbidden**, each `k` tested **independently (no silent
escalation)**: does a perfect derangement exist (min-cost assignment, forbidden edges = BIG)? Then
`REPS=12` independent matchings measure diversity and source→destination standardised distance,
compared to an unrestricted within-motif derangement. Two cost laws: **U** = uniform `U(0,1)` on
allowed edges; **DW** = additive `cost = feature_distance + λ·U(0,1)`, **λ=1.0** predeclared fixed
(the data-driven median-1NN λ degenerates to 0 because many vertices share identical integer-count
features — so `distance × U` is also rejected: it can make a distant edge artificially near-free).

## Result 1 — uniform-cost law: no single k is both broadly bijective and local
`movable_feasible_frac` (fraction of movable vertices in groups with a perfect assignment at k),
mean over the six offsets:

| config | k=2 | k=4 | k=6 | k=8 | k=12 | k=16 | k=32 |
|---|---|---|---|---|---|---|---|
| silver e16 | 0.03 | 0.11 | 0.34 | 0.55 | 0.72 | 0.75 | **1.00** |
| silver e18 | 0.02 | 0.05 | 0.13 | 0.28 | 0.60 | 0.73 | **0.97** |
| golden e18 | 0.27 | 0.72 | 0.88 | 0.93 | 0.97 | 0.98 | 0.99 |
| platinum e20 | — | — | — | — | — | — | 1.00 |

Silver's large motif groups (max group ~62–96) require **k=32** for broad bijectivity. But the
**uniform** law at k=32 is **not local** — mean source→dest distance ratio to unrestricted:
**median 0.89, p95 0.87** (overall). So k=32 uniform behaves essentially like a motif-only shuffle;
reducing k to gain locality loses bijectivity for silver. **No single uniform-k law meets the aim.**

## Result 2 — distance-weighted law at k=32, λ=1.0: RESOLUTION
Same broad candidate graph (k=32, so bijectivity retained) but distance-biased costs. Per-config
(mean over six offsets), U vs DW at k=32:

| config | law | movable-feasible | distinct/reps | dest-change | ratio median | ratio p95 |
|---|---|---|---|---|---|---|
| silver e16 | U | 1.00 | 1.00 | 0.95 | 0.82 | 0.63 |
| silver e16 | **DW** | 1.00 | 1.00 | 0.63 | **0.00** | **0.32** |
| silver e18 | **DW** | 0.97 | 1.00 | 0.70 | 0.00 | 0.25 |
| golden e18 | **DW** | 0.99 | 1.00 | 0.44 | 0.49 | 0.63 |
| golden e20 | **DW** | 0.99 | 1.00 | 0.51 | 0.26 | 0.43 |
| golden e22 | **DW** | 0.96 | 1.00 | 0.57 | 0.00 | 0.39 |
| platinum e20 | **DW** | 1.00 | 1.00 | 0.45 | 0.34 | 0.36 |
| silver e14 | **DW** | 1.00 | 1.00 | 0.54 | 0.00 | 0.38 |

**DW@k=32 overall:** movable-feasible **0.986**, distinct **1.000**, dest-change **0.546**, distance
ratio **median 0.155, p95 0.396**. **U@k=32 overall:** movable-feasible 0.986, distinct 1.000,
dest-change 0.898, ratio **median 0.892, p95 0.874**.

**Interpretation.** The distance-weighted law is **broadly bijective** (0.986; k=32 keeps silver's
large groups matchable), **genuinely diverse** (every replicate distinct; ~55% of movable vertices
move to a different destination each repetition), and **materially more local** — the 95th-percentile
source→destination feature distance is **~40% of an unrestricted shuffle**, and the median move is to
a **feature-identical** partner (ratio ≈ 0; hence the many 0.00 medians — a consequence of duplicate
integer-count features, so the p95 is the informative locality statistic). A λ-sweep {0.25, 0.5, 1.0,
2.0} at k=32 gives p95 ratios 0.32–0.42 — robust to λ.

## Conclusion (matching law justified)
A final matching law **does** meet the aim: **distance-weighted additive stochastic assignment,
candidate graph `k=32`, `cost = feature_distance + λ·U(0,1)`, `λ=1.0`, at r=16.** It genuinely
conditions on the continuous physical descriptors (not motif alone). It is proposed as the final
law (conditional-null §3); **`λ` is offered for crew ratification** (sweep shown), not silently
frozen. The k=32-only "motif-only" locality blocker is thereby **resolved**.

*Source: run by the `gpt/workbench` Claude collaborator; geometry/feature/synthetic only; not part
of the scientific record until reviewed.*

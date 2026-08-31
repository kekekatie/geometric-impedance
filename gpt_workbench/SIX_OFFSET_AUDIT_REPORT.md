# Six-offset singleton + matching-feasibility audit (geometry/feature only)

**Date 2026-08-31. Geometry-only feasibility record — no address values, no targets, no dynamics.**
`gpt_workbench/singleton_audit_v2.py`. Nine configs × all six frozen offsets, per patch. Preserves
the matched tiers, the 5% singleton ceiling, the r16 common-set vertex population, and the
deterministic `k`-escalation (32→64→full). No threshold change, no re-tiering.

## Per-patch results (singleton fraction; matching by escalation tier)

| config | offset | r16 | singleton % | k=32 / 64 / full / INF | verdict |
|---|---|---|---|---|---|
| silver e14 | (.13,.37)(.29,.11)(.41,.23)(.05,.47)(.19,.31)(.37,.09) | 653–671 | 0.30–1.22 | all k32 | FEAS ×6 |
| silver e16 | all six | 1102–1120 | 0.36 | all k32 | FEAS ×6 |
| silver e18 | all six | 1698–1723 | 0.00–0.18 | mostly k32, ≤4 to k64 | FEAS ×6 |
| golden e18 | all six | 581–600 | 2.33–4.19 | mostly k32, 1 to k64 | FEAS ×6 |
| golden e20 | all six | 1012–1027 | 0.98–1.85 | mostly k32, 1 to k64 | FEAS ×6 |
| golden e22 | all six | 1535–1559 | 0.58–1.17 | mostly k32, rare 64/full | FEAS ×6 |
| **platinum e16** | all six | 725–735 | **8.95–9.80** | all k32 | **INFEAS ×6** |
| **platinum e18** | all six | 1165–1171 | **5.13–6.24** | all k32 | **INFEAS ×6** |
| platinum e20 | all six | 1704–1719 | 2.97–4.17 | all k32 | FEAS ×6 |

(Exact per-offset numbers are in the run log; ranges above are min–max over the six offsets. Every
patch's verdict is unanimous across its six offsets — no borderline patch flips between offsets.)

## Conclusions
- **Feasible set for the local permutation null = 7 configs:** silver e14/e16/e18, golden
  e18/e20/e22, platinum e20. → the local-permutation reference statistic is **`M_perm,7`**.
- **Platinum e16 and e18 are permutation-null-infeasible on all six offsets** (consistently >5%
  singletons — 12-fold has 2–5× more motif types, hence more one-of-a-kind vertices). Their plain
  increment, residual-orthogonal null, parity and capacity (the `M₉` family) still apply; they are
  simply never described as surviving the *local permutation* null.
- **Matching bijection exists everywhere** at `k=32` primary; escalation to `k=64` is rare and to
  the full group is exceptional (golden e22). `k` is fixed by geometry, outcome-blind.

## Randomisation-diversity of the stochastic assignment law (40 reps)
| patch | distinct assignments | vtx dest-change between reps | src→dest std dist (constrained) | (unrestricted within-motif) |
|---|---|---|---|---|
| golden e18 | 40 / 40 | 80.3% | median 1.398, p95 3.391, max 5.168 | median 1.387, p95 3.396, max 4.739 |
| platinum e20 | 40 / 40 | 85.0% | median 1.795, p95 4.633, max 6.079 | median 1.886, p95 4.787, max 6.148 |

**Diversity: excellent** — the random-cost law yields 40/40 distinct matchings (jitter-degeneracy
fixed). **Locality: NOT achieved at k=32** — constrained ≈ unrestricted source→destination
distance, so at these group sizes k=32 conditions essentially on motif only, not tightly on the
continuous descriptors. **Flagged as a blocker** (conditional-null manifest §9): reduce `k` (≈4–8),
adopt distance-weighted random costs, or rename the null *motif-conditional*. Crew decision.

*Source: run by the `gpt/workbench` Claude collaborator; geometry/feature/synthetic only; not part
of the scientific record until reviewed.*

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

## Appendix — exact 54-row singleton audit (from committed `singleton_54.csv`)

| family | extent | offset | r16 | singletons | singleton_frac | groups≥2 |
|---|---|---|---|---|---|---|
| silver | 14 | (0.13,0.37) | 668 | 8 | 0.0120 | 33 |
| silver | 14 | (0.29,0.11) | 655 | 8 | 0.0122 | 33 |
| silver | 14 | (0.41,0.23) | 653 | 7 | 0.0107 | 33 |
| silver | 14 | (0.05,0.47) | 653 | 5 | 0.0077 | 34 |
| silver | 14 | (0.19,0.31) | 671 | 2 | 0.0030 | 36 |
| silver | 14 | (0.37,0.09) | 658 | 2 | 0.0030 | 36 |
| silver | 16 | (0.13,0.37) | 1120 | 4 | 0.0036 | 37 |
| silver | 16 | (0.29,0.11) | 1120 | 4 | 0.0036 | 37 |
| silver | 16 | (0.41,0.23) | 1120 | 4 | 0.0036 | 37 |
| silver | 16 | (0.05,0.47) | 1102 | 4 | 0.0036 | 37 |
| silver | 16 | (0.19,0.31) | 1120 | 4 | 0.0036 | 37 |
| silver | 16 | (0.37,0.09) | 1120 | 4 | 0.0036 | 37 |
| silver | 18 | (0.13,0.37) | 1698 | 3 | 0.0018 | 38 |
| silver | 18 | (0.29,0.11) | 1718 | 0 | 0.0000 | 41 |
| silver | 18 | (0.41,0.23) | 1698 | 2 | 0.0012 | 39 |
| silver | 18 | (0.05,0.47) | 1723 | 3 | 0.0017 | 38 |
| silver | 18 | (0.19,0.31) | 1723 | 2 | 0.0012 | 39 |
| silver | 18 | (0.37,0.09) | 1723 | 1 | 0.0006 | 40 |
| golden | 18 | (0.13,0.37) | 581 | 18 | 0.0310 | 82 |
| golden | 18 | (0.29,0.11) | 597 | 24 | 0.0402 | 81 |
| golden | 18 | (0.41,0.23) | 600 | 14 | 0.0233 | 81 |
| golden | 18 | (0.05,0.47) | 590 | 15 | 0.0254 | 85 |
| golden | 18 | (0.19,0.31) | 585 | 18 | 0.0308 | 81 |
| golden | 18 | (0.37,0.09) | 596 | 25 | 0.0420 | 79 |
| golden | 20 | (0.13,0.37) | 1025 | 19 | 0.0185 | 90 |
| golden | 20 | (0.29,0.11) | 1013 | 16 | 0.0158 | 93 |
| golden | 20 | (0.41,0.23) | 1012 | 11 | 0.0109 | 93 |
| golden | 20 | (0.05,0.47) | 1020 | 13 | 0.0127 | 95 |
| golden | 20 | (0.19,0.31) | 1024 | 10 | 0.0098 | 93 |
| golden | 20 | (0.37,0.09) | 1027 | 18 | 0.0175 | 90 |
| golden | 22 | (0.13,0.37) | 1535 | 18 | 0.0117 | 98 |
| golden | 22 | (0.29,0.11) | 1545 | 9 | 0.0058 | 104 |
| golden | 22 | (0.41,0.23) | 1559 | 14 | 0.0090 | 97 |
| golden | 22 | (0.05,0.47) | 1537 | 12 | 0.0078 | 101 |
| golden | 22 | (0.19,0.31) | 1547 | 15 | 0.0097 | 96 |
| golden | 22 | (0.37,0.09) | 1539 | 9 | 0.0059 | 103 |
| platinum | 16 | (0.13,0.37) | 726 | 65 | 0.0895 ⚠️ | 126 |
| platinum | 16 | (0.29,0.11) | 727 | 67 | 0.0922 ⚠️ | 123 |
| platinum | 16 | (0.41,0.23) | 730 | 66 | 0.0904 ⚠️ | 125 |
| platinum | 16 | (0.05,0.47) | 728 | 66 | 0.0907 ⚠️ | 124 |
| platinum | 16 | (0.19,0.31) | 725 | 70 | 0.0965 ⚠️ | 122 |
| platinum | 16 | (0.37,0.09) | 735 | 72 | 0.0980 ⚠️ | 126 |
| platinum | 18 | (0.13,0.37) | 1170 | 60 | 0.0513 ⚠️ | 150 |
| platinum | 18 | (0.29,0.11) | 1168 | 61 | 0.0522 ⚠️ | 148 |
| platinum | 18 | (0.41,0.23) | 1171 | 68 | 0.0581 ⚠️ | 146 |
| platinum | 18 | (0.05,0.47) | 1165 | 61 | 0.0524 ⚠️ | 151 |
| platinum | 18 | (0.19,0.31) | 1167 | 65 | 0.0557 ⚠️ | 147 |
| platinum | 18 | (0.37,0.09) | 1170 | 73 | 0.0624 ⚠️ | 148 |
| platinum | 20 | (0.13,0.37) | 1719 | 51 | 0.0297 | 178 |
| platinum | 20 | (0.29,0.11) | 1719 | 58 | 0.0337 | 169 |
| platinum | 20 | (0.41,0.23) | 1704 | 61 | 0.0358 | 179 |
| platinum | 20 | (0.05,0.47) | 1716 | 58 | 0.0338 | 167 |
| platinum | 20 | (0.19,0.31) | 1704 | 71 | 0.0417 | 170 |
| platinum | 20 | (0.37,0.09) | 1718 | 65 | 0.0378 | 173 |

⚠️ = exceeds the 5% ceiling (platinum e16 & e18, all six offsets) → local permutation null infeasible for that patch. Machine-readable source: `gpt_workbench/singleton_54.csv`.

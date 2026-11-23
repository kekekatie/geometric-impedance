# Resolution of the strict baseline-reproduction gate

The frozen protocol required matching the stored unrounded gains before interpretation. All original-site reused credit totals and binary-float scores match their sealed JSON exactly. Two full role-reversal replays completed but failed **literal binary-float equality** in the last printed digits:

| Site / gain | Sealed | Replayed | Difference (pp) |
|---|---:|---:|---:|
| AB_bal, keep A only | 0.0824274520392021 | 0.082427452039191 | −1.1102230246251565e−14 |
| Penrose_ear, full archive | 0.09911765096420888 | 0.09911765096423109 | +2.220446049250313e−14 |
| Penrose_ear, keep A only | 0.09481139521946291 | 0.09481139521948512 | +2.220446049250313e−14 |

All other compared gains match literally. These tiny differences were **not** accepted by rounding the results to eight or five decimal places. Instead, `baseline_precision.py` verifies the exact score grid implied by the experiment:

* Mathematical ordinary-fault odds are 1/999; per-history credit is 0, 1/2 or 1.
* Multiplying weights by 999² makes all weighted doubled-credit numerators integers.
* The weighted history denominator is `8×999² + 2480×999 + 383160 = 10,844,688`.
* Thus every possible gain lies on a grid of **50/10,844,688 = 0.000004610552189237717 pp**.

For each sealed baseline, its unique nearest grid point equals the exact integer numerator reconstructed from the replay. Both the sealed float and replay float lie within four absolute accuracy ulps (8.89e−14 pp) of that rational score, a bound more than a million times smaller than one grid step. The observed last-bit differences therefore encode **the same exact weighted truth-credit gain**, not a different score. This establishes aggregate score reproduction; it does not assert unrecorded history-by-history equality to Neon's run.

`baseline_precision` in each affected site JSON records the sealed/replayed floats, raw difference, exact rational gain and integer numerator. No scientific intervention, fault weights, tie rule, geometry or decoder changed. The numerical acceptance test was refined after the initial literal-equality failure; the immutable pre-score protocol is retained.

The complete CSVs were independently re-aggregated and their original stream hashes verified. Recovery then repeated the 192 original full-scan new-arm comparisons per site (zero mismatches, maximum posterior difference zero), and replayed all eight variants of every 251st configuration: 965 baseline-arm/configuration comparisons and 193 joint-arm/configuration comparisons per recovered site, all exact. No validation count was inferred from the failed process. The extra recovery checks are explicitly marked, and future full replays use the resolved score-grid gate directly.

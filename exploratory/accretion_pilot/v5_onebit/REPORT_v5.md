# Report v5 — one bit per added diagonal

*Plain-language write-up, written after the run. Register: speculative
exploration; not a confirmatory study, not cosmology. Bounded, snapshot-only
follow-up to v4. Rules fixed in advance in [`DESIGN_NOTE_v5.md`](DESIGN_NOTE_v5.md).
We reused v4's saved snapshots and changed only the reader. 200 seed pairs, v4
checkpoints. Reproduce: `python accretion_pilot_v5.py`. Separates observations,
algebraic identities, and mechanistic hypotheses.*

## Question

Can a **single bit per added diagonal** — whether it has accumulated **at least
four traversals** since activation — retain the late A/B history distinction?

## The bit (corrected threshold)

`b(e) = 1 if w_e ≥ 5.5`. Verified in exact arithmetic: since `6 − wₙ = 5/2ⁿ`, an
added edge first reaches `w ≥ 5.5` at **n = 4** (`w₃ = 5.375 < 5.5 ≤ 5.6875 = w₄`),
and `round(w) = 6 ⇔ w ≥ 5.5`. So the bit means **"four-or-more traversals since
activation"** / **"rounds to 6"** — never "finished saturating"; exact `w == 6` is
only float rounding.

Readers on present added diagonals only, with the coordinate sign `s(e)`:
`P_D = Σ s(e)` (presence), `S_high = Σ s(e)·b(e)` (the one-bit reader, primary,
A-positive), `S_low = Σ s(e)(1−b(e))`, complement `−S_low`. **Identity
`S_high + S_low = P_D` holds on every snapshot** (checked). Missing diagonals are a
distinct state (they enter no sum); counts retained.

**Gates:** exact-arithmetic threshold fixture PASS; snapshot schema PASS; v4's
added-edge readers `D0`, `D1` reproduced from the snapshots (max |ΔAUC| < 5e-4).
No trajectories were rerun.

## Answer — yes, the single bit retains the late distinction

Growing, one-bit `S_high` AUC (seed-pair bootstrap 95% CI):

| checkpoint | one-bit `S_high` | whole-number added `D1` | exact added `D0` | presence `P_D` |
|---|---|---|---|---|
| 400 | 0.796 [0.754, 0.840] | 0.829 | 0.831 | 0.834 |
| 2000 | 0.731 [0.682, 0.779] | 0.728 | 0.728 | 0.673 |
| 10000 | 0.619 [0.568, 0.669] | 0.616 | 0.641 | 0.497 |

The one bit per added diagonal is well above chance at every stage and, **late,
tracks the full whole-number added reader.**

**Cost of collapsing the added reader to one bit** (one-bit `S_high` minus `D1`,
within Growing, seed-pair bootstrap):

- t=400: **−0.034 [−0.055, −0.014]** — a real, if small, loss from using one bit
  early (the graded weights carry a little more when the world is far from
  saturation).
- t=2000: **+0.004 [−0.011, 0.018]**.
- t=10000: **+0.003 [−0.016, 0.021]**.

Late, the estimated change from collapsing to one bit is ≈ 0 with an interval
spanning a small loss to a small gain. **We do not declare the two equivalent** —
we report the estimate and its uncertainty: at t=10000 one bit costs, as a point
estimate, essentially nothing, but anything from about −0.016 to +0.021 AUC is
consistent with the data.

**Growing versus the timing-matched control**, one-bit AUC (seed-pair bootstrap):
+0.262 [0.198, 0.331] at t=400, +0.225 [0.152, 0.293] at t=2000, **+0.113 [0.039,
0.183] at t=10000**. The single bit distinguishes Growing from the random-placement
control at every stage; the control's own one-bit reader is at chance
(0.53 → 0.51 → 0.51).

## The bit works on identical topology (complete-topology subset)

At t=10000, 199 of 200 Growing seed pairs have both A and B worlds complete (only
seed 125 excluded); the control's complete subset is the **same 199 seeds**
(reported so this is not silently treated as a matched comparison — the subsets
happen to coincide here). On this subset every world has all 128 diagonals, so
`P_D = 0` and `S_high = −S_low` exactly (both verified). Discrimination there:

| reader | Growing | Control |
|---|---|---|
| one-bit `S_high` | **0.621** | 0.502 |
| whole-number `D1` | 0.618 | 0.494 |
| exact `D0` | 0.642 | 0.493 |
| presence `P_D` | 0.500 (by construction) | 0.500 |

With topology held identical (presence necessarily chance), the one bit still
scores 0.621 — the whole-population value. So the late distinction the bit reads is
a **thresholded visitation footprint on the added diagonals**: which shortcuts have
been re-crossed at least four times, more on the history-favoured side than its
mirror. The exact reader `D0` retains a little more (0.642), so there is residual
information in the sub-bin weights beyond the bit, but the single bit captures most
of it.

## An observation about which reader carries the signal, over time

The one-bit reader is **empty at t=0** (AUC 0.500): right after the imposed history,
almost no diagonal has yet been traversed four times *after activation*, so `b(e)=0`
nearly everywhere. It rises to a peak (~0.80 near t=200–400) and then declines to
0.62. Meanwhile the presence reader `P_D` does the opposite — ~1.0 at t=0 (which
diagonals exist is strongly history-shaped early) decaying to chance late. So which
reader carries the A/B contrast **shifts over time**: edge presence early, the
four-or-more-traversals footprint late.

*This is an observation about correlated readers, not a mechanism.* We do **not**
call it "memory transfer": nothing here shows a stored quantity moving between
substrates. Early one-bit readings would in any case mix presence and visitation;
the complete-topology subset (identical topology) is what isolates the late
statement to visitation.

## Interpretation limits (honoured)

A successful bit reader shows a **thresholded visitation footprint retains
information about the imposed history**. It does **not** reveal threshold-crossing
times, prove memory transfer, establish intrinsic addressing, or isolate
history-shaped placement from every remaining confounder (placement locality near
the probe and unequal evolved weights remain open, as in v2/v4). It is still a
reader with **external coordinates**. Comparisons are exploratory.

## Algebraic identities (checked, not mechanisms)

`S_high + S_low = P_D` per snapshot; on complete topology `P_D = 0` so
`S_high = −S_low`. These are bookkeeping, and AUC is not additive across them.

## One worthwhile next question

The late footprint is "≥4 traversals" on added diagonals. A single reader-only step
would sharpen *when* it forms without claiming threshold-crossing times: sweep the
**bit threshold** itself (b at ≥1, ≥2, ≥3, ≥4, ≥5 traversals, i.e. `w ≥ 3.5, 4.75,
5.375, 5.6875, 5.84375`) on the retained snapshots and report, per checkpoint, the
lowest traversal count whose bit already carries the late AUC. That locates how
*coarse* the visitation footprint can be and still remember, using the snapshots
already saved — no new worlds, no dynamics change. (It is a threshold sweep on a
fixed reader family, not a dynamics parameter sweep.)

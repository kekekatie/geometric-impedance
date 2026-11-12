# Stage 1.6 addendum: two reasons to abstain target two different errors

*Addendum to `STAGE1_REPORT.md` / `STAGE1_5_ADDENDUM.md`. Protocol and predictions
frozen in `stage1_6_abstention.py` (committed at `b09294c`, **before** the run).
Replay: `python3 stage1_6_abstention.py` -> `stage1_6_handback.json`.*

## The headline

The two abstention reasons are **not interchangeable**: each is optimal for a
different error, and which one "wins" depends entirely on what you are trying to
avoid. Both run on the same two-bit restorer, from the same permitted inputs, and
defer the same proposed answer.

- **P2 (sensitivity to discarded history)** — rank by the posterior mass of
  discarded completions whose unpruned same-deadline prediction would reverse the
  answer — **dominates against the deadline-reference**, driving pruning error to
  ~0 by κ≈0.7 on every ensemble and both onset models.
- **P1 (low confidence)** — rank by the restorer's posterior margin — **wins against
  simulated truth** at lower coverage, where P2 actively gets *worse*.

They target different things because the deadline-reference error is *pruning* loss
(which P2 is built to detect) while the truth error also contains future-noise and
inherent ambiguity (which only P1's margin reflects).

## Matched-coverage comparison (primary: t0 input, flag-after, fresh weight-4)

Error among *answered* cases; lower is better. P2 = sensitivity, P1 = low-confidence.

**ONSET_AVG**

| κ | P1 err vs deadline-ref | P2 err vs deadline-ref | P1 err vs truth | P2 err vs truth |
|---|---|---|---|---|
| 1.0 | 0.094 | 0.094 | 0.419 | 0.419 |
| 0.8 | 0.042 | **0.006** | 0.397 | 0.396 |
| 0.7 | 0.016 | **0.000** | **0.387** | 0.428 |
| 0.6 | 0.004 | **0.000** | **0.379** | 0.490 |
| 0.5 | 0.002 | **0.000** | **0.394** | 0.562 |

**FREE_BOTH**

| κ | P1 err vs deadline-ref | P2 err vs deadline-ref | P1 err vs truth | P2 err vs truth |
|---|---|---|---|---|
| 1.0 | 0.024 | 0.024 | 0.409 | 0.409 |
| 0.9 | 0.019 | **0.000** | **0.399** | 0.424 |
| 0.7 | 0.009 | **0.000** | **0.382** | 0.531 |
| 0.5 | 0.000 | 0.000 | **0.392** | 0.715 |

The pattern is identical on the witness stress set and under flag-before, and for
the `lip_parity` secondary input: **P2 is the abstention reason for pruning error;
P1 is the abstention reason for truth error.**

## Which policy did better, at matched coverage (the handback table)

| target \ model | ONSET_AVG | FREE_BOTH |
|---|---|---|
| vs deadline-reference (pruning) | **P2 sensitivity** | **P2 sensitivity** |
| vs simulated truth | **P1 low-confidence** | **P1 low-confidence** |

Not "effectively the same": on the discriminative sets the policies rank 25–50% of
cases on opposite sides of the median (`cases_where_policies_rank_differently`), and
the error curves diverge in opposite directions. They coincide only on the
prior-weighted realistic ensemble (`bounded_le4_prior`), where almost all mass is
easy and both are near-perfect (truth error 0.002–0.008) — prediction A3, held.

## One concrete case where they disagree (what each noticed)

History (scoring only): faults `d0@0, d1@1, d1@2` — a double-onset loss. Permitted
to the decoder: the restorer proposes **1**, with margin **0.497** (barely
confident) but reversal-mass **0.000** (no plausible discarded completion flips the
deadline-optimal). Actual deadline-reference = **1**, truth = **1** — the answer is
*correct*.

- **P1 (low-confidence)** abstains on it *early* (rank 104 of 258): the margin is low,
  so it looks risky.
- **P2 (sensitivity)** keeps it almost to the end (rank 249 of 258): nothing it threw
  away would have changed the deadline-optimal, so it is safe *with respect to
  pruning*.

P1 would discard a correct answer because of irreducible uncertainty; P2 keeps it
because the uncertainty is not about the discarded history. The mirror cases —
confidently wrong from future-noise — are where P2 keeps an error that P1 drops.
That is the whole distinction in one row.

## Frozen scorecard (A1–A5)

| | prediction | verdict |
|---|---|---|
| A1 | P2 ≤ P1 error vs deadline-ref at matched κ<1 (witness) | **HELD, stronger**: P2 dominates on *every* ensemble, → ~0 |
| A2 | policies within a couple points vs truth | **FAILED (informative)**: they diverge in opposite directions; P1 clearly better vs truth |
| A3 | prior-weighted ensemble: low error, P1 ≈ P2 | **HELD** |
| A4 | bracket4 ~0 vs deadline-ref; < always-answer vs truth | **HELD** (0.000 vs deadline-ref; 0.410 vs 0.419 truth) |
| A5 | determinism: identical permitted inputs → identical outputs | **HELD** (e.g. witness: 232 histories over 26 keys, all consistent) |

## What Stage 1.6 establishes

- A streaming decoder that keeps the two round-0 bits has **two distinct, principled
  reasons to hold its answer**, and they are genuinely different: one asks "am I
  unsure?", the other asks "would the past I discarded have changed the best
  same-time answer?". The second is the one aligned with the *information-loss* this
  whole thread is about, and it cleanly recovers the pruning error; the first is the
  one aligned with *being right*.
- Deadline ties never arose (`mean_tie_mass = 0.0` throughout); the frozen tie
  handling was exercised but not triggered.
- All scoring is at matched coverage, against the same-deadline unpruned reference
  and truth separately, with the actual discarded readings used only to score.

## Limits

- One error type, d = 3, T = 6, weight ≤ 4; the realistic ensemble is dominated by
  easy low-weight mass, so the policy *difference* is visible mainly on the
  discriminative weight-4 and witness sets. The witness set remains selection-biased.
- A deferred answer counts as an abstention; recovery after deferral is a separate
  experiment, as scoped.
- Both policies and the deadline-reference are exact-Bayesian for this tiny instance.

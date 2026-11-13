# Stage 1.6 addendum: two reasons to abstain (tie-fixed)

*Addendum to `STAGE1_REPORT.md` / `STAGE1_5_ADDENDUM.md`. Protocol and predictions
frozen in `stage1_6_abstention.py` (committed at `b09294c`, before the run).
Replay: `python3 stage1_6_abstention.py` -> `stage1_6_handback.json`.*

> **Correction (`stage1_6_tie_fix`).** The first version of this addendum reported
> that the two policies "diverge in opposite directions" on truth error. Sol
> replayed `15615db`, confirmed the main separation, and caught a tie-breaking
> artifact: many cases tie at exactly zero sensitivity score (P2 = 0.0), and the
> old `sweep` broke those ties by the hidden simulator fault tuple `h.faults` —
> which the decoder cannot see and which front-loads heavier fault patterns into the
> "answered" set. `sweep` now resolves score ties by **exact expectation over the
> tied bucket** (a boundary bucket is included fractionally and charged its mean
> error), never by `h.faults`. With that fix the apparent divergence disappears:
> P2's truth error at coverage 0.5 on the fresh ONSET_AVG set drops from the
> artefactual 0.562 to **0.393**, level with P1's 0.390. The corrected result is
> cleaner, and is below.

## The headline (corrected)

The two abstention reasons run on the same two-bit restorer, from the same permitted
inputs, and defer the same proposed answer.

- **P2 (sensitivity to discarded history)** — rank by the posterior mass of discarded
  completions whose unpruned same-deadline prediction would reverse the answer —
  **dominates against the deadline-reference across almost all settings**, driving
  pruning error to **~0 by κ≈0.7** on every ensemble and both onset models. Of the 84
  (setting × κ) deadline-ref comparisons there is **one** exception: ONSET_AVG,
  flag-before, fresh set, κ=0.9, where P1 is marginally lower (**0.046 vs 0.051**).
- **Against simulated truth the two policies are close**, with no consistent winner
  once ties are scored by exact expectation. The difference P2−P1 on truth error
  ranges from **−0.12 (P2 better)** to **+0.09 (P2 worse)** across all settings, and is
  within about **±0.025** on the primary t0 fresh sets.

So P2 is the better-or-equal policy overall: it removes the pruning error while its
truth error stays within a small band of P1's (sometimes better, sometimes slightly
worse, no clear direction). The two *rank individual cases differently* (25–50% land
on opposite sides of the median), but that difference is spent almost entirely on the
deadline-reference (pruning) axis — exactly the axis this whole thread is about.

## Matched-coverage comparison (primary: t0 input, flag-after, fresh weight-4)

Error among answered cases; lower is better. P2 = sensitivity, P1 = low-confidence.

**ONSET_AVG**

| κ | P1 err vs deadline-ref | P2 err vs deadline-ref | P1 err vs truth | P2 err vs truth |
|---|---|---|---|---|
| 1.0 | 0.094 | 0.094 | 0.419 | 0.419 |
| 0.8 | 0.042 | **0.006** | 0.396 | 0.396 |
| 0.7 | 0.016 | **0.000** | 0.387 | 0.393 |
| 0.6 | 0.004 | **0.000** | 0.379 | 0.393 |
| 0.5 | 0.002 | **0.000** | 0.390 | 0.393 |

**FREE_BOTH**

| κ | P1 err vs deadline-ref | P2 err vs deadline-ref | P1 err vs truth | P2 err vs truth |
|---|---|---|---|---|
| 1.0 | 0.024 | 0.024 | 0.409 | 0.409 |
| 0.9 | 0.019 | **0.000** | 0.400 | 0.406 |
| 0.7 | 0.009 | **0.000** | 0.381 | 0.406 |
| 0.5 | 0.000 | 0.000 | 0.391 | 0.406 |

On the witness stress set the truth columns often favour P2 (e.g. ONSET_AVG κ=0.7:
P1 0.457 vs P2 **0.437**; κ=0.5: P1 0.472 vs P2 **0.462**), and on the `lip_parity`
input P2 is clearly better on truth at low coverage (FREE_BOTH witness κ=0.5: P1 0.641
vs P2 **0.525**, a −0.12 swing). The witness and `lip_parity` sets are small (n=258)
and selection-biased, so their truth columns are noisier in both directions (up to
+0.09 against P2 at one κ); on the large t0 fresh sets P2 stays within +0.025 of P1.

## Which policy did better, at matched coverage (the handback table)

| target \ model | ONSET_AVG | FREE_BOTH |
|---|---|---|
| vs deadline-reference (pruning) | **P2** (one κ exception) | **P2 sensitivity** |
| vs simulated truth | close, no clear winner | close, no clear winner |

P2 dominates on the pruning axis (bar the single ONSET_AVG flag-before κ=0.9 cell) and
stays within a small band of P1 on truth, so **P2 is the preferable abstention reason**
here. The policies coincide outright only on the prior-weighted realistic ensemble
(`bounded_le4_prior`), where almost all mass is easy (truth error 0.001–0.004) —
prediction A3, held.

## One concrete case where they rank differently (what each noticed)

History (scoring only): faults `d0@0, d1@1, d1@2` — a double-onset loss. Permitted to
the decoder, the restorer proposes **1** with the two raw abstention scores
**P1 margin = 0.497** (barely confident) and **P2 reversal-mass = 0.000** (no plausible
discarded completion flips the deadline-optimal). Actual deadline-reference = **1**,
truth = **1** — the answer is correct.

- **P1 (low-confidence)** is tempted to abstain on it — the small margin looks risky.
- **P2 (sensitivity)** keeps it — it sits in a large zero-reversal-mass bucket (171 of
  the 258 witness cases tie at exactly 0) and is *not* singled out. We report the raw
  scores, not an integer rank inside that tied bucket, since such a rank depends on list
  ordering.

P1 would discard a correct answer over irreducible uncertainty; P2 keeps it because the
uncertainty is not about the discarded history. Summed over all such cases these
opposite rankings largely **cancel on the truth axis** (the cases P1 drops and P2 keeps
are about as often right as wrong), so the two policies end close on truth while P2
wins on pruning.

## Frozen scorecard (A1–A5), post-fix

| | prediction | verdict |
|---|---|---|
| A1 | P2 ≤ P1 error vs deadline-ref at matched κ<1 | **HELD, strongly** — P2 → ~0 on every ensemble |
| A2 | policies within a couple points vs truth, neither dominates | **HELD** (after the tie-fix; the earlier "fail" was the artifact) |
| A3 | prior-weighted ensemble: low error, P1 ≈ P2 | **HELD** |
| A4 | bracket4 ~0 vs deadline-ref; < always-answer vs truth | **HELD** (0.000 vs deadline-ref; 0.410 vs 0.419 truth) |
| A5 | determinism: identical permitted inputs → identical outputs | **HELD** (witness: 232 histories over 26 keys, all consistent) |

## What Stage 1.6 establishes (corrected)

- A streaming decoder that keeps the two round-0 bits has two principled reasons to
  hold its answer. The **sensitivity** reason — "would the past I discarded have
  changed the best same-time answer?" — is the one aligned with the information loss
  this thread is about, and it **removes the pruning error while keeping logical
  accuracy within a small band of the low-confidence policy** (P2−P1 truth error in
  −0.12…+0.09 across settings, ±0.025 on the primary t0 fresh sets). The
  **low-confidence** reason is comparable on accuracy but does not target pruning.
- Deadline ties never arose (`mean_tie_mass = 0.0`). Score ties are now handled by
  exact expectation, so no hidden (non-permitted) quantity enters the coverage curve.
- All scoring is at matched coverage, against the same-deadline unpruned reference and
  truth separately, with the actual discarded readings used only to score.

## Limits

- One error type, d = 3, T = 6, weight ≤ 4; the realistic ensemble is dominated by
  easy low-weight mass, so the policy difference is visible mainly on the
  discriminative weight-4 and witness sets. The witness set remains selection-biased.
- A deferred answer counts as an abstention; recovery after deferral is out of scope.
- Both policies and the deadline-reference are exact-Bayesian for this tiny instance.

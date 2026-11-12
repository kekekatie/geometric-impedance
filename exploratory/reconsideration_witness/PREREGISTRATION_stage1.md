# Stage 1: a principled minimal restorer, on fresh data, with abstention

*Pre-registration for the Stage 1 work in `reconsideration_witness/`, written and
committed **before** the Stage 1 decoder is scored and **before** any Stage 1
outcome is inspected. Builds on the reproduced Stage 0 commit `c0fb273`. The
Stage 0 protocol (`PREREGISTRATION.md`, commit `5971221`) and its code are
unchanged; this adds a new decoder, new evaluation sets, and two reconciliations
Astra asked for.*

## What Stage 1 adds

Stage 0 found the witness and showed, post-hoc, that restoring two pruned
detectors determines the reference's revision. Stage 1 turns that into an actual
**decoder that only ever sees allowed inputs**, scores it against the full-history
reference and against truth on **fresh data outside the original enumeration**,
and lets it **abstain**. It also settles two specification questions.

## Freezes (fixed now, before testing)

**F1 -- round-4 check order and flag delivery.** Round 4 measures `c0` then `c1`
(the circuit's standing per-round order). The delayed report is tested in two
delivery orders, both scored:
- **flag-after-checks:** the report arrives *after* the round-4 checks, so the
  decoder may use the round-4 detectors `det(c,4)`.
- **flag-before-checks:** the report arrives *before* the round-4 checks, so the
  decoder may **not** use `det(c,4)`.

**F2 -- decision deadline.** The decoder must output its logical prediction
immediately upon flag delivery. Consequently it **never** sees round-5 detectors
`det(c,5)` or the closing readout detectors `det(c,'f')`; those are always
unobserved and marginalised. Under flag-before-checks it additionally does not see
`det(c,4)`. The full-history reference (scoring only) sees everything.

**F3 -- evaluation sets.**
- **IN-DIST:** the 843 Stage-0 histories (total fault weight <= 3, one d1 loss at
  onset in `O = {1,2}`).
- **FRESH:** every history of total fault weight **exactly 4** containing >= 1 d1
  loss fault in `O` -- i.e. the next weight shell, entirely outside the Stage-0
  enumeration. Enumerated in full.

**F4 -- onset model (Astra reconciliation #1).** Two named models:
- **FREE_BOTH:** both located faults `('d',1,1)` and `('d',1,2)` freed
  simultaneously (an independent-erasure region). *This is what Stage 0 actually
  computed.*
- **ONSET_AVG:** exactly one onset `s in O`, uniform prior, marginalised; only
  `('d',1,s)` freed per term. *This is what the Stage-0 prose described.*
  ONSET_AVG is the physically-correct model (one loss, unknown onset) and is the
  **primary** model for Stage 1; FREE_BOTH is reported alongside for continuity.
  The witness count is reported under **both** (robustness of the phenomenon).

**F5 -- decoders.**
- **reference** (scoring only): full-history exact marginal over every detector,
  under the onset model. Gold standard; never an input to the others.
- **restorer-2bit:** the Bayesian posterior over the logical, given exactly
  `(serialized streaming state: frame, m2, d3)` + `(the two round-0 detectors
  det(c,0))` + `(observations available by the deadline)`, computed by **summing
  the exact model probability over all discarded/unobserved detector completions
  consistent with those inputs**, under the onset model. Predicts argmax; **abstains**
  when `|P0 - P1| <= eps` (`eps = 1e-12` on the normalised posterior).
- **baseline-0bit:** identical to restorer-2bit but **without** the two round-0
  bits (it marginalises over them). Isolates the value of the two restored bits.
- **streaming-hard:** the ordinary Stage-0 streaming decoder, `frame XOR live`,
  with the live decode using only detectors available by the deadline. It cannot
  use the delayed erasure (the Stage-0 fact). This is the "ordinary streaming
  baseline."

**F6 -- scoring.** For every (decoder, eval set, flag order, onset model): report,
**separately**,
- **reference agreement:** fraction of committed decisions equal to the reference;
- **logical correctness:** fraction of committed decisions equal to simulator truth;
- **coverage:** fraction of decisions committed (not abstained), with the two
  accuracies conditioned on committed decisions.
All three are reported for every decoder (streaming-hard never abstains, coverage
= 1). Truth and the reference are used only to score, never as decoder inputs.

**F7 -- controls reuse (Astra reconciliation #2).** Stage 0's `prompt_flag`,
`loss_aware` and `wide_window` entries are a **single calculation**
(`streaming_commit_erasure XOR streaming_live`), because in this geometry all three
retain the full core at the moment of decision. Their shared result, 52/129
witness pairs distinguished, is reported **once, as one shared Stage-0 figure**,
scored against the original predictions P2/P3, and kept **separate** from the new
Stage-1 restorer evaluation. Where the three would diverge (a report interval
wider than the buffer that the loss-aware deferral still cannot cover; a
multi-stage commit) is stated but not claimed to be exercised here.

## Predictions (fixed now)

**S1.** On IN-DIST, restorer-2bit reaches high reference agreement (>= 95%) on the
witness decisions, versus streaming-hard which fails ~half of them. Conf ~70%.

**S2.** The two bits matter: restorer-2bit beats baseline-0bit in reference
agreement on IN-DIST. Conf ~70%.

**S3.** On FRESH (weight-4), restorer-2bit's reference agreement falls below its
IN-DIST value and genuine abstention appears (coverage < 1): two bits are no longer
always sufficient outside the original shell. Conf ~60%.

**S4.** flag-before-checks is no better than flag-after-checks for every decoder
(strictly less information). Conf ~65%.

**S5.** Logical correctness is below reference agreement for restorer-2bit: it
tracks the reference, which is itself uncertain on these boundary decisions. Conf
~70%.

**S6 (reconciliation).** The witness exists under both onset models (neither count
is zero); the phenomenon is not an artefact of FREE_BOTH. Conf ~85%.

## Reported, not tested

- Witness counts under FREE_BOTH and ONSET_AVG (already: 129 and 575 -- reported
  as the reconciliation, not as a tuned result).
- The abstention rate and the accuracy-on-committed for the restorer on FRESH.
- Any case where baseline-0bit equals restorer-2bit (the two bits not needed).

## Limits I already know

- Still one error type, d = 3, T = 6, one site, `O = {1,2}`. FRESH extends only to
  weight 4; a negative there is bounded to weights <= 4.
- The restorer is exact-Bayesian for this tiny instance (it sums exact marginals
  over completions); it is a feasibility decoder, not one that scales.
- "Two bits" is specific to this commit/buffer geometry and onset interval; the
  geometry-free claim remains: verdict is one bit, the shed reason is more than one.
- Reference agreement is agreement with an optimal *soft* decoder, not with truth;
  the two are reported separately precisely because they differ on boundary cases.

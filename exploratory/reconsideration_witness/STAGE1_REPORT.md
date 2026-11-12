# Stage 1 results: the restorer works, but two bits do not fully heal at a deadline

*Results for the Stage 1 work, run under the protocol frozen in
`PREREGISTRATION_stage1.md` (committed at `28dacf1`, before any Stage 1 outcome
was scored). Built on Stage 0 commit `c0fb273`. Replays via `python3 stage1.py`
(~2 min, deterministic) -> `stage1_handback.json`.*

## One-line answer

A principled restorer that sees **only** allowed inputs (the serialized streaming
state, the two saved round-0 bits, and observations by the decision deadline)
**consistently beats both baselines** — the two bits carry real, usable value as an
actual online decoder. **But** under a realistic decision deadline it recovers only
~**80%** of the full-history reference on the witness decisions, not the ~100% Stage
0 implied. The decomposition shows why, and it is an honest correction: Stage 0's
"two bits suffice" quietly used post-cut future observations that an online decoder
at the report round does not have.

## Astra's two reconciliations (answered first)

**1. The onset model.** Named and tested, both:
- **FREE_BOTH** — both located faults `('d',1,1)`, `('d',1,2)` freed at once (an
  independent-erasure region). *What Stage 0 actually computed.* Witnesses: **129**.
- **ONSET_AVG** — one onset `s in O`, uniform prior, marginalised (only `('d',1,s)`
  freed per term). *What the Stage-0 prose described; the physically correct model
  for one loss of unknown onset.* Witnesses: **575**.

The witness is **not an artefact of FREE_BOTH**: it exists under both, and is in
fact *more* prevalent under the prose/physical model. ONSET_AVG is Stage 1's
primary model; FREE_BOTH is reported alongside. (The implementation discrepancy
Astra caught is real and is now resolved by naming and testing both.)

**2. The reused controls.** Stage 0's `prompt_flag`, `loss_aware` and `wide_window`
were **one calculation** (`streaming_commit_erasure XOR streaming_live`), because in
this geometry all three retain the full core at the moment of decision. Their shared
figure — **52/129 witness pairs distinguished** — is reported **once**, as a single
Stage-0 result bearing on P2/P3, not as three independent controls. They would
diverge only where the loss-aware deferral cannot cover the report interval, or
under a multi-stage commit; neither is exercised here. The genuinely new, independent
control is the Stage-1 restorer below.

## The decoders

All decide **at the flag-delivery deadline** and never see round-5 detectors or the
closing readout (those are marginalised). Scored against the full-history reference
(agreement) and simulator truth (correctness), **separately**.

- **restorer-2bit** — exact Bayesian posterior over the logical given only
  `(frame, m2, d3)` + the two round-0 bits + deadline observations, by summing the
  model probability over every discarded/unobserved completion. *Pre-registered.*
- **baseline-0bit** — same, without the two round-0 bits. *Pre-registered.*
- **streaming-hard** — ordinary Stage-0 streaming `frame XOR live`, live decode
  restricted to deadline detectors. *Pre-registered.*
- **deadline-reference** — Bayes-optimal given the **full, un-pruned** syndrome
  through the deadline. *Post-hoc diagnostic (added after seeing the 80%); clearly
  not pre-registered.* Its gap to the full reference isolates the cost of the
  **deadline**; the restorer's gap to it isolates the cost of **pruning to two bits**.

## Headline table (primary: ONSET_AVG, flag-after-checks)

Coverage = 1.00 for every decoder (see abstention note).

| decoder | IN-DIST witnesses (258) | | IN-DIST all (843) | | FRESH wt-4 (6930) | |
|---|---|---|---|---|---|---|
| | ref-agree | correct | ref-agree | correct | ref-agree | correct |
| deadline-reference | 0.953 | 0.651 | 0.865 | 0.720 | 0.811 | 0.590 |
| **restorer-2bit** | **0.771** | **0.469** | **0.807** | **0.698** | **0.765** | **0.581** |
| baseline-0bit | 0.469 | 0.298 | 0.783 | 0.681 | 0.742 | 0.572 |
| streaming-hard | 0.469 | 0.345 | 0.741 | 0.647 | 0.709 | 0.553 |

The ordering **deadline-ref > restorer-2bit > baseline-0bit >= streaming-hard** holds
on every set, both onset models, and both flag orders (`stage1_handback.json`).

## The gap decomposition (the key honest finding)

On the 258 IN-DIST witness decisions, flag-after-checks:

| | ONSET_AVG | FREE_BOTH |
|---|---|---|
| deadline-ref vs full reference | 0.953 | 0.953 |
| restorer-2bit vs full reference | 0.771 | 0.802 |
| restorer-2bit vs **deadline** reference | 0.810 | 0.849 |

Read it as two independent costs:
- **Deadline cost ~5%.** Even a pruning-free decoder that cannot see round 5 and the
  readout agrees with the all-seeing reference only 95.3% of the time: a few witness
  decisions are only resolved by the post-deadline future.
- **Pruning cost ~15–19%.** Against the *deadline-optimal* (full core, no pruning),
  the restorer with two saved bits + boundary reaches ~81–85%. Knowing `det(c,0)` and
  `m2` (hence `det1 XOR det2`) but not `det1`, `det2` individually genuinely costs
  accuracy once the future is unavailable.

**This corrects Stage 0.** Stage 0's "two pruned detectors determine the reference"
held because its post-hoc analysis conditioned on the whole post-cut record (rounds
4, 5, and the closing readout). Under a realistic online deadline at the report
round, two bits recover ~80%, not 100%. The witness and the information-loss
conclusion stand; the restoration *minimality* was over-optimistic, and only the
frozen deadline surfaced it.

## Pre-registered prediction scorecard

- **S1 — restorer >= 95% reference agreement on witnesses. FAILED.** 0.77 (ONSET_AVG)
  / 0.80 (FREE_BOTH). The deadline caps it at 0.953 and pruning brings it to ~0.80.
  Informative failure — see the decomposition.
- **S2 — the two bits matter (restorer > baseline). HELD, strongly.** On witnesses,
  0.771 vs 0.469 agreement and 0.469 vs 0.298 correctness (ONSET_AVG); the advantage
  persists, smaller, on all-histories and fresh. (Note baseline-0bit == streaming-hard
  on witnesses: without the two bits, the Bayesian decoder has no more distinguishing
  power than hard streaming there — a clean consistency check.)
- **S3 — fresh is harder and abstention appears. PARTIAL.** Fresh *is* harder
  (restorer 0.765 vs 0.807 in-dist agreement). But **no abstention**: with the frozen
  exact-tie threshold, coverage is 1.00 everywhere — the posterior is essentially
  never an exact tie. Meaningful abstention needs a confidence *margin*, which was not
  frozen; that is future work, stated not hidden.
- **S4 — flag-before <= flag-after. HELD.** Everywhere; the round-4 checks are
  informative (deadline-ref on witnesses drops 0.953 -> 0.833 when they are withheld).
- **S5 — correctness < reference agreement for the restorer. HELD.** Everywhere
  (e.g. 0.469 < 0.771): the restorer tracks the reference, itself uncertain on these
  boundary cases.
- **S6 — the witness exists under both onset models. HELD.** 129 and 575.

## Fresh data (outside the original enumeration)

On all 6930 weight-4 histories with a d1 loss — none in the Stage-0 shell — the
decoder ordering and the restorer's advantage **persist** with compressed margins
(restorer 0.765 / baseline 0.742 / streaming 0.709 agreement; deadline-ref 0.811).
The phenomenon and the restorer's value are not artefacts of the original enumeration.

## Handback

- **Built on:** Stage 0 `c0fb273`. **Stage 1 frozen protocol:** `28dacf1`.
- **Replay:** `python3 stage1.py` -> `stage1_handback.json` (deterministic, ~2 min).
- **Frozen before scoring (F1–F7):** round-4 check/flag order; decision deadline
  (predict at flag delivery; round 5 and closers never seen); eval sets (843 in-dist
  + 6930 fresh weight-4); the two onset models; restorer / 0-bit / hard-streaming
  decoders; scoring (agreement, correctness, coverage separate).
- **Abstention/coverage:** 1.00 for all decoders under the frozen exact-tie rule;
  margin-based abstention is noted as future work.
- **Post-hoc, labelled:** `deadline-reference` (the pruning-free deadline ceiling)
  was added after seeing the 80%, to attribute the gap. It is a diagnostic, not a
  pre-registered decoder.

## What Stage 1 establishes

- The retained two bits are **usable** by a real online decoder, not just a lookup
  table: restorer-2bit beats both baselines on every set and both onset models.
- The witness is **robust** to the onset-model choice and **generalises** to fresh,
  higher-weight data.
- Two bits do **not** fully heal under a realistic deadline: ~5% is the deadline,
  ~15% is the pruning. This is an honest correction to Stage 0's restoration
  minimality, and it is the kind of thing only a frozen deadline could reveal.

## Limits

- Still one error type, d = 3, T = 6, one site, `O = {1,2}`; fresh reaches weight 4.
- The restorer is exact-Bayesian for this tiny instance (sum over completions); a
  feasibility decoder, not a scalable one.
- `deadline-reference` is a diagnostic added post-hoc; it is reported as such.
- Reference agreement is agreement with an optimal *soft* decoder that sees the
  future; it is not truth, which is why correctness is reported separately.

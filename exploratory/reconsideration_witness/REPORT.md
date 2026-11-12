# Results: the streaming skin cannot re-judge a committed scar

*Results for `reconsideration_witness/`, written after running the frozen protocol.
The protocol was committed at `5971221` **before** this code existed and **before**
any outcome was seen (`git log` is the witness). Stage 0 feasibility test.*

## One-line answer

**Yes.** Two physically allowed syndrome histories can share byte-identical
serialized streaming state and the same pre-flag logical prediction, yet the
full-history reference strictly revises them in opposite directions when the
*same* delayed atom-loss report arrives — while the streaming decoder, holding one
state for both, cannot move. **129 such witness pairs** were found within the
frozen bound, with zero snapshot-restart failures. Information loss for this
streaming state in this model is established.

The restoration result **diverges from the paper**, informatively: where the
Penrose paper's closed scar was reopened by restoring *one* tile or *one* corner,
here the shed "reason" is **two** pruned detectors, not one — and we can say
exactly why.

## The witness pair (first of 129)

Report payload, identical to every arm, delivered at round 4:
`(site = d1, onset_interval = {1,2}, report_round = 4)`.

Shared serialized pre-flag streaming state (byte-identical, snapshot-restart
verified): `frame = 0`, boundary `m_c(2) = [0, 1]`, live round-3 buffer `[0, 0]`.
Post-cut inputs identical.

| | faults (truth, scoring only) | pruned core syndrome | ref **pre**-flag | ref **post**-flag | truth |
|---|---|---|---|---|---|
| **H1** | `d0@0, d1@1` | `[1,1,0,0,1,0]` | **0** (p0 = 0.5005) | **1** (p1 = 0.9980) | 1 |
| **H2** | `d0@1, d1@1, m1@0` | `[0,0,0,1,0,0]` | **0** (p0 = 0.9990) | **0** (p0 = 0.9980) | 1 |

The reference **strictly prefers 0 for both before the flag**, then **strictly
flips H1 to 1 and strictly keeps H2 at 0** after the same report. No ties. The
streaming decoder holds one state for the group and predicts **0 pre, 0 post, for
both** — it cannot revise, so it is wrong on H1 exactly where full history, using
the information streaming threw away, gets it right.

The only thing distinguishing the two histories is the **pruned core detectors**
`(c0,t0), (c0,t1), (c1,t0), (c1,t1)`. Every retained field — frame bit, boundary,
buffer — is identical. This is the QEC image of the paper's shed witness corner:
the one-bit **verdict** (`frame = 0`) is kept; the **reason** is gone.

## Pre-registered prediction scorecard

**P1 — the witness exists. HELD.** 129 witness pairs within `w_max = 3`
(843 histories, 180 groups, 150 with >1 member). Snapshot-restart failures: 0, so
every witness survives the "a fresh decoder resumes from the snapshot alone" test.

**P2 — delay, not loss information, is the cause. HELD (in substance).** Under the
delayed report the streaming decoder distinguishes **0 / 129** pairs (it has pruned
the relevant detectors). Release the *same* report *before* the commit and the
hard streaming decoder distinguishes **52 / 129** — a strict jump from zero,
driven entirely by *when* the report arrives relative to the commit, not by the
loss information itself. (It is not 129/129 because the hard separable decoder is
sub-optimal; see the retention note under P3.)

**P3 — a wide enough skin heals it. HELD as a retention claim (decoder-dependent as
an exploitation claim).** The loss-aware commit policy (commit delayed 2 rounds
until the report interval closes) and the wide-window control (`W = 5`, retaining
rounds 1–4) both **retain the pruned core**. The naive hard erasure decoder then
splits 52/129 pairs; but the retained information is provably **sufficient for all
129**: restoring just two core detectors determines the reference's revision in
every group (below, held-out confirmed). So *retention* preserves the distinction
exactly as the paper's "sufficiency, not necessity" framing predicts — the gap to
129 is the hard decoder leaving information on the table, not information lost.

**P4 — one bit restores the verdict. FAILED (and this is the interesting part).**
- The pre-registered single bit (round-1 d1-leg parity, `delta(b)=b`) does not even
  separate the first pair (`b_h1 = b_h2 = 0`); its best variant agrees with the
  reference on 141/258 witness decisions (~chance). The frozen rule is dead.
- No *single* fixed detector or parity heals all pairs. The best one corner,
  `(c0,t0)`, separates 89/129 pairs — a majority, so one bit is a genuine
  **pair-specific** restoration, but not a global one.
- The **minimal global restoration is two pruned detectors**, `(c0,t0)` and
  `(c1,t0)` — the two round-0 check detectors. With `(frame, m2)` and these two
  bits, the full-history reference's post-flag revision is determined in **all 180
  groups**. Discovered on even-indexed groups, it holds unchanged on the held-out
  odd groups.

**Why two, not one** (mechanism): the erasure frees the middle qubit d1 at rounds
1 and 2, so syndrome at those rounds can be absorbed by the loss. What cannot be
absorbed is the round-0 syndrome, and it sits on *both* checks around d1. The fate
of the committed logical therefore rides on two round-0 detectors, one per check —
two corners, not one. The paper's single-corner minimality does not port; its
*structure* (a small, local, identifiable remnant restores the full-history
verdict) does.

## Restoration recovers full-history accuracy, not omniscience

Scored on the 258 witness decisions, separating agreement-with-reference from
logical truth (as the protocol requires):

| decoder | agrees with full-history reference | logically correct vs truth |
|---|---|---|
| streaming (un-restored) | 0 / 129 pairs split | **39.1%** |
| streaming + 2 restored detectors | 129 / 129 (by construction) | **62.0%** |
| full-history reference | — | 62.0% |

Restoring two bits lifts streaming's logical accuracy on these hard decisions from
39% to the full-history level of 62%. It does **not** reach 100%, because witness
decisions sit on the logical boundary where the reference itself is only 62%
certain. The claim is retention, not clairvoyance: the two restored bits recover
exactly what the full history knew — no more, no less.

## Handback

- **Frozen protocol commit:** `5971221` (`PREREGISTRATION.md`, committed before any
  code or outcome).
- **Replay command:**
  ```bash
  cd exploratory/reconsideration_witness
  python3 repcode.py                           # linear-model self-check
  python3 decoders.py                          # decoder sanity + snapshot round-trip
  python3 search.py                            # frozen search -> handback.json
  python3 restoration_analysis_EXPLORATORY.py  # post-hoc minimum -> restoration_posthoc.json
  ```
  Deterministic; no RNG. `search.py` runs in ~5 s.
- **Search bounds:** histories = (one d1 loss at onset in O = {1,2}) + up to two
  further base faults, total weight `<= 3`; all 843 such histories enumerated;
  grouped by (serialized pre-flag streaming state, post-cut inputs) into 180 groups.
- **The pair:** both observation histories, the identical snapshot, and the
  reference likelihoods before/after the flag are above and in `handback.json`
  (`witness_pair`).
- **Which field carries the distinction:** none of the serialized fields —
  `boundary_fields_identical = True`; the distinction lives only in the pruned core
  detectors. Ordinary boundary bookkeeping does **not** preserve it.
- **Restoration:** the pre-registered one-bit rule failed; the re-frozen minimal
  rule is two pruned detectors `{(c0,t0),(c1,t0)}` (held-out confirmed),
  recovering reference agreement on 129/129 pairs and logical accuracy 39% -> 62%.
  Recorded in `CHANGES.md`.
- **Archive (Sol Part 1):** not inspected — network blocker recorded in
  `PREREGISTRATION.md` (proxy refuses doi.org / zenodo.org / nature.com). The loss
  model is faithful-by-construction, not matched to the Harvard data.

## What this establishes, and what it does not

- A positive witness **establishes information loss for this streaming state in
  this model**: the state that suffices to *continue* and to *predict* does not
  suffice to *re-judge* a committed decision when delayed evidence arrives. That is
  the paper's third row (Reconsideration), reproduced in a second, independent
  medium.
- It does **not** strengthen the Penrose claims themselves; it generalises the
  phenomenon. And it **refines** the paper's restoration minimality: one record
  there, two here, with a mechanism for the difference.
- Hardware benefit and generality are out of scope for Stage 0 (one error type,
  d = 3, T = 6, w_max = 3, single site, O = {1,2}). A negative elsewhere would be
  bounded to its own configuration; this positive is bounded to this one.

## Limits (carried from the pre-registration, plus what the run taught)

- The hard separable erasure decoder matches the soft reference only ~86% globally;
  we therefore make the retention claim via the information-sufficiency result
  (two detectors determine the reference everywhere), not via the hard decoder's
  52/129. The soft reference is the gold standard throughout.
- "Two detectors" is the minimum for *this* commit/buffer geometry and onset
  interval; a different cut or interval would move it. The robust, geometry-free
  statement is: the verdict is one bit, the shed reason is more than one bit, and a
  small local remnant restores the full-history verdict.

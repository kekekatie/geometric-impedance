# The streaming skin cannot re-judge a committed scar: a QEC witness search

*Pre-registration for `reconsideration_witness/`, written and committed **before** any simulator
exists and **before** any decoding outcome has been inspected (2026-11-12). Stage 0 feasibility
test. Protocol frozen here; any later change is recorded in `CHANGES.md` with its reason.*

## Where this comes from

The paper *The Skin Outlives the Archive* separates three uses of a grown world's past (its Table 6):
the living skin **suffices to continue** building and **suffices to identify** which sibling branch
the world is on, but it **does not suffice to re-judge a scar that was already closed**. The skip
label keeps the one-bit *verdict* ("closed") and sheds the *reason* (the opposing-arm witness corner).
Restoring one tile — or just that one corner — recovers the full-history verdict (its §5.2).

GPT Sol's question ports that third row into quantum error correction:

> Can two physically allowed syndrome histories have **identical retained streaming-decoder state**
> and the **same current logical prediction**, yet require **different revisions** of that prediction
> when the **same delayed atom-loss report** arrives?

The map we are testing:

| Penrose paper | This QEC instantiation |
|---|---|
| closed scar / skip label `Σ` (the kept one-bit verdict) | a committed logical correction in the Pauli frame |
| delayed re-judgment of a dormant site | a delayed, onset-ambiguous atom-loss report landing in an already-committed region |
| thinned state over-admits: `M_L ⊇ M_P` | the streaming state is a lossy function of the full detector history |
| the shed witness corner (the reason) | the pruned core detectors — the single bit the delayed report needs |
| §5.2 "one tile, or one corner" restores the verdict | one restored bit lets streaming reproduce the full-history split |

This is **Stage 0**: one error type, a repetition code, a bounded enumeration. A positive witness
would establish information loss **for this streaming state in this model only**. Hardware benefit and
generality are explicitly out of scope and belong to a later stage.

The Harvard archive (Nature `10.1038/s41586-025-09848-5`; Zenodo `10.5281/zenodo.15685795`;
`SurfaceCodeAnalysis.ipynb`) was to be inspected first (Sol's Part 1). **Access blocker, recorded
2026-11-12:** this environment's network proxy refuses `doi.org`, `zenodo.org` and `www.nature.com`
at CONNECT (`403`, tunnel refused); the allowlist carries only package registries. Archive version,
checksum, field schema and any Fig. 2 reproduction are therefore **not obtained**, and we proceed
with simulation as Sol's protocol directs. If the hosts are later allowed, Part 1 is a separate,
additive pass and does not alter anything frozen below.

## The circuit (frozen)

- **Code.** Distance-3 repetition code against bit-flip (X) errors. Data qubits `D = (d0, d1, d2)`.
  Two Z-parity checks per round: `c01 = Z d0 Z d1`, `c12 = Z d1 Z d2`.
- **Rounds.** `T = 6` check rounds, `t = 0..5`. Each round measures `c01` then `c12`.
- **Prep / readout.** Logical `|0_L>` prepared perfectly at the start (all data bit 0). Perfect
  transversal data readout after round 5; the final checks and the logical are computed from it.
- **Detectors.** A check detector fires where a check measurement differs from the same check in the
  previous round (round 0 compares against the perfect prep; the final data readout supplies the
  closing comparison for each check). Detector record `s` is the ordered bit vector over
  `(check, round)` plus the two readout-closing detectors.
- **Logical observable.** `Z_L` with frozen support `{d0}`. Logical class of a run = (final `d0`
  readout) XOR (decoder correction's net flip on `d0`), relative to the prepared `0`. A fault-free
  run has logical class 0 and an all-zero detector record; this is an implementation self-check that
  must pass before any result is trusted.

## Noise and loss model (frozen)

Faults are **enumerated**, not sampled; probabilities below are used only to weight the exact MAP
likelihood and to break would-be ties, never to draw randoms.

- **Data X fault** on each `(data qubit, round)` with weight `p_d = 1e-3`.
- **Measurement flip** on each `(check, round)` with weight `p_m = 1e-3`.
  (Equal weights; the search does not depend on the exact value, only `0 < p_d, p_m < 1/2`.)
- **Loss.** Exactly one designated site may be lost: the **middle data qubit `d1`** (in the support
  of both checks, so onset ambiguity reaches both). A lost `d1` is an **erasure**: from its onset
  round `s` onward, `d1` carries a hidden, fixed classical value `b_loss in {0,1}` that it did not
  have before (the atom is gone and reloads/reads as an unknown bit), so every `c01` and `c12`
  measurement in rounds `>= s` is taken against that hidden value. A history that includes a loss
  fixes both `s` and `b_loss`; neither is an input to any decoder.
- **Onset interval.** The onset `s` is drawn from the frozen set `O = {1, 2}` — at least two
  plausible onset locations, as required. Different `s` corrupts a different set of later detectors;
  that difference is the whole mechanism.

## Flag payload and release rule (frozen)

- **Payload.** The delayed loss report is the triple `(site = d1, report_round = 4, onset_interval =
  O = {1,2})`. It reveals the site, the detection time, and the interval — **not** the true onset `s`
  and **not** `b_loss`. The three timescales are kept distinct, exactly as Sol's Part 1 asks:
  *detected at* round 4; *may have occurred in* `{1,2}`; *physical onset* `s` (true, hidden, scoring
  only).
- **Release.** Every arm receives the **same** payload at the **same** time (end of round 4).
  - *Main (delayed) condition:* round 4 is **after** the streaming decoder has committed the core
    region that contains `O`; the report lands on already-pruned rounds.
  - *prompt-flag control:* identical payload released **before** that commit (report_round moved to 1),
    while the core detectors are still live.
  - *no-flag control:* the report is never released.

## Decoders (frozen)

Both decoders share the logical convention, the fault weights, and the tie epsilon `eps = 1e-12`.

- **Full-history reference.** Retains every detector and the report. Decodes by **exact MAP
  marginalisation** over the enumerated fault space: it computes `P(logical = 0 | evidence)` and
  `P(logical = 1 | evidence)` by summing fault-config probabilities consistent with the evidence.
  Pre-flag evidence = detectors. Post-flag evidence = detectors + erasure constraint (edges on `d1`
  for rounds `>= s` carry free/zero weight, marginalised over `s in O` with uniform prior). Logical
  prediction = argmax; **strict** iff `|P0 - P1| > eps`.
- **Streaming (sliding-window, Skoric-style).** Frozen widths: commit/core `C = 3` rounds, buffer
  `b = 1` round, window `W = C + b = 4`, step `= C`. It reads rounds left to right; once a window's
  core is settled it decodes the window (exact MAP restricted to the window given the carried
  boundary), **commits** the core correction into a Pauli frame, **drops the core detectors**, and
  carries forward a boundary record (committed boundary defects on the cut between round 2 and 3, plus
  the logical frame accumulator). With `C = 3`, rounds `{0,1,2}` (which contain all of `O`) are
  committed and pruned after reading round 3; the report at round 4 is therefore delayed past the cut.
- **Serialized streaming state (the complete forward-relevant state).** A single dict:
  `{pauli_frame, logical_accumulator, boundary_record, live_buffer_detectors, pending_metadata}`.
  Nothing outside this dict may influence future decoding. **Snapshot-restart check:** a fresh decoder
  constructed from this dict alone, fed the same post-cut inputs and flag, must reproduce the
  continuous run bit-for-bit. A positive witness is void if this check fails.
- **Flag across the cutoff (frozen handling).** When the report's interval intersects the **live**
  region, streaming reweights live-buffer edges and the carried boundary. When the interval lies in
  the **pruned** region (the main condition), streaming has only the committed frame bit for it: it
  applies the report's effect to the logical frame using the committed correction, which no longer
  carries the core detectors. That is the lossy step under test.

### Control decoders (frozen)

- **Loss-aware commit policy.** Same streaming decoder, but it **defers** committing any core round
  that lies inside an open reporting interval until `report_round` has passed. Record the realised
  commit delay and what was retained.
- **Wide-window control.** Same streaming decoder with `C` and `W` enlarged so the window retains the
  checks spanning every onset in `O` **and** their relevant fault paths through `report_round`
  (`W >= report_round - min(O) + 2`). Record realised retention and commit delay.

## Tie handling (frozen)

A decision is **strict** iff the two logical probabilities differ by more than `eps = 1e-12`. A
positive witness requires four strict decisions (same pre-flag argmax on both histories; flip on one,
keep on the other post-flag). Any pair with a non-strict decision anywhere is **excluded**, not
counted either way.

## Search bounds (frozen)

- A **history** = (fault configuration, loss onset `s in O`, hidden bit `b_loss in {0,1}`), with total
  fault weight `<= w_max = 3` (counting each data-X, each measurement flip, and the loss event as one
  fault each). Enumerate **all** such histories within the bound.
- **Grouping.** Histories are grouped by the pair *(identical serialized pre-flag streaming state,
  identical post-cut inputs through the revision decision)*. Report the number of histories
  enumerated, the number of groups, and the group-size distribution.
- Within each group, the candidate pairs are the `C(n,2)` pairs of distinct histories.

## Success criterion (frozen)

**Positive witness.** A pair `(H1, H2)` in one group such that:

1. their serialized pre-flag streaming states are byte-identical (and pass the snapshot-restart check);
2. their post-cut inputs and the flag are identical;
3. the full-history reference **strictly prefers the same** logical class on both pre-flag;
4. after the flag, the reference **strictly flips** one and **strictly keeps** the other;
5. no decision in (3)–(4) is a tie.

Report, for the pair: both observation histories, the shared state snapshot, and the reference
`(P0, P1)` before and after the flag.

**Controls (expected behaviour, stated now).** no-flag → no post-cut divergence introduced by the
flag machinery; prompt-flag → streaming matches the reference on the pair (no witness), isolating
*delay past commit*, not loss information, as the cause; loss-aware and wide-window → distinction
preserved, no witness, with the realised retention and commit delay recorded. If a control
misbehaves, that is reported as a finding against the apparatus, not suppressed.

**Restoration (frozen rule).** One bit `b`, computed from information available **before pruning**,
by the **same rule on both histories**:

> `b` = XOR of the two core detectors on `d1`'s check legs (`c01` and `c12`) at the round
> `min(O) = 1` — i.e. the committed-region syndrome bit that the erasure reweighting at the earliest
> plausible onset would consume. Metadata it needs and that we record: the site `d1`, the round `1`,
> and the two check indices.

Add `b` to the snapshot and let streaming re-run the post-flag revision. If the reference split on the
found pair is recovered, that is a **pair-specific** positive. Because this restoration rule is
written here **before** any outcome is seen, it is already frozen; if the run shows it must be revised
to fit the pair, the revision is recorded in `CHANGES.md` and then tested on **fresh** histories with
full counts reported. **Logical correctness** (agreement with simulator truth) is reported
**separately** from **agreement with the full-history reference**.

## Predictions (fixed now)

**P1: The witness exists.** At least one positive pair is found within `w_max = 3`. Confidence ~75%.

**P2: Delay is the cause, not loss information.** In the prompt-flag control, streaming matches the
reference on any pair found by P1 (zero surviving witnesses). Confidence ~70%.

**P3: A wide enough skin heals it.** Under both the loss-aware commit policy and the wide-window
control, zero witnesses survive — the result is *sufficiency, not necessity*, as the paper frames its
own retention claim. Confidence ~70%.

**P4: One bit restores the verdict.** The frozen one-bit rule `b` recovers the reference split on the
found pair. Confidence ~55% that the *frozen-as-written* rule works unchanged; ~80% that *some* single
pre-pruning bit works (with the rule then re-frozen and re-tested on fresh histories).

## Reported, not tested

- The group-size distribution and total search coverage (histories, groups).
- For a found pair: the exact serialized snapshot and the four `(P0, P1)` pairs.
- Realised retention and commit delay for the loss-aware and wide-window controls.
- Whether ordinary boundary bookkeeping (the `boundary_record` field) already distinguishes the pair;
  if so, which field carries it (this would weaken the claim and is reported plainly).
- If a pair exists but one-bit restoration fails, both outcomes are reported.

## Limits I already know

- One error type (bit-flip only), one code distance, one affected site, `T = 6`, `w_max = 3`,
  `O = {1,2}`. A negative result is bounded to exactly this configuration and claims nothing beyond it.
- Exact-MAP marginalisation is tractable only because the instance is tiny; this is a feasibility
  witness, not a decoder anyone would ship.
- "Streaming loses information" is trivially true for any under-buffered committing decoder. The only
  claim of interest is the sharp one: identical *verdict* kept, *reason* shed, and **one** restored
  bit heals it — the direct analogue of the paper's one corner.
- A positive QEC witness *generalises* the paper's phenomenon to a second medium; it does not
  strengthen the Penrose claims themselves.
- The archive was not inspected (access blocker above), so the loss model is faithful-by-construction,
  not matched to the Harvard data's actual loss reporting.

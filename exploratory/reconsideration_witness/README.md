# reconsideration_witness

The QEC port of the third use-of-the-past in *The Skin Outlives the Archive*
(Table 6, **Reconsideration**): the state that suffices to **continue** and to
**identify** does not suffice to **re-judge** a decision already committed.

**Question (GPT Sol).** Can two physically allowed syndrome histories have
identical retained streaming-decoder state and the same current logical
prediction, yet require different revisions when the same delayed atom-loss
report arrives?

**Answer (Stage 0, this folder).** Yes. In a distance-3 repeated-check
repetition code with one delayed, onset-ambiguous d1 loss, **129 witness pairs**
exist within a bounded search: identical serialized streaming state, same pre-flag
prediction, and the full-history reference strictly flips one history and keeps
the other on the same report, while streaming cannot move. The kept one-bit
**verdict** (the committed Pauli frame) survives; the **reason** (the pruned core
detectors) is shed — the QEC image of the paper's witness corner. Restoring a
small local remnant heals it, but **two** detectors, not the paper's one.

## Files

**Stage 0** — does the witness exist, and what restores it?

| file | role |
|---|---|
| `PREREGISTRATION.md` | the frozen protocol — committed **before** any code or outcome (`5971221`) |
| `repcode.py` | exact GF(2) simulator + linear model of the code (self-checking) |
| `decoders.py` | soft full-history reference (exact MAP, both onset models) + hard streaming decoder (commit / prune / serialize / restore) + control policies |
| `search.py` | bounded witness search, controls, frozen restoration rule -> `handback.json` |
| `restoration_analysis_EXPLORATORY.py` | post-hoc minimal-restoration analysis -> `restoration_posthoc.json` |
| `REPORT.md` | Stage 0 results, prediction scorecard (held / failed), handback |
| `CHANGES.md` | the one allowed post-outcome change: the restoration rule |

**Stage 1** — a principled restorer, on fresh data, at a real decision deadline.

| file | role |
|---|---|
| `PREREGISTRATION_stage1.md` | frozen Stage-1 protocol — committed before scoring (`28dacf1`) |
| `stage1.py` | Bayesian restorer + 0-bit / hard-streaming baselines + deadline-reference diagnostic + fresh weight-4 eval + both onset models -> `stage1_handback.json` |
| `STAGE1_REPORT.md` | Stage 1 results, scorecard, the deadline-vs-pruning decomposition, Astra's two reconciliations |
| `stage1_5_onset_lip.py` | Stage 1.5 diagnostic: live-vs-live scoring + onset-lip variants (t0/t1/lip-parity/3bit/bracket4) + frame-redundancy -> `stage1_5_handback.json` |
| `STAGE1_5_ADDENDUM.md` | Stage 1.5 results: the pruning gap is *exactly* the 4-bit onset bracket; frame redundant given it but non-substitutable; the t0/t1 lip asymmetry |
| `stage1_6_abstention.py` | Stage 1.6: two abstention policies (low-confidence margin vs sensitivity-to-discarded-history) on the same restorer, matched-coverage -> `stage1_6_handback.json` |
| `STAGE1_6_ADDENDUM.md` | Stage 1.6 results: the two abstention reasons target different errors — sensitivity wins vs the deadline-reference, low-confidence wins vs truth |

**Stage 1.6 result in one line.** Given the two retained bits, the streaming decoder
has two principled reasons to abstain, and they are *not* interchangeable: ranking by
sensitivity-to-discarded-history drives pruning (deadline-reference) error to ~0 by
κ≈0.7, while ranking by posterior margin (low confidence) is the one that lowers error
vs truth. One asks "would the past I discarded change the best same-time answer?"; the
other asks "am I unsure?" — and which you want depends on which error you fear.

**Stage 1.5 result in one line.** The deadline pruning gap is exactly the four
onset-bracket detectors `(c0,t0),(c1,t0),(c0,t1),(c1,t1)`: restoring them makes the
decoder equal the deadline-optimal (1.000), `frame` is then redundant but cannot
replace any of the four (it is a non-invertible threshold), and the t0-vs-t1
asymmetry follows Argon's lip geometry on unbiased data (FREE_BOTH→t0, ONSET_AVG→t1
/ timing-parity) — modestly, and masked on the t0-selected witness set.

**Stage 1 result in one line.** The restorer beats both baselines everywhere (the
two bits are usable), but under a realistic decision deadline it recovers ~80% of the
full reference on witnesses, not ~100%: ~5% is the deadline (future detectors unseen),
~15% is pruning to two bits. Stage 0's "two bits suffice" held only because its
post-hoc analysis also used the post-cut future. The witness is robust to the onset
model (129 under FREE_BOTH, 575 under the prose-faithful ONSET_AVG) and generalises to
fresh weight-4 data.

## Replay

```bash
python3 repcode.py                           # linear-model self-check
python3 decoders.py                          # decoder sanity + snapshot round-trip
python3 search.py                            # frozen search  -> handback.json
python3 restoration_analysis_EXPLORATORY.py  # post-hoc minimum -> restoration_posthoc.json
```

Deterministic, no RNG, ~5 s. Depends only on `numpy`.

## Scope and honesty

Stage 0: one error type, d = 3, T = 6, weight <= 3, one site, onset in {1,2}. A
positive witness establishes information loss **for this streaming state in this
model** — a second, independent instance of the paper's phenomenon, not a
strengthening of the Penrose claims and not a hardware result. The Harvard archive
(Sol Part 1) could not be inspected: the session's network proxy refuses
doi.org / zenodo.org / nature.com (blocker recorded in `PREREGISTRATION.md`), so
the loss model is faithful-by-construction, not matched to the Harvard data.

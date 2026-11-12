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

| file | role |
|---|---|
| `PREREGISTRATION.md` | the frozen protocol — committed **before** any code or outcome (`5971221`) |
| `repcode.py` | exact GF(2) simulator + linear model of the code (self-checking) |
| `decoders.py` | soft full-history reference (exact MAP) + hard streaming decoder (commit / prune / serialize / restore) + control policies |
| `search.py` | bounded witness search, controls, frozen restoration rule -> `handback.json` |
| `restoration_analysis_EXPLORATORY.py` | post-hoc minimal-restoration analysis -> `restoration_posthoc.json` |
| `REPORT.md` | results, prediction scorecard (held / failed), handback |
| `CHANGES.md` | the one allowed post-outcome change: the restoration rule |
| `handback.json`, `restoration_posthoc.json` | machine-readable results |

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

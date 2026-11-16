# Distance-5 bulk run (2026-11-16)

The first distance-5 site in the re-judgment series: **bulk (2,2)** in the
d=5 rotated surface code (25 data, 24 stabs) — interior, four neighbours, local
diamond query **8**, outside both logical supports. Tests whether the local
witness bracket still suffices when the code grows, using a tractable decoder
that replaces Astra's dense frame table (infeasible at d=5: 2^49/sector).

## Headline

**At d=5 the full archive almost stops being worth keeping — and it is the thin
record, not the local bracket, that catches up to it.** The archive's weighted
accuracy advantage over the thin record collapses **126×** (0.00289 → 0.000023)
from d=3 to d=5. The eight-reading bracket-vs-record disagreement *widened* ~47×
(Sol's open M4), but that is largely because the record no longer out-predicts
the thin record: when bracket and record disagree at d=5, the bracket is correct
**48.4%** of the time. See `HANDBACK_D5.md` for the full table and the caveat.

## Method (checkpoint 1) and result (checkpoint 2)

- `FEASIBILITY.md` — the feasibility pass: the bounded-weight sparse-frame decoder
  with packed-uint64 conditioning, validated at d=3 within a frozen tolerance of
  Astra's exact E_frame (`09a79c1`), and the frozen d=5 protocol (predictions
  M1–M4). Confirmed tractable (full 549,088-history run in 35 min).
- `HANDBACK_D5.md` — the d=3-vs-d=5 bulk table, the three-arm value breakdown, the
  ensemble weight-shift caveat, a replayable single-fault disagreement where the
  skin beats the archive, a related-work anchor, and the M1–M4 scorecard.

## Files

| file | role |
|---|---|
| `src/nd_surface.py` | general-d rotated surface code; validated to match stage2_surface at d=3 |
| `src/nd_infer.py` | tractable `Decoder(d, site)`: bounded-frame MAP, packed conditioning, four arms |
| `src/nd_run.py` | ensemble harness (XOR compose, onsets {1,2}, deadline 4); d=3 validation + d=5 measurement |
| `src/compare.py` | builds the comparison table + `results/d3_vs_d5.json` |
| `results/d3_1_1.json` | d=3 bulk under this method (diamond 331; validates vs Astra's 341) |
| `results/d5_2_2.json` | d=5 bulk measurement (549,088 histories) |
| `results/d3_vs_d5.json` | derived comparison |

## Replay

```sh
cd src
python3 nd_surface.py          # self-check: d=3 matches stage2_surface; d=5 builds
python3 nd_run.py 3 1,1        # d=3 bulk under this method (~90 s)
python3 nd_run.py 5 2,2        # d=5 bulk (~35 min, 549,088 histories)
python3 compare.py            # table + results/d3_vs_d5.json
```

Built on the d=3 geometry series: bulk `09a79c1`, edges `93cf914` / `9564067`,
corner `78f8337`. Runtime `*.out` and `__pycache__` are git-ignored.

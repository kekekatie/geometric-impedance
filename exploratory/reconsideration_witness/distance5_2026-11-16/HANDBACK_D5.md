# Distance-5 bulk: does the local witness bracket still suffice? (handback)

2026-11-16. Checkpoint 2 of Sol's distance-5 request. Full run over all
**549,088** histories of the d=5 bulk site **(2,2)** (interior, four neighbours,
query 8, outside both logical supports), scored with the tractable bounded-frame
decoder validated in `FEASIBILITY.md`. Compared against the **same method** at
d=3 bulk (not Astra's exact d=3). Invariants held: `whole == thick` exactly (0),
JSON roundtrip 0 / 21,963 sampled.

## Headline

**As the code grows from d=3 to d=5, the full archive almost stops being worth
keeping — and the thin record, not the local bracket, is what catches up.**

The eight-reading query disagrees with the full record *more* often at d=5
(weighted 0.0036% → 0.169%, a ~47× widening — Sol's open M4 gap **widened**). But
that number is misleading on its own, and the correctness metrics say why: the
full record itself barely out-predicts the thin record at d=5. The archive's
weighted-accuracy advantage over the thin record **collapses 126×** (0.00289 →
0.000023). At d=3 the local bracket did the heavy lifting of recovering that
advantage (99.6% of it); at d=5 there is almost no advantage left for anyone to
recover. On the shrinking set of histories where bracket and archive still
disagree, the archive is barely more trustworthy than the skin — the bracket is
the correct one **48.4%** of the time (vs 34.4% at d=3), approaching a coin flip.

## d=3-vs-d=5 bulk comparison (same decoder both distances)

| metric | d=3 bulk (1,1) | d=5 bulk (2,2) | read |
|---|---:|---:|---|
| query readings | 8 | 8 | four-neighbour bulk, unchanged |
| ensemble histories | 68,128 | 549,088 | pool scales with code (8×) |
| raw diamond-vs-record disagree | 331 | 3,464 | **not comparable** (8× ensemble) |
| weighted **thin** disagree % | 0.3006% | 0.1717% | thin got *closer* to the record |
| weighted **diamond** disagree % | 0.0036% | 0.1692% | **gap widened ~47× (M4)** |
| weighted truth — thin | 0.993013 | 0.997078 | thin caught up to thick |
| weighted truth — diamond | 0.995890 | 0.997092 | tracks thick at both d |
| weighted truth — thick/whole | 0.995901 | 0.997101 | d=5 protects the logical better |
| **archive marginal** (thick−thin truth) | 0.002888 | **0.000023** | **archive value shrank 126×** |
| diamond marginal (diamond−thin truth) | 0.002877 | 0.000014 | bracket adds almost nothing at d=5 |
| diamond-right / record-right (disagreements) | 114 / 217 | 1678 / 1786 | 34.4% → **48.4%** diamond-right |
| deadline payload — thin | 26 | 74 | fixed |
| deadline payload — diamond mean / max | 36.4 / 66 | 90.2 / 130 | mean saves 25% vs thick; max exceeds it |
| deadline payload — thick | 40 | 120 | fixed |
| whole == thick | 0 ✓ | 0 ✓ | archive==record, exact |
| roundtrip mismatches | 0 | 0 / 21,963 | serialization intact |

## What the three arms are each worth, at each distance

- **Thin alone** (the committed two-bit frames, no archive): at d=3 it is clearly
  the weakest (truth 0.99301, 0.29% below thick). At d=5 it is *essentially as
  accurate as the full record* (0.99708 vs 0.99710). The deadline-committed
  logical, at d=5 bulk, is almost entirely fixed by the thin record.
- **Diamond** (thin + local 8-reading bracket): recovers ~all of the archive's
  advantage at both distances — but at d=5 there is only 0.000023 of advantage to
  recover, so it adds 0.000014. The bracket is a faithful stand-in for the
  archive; it just has less and less to stand in *for*.
- **Thick / whole** (full record): the whole-archive query reproduces the thick
  record exactly at both distances (0 disagreements), as designed.

## The honest caveat (ensemble weight-shift)

The weighted **disagreement** widening (0.0036% → 0.169%) is partly an artifact of
the ensemble, and we flag it rather than lean on it. Because the fault pool grows,
the d=5 ensemble places more *relative* weight on single-fault histories (25.7% of
total weight vs 11.4% at d=3), and single-fault histories are exactly where the
bracket and the record can differ. So some of the higher weighted disagreement is
the ensemble reweighting, not a per-fault increase in bracket-insufficiency.

The **truth-based** statements are the ensemble-robust ones, and they all point
the same way: the archive's marginal accuracy over the thin record shrank 126×,
and the thin record alone reaches the full record's accuracy at d=5. That is the
result we stand behind. (A follow-up that holds the single-fault weight fraction
fixed across distances would sharpen the disagreement number specifically.)

## Replayable disagreement (a single fault where the skin beats the archive)

The highest-weight history where the bracket and the record part ways at d=5 is a
**single** X fault on data (0,0) at round 4, onset-1 loss at (2,2), weight 1e-3:

| arm | committed logical | correct? |
|---|---|---|
| thick (full record) | 0 | ✗ |
| diamond (thin + bracket) | 1 | ✓ |
| thin | 1 | ✓ |
| simulated truth | 1 | — |

Here the full archive commits the *wrong* deadline label and the local skin (and
the thin record) commit the right one — a concrete, non-exotic (single-fault)
instance of "agreement with the record ≠ correctness," now with the skin on the
correct side. Replay: `cd src && python3 nd_run.py 5 2,2` (the `example` field).

## Related work (anchoring, from a literature check)

Atom-loss-as-delayed-erasure in surface codes is an active 2024–2026 line, and
our toy is adjacent to it — usefully, not redundantly:

- Perrin et al., *QEC resilient against atom loss* ([arXiv:2412.07841](https://arxiv.org/abs/2412.07841)):
  using loss-detection information improves logical error ~3 orders of magnitude
  over a naive decoder — the real-world form of our thick-vs-thin premise (the
  delayed report is worth keeping *something* for).
- A delayed-erasure maximum-likelihood decoder with **"superchecks"** (gauge-merged
  stabilizers around the lost atom) is the real-world cousin of our local witness
  bracket.
- Li, Peng & Wang, *Where Atom Loss Lands Matters* ([arXiv:2608.17913](https://arxiv.org/abs/2608.17913)):
  total loss exposure is the wrong measure; *position* on the code and its decoder
  sensitivity are what count — a close echo of our non-monotonic geometry result
  (corner beats edges).

Their question is "how much does loss at position X hurt the **full** decoder?"
Ours is the complementary one the Penrose framing is about: "how much does the
**full archive** buy you over the thin record and a local bracket, and how does
that change as the code grows?" The d=5 answer — the archive's margin collapses
~126× while the thin record carries nearly everything — is, as far as the check
found, ours.

## Files

| file | role |
|---|---|
| `FEASIBILITY.md` | checkpoint-1 feasibility + frozen d=5 protocol (predictions M1–M4) |
| `src/nd_surface.py`, `src/nd_infer.py`, `src/nd_run.py` | general-d code, tractable decoder, harness |
| `src/compare.py` | builds the table + `results/d3_vs_d5.json` |
| `results/d3_1_1.json`, `results/d5_2_2.json`, `results/d3_vs_d5.json` | d=3 (this method), d=5, comparison |

## Predictions scorecard

- **M1** whole == thick at d=5 → **held** (0 disagreements).
- **M2** storage thick 120 / thin 74 / 7 bits per event / diamond max 116 →
  **held, with a sharper max**: thick 120, thin 74, 7 bits/event all exact. The
  predicted diamond max of 116 was the *150-history probe's* max (6 archived
  events); the full ensemble reaches **8** archived events → **130** (= 74 + 8×7),
  the same structural max-event count as d=3 (66 = 26 + 8×5). A probe under-counts
  the tail; the full run is the right source for a worst-case payload.
- **M3** query 8 → **held**.
- **M4** direction of the disagreement gap (left open) → **widened** (~47×
  weighted), but the load-bearing finding is the 126× collapse of the archive's
  marginal accuracy, with the thin record (not the bracket) being what catches up.

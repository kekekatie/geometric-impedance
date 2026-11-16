# Pass 1: stratified + tie-aware audit of the d=5 126× margin drop (handback)

2026-11-16. Sol's audit asked, before any k=3 sampling, whether the d=5 collapse
of the archive's truth-margin over the thin record is **real within-stratum** or
an artifact of **(a)** the k=0,1,2 mix shift (single-fault weight 11.4% → 25.7%),
**(b)** hard-label scoring hiding 50/50 ties, or **(c)** the k≤2 truncation. Pass 1
re-scores the *same* decoder over the *same* d=3 bulk (1,1) and d=5 bulk (2,2)
ensembles, stratified by k and scored both hard and tie-aware (0.5 credit on an
exact 1e-12 tie). Overall hard truth reproduces the headline runs exactly at both
distances.

## Verdict (two findings that fit together)

**1. The margin collapse is real and within-stratum — if anything the 126× is
conservative.** The archive's tie-aware truth advantage over the thin record,
*within each fault stratum*:

| stratum k | d=3 (thick − thin) | d=5 (thick − thin) | shrink |
|---|---:|---:|---:|
| k=0 (loss only) | 0 | 0 | — (no ordinary fault, arms agree) |
| k=1 (single fault) | **+0.0230769** | **−0.0000000** | → vanishes entirely |
| k=2 (double fault) | +0.0339744 | +0.0004907 | 69× |

A single ordinary fault at d=5 bulk *never* lets the archive decide better than
the thin record (margin is exactly zero to 1e-7). The archive's residual advantage
lives only in k=2, and even there it shrank 69×. Standardizing **both** distances
to a **common** fault-mix (so the mix shift cannot explain anything) confirms it:

| matched mix | d=3 margin | d=5 margin | ratio |
|---|---:|---:|---:|
| d=3's mix (for both) | 0.002888 | 0.000004 | **722×** |
| d=5's mix (for both) | 0.007556 | 0.000023 | **328×** |
| flat k1/k2 (ignore k=0) | 0.028526 | 0.000245 | 116× |

Under every matched mix the d=5 margin sits 116–722× below d=3. The mix shift did
**not** create the collapse — it partly *masked* it: under d=5's own mix the d=3
margin would have been *larger* (0.0076), because the shift upweighted exactly the
strata (k=1, k=2) where the archive helps at d=3. So the honest within-stratum
collapse (≈328× at matched d=5 mix) is steeper than the 126× own-mix headline.

**2. But Sol's tie catch is dead right about the *character* of d=5 — what little
thick/thin difference survives is almost entirely 50/50 ties, not wins.** The
pairwise decomposition (as fraction of total weight):

| | d=3 | d=5 |
|---|---:|---:|
| thick-only-right (decisive archive win) | 0.0029464 | 0.0000254 |
| thin-only-right (decisive thin win) | 0.0000581 | 0.0000021 |
| **tie-involved mass** | 0.0000037 | **0.0018609** |
| net (thick − thin) | 0.0028883 | 0.0000233 |

At d=3 the margin is genuine: the archive out-*decides* the thin record (decisive
wins 0.29% of weight, ties negligible). At d=5 the relationship **inverts** — the
tie-involved mass (0.00186) is **80× the net gap** and ~70× the decisive-win mass.
Where the full record and the thin record differ at d=5, they differ almost only
because the full record returns an **exact 50/50 tie** where the thin record
commits. The full record ties on **0.186%** of weight (5,408 histories) vs the
thin record's **0.017%** (1,952) — the archive lands on knife-edge ambiguity **11×
more often**. This is Sol's ambiguous 5-tile seam (a weight-5 logical chain through
the centre loss splitting into two weight-2 histories with identical readings and
opposite true parity): the archive's extra evidence, at d=5, mostly resolves into
*honest ambiguity*, not better commitments.

**Tie-aware scoring does not move the per-arm truth** (hard == tie-aware to 6 d.p.
at both distances), so the collapse is not a tiebreak artifact either — the archive
genuinely has nothing decisive left to add.

## What this does to the story

"The skin outlives the archive" gets sharper and more honest. At d=5 bulk the
archive neither beats nor is beaten by the thin record + local skin: all three
reach ~99.71% committed-logical accuracy. The archive's one surviving
distinction is epistemic, not operational — it *knows when it cannot know* (honest
50/50 on the seam) where the thin record guesses and is right about half the time
by luck. That honesty buys **no** accuracy at the deadline. So the committed
deadline logical at d=5 bulk is determined by the thin record; the archive's
residual role is to *flag* the genuinely-undecidable seams, not to decide them
better — and the earlier "the skin re-judges correctly where the archive fails"
framing of the highlighted single-fault example was wrong: that example is one of
these 50/50 ties (see erratum in `HANDBACK_D5.md`).

## The k≥3 question (Pass 2), and how cheap it is

The k≤2 truncation excludes ~0.64% of probability mass at d=5 (vs 0.03% at d=3),
which is large next to the 0.0023-point residual gap — so the truncation *could*
in principle hide archive value at k≥3. Two things make that unlikely but worth a
prespecified check: the within-stratum margin is *decreasing* in k (k=1 → 0, k=2 →
0.0005), and the seam mechanism is about ambiguity, not archive advantage. Pass 2,
as Sol proposed:

- **k=3 sample.** Full k=3 enumeration at d=5 is C(370,3)·8 ≈ 67M histories — too
  many — so a Monte-Carlo sample of ~100–200k k=3 histories, scored by the same
  arms, estimates the within-k=3 thick−thin margin and its tie mass. At the warm
  ~4 ms/history that is **~7–13 min**. Prespecify the sample size and the tolerance
  before running.
- **Decoder-cap check.** Re-score a sample with the marginal cap raised w_dec 3→4
  to confirm the bounded marginal is not itself hiding archive value at d=5. Same
  ~4 ms/history on the sample; a 50k sample is **~3–4 min**.

I'd run both as one short Pass 2 once these numbers are agreed. My expectation
(loosely held): k=3 will not resurrect the archive's decision-advantage, but it
*will* add more seam ties to the thick arm — same shape as k=2, more pronounced.

## Files

| file | role |
|---|---|
| `src/pass1.py` | stratified + tie-aware rescore (per distance); overall hard truth matches the headline runs |
| `src/compare1.py` | cross-distance report: within-stratum margins, mix standardization, pairwise decomposition |
| `results/pass1_d3_1_1.json`, `results/pass1_d5_2_2.json` | per-distance stratified rescores |
| `results/pass1_report.json` | the combined report (numbers above) |

Replay: `cd src && python3 pass1.py 3 1,1 && python3 pass1.py 5 2,2 && python3 compare1.py`
(d=5 rescore ~35 min; d=3 ~15 s).

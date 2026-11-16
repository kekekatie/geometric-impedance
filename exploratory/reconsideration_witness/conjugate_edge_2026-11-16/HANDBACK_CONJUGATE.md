# Distance-3 conjugate edge control: 3-way geometry comparison

**Result: the conjecture is refuted. Keeping both logical-sector Z-arms at (2,1) does
NOT restore bulk-like re-judgment accuracy. The 341 → ~870 jump is driven by bracket
SIZE (4 checks → 3), not by which sector's check is lost.** At (2,1) (2 Z-arms + 1
X-arm, 6 bits) the diamond disagrees with the same-deadline reference on 837 histories —
essentially the same as the Z-open site (1,2) (1 Z-arm + 2 X-arms, 6 bits) at 896, and
far above the bulk (1,1) (2 Z + 2 X, 8 bits) at 341. The onset-sector X-arm matters as
much as the logical-sector Z-arm, because shared-onset inference couples them.

Built on the Z-open edge run `93cf914` and Astra's corrected E_frame baseline `09a79c1`,
reusing her `model.py` **unchanged** (only the report site differs). Frozen conjugate
protocol `9832cd1`, committed before this run.

## 3-Way distance-3 geometry comparison (corrected E_frame; each site vs its own thick)

| site | star arms | lip bits | thin disagree | **diamond disagree** | diamond agreement (weighted) | diamond correctness vs truth | thick correctness |
|---|---|---:|---:|---:|---:|---:|---:|
| **bulk (1,1)** | 2 Z + 2 X | 8 | 3,433 | **341** | 0.999962 | 0.995891 | 0.995901 |
| **Z-open (1,2)** | 1 Z + 2 X | 6 | 3,280 | **896** | 0.999572 | 0.995523 | 0.995666 |
| **X-open (2,1)** | 2 Z + 1 X | 6 | 2,545 | **837** | 0.999030 | 0.996618 | 0.996625 |

**diamond-right / reference-right** (who was correct when diamond and thick disagreed):
bulk **123 / 218** (36% diamond-right), Z-open **301 / 595** (34%), X-open **387 / 450**
(46%). Payload bits max: bulk 66, both edges 61 (the edge archive is smaller — the loss
fires 3 checks not 4). Diamond query readings: bulk 8, both edges **6**.

## What the control shows

- **Bracket size dominates (H5 refuted).** Going from a 4-check bracket (bulk, 341) to a
  3-check bracket (either edge, 837–896) is the large effect. Keeping both logical-sector
  Z-arms at (2,1) buys nothing bulk-like: 837 is ≈ the Z-open 896 and ≈2.5× the bulk 341.
- **Both sectors' arms matter comparably.** The scored logical `Z_L` is decoded by the
  X-sector (Z-stabs), but the onset is inferred jointly, so an onset-sector X-arm feeds
  the logical decision almost as much as a logical-sector Z-arm. Losing either one
  degrades re-judgment similarly.
- **The small sector asymmetry is metric-dependent — do not over-read it.** By raw count
  X-open (837) is slightly *below* Z-open (896); by weighted agreement X-open (0.99903)
  is slightly *above* (worse than) Z-open (0.999572). The two disagree because the
  disagreements fall on different-weight histories at the two sites. There is no clean
  "logical sector dominates" signal; the honest statement is that both edges are far
  worse than bulk and roughly equal to each other.
- **Correctness ≠ agreement, again.** At (2,1) the diamond's *truth* correctness
  (0.996618) essentially equals its thick reference (0.996625) — in fact the (2,1)
  ensemble is a touch easier for everyone — and the diamond is right on **46%** of its
  disagreements. So the extra edge disagreements are not mostly the diamond being wrong;
  they are the diamond and the soft reference splitting on hard, near-boundary histories.

## Frozen-prediction scorecard (H1–H5)

| | prediction | verdict |
|---|---|---|
| H1 | edge query reconstructs 6 old values | **HELD** (positions {5,6,7}×{1,2}) |
| H2 | whole-archive == thick | **HELD** (0 disagreements; posteriors within 1e-12) |
| H3 | thin+diamond fewer disagreements than thin alone | **HELD** (837 < 2,545) |
| H4 | cold fresh-process restart reproduces every decision | **HELD** (272,512 roundtrip checks 0 mismatches; 4 cold processes, max prob Δ = 0.0) |
| H5 | **conjecture:** keeping both Z-arms restores near-bulk accuracy ((2,1) << 896, nearer 341) | **REFUTED** — (2,1) = 837 raw ≈ 896, weighted agreement 0.99903 (worse than Z-open); bracket size, not sector, is the driver |

## One replayable (2,1) disagreement

Faults (scoring only): `X@(1,0) round 1` and `X@(2,1) round 1` (the second is the loss
site). True onset 1, **truth = 1**. Decisions: **thick = 1, thin = 0, diamond = 0,
whole = 1** — here the reference is correct and the diamond misses: an X-error at (1,0)
(on the `Z_L` support) at round 1 is pruned and lies outside the (2,1) star, so the
3-check edge diamond cannot pair it. (In `results/conjugate_E_frame.json → example`.)

## Replay

```sh
cd exploratory/reconsideration_witness/conjugate_edge_2026-11-16/src
python3 conjugate_run.py        # run E_frame at (2,1), cold restart, 3-way summarize
```

- **Baseline (bulk):** `09a79c1`. **Z-open edge:** `93cf914`. **Conjugate protocol:**
  `9832cd1`. **Conjugate result:** this commit.
- Reuses `correction_2026-11-14/src/model.py` unchanged; `conjugate_run.py` only relocates
  the loss to (2,1) and passes `report={'site':[2,1],'onsets':[1,2],'deadline':4}`.

## Scope and limits

Single distance-3 conjugate edge site. No corner, no distance-5, no later deadline or
broader fault bound. Carries forward Astra's bounds/caveats (bounded model, deadline-
snapshot payloads not temporal peaks, reference agreement distinct from truth). The new
fact is the clean separation: **at d=3, the re-judgment degradation at an edge is set by
bracket size, not by which sector's arm is open** — which reframes any larger-distance or
toward-the-corner question as primarily about the number of local checks retained.

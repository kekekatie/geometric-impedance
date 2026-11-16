# Distance-3 geometry series: bulk–edge–edge–corner (handback)

**Result: the corner overturns the bracket-size story. The two-check corner (2,2) — the
*fewest* local readings, 4 — is the second-best site, with weighted disagreement 0.0083%
(~2× bulk), far better than either six-reading edge (0.0428% and 0.097%). So the local
diamond's sufficiency is NOT a simple function of bracket size: the asymmetric
mid-boundary edges are the pathological sites, while the maximally-isolated corner is
nearly as good as the central bulk.** Re-judgment difficulty is non-monotonic in the
number of local checks.

Built on the conjugate-edge run `9564067` (which carries the bulk baseline `09a79c1` and
both edge runs), reusing Astra's corrected E_frame `model.py` **unchanged** (only the
report site differs). Frozen corner protocol `351945b`, committed before this run.

## The 4-Way distance-3 geometry table (corrected E_frame; each site vs its own thick)

| site | star arms | local readings | thin disagree | **diamond disagree (raw)** | **weighted ref agreement** | weighted ref disagreement | diamond truth accuracy | thick truth accuracy |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| **bulk (1,1)** | 2Z + 2X | 8 | 3,433 | 341 | 0.999962 | **0.0038%** | 0.995891 | 0.995901 |
| **edge (1,2)** | 1Z + 2X | 6 | 3,280 | 896 | 0.999572 | **0.0428%** | 0.995523 | 0.995666 |
| **edge (2,1)** | 2Z + 1X | 6 | 2,545 | 837 | 0.999030 | **0.0970%** | 0.996618 | 0.996625 |
| **corner (2,2)** | 1Z + 1X | 4 | 2,095 | **753** | 0.999917 | **0.0083%** | 0.996598 | 0.996629 |

**diamond-right / reference-right** (who was correct when diamond and thick disagreed):
bulk 123/218 (36%), edge(1,2) 301/595 (34%), edge(2,1) 387/450 (46%), corner 237/516
(31%). Diamond payload bits max: bulk 66, edges 61, corner **56** (the corner archive is
smaller still — the loss touches only 2 checks). Query readings: 8 / 6 / 6 / **4**.

## What the series shows

- **Non-monotonic in bracket size.** Ordering by weighted disagreement:
  **bulk (0.0038%) < corner (0.0083%) ≪ edge (1,2) (0.0428%) < edge (2,1) (0.097%)**.
  The site with the *fewest* local checks (corner, 4) is second-best; the worst sites are
  the three-check *edges*. "Fewer local checks → worse re-judgment," which the conjugate
  run seemed to support, is refuted by the corner.
- **It is the mid-boundary edges that are hard, not the smallest bracket.** The corner is
  ~2× bulk; the edges are 11–26× bulk. A loss at the maximally-isolated corner interacts
  with little logical-relevant pruned structure outside its small diamond, so two checks
  suffice; the asymmetric edges sit amid more such structure.
- **Hypothesis, not conclusion (the confound stands).** Each site moves the loss *and*
  changes the neighbourhood *and* changes the ensemble, so this does not isolate a single
  cause. The clean, robust fact is the non-monotonicity; a plausible mechanism — local
  sufficiency is governed by how much logical-relevant pruned information lies *outside*
  the diamond, which depends on position, not just check count — is a hypothesis for
  distance-5 to test, not something these four points establish.
- **Correctness ≠ agreement, throughout.** At the corner the diamond's truth accuracy
  (0.996598) essentially equals its reference (0.996629); the extra disagreements are the
  diamond and the soft reference splitting on hard near-boundary histories, and on 31% of
  them the diamond is the one that is right.

## Frozen-prediction scorecard (K1–K5)

| | prediction | verdict |
|---|---|---|
| K1 | corner query reconstructs 4 old values | **HELD** (positions (6,1),(6,2),(7,1),(7,2)) |
| K2 | whole-archive == thick | **HELD** (0 disagreements; posteriors within 1e-12) |
| K3 | thin+diamond fewer disagreements than thin alone | **HELD** (753 < 2,095) |
| K4 | cold fresh-process restart reproduces every decision | **HELD** (272,512 roundtrip checks 0 mismatches; 4 cold processes, max prob Δ = 0.0) |
| K5 | **open:** does local disagreement grow again at the corner? | **RESOLVED — it does NOT**; the corner (0.0083%) is far below both edges, refuting the bracket-size trend |

## One replayable corner disagreement

Faults (scoring only): `X@(0,0) round 0` and `X@(0,0) round 4` on the corner (0,0),
with the loss at (2,2). True onset 1, **truth = 0**. Decisions: **thick = 1, thin = 0,
diamond = 0, whole = 1** — here the full-record **reference is wrong (1)** and the local
diamond is **right (0 = truth)**. (This is the same `X@(0,0)` round-0/round-4 pattern as
the historical bulk example, now with a corner loss; it is one of the 237 corner
diamond-right cases. In `results/corner_E_frame.json → example`.)

## Replay

```sh
cd exploratory/reconsideration_witness/corner_2026-11-16/src
python3 corner_run.py           # run E_frame at (2,2), cold restart, 4-way summarize
```

- **Baseline (bulk):** `09a79c1`. **Edge (1,2):** `93cf914`. **Edge (2,1):** `9564067`.
  **Corner protocol:** `351945b`. **Corner result:** this commit.
- Reuses `correction_2026-11-14/src/model.py` unchanged; `corner_run.py` only relocates
  the loss to (2,2) and passes `report={'site':[2,2],'onsets':[1,2],'deadline':4}`.

## Scope and the distance-5 question

Single distance-3 corner site; four points total (bulk, two edges, corner), each with the
site moved — a mapped survey, not a controlled sector/size isolation. Carries forward
Astra's bounds/caveats. The natural distance-5 question (Sol): **what changes when the
quilt gets bigger while the missing tile still has four neighbours?** — i.e. a bulk-like
(four-check) site on a larger patch, which these d=3 points cannot answer but now clearly
motivate, since the pattern here is about *position*, not check count alone.

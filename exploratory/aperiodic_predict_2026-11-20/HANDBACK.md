# Prospective route prediction — handback

Branch `claude/aperiodic-predict-2026-11-20`, forked from the decoder pilot `cf73715`.
**Prediction commit (pencil mark, frozen before any decode): `9062464`.** Result commit:
this one. Geometry generator + decoder engine reused unchanged; no tiling/geometry/decoder
source edited.

- Prediction: [`PROTOCOL.md`](PROTOCOL.md) + `results/prediction.(png|svg)` + selected
  patch JSONs & `*_certificate.json`, all in `9062464`.
- Result: [`results/result.png`](results/result.png) (+ `.svg`),
  [`results/paired_results.json`](results/paired_results.json),
  per-edge checkpoints folded into it; cap panel `results/caps_pairs.json`.
- Replay: `cd src && PYTHONPATH=. python3 select_and_export.py && python3 predict_fig.py && python3 paired_run.py && python3 analyse_pairs.py && python3 predict_fig.py result && python3 caps_pairs.py`

## The prediction, and the verdict

**Prediction (geometry only, committed first):** on a fresh AB/Penrose patch the full
archive raises tie-aware truth more at a loss edge on a **shortest X-logical route** than
at a matched off-route edge — `Δ_patch = G(on) − G(off) > 0`, `G = thick − thin` (pp).

**Verdict: holds on all three pairs, both tilings.** Exhaustive zero-/one-/two-fault
evaluation, identical configurations across each pair and all four arms, 385,648
histories per edge. The paired interval is a cluster bootstrap over the shared
ordinary-fault configurations (each config's 8 variants kept together, B=10,000); it
measures **fault-sampling uncertainty on a fixed patch**, not geometric generality.

| patch | match quality | on-route G (pp) | off-route G (pp) | **Δ = G(on)−G(off)** | 95% paired CI | diamond−thin at on-route |
|---|---|---:|---:|---:|---|---:|
| **AB_1** | deg ≠ (5,5 vs 3,5), dist = | e14 **+0.10310** | e8 +0.00312 | **+0.09998** | [+0.029, +0.558] | +0.00124 |
| **Penrose_1** | **deg = (3,6), dist =** (clean) | e14 **+0.12229** | e13 +0.00301 | **+0.11928** | [+0.031, +0.699] | +0.00072 |
| **Penrose_2** | deg = (3,5), dist Δ1 | e4 **+0.07235** | e0 +0.00319 | **+0.06916** | [+0.006, +0.484] | +0.00035 |

Every Δ is positive and every CI excludes zero. The on-route edge is 22–40× its matched
off-route partner — a conspicuous, S6-like bright spot sitting on a shortest X-route. The
intervals are wide because the archive advantage is carried by a small number of
high-impact fault configurations, so resampling configs has heavy-tailed variance; the
load-bearing fact is that the lower bound is positive at all three. The confound Astra
flagged is addressed: **Penrose_1 is a clean match** (identical endpoint degrees and
boundary distances), and the effect is as strong there as anywhere — so it is **not** an
endpoint-degree artifact.

The full off-route map confirms the specificity: the other eligible edges of each patch
sit at 0.0007–0.0041 pp (AB_1 e15 +0.00288, e16 +0.00409; Penrose_1 e2 +0.00205; Penrose_2
e1 +0.00070), i.e. near zero, exactly as the five off-logical square edges did in the pilot.

## What the eight readings recover — the clean miss

At **every** fresh on-route edge, `diamond − thin` is tiny (+0.0004 to +0.0012 pp) while
`thick − thin` is +0.07 to +0.12 pp, so `thick − diamond` ≈ the whole gain: **the eight
local readings recover essentially none of the on-route archive benefit.** This is the
**opposite** of the pilot's square S6, where the local bracket recovered nearly all of it.
The honest reading: on these aperiodic patches the route's logical information is
**delocalized along the shortest X-route**, outside the four checks incident to the lost
edge — the full archive sees it, the local onset-lip bracket does not. (Hypothesis, not
established by three sites: it may be that S6's benefit was local because its loss sat on a
*short, locally-supported* logical, whereas a generic shortest route threads across the
patch.) So the picture has a hit and a miss, both sharp: **the bright spot follows the
route (archive), but the local skin does not follow it there.**

## Checks

`whole == thick` labels and posteriors: **0 disagreements**; serialized restart ==
direct decode: **0 mismatches**, over 192 sampled restarts/edge across all 10 edges
(≈3.86M histories total). Adapter verified on each fresh geometry (ranks, commutation,
distance 3, 4-check/8-coord queries) via `*_certificate.json`; the pilot S6 baseline
replays bit-for-bit through the untouched engine. All three patches are fresh (disjoint
from the discovery cuts); S6 regression (unique on-route eligible among the original 18)
reproduced (`results/s6_regression.json`).

## Cap sensitivity

Preselected, outcome-independent panel on the six pair edges (all zero-/one-fault configs
+ a seeded 120 two-fault sample, baseline-agreeing histories included), `results/caps_pairs.json`.
The panel is k≤1-heavy, so its per-edge `G` is larger than the population `G` of §above;
the point is the on/off **contrast** and its **stability across caps**, not the level.

**Frame cap (3,3) → (4,3):** the on-route benefit is stable; the off-route edges stay at
exactly zero; frame-prefix coverage is complete (prefix-absent = 0 at both caps).

| edge | panel G (3,3) | panel G (4,3) | label flips | prefix-absent |
|---|---:|---:|---:|---:|
| AB_1 on e14 | +0.5655 | +0.5075 | 4 (cancel) | 0 |
| AB_1 off e8 | 0.0000 | 0.0000 | 0 | 0 |
| Penrose_1 on e14 | +0.5220 | +0.4640 | 11 (cancel) | 0 |
| Penrose_1 off e13 | 0.0000 | 0.0000 | 0 | 0 |
| Penrose_2 on e4 | +0.2320 | +0.2320 | 8 (cancel) | 0 |
| Penrose_2 off e0 | 0.0000 | 0.0000 | 0 | 0 |

Raising the frame cap changes the on-route benefit by ≤11% of its panel value (label flips
grow but cancel in the net), leaves every off-route edge at exactly zero, and introduces no
fallback-prefix effects. **The on > off contrast — hence `Δ_patch > 0` — is robust to the
frame cap at all three patches.**

**Marginal cap (w_dec = 4):** the `(3,4)`/`(4,4)` panels were **not completed** — their
per-edge 20.6M-row `w_dec=4` builds (~20 min each) were repeatedly interrupted by container
restarts, a run-environment limit, not a result. The one point that did complete before a
restart — AB_1 on-route e14 at `(3,4)` — gives panel `G = +0.551` vs `+0.566` at `(3,3)`
(0 flips), i.e. the marginal cap is also stable there. A full `w_dec=4` cap panel is left as
a follow-up to run in a stable environment.

## Plain-language answer, pointing at the pictures

**Did the bright spot follow the shortest route into AB?** Yes — the circled on-route edge
is the lone bright spot on the AB patch (+0.103 pp vs ~0.003 for every off-route edge).
**Into Penrose?** Yes, both times — most cleanly at Penrose_1, where the on- and off-route
edges have *identical* endpoint degrees and boundary distances and the on-route edge still
lights up 40× brighter (+0.122 vs +0.003). Penrose_2 is a smaller but clear hit (+0.072 vs
+0.003). **Where did the pencil mark miss?** Nowhere on the *route* prediction — three for
three. But there is a second, sharper miss worth seeing: **the eight old readings did not
recover the cost at any on-route edge** — unlike the pilot's S6. On a fresh aperiodic
patch the archive's advantage lives spread along the route, where the full record reaches
it but a local bracket of four checks cannot. The route predicts *where forgetting hurts*;
it does **not** promise that a local query can undo it.

## Scope

Bounded `(3,3)` decoder, bounded ≤2-fault ensemble (exhaustive), three fresh single
patches (AB yielded one non-overlapping cut, Penrose two). The paired CI is fixed-patch
fault-sampling uncertainty, not a claim about all patches. On-route = lies on ≥1 weight-3
X-logical support; the geometric selection and the prediction were frozen before any score
(`9062464`). A broader predictor study across many independent cuts, with boundary
proximity held fixed and the perpendicular-space coordinate brought in, remains future
work.

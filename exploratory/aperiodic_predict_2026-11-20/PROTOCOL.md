# Prospective route prediction — frozen protocol

**This file + the selected patches + certificates + the uncoloured circled figure are the
pre-registered prediction, committed before any fresh site is decoded.** Branch
`claude/aperiodic-predict-2026-11-20`, forked from the completed decoder pilot `cf73715`.
Geometry generator reused unchanged from `9c059c7`
(`aperiodic_qec_geometry_2026-11-19/pilot.py`, `certify.py`).

## The prediction

On a fresh Ammann–Beenker or Penrose patch, the full archive improves the decoder's
tie-aware truth score **more** at a loss edge that lies on a **shortest X-logical route**
than at a comparable edge off every shortest route. Operationally, with
`G(edge) = [thick − thin] weighted tie-aware truth, in percentage points`, and per patch

  Δ_patch = G(circled on-route edge) − G(matched off-route edge),

the directional prediction is **Δ_patch > 0**. On-route = the edge's lost qubit belongs to
**≥1 minimum-weight (weight-3) X-logical support**; off-route = it belongs to **none**.
Motivation (discovery data, not used here): in the pilot, square edge S6 showed
`thick − thin = +0.11431` pp while the five other `(4,4)` square edges were within
`0.00105` pp of zero, and S6 was the **unique** on-route eligible site across all 18 — a
regression check this run reproduces.

## 1. Geometric selection rule (frozen; geometry only, no scores)

Families **AB** and **Penrose**, aiming for two fresh, non-overlapping cuts each, one
preselected on/off pair per cut. Reuse the certified whole-tile construction,
`(dX,dZ)=(3,3)`, `k=1`, four-intact-check eligibility, **n = 21** data qubits.

- **Candidate cut:** `n=21`, distance `(3,3)`, ≥2 eligible edges, from the frozen disk-cut
  enumeration (24 nearest centres × aspects `{1,1.25,.8}` × angles `{0,π/8,π/4,3π/8}` ×
  `m∈[6,25)`), corner enumeration as the pilot; **disjoint** (face ids) from that family's
  discovery cut; hosting **≥1 on-route and ≥1 off-route** eligible edge.
- **Pair within a cut:** `(on,off)` minimizing in order (a) endpoint-degree mismatch
  (0 if sorted degrees equal else 1); (b) `|Δd_rough|+|Δd_smooth|` (graph distance of the
  edge's endpoints to the nearest rough / smooth arc vertex); (c) `−(on-route #supports)`;
  (d) `(on_edge_id, off_edge_id)` ascending.
- **Cut ranking / picking:** sort candidates by `(pair.a, pair.b, −on_supports, spec,
  corners)`; greedily take the top cut, then the next whose faces are disjoint from
  already-picked cuts and whose `(HX,HZ)` is not a duplicate, until two. **If a family
  yields fewer than two, report and proceed.**

Implemented deterministically in `src/geom_select.py` + `src/select_and_export.py`.
Imperfect matches are kept and labelled.

### Selection outcome (geometry; recorded with the prediction)

| patch | on-route edge (qubit) | off-route edge (qubit) | match | shortest X-routes | note |
|---|---|---|---|---|---|
| **AB_1** | e14 (q10), deg (5,5), #sup 2 | e8 (q6), deg (3,5) | deg ≠, dist Δ0 | 4 | degree mismatch (flagged) |
| **Penrose_1** | e14 (q10), deg (3,6), #sup 1 | e13 (q9), deg (3,6) | **deg =, dist Δ0** | 2 | clean match |
| **Penrose_2** | e4 (q4), deg (3,5), #sup 1 | e0 (q0), deg (3,5) | deg =, dist Δ1 | 1 | distance off by 1 |

AB yielded **one** non-overlapping fresh cut hosting an on/off pair (38 candidate cuts,
all mutually overlapping on faces); Penrose yielded two. All three certify as
`[[21,1]]`, `(dX,dZ)=(3,3)` (`*_certificate.json`), with 11 X-checks + 9 Z-checks (the
pilot's three were 10+10; both are valid `(3,3)` codes). The predicted (circled) edge is
the on-route edge; `results/prediction.(png|svg)`.

## 2. Paired test (carried over from the pilot)

Five rounds `0–4`, delayed report after round 4, shared unknown onset over `{1,2}`,
pre-report sparse archive, four arms (thick/thin/diamond/whole), `(w_frame,w_dec)=(3,3)`,
`p=1e-3`, tie-aware truth (½ on a `1e-12` tie). Scored observable: final X-error parity on
the patch's fixed certified `logical_Z` support. Adapter verified on each fresh geometry;
the saved S6 baseline is replayed as a regression check.

- `G = [thick − thin]` weighted tie-aware truth (pp); `Δ_patch = G(on) − G(off)`;
  prediction `Δ_patch > 0`. Both underlying gains reported.
- **Identical** ordinary-fault configurations and 8 onset/erasure variants for the two
  edges of a pair and across all arms. **Exhaustive zero-/one-/two-fault** evaluation of
  the marked pairs (feasible — only a handful of edges). If timing forces sampling the
  two-fault stratum, freeze the seed and size **from timing alone**.
- Paired uncertainty interval per `Δ_patch` by a **cluster bootstrap over the shared
  ordinary-fault configurations** (each config's 8 variants kept together), B=10,000. This
  measures **fault-sampling uncertainty on a fixed patch**, not geometric generality.

## 3. Recovery + checks + caps

Report `diamond − thin` and `thick − diamond` (signed, small negatives kept) beside `G`.
Verify `whole`-vs-`thick` labels and posteriors and report the serialized-restart count
and mismatches. Cap sensitivity: a **preselected, outcome-independent** paired panel
(all zero-/one-fault configs if feasible + a seeded two-fault sample), replayed at
`(3,3)`, `(4,3)`, `(3,4)` [+ `(4,4)` if feasible], **including baseline-agreeing histories**
so a disagreement first appearing at a higher cap is visible; if the panel carries too
little signal to judge stability, say so.

## 4. Handback

Committed pencil-mark prediction beside the measured archive-benefit map per patch (same
orientation + edge IDs, shared zero-centred colour scale, untested edges grey); a table
with one row per pair (matching quality, two gains, signed contrast). **Separate prediction
and result commit hashes.** End pointing at the pictures: did the bright spot follow the
shortest route into AB? into Penrose? where did the pencil mark miss, and what did the
eight old readings recover there — a miss shown as clearly as a hit.

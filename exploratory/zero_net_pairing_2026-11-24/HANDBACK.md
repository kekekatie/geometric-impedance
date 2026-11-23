# Are the zero-net-cost omission flips matched pairs? — handback

Branch `experiment/zero-net-pairing-2026-11-24`, cut from the sealed local-witness-omission
result `1922a7b`. Protocol frozen **before any flip list was examined** (`4d6b6ac`). The
corrected decoder and omission engine are imported unchanged; no sealed file is modified.

## For Katie, in plain words

When you drop one *endpoint* reading from the archive at Penrose_2's loss edge, the decoder
changes its mind on dozens of individual histories, yet the **total** truth score doesn't
move at all. We asked whether that exact zero is a lucky coincidence or a real symmetry. It
is a real symmetry. Those histories come in **twins**: two fault stories that leave the
decoder with the *identical* record — the same syndrome, so the same posterior and the same
decision — but whose *true* answers are opposite, because the two stories differ by exactly
the little weight-three logical loop that threads through the lost edge. So whenever dropping
the reading pushes one twin from right to wrong, it pushes the other from wrong to right, by
the same amount. Help one, hurt its twin, equally. On **Penrose_2 the twinning is perfect
and the net is exactly zero.** On **Penrose_1 it is almost perfect**: most of the 570-odd
flips are twinned, but a handful are not, and that small unpaired remainder *is* the tiny
`+0.00001844 pp` — so there the cost is near-zero, not exactly zero.

## Reproduction (step 2 — exact)

Re-deriving the committed Penrose_2 rows with the imported engine (385,648 histories/site,
bounded `(3,3)`, `p=1e-3`, tie-aware ½):

| check | flips | tie changes | lost (pp) | gained (pp) | net (pp) | committed |
|---|---:|---:|---:|---:|---:|---|
| X5 | 44 | 2 | 0.00020747 | 0.00020747 | 0.00000000 | matches exactly |
| X0 | 18 | 2 | 0.00008760 | 0.00008760 | 0.00000000 | matches exactly |

## The candidate symmetries tested

- **(a) erasure free-value swap, (b) onset swap** (and their combinations) — tested as exact
  lost→gained bijections keeping the ordinary configuration fixed. **None biject** for any
  check; the pairing does not act on the erasure variant alone.
- **(c) patch-graph automorphism fixing e4** — **not needed** (the record pairing below is
  exact without it), so not invoked.
- **(d) adding the on-route weight-3 X-logical to the total X-fault** — **this is the
  pairing.** Adding the weight-3 X-logical that threads the loss qubit (`{4,6,10}` on
  Penrose_2, `{1,10,17}` on Penrose_1) leaves every detector unchanged (a logical commutes
  with all stabilizers) but flips the scored Z-truth, so the two histories share an identical
  full record and every arm's decision/posterior, with opposite truth and opposite
  tie-aware credit. (A pure stabilizer shift leaves the decision *and* the truth unchanged —
  no movement — so it is not the mechanism.) We realise (d) by grouping movers on their exact
  detector record and verifying each opposite-truth pair's total-X-fault **symmetric
  difference is a weight-3 X-logical.**

## Per-check result

Lost/gained = credit-moving histories (`δ<0` / `δ>0`, tie-aware). "Record-paired" = exact
same-record, opposite-truth, equal-weight, opposite-`δ` pairs; "X-logical" = pairs whose
total-X-fault symmetric difference is a weight-3 X-logical.

| site · check | movers (flips+ties) | net (pp) | weight-matched | variant swap (a/b) | record-paired | X-logical diff | unpaired | verdict |
|---|---:|---:|:--:|:--:|---:|---:|---:|---|
| **Penrose_2 · X5** | 46 (44+2) | 0.00000000 | **yes** | none | 22/22 label pairs | **22/22** `{4,6,10}` | 2 ties (cancel, equal weight) | **structural pairing explains the zero** |
| **Penrose_2 · X0** | 20 (18+2) | 0.00000000 | **yes** | none | 9/9 label pairs | **9/9** `{4,6,10}` | 2 ties (cancel, equal weight) | **structural pairing explains the zero** |
| **Penrose_1 · X4** | 582 (570+12) | +0.00001844 | no | none | 279 pairs | 259/279 `{1,10,17}` | 24 of 582 | mostly structural; small genuine residue |
| **Penrose_1 · X6** | 584 (572+12) | +0.00001844 | no | none | 280 pairs | 260/280 `{1,10,17}` | 24 of 584 | mostly structural; small genuine residue |

Notes:
- **Penrose_2.** Every one of the 44 (X5) / 18 (X0) label flips is one half of an exact
  same-record twin differing by the single weight-3 X-logical `{4,6,10}` through the loss
  edge; the twin's credit is opposite and its weight equal, so the label flips net to zero.
  The 2 remaining movers per check are tie-status changes at `k=2` (one lost, one gained, so
  equal weight) and also net zero. The whole zero is accounted for.
- **Penrose_1.** The **entire** `+0.00001844 pp` lives in the label flips (the 12 tie-movers
  net exactly zero). Most flips twin by the weight-3 X-logical `{1,10,17}`, but `24` of the
  `582`/`584` movers are left unpaired (and `~20` further pairs differ by a weight-4, not
  weight-3, support). That unmatched remainder is the genuine, nonzero residue:
  `weight-matched = False`. So Penrose_1 is **near-zero by the same twinning, not exactly
  zero**; nothing maps every lost history to a gained one.

## Verdict

- **Penrose_2 (e4), X5 and X0: "structural pairing explains the zero."** The zero is the
  weight-3 X-logical degeneracy of the loss edge, candidate (d).
- **Penrose_1 (e14), X4 and X6: "no exact pairing found" — near-zero, not zero.** The same
  X-logical twinning covers the bulk of the flips, but a small unpaired residue carries the
  real `+0.00001844 pp`.

The reason endpoint (X) omissions sit at (or near) zero while adjacent-face (Z) omissions do
not: the loss edge is **on-route** (its qubit lies on a weight-3 X-logical), and that logical
is an X-type operator. Omitting an X endpoint perturbs decisions along exactly the X-logical
whose two cosets are twinned by an identical record — so the perturbation is self-cancelling.
This is the same on-route logical that drove the route prediction.

## Scope

Bounded `(3,3)` decoder, `k ≤ 2`, `p = 0.001`, the frozen sites **Penrose_2 (e4)** and
**Penrose_1 (e14)** only; corrected addresses from the fresh-site audit. Full per-flip records
(configuration, onset, erasure free-value, weight, intact/omitted labels and posteriors, true
outcome, direction) are in `results/flips_*.json`; the pairing analysis in `results/pairing.json`.
Replay: `python3 flips.py && python3 pairing.py`.

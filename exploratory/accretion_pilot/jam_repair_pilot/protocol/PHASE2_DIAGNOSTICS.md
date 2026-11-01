# Phase 2 — pre-committed geometry diagnostics

**Status: pre-committed.** The three diagnostics below, their gauge, units,
normalisation and empty-region handling are fixed here *before* their
relationship to jam outcomes is computed. Frozen 2026-11-01.

This is a **descriptive** comparison of the paired A/B fork states. It is not a
predictive model, not a causal claim, and not a hypothesis test. The 11 B jams
and 2 streams-per-fork are **not** independent trials; results are reported as
paired A−B differences grouped by fork. The earlier **+0.749 inward-alignment**
statistic is from a *different measurement population* (the 24-world
corner-response catalogue, final-patch completed-corner force directions) and is
**not** used here as an explanation of the jam asymmetry.

## Objects kept distinct (per the task)

- **True layer acceptance windows** `WIN[rk]` — the fixed Penrose pentagons per
  layer rank. Not measured per fork; the fixed reference.
- **Planar compatibility region F** — `Sl.region(Sl.constraints(tiles, rank))`,
  the clipped offset polygon derived from the 5D lift. *This is what the
  diagnostics below use.*
- **Finite sampled hulls** — `perp_map.depths`' per-layer convex hulls of the
  actually-present perp addresses. Used only for the descriptive depth proxy
  (D3b), never conflated with F or with WIN.
- **Birth-state vs after_first** — birth = the common saturated fork state `S*`;
  after_first = `CD.after_first(S*, option, rank)` (commit one candidate, one
  patient step). Every diagnostic states which it uses.

## Gauge (common to D1–D3)

All lifts use `M.lift` over rhombus legs; layers are the four consecutive
`k.sum()` values mapped to ranks 0–3 by `Sl.rank_of`. The offset region lives in
the fixed `[-50,50]²` box clipped by the true windows `WIN`. F is computed in
the fork's own `S*`-anchored gauge (the same gauge the closure used for
`C^A`,`C^B`), so A and B are directly comparable within a fork. Area and length
are in **perp/offset-space units** (dimensionless; the perp map uses
`ζ^{2j}` with unit edge length), not physical tile units.

## D1 — retained compatibility area (birth and after_first)

- `F0 = area(F(S*))` — birth wiggle-room.
- `FA = area(F(after_first(A)))`, `FB = area(F(after_first(B)))`.
- Birth-normalised retained fraction `pA = FA/F0`, `pB = FB/F0` (dimensionless).
- **Empty region → area 0** (a legitimate zero, reported as 0, distinguished in
  text from "not measured"). If `F0 = 0` the fork is degenerate and `p` is
  reported as `null`.
- Paired report: `FA−FB`, `pA−pB`, grouped by fork.

## D2 — compatibility-region centroid displacement

- `cen(F)` = area-weighted centroid of the F polygon (offset-space point).
- `δA = ||cen(F(after_first(A))) − cen(F(S*))||`,
  `δB = ||cen(F(after_first(B))) − cen(F(S*))||` (offset-space length).
- Interpretation: how far committing each option shifts the allowed-offset blob.
- **Empty after_first region → δ = null**, counted separately (not 0).
- Paired report: `δA−δB`, grouped by fork.

## D3 — local directional / in-window imbalance

Two sub-measures, both after_first, both per option:

- **D3a eccentricity** `eA, eB`: distance of `cen(F(after_first(opt)))` from the
  centroid of the fixed window stack centre (mean of `WIN` pentagon centres over
  the 4 ranks), normalised by the mean window circumradius → dimensionless in
  `[0, ~1]`; →1 means the retained offset sits near a window wall (wall-near).
  Empty region → null.
- **D3b depth proxy** `dA, dB`: mean `perp_map.depths` hull depth of the newly
  placed candidate tile's vertices on the after_first patch (depth∈[0,1],
  1=central/deep, 0=hull-boundary/shallow; convention stated). This is the
  "depth stands in for local pattern" descriptive comparison. Layers with <10
  points have no hull → that vertex contributes null; a tile with no depthed
  vertex → null.

## Descriptive option-type comparison

Also recorded per option (not a diagnostic, a label): the decorated **shape**
(type 0 = 36-72-72, type 1 = 108-36-36) of the committed candidate tile, and
whether the fork is one where B later jammed (in either stream). Reported as a
contingency, descriptively.

## Reporting

For each of the 22 forks: `F0`, and per option the tuple
`(F, p, δ, e, d, shape)`; then paired A−B differences. Forks are grouped as
**B-jammed** (world in the 11-jam set for ≥1 stream) vs **B-survived**. We report
medians and the paired-difference distribution; we do **not** fit a model or
quote a p-value as if the streams were independent, and we draw no causal arrow.

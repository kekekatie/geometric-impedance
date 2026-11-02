# Protocol deviations (dated)

Deviations from `PROTOCOL.md`, recorded rather than edited into the original.

## 2026-11-02

- **Region enumeration was exhaustive at size ≤ 8, below the cap.** All connected
  regions (edge-adjacency) up to size 8 seeded at the dead-site and witness
  vertices number **12248**, below the frozen cap of 50000. The cap was therefore
  not binding and the size-≤-8 enumeration is **exhaustive (not truncated)**. No
  limit was enlarged.

- **Obstruction characterisation searches beyond the size-8 region limit — as
  analysis, not as a repair search.** Part 3 reports a constraint-level lower
  bound (minimum facet-drop) and a faithful greedy vertex-engulfment upper bound
  for restoring feasibility. The greedy engulfment grows past 8 tiles (it reaches
  41). This measures *how distributed the obstruction is*; it is not a candidate
  repair and does not enlarge the frozen move class (connected region, size ≤ 8).
  Recorded openly.

- **Performance-only optimisation.** In Part 3, a region whose engulfed vertices
  do not change any binding constraint has an exterior identical to the full band
  and is infeasible by monotonicity; the LP is skipped for such regions. This is a
  pure speed-up and changes no verdict (verified: controls pass, and the few
  regions that do change binding constraints are all classified by LP).

- **Part 4 replacement search ran on flip-hexagon regions as concrete instances.**
  Part 3 permitted **0** regions, so the replacement search had nothing to carry
  forward. To exercise and validate the full enumeration + order-independent
  validation + scoring pipeline (and to make the null concrete), the search was
  run on the 15 flip hexagons near the dead sites — connected 6-tile regions
  inside the frozen move class. No region outside the move class was searched; no
  matching rule was relaxed.

- **Parts 5 and 6 were not fully reached.** No candidate restored compatibility,
  so there was no qualifying post-repair candidate. Part 5 therefore scored the
  **pre-repair baseline** readout only (the evaluator apparatus was validated);
  Part 6 (resume construction) was **not invoked** (nothing qualified). Both are
  documented rather than skipped silently.

## Notes

- No four-flip limit was imposed (none is established).
- The frozen engine, frozen reader, historical hypotheses, and all existing
  outputs are unchanged. Historical A/B data was read only by the Part-5
  evaluator, never by candidate generation or selection.

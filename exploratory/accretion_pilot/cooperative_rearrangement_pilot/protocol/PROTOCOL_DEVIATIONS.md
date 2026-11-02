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

## 2026-11-03 — reconciliation after the independent Codex audit

The audit (`audit/cooperative-rearrangement-2026-11-03`, commit `e7ff8ff`) found
gaps between the frozen `PROTOCOL.md` wording and the historical implementation.
These are recorded here (the frozen protocol is NOT rewritten as though it had
specified the actual values); none changed a scientific verdict in this study.

- **Region cap.** `PROTOCOL.md` lists a 200,000 max-regions cap; the earlier
  deviation note and the code use 50,000. The seeded size-≤-8 family has only
  **12,248** regions, so the cap never bound and the enumeration is exhaustive at
  size ≤ 8. (`part3_necessary.REGION_CAP = 50000`.)
- **Region ordering.** The order is size-first but **not** lexicographic within a
  size (the frontier BFS order). Since **no region was permitted**, the
  deterministic-selection ordering never affected any choice or the conclusion.
- **Replacement caps.** `PROTOCOL.md` lists 2,000 completed solutions and
  "depth ≤ 2 × region size"; the historical hex enumerator used a **256**-solution
  cap (Part 4) and a **hardcoded depth 8**, and the "200,000 search nodes" limit is
  not implemented. The audit's uncapped independent search reached at most depth 7
  and recovered the **same complete candidate sets** (2 geometric dissections, 128
  decorated fillings per hexagon), so these caps omitted no alternative here.
- **Truncation reporting.** `part4_search` infers truncation from the
  **deduplicated** returned solution count vs the cap, which can under-report
  truncation; this is now stated in the Part-4 output `truncation` block, and the
  audit's uncapped search is the authority on completeness for the 15 hexagons.
- **Dormant general search.** `PROTOCOL.md` describes a general permitted-region
  replacement search; only the flip-hexagon case is implemented. Because Part 3
  permits **0** regions, this path is dormant. `part4_search.permitted_region_guard`
  now reports it as **unsupported** and the run **stops clearly** if a future
  Part-3 ever permits a region outside the implemented shapes, rather than
  returning a spurious exhaustive negative. Building that general search is **out
  of scope** for this maintenance task.
- **Minimum-row-deletion.** The historical `min_facet_drop` returned the first
  feasible four-row set; the maintained version checks **every** subset at each
  cardinality and tracks `unresolved`, so it does not claim a minimum past an
  unresolved smaller-cardinality check. (No subset was unresolved; minimum four is
  certified.)
- **Shortcut subtotals are not a scientific requirement.** The Part-3 path split
  (no-engulfment / engulfed-nonbinding / LP) depends on exact-dict equality of
  aggregate coefficients and is environment/last-bit sensitive (this environment:
  9130 / 2724 / 394; the audit's: 9130 / 2793 / 325). All **final verdicts** agree
  (12,248 infeasible). The split is now labelled diagnostic in the output.

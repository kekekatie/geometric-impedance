# Protocol — cooperative rearrangement pilot (frozen before searching)

*2026-11-02. Bounded exploratory pilot, no preferred outcome; a negative or
unresolved result is equally acceptable. Frozen before running the search.
Deviations are recorded in `PROTOCOL_DEVIATIONS.md`, not edited in here.*

**Central question.** Can a finite rearrangement in the retained boundary band
restore projection-window compatibility and permit further construction, while
leaving the original historical A/B choice uniquely readable?

**No matching rules are relaxed.** Legality is decided only by the frozen engine.

## Source and scope (frozen)

- Repository `kekekatie/geometric-impedance`. Experimental branch
  `claude/cooperative-rearrangement-pilot`, directory
  `exploratory/accretion_pilot/cooperative_rearrangement_pilot/`.
- **Starting commit** `53692c20c68a03a96b1e682ad8c90e60b764df21` (audit branch
  `claude/jam-compatibility-diagnostic-audit`), confirmed latest reviewed.
- **Frozen engine / reader** imported read-only from
  `84130b97f5044197392e72cd53e0e71f81b043f3`. Not modified.
- **Case:** world 7, option B (shape 1), stream index 0, at the recorded jam
  (step 23). Retained-state input exported to `input/retained_state.json`
  (search-visible) and `input/evaluator_historical.json` (evaluator-only).

## Move class (what may change, what is fixed)

- **May change:** the interior geometry and decorations of a single **connected
  region R** of retained-band tiles (edge-adjacency), replaced by frozen template
  tiles covering the identical footprint.
- **Fixed:** every tile **outside R**; the **true outer growth frontier**; the
  **inner (pruning-exposed) boundary**; the **geometric footprint** (coverage) of
  R; R's **exterior interface** (the edges where R meets the retained exterior).
- This is a **fixed-boundary** move class: it **excludes** any repair that would
  move either boundary. A null result is a statement about this move class only.

## Connected replacement regions

- Adjacency: two half-tiles are adjacent iff they share a full edge (both own it).
- A region is an edge-adjacency-connected set of band-tile dkeys.
- **Seeds:** tiles incident to a dead-site vertex, and tiles incident to a
  compatibility-witness origin vertex (witnesses computed from the frozen
  constraints of the jammed band — a geometric property, **not** historical).
- **Ordering:** by region size ascending, then lexicographically by the sorted
  tuple of tile dkeys (deterministic).

## Bounded limits (conservative; fixed before any result)

| limit | value | rationale |
|-------|-------|-----------|
| max region size | **8 tiles** | > the audited single-flip hexagon (6 tiles) |
| max regions enumerated (Part 3) | **200000** | necessary-condition pre-filter is cheap |
| max regions carried to replacement search (Part 4) | **64** | first-ranked permitted regions |
| max completed solutions per region | **2000** | |
| max search nodes per region | **200000** | |
| recursion depth per region | **≤ 2 × (region tile count)** | |
| allowed replacement tiles | frozen `L.TEMPL` (shapes 0/1, all orientations) | engine's own atlas |
| runtime budget | ~10 min total | one bounded pilot |

**These limits are not enlarged after seeing a null result.** No four-flip limit
is imposed (no universal four-flip bound is established). Deviations are recorded.

## What counts as exhaustive within a region

All completed tilings of R's footprint by allowed tiles that preserve coverage
(no gaps/overlap) and the fixed exterior interface, enumerated up to the node/
solution caps, with **no rejection of a completed filling merely because an
intermediate partial filling violated a vertex-star condition** (the audited
order-independent completed-patch validator is used instead). "Exhaustive" holds
only if the caps were **not** hit (otherwise the region is reported **truncated**).

## Necessary condition before searching a region (Part 3)

For region R, retain every tile outside R and compute the compatibility
constraints supplied by those unchanged tiles **under a consistent gauge** (the
band's rank map). A vertex's constraint is dropped **only if every incident band
tile is in R** (fully engulfed); a vertex with any incident tile outside R still
supplies its constraint. Classify the exterior region with the **box-independent**
diagnostic (box-50 certifier **and** a box-free Phase-I LP):

- exterior **infeasible** (both agree) → **reject R**: changing only R cannot
  remove that contradiction.
- exterior **feasible** (both agree) → R is **permitted** to the replacement
  search (permission, not proof a replacement exists).
- otherwise → **unresolved** (reported as such, never as infeasible).

Witnesses guide seeding but we do **not** assume a single witness, that a repair
must change both sides of a witness, or that removing one witness resolves the
whole contradiction.

## Scoring (Part 5) — three axes kept separate, frozen reader unchanged

For each fully-legal completed candidate: (1) compatibility-region feasibility;
(2) candidate counts at the original dead sites **and** all true-frontier sites;
(3) frozen-reader geometric reconstruction; (4) the original A/B readout in the
five categories (uniquely correct / uniquely wrong / ambiguous /
empty-incompatible / reader-failure). The frozen reader and the original
historical hypotheses are unchanged; the reader receives only candidate retained
geometry and the historical hypotheses — never archived lifts or deleted tiles.
Reader coordinate limits are reported as limits, not as memory loss. A candidate
is selected for continuation by the frozen geometric rule (minimal sorted new-tile
dkey tuple), **not** by its A/B outcome.

## Resume construction (Part 6) — only after a qualifying repair

If a candidate is fully legal, restores compatibility, and the frozen scheduler
can proceed, continue **that one** to the original step-44 horizon on the
retained-state engine. If the original scheduler randomness is not faithfully
recoverable, a fixed continuation seed is disclosed before running (and the result
is **not** called the original trajectory). No extension beyond step 44, no fresh
worlds, no matching violations.

## Controls and honesty

- **Rejection control:** R = ∅ (exterior = full band) must be infeasible; a
  deliberately atlas-breaking filling must be rejected.
- **Positive control:** the identity replacement of a region must be found and
  validated; a constructed configuration with a feasible exterior must be
  classified feasible.
- A legal **joint** rearrangement does **not** establish a **sequence of
  elementary moves**; the latter is claimed only if an explicit valid path is
  constructed and checked.
- Truncation and all search limits are recorded. A bounded null is labelled by its
  move class and limits; it is not a universal no-go theorem.

## Stop

Stop after this pilot — including if every tested region is ruled out by the
necessary condition before any replacement search (that is itself evidence about
how spatially distributed the obstruction is). No fresh worlds, no new physical
interpretation, no manuscript.

# PROTOCOL — can the skin's hidden address re-judge a dormant scar?

*Pre-registered 2026-11-09 (brief dated 2026-11-10), committed **before** any F(W + c) is
computed. For Katie / Fable / Astra. One small diagnostic on worlds already grown. None of the
four declared outcome classes is a failure. Nothing frozen is modified; the scar stays skipped;
nothing here feeds back into any constructor or scientific run.*

## Question

At the first dormant-query disagreement of the amber-lobe ablation, the reduced live skin's
**local matching rule** admits a candidate tile `c` that the full history rejects. The reader's
**hidden-address (perpendicular-space) test** is a different instrument (Dworkin & Shieh 1995):
a tile can pass local legality yet be incompatible with the hidden offsets the surrounding tiles
allow. We ask whether, for this query, the reader can **reject** `c` from the reduced state
alone — i.e. whether the shed "reason" is recoverable from the pattern the skin belongs to.

No outcome licenses a claim that the growing world *uses* its hidden address. The engine's rule
is local. This concerns what a **reader** can recover from the reduced state (the "accessible
with aid" rung), not autonomous use.

## Frozen components (unchanged)

- Engine, lift, reader pinned at `84130b9`. Audit commit `6c5269a`
  (`audit/amber-lobe-verification-2026-11-07`). Base continuation `19981c2`.
- Reader reached through its existing path: `readout_check.score(w, si, tiles)` builds the payload
  from any tile list and calls the frozen `skin_reader.read`. **Confirmed: appending `c` to a
  window's tile list needs no wrapper** — `tiles + [c]` is a valid reader input (see §Gate 0).
- Chebyshev margin: the formulation of `jam_compatibility_diagnostic/src/feas.py`
  (unit normals; maximise `r` s.t. `n·x − r ≥ c`; box `[-50,50]`; `TOL_R = 1e-9`). We **replicate**
  this LP in `address_requery.py` rather than importing `feas.py`, to avoid pulling in its
  `study_common` dependency chain; the system solved is identical (same constraints `n·x ≥ c`).

## Recorded corrections (repository wins)

1. **Astra's amber-lobe work is now on GitHub** (it was not at the previous session). Branches
   `experiment/amber-lobe-ablation-2026-11-06` and `audit/amber-lobe-verification-2026-11-07`.
2. **Caches are external, not committed.** The `jam/verify/trace` base caches and the per-step
   `*-states.pkl` are rebuilt here into scratch dirs via `audit_2026-11-05/observe.py`
   (base cache) then `amber_lobe_ablation_2026-11-06/src/run_continuation.py` (states). The
   amber scripts cache trial JSON into their committed `results/` dir and short-circuit if present,
   so recomputation is forced by repointing `common.RESULTS` to a scratch dir; **no committed
   file is modified**.
3. **Fork-cache SHA differs by environment.** The rebuilt fork cache serialises to
   `7d766af7…` here vs `b0d8e0d4…` in the amber run (Linux/NumPy/pickle vs the recorded Windows
   build). Content faithfulness is certified by Gate 0 reproducing the exact query and the reader
   gate, not by the pickle hash.
4. **`GRID` is `scar_continuation_pilot/archive_free_2026-11-04/src/readout.py`**; its
   `window`, `centroid`, `edge_components`, `HALFWIDTHS = [π/8, π/4, π/2, 3π/4]` are used verbatim.
   Widest standard half-width = `3π/4`.

## Gate 0 (both reproduced before this protocol was committed)

- **Query.** For w7-s0 r2 the first dormant-query disagreement is at **step 35**, pinned edge
  `e = [(0.628274, -0.079527), (0.640786, -0.062306)]`, reduced menu = one tile
  `c = (1, (0.628274,-0.079527), (0.640786,-0.062306), (0.640786,-0.096748))`, full-history menu
  empty. This matches `amber_lobe_audit_2026-11-07/independent_query.json` exactly.
- **Reader gate.** The original full-band 528-window native grid reproduces **111 B / 64 ambiguous
  / 353 empty / 0 A** (regenerated here with `common.RESULTS` repointed).

## Instances (correlated; never independent trials)

| label | world,stream | radius | first-disagreement step | scar edge | candidate `c` |
|---|---|---|---|---|---|
| **primary** | w7-s0 | 2S | 35 | edge-A | c-A |
| **replicate** | w7-s1 | 2S | 35 | edge-A | c-A |
| secondary | w7-s0 | 1S | 26 | edge-A | c-A |
| secondary | w7-s0 | 3S | 37 | edge-A | c-A |
| secondary group-3 | w15-s0 | 1S | 42 | edge-B | c-B |
| secondary group-3 | w19-s0 | 1S | 42 | edge-B | c-B |
| secondary group-3 | w28-s0 | 1S | 42 | edge-B | c-B |

edge-A = `[(0.628274, -0.079527), (0.640786, -0.062306)]`, c-A = type-1 triangle
`(…, (0.640786, -0.096748))`. edge-B = `[(0.489517, 0.124612), (0.502029, 0.107391)]`, c-B =
type-1 triangle `(…, (0.502029, 0.141833))`. The w7 radii share one physical scar; the group-3
cases share another. **Report as correlated, not independent.** `c` is fixed as the first
reduced-menu candidate (in `D.candidates` enumeration order) absent from the full-history menu;
here each reduced menu is a single wrongly-admitted tile.

## Windows (fixed here; tile lists committed in `protocol_windows.json`)

For a case's reduced band at its first-disagreement step (`m['tiles']`), with
`cen = GRID.centroid(band)` and `ang = atan2(mid(e) − cen)`:

- **Primary window** `W`: the edge-connected component (via `GRID.edge_components`) of
  `GRID.window(band, cen, ang, 3π/4)` that contains `e`'s endpoints (largest if `e`'s endpoints
  fall in the largest). Primary `|W|`: w7-s0/s1-r2 = 312, w7-s0-r1 = 107, w7-s0-r3 = 404,
  group-3-r1 = 161.
- **Window ladder** (secondary): the same component rule at each other standard half-width
  (`π/8, π/4, π/2`), plus the **whole live skin** (all band tiles).

Every window's exact tile-key list and SHA-256 are committed in `protocol_windows.json` (the
primary SHA-256 prefixes are w7-s0/s1-r2 `823ab76fabcf`, w7-s0-r1 `aea61180900c`, w7-s0-r3
`0a3d15e3aeed`, group-3 `8941d4fbf41e`). `address_requery.py` recomputes each window by the rule
and **asserts the SHA matches** before computing any F.

## The test (per window, per convention)

Let `F(T)` be the frozen reader's compatibility region for tile list `T`
(`skin_reader.read` → polygon area and half-plane constraints). Compute `F(W)` and `F(W + c)`.

- **Reader statuses.** If `read` returns a status other than `reconstructed`, record
  **UNRECONSTRUCTIBLE** (distinct from UNDEFINED).
- **Emptiness, per convention.** *Open* (the reader's native rule): `F` non-empty ⟺ polygon
  area `> 1e-12`. *Closed*: `F` non-empty ⟺ the half-plane system is feasible as a closed region,
  i.e. Chebyshev `r ≥ −TOL_R` (a point/segment contact counts). Never merge the conventions.
- **Margin.** Record, for `F(W)` and `F(W + c)`, the polygon area and the Chebyshev radius `r`
  (and the smallest non-empty area seen), so the size of `c`'s effect is visible.
- **Witness.** If `F(W + c)` is empty, report a minimal infeasible subset of **≤ 3** half-plane
  constraints (2-D Helly), and, for each, the retained tile(s) whose lifted vertex supplies it
  (from the reader's returned per-vertex lift). Those tiles are where the reason now lives.

### Classification (per window, per convention)

- **UNRECONSTRUCTIBLE**: `F(W)` (or, after the ADMIT/REJECT branch, `F(W + c)`) is not reconstructed.
- **UNDEFINED**: `F(W)` is empty — the skin there has no consistent address; the test is silent.
- **REJECT**: `F(W)` non-empty and `F(W + c)` empty.
- **ADMIT**: both non-empty.

### Candidate lift (step 2)

Before the test, lift `band ∪ {c}` with the frozen `perp_map` lift anchored to the retained skin,
and record `c`'s Z5 address and whether a consistent lift exists. If it does not, record that as
the outcome and stop that case.

## Controls (same state and window sizes; all four reported)

- **True-tile control (interpretation gate).** At the primary step, for each tile the full-history
  scheduler places at the **next** step on a non-pinned (live) frontier edge whose endpoints are in
  the band, build the primary-half-width window centred on that edge's midpoint over the same band,
  add the true tile, classify. A healthy reader **ADMITs** every defined window; report the
  **false-reject count**. *If any defined window false-rejects, the primary result is reported with
  no headline reading.*
- **Wrong-tile control (sensitivity).** At the same live sites, add the **first excluded decorated
  tile**: enumerate the geometric placements on the edge by the frozen template rule *without* the
  legality filter, drop those in the legal menu, take the first remaining by sorted decorated key.
  Report the **REJECT rate** (sensitivity, not pass/fail).
- **Restored-state control.** Repeat the primary test with the witness tile (the single deleted
  neighbour named in `query_diagnostics.json`) restored to a diagnostic copy: `W' = W ∪ {witness}`,
  then `F(W')` vs `F(W' + c)`. Report the class — whether the reader agrees with the local rule once
  the reason is present.
- **Displaced-window control.** Add `c` to primary-size windows centred far from the scar
  (`ang + π/2`, `ang + π`, `ang + 3π/2` — at least a quarter ring away), over the same band. Report
  the class — whether any rejection is local to the scar or global.

## Outcome classes (declared in advance; read off the primary window, w7-s0, true-tile control clean)

- **A. Address rejects** — REJECT under both conventions. The reduced skin's hidden-address
  constraint excludes the locally-admitted `c`; the shed reason is recoverable by a window reader.
- **B. Address admits** — ADMIT under both conventions and on the whole live skin. The reason lives
  only in the shed corner; reconsideration needs the local witness even for a window reader.
- **C. Address undefined** — UNDEFINED under both conventions. The skin has no consistent address at
  this scar; feeds the jam-taxonomy study.
- **D. Split** — the conventions disagree, or the class changes along the ladder. Report the full
  table, no headline; the scale at which the class changes is the finding.

## Numerics

- Open: polygon-area non-empty cutoff `1e-12`; reader positive-hypothesis area `1e-9` (unused here —
  the test is F-emptiness, not A/B selection). Closed: Chebyshev `TOL_R = 1e-9`, box `50`.
- Report floating-point tolerances and the smallest non-empty `F` area observed.

## Scope (to restate in the handback)

One diagnosed query in one world with correlated replicates; a numerical reader under two
conventions, not a symbolic proof; a reader's recovery, not a mechanism of the growth rule; no
claim about other scars, longer horizons, or other tilings.

## Deliverables

`PROTOCOL.md` (+ `protocol_windows.json`, committed first), `address_requery.py`,
`address_requery.json`, `HANDBACK.md` (plain-language paragraph first). Commit and push to
`claude/address-requery-2026-11-10`; no merge, no force-push.

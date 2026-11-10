# PROTOCOL — what does the hidden address put in the gap?

*Pre-registered 2026-11-10, committed **before** any ideal tile is read at the scar gap (Gate 0
and Gate 1 ran first, as the brief allows, since they do not look at the gap). For Katie / Fable /
Astra. One diagnostic on a scar already grown. Frozen engine/lift/reader `84130b9` unchanged; the
reader is reached only through tile lists; nothing feeds back into any constructor; the scar stays
skipped.*

## Question

Brief 1 (`address_requery_2026-11-10`, `30afe8d`/`a47acb9`) showed `F(W+c)=F(W)`, which — as Fable
noted — was guaranteed, because the frozen reader constrains the hidden offset by **vertex
positions only** and all three vertices of `c` already sit in W. That showed the reader is **blind**
to `c`, not that the address is **silent** about `c`. Brief 2 asks the generative question: for
each hidden offset `t` the nearby skin allows, the perfect Penrose tiling with offset `t` places
exactly one tile across the scar edge `e`; read it off, `g(t)`, and ask how often it is `c`, how
often the deleted witness tile is present, and whether the two ever co-occur.

## The two convention maps (established, not assumed — see Gate results)

**Offset map.** The frozen reader's perp basis `PERP[j] = exp(4πij/5)` equals the generator's perp
basis `EV[(2j)%5]` coefficient-for-coefficient (verified, max difference `< 1e-15`). So the reader's
F-offset `t` and the generator's hidden offset are the **same 2-D coordinate**, no map needed.

**Physical/tile map.** With the reader's own global lift (`K ∈ ℤ⁵` per vertex), the engine's tile
positions satisfy, exactly (residual `2.4e-15` over all W vertices):

    pos(vertex) = origin + S · exp(i·18°) · Σ_j K_j · EV[j],   EV[j] = exp(i·72°·j)

where `origin`, `S` are the reader payload's origin and edge length. So the engine's decorated
Robinson triangles are the de Bruijn pentagrid's rhombi on the shared `ℤ⁵` lattice, rotated 18°
and scaled by `S`. The reader's four window pentagons (layers `sum(K) ∈ {-1,0,1,2}` → ranks
`{0,1,2,3}`; apothems `0.809, 1.309, 1.309, 0.809` = small/large = `cos(π/5)·{1,φ,φ,1}`) **are** the
cut-and-project acceptance window.

**Ideal-tiling membership.** A vertex `K` is in the perfect tiling at offset `t` iff
`perp(K) − t` lies inside its layer's window pentagon, i.e. `n_i·(perp(K) − t) ≤ h_rk` for every
facet `i` of rank `rk` — exactly the reader's own F constraint. So the ideal patch at `t` is read
straight from the frozen reader's window; `penrose_address.py` (same `GAMMA`, same window) is kept
as an independent structural cross-check (thick:thin = φ, the 7 star types). *Repository-wins note:*
we build the ideal patch from the reader's proven window-acceptance rather than re-deriving the
generator's `γ`-offset, because the bridge proves they are the same window; recorded here as a
convention choice.

**Reading `g(t)` (tile convention).** The reader is vertex-only, so a tile's **gap shape** is its
third vertex (the one not on `e`). Across `e`, the geometric candidates (the frozen template
enumeration `L.TEMPL` without the legality filter, on the empty side away from the frontier
reference `r`) are grouped by their third vertex's `K`. Exactly one third-vertex `K_z` is accepted
at a generic `t` (a tiling fills the gap once); that is `g(t)`. Mirror decorations sharing `K_z`
are reported together; the headline measurement is on the **shape** (third vertex). `g(t) = c` means
the accepted third vertex equals `c`'s third vertex `(0.640786, -0.096748)` [edge-A] /
`(0.502029, 0.141833)` [edge-B].

## Gates (ran before this commit; both passed)

- **Gate 0.** Primary π/8 window of w7-s0-r2: 39 tiles, SHA `e0d8d518ac64` (= committed), `F(W)`
  area `3.662249e-2`, Chebyshev radius `0.0729` — matches Brief 1 exactly.
- **Gate 1.** At the Chebyshev centre and 25 sampled offsets, **every** vertex of **every** W tile
  is accepted (`26/26`): the ideal patch contains all of W at each offset.
- **Machinery sanity (non-scar).** At a live forced site, `g(Chebyshev centre)`'s accepted third
  vertex equals the full-history scheduler's actual next tile — the reader recovers a known tile.

## Instances (correlated; never independent)

Primary **w7-s0 r2 step 35** (edge-A, candidate c-A). Replicate **w7-s1 r2 step 35**. Secondary
**w7-s0 r1 step 26**, **w7-s0 r3 step 37** (same edge-A/c-A). Group-3 **w15-s0 / w19-s0 / w28-s0,
r1 step 42** (edge-B, c-B). The w7 radii share one physical scar; the group-3 share another.

## Windows

The **committed** windows from `address_requery_2026-11-10/protocol_windows.json` (reused
unchanged, so no window is chosen after seeing any outcome): primary half-width `π/8` (where Brief 1
found `F(W)` non-empty), and the ladder — every other committed half-width whose `F(W)` is
non-empty, plus the whole live skin where non-empty. The script re-derives each window by the
committed rule and asserts its SHA before sampling.

## Sampling (fixed here)

For a window with `F(W)` non-empty: sample a deterministic axis-aligned lattice over the bounding
box of the reader's `F(W)` polygon, at `g × g` points (`g` chosen so ≥ **400** land inside
`F(W)`), plus the **Chebyshev centre**. Seed `20261110`. Drop any offset within Euclidean
`facet_tol = 1e-6` of any window facet of any vertex in the patch (near-facet, where membership is
ambiguous); **report the dropped count**. Report the smallest non-empty `F(W)` area seen.

## Measurements and summaries

Per accepted offset: `g(t)` (accepted third-vertex `K_z` and the decorated tiles sharing it);
whether `g(t) = c` (shape); whether the **witness tile** (the single deleted neighbour from
`query_diagnostics.json`) is present (all its vertices accepted at `t`); whether **c and the witness
are both present**. Summaries: `p_c` (fraction of accepted offsets with `g(t)=c`), `p_w` (fraction
with the witness present), the list of distinct `g(t)` shapes with fractions, and — where `g(t)`
changes across `F(W)` — the dividing line (a window cell boundary).

## Controls (same windows and sampled offsets; the first is the gate)

- **True-tile (gate).** At live forced sites inside the window, compare `g(t)` with the tile the
  full-history scheduler places next. A forced tile should be the ideal tile at every offset;
  report the disagreement count; **any disagreement withholds the headline.**
- **Wrong-tile.** At the same sites, the fraction of offsets where a **locally excluded** tile is
  the ideal tile. Rule (fixed): the first excluded decorated key in `L.TEMPL`-enumeration order
  (geometric candidates minus the legal menu). Should be zero.
- **Ordinary scars.** At pinned scars where reduced and full-history menus are **both empty**,
  record `g(t)`. Shows what the address says where rule and history agree nothing fits.
- **Two sides.** Split the window's tiles by the side of `e`'s line
  (`sign of Im((z − p)·conj(q − p))`), compute `F` for each half, their overlap, and `g(t)` from
  each half. Tests whether the scar sits where two stretches of skin hold different addresses.

## Outcome classes (declared; read off the primary window, both gates passed, true-tile clean)

- **A. Address forbids** — `p_c = 0`. The nearby skin's address excludes `c`; the shed reason is
  recoverable by a tile-level address reading.
- **B. Address predicts** — `p_c = 1`. The address calls for `c`; the thinned skin was following
  its own address and the deleted witness is the piece that does not belong. Report `p_w` beside it.
- **C. Address undecided** — `0 < p_c < 1`. The narrow skin does not pin the answer; report `p_c`
  along the ladder and the cell boundary dividing `F(W)`.
- **D. Not readable** — Gate 1 fails, or `F(W)` is empty at every committed window.

**Override.** If `c` and the witness tile are **ever present together** in an ideal patch, report
that first: it would mean the full-history rejection of `c` is not a fact about perfect tilings, and
the reading above needs rethinking.

Every statement is labelled by who could know it: the growing edge (local rule), or only the reader
(the address). No class licenses a claim that the growing world consults its address.

## Numerics, scope, deliverables

Float sampling, not symbolic proof: report sample counts, dropped offsets, `facet_tol = 1e-6`,
window `h` apothems, Chebyshev `TOL_R = 1e-9`. Scope: one scar in one world with correlated
replicates; a reader's inference from a narrow window, not a property of the growth rule;
perfect-tiling theory applied beside a jam where the wider skin has no consistent address; no claim
about other scars, horizons or tilings. Deliverables: this `PROTOCOL.md`, `address_gapfill.py`,
`address_gapfill.json`, `HANDBACK.md` (plain-language first; one results table; control counts;
declared class; one figure of `F(W)` coloured by the gap tile), and a dated correction note appended
to Brief 1's `HANDBACK.md`. Branch `claude/address-gapfill-2026-11-10` from `a47acb9`; no merge, no
force-push.

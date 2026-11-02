# Cooperative rearrangement pilot — 2026-11-02

> **Updated 2026-11-03** after the independent Codex audit
> (`audit/cooperative-rearrangement-2026-11-03`, commit `e7ff8ff`). Principal null
> **survives**; wording corrected. **Supported central result:** for the recorded
> world-7/B/stream-0 jam, all **12,248 seed-containing, edge-connected regions of
> at most eight triangular tiles** have a numerically incompatible unchanged
> exterior under the fixed-coordinate, four-layer projection-window convention.
> **Eight triangular tiles ≠ eight rhombi**; this is the **seeded** family (not
> every band region); the 15 hexagons are **6 triangles / 3 rhombi**, identity-only;
> no repair qualified, so construction/readout were not attempted; **numerical,
> model-specific**. The "41-tile" figure is **one heuristic disconnected DELETION
> footprint — not a minimum/repair** (12 vertices, 10 components, 8+4 boundary edges
> lost, 12.48/14.05 spans, zero-margin, uncertified). "Four" = minimum of the
> **20-row deletion** problem (not tiles/flips). True frontier is **73 / 71 growable
> / 2 blocked** (not 103/101). See `integration_2026-11-03/INTEGRATION_HANDBACK.md`.
> Maintained code now uses the audited safeguards (`src/safeguards.py`); historical
> outputs preserved; integration re-runs under `integration_2026-11-03/`.

A bounded exploratory pilot: can a finite rearrangement in the **retained
boundary band** restore projection-window compatibility and permit further
construction, while leaving the original A/B choice uniquely readable? A negative
result is acceptable; no matching rules are relaxed.

- **Starting commit:** `53692c20c68a03a96b1e682ad8c90e60b764df21` (audit branch
  `claude/jam-compatibility-diagnostic-audit`).
- **Branch:** `claude/cooperative-rearrangement-pilot`.
- **Case:** world 7, option B, stream 0, at the recorded jam (step 23).
- **Frozen engine / reader:** imported read-only from
  `84130b97f5044197392e72cd53e0e71f81b043f3`.

**Result (plain):** the obstruction is **spatially distributed** — every connected
fixed-exterior region of size ≤ 8 (all 12,248) is ruled out because the unchanged
exterior is already infeasible; no legal replacement restores compatibility;
construction does not resume; the historical readout was empty/incompatible
already at the jam. See [HANDBACK.md](HANDBACK.md).

## Layout

```
protocol/   PROTOCOL.md (frozen), PROTOCOL_DEVIATIONS.md
input/      retained_state.json (SEARCH-VISIBLE), evaluator_historical.json (EVALUATOR-ONLY)
src/        coop_common, export_state, part3_necessary, part4_search, part5_score, make_figure
tests/      test_coop.py
results/    part3_necessary.json (decisive), part4_search.json, part5_score.json
figures/    obstruction_map.png
HANDBACK.md
```

**Separation of concerns:** candidate generation (Part 3/4) reads only
`input/retained_state.json`. The historical A/B data (`evaluator_historical.json`)
is read **only** by the Part-5 evaluator (the frozen reader).

## Reproduce

```bash
git worktree add --detach /tmp/efp-snapshot 84130b97f5044197392e72cd53e0e71f81b043f3
export EFP_SNAPSHOT=/tmp/efp-snapshot/exploratory/accretion_pilot/expansion_front_paper
export MPLBACKEND=Agg
pip install numpy scipy matplotlib        # Python 3.12/3.13
# the pilot fork cache is reused if present; else:
#   (cd ../jam_repair_pilot/src && python3 build_fork_cache.py)
```

```bash
cd exploratory/accretion_pilot/cooperative_rearrangement_pilot/src
python3 ../tests/test_coop.py     # focused tests (pass)
python3 export_state.py           # Part 1: self-contained retained-state input
python3 part3_necessary.py        # Part 3: necessary condition (decisive; ~2-4 min)
python3 part4_search.py           # Part 4: replacement search + controls (concrete)
python3 part5_score.py            # Part 5: frozen-reader baseline readout
python3 make_figure.py            # figures/obstruction_map.png
```

Deterministic from the recorded `(world, stream)` identifiers. Feasibility is a
box-independent float LP over φ-irrational data (robust numerical evidence, not a
symbolic proof), consistent with the audited diagnostic.

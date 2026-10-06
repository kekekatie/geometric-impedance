# A perp-space map of grown worlds

> **Caution (2026-10-06):** M1 (open choices sit deeper) uses one depth measure at one scale. Depth and vertex type are entangled in Penrose tilings ([`../robustness_depth_clock/`](../robustness_depth_clock/)), so M1 should be re-checked within vertex type.

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md).*

Katie's parting thought was to bring in perp space, and her paper supplies the toolkit:
**Depth-Dependent Directional Balance and Discrete Holonomy in Projection Tilings**
(doi:10.5281/zenodo.20695694). Every vertex was lifted to its hidden address, and each vertex's
**hull depth** in the acceptance window was measured: 0 at the window's edge, 1 at its centre.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| V0 | the tools work on a genuine tiling: no lift conflicts, 4 layers | 401 vertices, 0 conflicts, 4 layers (two small windows, two large) | ✅ PASS |
| M1 | choices (frontier edges with 2+ options) sit **shallower** than forced edges, in ≥ 9/12 runs | **0/12**: open edges were **deeper** in every run (median 0.44–0.46 vs 0.37–0.39) | ❌ FAILED (the opposite) |
| M2 | a decapod **smears** the window: every decapod world has a larger perp hull area than the fillable median | **8/8** (15.1–16.0 vs 14.12–14.16; same tile budget, similar vertex counts 452–460) | ✅ HELD |

## What it means (plainly)

- **Choices live deeper in the window, not at its edge.** I predicted the opposite, but Katie's paper
  explains why it's this way round.
  - Shallow vertices, near the window's edge, have **truncated, lopsided** sets of directions. Fewer
    ways to carry on means growth there is **forced**.
  - Deep vertices have **balanced, complete** direction sets. More ways to carry on means that is
    where the **open** choices live.
  - So the directional balance mechanism from Katie's paper, found by looking at walks, also governs
    where a growing world has freedom.
  - Caveats:
    - The gap is modest.
    - The 12 runs are only 9 distinct histories.
    - Counting each edge once instead of once per round shrinks the gap but keeps its direction (0.40
      vs 0.37 in 3 runs; [`results/unique_edges_EXPLORATORY.txt`](results/unique_edges_EXPLORATORY.txt)).
    - The guessed edges themselves are mixed: mostly 0.45–0.59, but the first guess at the seed's rim
      is shallow (~0.28).
- **A decapod's memory shows up as a smeared window.** Decapod worlds needed **no** guesses. Their
  hidden addresses spread over a window about **8–13% larger** than ordinary worlds grown with the same
  tile budget (vertex counts 452–460). Ordinary worlds are remarkably consistent: 14.12–14.16.
  - **Hypothesis, not a finding:** the ten sectors around a decapod each fit a slightly shifted
    window. `../decapod_memory/` tests part of this, and its caution note applies.
  - The lift itself never breaks (0 conflicts). That is expected: any closed loop of edges in a
    rhombus tiling closes in Z⁵. So, as Astra pointed out, this result is **not** evidence of a lift
    failing to close. Calling the difference "holonomy" would need a separately defined transport
    and loop measurement. What is established is that the *distribution* of addresses differs.

## Limits

- The windows are each world's own finite hull, approximated from inside.
- Depth is taken from the final patch.
- One tiling family. Patches of 800–1,000 tiles.

## Files

- `perp_map.py`
- `unique_edges_EXPLORATORY.py`
- `results/perp_map_report.txt`
- `results/m1_runs.json`
- `results/m2_worlds.json`
- `results/unique_edges_EXPLORATORY.txt`

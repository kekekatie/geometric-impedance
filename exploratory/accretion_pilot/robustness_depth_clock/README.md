# Robustness: does "the present lasts longer deep in the window" survive?

> **Follow-up (2026-10-07, [`../window_cells/`](../window_cells/)):** Fable suggested that the clock is read off the **window cell** (local pattern) at each scale. It isn't. Within worlds, cells predict settling time no better than shuffled cells. Across worlds they predict only when the *same place* recurs (the decapod worlds are slices of one tiling). Settling time depends on **where** a place is (how growth reaches it), not on what kind of place it is. The withdrawal stands.

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md).*

**The finding under test** (`../structure_clock/` C1): places deeper in the hidden window take longer
to settle (ρ ≈ +0.2–0.3 at the 1-edge disc). Three challenges were set; the finding counts as
robust only if all three pass.

## Scorecard

| | challenge | result | |
|---|---|---|---|
| RA | 12 **new** decapod worlds | 12/12 positive (ρ 0.17–0.23) | ✅ HELD |
| RB | 12 **ordinary** worlds with choices (11 distinct histories) | 12/12 positive (ρ 0.14–0.21) | ✅ HELD |
| RC | **other measuring sizes**: disc 0.8 and 1.25 edges | 0.8: **3/8, ρ ≈ 0**; 1.25: 8/8 but weak (ρ 0.05–0.12) | ❌ FAILED |
| | **robust?** | | **NO** |

## What went wrong, and why (exploratory, post hoc)

**1. The sign flips with the size of the ruler**
([`scale_sweep_EXPLORATORY.py`](scale_sweep_EXPLORATORY.py),
[`results/scale_sweep_EXPLORATORY.txt`](results/scale_sweep_EXPLORATORY.txt)). Mean ρ(depth,
settling time) over 4 worlds, by disc radius:

| disc radius (edges) | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 | 1.1 | 1.25 | 1.5 | 1.75 | 2.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| ρ | **−0.31** | +0.04 | −0.03 | **+0.35** | +0.26 | +0.20 | +0.10 | +0.10 | −0.12 | **−0.24** |

A genuine "deep places last longer" law would not reverse sign as the ruler grows.

**2. At the original scale, depth was standing in for vertex type**
([`vertex_type_EXPLORATORY.py`](vertex_type_EXPLORATORY.py),
[`results/vertex_type_EXPLORATORY.txt`](results/vertex_type_EXPLORATORY.txt)).

- In a cut-and-project tiling, a corner's **type** (which of the 8 Penrose vertex stars it has) is
  fixed by where it sits in the window.
- At the 1.0-edge disc, the overall ρ was +0.23–0.29, but **within each vertex type it vanishes**
  (−0.17 to +0.03).
- So the original effect came from *different corner types catching different sets of tiles in a
  1-edge disc*, not from depth as such.
- At 0.6 and 2.0 edges, a negative within-type relationship remains (−0.23 to −0.48). That is
  unexplained, and is also scale-specific.

## What this means

- **The headline "the present lasts longer deep in the window" is withdrawn as a general claim.**
- What replicated (RA, RB) is real but narrower: at the 1-edge scale, settling time depends on the
  local **vertex geometry**, which depth happens to track. It is a fact about Penrose corner types
  at that scale, not a law of local time.
- **Knock-on caution:** `../decision_radius/` (deep places need a wider ring) and `../perp_map/` M1
  (choices sit deeper) used single scales and the same depth measure. They may also be vertex-type
  effects. They should be re-checked within vertex type before being relied on.
- **A lesson for future measures:** in Penrose tilings, "depth" and "vertex type" are entangled, so
  any depth effect must be checked within type and across scales.

## Files

- `robustness_depth_clock.py`
- `scale_sweep_EXPLORATORY.py`
- `vertex_type_EXPLORATORY.py`
- `results/worlds.json`
- `results/robustness_report.txt`
- `results/scale_sweep_EXPLORATORY.txt`
- `results/vertex_type_EXPLORATORY.txt`

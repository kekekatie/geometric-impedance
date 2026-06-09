# Where We Are & Where To Go Next

## Status (June 2026)

### What's solid
- **v0.3 validation**: Depth (how centrally embedded a vertex is in perpendicular space) is the stable predictor of address residue on near-return paths. Shallow/edge-of-hull vertices accumulate more hidden-address mismatch when the physical path comes home. This is stronger in Penrose than AB. Confirmed across 10 seeds, 20k walkers, with shuffled controls.
- **Exo/endo distinction**: AB retains identity via external coordinates (AUC 0.986) even after graph destruction; Penrose does not (0.661). Published on Zenodo.

### What's dead
- **alpha~0.553 via cost-time walks**: Lambda sweep showed flat lines at alpha~0.95 for all resistance strengths. GPT's scout was a small-sample artifact. We are NOT chasing 0.553 any more.

### What's alive
- **Holonomy** — the idea that near-closed physical loops accumulate hidden-space residue, and that this residue is geometry-dependent.

## Claude Code's recommendation for next step

**Discrete holonomy via loop analysis.**

Instead of trying to slow down diffusion to hit a magic exponent, directly measure the holonomy-like quantity:

1. Find paths that form approximate loops in physical space (walks that return within distance d of their start).
2. For each near-loop, measure the **signed** perpendicular-space displacement accumulated around the loop.
3. Ask: does this displacement correlate with the **area** enclosed by the loop? In real holonomy (Berry phase, parallel transport on curved surfaces), the phase picked up around a loop is proportional to the enclosed curvature. If the aperiodic geometry has anything holonomy-like, bigger loops should accumulate more perpendicular displacement, and the relationship should differ between Penrose and AB.

This is clean, directly tests the holonomy intuition, doesn't chase a specific number, and builds on everything we already have (the walk infrastructure, the vertex data, the perpendicular coordinates).

**Concrete test:**
- Run many random walks on both substrates
- Collect all near-return events at multiple time horizons
- For each near-return, estimate enclosed area (convex hull of visited positions)
- Plot perpendicular displacement vs enclosed area
- Compare Penrose vs AB slopes
- If Penrose shows a steeper or more structured relationship, that's discrete holonomy

## What GPT and Gemini recommended
(Karen to paste their suggestions here when she's back)

## Reminder for Karen
- You decided: no more chasing alpha~0.553
- All results are in this repo on branch `claude/bold-ritchie-l1Mc4`
- Handoff summaries are in the repo root (lambda_sweep_handoff_summary.md, v0_3_handoff_summary.md)
- Your brother is visiting from overseas — enjoy that first!

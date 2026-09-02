# Brachistochrone Dip Profile v0.1 — Handoff Summary

## What was tested

Following the path-depth profile finding (dip-and-return walkers have LESS residue), we asked: does the SHAPE of the dip matter? Specifically, does a brachistochrone-like profile (fast drop, slow return) produce cleaner address recovery?

10 seeds, 30,000 walkers/seed, 1,024 steps, both substrates, thresholds d≤2.0 and d≤3.0.

## Shape metrics tested

1. **Asymmetry**: (ascent_steps - descent_steps) / total. Positive = fast drop, slow return (brachistochrone-like).
2. **Sharpness**: Fraction of dip spent near minimum depth. High = V-dip (brief minimum). Low = U-dip (lingering minimum).
3. **Timing**: Where in the walk the dip occurs (early / mid / late).
4. **Descent smoothness**: Monotonicity of the drop phase.
5. **Ascent smoothness**: Monotonicity of the recovery phase.
6. **Excursion depth**: How far below start depth the walker dipped.
7. **Recovery**: End depth / start depth (how fully the walker returned).

## The headline: brachistochrone shape does NOT predict residue — but LINGERING TIME does

**The brachistochrone hypothesis is not supported.** Asymmetry (fast drop vs slow drop) has near-zero correlation with address residue:
- Spearman(asymmetry, residue): AB = 0.023–0.029, Penrose = -0.002 to -0.013
- p-values all > 0.4

**SHARPNESS is the surprise winner.** V-dips (sharp, brief touch at minimum) have substantially MORE residue than U-dips (broad, lingering at minimum):

| Substrate | Threshold | V-dip residue | U-dip residue | Gap |
|-----------|-----------|--------------|--------------|-----|
| AB        | d≤2       | 1.133        | 0.790        | **+0.343** |
| AB        | d≤3       | 1.231        | 0.894        | **+0.337** |
| Penrose   | d≤2       | 1.197        | 0.801        | **+0.395** |
| Penrose   | d≤3       | 1.423        | 0.926        | **+0.497** |

Spearman(sharpness, residue) = 0.22–0.29 across all conditions. This is the strongest shape-level predictor.

## What else matters

**Excursion depth** remains the strongest overall predictor (Spearman -0.25 to -0.32). Deeper dips = less residue.

**Ascent smoothness** negatively correlates with residue (Spearman -0.19 to -0.25). A smooth, monotonic return to depth produces cleaner recovery than a jagged one.

**Dip timing** shows a weak early-dip advantage in AB (early: 1.02, late: 0.99 at d≤2) but essentially no effect in Penrose.

## The reframed interpretation

The "engine" is not about the speed of the fall — it's about **how long you spend in the depths**. The stable core doesn't just need to be *visited*; it needs to be *inhabited* for a while. A brief touch at the minimum (V-dip) doesn't give the address time to reset. A sustained stay at minimum depth (U-dip) allows the hidden coordinates to relax back to their stable configuration.

Think of it like this: if the perpendicular-space hull has a "home base" at depth, then:
- **U-dip walkers** go home, sit down, and settle in → address resets cleanly
- **V-dip walkers** run through the living room without stopping → address barely changes
- **Non-dippers** never go home at all → worst residue

The smooth-ascent effect reinforces this: walkers that return to their starting depth gradually (without bouncing around) recover their address more cleanly than those that return chaotically.

## Penrose vs AB

Penrose shows a slightly stronger sharpness effect (gap 0.40–0.50 vs AB's 0.34–0.34). Consistent with Penrose having a more structured centre-vs-edge distinction in its hidden address space.

Both substrates show mean asymmetry ~0.11–0.13 (slightly brachistochrone-like on average), but this has no predictive power for address recovery in either substrate.

## What this does NOT claim

- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.
- The brachistochrone analogy (fast fall drives reconstruction) is NOT supported as stated.
- The REFRAMED version — "time at depth is the engine" — IS supported.

## Story arc so far

1. **v0.3 validation**: Depth predicts residue. Deeper start = less residue.
2. **Holonomy proxy**: Physical near-closure ≠ address closure. Depth-gated, not area-dependent.
3. **Path-depth profile**: Dip-and-return = LESS residue. The dip is the engine, not the obstacle.
4. **Brachistochrone (this test)**: The shape of the dip matters, but not the way we expected. It's not about fast-fall momentum — it's about **lingering time at the stable core**. U-dips >> V-dips.

## Files

- brachistochrone_v0_1_report.md — full report with all tables
- brachistochrone_summary.csv / per_seed.csv / dip_samples.csv
- fig_1_brachy_vs_anti.png — Brachistochrone vs anti-brachistochrone vs symmetric (KEY)
- fig_2_v_vs_u_dip.png — V-dip vs U-dip (THE STAR FIGURE)
- fig_3_dip_timing.png — Dip timing (early vs mid vs late)
- fig_4_spearman_shape.png — Spearman correlation summary
- fig_5_asymmetry_scatter.png — Scatter: asymmetry vs residue
- fig_6_substrate_shape_sensitivity.png — AB vs Penrose shape sensitivity
- brachistochrone_v0_1.py — reproducible script

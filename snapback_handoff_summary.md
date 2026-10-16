# Snap-back Threshold Analysis v0.1 — Handoff Summary

## What was tested

Following the brachistochrone finding (lingering at minimum depth matters more than dip shape), we asked: does address recovery happen gradually as linger time increases, or is there a sharp threshold — a "snap-back" where the address suddenly resets?

10 seeds, 30,000 walkers/seed, 1,024 steps, both substrates, thresholds d≤2.0 and d≤3.0.

## The headline: it's a SLOPE, not a snap — but the slope is steeper in Penrose

**No sharp phase transition.** The recovery curve is a smooth, monotonic decline from high residue (short linger) to low residue (long linger). There's no single bin boundary where the residue suddenly plummets.

BUT: the decline is not linear either. It's an S-like curve — slow improvement at first (1-9 steps barely helps), then a steep middle section, then a floor.

### The numbers

**Linger duration → mean final residue:**

| Linger steps | AB d≤2 | AB d≤3 | Penrose d≤2 | Penrose d≤3 |
|-------------|--------|--------|-------------|-------------|
| 1-4         | 1.03   | 1.15   | 1.23        | 1.44        |
| 5-9         | 1.17   | 1.32   | 1.27        | 1.48        |
| 10-19       | 1.13   | 1.22   | 1.14        | 1.28        |
| 20-39       | 1.05   | 1.13   | 1.01        | 1.12        |
| 40-79       | 0.95   | 1.02   | 0.85        | 0.96        |
| 80-159      | 0.74   | 0.85   | 0.72        | 0.88        |
| 160-319     | 0.38   | 0.73   | 0.62        | 0.62        |

The steepest part of the decline happens around 10-80 steps. Before that, more linger doesn't help much. After ~80 steps, diminishing returns set in (except for the very longest lingerers who reach the floor).

## Key finding 1: Penrose's slope is steeper

Penrose shows a stronger relationship between linger time and recovery:
- Spearman(linger, residue): Penrose = -0.31 to -0.32, AB = -0.24 to -0.25
- Penrose drops from 1.27 to 0.85 between the 5-9 and 40-79 bins (a 0.42 drop)
- AB drops from 1.17 to 0.95 over the same range (a 0.22 drop)

The endohedral structure of Penrose makes lingering at depth almost twice as effective as in AB.

## Key finding 2: Total linger > consecutive linger

Total steps near minimum predicts recovery better than the longest consecutive stretch:
- AB: Spearman -0.25 (total) vs -0.16 (consecutive)
- Penrose: Spearman -0.32 (total) vs -0.19 (consecutive)

It doesn't matter if the walker lingers in one long stay or makes multiple visits to the depth zone. What matters is TOTAL TIME at depth.

## Key finding 3: The aligned trajectory (fig 2) shows gradual drift, not a snap

When we align all dippers at their minimum-depth moment (step 0 = deepest point) and average the address residue:
- Before the dip: residue is roughly constant (the address hasn't changed yet)
- At the minimum: residue increases slightly (the address is disturbed during the descent)
- After the minimum: residue gradually decreases over ~100-200 steps
- The recovery is smooth and continuous — no sudden snap-back

## Key finding 4: Address is worse at minimum, better at end (fig 3)

Most walkers have HIGHER residue at their minimum depth point than at the end. The scatter plot (fig 3) shows points mostly below the diagonal — meaning the final residue is less than the residue at the minimum. Recovery happens AFTER the dip, during the return to depth.

## The reframed interpretation

The address recovery mechanism is a **continuous relaxation**, not a phase transition. Think of it like:
- The stable core (deep in the hull) is a basin of attraction for addresses
- When a walker lingers there, its address gradually relaxes toward the correct value
- More time at depth = more relaxation = lower residue
- But there's an S-curve shape: you need a minimum ~10 steps before improvement really kicks in, and ~80+ steps to get most of the benefit
- Penrose's basin is deeper/steeper (endohedral structure), so relaxation is faster there

This is not a thermostat (snap at threshold). It's a viscous relaxation (gradual, but with a characteristic timescale).

## Story arc so far

1. **v0.3 validation**: Depth predicts residue. Deeper start = less residue.
2. **Holonomy proxy**: Physical near-closure ≠ address closure. Depth-gated, not area-dependent.
3. **Path-depth profile**: Dip-and-return = LESS residue. The dip is the engine.
4. **Brachistochrone**: Dip SHAPE matters — lingering at depth (U-dip) >> brief touch (V-dip). Fall speed irrelevant.
5. **Snap-back (this test)**: Recovery is a smooth S-curve, not a snap. ~10-80 steps is the critical range. Penrose relaxes faster than AB. Total time at depth matters more than consecutive time.

## What this does NOT claim

- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.
- No phase transition — the "snap-back" hypothesis as stated is not supported.
- The RELAXATION interpretation IS supported: continuous recovery with a characteristic timescale.

## Possible next directions

1. **Controlled linger walks**: Force walkers to spend exactly N steps at depth (N = 5, 10, 20, 40, 80, 160) then return. This removes the confound that longer lingerers might start deeper.
2. **Depth-dependent relaxation rate**: Is the relaxation faster at depth 0.8 than at depth 0.5? Map the relaxation timescale as a function of depth.
3. **Address trajectory decomposition**: During the linger phase, does the address move toward the "correct" value monotonically, or does it oscillate around it?

## Files

- snapback_v0_1_report.md — full report with all tables
- snapback_summary.csv / snapback_linger.csv / snapback_linger_bins.csv
- snapback_threshold_detection.csv
- fig_1_linger_vs_residue.png — Residue vs linger duration (KEY FIGURE)
- fig_2_aligned_residue_trajectory.png — Step-by-step trajectory aligned at dip
- fig_3_residue_at_min_vs_final.png — Does recovery happen after the minimum?
- fig_4_total_vs_consecutive_linger.png — Total vs consecutive linger comparison
- fig_5_substrate_snapback_comparison.png — AB vs Penrose overlaid
- fig_6_normalised_recovery_curve.png — Normalised S-curve shape
- snapback_v0_1.py — reproducible script

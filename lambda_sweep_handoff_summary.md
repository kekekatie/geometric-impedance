# Lambda Sweep v0.3 — Handoff Summary

## What was tested

Claude Code ran a full lambda sweep of the depth-resistance walk model that GPT's v0.1 scout proposed. The scout had found that a cost-time walk (where outward/depth-losing steps cost extra time) pushed Penrose to alpha~0.560, close to the proposed 0.553 target.

We swept resistance strength lambda from 0 to 20, with 10 seeds per lambda, 5,000 walkers per seed, for both AB_N30 and Penrose_N24.

## The headline result

**The alpha~0.553 finding did NOT replicate at scale.**

Both substrates stay flat near normal diffusion (alpha~0.94-0.96) across ALL lambda values from 0 to 20. Neither substrate ever drops below alpha=0.553. The lines are essentially flat — cranking up the resistance strength has almost no effect on the diffusion exponent.

GPT's scout (1 seed, 1,200 walkers, lambda=10) showed AB at 0.445 and Penrose at 0.560. At scale (10 seeds, 5,000 walkers), those numbers are AB~0.942 and Penrose~0.954. The scout result was a small-sample artifact.

## What IS real in the data

Two genuine signals survived the scale-up:

### 1. Penrose consistently sits above AB
Penrose's alpha is about 0.01-0.02 higher than AB at every single lambda value. This gap is small but stable across all seeds and all resistance strengths. Penrose diffuses slightly *faster* than AB in physical space — the opposite direction from what the 0.553 hypothesis predicted, but a real substrate difference.

### 2. Penrose has higher near-return address mismatch
At low-to-moderate lambda (0-10), Penrose shows consistently higher near-return perpendicular mismatch than AB (~1.05-1.13 vs ~0.95-1.04). This echoes the v0.3 validation finding: Penrose accumulates more hidden-address residue on near-return paths.

## What this means

The depth-resistance walk model — at least in this simple form — is NOT the mechanism that produces alpha~0.553. The cost-time approach doesn't slow physical diffusion because the walker still takes the same physical steps; it just waits longer between some of them. When you measure MSD against cost-time (which includes the waiting), alpha stays near 1.0 because the waiting and the stepping scale together.

**The holonomy/address-residue story from v0.3 is still the solid finding.** The walk model needs to be fundamentally different — not "same walk but some steps cost more time," but something that actually changes *which* physical steps are taken based on hidden-space constraints.

## Possible next directions (for discussion with GPT/Gemini/Claude)

1. **Rejection walks**: instead of waiting-time cost, the walker *refuses* certain steps and tries again. Depth-losing steps get rejected with probability proportional to lambda. This actually changes the physical trajectory.
2. **Constrained loop analysis**: forget the diffusion exponent entirely. Instead ask: among paths that form approximate loops in physical space, does the accumulated perpendicular displacement correlate with loop area? That would be a direct discrete holonomy proxy.
3. **Accept that alpha~0.553 may not be the right target.** The v0.3 depth finding and the address-mismatch asymmetry are real, reproducible results. They may be more important than hitting a specific exponent.

## Numbers at a glance

| Lambda | AB alpha (cost-time) | Penrose alpha (cost-time) | Gap |
|--------|---------------------|--------------------------|-----|
| 0      | 0.948               | 0.960                    | +0.012 |
| 5      | 0.941               | 0.961                    | +0.020 |
| 10     | 0.942               | 0.954                    | +0.012 |
| 15     | 0.947               | 0.960                    | +0.013 |
| 20     | 0.944               | 0.962                    | +0.017 |

## Files in the bundle

- lambda_sweep_v0_3_report.md — full report with complete summary table
- lambda_sweep_summary.csv — mean across seeds for each substrate x lambda
- lambda_sweep_per_seed.csv — every seed individually
- fig_a_alpha_vs_lambda.png — THE key plot: flat lines, no crossing of 0.553
- fig_b_substrate_gap.png — Penrose-AB gap (always positive, ~0.01-0.02)
- fig_c_seed_scatter.png — per-seed scatter at lambda 8, 10, 12
- fig_d_nr_perp_vs_lambda.png — near-return address mismatch vs lambda
- lambda_sweep_v0_3.py — full reproducible script

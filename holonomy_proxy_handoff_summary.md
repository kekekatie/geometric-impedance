# Holonomy Proxy v0.1 — Handoff Summary

## What was tested

Claude Code ran a discrete holonomy proxy analysis: when random-walk paths nearly close in physical space, how much perpendicular/address displacement remains? Does it depend on where the walker started (depth), what regions it visited, or the area enclosed by the loop? Does Penrose behave differently from AB?

- 10 seeds, 20,000 walkers per seed, 1,024 steps
- Near-return thresholds: physical distance ≤ 1, ≤ 2, ≤ 3
- Both AB_N30 and Penrose_N24
- Shuffled controls (perpendicular coordinates randomly permuted)
- Loop area computed via shoelace formula
- Depth conditioning: deep vs shallow starts, shallow-region exposure

## Three headline findings

### 1. DEPTH IS THE SIGNAL (again, and stronger than ever)

The deep-vs-shallow start gap is the clearest, most stable result across everything we've run:

| Substrate | Threshold | Deep start residue | Shallow start residue | Gap |
|-----------|-----------|-------------------|----------------------|-----|
| AB        | d≤1       | 0.593             | 0.966                | 0.373 |
| AB        | d≤2       | 0.880             | 1.116                | 0.235 |
| AB        | d≤3       | 0.955             | 1.213                | 0.257 |
| Penrose   | d≤1       | 0.504             | 0.726                | 0.222 |
| Penrose   | d≤2       | 0.886             | 1.178                | 0.292 |
| Penrose   | d≤3       | 0.985             | 1.396                | **0.411** |

**Penrose's gap grows with threshold.** At d≤3 (larger loops), Penrose's shallow-start walkers have 42% more address residue than deep-start walkers. AB's gap is flatter.

In plain English: **the bigger the loop, the more Penrose's edge-of-town walkers fail to bring their hidden address home. AB doesn't show this scaling as strongly.**

This is the most holonomy-like signal in the data.

### 2. LOOP AREA DOES NOT PREDICT RESIDUE

Spearman correlations between loop area and perpendicular residue are essentially zero (~0.005) in both substrates. The binned-mean lines in figure 4 are flat.

This means the holonomy is NOT the classical "residue proportional to enclosed area" form. Whatever is happening depends on where you start (depth) and what regions you traverse, not on the area enclosed.

### 3. SHUFFLED CONTROLS: the geometry matters, especially for tight loops

At the tightest threshold (d≤1):
- AB real: 0.777 vs shuffled: 0.528 (real is 47% higher)
- Penrose real: 0.614 vs shuffled: 0.484 (real is 27% higher)

At looser thresholds (d≤2, d≤3), the real-vs-shuffled gap shrinks. The real perpendicular geometry matters most for the tightest near-returns — paths that come very close to home physically leave more address residue than they would if the hidden coordinates were randomly assigned.

## What this means for the theory

The holonomy intuition — "the body comes home but the hidden address hasn't" — is confirmed as a real, reproducible, geometry-dependent effect. But it's not the textbook form where residue scales with enclosed area.

Instead, it's **depth-gated**: the hidden-space residue depends on the starting position's embedding depth in perpendicular space, and this effect is STRONGER in Penrose for larger loops. This connects directly to the exo/endo distinction from the published paper: Penrose's address space is internally structured (endo), so depth within that space matters more for transport.

The honest sentence: **Aperiodic tilings exhibit a discrete holonomy-like effect where near-closed physical paths leave perpendicular-space residue that depends on hull-depth, not loop area, and this depth-sensitivity is stronger in Penrose than AB.**

## What this does NOT claim

- NOT Berry curvature (no area scaling)
- NOT quantum holonomy
- NOT alpha~0.553 (we've moved past that)
- It IS a classical discrete holonomy proxy with genuine geometric dependence

## Possible next directions

1. **Path-depth profile analysis**: instead of just start depth, characterize the full depth trajectory along the walk. Do paths that dip from deep to shallow and back accumulate more residue than paths that stay at one depth? That would be a "curvature encountered" proxy.
2. **Controlled loop construction**: instead of finding near-returns by chance among random walks, deliberately construct loops of known area and depth profile, then measure residue.
3. **The asymmetry question (from Gemini)**: does the depth-gated residue have a preferred direction in perpendicular space? Is there a systematic drift or is it random in orientation?

## Files in the bundle

- holonomy_proxy_v0_1_report.md — full report with tables
- holonomy_proxy_v0_1_summary.csv — aggregated across seeds
- holonomy_proxy_v0_1_per_seed.csv — every seed
- holonomy_proxy_v0_1_near_loops.csv — individual loop-level data (sampled)
- holonomy_proxy_v0_1_shuffled_summary.csv — shuffled control results
- fig_1_residue_by_substrate.png — AB vs Penrose with shuffled overlay
- fig_2_residue_by_start_depth.png — deep vs shallow start (KEY FIGURE)
- fig_3_residue_by_shallow_exposure.png — shallow-region exposure effect
- fig_4_residue_vs_area.png — residue vs loop area (flat = no area scaling)
- fig_5_real_vs_shuffled.png — real vs shuffled comparison
- holonomy_proxy_v0_1.py — full reproducible script

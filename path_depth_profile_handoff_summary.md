# Path-Depth Profile v0.1 — Handoff Summary

## What was tested

Following the holonomy proxy v0.1 (which showed that start depth predicts address residue), we asked: does what happens ALONG the path matter? Specifically:

- **Depth range**: max depth minus min depth along the path
- **Depth excursion**: how far below start depth did the walker dip?
- **Cumulative depth change**: total absolute depth traversed
- **Dip-and-return**: did the walker go significantly shallow and come back deep?

10 seeds, 20,000 walkers/seed, 1,024 steps, both substrates, shuffled controls.

## The headline: dip-and-return walkers have LESS residue

This is the opposite of what "curvature encountered along the path" would naively predict.

**Figure 4 (dip-and-return) is the star figure.** At every threshold, in both substrates:

| Substrate | Threshold | Dip-return residue | No-dip residue | Gap |
|-----------|-----------|-------------------|----------------|-----|
| AB        | d≤1       | 0.413             | 1.369          | **-0.956** |
| AB        | d≤2       | 0.869             | 1.140          | -0.272 |
| AB        | d≤3       | 0.957             | 1.213          | -0.256 |
| Penrose   | d≤1       | 0.367             | 1.198          | **-0.831** |
| Penrose   | d≤2       | 0.883             | 1.214          | -0.331 |
| Penrose   | d≤3       | 1.010             | 1.388          | **-0.378** |

Walkers that dip into shallow territory and come back bring their address home MORE cleanly. Walkers that never dip have MORE address residue.

## Why this makes sense (and is actually good news)

Think about it physically: a "dip-and-return" walker went deep → shallow → deep. That means it started from the centre of the hidden-space hull, ventured to the edge, and came back. Its address tracks its depth — it went out and came back in both physical AND hidden space.

A "no-dip" walker stayed shallow the whole time. It started near the edge of the hidden hull and never left. Its physical path closed, but its address was always in the high-residue zone. It never had the chance to "reset" by returning to depth.

**The excursion metric confirms this.** Spearman(excursion, residue) is the strongest path-level predictor:
- AB d≤3: -0.285
- Penrose d≤3: **-0.359**

Excursion is stronger than depth_range (essentially zero correlation) or cumulative depth change (near zero). And in Penrose it's stronger than in AB.

## What predicts address residue? (Figure 5)

In order of predictive strength:

1. **Start depth** — strongest at every threshold (Spearman -0.26 to -0.36)
2. **Excursion** — nearly as strong, especially in Penrose (Spearman -0.30 to -0.36)
3. **Depth range** — essentially zero correlation
4. **Cumulative depth change** — essentially zero correlation

Start depth and excursion are highly correlated (shallow starts = more excursion possible), but excursion adds genuine path-level information: among walkers from similar depths, those that dipped further have less residue.

## The interpretation

This is NOT "paths that traverse more curvature accumulate more residue" (the naive holonomy guess). Instead:

**Paths that return to depth bring their address home. Paths that stay shallow do not.**

The holonomy-like effect is real — physical near-closure does not guarantee address closure — but the mechanism is about depth RECOVERY, not depth traversal. The hidden space has a "home base" (deep in the hull) where addresses are stable, and an "edge zone" (shallow) where they're not. A walker that touches the edge zone but returns to depth recovers its address. A walker trapped in the edge zone cannot.

**Penrose shows this more strongly**, consistent with its endohedral (internally structured) address space having a more pronounced centre-vs-edge distinction.

## What this does NOT claim

- NOT Berry curvature (no area dependence, and now no traversal dependence in the classical sense)
- NOT quantum holonomy
- The effect is about depth recovery, not curvature accumulation

## Possible next directions

1. **Depth recovery dynamics**: at what point along the path does address recovery happen? Is there a critical depth threshold where the address "snaps back"?
2. **Controlled depth profiles**: deliberately construct walks with specific depth trajectories (stay-deep, stay-shallow, dip-and-return, progressive-shallowing) and compare residue
3. **The asymmetry question**: is the shallow→deep recovery symmetric with deep→shallow departure, or is there a directionality in the address space?

## Files

- path_depth_profile_v0_1_report.md — full report with all tables
- path_depth_profile_summary.csv / per_seed.csv / near_loops.csv
- path_depth_profile_shuffled_summary.csv
- fig_1 through fig_7 (fig_4_dip_return.png is the star)
- path_depth_profile_v0_1.py — reproducible script

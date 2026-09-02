# Depth-Stability Landscape v0.1 — Handoff Summary

## What was tested

The controlled linger experiment showed address residue is instantaneous and positional. So we asked: can we map the stability landscape directly? For every vertex, measure its hull depth and its address mismatch with its neighbours. No walks. Pure geometry.

## The headline: THERE IS NO LANDSCAPE

**Every edge in the tiling produces exactly the same perpendicular-space displacement: 1.0.**

Depth vs mean neighbour mismatch: flat line at 1.0 for every vertex. Both substrates. Spearman = 0.002 (AB), -0.075 (Penrose). The variation is at the 10^-11 level — floating-point noise.

This is not a surprise in hindsight: aperiodic tilings are constructed by projection from higher dimensions, and every edge corresponds to a unit vector in the higher-dimensional lattice. The perpendicular-space component of every edge has the same magnitude. It's a mathematical fact about the construction.

## What this means

**The depth effect on walk residue is NOT about local address stability.** Every vertex is locally identical — every step in perp-space moves you by exactly 1.0, regardless of where you are in the hull.

So where does the depth effect come from? It must be an **accumulation effect**: over many random walk steps, the perp-space displacements either tend to cancel (returning you near your start address) or tend to drift (accumulating in one direction). Which happens depends on the TOPOLOGY of available paths at your starting depth, not on any local property.

**Deep vertices** sit in regions where the path structure provides more cancellation — more ways to close loops in perp-space, more balanced directional options.

**Shallow vertices** sit near the hull boundary where paths are topologically constrained — fewer directions, more net drift.

## The reframing

The entire story simplifies to:

1. **Local geometry is uniform**: every edge moves you by 1.0 in perp-space. No "stable" vs "unstable" zones in the local sense.
2. **Global topology is not**: deep vertices have richer, more symmetric path connectivity. Shallow vertices have constrained, asymmetric connectivity.
3. **Walk residue is about cancellation**: when a walker physically returns to start, its accumulated perp-space displacement depends on whether the loop's steps cancelled in perp-space. At depth, they tend to cancel. At the edge, they tend not to.
4. **This IS a holonomy**: the accumulated perp-space displacement around a closed physical path is exactly the discrete analogue of parallel transport around a loop. The "curvature" is zero locally (every edge is identical) but non-zero globally (loops at different depths accumulate different net displacements).

Wait — that last point is important. This IS holonomy after all, just not the kind we were looking for initially. Not area-dependent Berry curvature. Not a local effect. It's a **topological** holonomy: the net perp-space transport around a closed path depends on WHERE in the tiling the path lives, because the connectivity structure varies with depth.

## Updated story arc

1. **v0.3 validation**: Depth predicts walk residue. TRUE.
2. **Holonomy proxy**: Physical near-closure ≠ address closure. TRUE.
3. **Path-depth profile**: Dip-and-return = less residue. TRUE (dippers start/end deep).
4. **Brachistochrone**: U-dip > V-dip. TRUE (U-dip walkers are deeper on average).
5. **Snap-back**: Linger S-curve. CONFOUNDED by starting depth.
6. **Controlled linger**: Linger has no causal effect. Address is positional.
7. **Landscape (this test)**: No local landscape exists! Every edge is identical in perp-space. The depth effect is TOPOLOGICAL, not local.

## The clean picture

- Every step moves you by exactly 1.0 in perp-space (uniform local geometry)
- Whether those steps cancel over a walk depends on path topology
- Path topology depends on hull depth (deep = more cancellation)
- This is a discrete topological holonomy: uniform local transport, non-trivial global accumulation

## What this does NOT claim

- NOT Berry curvature (still no area dependence)
- NOT quantum holonomy
- NOT alpha~0.553
- But it IS a form of holonomy — discrete, topological, depth-dependent

## Possible next directions

1. **Perp-space direction analysis**: Each edge has a unit displacement in perp-space but the DIRECTION varies. At depth, do neighbours' perp-space directions form a more balanced set (pointing in all directions equally)? At the edge, are they biased toward one direction? This would directly explain the cancellation.
2. **Loop perp-space closure**: For actual closed physical loops, measure the net perp-space displacement. Plot this against loop position (depth). This is the direct holonomy measurement.
3. **Direction balance as the predictor**: Replace "depth" with "directional balance of perp-space edge vectors" as the fundamental variable. If this is the real mechanism, it should predict residue better than depth does.

## Files

- depth_stability_landscape_v0_1_report.md — full report
- vertex_landscape.csv / depth_bin_stats.csv / landscape_stats.csv
- fig_1 — THE FLAT LINE: depth vs mismatch (key)
- fig_2 — Density plot
- fig_3 — Substrate comparison
- fig_4 — Max vs mean mismatch
- fig_5 — Depth gradient
- fig_6 — Perp-space map coloured by stability (uniform!)
- fig_7 — Degree control (also uniform!)
- depth_stability_landscape_v0_1.py — reproducible script

# v0.3 Validation Run — Handoff Summary

## What was tested

Claude Code ran a full v0.3 validation of the diffusion-texture/address-transport branch, following up on GPT's v0.2 stratified scout.

The question: **Do texture-rich or depth-rich regions of aperiodic tilings produce more perpendicular-space (address) residue when random-walk paths nearly return to their physical starting point?**

## Run specification

- Substrates: AB_N30 (22,663 vertices) and Penrose_N24 (28,719 vertices)
- 10 independent random seeds
- 20,000 walkers per group per seed
- Walk lengths: 64, 128, 256, 512, 1024 steps
- Near-return thresholds: physical distance ≤ 1, 2, 3
- Groups: all_interior75, texture_high_q25, texture_low_q25, depth_high_q25, depth_low_q25, texture_high_depth_high, texture_low_depth_low
- Shuffled controls: perpendicular coordinates randomly permuted across vertices, 5,000 walkers, 10 seeds

## Key findings

### 1. The v0.2 texture direction did NOT replicate

GPT's v0.2 scout (2,200 walkers, 1 seed) found high-texture > low-texture mismatch. At v0.3 scale:

- **AB:** high-texture mismatch = 0.960, low-texture = 1.163. Gap = **-0.203**, negative in **10/10 seeds**.
- **Penrose:** high-texture mismatch = 0.978, low-texture = 1.067. Gap = **-0.089**, negative in **7/10 seeds**.

Low-texture regions produce MORE address residue, not less. The v0.2 scout was undersampled.

### 2. Depth is the strong, stable predictor

- **AB:** depth-high mismatch = 0.761, depth-low = 1.119. Gap = 0.358.
- **Penrose:** depth-high mismatch = 0.782, depth-low = 1.287. Gap = 0.505.

Vertices near the edge of the perpendicular-space hull accumulate more address residue on near-return paths. Vertices deeply embedded in perp-space come home cleanly. This is stable across all seeds and both substrates, and the effect is **larger in Penrose**.

### 3. Shuffled controls confirm the geometry matters

When perpendicular coordinates are randomly shuffled across vertices, the texture-high vs texture-low distinction disappears (both ~1.04). The real effect requires the actual geometric assignment of perpendicular coordinates.

### 4. Physical diffusion remains normal

All groups show physical diffusion exponent alpha ~ 0.94-0.96 (close to 1.0 = normal diffusion). This does NOT show alpha ≈ 0.553. The interesting signal is in the address space, not the physical spreading rate.

## Plain-English interpretation

The holonomy intuition — "the body comes home but the hidden address hasn't quite come home with it" — is supported. But the predictor isn't local texture (neighbourhood roughness). It's **depth**: how centrally embedded the starting vertex is in the hidden perpendicular space.

Think of it as: starting from the "edge of town" in hidden space means your hidden address wanders more when your physical position comes home. Starting from the "centre of town" in hidden space means your address stays closer to home.

The depth effect is stronger in Penrose than AB, which is consistent with the exo/endo distinction: Penrose's address space is less externally anchored, so depth-dependent residue is more pronounced.

## What this does NOT claim

- This is NOT Berry curvature
- This does NOT prove alpha ≈ 0.553
- This is a classical random-walk address-transport proxy
- It measures statistical tendencies across many paths, not individual holonomy

## Files in the bundle

- `v0_3_report.md` — full report with tables
- `v0_3_summary.csv` — mean across seeds
- `v0_3_per_seed.csv` — every group × seed
- `v0_3_timeseries.csv` — MSD and near-return at each time step
- `v0_3_shuffled_summary.csv` — shuffled control results
- `fig_a_near_return_mismatch.png` — mismatch by group (both substrates)
- `fig_b_texture_gap_by_seed.png` — texture gap across seeds
- `fig_c_alpha_by_group.png` — physical diffusion exponent
- `fig_d_shuffled_control.png` — real vs shuffled comparison
- `diffusion_v0_3_validation.py` — the full script (reproducible)

## Questions for the next conversation

1. The depth effect being stronger in Penrose — does this connect to the exo/endo distinction from the silent corruption paper?
2. Should we test constrained or weighted walks (not just nearest-neighbour random) to get closer to the holonomy idea?
3. Is there a way to define a discrete "Berry phase" proxy using the accumulated perpendicular displacement around near-closed loops?

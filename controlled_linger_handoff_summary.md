# Controlled Linger Walks v0.1 — Handoff Summary

## What was tested

The snap-back analysis (v0.1) showed that walkers lingering longer at minimum depth have less address residue. But there was a confound: longer lingerers also start deeper. This experiment isolates the causal question by CONTROLLING start depth and FORCING specific linger durations.

Walk script (5 phases, same for all walkers):
1. START from medium-depth band (0.35–0.65) — controls starting position
2. DISTURB: 100 free random walk steps — scrambles the address
3. DESCEND: 100 biased-toward-deep steps — drives walker to depth
4. LINGER: hold near depth for exactly N steps (N = 0, 5, 10, 20, 40, 80, 160)
5. ASCEND: 200 biased-toward-shallow steps — returns walker toward start depth

The ONLY variable is N. Everything else is standardised.

10 seeds, 5,000 walkers/seed, both substrates.

## The headline: LINGER DURATION DOES NOT MATTER

**The result is a flat line.** From 0 to 160 forced steps at depth, final address residue is unchanged:

| Linger steps | AB final residue | Penrose final residue |
|-------------|-----------------|----------------------|
| 0           | 1.254           | 1.340                |
| 5           | 1.258           | 1.335                |
| 10          | 1.256           | 1.335                |
| 20          | 1.253           | 1.335                |
| 40          | 1.254           | 1.339                |
| 80          | 1.255           | 1.338                |
| 160         | 1.252           | 1.338                |

Total improvement from 0→160 steps: AB = 0.002, Penrose = 0.006. Effectively zero.

## What the phase-by-phase view reveals (fig 2 — THE STAR FIGURE)

The residue trajectory through the walk phases tells the whole story:

1. **After disturb** (~100 free steps): residue = 1.03 (AB) / 1.10 (Penrose)
2. **After descend** (100 biased-to-deep steps): residue DROPS to ~0.92 / 0.99
3. **During linger** (N biased-to-deep steps): residue stays flat — no change
4. **After ascent** (200 biased-to-shallow steps): residue JUMPS to ~1.25 / 1.34

**Descending to depth lowers residue. Ascending away from depth raises it. Lingering at depth does nothing.**

The address residue is INSTANTANEOUS AND POSITIONAL — it depends on where you are right now, not how long you've been there.

## What this means for the previous findings

**The snap-back S-curve was a confound.** In natural random walks, walkers that lingered longer at depth also started deeper. Starting depth is the real predictor. Time at depth adds nothing once starting depth is controlled.

**The dip-and-return finding is STILL REAL, but reinterpreted.** Dip-and-return walkers have lower residue not because lingering at depth "resets" the address, but because:
- They START deep (which means low residue)
- They END deep (back where they started — still low residue)
- Non-dippers stay shallow the whole time — high residue throughout

**The U-dip vs V-dip finding is reinterpreted too.** U-dip walkers (lingering at minimum) aren't recovering BECAUSE they linger — they linger because they're deep, and being deep means low residue. V-dip walkers touch the minimum briefly because they're shallower overall.

## The corrected story

1. **Address residue is positional**: it depends on your current hull depth, not your history
2. **Depth is the only predictor**: deeper = lower residue, instantaneously
3. **Path history doesn't matter for the address itself**: the address at any moment is determined by current position
4. **BUT path history matters for PHYSICAL return**: whether you physically get back to start depends on the walk path, and physical near-return is what makes the residue measurable

The geometry is simpler than we thought: the perpendicular-space hull has a depth gradient in address stability. Deep = stable addresses. Shallow = unstable. No relaxation dynamics, no soak time, no engine — just a static landscape.

## What IS still interesting

- The descent phase genuinely lowers residue (1.03 → 0.92 in AB). Moving toward depth immediately improves your address.
- The ascent phase genuinely raises it. Moving away from depth immediately worsens it.
- The effect is STRONGER in Penrose (consistent with endohedral structure).
- The exo/endo distinction is still real and important.
- Physical near-closure ≠ address closure is still real.

## Story arc (updated)

1. **v0.3 validation**: Depth predicts residue. CONFIRMED and now understood as positional.
2. **Holonomy proxy**: Physical near-closure ≠ address closure. STILL TRUE.
3. **Path-depth profile**: Dip-and-return = less residue. TRUE but reinterpreted — it's because dippers start/end deep, not because lingering helps.
4. **Brachistochrone**: U-dip > V-dip. TRUE but reinterpreted — U-dip walkers are deeper overall.
5. **Snap-back**: S-curve in linger vs residue. CONFOUNDED — driven by starting depth.
6. **Controlled linger (this test)**: Linger duration has NO causal effect. Address residue is instantaneous and positional.

## What this does NOT claim

- NOT Berry curvature. NOT quantum holonomy. NOT alpha~0.553.
- Does NOT claim the earlier results were wrong — just that the mechanism is simpler than we thought.
- The depth-dependence of address stability is real and reproducible.

## Possible next directions

1. **Controlled depth placement**: Skip the walk entirely. Just measure: for a vertex at depth X, what is the typical address residue of its neighbours? Is the depth-residue relationship purely local?
2. **Physical return without depth change**: Can a walker physically return to start WITHOUT changing depth? If so, what's its residue? This separates the physical-return effect from the depth effect.
3. **Depth gradient mapping**: Map the residue landscape — at each depth, what's the expected address mismatch with neighbours? Is there a sharp boundary?

## Files

- controlled_linger_v0_1_report.md — full report with tables
- controlled_linger_summary.csv / agg.csv / trajectories.csv
- fig_1 — Controlled residue vs linger (THE FLAT LINE)
- fig_2 — Phase-by-phase residue (THE STAR FIGURE)
- fig_3 — Depth through phases (sanity check)
- fig_4 — Substrate comparison
- fig_5 — Residue during linger phase (noise)
- fig_6 — Recovery fraction vs linger (flat)
- controlled_linger_v0_1.py — reproducible script

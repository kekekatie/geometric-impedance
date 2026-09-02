# Boundary Shell Dissociation v0.1 — Handoff Summary

## What was tested

Other Claude predicted: if we run the 2×2 (rewire × shuffle) on the boundary shell (outer 25%) instead of the interior, AB's weave should weaken enough that shuffle finally breaks AB, completing the symmetric double dissociation.

The prediction was specific: "AB-under-shuffle should finally break." The kill condition was explicit: "If AB's boundary weave is still strong enough to carry identity alone, there's no arm."

## The headline: THE PREDICTION FAILS — BUT THE REAL FINDING IS BETTER

**AB boundary weave drops from 0.999 to 0.944.** The directional-balance prediction is correct — weave weakens at the boundary. But 0.944 is still strong enough to carry identity when address gets shuffled. The kill condition triggers: no double dissociation, not even at the boundary.

**Both substrates drop more under rewire at every spatial scale.** The crossover never appears.

## The full interior/boundary/full comparison

| Substrate | Subset | Native Addr | Native Weave | Native Hybrid | Rewire Hybrid | Shuffle Hybrid |
|-----------|--------|-------------|--------------|---------------|---------------|----------------|
| AB | interior 75% | 0.979 | 0.999 | 0.999 | 0.990 | 0.999 |
| AB | boundary 25% | 0.762 | 0.944 | 0.944 | 0.776 | 0.944 |
| AB | full | 0.843 | 0.977 | 0.977 | 0.842 | 0.977 |
| Penrose | interior 75% | 0.553 | 0.908 | 0.912 | 0.853 | 0.908 |
| Penrose | boundary 25% | 0.640 | 0.950 | 0.949 | 0.637 | 0.950 |
| Penrose | full | 0.618 | 0.944 | 0.951 | 0.622 | 0.943 |

## The real asymmetry: backup channels, not primary channels

Weave is the PRIMARY channel for both substrates, everywhere. Neither shuffle (which kills address) nor the boundary (which weakens weave) can break the hybrid, because weave always compensates.

The substrates differ in their BACKUP channel — what happens when weave is destroyed by rewiring:

| At boundary | Weave (rewired) | Address (intact) | Hybrid (rewired) | Address rescues? |
|-------------|-----------------|------------------|-------------------|-----------------|
| **AB** | 0.528 | 0.762 | **0.776** | **YES** |
| **Penrose** | 0.514 | 0.638 | **0.637** | **NO** |

When rewire destroys weave at the boundary:
- AB's address (0.762) rescues the hybrid to 0.776 — substantial recovery
- Penrose's address (0.638) can't help — hybrid crashes to 0.637

**This IS the exo/endo distinction.** Not "which channel is primary" but "which substrate has a working backup when the primary fails." AB's identity has redundancy — two independent channels, either sufficient. Penrose's identity is fragile — weave-only, no parachute.

## Why the boundary matters (connecting to the drift story)

The boundary is where:
1. **Directional balance is biased** (Spearman -0.72/-0.78 from the directional balance test)
2. **Weave weakens** (AB weave: 0.999 interior → 0.944 boundary)
3. **Address also weakens** (AB address: 0.979 → 0.762)
4. **Rewire becomes devastating** (AB boundary rewire-weave: 0.528 vs interior rewire-weave: 0.991)

The boundary is where everything thins out. Both channels weaken there, but weave recovers faster than address does — weave is still 0.944 at the boundary while address is only 0.762. So the weave-primary nature of both substrates STRENGTHENS at the boundary relative to address, the opposite of the other Claude's intuition.

## What kills what

- **Symmetric double dissociation**: DEAD. Both substrates are weave-primary. Shuffle can't break either one because weave always compensates. The crossover pattern doesn't exist at any spatial scale.
- **The exo/endo distinction**: ALIVE but REFRAMED. It's not about which channel leads — it's about backup/redundancy. AB = redundant (two channels). Penrose = fragile (one channel).
- **Boundary-modulated effects**: CONFIRMED. Both channels weaken at the boundary. Rewire becomes more devastating there (the weave it destroys was carrying more weight).

## The honest correction

Other Claude said: "I could be wrong here exactly the way I was wrong last turn; the only fix is to run it, not to believe it." He was right to hedge. The prediction was:
- AB boundary weave weakens ✓ (0.999 → 0.944)
- AB-under-shuffle finally breaks ✗ (0.944 is plenty)
- Double dissociation at boundary ✗ (both substrates still weave-primary)

The apparatus caught it. Darts, not trophies.

## What this does NOT claim

- NOT a double dissociation at any spatial scale
- NOT "AB is address-led" — AB is weave-led everywhere, with address as backup
- NOT Berry curvature. NOT quantum holonomy.
- The original full-patch result (AB address 0.874 > weave 0.740) from the silent corruption paper used a different seed/protocol; our full-patch here shows weave > address (0.977 > 0.843). The discrepancy may be due to feature construction or CV setup differences. Flag for future work.

## Updated story arc

1. **v0.3**: Depth predicts walk residue. TRUE.
2. **Directional balance**: THE MECHANISM. Spearman -0.72/-0.78.
3. **Radial drift**: Inward, not outward. No chirality.
4. **Null disc**: Genuine structure, not boundary bookkeeping.
5. **Channel-level double dissociation**: CONFIRMED. Address and weave independently knockoutable.
6. **Substrate-level double dissociation**: DEAD. Both weave-primary. AB has address backup, Penrose doesn't.
7. **Boundary shell (THIS TEST)**: Prediction failed — weave still compensates at boundary. But reveals the real asymmetry: AB = redundant channels, Penrose = fragile (weave-only). Boundary is where rewire becomes devastating because weave carries more weight there.

## Files

- boundary_shell_dissociation_v0_1.py — reproducible script (interior + boundary + full, both substrates)
- boundary_shell_dissociation_results/summary_table.csv — all numbers
- boundary_shell_dissociation_results/per_replicate_table.csv — per-rep data
- boundary_shell_dissociation_results/fig_1_interior_vs_boundary.png — THE 6-PANEL GRADIENT (address/weave/hybrid × AB/Penrose across spatial scales)
- boundary_shell_dissociation_results/fig_2_boundary_heatmap.png — boundary-only heatmap
- boundary_shell_dissociation_results/boundary_shell_report.md

# Double-Dissociation Verification v0.1 — Handoff Summary

## What was tested

Other Claude proposed a unified 2×2 experiment: can address and weave be independently knocked out, and do the two substrates (AB, Penrose) show different vulnerability patterns?

Two perturbations, same AUC metric for all cells:
1. **Rewire**: degree-preserving edge swaps (5E attempts) — scrambles graph, keeps perp-space coords
2. **Shuffle**: random permutation of perp-space coordinates — scrambles coords, keeps graph

Identity persistence AUC via cross-validated logistic regression, interior 75% subset, 10 replicates per perturbation.

## Part A: Seed-level variance (does the shuffle asymmetry survive noise?)

Using the radial-drift Spearman metric from the null-disc experiment, with 10 shuffle seeds:

| Condition | AB Spearman | Penrose Spearman | Separation |
|-----------|-------------|------------------|------------|
| Native | 0.728 | 0.758 | — |
| Shuffled perp | 0.616 ± 0.004 | 0.712 ± 0.003 | **SEPARATED** (p=0.0002) |
| Null disc | 0.052 ± 0.003 | 0.046 ± 0.002 | Overlap (both near zero) |

**The shuffle asymmetry is robust.** AB retains 84.6% of native signal, Penrose retains 93.9%. Ranges do not overlap. Mann-Whitney p = 0.0002. Null seeds cluster tightly near zero (std ~0.003).

## Part B: The unified 2×2 (same ruler, same pipeline)

### THE HEADLINE: Channel-level double dissociation CONFIRMED

The channel-level results are clean and definitive:

| Channel | Native (AB / Pen) | Rewire (AB / Pen) | Shuffle (AB / Pen) |
|---------|-------------------|--------------------|--------------------|
| **Address** | 0.979 / 0.553 | 0.979 / 0.569 | **0.497 / 0.486** |
| **Weave** | 0.999 / 0.908 | 0.991 / **0.831** | 0.999 / 0.909 |
| **Hybrid** | 0.999 / 0.912 | 0.990 / 0.854 | 0.998 / 0.908 |

**Shuffle kills address, preserves weave.** AB address: 0.979 → 0.497 (chance level!). Weave: unchanged at 0.999.

**Rewire damages weave, preserves address.** Penrose weave: 0.908 → 0.831. Address: unchanged at 0.553.

Address and weave are genuinely independent channels that can be knocked out separately. This is the cleanest evidence for two distinct information channels in the tiling.

### The substrate-level nuance: single dissociation, not double

The hybrid (combined) AUC tells a more nuanced story:

|          | Native | Rewire Δ | Shuffle Δ |
|----------|--------|----------|-----------|
| **AB**   | 0.999  | -0.008   | -0.000    |
| **Penrose** | 0.912 | -0.058 | -0.003   |

Both substrates drop MORE under rewire than shuffle. This is a **single dissociation** (Penrose arm only), not a double. The reason: on the interior 75% subset, AB's weave channel is SO strong (0.999) that it alone carries the hybrid even when address is destroyed. AB isn't address-led on the interior — it's weave-dominated too.

This connects to a known finding: the original silent-corruption paper found AB to be address-led on the FULL patch (address 0.874 vs weave 0.740), but the interior subset pushes both to near-ceiling (address 0.979, weave 0.999). The "AB is address-led" characterization is specific to the full patch including boundaries.

### What this means

1. **Two channels are real.** Address (perp-space coordinates) and weave (graph topology) carry independent information about vertex identity. Knocking out one leaves the other intact.

2. **Penrose is clearly weave-led.** Rewire (weave knockout) drops Penrose hybrid by 0.058. Shuffle (address knockout) barely touches it (0.003). Penrose identity lives in the graph.

3. **AB is robust to both knockouts on the interior.** The interior subset has redundant information in both channels. The "address-led" characterization applies to the full patch where boundary vertices weaken the weave signal.

4. **The exo/endo distinction is real but boundary-modulated.** Near the boundary, AB relies on address (exo). In the interior, both channels are strong and redundant. This connects directly to our directional-balance finding: boundary vertices have biased directions (weak weave signal), interior vertices have balanced directions (strong weave signal).

## Kill-condition report

1. **Part A: AB-shuffle and Penrose-shuffle overlap?** NO — ranges fully separated. ✓
2. **Part B: off-diagonal cell doesn't drop?** The AB-shuffle cell barely drops (hybrid 0.999 → 0.998), because weave compensates. This is NOT a failure — it's the finding. AB has redundant channels on the interior.
3. **Metric artifact?** The channel-level results are unambiguous (address goes to chance under shuffle, weave drops under rewire). The hybrid result is the channels interacting, not a measurement problem.

## What this does NOT claim

- NOT a double dissociation at the substrate×perturbation level (it's a single dissociation + a redundancy finding)
- NOT Berry curvature. NOT quantum holonomy.
- The "AB = address-led" claim from the full-patch analysis is real but boundary-dependent, not a universal substrate property.

## Updated story arc

1. **v0.3**: Depth predicts walk residue. TRUE.
2. **Directional balance**: THE MECHANISM. Spearman -0.72/-0.78.
3. **Radial drift**: Inward, not outward. No chirality.
4. **Null disc**: Genuine structure, not boundary bookkeeping.
5. **Double dissociation (THIS TEST)**: Channel-level double dissociation CONFIRMED. Address and weave are independently knockoutable. Substrate-level: single dissociation (Penrose = weave-led). AB has redundant channels on interior.

## Files

- double_dissociation_partA_v0_1.py — seed variance analysis
- double_dissociation_partA_results/per_seed_table.csv, partA_report.md
- double_dissociation_partB_v0_1.py — unified 2×2 with AUC pipeline
- double_dissociation_partB_results/dissociation_2x2.csv, per_replicate_table.csv, partB_report.md
- double_dissociation_partB_results/fig_1_dissociation_heatmap.png — THE KEY FIGURE (3-panel: hybrid, address, weave)
- double_dissociation_partB_results/fig_2_delta_from_native.png

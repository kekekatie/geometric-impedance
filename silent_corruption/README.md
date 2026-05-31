# Silent Corruption in Aperiodic Substrates - v3 Matched-Scale Bundle

## What's in this bundle

This package contains the matched-scale validation for the Silent Relational Corruption paper, with apples-to-apples comparison of AB and Penrose substrates.

### Paper
- `relational_corruption_v3_matched_scale.md` - Updated paper with matched-scale results

### Figures
- `figure1_identity_vs_fresh_2x2.png` - 2x2 panel: Identity vs Fresh reconstruction for both substrates
- `figure2_ab_vs_penrose_identity.png` - Direct comparison of identity persistence AUC
- `figure3_comparison_table.png` - Summary comparison table

### AB v0.8 Results (22,663 full / 16,997 interior-75%)
- `large_ab_v0_8_5E_compact.csv` - Compact results table
- `large_ab_v0_8_5E_summary.csv` - Summary statistics
- `large_ab_v0_8_5E_report.md` - Full report

### Penrose v0.2 Results (28,719 full / 21,539 interior-75%)
- `large_penrose_v0_2_5E_compact.csv` - Compact results table
- `large_penrose_v0_2_5E_summary.csv` - Summary statistics
- `large_penrose_v0_2_5E_replicates.csv` - Per-replicate data
- `large_penrose_v0_2_5E_verification.csv` - Substrate verification
- `large_penrose_v0_2_5E_report.md` - Full report

### Analysis Code
- `large_penrose_v0_2_5E_audit.py` - Penrose audit script
- `generate_comparison_figures.py` - Figure generation script

## Key Results

| Metric | AB (N=16,997) | Penrose (N=21,539) |
|--------|---------------|-------------------|
| Identity Address AUC | **0.986** | 0.661 |
| Identity Hybrid AUC | 0.989 | **0.855** |
| Fresh Weave AUC | 0.892 | 0.912 |
| Edge Jaccard | 0.0001 | 0.0001 |

**The exo/endo split holds at matched scale:**
- AB identity is *address-led* (near-ceiling AUC)
- Penrose identity is *weave/hybrid-led* (address alone is weak)
- Fresh reconstruction is *weave-led* on both substrates

## Audit Parameters

- **Rewiring intensity:** 5E (5 × edge count) attempted swaps per replicate
- **Replicates:** 10 per substrate
- **Subsets:** Full patch + interior-75% (to avoid boundary effects)
- **Features:** Address (perp-space coords) + Weave (graph-local metrics)

---
Generated: 2026-05-30
K. T. Niedzwiecki

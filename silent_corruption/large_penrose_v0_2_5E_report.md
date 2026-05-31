# Large Penrose v0.2: Full-strength 5E validation

Apples-to-apples matched validation for the Silent Relational Corruption paper.
This matches the AB v0.8 protocol: 5E rewiring, 10 replicates.

## Inputs

- Vertices: 28719
- Edges: 54695
- Rewiring attempts per replicate: 273475
- Replicates: 10
- Address features: perp_x, perp_y, perp_r, k_sum_mod5
- Weave features: g_degree, g_neighbor_degree_mean, g_local_clustering, g_hop2_size

## Verification

| subset | active N | native core | graph priv | euclid priv | packet priv |
|---|---:|---:|---:|---:|---:|
| full_28719 | 28719 | 821 | 7060 | 7096 | 6371 |
| interior_75pct | 21539 | 208 | 4993 | 4815 | 5270 |

## Compact Results

AUC values are means over rewired replicates.

| subset | active N | native core | identity address | identity weave | identity hybrid | fresh address | fresh weave | fresh hybrid | fresh/native Jaccard | native-core retention |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| full_28719 | 28719 | 821 | 0.662 | 0.590 | 0.660 | 0.517 | 0.911 | 0.912 | 0.003 | 0.003 |
| interior_75pct | 21539 | 208 | 0.661 | 0.830 | 0.855 | 0.524 | 0.912 | 0.914 | 0.003 | 0.005 |

## Interpretation

This full-strength 5E audit provides apples-to-apples comparison with AB v0.8.

Key questions:
1. Does Penrose remain weave-led for identity persistence (not address-led like AB)?
2. Does fresh reconstruction remain weave-led on both substrates?
3. Is the interior subset well-behaved (enough positives for reliable CV)?

## Cautions

- This is a classical substrate diagnostic, not a quantum code simulation.
- The interior subset uses radial distance from center; a boundary-distance metric might be better.

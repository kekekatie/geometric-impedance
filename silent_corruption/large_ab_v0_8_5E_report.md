# Large AB v0.8: full-strength 5E interior validation

Classical substrate-integrity validation on the 22,663-node Ammann–Beenker tetragrid lift. This run uses full-strength degree-preserving rewiring: `5 × E` attempted swaps per replicate, with 10 replicates, comparing the full finite patch against central/interior subsets. It is not a quantum-code simulation.

## Inputs

- Node table: `clean_ab_full_raw_lift(5).csv` (22,663 vertices)
- Edge table: `large_ab_v0_6_edges.csv` (44,126 edges)
- Rewiring attempts per replicate: 220,630
- Rewired replicates: 10
- Mean accepted swaps: 220547.6
- Mean edge Jaccard after rewiring: 0.000112

## Compact result

AUC values are means over rewired replicates, except identity-address rows which are static because address features and native identity labels do not change across rewired replicates.

| subset | active N | native core | best identity address AUC | identity weave AUC | identity hybrid AUC | fresh address AUC | fresh weave AUC | fresh hybrid AUC | fresh/native Jaccard | native-core retention |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| all_22663 | 22663 | 1569 | 0.874 | 0.740 | 0.889 | 0.542 | 0.890 | 0.888 | 0.0031 | 0.0035 |
| interior_75pct | 16997 | 752 | 0.986 | 0.991 | 0.989 | 0.542 | 0.892 | 0.890 | 0.0043 | 0.0053 |
| interior_50pct | 11332 | 466 | 0.998 | 1.000 | 1.000 | 0.541 | 0.892 | 0.889 | 0.0058 | 0.0073 |

## Read

On the full finite patch, enriched address features give identity AUC 0.874, while rewired weave gives 0.740 and hybrid gives 0.889. This confirms the large-patch address advantage, but it is not the small-AB near-ceiling result across the whole finite patch.

Interior restriction restores near-ceiling identity legibility: interior_75pct gives address 0.986, weave 0.991, hybrid 0.989; interior_50pct gives address 0.998, weave 1.000, hybrid 1.000. This supports a boundary-contamination explanation for the full-patch wobble, but it also shows that interior weave becomes highly predictive, so the interior result is not address-only proof.

Fresh reconstruction remains robustly weave-led. Address-only prediction stays near chance for fresh regenerated cores, while weave and hybrid remain high. Fresh/native overlap and native-core retention are near zero under 5E relational scrambling, confirming that fresh cores are new present-tense structures, not the native core rediscovered.

## Cautions

- The interior subsets are central subsets of one finite AB patch, not independently generated AB tilings. They diagnose boundary contamination; they do not by themselves establish a full finite-size scaling law.
- The enriched address features are derived from the available full lift. They are close analogues of the small-AB feature set but may not be identical to the original feature construction.
- This remains a classical graph/substrate audit, not a quantum error-correcting-code simulation.

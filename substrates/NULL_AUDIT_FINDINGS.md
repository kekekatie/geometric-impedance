# Null-control audit of the v3 weave results

Run: 2026-07-31. Substrate: locally generated Ammann-Beenker patch
(22,451 vertices / 44,604 edges — matched to the v3 AB substrate at
22,663 / 44,126). Interior-75% subset, 5E degree-preserving rewiring,
3 replicates. Reproduce with:

```
python3 generate_ab.py --extent 37 --prefix ab
python3 audit_with_nulls.py --reps 3
```

## Result table

| arm | graph | features | AUC |
|---|---|---|---|
| identity | native | address | 0.9141 |
| identity | rewired tiling | weave | 1.0000 |
| identity | rewired tiling | hybrid | 1.0000 |
| identity | rewired tiling | **weave minus degree family** | **0.4997** |
| identity | rewired tiling | degree family only | 1.0000 |
| fresh | rewired tiling | weave | 0.9051 |
| fresh | rewired tiling | address | 0.5296 |
| fresh | rewired tiling | **weave minus degree family** | **0.4996** |
| fresh | **config model, no geometry** | weave | **0.9018** |
| leakage | rewired tiling | nbr_degree_mean alone → packet_priv | 0.9994 |
| leakage | rewired tiling | hop2_size alone → graph_priv | 0.6546 |

The `fresh / weave` figure of 0.9051 reproduces the v3 AB value of 0.892,
confirming the pipeline here is a faithful reproduction of the v3 protocol.

## Finding 1 — §5.4 does not survive a null

A configuration-model graph carrying the same degree sequence but no tiling
ancestry of any kind returns 0.9018, statistically indistinguishable from the
0.9051 obtained on the rewired tiling. The fresh-reconstruction AUC therefore
carries no information about the substrate.

The mechanism is algebraic rather than statistical. After 5E rewiring the graph
is locally tree-like, so the closed-neighbourhood retention score reduces to

    packet_score(i) ≈ 2 / (1 + mean_neighbour_degree(i))

which is a monotone function of `WEAVE_COLS[1]`. One of the three top-quartile
filters generating the label is a relabelling of a feature subsequently supplied
to the classifier (empirically: AUC 0.9994). Removing the degree-family features
drops the fresh audit to 0.4996 — chance. No signal survives the ablation, so
§5.4 cannot be rescued by feature selection; the reported effect is the leak.

## Finding 2 — the identity *weave* channel has the same problem

Identity labels are fixed on the native graph, so they cannot leak from the
rewired graph's topology — but degree-preserving rewiring preserves the degree
sequence exactly, and the native label is itself degree-driven by the same
algebra. Consequently the identity weave channel scores 1.0000 with the degree
family present, 1.0000 with the degree family alone, and 0.4997 with it removed.

The identity weave channel is measuring the one property the perturbation was
designed not to destroy. This affects the v3 claim that Penrose identity is
"weave/hybrid-led" (weave 0.830, hybrid 0.855): those numbers are most likely
the preserved degree sequence, not a relational blueprint.

## Finding 3 — the headline result is untouched, and gets stronger

The address channel uses perpendicular-space coordinates, which are neither
degree features nor recoverable from the rewired graph. It is unaffected by
either leak (0.9141 here on native; 0.5296 at chance for fresh reconstruction,
as v3 reports). The exo/endo contrast — AB 0.986 vs Penrose 0.661 — stands.

It also sharpens. If the weave-based numbers are degree bookkeeping, then the
address channel is the *only* thing carrying identity through relational
scrambling, and Penrose's apparent hybrid rescue to 0.855 disappears. Penrose
is then more exposed to silent relational corruption than v3 currently claims,
not less. The paper's thesis survives the correction; its supporting sections
do not.

## Scope and caveats

- Run on a locally generated AB substrate, not the v3 input files, which are not
  in the repository (`large_penrose_v0_2_5E_audit.py` reads them from a local
  Windows path). Penrose was not tested directly.
- The leakage algebra is substrate-independent — it holds for any sparse graph
  that is locally tree-like after rewiring — so it is expected to transfer, but
  the exact Penrose figures need the original lift and edge files.
- 3 replicates rather than 10. Replicate variance is small (SD < 0.01) and the
  effects here are large, but the final numbers should be run at 10.

## Suggested next steps

1. Rerun `audit_with_nulls.py` against the original AB and Penrose inputs.
2. Withdraw §5.4 and the fossil-record / living-ecology passages in §5.4 and
   §6.2, or replace the retention surrogate with a measure that is not a local
   degree functional (random-walk return mass or a spectral quantity).
3. Requalify the Penrose weave and hybrid identity figures in §5.2 and the
   hybrid-rescue claim in §5.3 and §6.2.
4. Report the address AUC as invariant by construction rather than as a
   replicate mean with SD 0.000 (it is the static row, `replicate == -1`).
5. Add the full-patch figures alongside interior-75% as a robustness row.

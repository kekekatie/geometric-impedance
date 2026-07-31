# Null-control audit of the v3 weave results

Run: 2026-07-31. Interior-75% subset, 5E degree-preserving rewiring, 3 replicates.

Run twice: once on a locally generated Ammann-Beenker patch (22,451 vertices /
44,604 edges), and once on the **original v3 AB substrate** (22,663 / 44,126).
The AB edge list was rebuilt from the K0–K3 lift coordinates using the audit's
own adjacency rule; it returns exactly 44,126 edges and reproduces the lift
file's own `degree` column on all 22,663 vertices with zero mismatches.

```
python3 generate_ab.py --extent 37 --prefix ab      # synthetic substrate
python3 audit_with_nulls.py --reps 3

python3 audit_with_nulls.py --lift real_ab_lift.csv --edges real_ab_edges.csv \
    --address-cols perp_x,perp_y,perp_r,k_sum_mod4 --reps 3
```

## Reproduction check against published v3 figures

Run on the original AB substrate, interior-75%:

| Quantity | v3 published | reproduced here |
|---|---|---|
| identity / address | 0.9790 | 0.9792 |
| identity / weave | 0.9914 | 0.9910 |
| identity / hybrid | 0.9894 | 0.9901 |
| fresh / weave | 0.8923 | 0.8886 |
| fresh / address | 0.5541 | 0.5524 |

The harness is a faithful reproduction of the v3 protocol, so the null results
below apply to the published analysis and not to a variant of it.

## Result table (original AB substrate)

| arm | graph | features | AUC |
|---|---|---|---|
| identity | native | address | 0.9792 |
| identity | rewired tiling | weave | 0.9910 |
| identity | rewired tiling | **weave minus degree family** | **0.5002** |
| identity | rewired tiling | degree family only | 0.9910 |
| fresh | rewired tiling | weave | 0.8886 |
| fresh | rewired tiling | address | 0.5524 |
| fresh | rewired tiling | **weave minus degree family** | **0.4967** |
| fresh | **config model, no geometry** | weave | **0.8977** |
| leakage | rewired tiling | nbr_degree_mean alone → packet_priv | 0.9991 |

Note that identity / weave (0.9910) and identity / degree-family-only (0.9910)
are the same number to four decimal places.

## Confirmation on the original Penrose topology

The Penrose lift file was not available, so the full audit could not be run —
but the leakage mechanism needs only the adjacency, and it is present:

| Quantity | value |
|---|---|
| edge Jaccard, native vs 5E rewired | 0.000064 |
| Spearman, packet_score vs 2/(1 + mean neighbour degree) | 0.9993 |
| packet_priv predicted by mean neighbour degree alone | AUC 0.9993 |

## Result table (synthetic AB substrate)

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

On the original AB substrate, a configuration-model graph carrying the same
degree sequence but no tiling ancestry of any kind returns 0.8977 — slightly
*higher* than the 0.8886 obtained on the rewired tiling itself. The
fresh-reconstruction AUC therefore carries no information about the substrate.

The mechanism is algebraic rather than statistical. After 5E rewiring the graph
is locally tree-like, so the closed-neighbourhood retention score reduces to

    packet_score(i) ≈ 2 / (1 + mean_neighbour_degree(i))

which is a monotone function of `WEAVE_COLS[1]`. One of the three top-quartile
filters generating the label is a relabelling of a feature subsequently supplied
to the classifier (AUC 0.9991 on AB, 0.9993 on Penrose). Removing the
degree-family features drops the fresh audit to 0.4967 — chance. No signal
survives the ablation, so §5.4 cannot be rescued by feature selection; the
reported effect is the leak.

## Finding 2 — the identity *weave* channel has the same problem

Identity labels are fixed on the native graph, so they cannot leak from the
rewired graph's topology — but degree-preserving rewiring preserves the degree
sequence exactly, and the native label is itself degree-driven by the same
algebra. Consequently, on the original AB substrate, the identity weave channel
scores 0.9910 with the degree family present, 0.9910 with the degree family
alone, and 0.5002 with it removed. The published 0.9914 is the degree sequence.

The identity weave channel is measuring the one property the perturbation was
designed not to destroy. This affects the v3 claim that Penrose identity is
"weave/hybrid-led" (weave 0.830, hybrid 0.855): those numbers are most likely
the preserved degree sequence, not a relational blueprint.

## Finding 3 — the headline result is untouched, and gets stronger

The address channel uses perpendicular-space coordinates, which are neither
degree features nor recoverable from the rewired graph. It is unaffected by
either leak (0.9792 on the original AB substrate, matching the published 0.9790;
and 0.5524 — chance — for fresh reconstruction, as v3 reports). The exo/endo
contrast, AB 0.986 vs Penrose 0.661, stands.

It also sharpens. If the weave-based numbers are degree bookkeeping, then the
address channel is the *only* thing carrying identity through relational
scrambling, and Penrose's apparent hybrid rescue to 0.855 disappears. Penrose
is then more exposed to silent relational corruption than v3 currently claims,
not less. The paper's thesis survives the correction; its supporting sections
do not.

## Scope and caveats

- The full audit ran on the original AB substrate and on a synthetic one, with
  matching results. Penrose was confirmed only at the mechanism level: its lift
  file (`clean_penrose_full_raw_lift.csv`) is still needed for x/y positions and
  perpendicular-space coordinates, without which the Euclidean seed sets and the
  address channel cannot be built.
- Expected Penrose outcome once the lift is available: identity weave 0.830 and
  hybrid 0.855 collapse toward chance under the degree-family ablation, leaving
  address-only 0.661 as the substrate's entire identity channel.
- 3 replicates rather than 10. Replicate variance is small (SD < 0.01) and the
  effects here are large, but the final numbers should be run at 10.

## Suggested next steps

1. Rerun `audit_with_nulls.py` against the original Penrose inputs (AB is done).
2. Withdraw §5.4 and the fossil-record / living-ecology passages in §5.4 and
   §6.2, or replace the retention surrogate with a measure that is not a local
   degree functional (random-walk return mass or a spectral quantity).
3. Requalify the Penrose weave and hybrid identity figures in §5.2 and the
   hybrid-rescue claim in §5.3 and §6.2.
4. Report the address AUC as invariant by construction rather than as a
   replicate mean with SD 0.000 (it is the static row, `replicate == -1`).
5. Add the full-patch figures alongside interior-75% as a robustness row.

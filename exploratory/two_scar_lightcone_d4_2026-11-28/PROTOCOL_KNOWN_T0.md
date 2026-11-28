# Pre-Registered Follow-Up Protocol: Known-Onset ($t_0$) Ablation on `d=(4,4)` Two-Scar Pairs

*Branch: `experiment/two-scar-lightcone-d4-2026-11-28`. Frozen before running any known-$t_0$ scoring.*

## Question (Astra's Timing-vs.-Space Ablation)
In `5b4384b`, even spatially disjoint scar pairs with zero Ring-2 overlap and zero short logical bridges (`Pen_sep`: `1.136×`, `AB_sep`: `1.354×`) showed pure $k=2$ super-additivity under simultaneous unknown onset $t_0 \in \{1, 2\}$, while `AB_touch` (which also has 2 shared weight-5 logical bridges) reached `1.590×`.

To separate **shared-clock timing coupling** from **spatial / bridge coupling**, we replay the exact same `(3,3)` bounded decoder (`nd_infer.py` untouched, `p = 0.001`, exhaustive $k \le 2$, 0 mismatches on full-table spot checks) with the true onset time $t_0 \in \{1, 2\}$ **revealed** to both `thick`/`ring1`/`ring2_z` and `thin` across the four pure-$k=2$ pairs and their six unique single-scar baselines:

- **Penrose (`Pen_d4_mid`, `n=26`):** `Pen_sep (q9, q11)`, `Pen_touch (q3, q9)`, and single-scar baselines `q3, q9, q11`.
- **Ammann–Beenker (`AB_2scar`, `n=31`):** `AB_sep (q12, q18)`, `AB_touch (q5, q12)`, and single-scar baselines `q5, q12, q18`.

## Pre-Registered Checks
- **T1 (Timing link at a distance):** On `Pen_sep` and `AB_sep`, revealing $t_0$ collapses $R_{AB}$ sharply toward `1.00×` (showing that shared onset timing alone coupled two spatially disjoint scars).
- **T2 (Spatial bridge residual):** On `AB_touch`, a clear super-additive residual ($R_{AB} > 1.00\times$) survives even with $t_0$ known, cleanly isolating the spatial contribution of its 2 shared weight-5 logical bridges from the shared-clock effect.

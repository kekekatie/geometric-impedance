# Decision-gate concordance — statistic & configuration set per gate

**Companion to physical-radius v6, MSD v7, conditional-null v3.** Which aggregate statistic and
which configuration set each decision gate uses. `δ_cap` = 95th percentile of the 200-draw
capacity distribution of `M₉` (physical §6). All at reference radius r=16, coherent engine unless
noted.

**Statistics.** `M₉` = per-offset median across the **nine** family×tier configs, then median
across the six offsets. `M_perm,7` = the same over the **seven permutation-feasible** configs
(silver×3, golden×3, platinum e20; platinum e16/e18 excluded — six-offset audit). `Δ_ap =
M₉,address − M₉,parity`.

| gate | question | statistic | reference distribution | threshold | denominator handling | config set |
|---|---|---|---|---|---|---|
| **G0** boundary | packet stays interior on [0,8]? | `t_bound*` | — | `> 8` (strict) | — | global (all launches, both engines) |
| **G1** quality | is β a good power-law fit? | median `R²_fit` | — | `≥ 0.90` | — | per (config, engine); failing cell → descriptive |
| **G2** permutation null | address beyond a motif-conditional shuffle? | `M_perm,7,address` | B=1000 constrained-permutation MC null | one-sided `p<0.05` | none (difference) | **`M_perm,7`** (feasible cells only) |
| **G3** capacity | above the pipeline noise floor? | `M₉,address` | 200-draw capacity `M₉` | `> δ_cap` | none | **`M₉`** |
| **G4** shuffle-kill | killed by the sealed stratified shuffle? | `(M₉,plain−M₉,shuf)/M₉,plain` | — | `≥ 0.70` | `M₉,plain ≤ δ_cap` or `≤0` → undefined → mixed | **`M₉`** |
| **G5** classical contrast | not reproduced by the classical walk? | classical `M₉,address` | — | `≤ 0.2 × coherent M₉,address` | coherent `≤ δ_cap` or `≤0` → undefined → mixed; classical G1 fail → inconclusive | **`M₉`** |
| **G6** residual null | orthogonal-to-`X_r` content present? | deterministic `M₉` of `ΔR²_resid` | `δ_cap` | `> δ_cap` (lower-bound detection, not a test) | none | **`M₉`** |
| **G7** vs parity | beyond representation repackaging? | `Δ_ap` | `δ_cap` | **descriptive only** ("compatible with collapse" iff `Δ_ap ≤ δ_cap`) | none | **`M₉`** (descriptive) |
| **G8** per-config secondary | which configs individually? | per-config `T_c` | B=1000 permutation, Westfall–Young step-down max-T | adjusted `p̃` | — | per config (secondary) |

**"Transport" earned** iff **G0 ∧ G1 ∧ G2 ∧ G3 ∧ G4 ∧ G5 ∧ G6** pass; **G7** descriptive; **G8**
secondary. Any undefined-denominator route → **mixed/undetectable**. Physical-radius outcomes
(compression / representational / stable-residual / mixed / infeasible) use the same statistics:
compression from `M₉,address` at r=2 vs r=16 with `δ_cap`+`ρ*`; representational from `Δ_ap` (G7);
stable-residual from G3+G6+G2(`M_perm,7`)+G7.

*Not part of the scientific record until reviewed and merged.*

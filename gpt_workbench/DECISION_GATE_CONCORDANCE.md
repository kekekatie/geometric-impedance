# Decision-gate concordance — statistic & configuration set per gate

**Companion to physical-radius v7, MSD v8, conditional-null v4.** Which aggregate statistic and
which configuration set each decision gate uses. `δ_cap` = 95th percentile of the 200-draw
capacity distribution of `M₉` (physical §6) — a capacity detection floor, **not** a threshold for
`address − parity`. All at reference radius r=16, coherent engine unless noted.

**Statistics (membership fixed a priori — never changed by observed dynamics).** `M₉` = per-offset
median across the **nine** family×tier configs, then median across the six offsets. `M_perm,7` = the
same over the **seven permutation-feasible** configs (silver×3, golden×3, platinum e20; platinum
e16/e18 excluded by the geometry-only six-offset audit). `Δ_ap = M₉,address − M₉,parity`
(descriptive). `q_ref` = the constrained-permutation reference tail `(1+#{null ≥ obs})/(B+1)`,
`B=1000` — **extremeness under the algorithmic reference, not exact-conditional significance.**

| gate | question | statistic | reference | threshold | denominator handling | config set |
|---|---|---|---|---|---|---|
| **G0** boundary | packet stays interior through t=8? | `t_bound*` | — | admissible iff `> 8` (strict); `≤ 8` → finite-size | — | global (all launches, both engines), computed before β |
| **G1** quality | is β a good power-law fit? | median `R²_fit` | — | `≥ 0.90` | — | per (config, engine); a failing cell → **descriptive & global claim downgraded**, `M₉` membership **unchanged** |
| **G2** permutation stress | address beyond the constrained shuffle? | `M_perm,7,address` | B=1000 constrained-permutation (distance-weighted, k=32, λ=1.0) **stress reference** | `q_ref < 0.05` (extremeness, not significance) | none (difference) | **`M_perm,7`** (7 feasible cells; infeasible never pass) |
| **G3** capacity | above the pipeline noise floor? | `M₉,address` | 200-draw capacity `M₉` | `> δ_cap` | none | **`M₉`** (9 cells) |
| **G4** shuffle-kill | killed by the sealed stratified shuffle? | `R_kill` = **paired** `red_{c,o}=(plain−shuf)/plain` aggregated by `M₉` | — | `R_kill ≥ 0.70` | any fold/config `plain ≤ δ_cap` or `≤0` → `red` undefined → mixed | **`M₉`** (paired) |
| **G5** classical contrast | not reproduced by the classical walk? | classical `M₉,address` | — | `≤ 0.2 × coherent M₉,address` | coherent `≤ δ_cap` or `≤0` → mixed; classical G1 fail → inconclusive | **`M₉`** |
| **G6** residual null | orthogonal-to-`X_r` content present? | deterministic `M₉` of `ΔR²_resid` | `δ_cap` | `> δ_cap` (lower-bound detection, not a test) | none | **`M₉`** |
| **G7** vs parity | beyond representation repackaging? | `Δ_ap` | — | **DESCRIPTIVE ONLY — no threshold, no gate** (`δ_cap` not valid for `Δ_ap`) | — | **`M₉`** (descriptive) |
| **G8** per-config secondary | which configs individually? | per-config `T_c` | B=1000 permutation, Westfall–Young step-down max-T over the **7 feasible cells** | extremeness `q̃` | — | per config (7 feasible; platinum e16/e18 descriptive) |

**"Transport" earned** iff **G0 ∧ G1 ∧ G2 ∧ G3 ∧ G4 ∧ G5 ∧ G6** pass; **G7** descriptive; **G8**
secondary. Any undefined-denominator route → **mixed/undetectable**. A G1 coherent failure downgrades
the global claim (it never recomputes `M₉`). Physical-radius outcomes (compression / representational
/ **survives-stress-controls** / mixed / infeasible) use the same statistics: compression from
`M₉,address` at r=2 vs r=16 with `δ_cap`+`ρ*`; "compatible with representation collapse" from `Δ_ap`
(G7, descriptive); "survives the frozen stress controls" (replaces "stable residual") from
G3 + G6 + G2(`M_perm,7`), with G7 reported descriptively — **no categorical "irreducible" verdict.**

*Not part of the scientific record until reviewed and merged.*

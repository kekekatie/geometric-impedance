# DRAFT v6 — `physical(r)` / radius-saturation manifest (STANDALONE)

**Status — DRAFT for crew review. NOT sealed, NOT run. Only geometry-only checks were run (no
dynamics/address/LDOS/targets/scores). No science-branch file altered.** This manifest is
**self-contained**: every definition needed to reproduce the design is stated here without relying
on earlier versions.

**v6 (2026-08-31)** applies Sol's second pre-seal pass: precise outer-fold parity scaler; Group E
empty-neighbourhood convention; `δ_cap` ratified (95th percentile of the 200-draw nine-config `M₉`
capacity distribution); parity comparison aligned to the descriptive downgrade. Builds on the
standalone v5. Full dated change log at the end.

*Source: drafted by the `gpt/workbench` Claude collaborator from crew decisions relayed by Katie;
not part of the scientific record until reviewed and merged.*

---

## 1. Frozen conventions
- **`ℓ := median edge length`** (one scalar per patch; measured `= 1.000` for all families).
  "Radius `r`" means Euclidean parallel-space distance `≤ r·ℓ` unless a group says otherwise.
- **Radius ladder** `S = {2, 4, 8, 12, 16}`, for all families including golden. `S(r) = {s∈S: s≤r}`,
  `m(r) = |S(r)|`.
- **Evaluated population:** the `d_bound ≥ 16ℓ` common interior set (`d_bound(i) = hull_depth(par)[i]`,
  the signed distance of vertex i to the convex hull of the patch's parallel-space points). **Fixed
  across all rungs** within a tier — changing `r` changes only which columns are included, never
  which vertices are scored.
- **Six frozen offsets:** `(0.13,0.37) (0.29,0.11) (0.41,0.23) (0.05,0.47) (0.19,0.31) (0.37,0.09)`.
- **Regressor (frozen, all rungs/controls/families):** `sklearn.ensemble.HistGradientBoostingRegressor(
  max_depth=3, max_iter=250, learning_rate=0.06, l2_regularization=1.0, random_state=0)`.
- **Moment conventions (frozen):** for a sample `x`: `mean`; `variance` (population, ddof=0);
  `skewness = E[(x−μ)³]/σ³`; `excess kurtosis = E[(x−μ)⁴]/σ⁴ − 3`. If `σ < 1e-9`, the three higher
  moments are set to 0.

## 2. The baseline `X_r` and the increments (unambiguous)
**`X_r := [ M3 , physical_extra(r) ]`.**
- **`M3`** (the sealed transport baseline, always retained **in full**) `= [dens, deg,
  edge_len_mean, edge_len_var, motif one-hot (width = shared codebook across offsets), g(1.6),
  g(2.6), ψ_N, ψ_{N/2}, ψ_{2N}, g(4.0), g(6.0)]`, where `dens`/`g(ρ)` are vertex counts within
  Euclidean radius ρ, `ψ_n(i) = |mean over incident bonds of exp(i n θ)|`, and the motif one-hot
  encodes the vertex-star type (canonical sorted multiset of incident `(star-line, sign)`).
  `dim(M3) = 11 + |codebook|`.
- **`physical_extra(r)`** = the nested radius block of §3 (dims **11/22/35/48/61** for
  r = 2/4/8/12/16).
- **Dedup (frozen):** drop a `physical_extra(r)` column **only** if bit-identical (`max|Δ| < 1e-12`
  on the evaluated set) to an M3 column; **never** drop an M3 column.
- **Every increment** `ΔR²_• = R²(X_r + •) − R²(X_r)`, held-out (§5), with `•` ∈ {address =
  `_m4_cols(perp)` (11 cols); parity block (§4); capacity block (§6); `X_r`-orthogonal address
  residual (conditional-null manifest §2)}.

## 3. `physical_extra(r)` column groups (address-free; prefix `phys_`)
Neighbourhood `Nb(i,s) = {j ≠ i : ‖par[j]−par[i]‖ ≤ s·ℓ}` (via `cKDTree.query_ball_point`).

### Group A — radial histogram g(ρ), right-closed bins
- Centre **excluded**; bin index **`k = ceil(d/ℓ − τ)`, `τ = 1e-9`, `k = 1 … r`**.
- Bin `k` = the **left-open, right-closed** annulus **`((k−1)ℓ, kℓ]`** (to `τ`). Exact unit-edge
  neighbours (`d=ℓ`) → bin 1; sub-edge thin-rhombus diagonals (`≈0.52–0.77ℓ`) → bin 1; **rung `r`
  never uses any point beyond `rℓ`**. `phys_gann_k = #{j≠i : bin(j)=k}`. **r columns.**
- (Geometry-checked: min inter-vertex distance 0.765/0.618/0.518 ℓ for silver/golden/platinum;
  bin-1 occupancy ≈ 4.7–5.5 — the innermost bin is non-empty and retained.)

### Group B — neighbour-degree moments within each `s ∈ S(r)`
For each `s`, the sample `{deg[j] : j ∈ Nb(i,s)}` (if empty, `{deg[i]}`); columns
`phys_nbrdeg_{mean,var,skew,exkurt}_s{s}`. **4 columns × m(r).**

### Group D — coarse-grained bond-orientational order within each `s ∈ S(r)`
`phys_psi{n}_cg_s{s} = mean_{j∈{i}∪Nb(i,s)} ψ_n(j)` for `n ∈ {N/2, N, 2N}`. **3 columns × m(r).**

### Group E — packing/void via padded-super-patch Voronoi within each `s ∈ S(r)`
Voronoi-cell areas of the parallel-space point set (§3a): `phys_voro_{mean,var}_s{s} =
mean/var_{j∈Nb(i,s)} area[j]` over the **bounded** cells in `Nb(i,s)`. **2 columns × m(r).**
**Empty-neighbourhood convention (frozen; never expected for deep r16 vertices):** if `Nb(i,s)`
contains no bounded cell, set `phys_voro_mean_s{s} = area[i]` (the vertex's own cell area) and
`phys_voro_var_s{s} = 0`.

### Exact dimensions
`dim(physical_extra(r)) = r + 9·m(r)`:

| r | m(r) | A | B(×4) | D(×3) | E(×2) | **total** |
|---|---|---|---|---|---|---|
| 2 | 1 | 2 | 4 | 3 | 2 | **11** |
| 4 | 2 | 4 | 8 | 6 | 4 | **22** |
| 8 | 3 | 8 | 12 | 9 | 6 | **35** |
| 12| 4 | 12| 16 | 12 | 8 | **48** |
| 16| 5 | 16| 20 | 15 | 10 | **61** |

Strictly nested. (Edge-length moments are **excluded** from `physical_extra(r)` — unit-rhombus
edges make them degenerate — and appear only as a pre-labelled robustness diagnostic.)

### 3a. Padded-super-patch Voronoi + convergence (mandatory)
Voronoi cells are computed on a **padded super-patch** generated at `core extent + Δ`, then
restricted to core vertices, so every cell contributing to a core descriptor is bounded/uncensored
(preflight: with padding, zero core cells remain invalid). **Frozen: `Δ ≥ 4`, padding ring width
`≥ 3ℓ`** (observed 10–16 ℓ); if a family/tier cannot afford `≥3ℓ` (generator too slow/saturated),
flag it — do not reduce Δ. **Convergence check** (`pad_convergence_check.py`): per-core-cell area
and perimeter at `Δ=4` vs `Δ=6` agree to worst-case **1.2e-12 (area) / 3.5e-15 (perimeter)**
relative — identical to machine precision (a cell depends only on its Delaunay neighbours, which
`Δ=4` already includes). Pass tolerance = **1e-6 relative**. `Δ=4` validated.

## 4. Parity control — z_N rejected; (degree, Voronoi-area) adopted
- **z_N rejected (measured):** the complex bond-orientational order is near-**constant** on the deep
  interior (`Var(Re z_N) ≈ Var(Im z_N) ≈ 0` on every tier); a near-constant field through `_m4_cols`
  gives near-constant, noise-amplified columns — inadequate.
- **Adopted parity field: `(local graph degree, padded-Voronoi-cell area)`**, passed through the
  exact 11-column `_m4_cols` pipeline (shell-mean + shell-variance at {2,4,8} + gradient + a
  hull-depth of the field cloud). Both are physical quantities already in the physical family
  (degree, Voronoi area), so this tests **repackaging**, not new content.
  - **Outer-fold scaler (frozen, precise):** for each family×tier **outer fold**, fit the z-score
    scaler (per-component mean/std) on the **pooled five training offsets' r16 common sets** and
    apply it **unchanged** to the held-out offset. No held-out data enters the scaler.
  - **Rank-2 verified on every planned patch:** covariance eigenvalues ≈ 0.29–0.55 / 1.45–1.72,
    condition 2.6–6.0. (For deep `r16` vertices padded = core Voronoi area to machine precision, §3a.)
  - **Zero-variance rule (frozen):** if either physical component's within-set std `< 1e-9` on a
    patch, that patch's **representation-parity verdict is marked unavailable / infeasible and
    reported** — the capacity control is **not** substituted (they answer different questions:
    capacity guards column-count inflation; parity guards representational repackaging). No patch
    triggered this.

## 5. Validation
- **Outer (primary):** leave one of the six offsets out **entirely**; features are geometry-only,
  the held-out offset's targets are never seen.
- **Replication level:** the **six offsets are the sampling clusters**; the six leave-one-offset-out
  estimates are **correlated through their overlapping training sets** and are never treated as
  independent replicates — inference uses the randomisation test of conditional-null manifest §4.
- **Inner CV (frozen):** within each *training* patch, PC1 of the centred `r16` common-set
  coordinates → project → **4 contiguous equal-count slabs**; **inner fold `j` simultaneously holds
  out slab `j` from every training-offset patch**, outer offset wholly unseen. Frozen: PCA centring
  = subtract common-set mean; PC1 sign `PC1[0] ≥ 0` (else `PC1[1] ≥ 0`); **ties broken by
  lexicographic order of the integer lift coordinates** `lifts[i]`; remainder vertices to the
  lowest-index slabs. **Floor (verified): all nine tiers pass** `r16 ≥ 400` (min 581) and every slab
  `≥ 100` (min 148).

### 5b. Balance diagnostic — source→destination locality (replaces the vacuous version)
Standardised means before/after an address permutation are identical **by construction** and prove
nothing. Instead, for the local permutation null (conditional-null §3), report for each assigned
**source→destination pair**: the **median, 95th-percentile and maximum standardised physical-feature
distance**; the **per-feature absolute source−destination differences**; **exact motif
preservation** (must be 100%); the **fraction of fixed points / singletons**; the **fraction of
groups requiring k-escalation**; and a **comparison against an unrestricted within-motif shuffle**
(to show the local assignment moves the address markedly *less* far). `k = 32` is **primary**;
`k ∈ {16, 64}` are **balance-sensitivity diagnostics only**, never selected after outcomes.

## 6. Capacity control and `δ_cap`
- **Capacity null:** **200 independent i.i.d.-Gaussian blocks** of the same dimensionality as the
  parity block, **seeds `0…199`**; report the **full distribution** and the summary (mean, 95th
  percentile) of the increment.
- **`δ_cap` (RATIFIED — empirical pipeline detection / noise floor, NOT a practical-equivalence
  margin):** each of the 200 Gaussian draws is run through the **exact same nine-config aggregate
  statistic `M₉`** used for address (per-offset median across the nine configs, then median across
  the six offsets — conditional-null §4); `δ_cap` = the **95th percentile** of those 200 `M₉`
  values. Detection floor only — not evidence of zero. The old fixed `0.005` margin is **deleted**.

## 7. Hierarchical decision procedure (evaluated in order)
1. **Infeasible** — a tier's `r16` common set `< 400`, a slab `< 100`, a required physical-size
   match unmet, **or the local conditional null infeasible for that patch (>5% singletons)**. →
   that cell's permutation-null result is unavailable; report, do not interpret its permutation test.
2. **Mixed / undetectable** — configs disagree beyond the null uncertainty, **or** `ρ` is undefined
   (`ΔR²(2)` non-positive, `< δ_cap`, or sign-unstable). → mixed, **never "infeasible."**
3. **Compression (at the pipeline's resolution)** — the fade rule holds: `ΔR²(2)` positive,
   sign-stable (≥5/6), `> δ_cap`; `ΔR²(16) < δ_cap`; and `ρ = ΔR²(16)/ΔR²(2) < ρ* = 0.25`. **Not
   proof the true effect is zero.** "CI includes zero" is never accepted as equivalence.
4. **Compatible with representation collapse (descriptive)** — the paired difference
   `Δ_ap = M₉,address − M₉,parity ≤ δ_cap` though the increment survives radius. Parity is
   deterministic (no null), so this is a **preregistered descriptive** comparison with **no
   significance threshold**; not proof of equality.
5. **Stable residual** — `M₉,address > δ_cap`, `Δ_ap > δ_cap`, the residual-orthogonal null passes
   (`ΔR²_resid > δ_cap`, a lower-bound detection check), **and** the permutation null passes on
   `M_perm,7` (conditional-null §6). → provisional irreducible increment.

## 8. Geometry-matched tiers (measured; morphology flagged)
| tier | patch | n | hull area | diameter | **aspect(r16)** | usable r16 area | r16 (min) |
|---|---|---|---|---|---|---|---|
| small  | silver e14 / golden e18 / platinum e16 | 3360/3999/3651 | 2753/3272/2977 | 61.4/95.9/80.2 | 1.02/**3.12**/1.25 | 516/452/569 | 653/581/725 |
| medium | silver e16 / golden e20 / platinum e18 | 4341/4913/4604 | 3552/4032/3726 | 70.0/106.5/88.6 | 1.04/**3.07**/1.27 | 885/794/921 | 1102/1012/1165 |
| large  | silver e18 / golden e22 / platinum e20 | 5463/5920/5660 | 4478/4840/4554 | 78.8/116.7/99.9 | 1.02/**2.98**/1.25 | 1370/1210/1345 | 1698/1535/1704 |

Matched on r16 count and usable area. **Golden's r16 interior is elongated (aspect ≈ 3.0);
reported as a morphology diagnostic/control — it is NOT added as a regression feature**, and the
ladder stays through r=16 for golden (not a radius-12 ceiling). The PCA-slab inner CV (§5) handles
the elongation.
**⚠️ Platinum small/medium local-null infeasibility (finalised by the six-offset audit,
`SIX_OFFSET_AUDIT_REPORT.md`):** singletons **8.9–9.8% (e16)** and **5.1–6.2% (e18)** on **all six
offsets** — consistently > 5%. Their **local permutation null is infeasible**; they retain the `M₉`
family (plain increment, residual null, parity, capacity) but the permutation reference is
**`M_perm,7`** over the seven feasible configs (silver×3, golden×3, platinum e20). Crew may accept
this, re-tier platinum upward (breaks r16-count matching), or ratify a different threshold.

## 9. Open choices for crew
- `δ_cap` (§6, ratified) and `ρ* = 0.25` (classification heuristic) accepted?
- Platinum small/medium → `M_perm,7` (§8) accepted, or re-tier?
- **Permutation-null locality (blocker):** at `k=32` the constrained shuffle ≈ an unrestricted
  within-motif shuffle (conditional-null §9) — reduce `k`, use distance-weighted costs, or rename
  the null *motif-conditional*?
- Golden aspect-3.0 extra boundary control (§8)?

---
## Change log
**v6 — 2026-08-31** (Sol 2nd pre-seal pass): specified the **outer-fold parity scaler** exactly
(pooled five training offsets, applied unchanged to held-out); added the **Group E
empty-neighbourhood convention**; **ratified `δ_cap`** as the 95th percentile of the 200-draw
nine-config `M₉` capacity distribution (detection floor only); aligned the parity comparison to the
**descriptive downgrade** (`Δ_ap ≤ δ_cap`, no significance threshold); and finalised the platinum
small/medium **`M_perm,7`** policy from the six-offset audit.

**v5 — 2026-08-31** (Sol pre-seal, standalone): made the manifest self-contained (restored the full
Group A/B/D/E definitions, moment conventions, padded-super-patch construction + convergence rule,
regressor parameters and dimensions); defined the baseline **`X_r = [M3, physical_extra(r)]`** with
M3 always retained + dedup rule and rewrote all increments as `R²(X_r+•)−R²(X_r)`; renamed
`δ*`→**`δ_cap`** (a detection floor built from the same aggregate statistic; deleted the 0.005
fallback); replaced the vacuous balance diagnostic with **source→destination distance statistics**
(§5b); repaired the hierarchical tree (local-null-infeasibility → infeasible; `ρ` undefined →
mixed/undetectable; "compatible with … at the pipeline's resolution"); removed broken `§A5`
references; and cleaned the duplicated change-log entry.

**v4 — 2026-08-29** (narrow closure). **v3 — 2026-08-29** (audit A1–A8). **v2 — 2026-08-29** (crew
A1–A11). **v1 — 2026-08-28** (initial column manifest).

*End of draft v6. Committed to `gpt/workbench` only. Nothing sealed; only geometry-only checks run;
no science-branch file altered.*

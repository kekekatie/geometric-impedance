# DRAFT v6 — MSD transport-endpoint manifest (radius-saturation stage-two, STANDALONE)

**Status — DRAFT for crew review. NOT sealed, NOT run. Only synthetic engineering benchmarks were
run (no study geometry/dynamics/address/LDOS/targets/β/outcomes). No science-branch file altered.**
This manifest is **self-contained**.

**v6 (2026-08-31)** restores the definitions shortened in v5, froze the time-grid details, removed
optionality, and removed the mid-band secondary from the sealable endpoint (points 8–9). Full dated
change log at the end.

*Source: drafted by the `gpt/workbench` Claude collaborator from crew decisions relayed by Katie;
not part of the scientific record until reviewed and merged.*

---

## 1. Physical setup (frozen)
- **Hamiltonian** `H = A` — the tiling adjacency (uniform hopping, `ħ = 1`, `J = 1`). The
  perpendicular-space address appears **nowhere** in `H`; it enters only later as an analysis
  feature. (Edge-length-weighted `H` is a robustness variant only.)
- **Distance** Euclidean parallel-space `‖par[v] − par[v0]‖`.
- **Boundary** `d_bound(i) = hull_depth(par)[i]` (signed distance of i to the patch's par-space
  convex hull), per vertex. **Unit** `ℓ = median edge length`; time in units `ħ/J`. All constants
  a-priori.

## 2. Launch-site selection (frozen)
- **Admission `d_bound(v0) ≥ 16ℓ`** — launches come from the same `d_bound≥16ℓ` common set the
  radius manifest evaluates.
- **Deterministic, spatially-balanced subsample: `L = 200` per patch, `L/4 = 50` per PCA slab**
  (the 4 slabs of physical manifest §5). Within each slab, sort by `(PC1 projection, lift-coordinate
  lexicographic)` and take **evenly-spaced** indices to the per-slab quota. No address used. If a
  patch's common set has `< 200`, use all of it (all nine tiers have `≥ 581`, so `L=200` is met).
- Every selected launch yields a `β(v0)`; nothing downstream culls sites (§7).

## 3. Initial state (frozen) — unfiltered, full-spectrum
`|ψ0⟩ = |v0⟩` (unit amplitude on `v0`, zero elsewhere): exactly localised, `MSD(0)=0`,
`P_strip(0)=0`. It spans the **full spectrum**. **This is a full-spectrum wavepacket-transport
test — NOT a mid-band test**, and it does not by itself establish the mid-band LDOS mechanism
(§8). *The mid-band-projected secondary is removed from this sealable endpoint (see §11).*

## 4. Algorithm (frozen, benchmark-ratified)
- **Primary: sparse/block Krylov propagation** (`scipy.sparse.linalg.expm_multiply`), validated vs
  exact diagonalisation to `max|Δ| = 3.4e-15` on synthetic graphs spanning the planned size/degree
  range — **sufficient; no family-specific toy validation required** (it would needlessly touch
  study substrates). Exact diagonalisation is **not** the production method (its per-vertex/all-time
  reconstruction is `O(n²·L·T)`, intractable).
- **Frozen constants:** `L = 200`; **launch-batch size 50**; propagate once on the **shared 161-point
  boundary grid** (§5) per batch and **reduce each time-slice on the fly** to the scalars `MSD(t;v0)`
  and `P_strip(t;v0)` — never materialise the `(T×V×L)` tensor (benchmark peak RSS ~1.6 GB, ~170 min
  over 54 patches × both engines). Numerical tolerances in §9.

## 5. Time grids and boundary detection (frozen)
- **Boundary-monitoring grid:** the **linear grid `linspace(0, 8, 161)`, `Δt = 0.05`** — drives the
  whole propagation.
- **β-fit grid:** the **48 log-spaced times on `[2,8]` snapped to the nearest boundary-grid points**
  — the exact snapped list is **generated and stored pre-seal** at
  `gpt_workbench/snapped_beta_times.txt` (checked: **48 unique** values, **max snap error 0.0231**).
  The fit uses the **actual snapped times**, not the unsnapped ideal times; the implementation
  **asserts 48 unique values**.
- **Boundary strip (frozen):** `STRIP := { v : d_bound(v) < w·ℓ }`, **`w = 2`**.
  `P_strip(t) = Σ_{v ∈ STRIP} |ψ_t(v)|²`; **excess mass** `ΔP_strip(t) = P_strip(t) − P_strip(0)`
  (per-destination hull-depth strip; for the interior primary launch `P_strip(0)=0`).
- **Boundary crossing:** the earliest monitoring-grid time with `ΔP_strip(t) ≥ 0.01`.
- **`t_bound*` = the earliest crossing over all selected launches, all families/tiers/offsets, and
  both engines** — a single global endpoint.
- **Primary β fit uses the fixed interval `[2,8]` only if `t_bound* ≥ 8`.** If `t_bound* < 8`, the
  primary transport endpoint is **finite-size-limited — no shortening, retuning or rescue after
  seeing results**.

## 6. MSD and exponent (frozen)
`MSD(t;v0) = Σ_v |ψ_t(v)|² · ‖par[v] − par[v0]‖²` (`= ΔMSD` for the primary since `MSD(0)=0`).
With `MSD(t) ∝ t^{2β}`, **`β(v0) = ½ · slope`** of an OLS fit of `log MSD` on `log t` over the
**snapped `[2,8]` grid points** (§5). Record `R²_fit(v0)` as a diagnostic. β = 1 ballistic,
½ diffusive, `<½` sub-diffusive; critical states `0 < β < 1`.

## 7. Missingness and admission checks (frozen; both engines)
- **Every admitted launch yields a `β`.** There is **no per-site `R²_fit` / curvature / dynamics-
  derived exclusion** (such a filter could correlate with the address). Admission uses only
  `d_bound`.
- **Address-correlated-admission check:** admission by `d_bound` is not assumed address-independent
  — report and test the admitted vs excluded population's M4-feature distributions; any imbalance is
  a stated caveat.
- **Aggregate quality stop (per engine):** if the median `R²_fit` across admitted launches `< 0.90`
  for an engine, that engine's exponent is **descriptive** (no transport claim); this is a whole-
  engine verdict, never a per-site cull.
- All rules apply to **both** the coherent and classical engines on the **same common window**.

## 8. Aggregation and inference (offset-level randomisation)
The per-vertex target `{β(v0)}` replaces `ld_primary` in the identical `transport_run.py` nested
M0→M4 pipeline (with the `M4shuf`/`M3pos`/`M4pos`/`M3far`/`M4far` controls, the parity and capacity
controls, and the conditional nulls), for both engines and all family×tier configs. **Inference is
the offset-level randomisation test of conditional-null manifest §4–§5:** the six leave-one-offset-
out increments are **not** independent replicates; the primary statistic is the median across the
nine family×tier configs then across the six offsets; the one-sided
`p = (1 + #{M_null ≥ M_obs})/(B+1)` with **`B = 1000`** and `α = 0.05`; **all six offset effects and
signs are always reported**; ≥5/6 positive is a supporting criterion.

## 9. Numerical tolerances (frozen, precise)
- **State/probability agreement:** the production propagator (Krylov) must match an exact-
  diagonalisation reference on a synthetic graph to **`max|ψ_t(v) − ψ_t^{exact}(v)| ≤ 1e-10`**
  (observed `3.4e-15`) at shared grid times, checked pre-seal.
- **Norm / probability conservation:** coherent `| ‖ψ_t‖² − 1 | ≤ 1e-8` at every grid time;
  classical `| Σ_v p_v(t) − 1 | ≤ 1e-8` and `p_v(t) ≥ −1e-10`. A patch/time violating these is
  flagged, not silently used.

## 10. Classical null engine (frozen) — continuous-time Markov generator
`Q = A·D⁻¹ − I` (`D = diag(deg)`; column-stochastic: columns of `Q` sum to 0). `Q_{vw} = A_{vw}/deg_w`
for `v≠w`, `Q_{ww} = −1` (unit exit rate; stationary `π ∝ deg`). `p(t;v0) = e^{Qt} e_{v0}` (valid
for all real `t ≥ 0`, via the same Krylov method), `MSD_cl(t;v0) = Σ_v p_v(t;v0)·‖par[v]−par[v0]‖²`.
Same grids, same window (§5), same OLS exponent → `β_cl`. Time axis matched to the quantum engine
(unit exit rate ↔ `J=1`). Expected diffusive, address-blind.

## 11. Removed: mid-band secondary (point 9)
The mid-band-projected state `|χ0⟩ = P_W|v0⟩/‖·‖` requires constructing the spectral projector
`P_W` (`|E|∈[0.8,2.5]`), which **reintroduces an eigendecomposition / spectral-filter problem the
Krylov benchmark did not resolve**. It is **removed from this sealable endpoint** and preserved only
as a **future, separately preregistered mechanistic study** requiring a specified and benchmarked
spectral-filter algorithm (e.g. a polynomial/Chebyshev band-pass with its own numerical validation).
The primary full-spectrum transport endpoint is unaffected.

## 12. Decision threshold and claim wording
The endpoint is met only if the coherent primary statistic (§8) is significant by the randomisation
test, is **killed by the stratified shuffle** (`M4shuf` consistent with 0; ≥70% of the plain
increment removed), is **not reproduced by the classical engine** (`β_cl` increment ≤ 0.2× the
coherent), **exceeds** the parity and capacity detection floors, **survives both conditional nulls**,
and the aggregate gates pass (median `R²_fit ≥ 0.90` per engine; global `t_bound* ≥ 8`).

**Claim wording (frozen):** at most —
> *"The address representation predicts heterogeneity in full-spectrum wavepacket spreading beyond
> the frozen physical descriptions and controls."*

**No inference that perpendicular space is a literal physical degree of freedom.**

**Classical-diagnostic caveat:** if the **classical** power-law diagnostic fails (median `β_cl`
`R²_fit < 0.90`), the **coherent-vs-classical contrast is inconclusive** — this does **not** erase a
well-defined quantum β result, but it **prevents the strongest coherence-specific claim**.

**Authorised non-positive outcomes:** shuffle-not-killed → "reads multiscale geometry, not cleanly
the address"; `t_bound* < 8` → **finite-size-limited** (legitimate, not a failed run); randomisation
non-significant → the address signal does not surface in spreading at this size/coupling. No family
ordering; no perp-space ontology.

## Appendix LR — retired analytic bound (documented failed diagnostic)
`t_hi ≈ 0.12–0.90` at every family/extent/launch-depth (preflight v2), extent-invariant at fixed
depth, ~145ℓ depth needed for `t_hi=8`. Retained for transparency; **never** an admissibility gate.

## 13. Open choices for crew
- Whether platinum small/medium (permutation-null-infeasible per conditional-null §9) affect the
  MSD endpoint's config set the same way.

---
## Change log
**v6 — 2026-08-31** (Sol pre-seal, standalone): restored the full boundary-strip / excess-mass /
exponent / engine / admission definitions self-contained; **froze the time-grid** — stored the
48-point snapped β-time list (48 unique, max error 0.0231), fit against the **actual snapped times**
with an assert of 48 unique values, and froze `L=200`, batch 50, `Δt=0.05`, `B=1000`, **removing the
optional L=400 / tighter-Δt / B=5000 language**; defined **boundary crossing as `ΔP_strip ≥ 0.01`**;
stated **precise numerical tolerances** (state ≤1e-10, norm/probability conservation ≤1e-8); and
**removed the mid-band secondary** from the sealable endpoint, preserving it only as a future
separately-preregistered spectral-filter study (pts 8–9).

**v5 — 2026-08-29** (closure + actual-grid benchmark). **v4 — 2026-08-29** (audit B1–B7).
**v3 — 2026-08-29** (crew B1–B8). **v2 — 2026-08-28** (four-blocker repair). **v1** initial.

*End of draft v6. Committed to `gpt/workbench` only. Nothing sealed; only synthetic benchmarks run;
no science-branch file altered.*

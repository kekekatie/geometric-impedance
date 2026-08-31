# DRAFT v8.1 — MSD transport-endpoint manifest (radius-saturation stage-two, STANDALONE)

**Status — DRAFT for crew review. NOT sealed, NOT run. Only synthetic engineering benchmarks +
geometry/feature diagnostics were run (no study geometry/dynamics/address/LDOS/targets/β/outcomes).
No science-branch file altered.** Self-contained, incl. the embedded snapped β-time list (§5).

**v8 (2026-08-31)** applies Sol's third pre-seal pass: **G1 no longer changes `M₉` membership** (the
nine-config primary is fixed a priori; a G1 failure downgrades the global claim, never recomputes
`M₉`); shuffle-kill is now a **paired fold/config reduction then aggregate** (not
difference-of-medians); permutation tail renamed **`q_ref`** (extremeness, not significance);
Westfall–Young over the **seven** feasible cells; finite-size at **`t_bound* ≤ 8`**. Builds on v7.
**v8.1 (2026-08-31)** applies the external-scout claim audit (implication 3, documentation-only): **G5
is relabelled cross-engine non-reproduction** and **"coherence-specific" is removed as an earned
verdict** — a G5 pass is engine-specific (coherent `H=A` vs the degree-normalised CTMC `Q=A·D⁻¹−I`)
and does not isolate coherence from generator choice. No endpoints, thresholds, other gates,
denominators, config sets or runtime design changed; the top-line claim is unchanged.
Full dated change log at the end.

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
- **β-fit grid (embedded; the manifest is self-contained):** the 48 log-spaced times on `[2,8]`
  **snapped to the nearest boundary-grid point** — **48 unique** values, **max snap error 0.0231**.
  The fit uses these **actual snapped times** (not the unsnapped ideal times); the implementation
  **asserts exactly 48 unique values**. A copy is also stored at `snapped_beta_times.txt`.
  ```
  2.0000 2.0500 2.1000 2.2000 2.2500 2.3000 2.4000 2.4500 2.5500 2.6000 2.7000 2.7500
  2.8500 2.9500 3.0000 3.1000 3.2000 3.3000 3.4000 3.5000 3.6000 3.7000 3.8500 3.9500
  4.0500 4.2000 4.3000 4.4500 4.5500 4.7000 4.8500 5.0000 5.1500 5.3000 5.4500 5.6000
  5.8000 5.9500 6.1500 6.3000 6.5000 6.7000 6.9000 7.1000 7.3000 7.5500 7.7500 8.0000
  ```
- **Boundary strip (frozen):** `STRIP := { v : d_bound(v) < w·ℓ }`, **`w = 2`**.
- **Boundary sums stated separately per engine:**
  - coherent: `P_strip(t) = Σ_{v ∈ STRIP} |ψ_v(t)|²`;
  - classical: `P_strip,cl(t) = Σ_{v ∈ STRIP} p_v(t)`.
  - **excess mass** `ΔP_strip(t) = P_strip(t) − P_strip(0)` (and `ΔP_strip,cl` likewise); for the
    interior primary launch `P_strip(0) = 0`.
- **Boundary crossing:** a launch/engine **crosses** at the earliest monitoring-grid time (including
  `t = 8`) with `ΔP_strip(t) ≥ 0.01`.
- **`t_bound*`** = the earliest crossing over **all** selected launches, all families/tiers/offsets,
  **and both engines** — a single global endpoint. If **no** launch/engine crosses on the entire
  grid through and including `t = 8`, `t_bound*` is recorded explicitly as **"no crossing observed"**
  (`t_bound* = +∞`).
- **The global boundary gate is computed BEFORE any β-based inference** (it depends only on
  `ΔP_strip`, not on β or any target).
- **Primary β fit uses the fixed interval `[2, 8]` only if `t_bound* > 8`** — i.e. **strictly**: no
  crossing anywhere on the grid *through and including* `t = 8` (a crossing at exactly `t = 8` would
  contaminate the final fit point 8.0000). Equivalently, admissible iff `t_bound* =` "no crossing
  observed". **If any crossing occurs at or before `t = 8`, the primary transport endpoint is
  finite-size-limited — no shortening, retuning or rescue after seeing results** (an authorised
  outcome, §12).

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
- **Aggregate quality stop — scope frozen: per (family×tier configuration, engine).** For each
  config and engine, the median `R²_fit` over that config's admitted launches **pooled across the
  six offsets** (a whole-`(config,engine)` verdict, never a per-site cull; not global-engine-wide,
  not per-patch).
- **G1 must NOT change the frozen `M₉` membership (critical).** `M₉` **always** aggregates all nine
  configs; its membership is fixed a priori and is **never** recomputed from observed fit quality
  (doing so would make the statistic data-dependent and differ between engines, invalidating
  comparisons). Exact global consequences of a G1 failure:
  - if a **coherent** config has median `R²_fit < 0.90`, that config is **descriptive** and the
    **global strongest transport claim fails or is downgraded** — `M₉` is **not** silently
    recomputed over the surviving cells;
  - if a **classical** config fails, the **cross-engine non-reproduction (G5) comparison is
    inconclusive** (failure of the specified classical comparator makes it inconclusive); again
    `M₉` membership is unchanged.
- All rules apply to **both** the coherent and classical engines on the **same common window**.

## 8. Aggregation and inference (offset-level randomisation)
The per-vertex target `{β(v0)}` replaces `ld_primary` in the identical `transport_run.py` nested
M0→M4 pipeline (with the `M4shuf`/`M3pos`/`M4pos`/`M3far`/`M4far` controls, the parity and capacity
controls, and the conditional nulls), for both engines and all family×tier configs. **Inference is
the offset-level randomisation test of conditional-null manifest §4–§5:** the six leave-one-offset-
out increments are **not** independent replicates; the primary statistic is `M₉` = the median across
the nine family×tier configs then across the six offsets (membership fixed a priori, §7); the
permutation stress reference gives the constrained-reference tail
`q_ref = (1 + #{M_null ≥ M_obs})/(B+1)` with **`B = 1000`**, operational gate `q_ref < 0.05`
(extremeness under the algorithmic reference — **not** exact-conditional inference; conditional-null
§3); **all six offset effects and signs are always reported**; ≥5/6 positive is a supporting
criterion.

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

## 12. Decision gates (each fully defined: statistic · reference · threshold · denominator · set)

All increments are `ΔR² = R²(X_r + •) − R²(X_r)` at the reference radius r=16 unless noted, on the
coherent engine unless noted. `δ_cap` = the 200-draw capacity detection floor (physical §6).

- **G0 Boundary gate (computed first, before any β inference):** stat `t_bound*` (§5); reference —;
  threshold **`t_bound* > 8` (strict)**; else **finite-size-limited**, stop. Set: global.
- **G1 Quality:** stat = per-`(config,engine)` median `R²_fit`; threshold `≥ 0.90`; a failing
  `(config,engine)` is **descriptive** and its **global claim fails/downgrades — `M₉` membership is
  NEVER changed** (§7). Set: per config.
- **G2 Primary permutation stress gate:** stat `M_perm,7,address` (coherent); reference = its
  `B=1000` constrained-permutation **stress reference** (conditional-null §3–4); threshold the
  **constrained-reference tail** `q_ref = (1+#{null ≥ obs})/(B+1) < 0.05` (extremeness under the
  algorithmic reference — **not** exact-conditional inference). Denominator: none (a difference).
  Set: **`M_perm,7`** (feasible cells only; infeasible cells never pass this gate).
- **G3 Exceeds capacity:** stat `M₉,address`; reference the 200-draw capacity distribution;
  threshold `M₉,address > δ_cap`. Denominator: none. Set: **`M₉`**.
- **G4 Shuffle-kill (paired reduction — NOT difference-of-medians):** compute the reduction
  **at the fold/config level first**: for each `(config, offset-fold)` form the paired
  `red_{c,o} = (plain_{c,o} − shuf_{c,o}) / plain_{c,o}`, then **aggregate `red` by the `M₉`
  construction** (median across configs, then across offsets) → `R_kill`. (Median-of-differences ≠
  difference-of-medians, so the reduction is built before aggregating, not from separately-computed
  medians.) Reference —; threshold `R_kill ≥ 0.70`. **Denominator handling:** any fold/config with
  `plain_{c,o} ≤ δ_cap` or `≤ 0` has `red` **undefined** → that fold/config routes to
  **mixed/undetectable** (a kill of an undetected signal is meaningless); if that leaves the global
  statistic undefined, the endpoint is mixed/undetectable. Set: **`M₉`** (paired).
- **G5 Cross-engine non-reproduction (NOT a "coherence-specific" verdict):** stat = classical
  `M₉,address` from the **specified degree-normalised classical CTMC** (§10); threshold
  `classical M₉,address ≤ 0.2 × coherent M₉,address`. **Interpretation (frozen):** a G5 pass
  establishes an **engine-specific non-reproduction** result — coherent adjacency propagation
  (`H = A`) versus the frozen degree-normalised CTMC (`Q = A·D⁻¹ − I`). It does **not** isolate
  coherence from generator choice, because `H = A` and `Q = A·D⁻¹ − I` are **different operators**
  on these irregular graphs. **Denominator handling:** if coherent `M₉,address ≤ δ_cap` or `≤ 0`
  → undefined → **mixed/undetectable**. **Classical-diagnostic caveat:** if the classical
  per-`(config,engine)` median `R²_fit < 0.90` (G1), **failure of the specified classical comparator
  makes the cross-engine non-reproduction comparison inconclusive** — it does not erase a
  well-defined quantum β. Set: **`M₉`**.
- **G6 Residual-orthogonal null "survives" (explicit pre-sealed criterion):** stat = deterministic
  `M₉` of `ΔR²_resid` (conditional-null §2); reference `δ_cap`; threshold `> δ_cap`. Stated as a
  **lower-bound detection** check, **not** a randomisation test. Set: **`M₉`**.
- **G7 Address vs parity — DESCRIPTIVE ONLY (no gate):** report `Δ_ap = M₉,address − M₉,parity` vs
  `δ_cap`. "**Compatible with representation collapse**" iff `Δ_ap ≤ δ_cap`. Parity is deterministic
  → **no significance threshold**, no pass/fail. Set: **`M₉`** (descriptive).
- **G8 Config-specific secondary:** Westfall–Young step-down max-T over the **seven feasible cells**
  (the permutation null exists only there; platinum e16/e18 remain descriptive for this control),
  giving extremeness values `q̃` (conditional-null §4); **secondary/descriptive**, never uncorrected
  selection. Set: per config (the seven feasible).

**"Transport" is earned** only if **G0, G1, G2, G3, G4, G5, G6 all pass** (G7 descriptive, G8
secondary). Any undefined-denominator route → **mixed/undetectable**. **Claim wording (frozen):** at
most —
> *"The address representation predicts heterogeneity in full-spectrum wavepacket spreading beyond
> the frozen physical descriptions and controls."*

**No inference that perpendicular space is a literal physical degree of freedom.**

**Authorised non-positive outcomes:** shuffle-not-killed → "reads multiscale geometry, not cleanly
the address"; `t_bound* ≤ 8` (any crossing at or before 8, inclusive) → **finite-size-limited**
(legitimate, not a failed run); randomisation
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
**v8.1 — 2026-08-31** (external-scout claim audit, implication 3; documentation-only): relabelled
**G5** "Classical contrast" → **"Cross-engine non-reproduction"** and removed **"coherence-specific"**
as an earned verdict in §7 and §12; stated explicitly that a G5 pass is **engine-specific** (coherent
`H=A` vs the specified degree-normalised CTMC `Q=A·D⁻¹−I`) and does **not** isolate coherence from
generator choice because the two are different operators on irregular graphs; replaced "prevents the
strongest coherence-specific claim" with "failure of the specified classical comparator makes the
cross-engine non-reproduction comparison inconclusive". No new propagation control; no change to
endpoints, thresholds, other gates, denominators, config sets, runtime design, or the frozen top-line
claim. (The generator-matched paired-Laplacian study — quantum `e^{−itL}` vs classical `e^{−tL}` — is
recorded as a separate future study, not a pre-seal addition; see `EXTERNAL_SCOUT_CLAIM_AUDIT.md`.)

**v8 — 2026-08-31** (Sol 3rd pre-seal pass): **G1 no longer mutates `M₉`** — the nine-config
membership is fixed a priori, and a poor-`R²_fit` config becomes descriptive with the global claim
downgraded rather than recomputing `M₉` over a subset (with the exact coherent/classical
consequences stated); **G4 shuffle-kill rebuilt as a paired fold/config reduction then aggregated**
(median-of-differences ≠ difference-of-medians) with fold-level denominator handling; renamed the
permutation tail **`q_ref`** and described it as extremeness under the algorithmic reference (not
exact-conditional); **G8 Westfall–Young over the seven feasible cells**; and changed the finite-size
statement to **`t_bound* ≤ 8`**.

**v7 — 2026-08-31** (Sol 2nd pre-seal pass): **embedded the 48 snapped β-times inline** (self-
contained); **separated** the coherent `P_strip = Σ|ψ|²` and classical `P_strip,cl = Σ p` boundary
sums; made the boundary gate **strict `t_bound* > 8`** with an explicit **"no crossing observed"**
state and computed it **before any β inference** (a crossing at exactly t=8 would contaminate the
final fit point); **fully defined every decision gate** (G0–G8: statistic, reference, threshold,
denominator handling, and whether it uses `M₉`, `M_perm,7`, or config-specific), gave the residual
null an explicit lower-bound "survives" criterion, and downgraded address-vs-parity to descriptive;
and **froze the `R²_fit` gate scope to per-(config,engine)**.

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

*End of draft v8. Committed to `gpt/workbench` only. Nothing sealed; only synthetic benchmarks +
geometry diagnostics run; no science-branch file altered.*

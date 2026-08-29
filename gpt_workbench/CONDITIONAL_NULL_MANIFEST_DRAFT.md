# DRAFT — conditional-null design manifest (radius-saturation §2)

**Status — DRAFT for crew review. NOT sealed, NOT run. No study dynamics/address/LDOS/targets/β/
scores accessed. No science-branch file altered.** Specifies the two conditional nulls of
`substrates/PREREG_radius_saturation.md §2` (residual-orthogonal + local physical-space
permutation), their fold structure, repetitions/seeds, equivalence/collapse criteria, and
computational feasibility, by inspecting the existing code and parent prereg.

*Source: drafted by the `gpt/workbench` Claude collaborator from crew decisions relayed by Katie;
not part of the scientific record until reviewed and merged.*

**Code facts inspected (`transport_run.py`, `residualize_check.py`):**
`M3` = `[dens, deg, edge_len_mean, edge_len_var, motif one-hot (width = shared codebook), g(1.6),
g(2.6), ψ_N, ψ_{N/2}, ψ_{2N}, g(4.0), g(6.0)]` — categorical (motif one-hot) + continuous. The
address block `m4 = M4[:, M3.shape[1]:]` = 11 columns. `held_out_r2` = leave-one-offset-out CV,
GBT `HistGradientBoostingRegressor(max_depth=3, max_iter=250, lr=0.06, l2=1.0, random_state=0)`.
Stratified shuffle bins on `motif_code × degree-decile`. Radius-saturation replaces M4's raw perp
with the frozen physical(r) baseline + the address block; the address block is the object all nulls
act on.

---

## 1. Residual-orthogonal null (deterministic; every rung r)
Tests whether the address block carries transport-relevant structure **orthogonal to physical(r)**.
- **Leakage-safe cross-fitting:** within each outer fold (one offset held out), **fit only on the
  five training offsets**. Nothing touched by the held-out offset enters any residualiser or the
  scoring model.
- **M3/physical(r) predictors:** residualise each address column against the **full** physical(r)
  block — **all categorical (motif one-hot) and continuous descriptors** — using the same frozen
  GBT. (One residualiser per address column: 11 per fold per rung.)
- **Residual block construction (exact):** for address column `a_j`, fit `g_j = GBT(physical(r)_tr
  → a_j^tr)`; the residual is `ã_j = a_j − g_j(physical(r))`, evaluated with `g_j` trained on the
  training offsets only and applied to both train and held-out rows. The residual address block is
  `Ã = [ã_1 … ã_11]`.
- **Exact statistic:** `ΔR²_resid = R²(physical(r) + Ã) − R²(physical(r))`, held-out, averaged as
  the six-offset structure in §3. (Documented **lossy lower bound** — a GBT residual is hard for a
  second GBT; this is a *conservative* null, stated as such, not a symmetric test.)

## 2. Local physical-space permutation null (randomised; reference radius)
Tests whether the increment survives holding **all of physical(r)** approximately fixed — the
generalisation of the sealed motif×degree-decile shuffle to the continuous descriptors.
- **Cell construction:** standardise the **continuous** physical(r) descriptors within the training
  set (z-score with **training-only** mean/std), and within each exact **motif class** (the
  categorical one-hot identity — never permuted across motif classes), build **k-NN cells** in the
  standardised continuous space (proposed `k = 32`, flagged). The address labels are permuted
  **only within a cell**, so motif class is held exactly and the continuous descriptors are held
  approximately fixed.
- **Training-only scaling/neighbours:** the standardiser and the k-NN graph are built on the
  training offsets only, then applied to the held-out offset (no leakage).
- **Continuous descriptors held approximately fixed:** by permuting within small same-motif kNN
  cells, `g(ρ)`, degree, ψₙ, Voronoi statistics vary negligibly within a cell; a **balance
  diagnostic** (below) verifies this.
- **Sparse cells / ties:** a cell with `< k+1` members is merged with its nearest same-motif cell
  (by cell-centroid distance) until `≥ k+1`; distance ties broken by **lift-coordinate
  lexicographic order** (as in the physical manifest §5). A vertex whose motif class has `< k+1`
  members total is flagged and excluded from the permutation (reported, not silently dropped).
- **Forbidden boundaries:** permutations occur **only within a single (family, tier, offset)**;
  never across families, tiers, or offsets.
- **Balance diagnostic (must be reported):** after permutation, report the standardised-mean
  difference of every continuous physical(r) descriptor between original and permuted assignments
  (target ≈ 0), and the within-cell variance retained — demonstrating physical-feature balance was
  preserved.
- **Exact statistic:** `ΔR²_perm` = the increment with permuted address labels, held-out, six-offset
  structure (§3). A genuine increment must survive **both** §1 and §2.

## 3. Fold dependence (identical structure in observed and null)
- **Preserve the full six-offset leave-one-out structure in every null repetition:** each repetition
  recomputes the entire six-element held-out vector `{Δ_o}` (o = 1…6), **not** a single pooled
  number.
- **Statistic:** the **median of the six** held-out increments, `M = median_o(Δ_o)`.
- **Comparison:** the observed `M_obs` is compared against the **null distribution of six-offset
  medians** `{M^(b)}` from the permutation repetitions — a randomisation test carrying the same
  fold correlation in observed and null.
- **Always report all six `Δ_o` and their signs**, regardless of the aggregate verdict; **≥5/6
  positive** is a supporting consistency criterion, not the test.
- Offsets are the **sampling clusters**; the six LOO estimates remain **correlated through
  overlapping training sets** — never treated as independent replicates.

## 4. Repetitions and seeds (exact, frozen)
- **Permutation / randomisation count: exactly `B = 1000`** (not "≥1000"). Justification: a one-sided
  randomisation tail probability has Monte-Carlo SE `≈ sqrt(p(1−p)/B)`; at `p≈0.05`, `B=1000` gives
  SE `≈ 0.0069` — enough to resolve a 0.05 threshold, and the smallest reportable tail is `1/(B+1)
  ≈ 1e-3`. (If the crew needs to resolve `p≈0.01` tightly, raise to `B=5000`, SE≈0.0014 — flagged.)
- **Seeds:** `numpy.random.SeedSequence(20260829)` spawned into `B` child streams; repetition `b`
  uses child `b`. **Every seed frozen** pre-seal and recorded.
- **Synchronised repetitions:** where the coherent and CTMC engines (or address vs parity/capacity)
  are compared, repetition `b` uses the **same** child seed for both, so their null medians are
  paired and differences are within-repetition.

## 5. Equivalence and collapse rules (numerical, outcome-independent)
- **`δ*` (practical-equivalence margin) — outcome-independent justification required.** Do **not**
  set `δ*` just above the known `+0.004` fully-M3-residual result. Proposed **calibration rule**
  (flagged for crew): set `δ*` = the **95th percentile of the 200-draw Gaussian capacity-null
  increment** (physical manifest §6) at the reference radius — i.e. the largest increment a
  same-dimensional block of pure noise produces by chance. This ties `δ*` to a measured
  noise-floor, not to any address result. (A fixed `δ* = 0.005` is retained only as a fallback and
  is explicitly **provisional/unratified**.)
- **`ρ* = 0.25` denominator handling:** `ρ = ΔR²_addr(16)/ΔR²_addr(2)` is defined **only if
  `ΔR²_addr(2)` exceeds the capacity noise-floor `δ*` and is positive**. If `ΔR²_addr(2) ≤ δ*`, is
  negative, or its six-offset sign is unstable (< 5/6 one sign), **`ρ` is undefined** → the radius
  ratio is not used; the outcome routes to **mixed/infeasible** (§7), never to "fade."
- **Numerical criteria (frozen forms; thresholds flagged):**
  - *"exceeds capacity"*: `M_obs >` the 95th percentile of the 200-draw Gaussian capacity null.
  - *"exceeds parity"*: `M_obs >` the physical (degree,Voronoi) parity block's six-offset-median
    increment (representation-matched), by more than the capacity noise-floor `δ*`.
  - *"representation collapse"*: the address increment does **not** exceed parity (above) though it
    survives radius — i.e. `M_obs ≤ parity_median + δ*`.
  - *"survives the conditional null"*: `M_obs` exceeds the 95th percentile of the §2 permutation
    null of six-offset medians **and** `ΔR²_resid > δ*` (§1).
- **`CI includes zero` is never accepted as proof of equivalence** (a wide CI is ignorance, not
  equivalence); equivalence requires the relative + absolute (`ρ*`, `δ*`) rule met.

## 6. Computational feasibility (fits estimate + factorisation)
- **Deterministic parts (cheap):** the plain increment and the residual-orthogonal null (§1) are
  computed at **every rung** (5 radii) × 9 patch-configs × 6 folds × 2 engines ≈ 540 baseline fits
  + 11 residualisers each — a few thousand GBT fits, minutes-scale.
- **Randomised part (dominant):** the permutation null (§2) and the capacity null are proposed at the
  **fixed reference radius r=16 only** (the decisive test), not all 5 radii. Fits ≈ `B(1000) ×
  6 folds × 9 configs × 2 engines ≈ 108,000` address-model fits, plus `200 (capacity draws) × 6 ×
  9 × 2 ≈ 21,600`. At ~0.15 s per GBT fit ≈ **~5–6 h total**, parallelisable.
- **Factorisation (scientifically identical):** within a fold, **fit the physical(r) baseline model
  once and cache its held-out `R²`**; each repetition refits only the `physical(r)+address` model
  (the baseline is unchanged by permuting address). Residualisers `g_j` are fit **once per fold**
  and reused across the deterministic null. No target/outcome regression is run here — this is the
  fit-count estimate only.
- Applying the randomised nulls at all 5 radii instead of only r=16 would ×5 the dominant cost
  (~27 h); **flagged** as a crew scoping choice.

## 7. Authorised outcomes (kept distinct; cautious language)
- **compression** (radius fade meeting the `ρ*`+`δ*` rule, §5) · **representational** (survives
  radius, collapses to parity) · **stable residual** (exceeds parity + capacity, survives both
  conditional nulls) · **mixed** (families/tiers/ρ-undefined disagree beyond null uncertainty) ·
  **infeasible** (physical/count floor unmet). These are **distinct**; a result is routed to exactly
  one.
- **Claim language:** at most *"the address representation predicts heterogeneity beyond the frozen
  physical descriptions and controls."* **No literal perpendicular-space physical-degree-of-freedom
  ontology**, regardless of outcome.

## 8. Open choices for crew
- `k = 32` kNN cell size (§2); `B = 1000` vs 5000 (§4); `δ*` = capacity-95th-percentile calibration
  vs fixed 0.005 (§5); whether the randomised nulls run at r=16 only or all 5 radii (§6).

---
*End of draft. Committed to `gpt/workbench` only. Nothing sealed; no study dynamics/address/targets
accessed; no science-branch file altered.*

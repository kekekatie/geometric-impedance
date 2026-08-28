# DRAFT v2 — frozen protocol for the MSD transport endpoint (radius-saturation, stage-two)

**Status — DRAFT for crew knife-sharpening. NOT sealed, NOT run. No data touched to write
this. No science-branch file altered.** A workbench design artifact only. It gives the
"required dynamical endpoint" of `substrates/PREREG_radius_saturation.md §6` — the bulk
wavepacket mean-square-displacement (MSD) exponent — the same a-priori freezing the address
block M4 already has (`PREREG_transport_hierarchy.md §4a` → `transport_run.py::_m4_cols`). It
addresses **blocking item #8** of the 2026-08-28 radius-saturation adversarial review.

**v2 (2026-08-28)** repairs four blockers raised by Work-GPT against v1: (1) the initial state
is now the genuinely localized unfiltered site quench (energy-filtering demoted to a rigorously
defined secondary); (2) boundary leakage is now a geometrically correct hull-depth strip, not a
circle; (3) the classical null is a well-defined continuous-time Markov generator; (4) no
per-site fit-quality culling (β is defined for every admitted site), and the fit window comes
from a geometry-only Lieb-Robinson feasibility bound rather than an assumed front velocity. Full
change log at the end.

*Source: drafted by the `gpt/workbench` Claude collaborator at Work-GPT's request (relayed by
Katie). A proposal to be verified and amended by the crew; it enters no experimental record and
changes no scientific meaning of any existing result until reviewed and merged.*

---

## 0. Why this exists, and what it is for

The transport result is currently **spectral** (per-vertex LDOS in the sealed mid-band). The
pre-reg forbids the word "transport" until the address increment **also** appears on a genuinely
**dynamical** quantity, analysed with the identical nested-increment ladder and controls. On
quasicrystals the wavepacket exponent is anomalous and notoriously fit-window-sensitive, so the
endpoint is only meaningful if launch site, initial state, time window, boundary cutoff, and the
fit are all frozen in advance. That is this document.

**The observable is per-vertex, to match the ladder.** For each admitted bulk launch vertex
`v0` we compute a spreading exponent `β(v0)`, and regress the vector `{β(v0)}` on M0→M4 exactly
as `transport_run.py` regresses LDOS. The decisive quantity remains the **M4-over-M3 increment**
under the stratified-shuffle / position / M3far / conditional-null controls. Nothing new in the
statistics; the new content is *how `β(v0)` is defined*, frozen below.

---

## 1. Frozen physical setup (fix before any run)

- **Hamiltonian:** the sealed engine `H = A` (tiling adjacency, uniform hopping, ħ = 1, hopping
  amplitude `J = 1`), from `build_features(..., return_dynamics=True)` (`evals`, `evecs`). The
  perpendicular-space address appears NOWHERE in H — only later as an analysis feature. The
  edge-length-weighted H is a robustness variant, not primary.
- **Distance metric:** Euclidean parallel-space distance `‖par[v] − par[v0]‖`. (Graph-distance
  MSD is a robustness variant, §11.)
- **Distance-to-boundary:** `d_bound(i) := hull_depth(par)[i]` — reuse the existing signed
  distance-to-convex-hull function (`transport_run.py:59`), applied to the parallel-space cloud.
  This is a **per-vertex** quantity for *every* vertex, and is the basis of the boundary strip
  (§5), not just of launch admissibility.
- **Units:** `ℓ := median edge length`; times are in units of inverse hopping (ħ/J = 1). Every
  constant below is chosen a priori and is **not** tuned to any outcome.

## 2. Launch-site selection (frozen, deterministic, offset-independent)

1. **Interior requirement.** A vertex `v0` is *admissible* iff `d_bound(v0) ≥ R_min·ℓ` with
   **`R_min = 8`** (frozen). (Set before the run; matches the largest address shell and the
   mid-ladder physical radius.)
2. **Deterministic subsample (only if needed for cost).** If the admissible set for an offset has
   `≤ 1500` vertices, use all of them. Otherwise use the **1500 admissible vertices with the
   largest `d_bound`** (ties broken by ascending vertex index). This rule is fixed, uses no
   perp/address information, and is identical across offsets and families. Record the count used.
3. The same admitted launch set is used for the coherent engine, the classical null, and every
   control, per offset.
4. **Every admitted site produces a `β(v0)`** (§7–§8). Admissibility depends only on `d_bound`
   (a physical boundary-distance quantity, already inside the M3pos position control), never on
   the perpendicular-space address — so the *admitted set itself* carries no address-correlated
   selection. See §8 for why nothing downstream re-introduces it.

## 3. Initial state (frozen)

**Primary — unfiltered site quench (genuinely localized).**

    |ψ0⟩ = |v0⟩   (unit amplitude on v0, zero elsewhere)

This is exactly site-localized: `MSD(0; v0) = 0` and `P_strip(0) = 0` for every admitted `v0`
(admitted sites are interior, `d_bound ≥ 8ℓ`, so v0 is not in the boundary strip). It spans the
full spectrum, which is the honest meaning of "a wavepacket from a localized start"; the mid-band
connection is preserved by the analysis window and by the secondary state below, not by
pre-localizing in energy.

**Secondary — mid-band-projected state (rigorously defined, NOT called site-localized).**

    |χ0⟩ = P_W |v0⟩ / ‖P_W |v0⟩‖,     P_W = projector onto |E| ∈ [0.8, 2.5]

Spectral projection gives `|χ0⟩` **nonlocal initial support**, so for this state we must:
- **report and use excess MSD** `ΔMSD(t) := MSD(t) − MSD(0)`, since `MSD(0; χ0) > 0`;
- quantify the initial support: report `MSD(0; χ0)` and the initial participation radius
  `ρ0 := sqrt(MSD(0; χ0))` per site;
- apply an **initial-boundary-mass admissibility rule**: admit `|χ0⟩` only if
  `P_strip(0) < 10⁻³` **and** `ρ0 ≤ R_min·ℓ / 2` (its initial cloud is well inside the interior);
  sites failing either are reported separately, **not silently dropped** (their β is flagged, not
  culled — same anti-missingness principle as §8).

The primary claim rests on the unfiltered state; `|χ0⟩` is reported as a robustness check that
ties the spreading to the mid-band states specifically. (The excess-MSD convention `ΔMSD` is also
applied to the primary, where it is identical to `MSD` because `MSD(0)=0` — so the pipeline is
uniform.)

## 4. Time evolution (frozen)

- **Evolution (exact by definition):**
  `ψ_t(v) = Σ_k e^{−iE_k t} c_k φ_k(v)`, `c_k = ⟨k|ψ0⟩`, over the eigenpairs already computed.
  This defines the endpoint. (Implementations may use Chebyshev/Krylov propagation for speed
  **iff** they reproduce the exact-diagonalization `β` to within `Δβ ≤ 0.01` on a fixed
  100-site validation subset; otherwise exact diagonalization is required. The *definition* is
  exact-diagonalization.)
- **Time grid:** log-spaced, `N_t = 48` points on the common fit interval `[t_lo, t_hi]` derived
  in §7 (geometry-only). Same grid for coherent and classical engines and all controls.
- **No stochastic repetitions.** Coherent evolution from a fixed state on a fixed H is
  **deterministic** — there is nothing to average over per site. The statistical ensemble is the
  set of admitted launch sites × the 5 window offsets (§9). Seeds do not enter the endpoint;
  the only rng in the pipeline is the stratified-shuffle control's `default_rng(0)`, already
  frozen in `transport_run.py`.

## 5. Boundary strip and leakage cutoff (frozen — geometric, per destination vertex)

The boundary region is defined by **each destination vertex's own hull depth**, not by a circle
around `v0`:

    STRIP := { v : d_bound(v) < w·ℓ },     w = 2   (frozen strip width)

Leaked probability, accounting for any initial mass already in the strip:

    P_strip(t) = Σ_{v ∈ STRIP} |ψ_t(v)|²,     ΔP_strip(t) = P_strip(t) − P_strip(0)

This correctly labels near-boundary sites as "boundary" regardless of their direction or distance
from `v0`, and correctly ignores interior sites that merely happen to be far from `v0`. For the
primary unfiltered launch from an interior site, `P_strip(0) = 0`. `ΔP_strip(t)` is used only as
a **reported diagnostic** confirming the geometry-derived window (§7) kept the packet interior
(must stay `< ε = 0.01` across the fit window; if a whole family violates this, that family's
endpoint is flagged finite-size-limited — an *aggregate* rule, never a per-site cull).

## 6. MSD definition (frozen)

    MSD(t; v0) = Σ_v |ψ_t(v)|² · ‖par[v] − par[v0]‖²      (Euclidean, parallel space)
    ΔMSD(t; v0) = MSD(t; v0) − MSD(0; v0)                 (excess over the initial spread)

`ΔMSD` is the fitted quantity (= `MSD` for the primary state since `MSD(0)=0`; genuinely needed
for the secondary state, §3).

## 7. Fit window from a geometry-only feasibility bound, and exponent extraction (frozen)

**No assumed front velocity.** The window `[t_lo, t_hi]` is fixed **before any dynamics**, per
family, from the patch graph geometry and a conservative Lieb-Robinson (LR) series bound:

- Let `d_max` = maximum graph degree in the patch, and `G_strip` = the minimum over admitted
  launch sites of the **graph distance** from `v0` to `STRIP` (computed from the fixed graph
  before any evolution; deterministic geometry, not an experiment). Let `N_strip` = |STRIP|.
- Single-amplitude LR tail bound (from `(A^k)_{v,v0}=0` for `k <` graph distance, and
  `|(A^k)_{v,v0}| ≤ d_max^k`):
  `|(e^{−iAt})_{v,v0}| ≤ B(t;G) := Σ_{k ≥ G} (d_max·t)^k / k!`.
  Union-bounded leaked probability into the strip:
  `P_strip(t) ≤ N_strip · B(t; G_strip)²`.
- **`t_hi`** = the largest `t` satisfying `N_strip · B(t; G_strip)² ≤ ε'`, **`ε' = 5·10⁻³`**
  (frozen). This is a rigorous, geometry-only upper bound on leakage; it is conservative (it may
  cut the window shorter than strictly necessary — the safe direction).
- **`t_lo = 2.0`** (frozen; drops the first couple of hops of transient).
- **Leverage / feasibility:** require `t_hi / t_lo ≥ 4` and `≥ 6` grid points in-window. If the
  geometry does not afford this (LR bound too tight for the patch size), the endpoint is
  **finite-size-limited for that family** — report exponents descriptively, make no transport
  claim (an honest, expected possibility for these patch sizes; §8 aggregate rule).

**Exponent (defined for every admitted site).** With `ΔMSD(t) ∝ t^{2β}`,
`β(v0) = ½ · slope` of an OLS fit of `log ΔMSD` on `log t` over the in-window grid points
(unweighted). Interpretation: β = 1 ballistic, β = ½ diffusive, β < ½ sub-diffusive; critical
states give `0 < β < 1`. Record `R²_fit(v0)` as a **diagnostic only** (see §8).

## 8. No feature-correlated missingness (frozen)

- **Every admitted site (§2) yields a `β(v0)`** and enters the regression. There is **no per-site
  exclusion on `R²_fit`**, on curvature, or on any dynamics-derived quantity, because such a
  filter could correlate with the address (e.g. confined vs extended launch neighbourhoods fit
  power laws differently), manufacturing address-correlated missingness in exactly the variable
  under test. `β` from OLS is always defined.
- The fit window is **common to all admitted sites in a family** (§7, derived from the guaranteed
  interior depth `R_min` and `G_strip`), so no site is dropped for "too small a window" either —
  admissibility (a pure `d_bound` geometric criterion) already guarantees the window applies.
- `R²_fit` is retained **only** as (a) a per-site diagnostic reported alongside β, and (b) an
  **aggregate stop rule**: if the median `R²_fit` across admitted sites in a family is `< 0.90`,
  or `ΔP_strip` exceeds `ε` anywhere in the window, the MSD-power-law summary is judged unmet for
  that family — report β descriptively, make no transport claim. These are whole-family verdicts,
  never per-site filters, so the regressed sample is never thinned by an address-correlated rule.
- The secondary state's admissibility (§3) likewise **flags-not-drops** sites, and its
  missingness (if any) is confined to the secondary robustness analysis, never the primary claim.

Aggregate finite-size rule (unchanged in spirit): if the admitted launch count per offset is
`< 300`, or §7 feasibility fails, treat as finite-size-limited (the pre-reg's outcome-4
analogue): report as unresolved, do not interpret.

## 9. Aggregation across offsets (frozen — reuse the sealed pipeline verbatim)

The per-vertex target vector `{β(v0)}` replaces `ld_primary` and is fed to the **identical**
`transport_run.py` machinery: nested M0→M4, `held_out_r2` leave-one-offset-out CV over the 5
`OFFSETS`, same GBT, with the `M4shuf` (stratified shuffle), `M3pos`/`M4pos` (position), and
`M3far`/`M4far` (long-range physical) controls, plus the pre-reg §2 conditional nulls and §3
fake-address / equal-count controls at the fixed reference radius. Report `M4−M3` ± std across
the 5 CV folds, for coherent and classical engines, all three families. No per-offset tuning.

## 10. Classical null engine (frozen — continuous-time Markov generator)

A single, unambiguous continuous-time random walk (no discrete-power / interpolation ambiguity,
no row/column orientation ambiguity):

    Q = A·D⁻¹ − I        (D = diag(deg));  columns of Q sum to 0 ⇒ column-stochastic generator
    p(t; v0) = e^{Q t} · e_{v0}            (always a valid probability vector, Σ_v p_v = 1)
    MSD_cl(t; v0) = Σ_v p_v(t; v0) · ‖par[v] − par[v0]‖²

- `Q_{vw} = A_{vw}/deg_w` for `v ≠ w` (rate from `w` to a neighbour `v`), `Q_{ww} = −1` (unit
  total exit rate). Stationary distribution `π ∝ deg`. Defined for **all real `t ≥ 0`**;
  evaluated on the **same** log time grid, with the **same** strip cutoff (§5), the **same**
  common fit window (§7), and the **same** OLS exponent extraction (§7) — yielding `β_cl(v0)`.
- **Time comparability with the quantum engine:** both use the identical continuous `t` in units
  `ħ/J` with `J = 1`; the classical unit exit rate (`Q_{ww} = −1`) sets one expected hop per unit
  time, matching the quantum hopping matrix element `J = 1`. This rate normalization is an
  explicit a-priori convention (stated, not tuned); a `2×` rate variant is a §11 robustness check.
- Expected outcome: diffusive (`β_cl ≈ ½`) and address-blind — the incoherent contrast.

## 11. Robustness variants (secondary; reported, never the basis of the claim)
- Graph-distance MSD (BFS distance in place of Euclidean).
- Mid-band-projected secondary state `|χ0⟩` (§3), with excess MSD and its admissibility flags.
- Secondary window |E| ≤ 0.2; edge-length-weighted H.
- Classical exit-rate `×2`; strip width `w ∈ {1.5, 3}`; `R_min ∈ {6, 12}`; LR `ε' ∈ {10⁻³,10⁻²}`
  — a sensitivity band showing the exponent's stability to the frozen constants (the frozen
  values above define the primary claim).

## 12. Decision threshold (frozen)

The dynamical endpoint **earns the word "transport"** only if, on `β(v0)` from the **primary**
unfiltered state in the sealed mid-band-analysed window, **all** hold (mirroring
`PREREG_transport_hierarchy.md §10`, applied to β, plus the radius-saturation §2/§3 controls):

1. the coherent `M4−M3` increment on β is **positive held-out** (mean − 1·std across the 5 CV
   folds `> 0`);
2. it is **killed by the stratified shuffle** — `M4shuf−M3` within `±1·std` of 0, and the
   shuffle removes **≥ 70 %** of the plain increment (the golden threshold met by the spectral
   result);
3. it is **not reproduced by the classical engine** — `β_cl` shows `M4−M3 ≤ 0.2 ×` the coherent
   increment;
4. it **survives both conditional nulls** (§2 of the pre-reg) and **exceeds both** the
   fake-address and equal-count controls (§3), at the fixed reference radius;
5. the §8 aggregate quality gates pass (median `R²_fit ≥ 0.90`, `ΔP_strip < ε` across the window,
   admitted count `≥ 300`/offset, §7 feasibility met).

If (1) holds but the increment is not shuffle-killed → "reads multiscale geometry dynamically,
not cleanly the address." If (1) fails, or (5) fails → "the spectral address signal does not
surface in bulk wavepacket spreading at this coupling / patch size" (a real, publishable
negative, not a failure of the programme). No family ordering is claimed. No new ontology ("perp
space is physical") regardless of result. This endpoint gates only the word **transport**, not
the already-earned spectral claim.

---

## 13. What this manifest deliberately does NOT decide
- It does not seal the pre-reg, and does not run.
- It inherits — does not re-decide — the interior mask (physical-radius manifest App-B), the
  reference radius for §12(4), and the silver/platinum-vs-golden scope.
- The frozen constants (`R_min = 8`, strip `w = 2`, LR `ε' = 5·10⁻³`, diagnostic `ε = 0.01`,
  grid `N_t = 48`, `t_lo = 2.0`, leverage `≥ 4×` & `≥ 6` pts, aggregate `R²_fit ≥ 0.90`,
  count `≥ 300`) are proposals for crew red-pencil; once the crew signs off they are sealed and
  any later change is a dated amendment.

---

## Change log

**v2 — 2026-08-28** (repairs to Work-GPT's four blockers on v1):
1. **Initial state (§3).** Primary is now the **unfiltered site quench** `|v0⟩` (genuinely
   localized, `MSD(0)=0`). The energy-filtered state is demoted to a **secondary** `|χ0⟩`, is no
   longer called "site-localized," and is defined rigorously via **excess MSD** `ΔMSD = MSD −
   MSD(0)` plus an **initial-boundary-mass / initial-support admissibility rule**
   (`P_strip(0) < 10⁻³`, `ρ0 ≤ R_min·ℓ/2`), with flag-not-drop handling.
2. **Boundary leakage (§5).** Replaced the circle `‖par[v]−par[v0]‖ > d_bound(v0)` with a
   **hull-depth boundary strip** `STRIP = {v : d_bound(v) < w·ℓ}` and `ΔP_strip(t) = P_strip(t) −
   P_strip(0)`, accounting for initial strip mass and correctly classifying interior sites in all
   directions.
3. **Classical engine (§10).** Replaced the ambiguous `P = A/deg`, `[P^t]_{v,v0}`, noninteger-t
   interpolation with a **continuous-time Markov generator** `Q = A·D⁻¹ − I`,
   `p(t) = e^{Qt}e_{v0}` — column-stochastic, valid at all real `t`, orientation-explicit, on the
   same time axis as the quantum engine (comparability convention stated).
4. **Missingness & `t_cap` (§7, §8).** Removed per-site `R²_fit` culling — **β is defined for
   every admitted site**, `R²_fit` is diagnostic + an **aggregate** family-level stop rule only,
   with an explicit argument that admission depends solely on `d_bound` (physical, not address).
   Deleted the "unit front velocity" justification for `t_cap`; the fit window now comes from a
   **geometry-only Lieb-Robinson feasibility bound** (`t_hi` from `N_strip·B(t;G_strip)² ≤ ε'`),
   with a stated finite-size-limited outcome when geometry can't afford the leverage.

**v1 — 2026-08-28.** Initial frozen MSD-endpoint draft (blocking review item #8).

---

*End of draft v2. Committed to `gpt/workbench` only. No experiment was run; no pre-registration
was sealed; no file on `claude/giv-quasicrystal-phason-5syx5s` was touched.*

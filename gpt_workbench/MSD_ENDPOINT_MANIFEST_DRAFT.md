# DRAFT — frozen protocol for the MSD transport endpoint (radius-saturation, stage-two)

**Status — DRAFT for crew knife-sharpening. NOT sealed, NOT run. No data touched to write
this. No science-branch file altered.** A workbench design artifact only. It gives the
"required dynamical endpoint" of `substrates/PREREG_radius_saturation.md §6` — the bulk
wavepacket mean-square-displacement (MSD) exponent — the same a-priori freezing the address
block M4 already has (`PREREG_transport_hierarchy.md §4a` → `transport_run.py::_m4_cols`). It
addresses **blocking item #8** of the 2026-08-28 radius-saturation adversarial review.

*Source: drafted by the `gpt/workbench` Claude collaborator at Work-GPT's request (relayed by
Katie). A proposal to be verified and amended by the crew; it enters no experimental record and
changes no scientific meaning of any existing result until reviewed and merged.*

---

## 0. Why this exists, and what it is for

The transport result is currently **spectral** (per-vertex LDOS in the sealed mid-band). The
pre-reg forbids the word "transport" until the address increment **also** appears on a genuinely
**dynamical** quantity, analysed with the identical nested-increment ladder and controls. On
quasicrystals the wavepacket exponent is anomalous and notoriously fit-window-sensitive, so the
endpoint is only meaningful if launch site, time window, boundary cutoff, and the fit are all
frozen in advance. That is this document.

**The observable is per-vertex, to match the ladder.** For each admitted bulk launch vertex
`v0` we compute a spreading exponent `β(v0)`, and regress the vector `{β(v0)}` on M0→M4 exactly
as `transport_run.py` regresses LDOS. The decisive quantity remains the **M4-over-M3 increment**
under the stratified-shuffle / position / M3far / conditional-null controls. Nothing new in the
statistics; the new content is *how `β(v0)` is defined*, frozen below.

---

## 1. Frozen physical setup (fix before any run)

- **Hamiltonian:** the sealed engine `H = A` (tiling adjacency, uniform hopping, ħ = 1, hopping
  amplitude = 1), from `build_features(..., return_dynamics=True)` (`evals`, `evecs`). The
  perpendicular-space address appears NOWHERE in H — only later as an analysis feature. The
  edge-length-weighted H is a robustness variant, not primary.
- **Distance metric:** Euclidean parallel-space distance `‖par[v] − par[v0]‖`. (Graph-distance
  MSD is a robustness variant, §11.)
- **Distance-to-boundary:** `d_bound(i) := hull_depth(par)[i]` — reuse the existing signed
  distance-to-convex-hull function (`transport_run.py:59`), applied to the parallel-space cloud.
- **Units:** `ℓ := median edge length` (as in the physical-radius manifest); times are in units
  of inverse hopping (ħ/J = 1). Every constant below is chosen a priori and is **not** tuned to
  any outcome.

## 2. Launch-site selection (frozen, deterministic, offset-independent)

1. **Interior requirement.** A vertex `v0` is *admissible* iff `d_bound(v0) ≥ R_min·ℓ` with
   **`R_min = 8`** (frozen): the packet must have room to establish a power law before it can
   reach the boundary. (`R_min = 8` matches the largest address shell and the mid-ladder physical
   radius; it is set before the run, not chosen from results.)
2. **Deterministic subsample (only if needed for cost).** If the admissible set for an offset has
   `≤ 1500` vertices, use all of them. Otherwise use the **1500 admissible vertices with the
   largest `d_bound`** (ties broken by ascending vertex index). This rule is fixed, uses no
   perp/address information, and is identical across offsets and families. Record the count used.
3. The same admitted launch set is used for the coherent engine, the classical null, and every
   control, per offset.

## 3. Initial state (frozen)

Primary — **mid-band–filtered site quench**, tying the dynamical endpoint to the *same* states
the spectral claim is about:

    |ψ0(v0)⟩ = P_W |v0⟩ / ‖P_W |v0⟩‖,     P_W = projector onto eigenstates with |E| ∈ [0.8, 2.5]

(the sealed primary window). `|v0⟩` is the unit site basis vector on `v0`.
- **Admissibility floor:** if `‖P_W |v0⟩‖ < 0.05` (v0 carries negligible mid-band weight, so β
  is ill-defined) the site is **excluded** and counted as a §8 failure.
- Robustness variant (reported, not primary): the **unfiltered** site quench `|ψ0⟩ = |v0⟩`
  (all energies). Secondary window |E| ≤ 0.2 filtering is reported for contrast only, never the
  basis of the claim.

## 4. Time evolution and time sampling (frozen)

- **Evolution (exact by definition):**
  `ψ_t(v) = Σ_k e^{−iE_k t} c_k φ_k(v)`, `c_k = ⟨k|ψ0⟩`, over the eigenpairs already computed.
  This defines the endpoint. (Implementations may use Chebyshev/Krylov propagation for speed
  **iff** they reproduce the exact-diagonalization `β` to within `Δβ ≤ 0.01` on a fixed
  100-site validation subset; otherwise exact diagonalization is required. The *definition* is
  exact-diagonalization.)
- **Global time grid:** `t_grid = logspace(log10(0.5), log10(t_cap), 60)` (60 points), with
  `t_cap = 2·max_v d_bound(v)` (unit front velocity for unit hopping; the factor 2 guarantees the
  grid overruns every site's boundary arrival). All constants frozen.
- **No stochastic repetitions.** Coherent evolution from a fixed state on a fixed H is
  **deterministic** — there is nothing to average over per site. The statistical ensemble is the
  set of admitted launch sites × the 5 window offsets (§9). Seeds do not enter the endpoint;
  the only rng in the pipeline is the stratified-shuffle control's `default_rng(0)`, already
  frozen in `transport_run.py`.

## 5. Boundary-arrival cutoff (frozen)

Measured, not assumed. For each launch site define the leaked probability
`P_out(t) = Σ_{v : ‖par[v]−par[v0]‖ > d_bound(v0)} |ψ_t(v)|²`
and
`t_bound(v0) = first grid time at which P_out(t) ≥ ε`, **`ε = 0.01`** (frozen), linearly
interpolated between grid points. All analysis uses only `t < t_bound(v0)`; probability that has
reached the boundary is a finite-size artefact and is never fitted.

## 6. MSD definition (frozen)

    MSD(t; v0) = Σ_v |ψ_t(v)|² · ‖par[v] − par[v0]‖²      (Euclidean, parallel space)

## 7. Fitting window and exponent extraction (frozen)

- **Convention:** `MSD(t) ∝ t^{2β}`, so `β = ½ · d[log MSD]/d[log t]`. Interpretation:
  β = 1 ballistic, β = ½ diffusive, β < ½ sub-diffusive; quasicrystal critical/multifractal
  states typically give `0 < β < 1`.
- **Fit window:** grid times with `t_fit_lo ≤ t ≤ κ · t_bound(v0)`, with **`t_fit_lo = 2.0`**
  (drop the first few hops of transient) and **`κ = 0.5`** (stay well pre-boundary). Both frozen.
- **Minimum leverage:** the window must contain **≥ 8 grid points** and span
  `t_hi / t_lo ≥ 8`. A site that cannot meet this pre-boundary **fails** (§8) — it is not
  refit on a shorter window.
- **Estimator:** ordinary least squares of `log MSD` on `log t` over the in-window grid points
  (unweighted), `β = slope / 2`. Record the fit's `R²_fit` per site.

## 8. Failure rules (frozen, applied before any interpretation)

Per launch site, exclude and tally the reason if any of:
- `‖P_W|v0⟩‖ < 0.05` (no mid-band weight; §3);
- no fit window meeting the §7 leverage requirement (patch too small for this site);
- `R²_fit < 0.90` (β is not a faithful power-law summary at this site — recorded, not silently
  kept).

Aggregate failure / stop rules (declare the endpoint **unresolved**, do not claim transport):
- if **> 20%** of admitted sites in any family fail `R²_fit ≥ 0.90`, the MSD-power-law
  assumption is not met for that family — report exponents descriptively with a caveat, make no
  transport claim;
- if the admitted-and-passing launch count per offset falls below **300**, treat as
  finite-size-limited (the pre-reg's outcome-4 analogue): report as unresolved, do not interpret;
- if the **classical-null** MSD exponent (§10) shows the same M4-over-M3 increment as the
  coherent engine, the coherent-vs-incoherent contrast fails and no "reads the address as
  transport" claim is made (the contrast is itself the finding).

## 9. Aggregation across offsets (frozen — reuse the sealed pipeline verbatim)

The per-vertex target vector `{β(v0)}` replaces `ld_primary` and is fed to the **identical**
`transport_run.py` machinery: nested M0→M4, `held_out_r2` leave-one-offset-out CV over the 5
`OFFSETS`, same GBT, with the `M4shuf` (stratified shuffle), `M3pos`/`M4pos` (position), and
`M3far`/`M4far` (long-range physical) controls, plus the pre-reg §2 conditional nulls and §3
fake-address / equal-count controls at the fixed reference radius. Report `M4−M3` ± std across
the 5 CV folds, for coherent and classical engines, all three families. No per-offset tuning.

## 10. Classical null engine (frozen)

Same launch sites and metric, classical random walk `P = A / deg`:
`MSD_cl(t; v0) = Σ_v [P^{t}]_{v, v0} · ‖par[v]−par[v0]‖²`, evaluated on the same log time grid
(integer-step interpolation as needed), with the identical boundary cutoff (§5), fit window
(§7) and failure rules (§8). Yields `β_cl(v0)`, the incoherent contrast. Expected diffusive
(β_cl ≈ ½) and address-blind.

## 11. Robustness variants (secondary; reported, never the basis of the claim)
- Graph-distance MSD (BFS distance in place of Euclidean).
- Unfiltered site quench (§3) and the secondary window |E| ≤ 0.2.
- Edge-length-weighted H.
- `R_min ∈ {6, 12}` and `κ ∈ {0.4, 0.6}` sensitivity band, to show the exponent's stability to
  the frozen constants (reported as a band; the frozen values above define the primary claim).

## 12. Decision threshold (frozen)

The dynamical endpoint **earns the word "transport"** only if, on `β(v0)` in the sealed mid-band,
**all** hold (mirroring `PREREG_transport_hierarchy.md §10`, applied to β, and requiring the
radius-saturation §2/§3 controls):

1. the coherent `M4−M3` increment on β is **positive held-out** (mean − 1·std across the 5 CV
   folds `> 0`);
2. it is **killed by the stratified shuffle** — `M4shuf−M3` within `±1·std` of 0, and the
   shuffle removes **≥ 70%** of the plain increment (the golden threshold met by the spectral
   result);
3. it is **not reproduced by the classical engine** — `β_cl` shows `M4−M3 ≤ 0.2 ×` the coherent
   increment;
4. it **survives both conditional nulls** (§2 of the pre-reg) and **exceeds both** the
   fake-address and equal-count controls (§3), at the fixed reference radius.

If (1) holds but the increment is not shuffle-killed → "reads multiscale geometry dynamically,
not cleanly the address." If (1) fails → "the spectral address signal does not surface in bulk
wavepacket spreading at this coupling" (a real, publishable negative, not a failure of the
programme). No family ordering is claimed. No new ontology ("perp space is physical") regardless
of result. This endpoint gates only the word **transport**, not the already-earned spectral
claim.

---

## 13. What this manifest deliberately does NOT decide
- It does not seal the pre-reg, and does not run.
- It inherits — does not re-decide — the interior mask (physical-radius manifest App-B), the
  reference radius for §12(4), and the silver/platinum-vs-golden scope.
- The frozen constants (`R_min = 8`, `ε = 0.01`, grid = 60 pts, `t_fit_lo = 2.0`, `κ = 0.5`,
  leverage `≥ 8 pts` & `≥ 8×`, `R²_fit ≥ 0.90`, thresholds in §8/§12) are proposals for crew
  red-pencil; once the crew signs off they are sealed and any later change is a dated amendment.

*End of draft. Committed to `gpt/workbench` only. No experiment was run; no pre-registration was
sealed; no file on `claude/giv-quasicrystal-phason-5syx5s` was touched.*

# DRAFT v3 — frozen protocol for the MSD transport endpoint (radius-saturation, stage-two)

**Status — DRAFT for crew review. NOT sealed, NOT run. No dynamics/address/LDOS/targets/scores
accessed to write this. No science-branch file altered.** The "required dynamical endpoint" of
`substrates/PREREG_radius_saturation.md §6` — the bulk wavepacket MSD exponent — frozen to the
same a-priori discipline as the address block M4.

**v3 (2026-08-29)** incorporates crew decisions B1–B8 after the geometry-only preflights, which
showed the analytic Lieb–Robinson (LR) window is infeasible at every family/extent/launch-depth
(`PREFLIGHT_GEOMETRY_REPORT_V2.md` `6ab1647`, F6). Full dated change log at the end. Several items
are flagged for crew judgement (§ "Open choices").

*Source: drafted by the `gpt/workbench` Claude collaborator from crew decisions relayed by Katie;
not part of the scientific record until reviewed and merged.*

---

## 0. What this endpoint is for

The transport claim is currently **spectral** (per-vertex LDOS). The pre-reg forbids the word
"transport" until an address increment also appears on a genuinely **dynamical** quantity. The
observable is per-vertex — a spreading exponent `β(v0)` per admitted launch — regressed on M0→M4
by the identical `transport_run.py` machinery. This document freezes **how `β(v0)` is defined**.

## 1. Frozen physical setup
- **Hamiltonian** `H = A` (adjacency, uniform hopping `J=1`, ħ=1); the address appears nowhere in
  H. Edge-length-weighted H is a robustness variant only.
- **Distance** Euclidean `‖par[v]−par[v0]‖`. **Boundary** `d_bound(i)=hull_depth(par)[i]`,
  per-vertex. **Unit** `ℓ = median edge length`; time in units `ħ/J`. All constants a-priori.

## 2. Launch-site selection (B3) — admission `d_bound ≥ 16ℓ`, spatially-balanced subsample

- **Admission raised to `d_bound(v0) ≥ 16ℓ`** (was 8ℓ): launches come from the **same
  `d_bound≥16ℓ` common set** the radius manifest evaluates, so the two endpoints share a
  population. (Preflight counts: 592–1714 per patch across tiers.)
- **Deterministic, spatially-balanced subsample (PROPOSAL, flagged for crew).** From the common
  set, select launches balanced across the **four PCA slabs** defined exactly as in the physical
  manifest §5 (PC1 of the common-set coordinates, contiguous equal-count slabs). Proposed count
  **`L = 400` per patch (100 per slab)**; if a patch's common set has `< 400`, use all of it.
  Within each slab, sort by `(PC1 projection, vertex index)` and take **evenly-spaced** indices to
  hit the per-slab quota (spatially spread along the slab). Uses no address; identical across
  engines and controls.
  - *Justification (geometry/compute, for crew):* exact-diagonalisation propagation costs
    `O(48·n²)` per launch (48 log-times × one length-n mode sum per time); `L=400` launches per
    patch × ~5k vertices × 54 patches is tractable offline, while `L` stays ≫ the ~6-offset
    replication level so per-offset β distributions are well sampled. **`L=400` is a proposal —
    the crew may raise/lower it; it must be frozen before sealing.**
- Every selected launch yields a `β(v0)` (§7); nothing downstream culls sites (B4, §8).

## 3. Initial state — primary is unfiltered, full-spectrum (B2)

**Primary — unfiltered site quench** `|ψ0⟩ = |v0⟩` (exactly localised: `MSD(0)=0`,
`P_strip(0)=0`). It spans the **full spectrum**. **This is a full-spectrum wavepacket-transport
test; it is NOT a mid-band test and must not be described as one.** It gates only the general word
"transport"; it does **not** by itself reproduce or establish the mid-band LDOS mechanism — that
is a separate, weaker claim (§12).

**Secondary — mid-band-projected mechanistic diagnostic (B5, no β fit).** `|χ0⟩ = P_W|v0⟩/‖·‖`
(`P_W` = projector onto `|E|∈[0.8,2.5]`) has **nonlocal** initial support and its excess MSD
`ΔMSD(t)=MSD(t)−MSD(0)` **can be zero or negative** (breathing/recoherence), so `log ΔMSD` is
undefined. **The β fit is removed from the secondary.** It is retained only as a **clearly
secondary signed-curve / integrated mechanistic diagnostic** (e.g. the signed `ΔMSD(t)` curve, or
`∫ΔMSD dt` over the common window), reported descriptively, **never called a localised launch**
and never the basis of the transport claim.

## 4. Time evolution and grid
- **Exact by definition:** `ψ_t(v)=Σ_k e^{−iE_k t} φ_k(v0) φ_k(v)`. (Chebyshev/Krylov allowed iff
  they reproduce exact-diag β within `Δβ≤0.01` on a fixed 100-site check.)
- **Fixed log-time grid**, 48 points, on the frozen fit window `[2, 8]` (§7). Same grid for both
  engines and all controls. Deterministic; no stochastic repetitions (coherent evolution from a
  fixed state is deterministic; the ensemble is launches × the six offsets).

## 5. Boundary strip and excess mass (unchanged from v2; used by the §7 rule)
`STRIP := {v : d_bound(v) < w·ℓ}`, `w=2` (frozen). `P_strip(t)=Σ_{v∈STRIP}|ψ_t(v)|²`,
`ΔP_strip(t)=P_strip(t)−P_strip(0)`. Per-destination hull-depth strip (correctly classifies
interior sites in every direction). For the primary launch `P_strip(0)=0`.

## 6. MSD definition
`MSD(t;v0)=Σ_v |ψ_t(v)|²·‖par[v]−par[v0]‖²`; `ΔMSD=MSD−MSD(0)` (= MSD for the primary).

## 7. Fit window (B1, B4) — LR retired as a gate; measured-boundary rule instead

**B1 — the analytic LR bound is RETIRED as an admissibility gate.** The preflight proved it
vacuous at every family/extent/depth (`t_hi≈0.12–0.90 ≪ t_lo=2`; extent-invariant at fixed depth;
would need ~145ℓ launch depth). It is **kept only as a documented, failed conservative diagnostic**
(Appendix LR) — reported, never used to admit or reject a window.

**B4 — pre-registered measured-boundary rule (run only AFTER sealing):**
- Retain the **fixed log-time grid** and the hull-depth **excess strip mass** `ΔP_strip(t)` (§5).
- Compute boundary crossing for **both** the coherent and the classical engine.
- Define **one common global admissible window** across **all** preselected launches, families,
  tiers, offsets **and both engines**.
- The **global boundary endpoint `t_bound*`** = the **earliest** time at which `ΔP_strip(t)`
  reaches the frozen **1% (`0.01`)** excess-boundary-mass threshold, over that entire set.
- **Primary β fit uses the fixed interval `[2, 8]` only if `t_bound* ≥ 8`.** If `t_bound* < 8`,
  the primary transport endpoint is declared **finite-size-limited** — do **not** shorten, retune
  or rescue the window after seeing results (B8; an authorised outcome, §12).
- **Retain every admitted site**; fit quality is a diagnostic, **never** a site-level exclusion.

**Exponent (every admitted site):** with `ΔMSD∝t^{2β}`, `β(v0)=½·slope` of an OLS fit of
`log ΔMSD` on `log t` over the `[2,8]` grid points. Record `R²_fit(v0)` as a **diagnostic**.

## 8. No feature-correlated missingness (B4) — both engines
- **Every admitted launch yields a `β`**; **no per-site `R²_fit` / curvature / dynamics-derived
  exclusion** (such a filter could correlate with the address). Admission uses only `d_bound`.
- **Address-correlated-admission check (retained from the review):** admission by `d_bound` is not
  *guaranteed* address-independent, so **report and test** the admitted population's M4-feature
  distribution vs the excluded population; any imbalance is a stated caveat.
- `R²_fit` is used only as (a) a per-site diagnostic and (b) an **aggregate** family/engine stop
  rule (median `R²_fit < 0.90` ⇒ that engine's exponent is descriptive, no transport claim).
- These rules apply **explicitly to both** the coherent and classical engines, on the **same
  common window**.

## 9. Aggregation & uncertainty (B7) — offsets are the replication unit

`{β(v0)}` replaces `ld_primary` in the identical `transport_run.py` pipeline (nested M0→M4, the
`M4shuf`/`M3pos`/`M4pos`/`M3far`/`M4far` controls, the pre-reg §2 conditional nulls and §3 parity
/ capacity controls) — for both engines, all families/tiers.

**Replace "mean − 1·fold-SD > 0"** (fold SD understates correlated-fold uncertainty). **Proposed
offset-level rule (thresholds flagged for crew):**
- treat the **six leave-one-offset-out held-out increments `{Δ_o}` as the six replication units**;
  **report all six `Δ_o` individually**, always, regardless of the aggregate verdict;
- **primary inference:** `median_o(Δ_o)` must exceed the **95th percentile of the offset-level
  stratified-shuffle null** `{Δ_o^shuf}` (the null the pipeline already produces, which preserves
  all M3-conditional structure);
- **supporting consistency:** report the sign pattern; require **≥ 5 of 6** offsets with `Δ_o > 0`
  as a supporting (not sole) criterion;
- **CI:** an **offset-level block bootstrap** (resample the six offsets with replacement), not a
  fold-variance CI.
This treats offsets — not vertices or CV folds — as independent replicates.

## 10. Classical null engine (unchanged) — continuous-time Markov generator
`Q = A·D⁻¹ − I` (column-stochastic), `p(t;v0)=e^{Qt}e_{v0}`,
`MSD_cl(t;v0)=Σ_v p_v(t;v0)·‖par[v]−par[v0]‖²`. Valid at all real `t`; same log grid, same common
window (§7), same excess-strip cutoff, same OLS exponent → `β_cl`. Time axis matched to the
quantum engine (unit exit rate ↔ `J=1`). Expected diffusive, address-blind.

## 11. Robustness variants (secondary; never the primary basis)
Graph-distance MSD; the mid-band secondary **signed-curve** diagnostic (§3, no β); secondary
window `|E|≤0.2`; edge-length-weighted H; classical exit-rate ×2; strip `w∈{1.5,3}`.

## 12. Decision threshold (B2, B7, B8)

The endpoint **earns the word "transport"** only if, on `β(v0)` from the **primary full-spectrum**
launch on the common `[2,8]` window, **all** hold:
1. the coherent increment passes the **offset-level rule** (§9): `median_o(Δ_o)` above the 95th
   percentile of the offset-level shuffle null, with ≥5/6 offsets positive;
2. it is **killed by the stratified shuffle** (`M4shuf−M3` consistent with 0; ≥70% of the plain
   increment removed);
3. it is **not reproduced by the classical engine** (`β_cl` increment ≤ 0.2× the coherent);
4. it **survives both conditional nulls** and **exceeds both** the representation-matched parity
   block and the capacity control (radius manifest §4);
5. the aggregate gates pass (median `R²_fit ≥ 0.90` per engine; global `t_bound* ≥ 8`; admitted
   launch count adequate per offset).

**Claim scope (B2):** success licences only **"a physical law reads the address in full-spectrum
wavepacket transport."** It does **not** establish the *mid-band* mechanism — that remains a
separate, weaker claim probed only by the descriptive secondary (§3).

**Authorised non-positive outcomes (B8):** if (1) holds but not (2) → "reads multiscale geometry
dynamically, not cleanly the address." If (5) fails on `t_bound*<8` → **finite-size-limited**
(a legitimate, publishable outcome, **not** a failed run). If (1) fails → "the spectral address
signal does not surface in bulk wavepacket spreading at this size/coupling." No family ordering;
no "perp space is physical" ontology, regardless of result. This endpoint gates only the word
*transport*, never the already-earned spectral claim.

## 13. Open choices requiring crew judgement
- **Launch count `L`** (§2): 400/patch proposed; crew to freeze.
- **Offset-level thresholds** (§9): the 95th-percentile null rule and ≥5/6 sign rule are proposals.
- **Global `t_bound*`** is measured post-seal; if the crew wants an a-priori feasibility read,
  only a geometry/measured-boundary calibration (which touches dynamics) can give it, and that must
  be sealed first — the analytic route is retired (B1).

## Appendix LR — the retired analytic bound (documented failed diagnostic)
`t_hi` = largest `t` with `N_strip·(Σ_{k≥G_strip}(d_max t)^k/k!)² ≤ 5e-3`. Preflight result:
`t_hi≈0.12–0.90` at every family/extent/launch-depth (0/6 feasible everywhere); invariant with
patch size at fixed depth; ~145ℓ depth needed to reach `t_hi=8`. Retained for transparency; **not**
an admissibility gate.

---

## Change log
**v3 — 2026-08-29** (crew decisions B1–B8): retired the analytic LR bound as a gate, keeping it as
a documented failed diagnostic (B1); restated the primary launch as unfiltered full-spectrum and
struck all "mid-band-analysed" wording, separating full-spectrum-transport from the mid-band
mechanism (B2); raised launch admission to `d_bound≥16ℓ` with a deterministic PCA-slab
spatially-balanced subsample and a flagged `L=400` proposal (B3); replaced the LR window with the
pre-registered measured-boundary rule — fixed grid, hull-depth excess mass, both engines, one
common global window, earliest 1% crossing, fixed `[2,8]` fit only if `t_bound*≥8`, else
finite-size-limited with no rescue, every site retained (B4); removed the β fit from the
energy-filtered secondary, keeping it as a signed-curve mechanistic diagnostic (B5); applied
boundary/quality rules to both engines on the same window (B6); replaced "mean−1·fold-SD>0" with an
offset-level rule treating the six offsets as replicates and reporting all six effects (B7); and
made a clean negative / finite-size-limited result an authorised outcome (B8).

**v2 — 2026-08-28.** Four-blocker repair (unfiltered primary, hull-depth strip, CTMC classical, no
per-site culling). **v1 — 2026-08-28.** Initial frozen MSD-endpoint draft.

*End of draft v3. Committed to `gpt/workbench` only. Nothing sealed; no dynamics/address/targets
accessed; no science-branch file altered.*

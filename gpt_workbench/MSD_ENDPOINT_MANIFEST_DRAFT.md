# DRAFT v4 — frozen protocol for the MSD transport endpoint (radius-saturation, stage-two)

**Status — DRAFT for crew review. NOT sealed, NOT run. Only a synthetic engineering benchmark was
run (no study geometry/dynamics/address/LDOS/targets/β/outcomes). No science-branch file altered.**

**v4 (2026-08-29)** applies Sol's exact-audit repairs B1–B7 on top of v3, using the authorised
synthetic benchmark (`gpt_workbench/benchmark_msd.py`). Full dated change log at the end.

*Source: drafted by the `gpt/workbench` Claude collaborator from crew decisions relayed by Katie;
not part of the scientific record until reviewed and merged.*

---

## 0. What this endpoint is for
A per-vertex spreading exponent `β(v0)` per admitted launch, regressed on M0→M4 by the identical
`transport_run.py` machinery. This document freezes **how `β(v0)` is defined and computed**.

## 1. Frozen physical setup
`H = A` (adjacency, `J=1`); Euclidean distance; `d_bound(i)=hull_depth(par)[i]`; `ℓ = median edge
length`. Address nowhere in H.

## 2. Algorithm & launch count (B1, B2) — benchmarked, not asserted

**Primary method: sparse/block Krylov propagation** (`scipy.sparse.linalg.expm_multiply`),
**validated** against exact diagonalisation to `max|Δ| = 3.4e-15` on an n=500 toy (benchmark).
**Exact diagonalisation is NOT the production method:** its per-vertex/all-time reconstruction is
`O(n²·L·T)` (≈`6000²·L·48`), intractable; even the eigendecomposition alone projects to ~57 min
across the 54 patches, before the infeasible reconstruction.

**Engineering benchmark (synthetic sparse graphs, matched only in n and degree; no study
geometry/dynamics/outcomes):**

| n | exact eigh | Krylov coh. L=50 | Krylov coh. L=400 | Krylov CTMC L=400 | peak RSS |
|---|---|---|---|---|---|
| 2000 | 5.2 s | 2.5 s | 26.7 s | 18.9 s | 1.3 GB |
| 4000 | 36 s | 5.9 s | 60 s | 46 s | 2.6 GB |
| 6000 | 67 s | 9.0 s | 105 s | 85 s | 4.2 GB |

Projected over 54 patches at largest n: **Krylov coherent+CTMC, L=400 ≈ 158 min, ~4.2 GB peak**;
L scales ~linearly, so **L=200 ≈ 80 min, ~2.5–3 GB**.

- **Proposed frozen launch count `L = 200` per patch** (100 fewer than v3's un-benchmarked 400):
  feasible (~80 min total, memory comfortable), and ≫ the 6-offset replication level so per-offset
  β distributions are well sampled. **Flagged for crew** — L may be set to 400 if the compute
  budget allows (benchmark shows it is possible at ~2.6 h / ~4.2 GB). Krylov numerical agreement
  must be **re-validated on a small toy of each family before sealing** (B2).
- Launches are the **deterministic PCA-slab spatially-balanced subsample** (physical manifest §5):
  `L/4` per slab, evenly spaced by sorted PC1 (lift-coordinate tie-break). No address used.

## 3. Initial state (unchanged from v3) — primary unfiltered, full-spectrum
`|ψ0⟩ = |v0⟩` (localised, `MSD(0)=0`). **A full-spectrum wavepacket-transport test; not a mid-band
test.** Secondary state handled in §6.

## 4. Time grids and boundary detection (B3) — separate monitoring grid

- **β-fit grid:** retain the **48 log-spaced points on `[2,8]`** for the exponent fit.
- **Boundary-monitoring grid (new, frozen):** a dense **linear grid on `[0,8]`** to detect a
  *transient* 1% excess-boundary-mass crossing that the log `[2,8]` grid could miss. **Proposed
  spacing `Δt = 0.05` → 161 points on `[0,8]`; flagged for crew review** (fine enough to catch a
  brief crossing at these hopping rates; crew may tighten).
- On the monitoring grid compute `ΔP_strip(t) = P_strip(t) − P_strip(0)` (hull-depth strip, `w=2ℓ`)
  for **both** engines and **every** selected launch.
- **`t_bound*` = the earliest sampled monitoring-grid time at which any launch, on either engine,
  reaches `ΔP_strip = 0.01`** — a **single global endpoint** over all launches/families/tiers/
  offsets/engines.
- **Primary β fit uses `[2,8]` only if `t_bound* ≥ 8`.** If `t_bound* < 8`, the primary transport
  endpoint is **finite-size-limited — no shortening, retuning, or rescue after seeing results**.

## 5. MSD, exponent, missingness (unchanged)
`MSD(t;v0)=Σ_v|ψ_t(v)|²‖par[v]−par[v0]‖²`; `β(v0)=½·slope` of OLS `log MSD` on `log t` over the
`[2,8]` grid. **Every admitted launch yields a β**; `R²_fit` is a diagnostic + aggregate stop
(median `R²_fit<0.90` ⇒ that engine descriptive), never a per-site cull. Admitted-vs-excluded
population M4-feature distributions reported and tested (admission not assumed address-independent).
Rules apply to **both engines on the same common window**.

## 6. Mid-band secondary (B4) — frozen as the signed ΔMSD(t) curve only
The mid-band-projected state `|χ0⟩=P_W|v0⟩/‖·‖` (`P_W`: `|E|∈[0.8,2.5]`) is reported **only as the
signed `ΔMSD(t)` curve on the common grid** — a descriptive mechanistic diagnostic. **No β fit, no
post-hoc AUC, no scalar endpoint**, and it is never called a localised launch. (Removed v3's "e.g."
open-endedness.)

## 7. Classical null engine (unchanged) — continuous-time Markov generator
`Q=A·D⁻¹−I`, `p(t)=e^{Qt}e_{v0}` via the same Krylov method; same grids, same window; yields
`β_cl`. Expected diffusive, address-blind.

## 8. Offset-level inference (B5-repaired) — randomisation over the same fold structure
- **Always report the six held-out (leave-one-offset-out) increments `{Δ_o}` and their sign
  pattern.** The six overlapping LOO folds are **not** treated as independent replicates.
- **Removed:** the ordinary six-offset bootstrap CI (v3) — it wrongly assumed fold independence.
- **Randomisation test (frozen):** for each of **≥ 1000 frozen stratified-shuffle repetitions**,
  recompute the **full six-offset held-out vector** and its **median**, building a null
  distribution of six-offset medians. This carries the **same fold dependence** in the observed and
  shuffled statistics.
- **Decision:** report the **randomisation tail probability** of the observed six-offset median
  against that null, with **≥ 5/6 offsets positive** as a **supporting** consistency criterion
  (not the sole test). **All seeds frozen** pre-seal.

## 9. Decision threshold & claim wording (B6, B7)
The endpoint is met only if the coherent six-offset-median increment is significant by the §8
randomisation test, is shuffle-killed (≥70% removed), exceeds the parity and capacity controls and
the conditional nulls, and the aggregate gates pass (`R²_fit`, `t_bound* ≥ 8`, launch count).

**Claim wording (B6, frozen):** success licences only —
> *"The address representation predicts heterogeneity in full-spectrum wavepacket spreading beyond
> the frozen physical descriptions and controls."*

**No inference that perpendicular space is a literal physical degree of freedom.** The older phrase
"a physical law reads the address" is retired.

**Classical-diagnostic caveat (B7, frozen):** if the **classical** power-law diagnostic fails
(median `β_cl` `R²_fit < 0.90`), the **coherent-vs-classical contrast is inconclusive**. This does
**not** erase a well-defined quantum `β` result, but it **prevents the strongest coherence-specific
claim** — report the quantum β with that limitation stated.

**Authorised non-positive outcomes:** shuffle-not-killed → "reads multiscale geometry, not cleanly
the address"; `t_bound*<8` → **finite-size-limited** (legitimate, not a failed run); randomisation
non-significant → address signal does not surface in spreading at this size/coupling.

## 10. Open choices for crew
- **`L`** (§2): 200 proposed (benchmarked feasible); 400 possible with more compute.
- **Boundary-monitoring spacing** (§4): `Δt=0.05` proposed; crew may tighten.
- **Randomisation repetitions** (§8): ≥1000 proposed; freeze the exact count and seeds at seal.

## Appendix LR — retired analytic bound (documented failed diagnostic)
`t_hi ≈ 0.12–0.90` at every family/extent/depth (preflight v2), extent-invariant at fixed depth,
~145ℓ depth needed for `t_hi=8`. Kept for transparency; **never** an admissibility gate (B1, prior).

---

## Change log
**v4 — 2026-08-29** (Sol audit B1–B7): benchmarked the propagation cost on synthetic graphs and
**proposed a frozen `L=200` with sparse Krylov as the primary method** (validated to 3.4e-15),
retiring the un-benchmarked L=400 and the "exact-diag is tractable" assumption (B1, B2); added a
separate dense **boundary-monitoring grid on `[0,8]` (Δt=0.05)** with `t_bound*` as the earliest
global crossing over both engines and no post-hoc rescue (B3); froze the mid-band secondary as the
**signed ΔMSD(t) curve only** — no AUC/scalar (B4); repaired offset-level inference to a
**randomisation test over the same six-offset fold structure** (≥1000 shuffles, median-of-six null,
tail probability + ≥5/6 supporting), removing the invalid bootstrap CI (B5); replaced the claim
wording with **"the address representation predicts heterogeneity in full-spectrum wavepacket
spreading beyond the frozen physical descriptions and controls"** and forbade the literal-physical-
DOF inference (B6); and stated that a failed classical power-law diagnostic makes the
coherent-vs-classical contrast **inconclusive** without erasing a well-defined quantum β (B7).

**v3 — 2026-08-29.** Crew decisions B1–B8. **v2 — 2026-08-28.** Four-blocker repair. **v1.** Initial.

*End of draft v4. Committed to `gpt/workbench` only. Nothing sealed; only the synthetic benchmark
run; no science-branch file altered.*

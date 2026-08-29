# DRAFT v4 — frozen `physical(r)` column manifest + design (radius-saturation experiment)

**Status — DRAFT for crew review. NOT sealed, NOT run. Only geometry-only checks were run to
produce this (no dynamics/address/LDOS/targets/scores). No science-branch file altered.**

**v4 (2026-08-29)** applies Sol's narrow closure corrections on top of the structurally-accepted v3
(which applied audit repairs A1–A8 using `gpt_workbench/compute_checks_v3.py`). Full dated change
log at the end.

*Source: drafted by the `gpt/workbench` Claude collaborator from crew decisions relayed by Katie;
not part of the scientific record until reviewed and merged.*

---

## 1. Frozen conventions
- `ℓ := median edge length` (measured `= 1.000` all families). Radius `r` = Euclidean par-space
  distance. Radius ladder **`{2,4,8,12,16}`, retained for all families incl. golden (A3)**.
- **Evaluated population:** the `d_bound ≥ 16ℓ` common interior set, **fixed across all rungs**
  within a tier (changing `r` changes only which columns are included, never the vertices).
- **Six frozen offsets:** `(0.13,0.37)(0.29,0.11)(0.41,0.23)(0.05,0.47)(0.19,0.31)(0.37,0.09)`.
- **Regressor:** sealed harness GBT, identical everywhere.

## 2. Geometry-matched tiers (A2) — now with the measured metrics

The three missing patches (silver e14/e16, platinum e16) were measured (geometry only); **all nine
planned patches now have full metrics** (mean over the six offsets):

| tier | patch | n | hull area | diameter | **aspect(r16)** | usable r16 area | r16 count (min) |
|---|---|---|---|---|---|---|---|
| small  | silver e14   | 3360 | 2753 | 61.4 | **1.02** | 516  | 653 |
| small  | golden e18   | 3999 | 3272 | 95.9 | **3.12** | 452  | 581 |
| small  | platinum e16 | 3651 | 2977 | 80.2 | **1.25** | 569  | 725 |
| medium | silver e16   | 4341 | 3552 | 70.0 | **1.04** | 885  | 1102 |
| medium | golden e20   | 4913 | 4032 | 106.5| **3.07** | 794  | 1012 |
| medium | platinum e18 | 4604 | 3726 | 88.6 | **1.27** | 921  | 1165 |
| large  | silver e18   | 5463 | 4478 | 78.8 | **1.02** | 1370 | 1698 |
| large  | golden e22   | 5920 | 4840 | 116.7| **2.98** | 1210 | 1535 |
| large  | platinum e20 | 5660 | 4554 | 99.9 | **1.25** | 1345 | 1704 |

**Tier confirmation (A2, outcome-blind):** the tiers match well on **r16 count** (small 581–725,
medium 1012–1165, large 1535–1704) **and on usable r16 area** (small 452–569, medium 794–921,
large 1210–1370) — within ~20% / ~15%. The tiers are **confirmed**, not re-optimised.
**⚠️ Reported morphology mismatch (A3):** they do **not** match on shape — golden's r16 interior is
strongly elongated (**aspect ≈ 3.0**) vs silver (~1.02, near-round) and platinum (~1.25). Per A3
this is a **reported morphology / control issue, not grounds for a golden radius-12 ceiling** — the
ladder stays through r=16 for golden; the elongation is handled by the PCA-slab inner CV (§5) and
**reported as a morphology diagnostic/control**. It is **not** added as a regression feature.

## 3. `physical(r)` column groups (A6/A7 applied)

### Group A — radial histogram g(ρ) — **A6-corrected, right-closed bins**
- Centre **excluded**; bin index **`k = ceil(d/ℓ − τ)`, `τ = 1e-9`, retaining `k = 1 … r`**.
- Bin `k` represents the **left-open, right-closed** annulus **`((k−1)ℓ, kℓ]`** (up to `τ`). Exact unit-edge
  neighbours (`d=ℓ`) → bin 1; sub-edge thin-rhombus diagonals → bin 1; **rung `r` never uses any
  point beyond `rℓ`** (fixes the v2 `(r+0.5)ℓ` overrun). **r columns per rung.**
- **Geometry check ran (A6):** min inter-vertex distance = **0.765ℓ (silver), 0.618ℓ (golden),
  0.518ℓ (platinum)** — all `< ℓ`, confirming sub-edge diagonals exist; bin-1 occupancy ≈ 4.7–5.5.
  **The innermost bin is genuinely non-empty and is retained** (the v1 "empty bin" claim was
  wrong; the v2 correction is now confirmed by direct measurement).

### Group B — neighbour-degree moments within each `s∈S(r)` → 4 cols × m(r).
### Group D — coarse-grained ψₙ (`n∈{N/2,N,2N}`) within each `s` → 3 cols × m(r).
### Group E — packing/void via **padded-super-patch** Voronoi (mandatory, §A5) → 2 cols × m(r).
Edge-length moments removed from the primary (A7); robustness diagnostic only.
Per-rung dim `= r + 9·m(r)` → **11, 22, 35, 48, 61** for r = 2,4,8,12,16.

## 4. Parity control (A5-repaired) — z_N rejected, (degree, Voronoi-area) adopted

**z_N is degenerate — rejected as the parity field.** Geometry check: `Var(Re z_N) ≈ Var(Im z_N)
≈ 0.000` on **every** tier (the complex bond-orientational order is a near-**constant** field on the
deep interior — the tiling's global orientational order makes it nearly uniform), with rising
condition number (3.2 → 19.8 as elongation grows). A near-constant field through `_m4_cols`
produces near-constant, noise-amplified columns — an inadequate parity control.

**Adopted parity field (A5): the two-component, address-free physical field
`(local graph degree, padded Voronoi-cell area)`**, each **z-scored within the `d_bound≥16ℓ`
common set**, passed through the exact 11-column `_m4_cols` pipeline. Both are physical quantities
already represented in the physical feature family (degree ∈ M1/B; Voronoi area ∈ Group E), so this
tests **repackaging**, not arbitrary new content.
- **Rank-2 verified on every planned patch (geometry check):** covariance eigenvalues
  ≈ 0.29–0.55 (min) / 1.45–1.72 (max), **condition number 2.6–6.0**, `deg_var ≈ 1.2–1.4`,
  `voro_var ≈ 0.006–0.017` — comfortably rank 2 everywhere. (For the deep `r16` vertices, the
  padded and core Voronoi cell areas are identical to machine precision by the §A5 convergence
  result, so the padded area is well-defined and equals what the rank check used.)
- **Zero-variance handling (frozen):** if either physical component's within-set std `< 1e-9` on a
  patch, that patch's **representation-parity verdict is marked unavailable / infeasible and
  reported** — the capacity control is **not** substituted for a failed physical parity field
  (capacity and physical parity answer different questions: capacity guards column-count inflation;
  physical parity guards *representational* repackaging). No silent divide-by-zero. (No patch
  triggered this in the check.)
Capacity control retained separately (§6), for its own distinct question.

## 5. Validation (A6/A9 clarified)
- **Outer (primary):** leave one of the six offsets out **entirely**; features are geometry-only,
  the held-out offset's targets are never seen.
- **Replication level:** the **six offsets are the sampling clusters** — the level over which
  statistical conclusions are stated (not vertices or folds). The six leave-one-offset-out
  estimates themselves remain **correlated through their overlapping training sets**, and are never
  treated as independent replicates (the inference uses the randomisation test of the conditional-
  null manifest §3, which preserves this fold dependence).
- **Inner CV (frozen, A6):** within each *training* patch, PC1 of the centred `r16` common-set
  coordinates → project → **4 contiguous equal-count slabs**. **Inner fold `j` simultaneously
  holds out slab `j` from *every* training-offset patch**, while the outer offset stays wholly
  unseen. Frozen: PCA centring = subtract the common-set mean; PC1 sign rule `PC1[0] ≥ 0`
  (else `PC1[1] ≥ 0`); **ties in the PC1 projection broken by lexicographic order of the integer
  lift coordinates** `lifts[i]` (canonical and offset-robust — replaces vertex-index tie-breaking);
  remainder vertices to the lowest-index slabs. **Floor check (A4): all nine tiers PASS** — every
  tier has `r16 ≥ 400` (min 581) and every equal-count slab `≥ 100` (min slab 148).

## 6. Capacity control (A8) — frozen seeds/repetitions
The pure-capacity null is **not** one arbitrary Gaussian draw (20 was insufficient for a stable
95th percentile). Frozen: **200 independent i.i.d.-Gaussian blocks** of the same dimensionality as
the parity block, **seeds `0…199`**; report the **full distribution** and the predeclared summary
(**mean and 95th percentile**) of their increment as the capacity noise-floor the address increment
must exceed. All seeds frozen pre-seal. (This 95th percentile is also the proposed outcome-
independent calibration for `δ*`; see §7 and conditional-null manifest §5.)

## 7. Hierarchical decision procedure (A7-repaired)
Evaluated in order:
1. **Infeasible (physical/count only)** — a tier's `r16` common set `< 400`, or a slab `< 100`, or
   a required physical-size match unmet. → stop; do not interpret. (Purely feasibility; **tier
   instability does NOT live here.**)
2. **Mixed / unstable (a scientific result)** — the address increment varies across tiers or
   families beyond the offset-level randomisation uncertainty. → report as a **mixed** scientific
   outcome, explicitly **not** "infeasible."
3. **Radius fade compatible with physical compression** — declared by a **predeclared equivalence
   rule**, requiring **both**: (a) relative reduction `ΔR²_addr(16)/ΔR²_addr(2) < ρ*` **and**
   (b) the absolute increment below a **practical-equivalence margin** `ΔR²_addr(16) < δ*`.
   **"CI includes zero" is NOT accepted as evidence of equivalence.**
   - **`δ*` — outcome-independent justification required.** `δ*` **must not** be chosen to sit just
     above the known `+0.004` fully-M3-residual result. Proposed **calibration:** `δ*` = the **95th
     percentile of the 200-draw Gaussian capacity null** (§6) at the reference radius — a measured
     noise-floor, independent of any address outcome. A fixed `δ* = 0.005` R² is retained only as a
     fallback and is **explicitly provisional / unratified**.
   - **`ρ* = 0.25` is likewise provisional / unratified.** Denominator handling: `ρ` is defined only
     if `ΔR²_addr(2) > δ*` and its six-offset sign is stable (≥5/6); otherwise `ρ` is undefined and
     the outcome routes to branch 2/1, never to "fade" (see conditional-null manifest §5).
4. **Representation collapse** — increment survives radius but collapses to the (degree,Voronoi)
   parity block (§4). → representational.
5. **Stable residual increment** — survives radius, exceeds **both** the parity block and the
   capacity control (§6), and survives the conditional nulls at the offset level. → provisional
   irreducible.

## 8. Open choices for crew
- **`δ*`** (§7): capacity-95th-percentile calibration proposed (outcome-independent); fixed 0.005 R²
  fallback is provisional/unratified.
- **`ρ*`** (§7): 0.25 provisional/unratified.
- Whether golden's aspect ≈ 3.0 (§2) warrants any extra boundary control beyond the PCA-slab CV.

---

## Change log
**v4 — 2026-08-29** (Sol narrow closure): golden elongation reworded to a reported morphology
diagnostic/control, **not** a regression feature; the parity zero-variance rule now marks a
degenerate patch's representation-parity verdict **unavailable/infeasible** rather than substituting
the (differently-purposed) capacity control; the Gaussian capacity null raised from 20 to **200
draws (seeds 0…199)** reporting the full distribution; offsets clarified as **sampling clusters**
with the six LOO estimates correlated through overlapping training sets; `ρ*=0.25` / `δ*=0.005`
marked **provisional/unratified** with an outcome-independent `δ*` calibration (capacity 95th
percentile) and an explicit "not chosen to sit above +0.004" caution; and the annulus wording fixed
to **left-open, right-closed**.

**v3 — 2026-08-29** (Sol audit A1–A8): right-closed radial bins `k=ceil(d/ℓ−τ)` with the geometry
occupancy/min-distance check (A1); measured the missing silver e14/e16, platinum e16 metrics and
confirmed the tiers on count+usable-area with a flagged aspect-ratio mismatch (A2); kept the golden
ladder through r=16, treating elongation as a reported control issue (A3); froze and verified the
≥400/≥100-per-slab floor — all nine tiers pass (A4); rejected the degenerate `z_N` parity field
(var≈0 measured) and adopted the rank-2-verified `(degree, Voronoi-area)` field through the exact
`_m4_cols`, with frozen zero-variance handling (A5); clarified the inner CV (fold `j` holds out
slab `j` across all training patches; lift-coordinate lexicographic tie-break) (A6); repaired the
hierarchical tree (feasibility vs mixed separated; "CI includes zero" ≠ equivalence; predeclared
equivalence rule with relative + absolute margin flagged for crew) (A7); and froze a 20-draw
capacity control with fixed seeds (A8).

**v3 — 2026-08-29** (Sol audit A1–A8). **v2 — 2026-08-29.** Crew decisions A1–A11.
**v1 — 2026-08-28.** Initial column manifest.

*End of draft v4. Committed to `gpt/workbench` only. Nothing sealed; only geometry-only checks run;
no science-branch file altered.*

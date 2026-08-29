# DRAFT v2 — frozen `physical(r)` column manifest + design (radius-saturation experiment)

**Status — DRAFT for crew review. NOT sealed, NOT run. No dynamics/address/LDOS/targets/scores
accessed to write this. No science-branch file altered.** A workbench design artifact only. It
gives the `physical(r)` block, geometry tiers, validation and controls of
`substrates/PREREG_radius_saturation.md` the same a-priori discipline as the sealed address block
M4 (`transport_run.py::_m4_cols`, 11 columns).

**v2 (2026-08-29)** incorporates crew decisions A1–A11 after the v1/v2 geometry-only preflights
(`PREFLIGHT_GEOMETRY_REPORT.md` `49d37be`, `PREFLIGHT_GEOMETRY_REPORT_V2.md` `6ab1647`) and the
padding-convergence check (§A5). Full dated change log at the end. It remains a proposal; several
items are explicitly flagged for crew judgement (§ "Open choices").

*Source: drafted by the `gpt/workbench` Claude collaborator from crew decisions relayed by Katie;
not part of the scientific record until reviewed and merged.*

---

## 1. Frozen conventions

- **Radius unit** `ℓ := median edge length` (measured `= 1.000` for all families). "Radius r"
  means Euclidean parallel-space distance `≤ r·ℓ` (address M4 stays graph-shell; the contrast is
  intended).
- **Radius ladder (A1):** `S = {2, 4, 8, 12, 16}`, retained for all families. `S(r)={s∈S:s≤r}`,
  `m(r)=|S(r)|`.
- **Evaluated population (A3):** every rung within a tier is evaluated on the **same** fixed
  vertex set — the `d_bound ≥ 16ℓ` common interior set (`d_bound(i)=hull_depth(par)[i]`). Changing
  `r` changes only which `physical(r)` columns are included, **never which vertices are scored**.
  This removes the shrinking-sample confound entirely.
- **Six fresh offsets (A4), frozen:**
  `(0.13,0.37) (0.29,0.11) (0.41,0.23) (0.05,0.47) (0.19,0.31) (0.37,0.09)` — the offsets used in
  both preflights (disjoint from the sealed transport run's five).
- **Regressor:** the sealed harness GBT (`HistGradientBoostingRegressor(max_depth=3, max_iter=250,
  learning_rate=0.06, l2_regularization=1.0, random_state=0)`), identical for every rung, control
  and family.
- **Moment definitions:** `mean`, population `variance`, `skewness`, `excess kurtosis`; the three
  higher moments set to 0 when `σ<1e-9`.

## 2. Geometry-matched tiers (A2) — replacing equal generator extents

Equal generator extent does **not** mean equal physical size (preflight F2), so the three tiers
below were chosen **outcome-blind** to approximately match the radius-16 common-set count across
families:

| tier | silver(8) | golden(10) | platinum(12) | r=16 common count (silver / golden / platinum) |
|---|---|---|---|---|
| small  | e14 | e18 | e16 | 660 / 592 / 728 |
| medium | e16 | e20 | e18 | 1117 / 1020 / 1168 |
| large  | e18 | e22 | e20 | 1714 / 1544 / 1713 |

Radius-16 counts are well matched within each tier (spread ≤ ~15%). Physical area / diameter /
usable-r16-area (from preflight v2, per-offset spread <1%):

| patch | n | hull area | diameter | usable r16 area |
|---|---|---|---|---|
| silver e18 (large) | 5463 | 4478 | 78.8 | 1370 |
| golden e18 (small) | 3999 | 3272 | 95.9 | 452 |
| golden e20 (medium)| 4913 | 4032 | 106.5 | 794 |
| golden e22 (large) | 5920 | 4840 | 116.7 | 1210 |
| platinum e18 (medium)| 4604 | 3726 | 88.6 | 921 |
| platinum e20 (large)| 5660 | 4554 | 99.9 | 1345 |

**⚠️ Flagged mismatches (A2 requires flagging, not silent tier changes):**
1. **Missing physical metrics.** Area / diameter / usable-area for **silver e14, silver e16,
   platinum e16** were **not measured** — computing them needs a geometry run beyond the single
   padding-convergence check the crew authorised, so they are left as a **required pre-seal
   geometry-only measurement**, not fabricated. Counts (from the first preflight) match; physical
   size must be confirmed.
2. **Residual shape mismatch.** Even matched on r=16 count, **golden stays elongated**: in the
   large tier, areas are comparable (silver 4478 / golden 4840 / platinum 4554) but diameters are
   not (78.8 / 116.7 / 99.9). Matching count does not match diameter/aspect. This bears on
   boundary effects and on the inner-CV slab construction (§5); flagged for crew.

## 3. The `physical(r)` column groups (A6, A7 applied)

Per-vertex, address-free, prefix `phys_`. **Group C (edge-length moments) is removed from the
primary (A7)** — unit-rhombus edges make it degenerate — and appears only as a pre-labelled
robustness diagnostic (§6).

### Group A — radial histogram g(ρ) (A6-corrected)
The centre is **excluded**, and bins are **integer-centred** to eliminate the boundary pile-up of
edge-neighbours (which all sit at exactly `d=ℓ`):
- bin index `k(j) = round(‖par[j]−par[i]‖ / ℓ)` with round-half-up tolerance `+1e-9`
  (i.e. `k = floor(d/ℓ + 0.5 + 1e-9)`), excluding `j=i`;
- `phys_gann_k = #{ j≠i : k(j)=k }`, for **k = 1 … r** (`k=0`, i.e. `d<0.5ℓ` incl. the centre, is
  excluded → no self-count, no ambiguous edge). **r columns per rung.**
- **Correction to the v1 "empty innermost bin" claim (adversarial, both directions):** the
  innermost retained bin `k=1` (`[0.5,1.5)ℓ`) is **expected to be non-empty** — it captures both
  the unit-length edge-neighbours (`d=ℓ`) *and* the sub-edge thin-rhombus short-diagonal partners
  (`≈0.6–0.77ℓ` for AB/Penrose thin rhombi). It should therefore be **retained**, not eliminated;
  what v1 got wrong was calling it empty. A one-line geometry check (min inter-vertex distance and
  the `k=1` occupancy) should confirm this before sealing.

### Group B — neighbour-degree moments within each `s∈S(r)`
`{deg[j] : j∈Nb(i,s)}` (Euclidean ball `Nb(i,s)={j≠i:‖par_j−par_i‖≤s·ℓ}`); 4 moments →
**4 columns × m(r)**.

### Group D — coarse-grained bond-orientational order ψₙ within each `s∈S(r)`
`ψₙ(i)=|mean_bond exp(i n θ)|` for `n∈{N/2,N,2N}`, averaged over `{i}∪Nb(i,s)` →
**3 columns × m(r)**.

### Group E — packing/void via **padded-super-patch** Voronoi (A5, mandatory)
Voronoi cell areas of the parallel-space point set, per-vertex mean and variance over `Nb(i,s)`:
`phys_voro_mean_s{s}`, `phys_voro_var_s{s}` → **2 columns × m(r)**. **Cells are computed on a
padded super-patch** (§A5), so every cell contributing to a core descriptor is bounded/uncensored.

### Exact dimensions (A8)
Per-rung dim `= r + 9·m(r)` (A=r; B+D+E = 4+3+2 = 9 per radius-slice):

| rung r | m(r) | A | B(×4) | D(×3) | E(×2) | **total** |
|---|---|---|---|---|---|---|
| 2 | 1 | 2 | 4 | 3 | 2 | **11** |
| 4 | 2 | 4 | 8 | 6 | 4 | **22** |
| 8 | 3 | 8 | 12 | 9 | 6 | **35** |
| 12| 4 | 12| 16 | 12 | 8 | **48** |
| 16| 5 | 16| 20 | 15 | 10 | **61** |

Strictly nested; every column at rung r persists unchanged at larger r.

## A5. Padded-super-patch Voronoi + convergence check (mandatory)

Voronoi for Group E (and for any packing descriptor) is computed on a **padded super-patch**
generated at `core extent + Δ`, then restricted to core vertices; this gives a valid bounded cell
to every vertex contributing to an r=16 descriptor (preflight v2 F5: with padding, **zero** cells
remain invalid).

**Convergence result (the one authorised geometry-only run;** `gpt_workbench/pad_convergence_check.py`):
comparing per-core-cell **area and perimeter** at `Δ=4` vs `Δ=6` on silver e14, golden e18,
platinum e18 (2 offsets each):

| case | core cells compared | max rel Δarea | max rel Δperimeter |
|---|---|---|---|
| silver e14 | 3365 | 3.0e-13 | 3.5e-15 |
| golden e18 | 3995 | 1.2e-12 | 3.5e-15 |
| platinum e18 | 4605 | 6.7e-13 | 3.5e-15 |
| **worst case** | — | **1.2e-12** | **3.5e-15** |

**Tolerance & verdict:** pass bar = **1e-6 relative** on both area and perimeter; observed worst
case is **~6 orders below** it. `Δ=4` and `Δ=6` cells are identical to machine precision (a
Voronoi cell depends only on its Delaunay neighbours, which `Δ=4` already fully includes).
**Therefore `Δ=4` is a converged, validated padding, and platinum e22's `Δ=4` result stands.**
Frozen rule: **`Δ ≥ 4`, and the padding ring width must be `≥ 3ℓ`** (verified 10–16ℓ in preflight);
if a family/tier cannot afford `≥3ℓ` (generator too slow/saturated), flag it, do not reduce Δ.

## 4. Parity control (A11) — genuine 2-component physical field through the exact pipeline

Inspecting `transport_run.py::_m4_cols(f, field)`: it takes a **2-component** field `(n,2)` and
returns exactly 11 columns — for each shell `r∈{2,4,8}`: shell-mean (2 cols) + shell-variance-sum
(1 col) = 9; plus gradient magnitude (1) and `hull_depth(field)` of the field-value cloud (1).

**Representation-matched parity block (frozen):** feed an **address-free, genuinely 2-component
physical field** through the *identical* `_m4_cols`:
- **Field = the complex bond-orientational order parameter** `z_N(i) = mean_{bond b at i}
  exp(i·N·θ_b)` (N = family fold; θ_b = `arctan2` of `par[j]−par[i]`). Its two components are
  `(Re z_N, Im z_N)` — physical (bond geometry only), **no perpendicular-space content**. (Note:
  M3 already uses the *magnitude* `|z_N|`; the parity field uses the *complex* value, a distinct,
  genuinely 2-D physical field.)
- **Normalisation:** z-score each of `Re z_N`, `Im z_N` across the `d_bound≥16ℓ` common set
  (subtract mean, divide by std) so the 2-D cloud is well-conditioned.
- **Pipeline:** `parity_block = _m4_cols(f, column_stack([Re z_N, Im z_N]_zscored))` → **exactly
  11 columns by the identical construction** (shell-means, shell-variances at {2,4,8}, gradient,
  and a hull-depth of the field cloud).

**Honest caveat (A11 requires it):** this achieves **exact pipeline / representation parity** (the
same 11-column multiscale machinery, no 8+3 padding). It is **not** a physically interpretable
block: `hull_depth` of an orientational-order cloud has no physical meaning — it is a
representational analogue of M4's window-depth column. So the parity block answers "does the
identical multiscale machinery on a real physical 2-field reproduce the address increment?", and
must not be over-read further. The pure-capacity control (11 i.i.d. Gaussian columns) is retained
alongside.

## 5. Validation (A9)

- **Outer (primary):** leave **one of the six offsets out entirely**; feature construction is
  geometry-only and the held-out offset's targets are **never** seen during training.
- **Replication level:** **offsets are the independent replication unit** — statistical
  conclusions are stated over the six offsets, **not** over vertices or CV folds (which are
  correlated).
- **Inner (frozen deterministic slabs; NOT equal-angle quadrants):** within each *training* patch,
  take the `d_bound≥16ℓ` common-set coordinates `par`, **centre** them (subtract the common-set
  mean), compute the `2×2` covariance, take **PC1** = eigenvector of the larger eigenvalue with a
  frozen **sign rule** (fix `PC1[0] ≥ 0`; if `PC1[0]=0`, require `PC1[1] ≥ 0`), project the
  centred coordinates onto PC1, **stable-sort** by `(projection, vertex-index)` (tie handling
  frozen), and split into **4 contiguous equal-count slabs** (remainder vertices assigned to the
  lowest-index slabs). Fit separately within each training patch. This yields balanced folds even
  for golden's elongated interior (§2 caveat 2), which equal-angle quadrants do not (preflight v2
  F4).

## 6. Robustness diagnostics (pre-labelled, secondary; never the primary basis)
- **Edge-length moments** (former Group C) — reported only if a family shows non-trivial
  edge-length spread (none expected).
- Graph-distance variant of `physical(r)`; rhombus thick/thin fraction as an alt Group-E.

## 7. Hierarchical decision procedure (A10) — replaces the overlapping outcomes

Evaluated in order; the first matching branch is the verdict (per tier/family, then reconciled):
1. **Infeasible / finite-size-limited** — the tier's `d_bound≥16ℓ` common set is below the frozen
   floor, or physical-size matching (§2) is unmet, or ΔR²_addr is unstable across tiers beyond the
   offset-level uncertainty. → stop; do not interpret shape.
2. **Radius fade (physical compression)** — `ΔR²_addr(r)` decays to ≈0 as r→16
   (`ΔR²_addr(16)/ΔR²_addr(2) < 0.25`, offset-level CI includes 0 at r=16). → address is a compact
   encoding of finite-radius real-space structure.
3. **Representation collapse** — the increment survives radius but **collapses to the
   representation-matched parity block** (§4). → the advantage was representational, not
   informational.
4. **Stable residual address increment** — survives the radius ladder, exceeds **both** the parity
   block and the capacity control, and survives the conditional nulls at the offset level. →
   provisional irreducible increment.
5. **Inconclusive / mixed** — families or tiers disagree beyond the offset-level uncertainty. →
   report as mixed; make no single verdict.

## 8. Open choices requiring crew judgement
- The three **missing physical-size metrics** (silver e14/e16, platinum e16) need a geometry-only
  measurement before sealing (§2 flag 1).
- **Radius-16 adequacy floor** (minimum common-set count per tier) is not yet fixed — needed for
  branch 1.
- Whether to **cap golden's ladder at r=12** given its residual elongation (§2 flag 2), or accept
  the large-tier golden e22 count as adequate.
- Parity-field choice (§4): `z_N` complex components are proposed; the crew may prefer a different
  address-free 2-field, but it must go through the exact `_m4_cols` (no padding).

---

## Change log
**v2 — 2026-08-29** (crew decisions A1–A11): retained ladder {2,4,8,12,16} (A1); replaced equal
extents with geometry-matched tiers + physical metrics, with flagged missing e14/e16 metrics and a
residual golden-elongation mismatch (A2); fixed the evaluated set to the `d_bound≥16ℓ` common
population for all rungs (A3); froze the six preflight offsets (A4); made padded-super-patch
Voronoi mandatory and added the Δ=4-vs-Δ=6 convergence check with a 1e-6 tolerance (A5); corrected
Group A annuli (exclude centre, integer-centred round-bins with tolerance, and *corrected the
"empty innermost bin" claim* — it is expected non-empty) (A6); removed edge-length moments from the
primary (A7); updated all feature counts to `r+9·m(r)` (A8); specified outer leave-one-offset-out
validation with offsets as the replication unit and a frozen PCA-slab inner CV, not equal-angle
quadrants (A9); replaced the overlapping outcomes with a 5-branch hierarchical procedure (A10); and
rebuilt the parity control as a genuine 2-component physical field (complex `z_N`) through the exact
11-column `_m4_cols`, with an honest depth-column caveat (A11).

**v1 — 2026-08-28.** Initial frozen `physical(r)` column manifest.

*End of draft v2. Committed to `gpt/workbench` only. Nothing sealed; no dynamics/address/targets
accessed; no science-branch file altered.*

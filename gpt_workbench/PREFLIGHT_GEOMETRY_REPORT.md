# Geometry-only feasibility preflight — report

**Date: 2026-08-29. Status: geometry-only feasibility record. Nothing sealed, no manifest
amended, no dynamics/address/targets used, science branch untouched.** Authorised by
Work-GPT/Sol (2026-08-28) to test whether the radius-saturation and MSD manifests are
geometrically feasible at the proposed patch sizes, before any crew sealing decision.

Method + exact frozen configuration + results below. Code: `gpt_workbench/preflight_geometry.py`
(committed alongside this report; reproducible). *This report resolves nothing on its own; it is
input to crew review.*

---

## 1. Methods (what was and was not computed)

**Computed (geometry + admission masks only):** for each family × extent × fresh offset, the
tiling was generated (`substrates/generate_rank4.py`), and from **parallel-space positions and
graph connectivity only** we computed: convex-hull depth `d_bound` per vertex, graph degree,
interior-admission counts under `d_bound ≥ r·ℓ`, Voronoi cell boundedness and guard-ring
validity, multi-source graph distance to the boundary strip, and an **analytic** Lieb–Robinson
series bound for the MSD time window.

**Deliberately NOT used (per Sol's constraints):** no Hamiltonian, no eigen-decomposition, no
time evolution, no LDOS, no MSD dynamics, no perpendicular-space **address**, no regression, no
scores, no outcome curves. The MSD "feasibility" is a pure geometry+series calculation, not a
wave simulation. `ℓ = median edge length` (measured `= 1.000` for all families — unit-rhombus
edges, as expected).

## 2. Frozen configuration

- Families `N ∈ {8 silver, 10 golden, 12 platinum}`; extents `{12, 14, 16}`; radii
  `r ∈ {2,4,8,12,16}` (edge units).
- **Six fresh offsets** (disjoint from the sealed transport run's five):
  `(0.13,0.37) (0.29,0.11) (0.41,0.23) (0.05,0.47) (0.19,0.31) (0.37,0.09)`.
- Boundary strip width `w = 2ℓ`; Voronoi guard margin `= 2ℓ`; MSD launch depth `R_min = 8ℓ`;
  MSD fit-window lower bound `t_lo = 2`; LR leakage cap `ε' = 5·10⁻³`; required
  `t_hi/t_lo ≥ 4` (i.e. `t_hi ≥ 8`).

## 3. Interior survivors — counts and proportions (mean over 6 offsets)

The **`r ≥ 16ℓ` row is the binding constraint** (the common set for the radius ladder).

| family | extent | r≥2ℓ | r≥4ℓ | r≥8ℓ | r≥12ℓ | **r≥16ℓ (common set)** |
|---|---|---|---|---|---|---|
| silver(8)   | 12 | 2116 (84.6%) | 1755 (70.2%) | 1139 (45.6%) | 686 (27.5%) | **319 (12.8%)** |
| silver(8)   | 14 | 2900 (86.3%) | 2486 (74.0%) | 1740 (51.8%) | 1158 (34.5%) | **660 (19.6%)** |
| silver(8)   | 16 | 3788 (87.3%) | 3340 (76.9%) | 2464 (56.8%) | 1739 (40.1%) | **1117 (25.7%)** |
| golden(10)  | 12 | 1492 (81.9%) | 1156 (63.4%) | 590 (32.4%) | 172 (9.5%) | **3 (0.2%)** |
| golden(10)  | 14 | 2061 (84.1%) | 1671 (68.2%) | 982 (40.0%) | 426 (17.4%) | **83 (3.4%)** |
| golden(10)  | 16 | 2724 (85.6%) | 2282 (71.7%) | 1469 (46.2%) | 790 (24.8%) | **280 (8.8%)** |
| platinum(12)| 12 | 1731 (83.1%) | 1399 (67.1%) | 830 (39.9%) | 428 (20.6%) | **142 (6.8%)** |
| platinum(12)| 14 | 2403 (85.4%) | 2001 (71.1%) | 1300 (46.2%) | 784 (27.9%) | **374 (13.3%)** |
| platinum(12)| 16 | 3208 (87.9%) | 2741 (75.1%) | 1909 (52.3%) | 1274 (34.9%) | **728 (20.0%)** |

Per-offset spread is tight (e.g. silver e16 r≥16ℓ ∈ [1102,1120]); full min–max is in the raw
console log. **`ℓ = 1.000`, `d_max` = 8 / 10 / 12 for silver / golden / platinum.**

## 4. Voronoi guard-ring losses (reported separately)

`guard-invalid` = Voronoi cell unbounded **OR** the neighbour's own `d_bound < 2ℓ`. The last two
columns quantify censoring of the **packing/void descriptor** on the `r=16` admitted centres.

| family | extent | unbounded cells | guard-invalid | r=16 centres: mean censored nbrs | r=16 centres touching a censored cell |
|---|---|---|---|---|---|
| silver(8)   | 12 | 3.4% | 15.4% | 4.6 | 33.0% |
| silver(8)   | 14 | 3.2% | 13.7% | 3.0 | 23.7% |
| silver(8)   | 16 | 2.8% | 12.7% | 2.3 | 18.6% |
| golden(10)  | 12 | 2.7% | 18.1% | 64.9 | **100.0%** |
| golden(10)  | 14 | 2.5% | 15.9% | 12.8 | 75.7% |
| golden(10)  | 16 | 2.3% | 14.4% | 6.5 | 46.6% |
| platinum(12)| 12 | 1.7% | 16.9% | 10.4 | 54.3% |
| platinum(12)| 14 | 1.9% | 14.6% | 5.2 | 35.8% |
| platinum(12)| 16 | 1.5% | 12.1% | 3.5 | 25.3% |

## 5. MSD time-window geometric feasibility (analytic LR bound, no dynamics)

| family | extent | admitted launch (d_bound≥8ℓ) | G_strip (min graph dist to strip) | LR t_hi | feasible (t_hi≥8)? |
|---|---|---|---|---|---|
| silver(8)   | 12/14/16 | 1139 / 1740 / 2464 | 8 / 8 / 8 | 0.226 / 0.224 / 0.221 | **0/6 every extent** |
| golden(10)  | 12/14/16 | 590 / 982 / 1469 | 7–8 | 0.171 / 0.158 / 0.156 | **0/6 every extent** |
| platinum(12)| 12/14/16 | 830 / 1300 / 1909 | 7 / 7–8 / 7 | 0.123 / 0.145 / 0.121 | **0/6 every extent** |

The analytic LR-admissible window is `t_hi ≈ 0.12–0.23` everywhere — roughly **35–65× short** of
even `t_lo = 2`, let alone the required `t_hi ≥ 8`. `G_strip ≈ 7–8` throughout (the strip is
close in graph distance even to depth-8ℓ launch sites), which is exactly why the series bound is
vacuous.

## 6. Patch-growth / saturation check

| family | n at extent 12 / 14 / 16 | monotone growth? |
|---|---|---|
| silver(8)    | 2500 / 3360 / 4341 | yes |
| golden(10)   | 1822 / 2452 / 3181 | yes |
| platinum(12) | 2083 / 2815 / 3650 | yes |

**No generator saturation at extents ≤ 16, platinum/12-fold included** — enlarging the extent
does grow every family's patch here. (Caveat: the historical saturation note in
`generate_rank4.py` concerns much larger extents, 22/26/30; if MSD feasibility later demands
substantially larger patches, saturation must be re-checked in that regime — it was not tested
here.)

---

## 7. Findings (factual; interpretation deferred to crew)

- **F1 — the `r=16` interior is the binding constraint, and golden is the worst case.** Golden at
  extent 12 has an essentially empty common set (**≈3 vertices**), unusable for the ladder;
  extent 14 is thin (83); extent 16 is marginal (280, 8.8%). Silver and platinum are far more
  forgiving (374–1117 at extents 14–16). Golden — the scientifically central family (the clean
  address-reader) — is precisely the one that most strains the `r=16` design.
- **F2 — the Voronoi guard-ring is genuinely necessary (confirms review catch A2).** Even away
  from the golden-e12 degenerate corner, 18–54% of `r=16` centres touch a censored Voronoi cell
  and carry a mean censored-neighbour load of 2–10; the packing/void descriptor at `r=16` is
  compromised without a guard-ringed super-patch, and the guard-ring further reduces usable data.
- **F3 — the MSD LR time-window is infeasible everywhere (confirms review catch B1).** The
  analytic bound leaves `t_hi ≈ 0.15 ≪ t_lo = 2` for every family/extent/offset (0/6 feasible).
  The MSD endpoint as specified cannot be justified by the geometry-only LR bound at these patch
  sizes. There is also a structural tension: raising `R_min` to enlarge `G_strip` would shrink the
  admitted launch set. The endpoint would need either a measured-boundary calibration (which
  requires the dynamical engine and therefore a sealed protocol) or a substantially larger
  substrate.
- **F4 — no patch saturation at extents ≤ 16** (all families grow monotonically), so "enlarge the
  extent" is a viable lever in this range; the platinum saturation concern does not bite here.

## 8. Feasibility flags for crew decision (NOT sealed here)

Offered as design input only, for the crew to accept, modify or reject:
- The radius ladder to `r=16` is viable for **silver and platinum at extents ≥ 14**, and for
  **golden only at extent 16 (marginally)**; golden at extent 12 should be excluded. The crew may
  wish to consider whether the golden ladder should **top out at `r=12`** (golden r≥12ℓ =
  172/426/790 — far healthier) rather than force `r=16`, or standardise on **extent 16** with a
  guard ring.
- The Voronoi guard-ring (super-patch generation + `d_bound ≥ 2ℓ` neighbour margin) should be
  treated as **required**, and its data loss (F2) budgeted into the power estimate.
- The MSD endpoint needs a **decision before sealing**: replace the LR window with a
  pre-registered measured-boundary calibration (run under seal), and/or move to larger patches
  (with saturation re-checked past extent 16). As specified, it is not geometrically feasible.

## 9. Scope / what this preflight did not do

No manifest was amended, nothing was sealed, the conditional-null packet was not started, and no
dynamics/address/target/score/outcome-curve was computed. Larger extents than 16 were not tested.

*Source attribution: geometry-only preflight run by the `gpt/workbench` Claude collaborator at
Work-GPT/Sol's authorisation, relayed by Katie. A feasibility record only; not part of the
scientific record, and resolving nothing, until reviewed by the crew.*

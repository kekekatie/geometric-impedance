# Geometry-only feasibility preflight — v2 extension (addendum)

**Date: 2026-08-29. Status: geometry-only feasibility record (extension). Nothing sealed, no
manifest amended, conditional-null packet not started, science branch untouched.** Authorised by
Work-GPT/Sol (2026-08-29) as a final geometry-only preflight extension before any manifest
amendment. Additive to the first report (`PREFLIGHT_GEOMETRY_REPORT.md`, commit `49d37be`),
which is left unchanged.

**No scientific outcome was accessed:** no Hamiltonian, eigen-decomposition, wave dynamics,
LDOS, MSD propagation, perpendicular-space address, regression, targets, family-result curves or
scores. Only geometry, admission masks, Voronoi tessellation, graph distances and an analytic
Lieb–Robinson series bound. Code: `gpt_workbench/preflight_geometry_v2.py` (new; does not
overwrite the v1 script or report). Raw per-offset console logs retained in the run output.

**Frozen config:** families {8,10,12}; extents {18,20,22}; the **same six fresh offsets** as v1
`(0.13,0.37)(0.29,0.11)(0.41,0.23)(0.05,0.47)(0.19,0.31)(0.37,0.09)`; strip `w=2ℓ`; MSD launch
depths {8,12,16,20}ℓ; `t_lo=2`, LR `ε'=5e-3`, required `t_hi≥8`; Voronoi pad `Δ=6` (see §1 note).
`ℓ=1.000` all families.

---

## 1. Larger geometries + generator-saturation check (task 1)

All three families grow **monotonically** across core extents 18→20→22 — **no generator
saturation**; the stop-rather-than-extrapolate rule was never triggered.

| family | n @ e18 / e20 / e22 | monotone? |
|---|---|---|
| silver(8)    | 5463 / 6719 / 8100 | yes |
| golden(10)   | 3999 / 4913 / 5920 | yes |
| platinum(12) | 4604 / 5660 / 6806 | yes |

*Documented deviation:* the **extent-28 padded** super-patch for platinum core-extent 22 was
prohibitively slow to generate (slow, **not** saturated — the core series above is healthy), so
that one cell's Voronoi pad used `Δ=4` (extent 26) instead of 6. Ring width stayed 10.1ℓ (≥3ℓ),
so the correction is unaffected. Baked into the script as `PAD_DELTA_OVERRIDE={(12,22):4}` for
reproducibility.

## 2. Physical-size comparability — equal extent ≠ equal physical size (task 2)

Per-offset spread is negligible (<1%); means shown. **Golden has the largest diameter yet the
smallest area, fewest vertices, and smallest usable r=16 interior at every extent** — it is the
least dense / most elongated family, so equal generator-extent understates how much substrate
golden needs.

| family | extent | n | hull area | diameter | usable r=16 area |
|---|---|---|---|---|---|
| silver(8)    | 18 | 5463 | 4478 | 78.8 | 1370 |
| silver(8)    | 20 | 6719 | 5522 | 87.4 | 1976 |
| silver(8)    | 22 | 8100 | 6667 | 96.1 | 2690 |
| golden(10)   | 18 | 3999 | 3272 | 95.9 | 452 |
| golden(10)   | 20 | 4913 | 4032 | 106.5 | 794 |
| golden(10)   | 22 | 5920 | 4840 | 116.7 | 1210 |
| platinum(12) | 18 | 4604 | 3726 | 88.6 | 921 |
| platinum(12) | 20 | 5660 | 4554 | 99.9 | 1345 |
| platinum(12) | 22 | 6806 | 5489 | 108.3 | 1879 |

## 3. Radius-16 feasibility — full per-offset survivors (task 3)

Common-set logic retained; **adequacy is NOT declared here** (crew decision). Per-offset spread
is tight.

| family | extent | r≥16ℓ per offset (count) | proportion | mean / min / max |
|---|---|---|---|---|
| silver(8)    | 18 | 1698,1718,1698,1723,1723,1723 | ~31% | 1714 / 1698 / 1723 |
| silver(8)    | 20 | 2459,2459,2452,2452,2459,2459 | ~36.5% | 2457 / 2452 / 2459 |
| silver(8)    | 22 | 3354,3303,3333,3333,3323,3333 | ~41% | 3330 / 3303 / 3354 |
| golden(10)   | 18 | 581,597,600,590,585,596 | ~14.7% | 592 / 581 / 600 |
| golden(10)   | 20 | 1025,1013,1012,1020,1024,1027 | ~20.8% | 1020 / 1012 / 1027 |
| golden(10)   | 22 | 1535,1545,1559,1537,1547,1539 | ~26% | 1544 / 1535 / 1559 |
| platinum(12) | 18 | 1170,1168,1171,1165,1167,1170 | ~25.4% | 1168 / 1165 / 1171 |
| platinum(12) | 20 | 1719,1719,1704,1716,1704,1718 | ~30.3% | 1713 / 1704 / 1719 |
| platinum(12) | 22 | 2387,2367,2373,2380,2361,2389 | ~35% | 2376 / 2361 / 2389 |

## 4. Spatial-block feasibility (task 4)

**The prereg/manifest spatial-block CV scheme is NOT fully specified** — it names "quadrants/
rings" but does not fix: number of blocks, angular origin, equal-angle vs equal-count,
contiguity, whether on the full patch or the r=16 interior set, or the fold-assignment rule. Per
instruction, I did **not** invent-and-optimise one. Below is a **clearly-labelled deterministic
PROPOSAL for crew review only**: 4 equal-angle angular quadrants about the centroid of the r≥16ℓ
common set, each quadrant one held-out fold.

Geometry-only admitted vertices per quadrant/fold (mean over offsets; min fold across offsets):

| family | extent | per-quadrant folds | min fold | balanced? |
|---|---|---|---|---|
| silver(8)    | 22 | [834,825,825,846] | 801 | yes |
| golden(10)   | 22 | [577,198,576,193] | 190 | **no — ~3× imbalance** |
| platinum(12) | 22 | [659,523,663,531] | 510 | mild |

**Finding (design caveat, not a decision):** golden's r=16 interior is **anisotropic/elongated**
(consistent with its large diameter / small area, §2), so equal-**angle** quadrants give strongly
unequal folds for golden. If a spatial-block CV is sealed, it should use **equal-count** blocks
(or ring-based blocks) rather than equal-angle, or golden's folds will be badly imbalanced. This
is flagged for the crew; the equal-angle proposal above is illustrative, not recommended as-is.

## 5. Corrected Voronoi on a padded super-patch (task 5)

**Clarifying the v1 "censored neighbours" figure (and the golden e12 = 64.9).** In v1,
"censored-neighbour load" counted **every vertex within a Euclidean 16ℓ ball of an r=16 centre
that had an invalid cell** — i.e. *ball members*, **not immediate graph neighbours**. The golden
extent-12 mean of 64.9 arose because that whole patch's radius was ≲16ℓ, so the 16ℓ ball around
its ~3 deep-core centres covered almost the entire tiny patch (hundreds of vertices), most of
them near the boundary and hence invalid. It was an artifact of the ball nearly covering a small
patch — **not** a real per-neighbour censoring rate, and not immediate graph neighbours.

**Corrected padded calculation.** Recomputing Voronoi on a padded super-patch (core + Δ, ring
10–16ℓ ≥ the 3ℓ requirement in every case) and restricting to core vertices:

| family | extent | core-only invalid cells | recovered by padding | **REMAIN invalid** |
|---|---|---|---|---|
| silver(8)    | 18/20/22 | 150 / 148 / 162 | 150 / 148 / 162 | **0 / 0 / 0** |
| golden(10)   | 18/20/22 | 79 / 74 / 92 | 79 / 74 / 92 | **0 / 0 / 0** |
| platinum(12) | 18/20/22 | 57 / 66 / 62 | 57 / 66 / 62 | **0 / 0 / 0** |

**Every** invalid core cell is recovered by padding; **zero remain invalid** on all patches. So
the true data loss for the packing/void descriptor **with a proper guard-ringed super-patch is
zero** — the v1 "18–54% contamination" figures are **not** final data loss and should not be
treated as such. The guard-ring (generate a larger super-patch, compute Voronoi there, analyse
the core) fully resolves the censoring.

## 6. MSD geometry — depth sweep, analytic only (task 6)

Analytic LR window recomputed **separately per launch depth** (no propagation). `t_hi` = largest
`t` with `N_strip·B(t;G_strip)² ≤ ε'`.

| family | extent | depth 8: adm / G / t_hi | depth 12 | depth 16 | depth 20 |
|---|---|---|---|---|---|
| silver(8)    | 18 | 3327 / 8 / 0.220 | 2473 / 13 / 0.441 | 1714 / 18 / 0.669 | 1097 / 23 / 0.899 |
| silver(8)    | 20 | 4322 / 8 / 0.219 | 3359 / 13 / 0.440 | 2457 / 18 / 0.668 | 1700 / 23 / 0.898 |
| silver(8)    | 22 | 5442 / 8 / 0.218 | 4373 / 13 / 0.439 | 3330 / 18 / 0.667 | 2432 / 23 / 0.897 |
| golden(10)   | 18 | 2056 / 7–8 / 0.156 | 1252 / 12–13 / 0.344 | 592 / 17–18 / 0.514 | 163 / 23 / 0.723 |
| golden(10)   | 20 | 2744 / 7–8 / 0.155 | 1816 / 12–13 / 0.331 | 1020 / 17–18 / 0.513 | 418 / 22–23 / 0.697 |
| golden(10)   | 22 | 3511 / 7–8 / 0.148 | 2459 / 12–13 / 0.341 | 1544 / 17–18 / 0.517 | 783 / 22–23 / 0.695 |
| platinum(12) | 18 | 2599 / 7–8 / 0.139 | 1850 / 12 / 0.266 | 1168 / 17 / 0.417 | 686 / 22 / 0.571 |
| platinum(12) | 20 | 3367 / 8 / 0.147 | 2504 / 12 / 0.264 | 1713 / 17 / 0.416 | 1114 / 22 / 0.569 |
| platinum(12) | 22 | 4299 / 7–8 / 0.123 | 3294 / 12 / 0.264 | 2376 / 17–18 / 0.420 | 1658 / 22 / 0.568 |

*(admitted launches / min graph-distance-to-strip G_strip / LR `t_hi`; feasible = `t_hi≥8`, which
is **0/6 in every single row**.)*

**Two structural findings (Sol's observation confirmed and extended):**
- **Enlarging the patch does not rescue the worst case while depth-8 launches remain admitted.**
  At fixed depth 8, `t_hi` is essentially invariant across extents (silver 0.220→0.219→0.218;
  platinum 0.139/0.147/0.123). The worst-case is set by the shallowest admitted launch, whose
  graph distance to the strip (`G_strip≈7–8`) does not grow with the patch. Exactly Sol's point.
- **Raising the launch depth helps monotonically but nowhere near enough.** `t_hi` rises roughly
  linearly with depth (≈0.055/ℓ on silver): depth 8→20 gives `t_hi` ≈ 0.22→0.90 (silver),
  0.14→0.57 (platinum) — still **~9–14× short** of the required 8, while admitted counts fall
  (golden depth-20/e18 = 163). Linear extrapolation implies a launch depth of **~145ℓ** would be
  needed to reach `t_hi=8` — far beyond the deepest interior any feasible patch offers (silver
  e22 max depth ≈ diameter/2 ≈ 48ℓ). **The analytic LR window is unreachable at any realistic
  patch size and any launch depth.**

---

## 7. Summary of findings (factual; interpretation/decision deferred to crew)

- **F1 — no generator saturation** at core extents ≤22 for any family; growth is monotone. (The
  extent-28 *padded* patch was merely slow; documented deviation, conclusion unaffected.)
- **F2 — equal extent ≠ equal physical size**; golden is the least-dense/most-elongated family
  and has the smallest usable r=16 interior at every extent. Family comparisons must be matched on
  physical size / usable interior, not generator extent.
- **F3 — radius-16 is now workable at larger extents** (golden reaches ~1544 at e22 vs ~3 at e12
  in v1); full per-offset counts provided; **adequacy not declared**.
- **F4 — the spatial-block CV scheme is under-specified**; a deterministic proposal is offered for
  crew review, and it surfaces that **equal-angle quadrants are badly imbalanced for golden** —
  equal-count (or ring) blocks are the safer construction.
- **F5 — the v1 Voronoi "contamination" was an artifact**; the "64.9" counted ball-members of a
  tiny patch, not graph neighbours. With a proper guard-ringed super-patch, **zero** cells remain
  invalid — the packing/void descriptor loss is nil once padding is used.
- **F6 — the analytic LR MSD window is infeasible at every family/extent/depth** and, decisively,
  **cannot be rescued by larger patches (fixed-depth `t_hi` is extent-invariant) nor by deeper
  launches (would need ~145ℓ depth)**. An analytic-geometry justification of the MSD window is
  not available on realistic substrates; a measured-boundary calibration (requires the dynamical
  engine → sealed protocol) or a spectrum-based bound (requires eigen-decomposition) would be
  needed. This is input to the crew's decision, not a decision.

## 8. Scope / confirmation

No manifest amended, nothing sealed, conditional-null packet not started, no dynamics/address/
target/score/outcome-curve accessed, science branch untouched. Extents >22 not tested. Stops here
for crew review.

*Source attribution: geometry-only preflight extension run by the `gpt/workbench` Claude
collaborator at Work-GPT/Sol's authorisation, relayed by Katie. A feasibility record only; not
part of the scientific record, and resolving nothing, until reviewed by the crew.*

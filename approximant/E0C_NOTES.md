# Seamless phason-shear approximant — E0c validation notes

The object that unblocks three threads (winding Stage D control, memory §7 surgical
leg, AI-memory §2.1 control). Construction: ideal parallel positions + phason shear
applied to the **acceptance only** (`π⊥'(K)=π⊥(K)−A·π∥(K)`, `A` sends the period
sublattice to zero in sheared-perp). Result: periodic, unit-edge, seamless by
construction. See `phason_shear.py`; validation `e0c_validate.py`;
numbers `e0c_results.json`.

## Ammann–Beenker — VALIDATED (orders 2, 3)

| order | conv | connected | seam (edge residual) | periodicity | degree TVD vs ideal | heals |
|---|---|---|---|---|---|---|
| 1 | 1/1 | no | 2e-15 | 100% | 0.243 | yes |
| **2** | **3/2** | **yes** | **2e-15** | **100%** | **0.051** | **yes** |
| **3** | **7/5** | **yes** | **2e-15** | **100%** | **0.065** | **yes** |
| 4 | 17/12 | yes | 2e-15 | (unverified*) | 0.037 | yes |

- Orders **3/2 and 7/5 are clean E0c passes** — a genuinely seamless, periodic,
  degree-matched, unit-edge approximant. This validates the construction and
  unblocks the AB surgical leg and the AB Stage-D / §2.1 controls.
- Order 1/1 is the crudest convergent (disconnected, poor degree match) — expected;
  not usable.
- \*Order 4 periodicity is **unverified at this patch size**: its physical period
  (|P_a| ≈ 17+12√2 ≈ 34) exceeds the patch radius (14), so less than one unit cell
  fits and the position-based periodicity check has no in-patch image to match.
  Degree still matches (TVD 0.037). Verifying high-order periodicity needs a patch
  larger than the period — an execution detail, not a construction fault.
- Healing (theorem-echo): contractible loops carry ~1e-16 holonomy on every AB
  order — ideal positions heal exactly, as Theorem 1 requires. The pipeline does
  not leak.

## Penrose — NOT YET VALIDATED (degree-match caveat, per sealed B5)

Connected, seamless (edge residual ~5e-15), heals (~1e-16) at every order — but the
degree histogram is only a **marginal** match to the ideal, TVD 0.087–0.162, with a
**systematic deficit of degree-5 vertices** (approximant ~30 vs ideal 48; ideal
`{3:83,4:91,5:48,6:3,7:1,8:3,10:2}`). Per the sealed rule (winding
`SEALED_PREREGISTRATION.md` §B5: "if bulk histograms differ materially, the control
is invalid and the design must be revisited"), **Penrose is not yet a usable
matched-degree control.**

Candidate causes to run down (next step, before any Penrose Stage-D result):
1. The per-residue-class window + `(1,1,1,1,1)`-gauge dedup interacting with the
   shear may mis-accept near the degree-5 window regions.
2. The multigrid "ideal" reference degree histogram may itself be imperfect
   (geometry.py occasionally yields spurious degree-9/10 vertices) — the TVD
   compares two imperfect distributions; part of the gap may be reference noise.
3. Small interior sample (~230 vtx at r<7.7) inflates TVD; larger Penrose patches
   would sharpen the comparison.

Honest status: the **construction is proven on AB**; **Penrose needs the degree-5
deficit resolved** before it earns control status. Not massaged, not hidden.

## What is unblocked now vs next

- **Unblocked now:** the **AB surgical leg** — cut a dislocation dipole into the
  validated 3/2 (or 7/5) approximant and test whether it carries the registered
  quantum π⊥(M_a) = 0.1716 (0.5σ-live against strangeness T1, and the memory §7
  Outcome-A robustness test). AB Stage-D control and AB §2.1 control likewise.
- **Next:** resolve the Penrose degree-5 deficit; verify high-order periodicity on
  patches larger than the period.

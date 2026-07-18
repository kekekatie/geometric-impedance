# Stage-1C uniform-defect control — construction seal (predeclared BEFORE transport)

**Status: SEALED before any Stage-1C transport.** Additive follow-up (GPT review of
Stage-1B). Stage-1 and Stage-1B results are FROZEN and unchanged. Same sealed
dynamics, κ=10. Purpose: a crystalline control whose defect field is genuinely
**uniform / hyperuniform-like** — matched to each native's spatial defect statistics,
not a nearest-node label stamp — to separate *defect spacing* from *quasicrystalline
weave*.

## Language discipline (GPT)
Finite graphs over a small range of scales cannot establish strict mathematical
hyperuniformity. We say **"hyperuniform-like"**, **"strongly uniform"**, or
**"suppressed number fluctuations"** unless a low-k structure-factor / asymptotic
number-variance criterion is actually demonstrated. Not claimed here.

## Defect field definition (consistent with Stage-1B)
Defect sites = grid nodes forced off degree 4 (the quadrangulation baseline). Trap
sites = degree ≤ 3 (the transport-relevant, trapping subset). Diagnostics computed on
the **trap** field (matching Stage-1B), plus total defect count and degree histogram.

## Construction (predeclared)
1. **Site placement — repulsive / blue-noise (Poisson-disk).** Place M defect sites on
   grid nodes by dart-throwing with a torus min-separation r; binary-search r so the
   count ≈ M_QC (QC's degree≠4 count). Blue noise gives suppressed number fluctuations
   by construction (unlike random/Poisson placement).
2. **Degree assignment.** Each defect site gets a degree sampled (shuffled) from the
   QC's degree≠4 histogram, so the control's degree histogram matches the QC. Non-site
   nodes stay degree 4.
3. **Realisation.** Local short edge edits (existing `matched_control` machinery,
   explicit `target_degrees`) realise the target degrees while preserving
   connectivity, no self/dup edges, winding validity, and no multi-cell edges; edge
   count pinned to the native mean.
4. **Ensemble.** ≥10 independent realisations per substrate/size (many arrangements can
   satisfy the same coarse statistics).

## Number-variance scales (predeclared)
Window radii R = s·√(cell area) for **s ∈ {0.15, 0.20, 0.25}**; ratio σ²(N_R)/⟨N_R⟩
(1 = Poisson, <1 = suppressed). The **s=0.20** scale is the gated one; all reported.

## SPATIAL-MATCH GATE (must pass BEFORE transport; predeclared tolerances)
Per substrate/size, on the ensemble mean vs the QC target:
- **T1 defect count:** |M_ctrl − M_QC| / M_QC ≤ 0.05
- **T2 degree histogram:** total-variation(ctrl, QC) ≤ 0.05
- **T3 trap number-variance (s=0.20):** |ν_ctrl − ν_QC| ≤ 0.12 **and** ν_ctrl ≤ 0.30
  (i.e. genuinely suppressed and close to QC — the crux the stamp failed for Penrose)
- **T4 trap nearest-neighbour spacing (mean):** |nn_ctrl − nn_QC| / nn_QC ≤ 0.15
- **Reported, not gated:** pair-correlation over distance bins; void-size (largest
  empty-window) proxy; number variance at s ∈ {0.15, 0.25}.

**Rule:** if **T1–T4 all pass**, run the sealed transport (κ=10) on the ensemble and
return graph-ensemble + walker uncertainty. **If any of T1–T4 fails, STOP** for that
substrate/size: report the spatial mismatch and run **no** transport there (do not
interpret transport from a control that did not instantiate the target field).

## Outcome interpretations (predeclared)
For sizes that pass the gate:
- **uniform control ≈ QC** → the Stage-1 QC>random gap is primarily **defect spacing /
  suppressed fluctuations**.
- **uniform control remains below QC** → **broader quasicrystalline connectivity /
  motif correlations** contribute beyond defect placement.
- **uniform control between random and QC** → **both** spacing and weave contribute.

*Sealed. Records below.*

---

# Records — the gate FAILED at every size; per the seal, NO transport was run

10 realisations/size, blue-noise (Poisson-disk) trap placement + degree-histogram
degrees + local-edit realisation. Number variance at s=0.20 (1=Poisson, <1=suppressed):

| substrate | N | QC numvar | control numvar | QC nn | control nn | defcount QC/ctrl | histTV | GATE |
|-----------|---|-----------|----------------|-------|------------|------------------|--------|------|
| AB | 42 | 0.598 | 0.532 | 0.77 | 1.24 | 28 / 17 | 0.253 | FAIL |
| AB | 225 | 0.156 | 0.564 | 0.82 | 1.03 | 155 / 140 | 0.086 | FAIL |
| AB | 1369 | 0.144 | 0.482 | 0.79 | 1.38 | 914 / 478 | 0.319 | FAIL |
| Pen | 240 | 0.130 | 0.434 | 0.74 | 0.96 | 207 / 203 | 0.028 | FAIL |
| Pen | 658 | 0.089 | 0.432 | 0.76 | 0.95 | 589 / 571 | 0.043 | FAIL |
| Pen | 1694 | 0.085 | 0.416 | 0.76 | 0.96 | 1527 / 1499 | 0.025 | FAIL |

For Penrose the count and histogram matched well (T1, T2 pass), but **T3 (number
variance) failed everywhere** and by a wide margin: the control's trap field is
~0.42–0.56 (blue-noise: suppressed vs Poisson=1, but not close), while the QC is
~0.08–0.16. **The QC defect field is far more uniform than blue noise achieves.**

## The informative failure (the key insight)
The QC defect field has a **quasicrystal-specific spatial signature that a grid point
process cannot reproduce**:
- **small nearest-neighbour spacing** (QC nn ≈ 0.76 < control ≈ 0.96–1.38), i.e. some
  close trap pairs / locally variable spacing; **yet**
- **strongly suppressed large-scale number fluctuations** (QC numvar ≈ 0.08–0.16,
  falling with size — hyperuniform-like), far below blue noise.

Generic point processes cannot hit **both** at once: Poisson → high numvar; blue-noise
/ jittered-lattice → large *uniform* nn with only moderate (or, if pushed to a lattice,
very low) numvar — but then *large* nn, not the QC's small nn. The combination
*small-nn + low-numvar* is characteristic of **quasiperiodic order** itself. So a
crystalline control that matches the QC's full defect spatial statistics may be
**fundamentally hard to construct** — which is itself a result about how special the
QC's defect organisation is.

## Consequence for the discrimination (honest)
- Per the seal, **transport was NOT run** (gate failed) — no over-interpretation.
- The clean "spacing vs weave" separation is **harder than anticipated**: the QC's
  defect *spacing statistics are themselves quasicrystalline* and not reproducible by
  blue-noise on a grid. A matched control would need a construction whose defect field
  attains small-nn + low-numvar simultaneously — plausibly only a quasiperiodic
  arrangement does — which blurs the line between "matched-spacing control" and "a
  second quasicrystal."
- **Options for the three-way review:** (a) accept that the QC defect field's spatial
  signature is quasicrystal-specific and report Stage-1B's leaning result with this
  boundary stated; (b) attempt a harder construction (e.g. a *different* quasiperiodic
  tiling's defect pattern stamped on the grid, or a tuned pair-correlation-matched
  process) as Stage-1D; (c) reframe the question from "spacing vs weave" to
  "the QC defect field is a distinctive, hard-to-mimic hyperuniform-like point
  pattern," which is a finding in its own right.

*Gate details in `results/stage1c.json`. Stage-1 and Stage-1B unchanged and frozen.*

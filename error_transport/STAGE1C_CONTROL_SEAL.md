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

*Sealed. Records (achieved spatial stats, gate pass/fail, and — only if passed —
transport ensemble) appended by `stage1c.py`.*

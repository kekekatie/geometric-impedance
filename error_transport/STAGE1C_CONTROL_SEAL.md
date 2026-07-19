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

## The informative failure (tempered per GPT review)
**The tested blue-noise controls failed to match the quasicrystalline approximants'
distinctive multiscale defect-field statistics.** Specifically the QC trap field
combines:
- **small nearest-neighbour spacing** (QC nn ≈ 0.76 < control ≈ 0.96–1.38), i.e. some
  close trap pairs / locally variable spacing; **with**
- **strongly suppressed finite-scale number fluctuations** (QC numvar ≈ 0.08–0.16,
  falling with size — hyperuniform-like), far below the blue-noise controls (~0.42–0.56).

The blue-noise / Poisson-disk family we tested could not reproduce **both** at once
(it gives large, uniform nn with only moderate number-variance suppression). **This
does NOT prove that no generic correlated process could match it, nor that only
quasiperiodicity produces this combination** — only that *this* construction failed
its gate. Whether another correlated point process can hit the QC's multiscale
statistics is an open, named future question, not a claim of this paper. We use
"hyperuniform-like" / "strongly suppressed finite-scale number fluctuations," never
strict or uniquely-quasicrystalline hyperuniformity.

## Consequence for the discrimination (honest)
- Per the seal, **transport was NOT run** (gate failed) — no over-interpretation.
- The clean "spacing vs weave" separation was **not achieved** by this construction:
  the tested blue-noise controls did not instantiate the QC's multiscale defect-field
  statistics, so they cannot discriminate. Exact causal separation of defect spacing
  from the wider weave is a **named future experiment**, not a prerequisite for
  Paper 1.
- **Decision (GPT, adopted): stop control escalation for Paper 1.** No further new
  controls. The paper is framed around what is already supported (see
  `paper/CLAIMS_MAP.md`), with the causal separation listed as future work.

*Gate details in `results/stage1c.json`. Stage-1 and Stage-1B unchanged and frozen.*

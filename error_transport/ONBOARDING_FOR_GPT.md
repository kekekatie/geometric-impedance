# Onboarding brief — Paper 1 (error-transport), for a fresh collaborator

*One-page catch-up: the question, what we tried, what we shed, what we found, and the
exact files for the leading edge. Everything below is FROZEN unless it says "future".*

## The question (Paper 1)
A narrow **classical** proxy (not a quantum-code claim). On a finite 2-D torus, start a
pair of defects on **adjacent** sites and let them diffuse **unbiasedly**. Each run ends
as **HEAL** (they annihilate with net homology `c = 0`), **LOGICAL** (annihilate with
`c ≠ 0` — a non-contractible winding), or **CENSORED** (budget `S_max = κ·N` reached).
Core question: **does the wiring geometry — faithful quasicrystal vs crystal —
change the heal-vs-logical-vs-censored distribution?**

Method discipline: three-way review (Claude builds/validates, GPT reviews, Katie
adjudicates) with **pre-registration**: design seal → construction-only → runtime-only
κ-pilot → κ-seal → inference. No tuning after outcomes are visible.

## Foundations it rests on (prior work, already solid)
- **Faithful Penrose**: the de Bruijn offset-sum Σγ had been 0.5 (a *generalised*
  Penrose, coordination up to 10). Pinned to ∈ ℤ → true Penrose, coordination ≤ 7.
- **The class-preserving ×5 cell**: Penrose's true period cell is 5× the naive one
  (naive period vectors shift residue class). This ×5 is the four-class "this/that"
  structure made physical — and it is required to wrap a faithful Penrose torus.

## What we TRIED and SHED (the journey's dead ends — all informative)
1. **Naive "wrap-a-cell" torus** → a real **frozen phason wall**: ~2.3% of Penrose
   seam edges do not close. **Shed** (cannot pass an edge-completeness gate).
2. **Rational-cut approximant** (to get a *defect-free* substrate) → **not faithful for
   Penrose** at accessible orders (the (1,1,1,1,1) kernel readmits over-coordination).
   **Shed as a substrate; kept as a bracketing result + future work.**
3. **Overclaim "QC differs from both controls"** → the table actually shows QC ≈ clean
   grid. **Corrected** to `QC ≈ clean grid > random-defect grid`.
4. **Hyperuniform *stamp* control** (Stage-1B) → imperfect; inconclusive. Superseded.
5. **Blue-noise uniform control** (Stage-1C) → **failed its pre-declared spatial-match
   gate** (could not reproduce the QC's defect-field statistics), so per seal **no
   transport was run**. **Shed further control escalation for Paper 1.**
6. **Overclaim "only quasiperiodicity can produce that defect field"** → **tempered** to
   "the *tested* blue-noise controls failed to match it."

## What we FOUND and KEPT (the substance)
**Construction (validated, frozen):**
- **Seamless phason-shear torus** passes the §7.1 combinatorial gate for both
  substrates/all orders (zero dropped edges, reverse-winding antisymmetry, unit-star
  edges, connectivity, fundamental-cycle winding closure, Penrose coord 7).
- It carries an **intrinsic, distributed ~1–5% phason-defect burden** (merged faces) —
  a substrate property (also in the e0c open approximant), *not* a wall.
- Controls: **oblique-Z² clean grid** (mean degree exactly 4); **defect-matched grid**
  (same N/mean-degree/degree-histogram, defects placed at random); **bounded-rewire**
  (secondary; ~70% replacement saturation under the specified double-swap procedure).
- **κ-seal = 10** from an outcome-blind pilot (smallest ladder value with worst-case
  censoring ≤ 5%).

**Results (frozen; Stage-1 + Stage-1B):**
1. **Generic winding dominates.** P_logical is large (0.23–0.44) and falls with N; best
   of three *descriptive* fits is `a/logN + b` (2-D winding-angle statistics). All
   substrates behave similarly at leading order.
2. **QC ≈ clean crystalline grid.** Aperiodicity per se does not markedly change the
   winding rate (AB within CIs; Penrose marginally below).
3. **QC > randomly defect-matched grid** — CI-separated at every substrate/size, and
   **robust to a 10-graph ensemble** (graph-to-graph σ ≪ the gap). Random weak disorder
   *suppresses* winding (trapping).
4. **The defect fields are organised differently.** QC trap field shows **strongly
   suppressed finite-scale number fluctuations** (number-variance ratio 0.08–0.18,
   hyperuniform-like) vs random-matched clumpy (0.40–0.77 ≈ Poisson).
5. **Core claim:** equal defect *count + mean degree + degree histogram* do **not**
   determine transport — the **spatial organisation** of the defects does.

**Open boundary (named future work, NOT a Paper-1 prerequisite):**
- Isolating *defect spacing* from the *wider quasiperiodic weave* — the blue-noise
  control could not instantiate the QC's multiscale defect statistics, so this is
  deferred to a future correlated/point-process-matched experiment.

## The leading edge = the paper (single object)
Framed around what is supported (above), **not** "Penrose is better". Spine:
> The *absolute* local→global winding rate is generic 2-D physics; the *residual* that
> geometry controls is set by the **spatial organisation of an equal defect burden, not
> its amount** — random clumping traps; the QC's suppressed-fluctuation field does not.

## Files to read, in priority order (leading edge first)
1. **`paper/CLAIMS_MAP.md`** — the results→claims ledger (established / suggestive /
   future) with per-claim wording guards. **Read this first to calibrate what we may
   say.**
2. **`paper/MANUSCRIPT.md`** — title, abstract, section skeleton, methods, figure/table
   markers.
3. **`paper/FIGURES_TABLES.md`** — the minimal 5-figure / 4-table plan.
4. **`STAGE1_RESULTS.md`** — main inference reading (frozen).
5. **`STAGE1B_DISCRIMINATION.md`** — ensemble + spatial-organisation diagnostics.
6. **`STAGE1C_CONTROL_SEAL.md`** — the gate-failure + tempered boundary.
7. **`VALIDATION_NOTES.md`** — construction findings (phason wall → seamless torus →
   phason defects; controls; rational-cut).
8. **`SEALED_PREREGISTRATION.md`** + **`PILOT_SEAL.md`** — the frozen design + κ-seal.
9. **`results/*.json`** — machine-readable frozen numbers (inference_stage1,
   discrimination, stage1c, *_validation).

## The four-paper staircase (context)
1. **This paper** (local→global defect transport; disorder organisation). ← we are here
2. Broader generic-geometry comparison (which effects are aperiodic vs graph-statistical).
3. AI-memory paper (clumped vs even vs channelled silent corruption — borrows this
   heal/logical/censored taxonomy; does not need E8).
4. E8-specific adversarial benchmark.

*Immediate next step for the paper: pick the title, tighten the abstract, generate the
5 figures from the frozen JSON. No new experiments required.*

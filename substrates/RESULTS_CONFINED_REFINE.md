# Results — refining the confined-address picture (finer control + selection-rule test)

*EXPLORATORY. Code: `confined_refine.py`. Three checks GPT asked for before trusting the
within-motif picture (`RESULTS_CONFINED.md`): (1) does the address effect survive a FINER
local control? (2) mark ill-conditioned classes inconclusive; (3) does the preferred depth
sit at the same NORMALIZED perp-space depth across classes/families (a selection rule), and is
it stable across offsets? Extent 12, 4 offsets, held-out-offset CV, |E|<0.1 confined window.*

## 1. The address effect survives finer local control — strongly

The main worry: coarse vertex classes lump together finer local configurations, so maybe
"address" is just residual finer local structure. Test: add the FINE (star/sign) vertex type
as a nuisance control inside each coarse class and re-measure the address effect.

It is essentially **unchanged** in every class:

| family | class | addr effect over physical | addr effect over physical + **fine type** |
|---|---|---|---|
| golden   | #3  | +0.094 | +0.093 |
| golden   | #15 | +0.116 | +0.118 |
| silver   | #5  | +0.261 | +0.269 |
| silver   | #2  | +0.193 | +0.197 |
| platinum | #5  | +0.215 | +0.217 |
| platinum | #3  | +0.127 | +0.127 |

Controlling for the *exact fine local configuration* removes none of it. So the effect is
**not** finer local structure — perpendicular-space placement predicts confined-state weight
beyond both the coarse *and* the fine local vertex type. This is the key rigor win: the
signal is genuinely about global quasiperiodic placement.

## 2. Honest conditioning and heterogeneity

Ill-conditioned classes (held-out physical R² < 0.2: platinum #6, #11) are marked
**inconclusive**, not "noise". Among well-conditioned classes the effect is **positive in
most, but not all**: one clean class (golden #1, physical R² 0.69) shows a *negative* address
effect (−0.075). So the within-motif address effect is real and often large, but genuinely
heterogeneous across vertex types — not a universal law over every class.

## 3. Preferred depth: reproducible, but class-specific — NOT one universal band

My earlier "resonant peak at ~0.35" was for a single class and over-read. The refinement:

- **Per-offset stability is excellent** — each class's preferred (peak) confined-depth
  repeats across the 4 held-out offsets to ±0.00–0.06 (normalized). So each vertex type does
  have a well-defined, reproducible preferred perpendicular-space depth. Real, not an artefact.
- **But the preferred depth is class-specific, not universal.** Across well-conditioned
  classes the peak normalized depth ranges ~0.19 → 0.72 (cross-class sd ≈ 0.19 on a 0–1 scale).
  There is **no single shared internal-space band** — GPT's selection-rule hypothesis in its
  strong form is *not* supported. Different vertex types prefer *different* internal-space
  depths (with a hint of low ~0.2 and high ~0.6–0.7 groupings, not over-claimed here).

So the honest statement replaces "a resonance at a universal depth" with: **each vertex type
has its own reproducible preferred perpendicular-space depth for confined-state weight.** That
is consistent with the global-standing-mode picture — locally different configurations couple
to the global quasiperiodic organization at their own characteristic internal-space location —
and it is a more specific, more testable claim than a single band.

## Net (what to carry into the synthesis)

- **Strengthened:** within a fixed local vertex type — coarse *and* fine — perpendicular-space
  placement predicts confined-state participation, beyond long-range physical structure. Local
  physical identity does not fix spectral role; global quasiperiodic placement does.
- **Deflated (correctly):** no single universal internal-space band; the preferred depth is
  class-specific (though offset-stable). "Resonance" was the wrong word; "reproducible,
  class-specific preferred depth" is right.
- **Open:** whether the class-specific preferred depths follow a rule (e.g., group structure,
  or a relation to the vertex type's own window geometry) — a future question, not claimed now.

## Files

`confined_refine.py` · builds on `confined_address.py`, `RESULTS_CONFINED.md`,
`RESULTS_COHERENCE.md`.

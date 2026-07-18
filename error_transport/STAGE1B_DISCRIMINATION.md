# Stage-1b discrimination test (labelled follow-up; Stage-1 FROZEN)

Answers GPT's review of Stage-1 (QC ≈ clean grid > random-defect grid). Same sealed
dynamics, κ=10. 8000 walkers/graph; matched-defect ensembles. Seed `27182818`
(distinct from pilot + Stage-1). Numbers: `results/discrimination.json`.
**Nothing here retunes Stage-1.**

## P_logical — QC vs clean vs random-matched (10-graph ensemble) vs hyperuniform-stamped (4-graph)
| substrate | N | QC | clean | random-matched (mean±graph-σ) | hyperuniform-stamped (mean±σ) |
|-----------|---|----|-------|-------------------------------|-------------------------------|
| AB | 41 | 0.4225 | 0.420 | 0.400 ± 0.017 | 0.411 ± 0.017 |
| AB | 220 | 0.3308 | 0.332 | 0.302 ± 0.006 | 0.305 ± 0.009 |
| AB | 1355 | 0.2745 | 0.2545 | 0.254 ± 0.004 | 0.266 ± 0.003 |
| Pen | 247 | 0.3295 | 0.351 | 0.306 ± 0.011 | 0.305 ± 0.009 |
| Pen | 650 | 0.2995 | 0.304 | 0.269 ± 0.006 | 0.276 ± 0.008 |
| Pen | 1700 | 0.2589 | 0.278 | 0.235 ± 0.004 | 0.237 ± 0.005 |

## Trap-field spatial diagnostics (degree ≤ 3 nodes)
Number-variance ratio σ²/⟨N⟩ (1 = Poisson/random, <1 = even/hyperuniform):
| substrate | N | QC | random-matched | hyperuniform-stamped |
|-----------|---|----|-----------------|-----------------------|
| AB | 41 | 0.65 | 0.77 | 0.47 |
| AB | 220 | 0.18 | 0.40 | 0.37 |
| AB | 1355 | 0.14 | 0.49 | 0.32 |
| Pen | 247 | 0.13 | 0.60 | 0.38 |
| Pen | 650 | 0.11 | 0.74 | 0.60 |
| Pen | 1700 | 0.08 | 0.59 | 0.90 |

## What is ROBUST
1. **The QC > random-matched signal is not a one-graph fluke.** Across a 10-graph
   ensemble the graph-to-graph σ (0.003–0.017) is **much smaller than the QC–random
   gap** (~0.02–0.04) at every size. The statistical-unit caution is addressed: the
   effect survives when the *graph* is the unit, not just the walker.
2. **The mechanism is measured, not asserted.** The QC trap field is markedly
   **uniform** (number-variance ratio 0.08–0.18, strongly sub-Poissonian /
   hyperuniform-like); the random matched field is **clumpy** (0.40–0.77, near
   Poisson). So "random defects clump into traps; the QC's defects are evenly spread"
   is now a quantified statement.
3. **Random weak disorder suppresses winding** (random-matched < clean at every size),
   consistent with clumps acting as local traps that promote quick annihilation.
4. **Scaling:** among three descriptive fits, `a/logN + b` is best (SSE ≈ 7e-6 AB,
   8e-5 Pen — ~10× better than `a/√N+b` or `a/N+b`), consistent with 2-D random-walk
   winding. **Still only 3 sizes → a candidate description, not a claimed law.**

## What is NOT yet settled (honest boundary)
The hyperuniform-stamped control was meant to decide *spacing vs weave*. It is
**imperfect and the result is inconclusive**:
- The degree-stamp only **partially** reproduced the QC's trap uniformity — reasonably
  for AB (number-variance pulled down toward QC), **poorly for Penrose** (Pen N=1700
  stamped ratio 0.90 vs QC 0.08 — it did *not* achieve QC-like uniformity).
- Transport **tracked the achieved uniformity, not the intent**: where the stamp made
  the field more uniform (AB), P_logical moved **toward** QC (AB 1355: random 0.254 →
  stamped 0.266 → QC 0.2745); where the stamp failed to (Penrose), P_logical stayed at
  the random level (Pen 1700: random 0.235 ≈ stamped 0.237 ≪ QC 0.259).

This pattern is **consistent with defect uniformity driving the QC–random gap** (more
uniform ⇒ fewer traps ⇒ more winding), but because the stamp did not *fully* reach
QC-level uniformity — especially for Penrose — it **cannot cleanly separate** "defect
spatial organisation" from "quasicrystalline connectivity beyond the degree field."

## Supported conclusion (careful)
- **Confirmed:** the same defect *burden* transports differently when *clumped
  (random)* vs *evenly spread (QC)*; the QC's higher winding vs random-matched is
  **robust to graph-realisation variance**, and the QC's defect field is
  **quantifiably more uniform**. Degree + histogram + count do **not** determine
  transport — the **spatial statistics of the defects** do.
- **Leaning (not proven):** that difference is **largely explained by defect
  uniformity / trap-clumping** — transport rises with achieved uniformity. The current
  control cannot fully exclude an additional quasicrystalline-connectivity contribution
  because it did not reach QC uniformity.
- **Next discriminator (flagged, not run):** a construction that **actually matches the
  QC number-variance** (e.g. place traps by a hyperuniform point process, or match
  pair-correlation directly, rather than a nearest-node degree stamp), so "uniformity"
  and "weave" can be cleanly separated. Especially needed for Penrose.

*Ensemble means/σ, per-graph values, and spatial diagnostics in
`results/discrimination.json`. Stage-1 table unchanged and frozen.*

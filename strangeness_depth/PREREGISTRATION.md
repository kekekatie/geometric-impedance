# Pre-registration: Strangeness as Quantised Depth in a Bounded Acceptance Window

**Author:** K. T. Niedzwiecki (Independent Researcher, South Australia)
**Status:** SEALED — predict-before-build. All target values, tolerances, kill
conditions, and priors below are committed *before* any Stage 1 / Stage 2
construction is built or run.
**Date sealed:** 8 July 2026, 19:20 ACST (UTC+9:30), Adelaide, South Australia
**Commit intent:** timestamp this file in the geometric-impedance repo before
the corresponding Claude Code work begins. Nothing in Sections 4–6 may be
edited after the timestamped commit; corrections go in an appended changelog.

---

## 0. Provenance

Builds on two existing works:

- *Strangeness-Dependent Impedance and the Hyperon Puzzle* (Jan 2026) — the
  phase-space-corrected permeability η\* and the anchoring variable w(|S|).
- *Where Memory Can Live: A Taxonomy of Persistence on Aperiodic Substrates*
  (Zenodo 10.5281/zenodo.21200995) — perpendicular-space address, depth,
  Theorem 1 (perfection carries no wake), Theorem 2 (imperfection remembers at
  a quantum equal to its misfit), and the geometric shrink ratios √2−1 (AB),
  1/φ (Penrose).

Connecting conjecture: the "grip" that rises with strangeness (w) is the same
object as holonomy/memory; strangeness is quantised **depth** in a bounded
acceptance window; the window's finite depth is the ceiling; the discrete
strangeness levels are a ladder.

---

## 1. Hypothesis (one sentence)

Strangeness |S| indexes a discrete, geometrically-spaced ladder of depth-shells
in a bounded acceptance window, such that a single window geometry — fixed
before any comparison — reproduces the measured first-step suppression ratio,
the anchoring ceiling, and the finite number of levels, with no parameter tuned
to the baryon data.

---

## 2. Committed data targets (computed with error propagation)

Source values (from the strangeness paper, PDG-derived):

| S | Baryon | η\* (GeV⁻³) |
|---|---|---|
| 0 | Δ(1232)  | 8.11 ± 0.30 |
| 1 | Σ\*(1385) | 2.63 ± 0.07 |
| 2 | Ξ\*(1530) | 1.76 ± 0.10 |
| — | fitted floor η∞ | 1.60 ± 0.15 |

Derived, excess above floor E(S) = η\*(S) − η∞:

- E(0) = 6.510 ± 0.335
- E(1) = 1.030 ± 0.166
- E(2) = 0.160 ± 0.180  ← **consistent with zero**

**Committed targets a fixed geometry must reproduce:**

- **T1 — first-step ratio:** r₁ = E(1)/E(0) = **0.158 ± 0.027**
- **T2 — ceiling:** w_max = E(0)/η\*(0) = **0.80 ± 0.02** *(conditional on the
  3-point floor fit; see §3)*
- **T3 — level count:** a finite ladder terminating at ~3–4 levels.
  Justification: strong-decay-measurable levels exist at S = 0, 1, 2; the S = 3
  member (Ω⁻) has its strong channel closed and decays weakly — the ladder
  visibly stops.

The second ratio r₂ = E(2)/E(1) = 0.16 ± 0.18 is **unconstrained** (E(2) is
consistent with zero) and is therefore **not** a target. Committing this now so
it cannot later be promoted to a "match."

---

## 3. Honest state of the evidence (committed caveats)

These are limitations of the *target*, sealed so success is judged against what
the data can actually bear:

1. **The fit is an exact solve.** Three data points (S = 0,1,2), three
   parameters (floor, amplitude, ratio). Zero degrees of freedom — it *cannot*
   fail to fit. The 80% floor is a solved value, not an independently
   constrained one.
2. **Only one ratio is firm.** T1 (r₁ = 0.158 ± 0.027) is well-measured. T2 is
   partly circular (driven by the same floor fit). T3 rests on the Ω⁻ threshold
   fact, which is standardly kinematic, not obviously geometric.
3. **The floor is nonzero.** A pure geometric ladder decays to zero; the data
   decays to η∞ = 1.60. Committed structural reading: the floor is the
   irreducible un-anchored baseline permeability, and only the *excess* is the
   geometric-ladder / holonomy part (consistent with Theorem 2 quanta → 0 at
   the ideal limit). A candidate geometry is not required to explain η∞; it is
   required to explain the *excess* ladder sitting on top of it.

**Consequence for what "success" means:** because the data alone is thin, a
single free ratio hitting 0.158 is numerology. Success requires **one committed
construction, zero data-tuned parameters, hitting T1 AND T2 AND T3 together.**
That triple is the teeth.

---

## 4. Candidate ratios — sealed, with corrected prior

Nearest first-power and small-power constants vs T1 (r₁ = 0.158 ± 0.027):

| candidate | value | distance |
|---|---|---|
| 1/φ | 0.618 | 17.2σ |
| 1/φ² | 0.382 | 8.4σ |
| 1/φ³ | 0.236 | 2.9σ |
| **1/φ⁴** | **0.146** | **0.46σ — LIVE** |
| √2−1 | 0.414 | 9.6σ |
| **(√2−1)²** | **0.172** | **0.50σ — LIVE** |
| (√2−1)³ | 0.071 | 3.3σ |

**Correction on record.** An earlier informal claim (in conversation) held that
0.157 was "not close to any clean power" and that 2D substrates would likely be
*excluded* by the ratio. Proper error propagation shows this is **wrong**: both
(√2−1)² and 1/φ⁴ fall inside 1σ of the measured ratio. **2D is not excluded by
T1.** This correction is committed here so no retroactive credit can be claimed
in either direction.

**Anti-fishing rule.** The single geometric quantity each stage tests is *named
in advance* (below). No scanning a basket of ratios for whichever lands near
0.158. Any measured value arriving near a *substrate signature irrationality*
(1+√2 on AB, φ² on Penrose — the canary signatures from *Where Memory Can
Live* §5) is presumed artefact until proven otherwise.

---

## 5. Stages, sealed predictions, kill conditions

### Stage 0 — sharpen the target (no Claude Code)
- **Action:** re-derive T1–T3 with full error propagation (done above); attempt
  one out-of-sample point from the charmed-baryon decuplet analogues
  (Σ_c, Ξ_c, Ω_c) using PDG data.
- **Committed caveat:** SU(4) is badly broken and charm decays differently, so
  any charmed point is a *messy probe*, not a pillar. It may not continue the
  ladder even if the hypothesis is true.
- **Kill condition:** none — this stage only sharpens.

### Stage 1 — does depth quantise on the 2D substrates already coded (AB, Penrose)?
- **Named quantity:** the depth-ordered grip ratio between successive *discrete
  vertex environments* (Penrose/AB have finitely many local vertex
  configurations), NOT the naive per-vertex depth histogram.
- **Sealed prediction (committed prior):**
  - (a) the naive per-vertex depth distribution is ~equidistributed and will
    look **continuous** — this is a *boring null*, not a real kill;
  - (b) discrete vertex-environment bands **do** exist;
  - (c) given §4, I now expect a 2D substrate **can** match T1 (via (√2−1)² or
    1/φ⁴) — so the ratio will *not* by itself exclude 2D;
  - (d) I am **genuinely uncertain** whether any 2D window also yields T2 (0.80
    ceiling) and T3 (~4-level truncation). My lean: 2D fails the *count*,
    because a 2D window has no obvious reason to truncate at ~4 shells. Prior
    confidence: low. Committed so it can be checked against the outcome.
- **Kill condition (for 2D):** if no discrete banding appears at all, OR a
  committed 2D ratio matches T1 but the same construction fails T2 or T3, then
  2D substrates are **excluded** as the home of strangeness — a clean,
  publishable negative — and the hypothesis narrows to higher-dimensional or
  dies.

### Stage 2 — the E8 (or other higher-dimensional) window
- **Named quantity:** the shell-to-shell depth-ladder ratio of the projection's
  bounded window, its number of shells, and the ceiling those imply — all three
  derived **from the geometry alone and committed with timestamp before any
  comparison to T1–T3.**
- **Motivation (committed, not a result):** SU(3) flavour sits inside E8; E8 has
  genuine discrete shell structure (theta-series shells), which is a natural
  source of *both* a quantised ladder *and* a finite count. This is a candidate
  mechanism I am proposing, not an established correspondence. The E8-particle
  cautionary precedent (Lisi) is explicitly noted: correspondences must be
  cashed numerically, predicted-before-compared, or dropped.
- **Kill condition:** the sealed geometric prediction misses the committed
  tolerance on **any** of T1 (±0.027), T2 (±0.02), or T3 (finite, ~3–4). A pass
  requires all three from one construction with no data-tuned parameter.

---

## 6. What would count as each outcome

- **Clean hit:** one higher-dimensional window, sealed before comparison,
  reproduces r₁ = 0.158 ± 0.027, w_max = 0.80 ± 0.02, and a natural ~4-level
  truncation — no parameter tuned to baryon data. → worth a paper.
- **Clean negative (2D excluded):** discrete banding exists but no 2D
  construction hits the T1–T3 triple. → publishable negative; retire "strangeness
  = 2D depth"; keep the higher-dimensional question open.
- **Clean negative (no quantisation):** depth does not band discretely in any
  tested window. → the depth ladder is a metaphor; retire the hypothesis,
  α-precedent style, and document it.
- **Ambiguous:** ratio matches but ceiling/count do not, or the charmed probe
  muddies the ladder. → report as ambiguous; do not massage.

---

## 7. Handover notes for the Claude Code instance

- This is the same programme as the memory paper (perpendicular-space address,
  Theorem 1/2). Reuse the existing AB/Penrose projection code for Stage 1.
- Follow the measurement convention of *Where Memory Can Live* §2: classify
  edges against the substrate's own star vectors; accumulate ideal e⊥ increments.
- Preserve the pre-registration discipline: compute and commit every predicted
  number **before** building the construction that tests it, exactly as Table 1
  of the memory paper was committed before the torus was walked.
- Report failed constructions in full (canary-signature discipline).

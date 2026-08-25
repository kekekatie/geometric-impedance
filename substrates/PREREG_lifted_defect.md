# Draft pre-registration: can the map carry a localized conserved defect? (lifted Burgers audit)

**Status — SEALED. Crew agreed (Karen, Gemini, GPT, Fable; Claude), with Fable's two knives
incorporated (Gate 0 null via the periodic control; Test 2 loop census). Sealed by this
commit; corrections go only in a dated amendment.** From GPT's handoff spec, Fable's cautions,
and the materials report's Experiment 5.

The foundational "thing made of map" question, kept clean: **can the existing rank-4 map
support a genuine localized *conserved* defect carried entirely by its own lift variables,
using only the existing representation and legal flips — adding nothing from outside?** The
exciting outcome is not "a weird patch survives" but *local embodiment changes while a
relational/topological identity persists.*

---

## 1. Structural facts already established (the spine)

- Our cut-and-project tilings are **defect-free by construction**: single-valued lift
  (a ∈ Z⁴, ustar), Euler χ = 2, 100% rhombi.
- **Flips preserve this** — every flip validation kept χ = 2 and 100% quads. So a legal flip
  **can neither create nor destroy** a topological defect. Two consequences, both design-critical:
  (i) the protection mechanism a persistent object needs is **real and already demonstrated**;
  (ii) a defect therefore **cannot be flipped into being** — it must be *constructed*, and whether
  the grammar even admits a legal constructed defect is the first gate.

## 2. The charge, defined in existing variables only

Along each tiling edge the lift increment is a unit step e_k in the parent lattice
(Δa = star[k], Δustar = K[:,k]). The **lifted Burgers charge** of a closed physical-space loop
is the sum of these increments around it, an element of the parent lattice, split into
**b∥** (its parallel-space image, ordinary elastic distortion) and **b⊥** (its
perpendicular/kernel part, the phason mismatch). It is identically zero on every loop of the
perfect tiling. No new "particle" object is introduced; the charge is a functional of the
lift the tiling already carries.

## 3. The audit (gated)

**Gate 0 — constructability.** Can we build a **legal** rhombus tiling (existing tiles and
matching, existing lift variables) containing a controlled dislocation dipole **+B, −B** with
a well-defined nonzero closure on an enclosing loop, via a Volterra-type cut-and-displace?

**Gate 0's own null (Fable's knife 1).** A construction can fail for boring reasons —
implementation fiddliness, too-small patch, an awkward cut path — and that failure is
outwardly identical to "the grammar forbids it." So before concluding H_none, **run the
identical construction on the periodic lift control.** Three outcomes, three different reports:
(a) succeeds on the periodic lift but **not** on the QC → a real grammar difference, H_none
earned; (b) fails on **both** → an implementation limit, reported honestly as "**Gate 0 not
resolved**", never as H_none; (c) succeeds on the QC → proceed to the tests below. The control
ladder thus extends *downward into the gate*, not just into the dynamics.

If Gate 0 passes:
- **Test 1 — core mobility vs charge invariance.** Apply legal flips near and far from the
  core; does the microscopic core move/reshape while **b∥ and b⊥ around an enclosing loop stay
  invariant**?
- **Test 2 — annihilation.** Can a +B and −B pair be brought together by flips and annihilate?
  **Pass condition, by loop census (Fable's knife 2):** *every* loop in a stated family —
  all elementary tile boundaries, plus a set of nested loops around each former core site —
  has zero closure afterward, not merely the one large enclosing loop. (Otherwise a pair that
  "annihilates" into two smaller offsetting mismatches would falsely pass.)
- **Test 3 — no bulk vanishing.** Can a single isolated B disappear in the bulk under flips?
  (It should not — it must reach a boundary or annihilate with its opposite.)
- **Test 4 — identity is the charge, not the patch.** Compare charge persistence against
  vertex-set persistence and core-shape persistence; the object is the conserved closure class,
  not any fixed collection of vertices.

## 4. Controls (the decisive one is the lift-label control)

- **Lift-label / generic-lattice control.** The conserved charge may be generic to *any*
  parent-lattice edge labelling, **not** to quasiperiodicity. Run every test on a **periodic**
  parent-lattice-lifted tiling and a **scrambled** tiling. If the charge behaves identically
  there, it is generic lifted-lattice topology, not a quasicrystal property.
- **Approximant control** as a chemically-related intermediate.

## 5. Not allowed / not used (kept honest)

No energy, no target state, no external traveller, no new conservation law, no hand-designed
particle dynamics — the charge must live in the existing lift variables. And (Fable) the
history-experiment "defect" (a vertex whose type is absent from the ideal vocabulary) is **not**
used as objecthood — it is too reference-dependent; the object here must be an intrinsic
conserved lifted-closure class.

## 6. Hypotheses

- **H_object** — a constructed ±B pair has flip-mobile cores with invariant B, annihilates in
  pairs, and a single one cannot vanish in the bulk → the map supports a genuine object made of
  map: topological, not a fixed patch.
- **H_generic** — the same holds, but *identically* on the lift-label/periodic control → the
  charge is generic parent-lattice topology, not quasiperiodic.
- **H_none** — no legal defected configuration is constructible in the grammar → the map does
  not support endogenous lifted defects.

## 7. Predictions, to be scored

- **Gate 0 constructability:** genuine QC dislocations exist in the literature, so plausibly
  yes, but our specific representation may resist a clean legal construction. **Credence 0.55.**
- **If constructible, B invariant under flips** (basic lift topology): **Credence 0.85.**
- **QC-specific beyond the lift-label control (H_object over H_generic):** **Credence 0.25** —
  the charge is likely generic to the parent-lattice labelling, per the control caution.

Overall: **H_generic 0.45 / H_none 0.30 / H_object 0.25.** Honest expectation: *if* an object
exists it is most likely a **generic lifted-lattice** topological object — real, but not a
quasicrystal-specific one. Still a clean, meaningful result.

## 8. Decision rule

Claim "object made of map" only if Gate 0 passes **and** B is invariant under flips **and**
pairs annihilate **and** a single one cannot vanish in the bulk. Claim it **quasiperiodic**
only if it *differs* from the lift-label/periodic control. Otherwise report the honest weaker
statement (generic lifted-lattice object, or none).

## 9. Out of scope

Energetics (Branch B, parked); coherent transport (its own pre-reg, `PREREG_transport_hierarchy.md`).

---

## Amendment 1 (dated 2026-08-25) — Gate 0 outcome recorded

Gate 0 has been run (`lifted_defect_gate0.py`; results in `RESULTS_GATE0_DEFECT.md`).
**Outcome (b): not resolved, implementation-limited — H_none NOT earned or claimed.**
The periodic control (square lattice) constructs a genuine localized dislocation whose
radius-invariant Burgers vector the instrument reads correctly (also the first
validation of the functional on a *nonzero* charge). The QC failures are a missing
coupled phonon–phason elasticity relaxation, not a grammar obstruction. One off-menu
finding stands: a pure phason-offset winding on the QC yields only **kernel** holonomy
(b∥ = b⊥ = 0) — the phason relabels congruence classes, it does not carry a physical
charge. Tests 1–4 remain untested pending a legal constructor (elasticity solve or de
Bruijn multigrid). This amendment records an outcome only; it does not alter the sealed
plan above.

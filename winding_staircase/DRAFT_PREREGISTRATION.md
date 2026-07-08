# DRAFT Pre-registration: Does Holonomy Winding Mode-Lock? (Arnold-Tongue / Devil's-Staircase Test)

**Status:** ⚠️ **DRAFT SKELETON — NOT SEALED.** Scaffolded by Claude Code as an
on-ramp. Every prediction, tolerance, and kill condition marked `[AUTHOR TO
SEAL]` must be filled in and committed *by the author* **before** any sweep is
run. Sealing = a later, separate, timestamped commit. Nothing here is a
committed prediction yet.
**Author (to seal):** K. T. Niedzwiecki
**Date drafted:** (this commit's timestamp) — *draft only, not the seal*

---

## 0. Provenance

Builds on:
- *Where Memory Can Live* (Zenodo 10.5281/zenodo.21200995): Theorem 1 (perfection
  carries no wake — ideal-lattice closed-loop holonomy ≡ 0), Theorem 2
  (imperfection remembers at a quantum = its misfit), shrink ratios √2−1 (AB),
  1/φ (Penrose); the torus winding integers w = ±1, ±2 and the phason-strain
  quantum π⊥(M).
- The devil's-staircase insight (wandering session, 9 Jul 2026): imperfection
  has **two dials** — *winding* (integer, no half-steps) and *misfit/phason*
  (continuous, mediants/half-steps, silent until it winds into a quantum). Mode-
  locking, Arnold tongues, and Diophantine approximation are the formal home.

**Connecting conjecture (to test):** our holonomy system has a natural *winding
frequency* that, as a control parameter is swept, **mode-locks** onto rational
plateaus forming a devil's staircase — widest plateaus on the simplest rationals,
narrowest (or absent) at the substrate's characteristic irrational (√2−1 for AB,
1/φ for Penrose), with φ (most irrational) the last to lock. If true, the AB-vs-
Penrose commensurability contrast we already measured is two points on this
staircase.

---

## 1. Hypothesis (one sentence)

`[AUTHOR TO SEAL — one sentence.]` *Candidate:* "As the phason/cut parameter of
the acceptance window is swept continuously, the accumulated holonomy winding
number per unit sweep locks onto rational plateaus (Arnold tongues) whose widths
are ordered by denominator, forming a devil's staircase governed by the
substrate's Diophantine class."

---

## 2. The knob (control parameter) — MUST be named before sweeping

This is the crux and the anti-fishing linchpin. Candidates for the author to
choose **one** (or name another), and commit before any sweep:

- **(K1) phason / cut offset γ.** Sweep the acceptance-window offset γ ∈ ℝ²
  (or along one direction) continuously. Each γ gives a tiling; track a winding
  observable vs γ. Physically: turning the *continuous* misfit dial and watching
  the *integer* response — the exact "silent until it winds" picture.
- **(K2) approximant slope.** Sweep the rational slope p/q of the projection
  continuously through the reals (irrational = quasicrystal, rational =
  approximant). The winding rate as a function of slope is the classic
  circle-map setting.
- **(K3) drive ratio.** Impose two competing periods (parallel vs perp, or an
  external drive vs the intrinsic inflation) and sweep their ratio; measure
  phase-locking of the holonomy accumulation.

**Named knob:** `[AUTHOR TO SEAL — K1 / K2 / K3 / other]`

## 3. The observable (winding frequency) — named before sweeping

`[AUTHOR TO SEAL]` *Candidate:* Ω(knob) = (net integer holonomy winding
accumulated over a fixed sweep window) / (sweep length) — the "rotation number"
of the drive. Measured via the *Where Memory Can Live* §2 convention (classify
against own stars; accumulate ideal e⊥ increments).

---

## 4. Sealed predictions — ALL `[AUTHOR TO SEAL]` before the sweep

Do not fill by looking at a sweep. Fill from theory, seal, then sweep.

- **P1 — plateaus exist:** Ω(knob) is a *staircase*, not smooth. `[SEAL: yes/no
  and confidence]`
- **P2 — plateau locations:** widest plateaus sit at `[SEAL: which rationals —
  candidate 0, 1, 1/2, and substrate-symmetry-related values]`.
- **P3 — width ordering:** plateau width decreases with denominator (simplest =
  widest). `[SEAL: quantitative form, e.g. width ∝ 1/q^k for k = ?]`
- **P4 — substrate contrast:** AB (silver/commensurate-leaning) shows *wider*
  plateaus than Penrose (golden); φ-related values lock last/least. `[SEAL:
  predicted width ratio AB:Penrose at a named value]`
- **P5 — staircase dimension (optional):** fractal/box dimension of the locked
  set. `[SEAL: predicted value — e.g. the ~0.87 critical-circle-map universal,
  or a substrate-specific number, with justification]`

## 5. Anti-fishing rules (carried from the programme)

- The knob (§2) and the predicted plateau locations (§4) are named **in advance**.
  No sweeping first and labelling plateaus afterward.
- Any measured plateau at a **substrate signature irrationality** (1+√2 on AB,
  φ² on Penrose — canary signatures) is presumed artefact until proven otherwise.
- Report the full Ω(knob) curve including non-locking regions; no cropping to the
  pretty plateaus.

## 6. Kill conditions

- **No staircase:** Ω rises smoothly with no measurable plateaus → the winding-
  frequency idea is a metaphor, not a mechanism. Retire it (α ≈ 0.553 precedent),
  document fully.
- **Plateaus but no Diophantine order:** locking exists but widths do not track
  denominator / substrate class → partial; report structure, do not massage.

## 7. Outcomes (pre-registered)

- **A — Clean staircase, substrate-ordered:** plateaus exist, widths ordered by
  denominator, AB:Penrose contrast as predicted (P4), φ locks last. → the winding-
  frequency thread earns its teeth; candidate for the ONN/Kuramoto bridge.
- **B — Staircase without substrate order:** generic mode-locking, but not
  governed by the substrate's Diophantine class → interesting-but-not-ours;
  report honestly.
- **C — No locking:** retire the winding-frequency mechanism; keep the two-dials
  *description* (which is already established in the memory/defect results) as
  the durable result.

## 8. Handover notes for Claude Code (once sealed)

- Reuse `reverse_loop_test/geometry.py` (AB/Penrose projection, depth, stars) and
  the `defect_holonomy_test/` holonomy machinery (lift-by-integration, torus
  winding). The winding integers and phason quantum are already in hand.
- The sweep is a new loop over the named knob; the observable reuses the existing
  ideal-e⊥ accumulation. No new substrate types needed for K1/K2.
- Preserve pre-registration discipline: this file's `[AUTHOR TO SEAL]` fields
  become a sealed commit *before* the sweep commit. Report failed/partial sweeps
  in full (canary discipline).

---

*Reminder: this is a DRAFT. It is safe to edit freely until the author fills the
`[AUTHOR TO SEAL]` fields and makes the separate sealing commit. Only after that
commit are §§1–7 frozen.*

# SEALED Pre-registration: Does Holonomy Winding Mode-Lock? (Winding Staircase)

**Status:** **SEALED.** What seals is the Sealing Ruling as amended by Amendment 1
and Amendment 2, with two folds applied at seal per the reviewing Claude Code
instance's flags: (i) the topology/boundary-condition control line added to §B5;
(ii) the substrate-discrimination tolerance tightened from ±20% to ±15% in §B3
(the ±20% bands overlap — √2−1·1.20 = 0.497 > 1/φ·0.80 = 0.494; ±15% bands are
disjoint: silver [0.352, 0.476], golden [0.525, 0.711]).

**Author:** K. T. Niedzwiecki. **Sealed by this isolated, timestamped commit.**
Sections are frozen; corrections go in an appended changelog only. Supersedes
`DRAFT_PREREGISTRATION.md`.

**Date sealed:** 9 July 2026, ACST.

---

# PART I — THE SEALING RULING

## 0. Disclosure (anti-fishing integrity)
- No sweep of any kind has been run. No Ω(knob) curve has been seen by author or
  any Claude instance.
- Two literature values were verified before sealing: the universal critical-
  circle-map staircase dimension **D ≈ 0.8700** (Jensen, Bak, Bohr) and the
  substep width-decay exponent **δ ≈ 3** at criticality. Used as instrument
  calibration targets, **not** as predictions of the framework (§5 / rule C).

## 1. Central ruling: the substrate is a K = 0 system
A devil's staircase is a phenomenon of dissipative, nonlinear dynamics with two
competing frequencies, at the critical line where the map loses invertibility.
The cut-and-project substrate has none of the ingredients: π⊥ is **linear**,
holonomy **telescopes** (why Theorem 1 is arithmetic, not dynamical; residue is
single-valued in position). No dissipation, no attractor, no nonlinear coupling —
an ideal tiling is the orbit of a rigid rotation. In circle-map language the
substrate sits at **K = 0**: rotation number = bare frequency, a straight line,
no plateaus. Mode-locking cannot occur on the rigid substrate as a matter of
structure.

## 2. Ruling on the knob: **K3**, with K1 and K2 as predicted nulls
- **K1 (phason/cut offset γ) — RULED OUT by Theorem 1.** Every γ yields a
  different ideal tiling; all lie on the ideal projected lattice; all heal.
- **K2 (approximant slope) — RULED OUT by linearity.** Winding tracks slope
  exactly and monotonically; no interval shares a winding number.
- **K3 (drive ratio) — NAMED KNOB.** The only candidate supplying the two
  ingredients locking needs: a second competing frequency and a nonlinear
  coupling. Ruling made on framework grounds, before any sweep.

## 3. Epistemic cost of K3 (committed)
Selecting K3 means **we test tiling + imposed dynamics, not the tiling.** The
substrate's whole role is to supply the intrinsic frequency:
ω_intrinsic is set by the Theorem-2 misfit quantum π⊥(M) — nonzero, quantised,
shrinking √2−1 per approximant order (AB), 1/φ per order (Penrose). Coupling K and
ω_drive are imposed by us; knob Ω = ω_drive/ω_intrinsic; K is the second axis.
**Committed prior:** single most likely outcome is **Outcome B** (generic mode-
locking, no substrate content), ≳ 50%.

## 4. Sealed predictions
- **N1 (K1 null, theorem-grade):** Ω(γ) ≡ 0 within FP floor (≲ 10⁻¹⁵), all γ,
  both substrates. Any nonzero holonomy on an ideal tiling is a **code defect**
  until proven; if it survives scrutiny, Theorem 1 is in question and *that* is
  the story.
- **N2 (K2 null, linearity-grade):** Ω(slope) strictly monotone, no plateaus
  above the finite-size floor.
- **F — finite-size canary (mandatory control):** a finite patch quantises the
  measurable rotation number and manufactures spurious plateaus of width ~1/N.
  Measure plateau width at ≥ 3 patch sizes N; a genuine plateau is **N-
  independent**, an artefact is **∝ 1/N**. Mandatory for N1, N2, and every K3
  sweep. Applies to Stage D's K* as well.
- **C — calibration rule (NOT a prediction):** D ≈ 0.87 and δ ≈ 3 are properties
  of any critical circle map; reproducing them is instrument calibration, never a
  finding. Failure to reproduce D ≈ 0.87 ± 0.01 at criticality means the
  instrument is broken.
- **P2 (K3):** widest plateaus at simplest rationals ρ = 0, 1, 1/2, then 1/3,
  2/3; width decreasing with denominator (Farey/Stern–Brocot).
- **P3 (K3):** at criticality Δ(p/q) ~ q^(−δ), δ = 3.0 ± 0.3 (calibration check).
- **P4 (see Amendment 1 — withdrawn/reformulated as P4′, calibration-2).**

## 5–7. Anti-fishing, kills, stages
Knob and plateau locations named in advance; canary F mandatory before any
plateau claim; D ≈ 0.87 / δ ≈ 3 are calibration never findings; substrate
signature irrationalities (1+√2 AB, φ² Penrose) are standing artefact canaries;
full Ω(knob) curves reported, unlocked regions included. Kills: N1/N2 violated →
suspect code first, theorem second; no N-independent plateaus at supercritical K
with calibration passing → retire the mechanism (Outcome C).

## 8. Programme note
K3 can lock only because locking needs coupling, which a rigid tiling lacks and an
oscillator network has. The winding-frequency thread and the ONN/Kuramoto bridge
are therefore **one thread**. Held to standard: **structural correspondence, not
isomorphism.**

---

# PART II — AMENDMENT 1 (P4 forced; Stage C reclassified; Stage D introduced)

## A1. Stage C has no empirical content
Hand-feeding the substrate's irrational into a driven circle map and observing
circle-map theory is composing two known facts (Theorem 2 arithmetic + circle-map
locking), a valid **deduction, not a measurement**. No tiling participates in the
dynamics. The "unification" is true by construction. Confirming it verifies the
code, and is **never a finding** (same reclassification the reverse-loop test
received once residue was seen to telescope).

## A2. P4 as written is ill-posed; corrected to P4′
There is **no subcritical K_c** for either substrate irrational: golden ([0;1,1,…],
Lagrange √5 ≈ 2.236, the most badly approximable number) and silver ([0;2,2,…],
Lagrange 2√2 ≈ 2.828) are both badly approximable and both survive **unlocked to
K = 1**. So "compare K_c" compares thresholds that do not exist (author error,
caught pre-seal).
**Corrected, well-posed observable P4′ (calibration-2, forced, never a finding):**
at matched subcritical K < 1, g(α, K) = width of the unlocked gap containing α.
Sealed: g(golden, K) > g(silver, K), closing more slowly as K → 1⁻ (golden sits
farther from every rational, |α−p/q| ≳ 1/(Lq²), smaller L = farther). A P4′
failure means the code is wrong, not the framework. **Outcome A as originally
written is withdrawn; there is no Outcome A in Stage C.**

## A3–A6. Stage D introduced; honest net shape
Stage D is the only stage with genuine empirical content (see Part III as further
amended). After Amendment 1 the thread contains two theorem-grade nulls, two
calibration checks, and one real experiment (Stage D) whose expected outcome is
negative — the true, thinner shape. Worth running (α-precedent); not a paper on
the strength of the forced stages; the ONN bridge is not claimed until Stage D
says something no circle map would have said anyway.

---

# PART III — AMENDMENT 2 (Stage D control corrected + graded), with seal folds

## B1. Degree-preserving rewiring is the wrong *primary* control
Rewiring preserves the degree sequence but not **locality**; a random rewire of a
planar local graph greatly enlarges the spectral gap / algebraic connectivity,
which is exactly what Kuramoto onset K* is dominated by. So the rewired control
departs from the native graph with near-certainty for reasons of locality, not
aperiodicity — it answers "does locality matter?" (trivially yes) and is silent on
the Diophantine class. **Periodicity is the treatment, not a confound.**

## B2. Correct primary control: the rational approximant
Periodic (the treatment), planar, local, spatially embedded, same vertex
environments (hence ~same bulk degree histogram — **to be verified empirically
before use**), differing from the ideal in exactly one respect: rational slope
p/q vs the irrational. Aperiodicity isolated, everything else held. Already the
object of *Where Memory Can Live* §6.

## B3. Stage D upgraded: binary → graded  *(seal fold: tolerance ±15%)*
Run the Kuramoto protocol on the convergent sequence k = 1, 2, 3, 4 and on the
ideal; measure K*(k).
- **Degree governs:** K*(k) is **flat** across orders (degree histogram barely
  changes).
- **Diophantine class governs:** K*(k) converges to K*(ideal) **at the
  substrate's own registered shrink ratio — √2−1 per order (AB), 1/φ per order
  (Penrose)** (*Where Memory Can Live* Table 1, sealed and recovered). The
  dynamical onset would pay the same price list as the memory quanta.

**This prediction is NOT forced** — nothing in circle-map, Kuramoto, or projection
theory requires the locking onset to track the misfit.

**Sealed prediction (committed pre-run):** K*(k) is **flat across approximant
orders**, within the finite-size floor. Locking governed by coordination/degree,
not the Diophantine class. Confidence moderate-to-high (coordination-gap Spearman
0.982 AB / 0.967 Penrose; Goldilocks degree-not-substrate across Penrose, AB, and
E8).

**Kill / discovery condition (D-positive):** K*(k) → K*(ideal) at the registered
**substrate-specific** ratio, **±15%** — AB must land in the silver band
**[0.352, 0.476]** and Penrose in the golden band **[0.525, 0.711]** (disjoint by
construction; ±20% was overlapping and is rejected). A single shared ratio across
both substrates, a ratio in the wrong substrate's band, or convergence at any
unregistered rate is **not** a hit and must be reported as such. D-positive is the
only genuine, non-forced discovery available anywhere in this thread.

## B4. Rewiring retained as secondary
Degree-preserving rewire = maximal-disruption reference / upper bound on how much
non-degree structure can matter for K*. Reporting order: (1) primary — approximant
sequence vs ideal; (2) secondary — rewire (upper bound); (3) optional tertiary —
matched-degree periodic lattice. A native-vs-rewired departure is **not** evidence
for D-positive.

## B5. Construction cost + control-validity conditions  *(seal fold: topology line)*
Planar approximants tile with seams (1,482 seam artefacts in the order-2 AB test,
*Where Memory Can Live* §7). Stage D's primary control therefore needs either the
**seamless phason-shear approximant** (specified, tractable-but-open) or **torus
topology** (single seam, pristine interior). Same construction the memory paper's
outstanding surgical leg needs — build once, serves both.

Control-validity conditions (all mandatory before any Stage D result is reported):
1. **Degree-histogram match must be verified empirically** on the chosen
   construction; if bulk histograms of approximant and ideal differ materially,
   the control is invalid and the design must be revisited.
2. **Topology / boundary conditions must be held fixed across the entire
   k-sequence AND the ideal comparison** — torus throughout, or seamless-planar
   throughout, **never mixed**. Kuramoto K* depends directly on the spectral gap,
   which open-planar vs periodic-torus boundary conditions change outright; a
   topology mismatch would measure boundary conditions wearing aperiodicity's
   clothes.
3. Finite-size canary F (≥ 3 sizes; K* must be N-independent) applies to K*.

## B6. Net effect
Stage D remains the single stage whose outcome is not fixed by theory. Amendment 2
sharpens it from a binary "does geometry matter?" (answerable trivially and wrongly
by rewiring) to a graded, quantitative, substrate-specific question: **does the
dynamical locking onset pay the same price list as the memory?** Expected answer:
no. Committed in advance. Worth running anyway.

---

# Amended stage list (execution order)

- **Stage A** — the two nulls (N1 Theorem 1; N2 linearity) + canary F. Cheap,
  existing code. Proves the instrument does not hallucinate plateaus.
- **Stage B** — calibration: reproduce D ≈ 0.8700 ± 0.01, δ ≈ 3.0 ± 0.3. Control,
  not result. Do not proceed if it fails.
- **Stage C** — deterministic verification (calibration-2): test P4′. Confirms the
  substrate number is transported correctly. Reportable only as a check.
- **Stage D** — the real test: emergent Kuramoto dynamics on the substrate's own
  graph (ω_i = f(depth_i), coupling along native edges), across the approximant
  convergence sequence vs ideal, one fixed topology throughout, degree-histogram
  verified, canary F on K*. Primary control = approximant sequence; secondary =
  degree-preserving rewire. The only stage whose outcome is not fixed in advance.

# Standing rules
Knob/plateau locations named in advance; canary F mandatory; D ≈ 0.87 & δ ≈ 3 &
P4′ are calibration never findings; signature irrationalities (1+√2, φ²) are
artefact canaries; report full curves and all failed/partial sweeps. Changelog
only for post-seal corrections.

## Changelog
- *(none yet — seal is the initial state; folds noted in the status header were
  applied at seal, not after.)*

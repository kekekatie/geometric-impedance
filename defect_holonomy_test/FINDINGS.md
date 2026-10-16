# Defect-Holonomy Test — Findings (Iterations 1–4)

## Iteration 4b — v3.1 surgical leg: attempted, hit a genuine construction wall

Per v3.1, the planar surgical dipole was attempted (Bravais-level Volterra:
quadrant shift by the period P_a, corner core, split-convention measurement).
**It hit a genuine wall, reported per house rules (not massaged):**

- The naive planar approximant — tiling the ideal-patch unit cell periodically —
  is **not a seamless unit-edge crystal**. The order-2 AB tiling showed **1482
  misfit edges** (residual > 0.3) pervading the bulk, because the ideal
  quasicrystal cell does not tile periodically without inter-cell misfit at
  *every* cell boundary. The measurement was consequently dominated by tiling
  artifacts, not the dislocation.
- **Why the torus works and the naive plane does not:** the torus has exactly
  **one** seam (the phason wall at the wrap) with a pristine ideal interior; the
  naive planar periodic tiling has a seam at every cell boundary. A clean Bravais
  dislocation needs a genuinely seamless approximant crystal first.
- **The open construction question:** a proper periodic approximant (seamless,
  unit-edge — the standard QC-literature construction via a perp-space phason
  shear that snaps acceptance to periodicity, not naive motif-tiling) is the
  prerequisite. Building it, then cutting the Bravais dislocation, is the
  remaining computational step. Flagged open, as pre-agreed: the torus stands as
  the crown; the surgical robustness of the quantum is untested.

This is an honest negative on the *construction*, not on the physics: the torus
(iteration 4) already establishes quantisation, the registered quanta, and the
price-list scaling as theorem-grade verification.

## Iteration 4 — v3 torus crown jewel: quantised holonomy at the registered quanta

**Result: Outcome A on the approximant torus.** Path memory exists, is quantised,
and hits the Phase-0 registered quanta exactly on both substrates — with the
predicted geometric shrink across the convergent sequence.

**Phase 0 (pre-registered, committed before construction, `phase0_registration.json`):**
holonomy quantum = ideal `π⊥(M_a)` of the approximant period sublattice. Shrink
ratio derived as `√2−1 ≈ 0.41421` (AB) and `1/φ ≈ 0.61803` (Penrose) — the first
power, not the squared guess.

**E4 + E2 measurement (`torus_holonomy.py`, `results/v3_torus_pricelist.json`):**
the approximant torus is built with ideal positions and boundary wrap (the seam
is the frozen phason wall); edges classified against the substrate's own stars at
the FP floor; perp increments taken **ideal** (the split convention). Any closed
torus loop's holonomy is `π⊥(net lift)`, quantised on `π⊥(S)`.

| order | AB conv | AB registered = measured | Penrose conv | Penrose registered = measured |
|---|---|---|---|---|
| 1 | 1/1 | 0.414214 | 1/1 | 0.236068 |
| 2 | 3/2 | 0.171573 | 2/1 | 0.145898 |
| 3 | 7/5 | 0.071068 | 3/2 | 0.090170 |
| 4 | 17/12 | 0.029437 | 5/3 | 0.055728 |

Measured = registered to all printed digits at every order; measured shrink ratio
= 0.41421 (AB) / 0.61803 (Penrose) at every step. **All orders hit registered
quanta.**

**Why the torus and not the plane (the construction insight).** The ideal-lattice
theorem (iteration 3) heals *any* physically-closed loop. An approximant with
ideal positions inherits the theorem (heals); naively rationalising the
projection collapses (the period sublattice maps every coset to one point). The
escape is topological: on the torus a non-contractible loop has
`π∥(m)=P_a ≠ 0`, so it is **not** physically closed — the theorem's hypothesis
fails, the net lift is a period vector `m ∈ ⟨M_a,M_b⟩`, and the ideal perp of that
lift is the nonzero quantum. This is the reverse-loop caveat and the iteration-3
theorem meeting exactly: rigid-edge holonomy lives in `π⊥(ker π∥')`, zero for the
ideal QC, geometrically small but nonzero for each approximant.

**Honesty on scope.** Holonomy here telescopes to `π⊥(net lift)` exactly (edges
are ideal stars), so the E4 result is deterministic — its content is the *match*
between the torus measurement and the *independently computed* Phase-0
registration (two separate calculations agreeing exactly), the nonzero-ness
versus ideal/planar, and the geometric scaling. The still-open robustness tests:
E1 planar surgical dipole (does a real dislocation core with seam misfit hit the
quantum within the FP floor, or does the phason wall add spread?), E3 M-dependence
forgery (holonomy must track the chosen period's *direction*, not just magnitude),
and the §6 calibration statistics on that spread. The torus establishes the
quantisation and the price list; the surgical tests probe how a real defect
carries them. Canaries (1+√2, φ²) absent; ramp method remains forbidden.

---

# Defect-Holonomy Test — Findings (Iterations 1, 2 & 3)

## Iteration 3 — the rigid-edge holonomy theorem (verified)

The boundary-escape mechanism (iteration 2) is the *relaxation pathway*, but a
deeper theorem makes healing **inevitable**, independent of construction or
topology:

> **Theorem.** On any structure whose vertices lie on the ideal projected lattice
> with exact star-vector edges, the perpendicular holonomy of every closed
> physical loop is identically zero. A closed loop's integer edge-sum
> `m = Σ s·ê_j` satisfies `π∥(m)=0`; and `ker(π∥) ∩ Z^N` maps to zero under `π⊥`.

Verified numerically (`verify_holonomy_theorem.py`), |mᵢ| ≤ 20:

- **Ammann–Beenker:** `ker(π∥) ∩ Z⁴ = {0}` exactly ⇒ `m = 0` ⇒ holonomy 0.
- **Penrose:** `ker(π∥) ∩ Z⁵ = Z·(1,1,1,1,1)` exactly (cyclotomic relation Φ₅),
  and `‖π⊥((1,1,1,1,1))‖ = 3.5×10⁻¹⁶ ≈ 0` ⇒ holonomy 0.
- **Corollary (strongest form):** the v2 tight-loop integer sums are *literally*
  the zero vector `[0,0,0,0(,0)]` at every radius, both substrates — not "small
  perp norm." Healing is the exact algebraic identity, not a numerical accident.

**Consequence — the correction to iteration 2's framing.** Healing is *not*
fundamentally a free-boundary effect; even an ideal-tiling torus would heal
(`ker(π∥)` still has zero perp image). The load-bearing ingredient for rigid-edge
holonomy is **rationality of the projection**: a periodic (rational-approximant)
tiling gives `π∥` a nonzero integer kernel vector `M` (the approximant period)
with `π⊥(M) ≠ 0`. That perp image is the **only legal home** for rigid-edge
holonomy, and it is what v3 must target. Non-simply-connectedness is necessary
(you need a loop that winds the torus so `m = M`), but rationality is what makes
`π⊥(M) ≠ 0`.

**Registered v3 predictions (pre-compute before running):** holonomy quantum =
`π⊥(M)` of the chosen approximant and integer multiples (NOT `±e⊥_{j*}`); across
the convergent sequence k = 1, 2, 3…, `|π⊥(M_k)|` shrinks geometrically toward
zero (asymptotic ratio 1/δ_silver² for AB, 1/φ² for Penrose), the ideal QC being
the k→∞ limit where topological memory is squeezed out. M-dependence replaces
b-dependence as the forgery test: each approximant order must yield its own
registered quantum.

---

# Defect-Holonomy Test — Findings (Iterations 1 & 2)

**Programme:** Aperiodic projection tilings / directional balance / arrow-of-time
**Status:** Pre-registered protocol (v1 + v2 amendment) executed to a genuine,
mechanistic result. Honest report; nothing massaged.
**Substrates:** Ammann–Beenker and Penrose, reported separately.

---

## Headline

- **E0 (metric validation) — PASSED.** Lift-by-integration, reading perp
  displacement from **edge geometry alone**, reproduces the reverse-loop
  machinery to the floating-point floor (open-walk error ~2–3×10⁻¹⁵; closed-loop
  holonomy ~5×10⁻¹⁶). Integrity lock 2 holds.

- **v2 terminating-grid-line construction — TOPOLOGY CORRECT, EDGES CLEAN, but
  PHYSICAL HOLONOMY HEALS — with an identified mechanism.** The construction
  builds a genuine unit-edge tiling whose lift has closure defect exactly
  `±ê_{j*}` (the topological monodromy is really present), with all edges exact
  star vectors (residual ~10⁻¹⁵, zero over-tolerance). Yet the measured
  holonomy of every winding loop sits at the floating-point floor (≤10⁻¹⁵).

- **Why it heals (verified, not conjectured):** the dislocation's lift-shift
  field is single-valued (`sc ∈ {0,1}`), and the shifted region **reaches the
  free patch boundary** (radius 26 of 26). On a finite, simply-connected patch
  the topological obstruction slides out to the boundary; the merged lift is
  therefore globally single-valued, so every closed loop sums to zero and the
  bulk holonomy vanishes identically.

- **This is the reverse-loop caveat, closed.** The reverse-loop FINDINGS said
  genuine holonomy needs a **non-simply-connected perp coordinate**. We now have
  the sharp form: on a simply-connected patch with a free boundary, a
  lattice-vector dislocation **cannot** carry bulk holonomy — the obstruction
  escapes. **Genuine bulk holonomy requires a domain with no free boundary for it
  to escape into: a toroidal patch / periodic approximant.** That is the next
  experiment.

**H1 is therefore not confirmed and not refuted on finite patches; it is shown
to be untestable there for a structural reason, and the fix is specified.**

---

## The b-dependence discriminator (§4-v2, "a forgery can't follow the knife")

Run for two families j* per substrate. The v1 artifact holonomies were
**b-independent** (the forgery). The v2 construction's *topological* Burgers
vector does follow the knife exactly — the closure defect equals `±ê_{j*}` for
each chosen family (AB: b⊥ = [1,0] for j*=0, [−0.707,0.707] for j*=1; Penrose:
[1,0] and [−0.809,0.588]). But because the physical holonomy heals to the floor,
there is no *measured* holonomy to rotate — consistent with healing, not with a
hidden artifact. The canary values (1+√2 on AB, φ² on Penrose) do **not** appear
in v2, confirming the v2 seam is clean.

## The healing theorem, now demonstrated three ways

1. **v1 region-shift + geometric re-glue** (iteration 1): heals for many
   cores, or yields the b-independent √2 / φ² seam artifact. A region shift
   faults along its whole boundary → even crossing parity → cancellation.
2. **v1 displacement ramp** (iteration 1): rejected on principle — elastic
   distortion injects non-exactness (forbidden by §2). Retained only as a
   documented artifact / canary calibration.
3. **v2 terminating grid-line** (iteration 2): the topologically correct
   construction. Closure defect = `±ê_{j*}`, unit edges everywhere, **and it
   still heals** — because the single-valued shift field escapes to the free
   boundary. This is the deepest and cleanest demonstration: even a
   topologically genuine dislocation carries no bulk holonomy on a
   simply-connected finite patch.

## Gate E0b results (per protocol §4-v2)

| substrate | j* | closure = ±ê_{j*} | unit-edge clean | boundary escape | max tight-loop holonomy |
|---|---|---|---|---|---|
| Ammann–Beenker | 0 | ✔ | ✔ | ✔ | 8.9×10⁻¹⁶ |
| Ammann–Beenker | 1 | ✔ | ✔ | ✔ | 4.4×10⁻¹⁶ |
| Penrose | 0 | ✔ | ✔ | ✔ | (loop-coverage gap) |
| Penrose | 1 | ✔ | ✔ | ✔ | 1.1×10⁻¹⁵ |

E0b's healing counter-check is automatically satisfied: the merged lift being
single-valued *is* the statement that restoring the line returns all loops to the
floor. (The Penrose j*=0 row is a ring-loop generator coverage gap, not a
construction failure; the topological and edge checks pass. Full per-instance
data in `summary.json`.)

## Interpretation (against the pre-registered outcomes)

- **Not Outcome A:** no quantised bulk holonomy on finite patches.
- **Outcome B, in its strong physical form:** the defect heals — but not because
  "defects are generic," rather because a **simply-connected free-boundary
  domain lets the topological obstruction escape to the boundary.** This is a
  physical statement about the domain topology, exactly as §8-B anticipates, and
  it is the more interesting reading.
- **Not Outcome C:** the nonzero holonomies seen in v1 were construction
  artifacts (identified by the canary signatures and b-independence), not
  evidence of non-exact true transport.

## Required next step (v3 direction)

Repeat the v2 construction on a **periodic approximant / toroidal patch** (perp
space of a quasicrystal is already a torus; the point is to remove the *parallel*
free boundary so the dislocation's obstruction cannot escape). On a torus a
single dislocation cannot be built alone (total Burgers must vanish) → build a
**dipole** and wind loops enclosing one core: prediction `w·b⊥`, now with no
boundary to heal into. This simultaneously realises §4-v2, the §5 E3
additivity/screening tests, and the reverse-loop caveat's non-simply-connected
requirement. That is where the fair test of H1 lives.

## Housekeeping (protocol §9)

1. `directional_balance` mismatch (reverse-loop §Provenance) still to reconcile
   before mechanism-chain claims.
2. Linger pipeline still not committed anywhere.
3. Core-region exclusion radius fixed before measurement (core_pad = 2 edge
   lengths + coordination anomalies + merged-ribbon vertices), logged, not
   adjusted after seeing results.

## Files

`lift_metric.py` (E0 metric), `defect.py` (v1 surgery + artifacts),
`defect_v2.py` (terminating grid-line construction), `run_dh.py` (E0 + v1
diagnostic + v2 E0b), `summary.json`. E1–E5 remain unrun by design until a
non-simply-connected domain makes them a fair test.

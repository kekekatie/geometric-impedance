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

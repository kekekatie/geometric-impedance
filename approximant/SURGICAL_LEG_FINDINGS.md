# Surgical leg — resolved: the memory quantum is topological, not local

**Question (memory paper §7 / defect-holonomy E1-v3.1):** does a *surgical
dislocation core* cut into a seamless approximant carry the registered
perpendicular-space quantum `q_a = π⊥(M_a)` (= 0.1716 on AB 3/2), the way a
torus winding loop does?

**Answer: no — and Theorem 1 says why. The quantum is carried by
non-contractible (winding) topology, never by a local core, on any
ideal-embedding substrate. This resolves the surgical question rather than
leaving it open.**

## The argument (theorem-backed)

The seamless phason-shear approximant is seamless *precisely because* it keeps
**ideal parallel positions** (every edge an exact unit star). But Theorem 1's
proof (`defect_holonomy_test/verify_holonomy_theorem.py`) is arithmetic and
applies to any exact-unit-star, ideal-position tiling:

> For any physically-closed loop, `Σ edge-vectors = 0`, so `π∥(m)=0` for the net
> integer lift `m`; and `ker(π∥) ∩ Z^N = {0}` (Ammann–Beenker) / `Z·(1,1,1,1,1)`
> (Penrose), whose perp image is zero. Hence closed-loop holonomy ≡ 0.

A surgical dislocation is a *local rewiring* — but it leaves positions ideal, so
every Burgers circuit around its core is a **physically-closed, contractible**
loop, and heals by the theorem. A core cannot carry `q_a`.

The only loops that escape the theorem are **non-contractible** ones, where the
loop is *not* physically closed on the plane (`π∥(m) = P_a ≠ 0`) — exactly the
torus winding loops that already hit `q_a` to all digits (the crown jewel,
`defect_holonomy_test/torus_holonomy.py`). Memory lives in the winding, not the
wound.

## Empirical confirmation (both naive cuts fail, for the predicted reasons)

Cutting a dislocation dipole (Burgers ±M_a) into the validated AB 3/2 approximant:

- **Rigid region-shift by the period P_a → heals to 0.** Shifting a region by a
  full lattice period re-registers it onto its own periodic image; no misfit, no
  core. (Holonomy `[0,0]` at every radius; healing counter-check also 0.)
- **Elastic displacement ramp `u=(P_a/2π)θ` → contaminates.** Because `|P_a|≈5.83`
  is large, the ramp distorts edges globally (148 misfit edges); the measured
  "holonomy" is radius-unstable and lands on AB's √2 canary values (2.86, 7.12,
  3.24 = 2+√2…) — misclassification artefacts, not `q_a`. Same signature the
  ideal-QC ramp produced (defect-holonomy iteration 4b).

Neither is a construction bug to iterate away: they are the two faces of the
theorem. On an ideal-embedding substrate there is no local holonomy to find.

## What this means for the programme

- **The surgical question is answered, cleanly:** the perpendicular-space memory
  quantum is a **global / topological** property (winding number around
  non-contractible cycles, i.e. the phason wound around the whole approximant
  torus), **not a local defect-core property.** This is the dynamical/holonomic
  restatement of Theorem 1: *perfection carries no local wake; the wake it does
  carry is topological.* It sharpens, not weakens, the memory taxonomy.
- **To probe genuinely local-core holonomy** one would need a **non-ideal-embedding
  (rationalised-position) crystal**, where `ker(π∥')` is nontrivial so
  contractible loops need not heal. That is a distinct, harder object (the naive
  rationalised projection is degenerate; see defect-holonomy notes). Flagged as
  the remaining open construction — but it is a *different* question, not this one.

## Status of the three unblocked threads

- **Winding Stage-D control:** unblocked and unaffected — Stage D uses the
  approximant *graph* (Kuramoto), which is built and AB-validated; it never
  needed a dislocation.
- **AI-memory §2.1 control:** likewise unblocked — it needs a degree-and-locality-
  matched control graph, which the seamless approximant is (AB-validated).
- **Memory §7 surgical leg:** *resolved* here — the quantum is topological, so the
  §7 "does a surgical core carry it" framing is answered *no*, with the theorem as
  the reason and the torus winding result as the positive carrier. The paper can
  state this directly rather than leaving §7 open.

Reported per house rules: both naive cuts retained as documented negatives; the
canary values (2+√2 family) flagged as artefacts, not findings; no massaging.

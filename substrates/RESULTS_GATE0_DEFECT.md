# Results — Gate 0 of the lifted-Burgers defect audit: can the map carry a defect?

*Runs the sealed `PREREG_lifted_defect.md`, Gate 0 (constructability), with Fable's
knife-1 discipline: a construction failure is told apart from a grammar difference by
the periodic control, and three outcomes are kept distinct. Code: `lifted_defect.py`
(Part 1, the closure instrument) and `lifted_defect_gate0.py` (this gate). Reproduce
the whole chain with `python lifted_defect_gate0.py --N 10`; the individual pieces are
`--square`, `--qcpar --N {8,10,12}`, `--coupled --N {8,10,12}`.*

## Verdict, up front

**Gate 0 is NOT resolved — outcome (b), implementation-limited. It is NOT evidence
that the grammar forbids defects.** Our simple Volterra constructions do not heal into
a legal, localized quasicrystal dislocation, but the reason is a missing elasticity
solve, not an obstruction in the map. Real quasicrystals demonstrably carry
dislocations, so H_none in the strong sense is off the table; we did not earn it and do
not claim it. Along the way we banked **two solid, genuinely new sub-results** (below).
The decision Gate 0 forces is a *methods* decision — whether to build a proper
constructor — not a verdict on the object.

## What we did

Part 1 built the **lifted Burgers closure functional**: each tiling edge is a signed
unit step `e_k` in the parent lattice; the closure of a loop is the sum of those steps,
an element of `Z^m` (m = N/2), split into **b∥** (parallel/elastic) and **b⊥**
(perpendicular/phason). Part 1 validated that it reads *exactly zero* on every loop of
the perfect tilings. Gate 0 asks whether we can build a **legal** rhombus tiling whose
closure is *nonzero* around a localized core, using only the existing tiles and lift.

Faces are the rigorous tool: closure telescopes, so the charge inside any loop is the
sum of the enclosed **per-face** closures, and a clean rhombus face is always zero
(that is exactly the Part-1 topological protection — a pure-rhombus tiling has zero
Burgers charge on *every* loop). A nonzero loop therefore *requires* an enclosed
non-rhombus (defect) face. Legality is judged the hard way: 100 % quadrilateral faces,
no crossings, Euler characteristic 2, as everywhere else in this programme.

We tried three constructions and one periodic control.

| construction | quad faces | Euler | net enclosed charge | reads as |
|---|---|---|---|---|
| perfect tiling (control, no cut) | 100.00 % | 2 | 0 at every radius | clean (instrument sanity) |
| **periodic control** — square lattice, parallel Volterra | 99.23 % | 0 | **b∥ = (±1, 0), radius-invariant** | genuine localized dislocation |
| QC, pure phason (perp-offset) winding | 99.29 % | −18 | kernel dipole, **b∥ = b⊥ = 0** | labels move, matter does not |
| QC, parallel Volterra (b∥ = star vector) | 0.10 % | −578 | fluctuates with radius | whole tiling sheared |
| QC, coupled phonon+phason cut | 0.10 % | −620 | fluctuates with radius | whole tiling sheared |

(Numbers are golden/N=10, extent 12; silver and platinum behave the same way — silver,
which has no kernel at all, produces *no* localized charge under the phason winding,
only holes.)

## Sub-result 1 — the instrument reads a real Burgers vector (periodic control)

On a square lattice the identical parallel Volterra cut **heals**, because the Burgers
vector is a lattice period: across the branch cut the columns re-register and only a
terminating half-column — the dislocation core — survives. The closure functional then
reads **b∥ = (±1, 0), constant across every enclosing loop from R ≈ 4 to R ≈ 20.**
Radius-invariance is the defining signature of a genuine localized topological charge,
and this is the first time the instrument has been checked on a *nonzero* reading (Part
1 only checked the zero). It passes: when a legal localized dislocation exists, the
functional reports its Burgers vector correctly and stably. The periodic **grammar**
plainly admits such an object.

## Sub-result 2 — the phason offset moves labels, not matter

A pure **perpendicular** (phason-offset) winding on the quasicrystal produces closure
that is **purely a kernel element** — on golden, `B = ±[1,-1,1,-1,1] = ±Φ₁₀`, the
kernel generator, for which **b∥ = 0 and b⊥ = 0 identically.** Where there is no kernel
(silver, K = 0) the same winding produces **no localized charge at all**, only a seam
of holes. And the kernel charge is not even an isolated monopole: it appears as a **±
dipole strung along the branch cut** (the innermost disk catches one sign, larger disks
catch the cancelling partner, netting zero).

The structural reason is clean and worth stating as a finding: **winding the acceptance
window can only wind the discrete congruence label, which lives in the kernel and has
zero parallel- and perpendicular-space footprint.** A phason-offset field relabels
congruence classes; it cannot manufacture a physical Burgers vector, because a physical
Burgers vector requires the *positions* to wind, and offset-winding never touches them.
This dovetails with the earlier `check_z2.py` null (the congruence class is real but not
conserved under flips): the congruence/phason degree of freedom is genuine bookkeeping,
but it is *physically null* as a transportable charge — possibility ≠ preference,
relabelling ≠ displacement.

## Sub-result 3 — the quasicrystal resists the naive Volterra cut, for a known reason

A **parallel** Volterra cut by a star vector (and even a **coupled** phonon+phason cut
built from a single lattice vector B) shears the *entire* quasiperiodic tiling into a
non-tiling (≈ 0 % rhombi, wildly non-2 Euler, radius-dependent charge). The cause is
definite: the bare winding field `(b/2π)·θ` applies an O(1) shear *everywhere*, and on
the quasiperiodic point set there is **no period** for it to re-register against — so
nothing heals. On the square lattice it healed only because b∥ *is* a period there.

This is exactly Fable's "boring reason" for failure. A real dislocation's displacement
field is the multivalued winding **plus** a single-valued **elastic relaxation** whose
strain decays as 1/r; that relaxation is what localizes the mismatch to a core. We did
not implement it. So the QC failure is a missing elasticity solve, **not** a grammar
obstruction — precisely the (a)-vs-(b) ambiguity the control was built to resolve, and
it resolves to (b).

## Hypotheses — where this leaves the pre-registered credences

- **H_none** (no legal defect constructible in the grammar): **not earned, not claimed.**
  The periodic control shows the machinery and instrument work; the QC failure is
  implementation-limited. The pre-reg's 0.30 prior on H_none should, if anything, fall.
- **H_object / H_generic** (a genuine flip-mobile conserved defect, quasiperiodic or
  generic): **untested** — they require a legal construction we do not yet have.
- New, off-menu finding (sub-result 2): the phason/congruence charge is **real but
  physically null** — a localized kernel holonomy with b∥ = b⊥ = 0. It is not the
  "object made of map" the audit was hunting (no physical or phason content, and it
  arrives as a cut-strung dipole, not an isolated core), but it is a clean statement
  about what the phason degree of freedom *is*.

## The decision Gate 0 forces (for the crew)

To turn Gate 0 into a real (a)-vs-(c) answer we need a constructor that produces a
*legal* isolated QC dislocation. Two honest routes, both real work, neither a butterfly:

1. **Coupled phonon–phason elasticity solve.** Add the single-valued relaxation field
   (minimise the discrete elastic + phason energy with the winding as a boundary
   condition) so the strain decays and the mismatch localizes. This is the physically
   faithful route and connects directly to the parked energetic branch (report Exp. 1).
2. **De Bruijn multigrid constructor.** Build the tiling as the dual of N line-grids and
   terminate a single grid line in the interior — a *combinatorial* dislocation that is
   all-rhombi by construction and needs no elasticity. Cleaner topologically, but a new
   generator (~a few hundred lines) sitting beside `generate_rank4.py`.

Recommendation: **bank sub-results 1 and 2, and do not spend the elasticity/multigrid
build unless the crew wants the defect object specifically.** The audit's exciting
target (a conserved identity that persists while its embodiment changes) is still worth
chasing, but it is a substantial constructor project, and the transport-hierarchy test
is the nearer, cheaper rung and is nearly ready to seal. Sub-result 2 already delivers a
publishable clarification for free: in this representation the phason field is a
relabelling, not a carrier.

## Files

`lifted_defect.py` (Part-1 instrument, validated zero) · `lifted_defect_gate0.py` (this
gate: `construct`, `geom_edges`, `face_charges`, `square_control`, `qc_parallel`,
`coupled_volterra`) · sealed plan `PREREG_lifted_defect.md`.

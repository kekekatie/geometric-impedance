# Leads register

Everything this project has chased, with a status. Kept in the repository rather
than in any conversation, so it survives model deprecations, lost chat histories
and the several-day gaps in which details evaporate.

**How to use it.** Add a lead the moment it appears, even half-formed, with
whatever name you have. A lead written down as *untested* is worth more than a
model's recollection of having confirmed it — the track record of testimony in
this project is poor, and every claim that "checked out" in conversation and was
later run against a null has needed correcting. Nothing moves to CONFIRMED
without a null beside it.

Status values: **UNTESTED** · **RUNNING** · **UNDETERMINED** · **CONFIRMED** ·
**WITHDRAWN**

---

## CONFIRMED

### Address-channel fragility under phason disorder
Both Ammann-Beenker and Penrose have near-perfect perpendicular-space address
channels in clean bulk (0.9996 / 0.9816). Under phason disorder they separate
immediately: at amplitude 0.05 AB loses 0.0067 and Penrose loses 0.1291. The
distinction is about **fragility, not presence**.
Survived: nonlinear model, matched positive rate, matched scale, bulk crop,
shuffle null, replication across seeds.
→ `substrates/PHASON_DOSE_RESPONSE.md`

---

## UNDETERMINED

### Fragility vs perpendicular-space dimension
Perpendicular dimension 2 is far more robust than 3 or 4 (at disorder 0.10 it has
lost 0.005 against 0.250 and 0.197). But there is **no monotone scaling** — 3
collapses as fast as 4. Reads as a cliff at dimension 2, not a gradient.
Blocked on: the jitter is isotropic in perpendicular space, whose dimension is
the variable under test, so equal amplitude may not mean equal damage. Needs
replotting against measured damage.
→ `substrates/PERP_DIMENSION.md`, `substrates/calibrate_damage.py`

---

## UNTESTED

### Devil's staircase / threshold structure in the fragility curve
The perp-2 curve is flat within noise from disorder 0.00 to 0.10 (0.979, 0.983,
0.974) and then falls sharply. That is a plateau-then-collapse shape, not a
decay — consistent with a **pinning threshold**. Adjacent literature: devil's
staircase, Arnold tongues, the Aubry transition, stickiness in Hamiltonian
systems.
Next step: fine-grained disorder sweep between 0.05 and 0.25 on perp 2. A
threshold has a *location*, which is a number that can be predicted and checked;
a decay curve is what everything does.
*(Recalled from a pre-travel conversation as "sticky steps".)*

### Phase-randomised surrogate for the localisation result
The only null that could support a quasiperiodicity claim: a surrogate field with
the same spatial power spectrum but randomised phases, holding two-point
correlation fixed and varying only higher-order structure. Needs interpolation to
a grid and back, as the field lives on an irregular point set.
→ `substrates/LOCALISATION_MECHANISM.md`

### Why Penrose is more boundary-sensitive
AB reaches bulk behaviour after trimming 25% of the patch; Penrose needs ~50%.
Obvious suspect: Penrose's acceptance region is four pentagons indexed by lift
sum, against AB's single octagon. Hypothesis only, unmeasured.
→ `substrates/BOUNDARY_SENSITIVITY.md`

### E8 and the Elser-Sloane quasicrystal
E8 arrived as recognition, not derivation, and the substrates tested so far come
from Z⁴ and Z⁵ — neither is E8-derived. The Elser-Sloane quasicrystal is a
genuine E8 → 4D cut-and-project and could be built with the same machinery.
Open question first: does the framework *need* E8, or did it show up because any
search for deep structure with good packing properties returns it?

### Cross-check the matched-rate label
Every current result uses one privileged-site definition (top 3–5% by
rank-averaged retention). Needs at least one independent definition before any of
it is quotable.

---

## WITHDRAWN

### Quasiperiodic order resists localisation
A smooth radial ramp resists localisation *more* than the perpendicular field,
and a long-wavelength periodic field more still. The driver is spatial
correlation length, not quasiperiodic order. The measurement stands; the
interpretation does not. → `substrates/LOCALISATION_MECHANISM.md`

### Exo/endo as presence — "Penrose has no address channel"
Boundary contamination at the interior-75% crop. In bulk Penrose reads its own
addresses at 0.98. Anything depending on Penrose *lacking* perpendicular-space
addressability needs withdrawing. → `substrates/BOUNDARY_SENSITIVITY.md`

### §5.4 fresh reconstruction (Silent Corruption v3)
Reproduces at ~0.90 on a graph with no geometry at all; falls to chance when
degree-family features are ablated. The label was a relabelling of a feature fed
to the classifier. → `substrates/NULL_AUDIT_FINDINGS.md`

### Toy-model floor and ceiling claims
Floor: the Penrose patch is a disc and the square lattice is a square, and the
metric penalises corners — the static shape gap alone reproduces the reported
effect. Ceiling: a plain periodic lattice shows the same memory benefit and the
same collapse under rewiring, so it is spatial locality, not aperiodicity.
→ `toy_model/review/`

### AB under strong disorder ≈ Penrose at rest
Single-seed noise at ~5,400 vertices. At proper scale AB at amplitude 0.40 sits
above Penrose's best value anywhere. → `substrates/PHASON_DOSE_RESPONSE.md`

---

## Outstanding obligations

- **Zenodo.** The published papers still carry the withdrawn claims above.
  Silent Corruption v3 needs §5.4 removed and the Penrose weave/hybrid figures
  requalified; both toy-model papers need their headline claims narrowed.

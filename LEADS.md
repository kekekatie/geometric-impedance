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

### Address fragility follows the cyclotomic field — PROSPECTIVE
At matched perpendicular dimension, lattice rank, window construction and edge
rule, address fragility orders **silver > platinum > golden** at every damage
level (0.976 / 0.920 / 0.842 at 10% damage).

Prediction recorded in git before the run: 10-fold fragile, 8-fold robust.
Confirmed. The 10-fold substrate shares nothing with Penrose but its field —
different lattice, window, perpendicular dimension and edge structure — so
golden-ratio arithmetic reproduces Penrose's fragility independently of
construction.

**The family is complete, not sampled**: φ(N)=4 has solutions N = 5, 8, 10, 12,
and N=5 and N=10 give the same field, so there are exactly three quasicrystal
families at perpendicular dimension 2 and all three are measured.
→ `substrates/CYCLOTOMIC_RESULT.md`

---

## UNDETERMINED

### Fragility vs perpendicular-space dimension
Perpendicular dimension 2 is far more robust than 3 or 4. The damage calibration
is **done**: dimension 4 sustains 1.55–1.75× dimension 2's flipped-vertex
fraction at equal amplitude, and replotting against measured damage leaves
dimension 2 ahead by +0.09 to +0.21 throughout. There is **no monotone scaling** —
3 and 4 cross over. Reads as a cliff at dimension 2, not a gradient.
→ `substrates/PERP_DIMENSION.md`, `substrates/calibrate_damage.py`

### ⚠ The n = 1 problem underneath both "cliff" results
Two independent measurements have come out as *one special case and everything
else*: a cliff at perpendicular dimension 2, and a cliff at Penrose. It is
tempting to read that as a shared structure in the world. But **we have exactly
one substrate at perpendicular dimension 2, and exactly one fragmented-window
substrate.** Both cliffs rest on a single point at the special value, so the
pattern may be describing our sampling rather than the substrates.

Next step before any mechanism is built on it: generate *siblings* — more
perpendicular-dimension-2 substrates (different Z⁴ windows, different
parallel-plane slopes) and more fragmented-window substrates at various
dimensions. If AB's robustness is a property of dimension 2, its siblings share
it. If it is a property of Ammann-Beenker specifically, they do not. At present
these cannot be told apart.

*Related framing note:* bimodality is not evidence for binary ontology — it is one
of the commonest shapes in nature and arises from dozens of unrelated mechanisms.
The better-posed question is whether this is a **phase transition**, which brings
order parameters, critical exponents and finite-size scaling, all of which
produce checkable numbers.

---

## UNTESTED

### ⚠ Window scale is NOT a free parameter — it breaks the tiling
Discovered while trying to fragment the window. Cut-and-project window size is
pinned by the tiling requirement: the tile-edge rule needs both endpoints of a
lattice step accepted, so shrinking the window deletes edges wholesale. Mean
degree falls 3.95 → 3.28 → 2.39 at scales 1.00 → 0.85 → 0.70, with half the
vertices below degree 3 at 0.70. Inflating is not neutral either (4.46 and 4.86
at 1.15 and 1.30).

**This invalidated the granularity family regression**, which used those scales.
Any future substrate family must verify mean degree before use. Candidate dials
that may be legitimate: parallel-plane slope, lattice choice, window *shape* at
fixed measure.

### Partition granularity as the fragility mechanism — back to UNTESTED
Neighbour purity orders four hand-picked substrates correctly (AB +0.423,
Z5 +0.348, Z6 +0.268, Penrose −0.062) under two class definitions. The
twelve-substrate test that appeared to kill it was malformed — see above — so the
candidate is neither supported nor refuted. Needs a valid family.
→ `substrates/GRANULARITY_TEST.md`

### Discrete address component — REFUTED
Penrose's lift-sum index carries almost no address information: AUC 0.5398 at
zero disorder against a chance baseline, rising only to 0.5696 at disorder 0.20.
It neither carries the signal nor collapses. Penrose's readability is entirely in
its continuous perpendicular coordinates (0.9517 → 0.6726 across the same range),
and those are what degrade. The four pentagons are irrelevant to readability.
→ `substrates/discrete_vs_continuous.py`

**What this eliminates.** Penrose lifts Z⁵ into 2 parallel + 3 perpendicular, and
the third perpendicular direction *is* the lift-sum direction, now shown inert.
So Penrose's live address space is 2-dimensional, and so is Ammann-Beenker's.
Both have a two-dimensional continuous address and Penrose's degrades four times
faster.

Ruled out to date: presence of an address channel, model class, positive rate,
boundary crop, window fragmentation, a discrete component, and the dimensionality
of the continuous part.

**What remains:** the shape of the window in that 2D slice (pentagon vs octagon),
and the arithmetic behind it (golden vs silver ratio). Both are properties of the
same 2D object rather than of the ambient construction.

### Lattice-commensurate window fragmentation
Arbitrary fragmentation (parallel slabs cut through the window) also destroys the
tiling — every fragmented variant tested came out with mean degree below 3.2.

But **Penrose's window is already disconnected**, as four pentagons indexed by
lift sum. That fragmentation is special: lift sum is a lattice invariant, every
lattice point has a definite integer value of it, so no point falls "between"
pieces and no edges are destroyed. Arbitrary slabs cut across the lattice
structure; Penrose's cut along it.

Hypothesis worth testing: it is not fragmentation as such that matters but that
Penrose's address carries a **discrete component** (which pentagon) alongside a
continuous one, and the discrete part degrades differently under jitter. Testable
by building substrates whose windows are fragmented by other lattice invariants,
or by measuring the discrete and continuous address components separately.

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

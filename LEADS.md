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

## Where we are — 2026-08-26 (breadcrumb for a lost-tomorrow Karen)

The wave arc is now largely *done and consolidated* — see the new **Part II of
`SYNTHESIS.md`**. In one line: a coherent law reads golden's address (four controls); the
mechanism is the wave's **stationary spectral structure**, not dynamical interference
("shape-memory", not "journey-memory"); and it shows up physically as same-vertex-type,
different-address → different confined-state role. The border wall from Part I *holds at the
mechanism level*: static geometry, read by static standing structure.

- **Landed & written up (Part II):** defect Gate-0 (no cheap endogenous object; multigrid
  asset) · transport positive (`RESULTS_TRANSPORT.md`) · coherence-ladder mechanism
  (`RESULTS_COHERENCE.md`) · address-made-physical + refinement (`RESULTS_CONFINED*.md`).
- **Open / candidate next steps (deliberate choice, not reflex):**
  1. the full **Haken–Strobl γ death-curve** — does address-reading fade smoothly or collapse
     at a threshold as standing structure is dismantled? (home of the "compounding" intuition);
  2. the **class-specific preferred-depth** rule — why does each vertex type prefer its own
     internal-space depth? does it relate to the type's own window geometry?
  3. sharpen the **silver/platinum** partial-address attribution (M4 orthogonalized vs M3).
- **Superseded from the last breadcrumb:** "memory reads memory / dephasing sweep next" — the
  cheap coherence ladder already answered the conceptual question, reframing it to
  shape-memory; the expensive sweep is now optional, for the curve shape only.

If you come back unsure where we left off: we had a *very* good couple of days. The scent we
chased ("why can coherent dynamics read it?") has been caught and consolidated.

---

### Address ablation — the carrier is the VARIANCE, not the mean (2026-09-02, EXPLORATORY)
Group-by-group ablation of the M4 address block on the sealed transport pipeline: what a coherent law reads is the multiscale *within-neighbourhood variance* of the perp coordinate (var-alone recovers 95/99/80% of the golden/silver/platinum increment; the shell-*mean* adds ≈0 everywhere), with the incoherent null flat — ROADMAP step 5, interpretive not sealed. → `substrates/RESULTS_ABLATION.md`, `substrates/ablation_run.py`

---

### (earlier breadcrumb, 2026-08-25 — kept for the record)

Two things just landed, and one shiny scent is pulling us forward.

- **Just landed (banked, committed, pushed):**
  1. *Defect audit (Gate 0)* — a clean negative, sharpened: no cheap endogenous
     Burgers-charged object falls out of the clean map (proved three ways; the key wall
     is "single-valued lift ⇒ zero closure by construction"). Bonus asset: a validated
     **multigrid** second generator. → `RESULTS_GATE0_DEFECT.md`, `multigrid.py`.
  2. *Transport hierarchy (sealed, then run)* — the programme's **first strong positive**:
     a coherent wave READS the perpendicular-space address, cleanly on **golden**
     (increment killed by the stratified shuffle, survives the position control), partly
     on silver/platinum; the incoherent random walk reads nothing. → `RESULTS_TRANSPORT.md`,
     `transport_run.py`, `transport_result.png`.

- **The scent we were chasing when Karen had to go — "MEMORY READS MEMORY":**
  Every *memoryless* process came back null (flips, damage-diffusion, random walk). The one
  process that read the address is the one that keeps its **phase** — and phase is memory
  that **accrues** as the wave moves (Karen's word: *accruement*). Candidate penny-drop:
  *the aperiodic geometry is a memory that only another memory can read.* Ties straight back
  to the founding image (the irrational way memory moves forward).

- **The decisive cheap experiment to chase that why (next up):** a **coherence/dephasing
  sweep** — dial the quantum walk from fully coherent toward the memoryless random walk and
  watch the M4 address-reading signal. If it dies *in step with* coherence → "memory reads
  memory" caught red-handed. If it dies faster/slower/clings → a different, better why.

- **Two one-afternoon looks also open:** (a) plot where the E≈0 **confined states** sit
  against the address field — they may *be* the address made physical (would explain why
  E≈0 beat the mid-band, against Claude's prediction); (b) test whether golden's clean
  readout is about the golden ratio being the *most irrational* (why golden separates
  address from ordinary structure while silver/platinum blur).

- **Deliberately NOT doing yet:** forcing a paper. The effects are real; we want the *why*
  first. (Gemini thinks we'd have 5 papers by now — the optimist has a place, but the whys
  are what make the paper worth writing.)

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

### Quasiperiodicity governs static structure, not free dynamics — CONFIRMED (null → H1a)
Three independent energy-free phason-dynamics probes return one verdict: the
quasiperiodic substrates show nothing special under free dynamics.
- **Branch A** — structural loss per flip is family-independent, monotone, no
  spontaneous recovery.
- **History** — unbiased mobility erases spatial history within ~0.06 flips/vertex,
  alike across all three fields.
  Both → `substrates/RECOVERY_UNBIASED.md`
- **Intrinsic drift** — deeper *local* continuation volume does carry structure beyond
  immediate degree (real, robust across radius R in the bulk, grows with horizon), **but
  it is not quasiperiodic-specific**: a 5-seed matched-scramble control finds it equal or
  *lower* near the QC than in the random-tiling bulk (near-QC minus saturated: silver
  −0.026±.006, golden −0.036±.025, platinum −0.002±.021). H1a, generic rhombus-tiling
  combinatorics. The platinum/family ordering is retired as finite-size/small-scale noise.
  → `substrates/RESULTS_INTRINSIC_DRIFT.md`, sealed `PREREG_intrinsic_drift.md`

Cross-validates the Stage D metronome null: **the geometry reaches into static structure
and memory-in-the-pattern, not into the free dynamics** — a border now drawn from two
independent directions. Branch B (imposed energetics) abandoned without remorse.

---

## UNDETERMINED

### ⚠ Address fragility follows the cyclotomic field — MOVED DOWN FROM CONFIRMED
The measurement stands: on the substrates as built, address fragility orders
**silver > platinum > golden** at every damage level (0.976 / 0.920 / 0.842 at 10%
damage), with the direction recorded in git before the run.

**The causal claim does not stand.** The edge rule "differ by one basis vector" is
identical in Z⁴ coordinates and *not* identical in the plane: it gives the complete
octagonal star for N=8 (because ζ₈⁴ = −1), 4 of 5 decagonal directions for N=10, and
4 of 6 dodecagonal directions for N=12. As a result the 10-fold substrate is **not a
tiling at all** — 664 properly crossing edges, Euler characteristic −682 — while the
8- and 12-fold substrates are perfect rhombus tilings.

Star completeness and planarity therefore vary monotonically with the outcome, so
"only the cyclotomic field changes" is false as built, and the field cannot be
isolated by this design. Ammann-Beenker got a complete star by luck of the minimal
polynomial, not by matched construction.
→ `substrates/TILING_CONFOUND.md`, `substrates/tile_audit.py`

*Route out:* the Z^n family (`generate_nfold.py`) tiles properly at all three folds —
zero crossings, 100% quadrilaterals, Euler 2 — but varies perpendicular dimension.
Except Penrose's extra dimension is already measured **inert**. If Z⁶'s two grading
dimensions are also inert, that family is matched at 2 *continuous* address dimensions
and is strictly better on every axis. Gate test is cheap; see UNTESTED.

**⚠ `address_fragility.md` v2.0 §6.2 asserts the false clause. Do not upload.**

### Experimental literature check — the matched experiment does not exist
A deep-research survey of experimental phason literature through Aug 2026 returns
**underdetermined, not positive and not negative**. There is no matched 8-/10-/12-fold
dataset in which the same calibrated damage is applied to comparable specimens, so
the ordering silver > platinum > golden cannot currently be tested against experiment.
No directly calibrated phason elastic constants exist for any of the three target
families; the only absolute determination is icosahedral Al–Pd–Mn.

**Spot-checked against primary sources** (3 of ~25 citations; all real journals, two
verbatim-accurate, one directionally accurate with unverified specifics). The survey
reads abstracts, not full texts, and says so.

**The awkward observation.** The ten-fold/golden family carries by far the strongest
direct evidence of phason-mediated *self-repair*: imaged thermal phason flips in
Al–Cu–Co; growth errors repairing in ~1 s at 1183 K and 10–20 s at 1123 K; grain
coalescence; defect-free growth around shrinkage pores (PRL 135, 166203, 2025). Taken
at face value that is hard to square with "golden is least resilient".

**Why it is not yet a refutation.** (a) Al–Ni–Co decagonal is *the* workhorse 2D
quasicrystal — there is no octagonal single crystal of comparable quality to run these
experiments on, so "golden has the most repair evidence" is close to "golden has the
most evidence"; (b) the measured quantities are different — we measure immediate
address readability under static perpendicular-space jitter, the experiments measure
kinetic recovery, and stiffness, mobility and healing are not the same axis.

**The defence in (a) is available once.** It makes a prediction: if matched 8- and
12-fold repair experiments are done and golden still wins on repair, the resilience
reading is wrong — though the address-readability result could still stand, being a
different quantity. That is the honest position and it should be stated in the paper.

**Calibration anchor gained.** Real octagonal quasicrystals carry ~5% local tiling
error (Ammann-line jags, Mn₈₀Si₁₅Al₅). Our damage axis is flipped-vertex fraction,
quoted at 10%. Not the same quantity, but the first time the x-axis has touched a
measured number.
→ `substrates/LITERATURE_CHECK.md`

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

### ⭐ Headline re-run — DISCRIMINATING TEST VOID, silver > golden reconfirmed
Ran to the pre-registered protocol. Ordering came out silver > golden > platinum at
every damage level, which is H2's ordering, but **it cannot be claimed for H2**:
platinum failed the pre-registered clean-channel check (0.6658 against a predicted
≥0.95) and never had a channel to lose. H2's quantitative refinement also failed — the
golden-to-platinum gap should have been about half the silver-to-golden gap and was
2.0–2.4× larger at low damage, a case the prediction document names as fitting neither
hypothesis.

**Diagnosed, and the fault is the generator's extra offset, not the 12-fold substrate.**
`class_inertness.py` shows singular Penrose's class inert at 0.5210 — vindicating
`discrete_vs_continuous.py`'s 0.5398, which does *not* need correcting — while the
generic members read 0.8230 and 0.6619. The generic offset slices the zonotope at
arbitrary levels, producing near-degenerate slivers (52 points in one 10-fold class) and
class mean degrees from 3.49 to 4.84. Class then predicts degree, degree predicts
retention. With the class included, platinum reads 0.8579, not 0.6658 — its address is
largely discrete and the pre-registered feature set was chosen on silver, which has no
class at all.

**`RANK4_FAMILY.md`'s "generic is the better default" claim is withdrawn.** The fix is a
deterministic half-open window rule, not a jitter that moves the cut. Class occupancy and
per-class degree homogeneity become substrate acceptance criteria, checked before any
address measurement.

**Survives untouched:** silver > golden at matched damage on audited tilings — 0.98 vs
0.88 at 5% damage, 0.96 vs 0.84 at 10%, holding to 0.92 vs 0.66 at 25%. Silver has one
class and no extra offset, so its substrate is unaffected.
→ `substrates/RANK4_HEADLINE.md`, `rank4_headline.py`, `class_inertness.py`

### ⭐ Rank-4 congruence-window family — BUILT AND VALIDATED
All three members are genuine rhombus tilings at rank 4, perpendicular dimension 2,
with the complete N-fold star: zero crossings, 100% quadrilaterals, Euler 2, rhombus
vocabularies 2/2/3, mean degrees 3.907/3.795/3.733. Congruence classes 1, 5, 9 =
det Gram(K), all occupied.

**Validated against Penrose exactly.** Inside a radius both patches cover: 872 points
each, 0 differing either way; 1677 edges each, 0 differing. Penrose was always a
rank-4, perpendicular-dimension-2 cut-and-project — the fifth dimension is bookkeeping.

Two bugs found and fixed en route: the zonotope's extent along each extra direction
*exactly* equals the preimage spacing (ratio 1.0000), so a closed unoffset window
double-accepts boundary points; and a rank-4 step by ζ^k is not sufficient for an edge,
since accepted preimages may differ by e_k *plus a kernel element* — without that check
12-fold carried mean degree 4.736, impossible for a quadrangulation.

**⚠ Field and fragmentation remain perfectly confounded**: 1, 5, 9 pieces map
one-to-one onto silver, golden, platinum. This family cannot separate them either, and
φ(N)=4 has exactly three members so it cannot supply a case where they disagree.
Recorded now rather than discovered later.
→ `substrates/RANK4_FAMILY.md`, `generate_rank4.py`, `validate_rank4_penrose.py`

*Original reasoning, kept for the record:*

### Rank-4 congruence-window family — the construction that is matched on all axes
**Built on a gate that failed.** Perpendicular space splits into the Galois-conjugate
plane plus a non-primitive remainder (dimension 0, 1, 2 for 8-, 10-, 12-fold). The
remainder is **not inert**: AUC 0.7937 (10-fold) and 0.6169 (12-fold) at zero disorder
against a shuffle null near 0.49, and it improves the joint model. So the Z^n family's
perpendicular dimension differs in substance, and neither existing family is clean —
Z⁴ matches dimension but breaks the tiling, Z^n tiles but varies dimension.
→ `substrates/GALOIS_BLOCK_RESULT.md`, `substrates/galois_block_test.py`

*(No contradiction with `discrete_vs_continuous.py`, which showed the **discrete**
lift-sum index inert while grouping all continuous coordinates together. The third
**continuous** coordinate is the live one. Both stand.)*

**The third construction fails on neither.** Penrose is already a rank-4,
perpendicular-dimension-2 cut-and-project: the kernel of Z⁵ → Z[ζ₅] is generated by
(1,1,1,1,1) with lift sum 5, so lift sum *mod 5* is well defined on the rank-4 module
and the four pentagons are a **congruence class of the Z⁴ point**, not an extra
dimension. Verified: on 5,192 vertices the lift sum takes exactly {1,2,3,4} and equals
its own residue mod 5.

Generalises: Z[ζ_N] is rank 4 for N = 8, 10, 12; the star has N/2 directions; the
relation lattice has rank N/2 − 4 = 0, 1, 2. The window is a union of pieces indexed by
the resulting congruence group — **1 piece for 8-fold, 5 for 10-fold, TBD for 12-fold.**

Matched on all four axes at once: rank 4 and perpendicular dimension 2; complete
N-fold star (basis-independent edge rule); genuine rhombus tilings; windows differing
only in congruence structure. And the **number of window pieces becomes a mechanism
variable forced by the arithmetic** rather than imposed — which is the
lattice-commensurate fragmentation lead below, arriving on its own.

Order: (1) build it, validating by reproducing `generate_penrose.py` exactly; (2) find
the 12-fold congruence group; (3) audit star/crossings/faces/Euler/degree; (4) re-run
the headline with the direction recorded in git first; (5) then recovery.

### Recovery / annealing as a separate axis from immediate loss
Every result to date measures *immediate* address loss under static disorder. The
physics literature insists this is only one axis: a substrate can be stiff but
kinetically frozen, or soft but highly mobile and therefore fast to repair. The
experimental repair evidence for decagonal alloys is strong precisely on the axis we
have never measured.

**The jitter generator cannot answer this.** It regenerates from scratch at each
disorder amplitude — no dynamics, no history, no memory. Turning the jitter back down
recovers exactly, because there is nothing to anneal; the "recovery curve" would be the
dose-response curve read backwards. It would look like a result and be an artefact.

**Flip machinery now built and validated** — `substrates/phason_flips.py`. A simpleton
flip is the elementary phason move: three rhombi meeting at a degree-3 vertex fill a
hexagon that admits exactly two tilings, and exchanging them sends the interior vertex
to the opposite corner. Exact in lift coordinates: v → v + s_a e_a + s_b e_b + s_c e_c.
On the 8-fold patch, 435 flippable sites (37.7% of vertices); 40 flips leave vertices,
edges, crossings (0), quadrilateral fraction (100%), Euler (2) and rhombus vocabulary
all unchanged.

**This also fixes the calibration criticism.** Damage becomes a *count of flips* rather
than an uncalibrated jitter amplitude — directly comparable to experimental defect
densities such as the ~5% octagonal tiling-error figure. Worth adopting even if
recovery turns out null.

Still needed: the relaxation rule. It is a modelling decision that will drive the
answer, so it must be fixed and justified in git before running. Note the physics is
genuinely open — under unbiased flips a random tiling has no restoring force at all, so
whether recovery happens depends on whether the tiling is energy- or entropy-stabilised.
Both branches are informative and both should be run.

**⚠ Designed-in leak to avoid.** The obvious repair rule — re-test each vertex against
the true window using its neighbours' consensus perpendicular position — is the same
operation as the address classifier. Annealing with the address channel and then
measuring the address channel rebuilds the §5.4 leak in a new costume. The relaxation
rule must use only parallel-space/tiling-local information.

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

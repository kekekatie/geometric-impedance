# Design note (v9) — substrate comparison: design & feasibility only

*Register: speculative exploration; not a confirmatory study, not cosmology.
**Design and feasibility only — no new scientific simulations were run.** Chain
v1 `cc514ee` → … → v8 `55ba85e`. Isolated under
`exploratory/accretion_pilot/v9_substrate_design/`. v1–v8 preserved; a dated wording
correction is appended to `../v8_neutral_weights/REPORT_v8.md`. No merging,
publishing, or sealed-study access. Only the exploratory accretion-pilot code was
inspected; no tiling generators or data from the sealed studies were opened or
will be reused — the pilot ships its own self-contained geometry.*

Requested by Astra (Katie has authorised Astra to steer routine steps here). This
document is for Astra's review **before** any pilot is run.

## Central question

Does quasiperiodic spatial organisation change the persistence of history-readable
footprints under local reinforcement and connection growth, compared with suitable
periodic and disordered substrates? **We do not assume quasiperiodicity helps.**

## What the existing engine already gives us (feasibility ground truth)

The v2 `World` engine cleanly separates **substrate** from **dynamics**:

- **Graph-general, reusable unchanged:** the weighted walk (`weighted_step`),
  reinforcement (`w ← w + 0.5(6−w)`), diagonal activation (`_activate`), and every
  opportunity/capacity readout (`structural_access`, `effective_alternatives`,
  `frac_inactive`, `headroom`, `frac_saturated`) — all operate only on an adjacency
  map and a weight dict.
- **Substrate-specific, must be generalised:** graph construction (currently
  grid-hardcoded), the growth trigger's face lookup (`edge→faces`,
  `face→candidate-diagonals`, `face→bounding-edges`), and the reader's sign function
  (currently the transpose contrast `sign(col−row)`).

So a substrate-agnostic refactor needs only to supply, per substrate: a vertex set
with positions, an edge list (originals), a face list with each face's bounding
edges and its candidate diagonals, an `edge→incident-faces` map, and a frozen
reader-sign per edge. **Everything dynamical is reused.** This is a bounded,
low-risk refactor (the engine was written this way).

## 1. Substrate choice (and why rhombus tilings)

Every face-based growth rule needs faces with well-defined **bounding edges** and
**candidate diagonals**. **Rhombus tilings are the natural common language:** every
face is a rhombus (4 vertices, 4 bounding edges, exactly 2 diagonals) — structurally
identical to the square model's unit cell, so the v1–v8 rule transfers *verbatim*
(2 candidate diagonals per face; activate when the face's 4 bounding edges have
accumulated wear ≥ θ).

Recommended families, all expressible through **one de Bruijn multigrid generator**
(N=5 line families at regular 72° orientations; the dual of the line arrangement is
a rhombus tiling using the same **two Penrose rhombi**, thick 72° and thin 36°, all
of unit edge length):

- **Quasiperiodic — Penrose P3:** regular line spacings, generic offsets.
- **Disordered — jittered pentagrid:** *randomised line positions* within each of
  the 5 families (same 5 orientations ⇒ **same two rhombi**), which destroys
  long-range order while keeping the tile set. This is a **genuinely feasible**
  matched disordered control: because the rhombus *shapes* are fixed by the pairwise
  orientation angles (unchanged) and only the *arrangement* is disordered.
- **Periodic — rational (Fibonacci) approximant:** a periodic supercell built from
  the same two rhombi (a standard Penrose approximant). **Feasible but more work**:
  it needs an approximant construction and gap-free/edge-matching validation across
  the periodic seam.

Using one generator for all arms guarantees a **shared mechanism** and matches the
**local tile set** by construction, so the families differ (as far as possible) only
in long-range organisation — the cleanest separation of "higher-order organisation"
from "local geometry". Ammann–Beenker (8-fold, square+rhombus) is a viable
alternative quasiperiodic family but mixes two face *types*; Penrose P3 keeps a
single face type (rhombus) and is recommended.

**Recommendation (smallest informative comparison):** the **two-family core —
Penrose (quasiperiodic) vs jittered (disordered)** — is the minimal comparison that
is *both* clean and cheap, because both arms come from the same generator differing
only in line-position regularity (tile set, edge length, per-face candidate count
all matched by construction). The **periodic approximant is the scientifically
central third arm** (quasiperiodic-vs-periodic is the sharpest "does quasiperiodicity
matter" contrast), and I recommend **including it if and only if its construction
passes the validation gates within the pilot budget**; otherwise run the two-family
core and defer periodic to a clearly-scoped v10. See `RECOMMENDED_PILOT.md`.

*Limitation:* a disorder arm requires **averaging over several random patches**
(each jittered patch is a different graph), adding between-patch variance the ordered
arms do not have; budget for a small fixed set of patches, not a sweep.

## 2. Translating the rule explicitly (all substrates)

- **Original edge:** a tiling edge (rhombus side), shared by ≤2 faces; initial
  weight `w0 = 1`.
- **Candidate added connection:** the **2 diagonals of each rhombus face**,
  initially absent, activated weight `1`.
- **Local activation trigger:** for a face, activate its diagonal(s) when
  `Σ(w_e − w0)` over the face's **4 bounding edges** ≥ θ — combinatorially identical
  to v1–v8.
- **Traversal:** the walker moves to a neighbour along a **present** edge with
  probability ∝ edge weight — identical to v1–v8.
- **Different diagonal lengths:** thick/thin rhombi (and their short/long diagonals)
  have different **geometric** lengths. In this **graph model** length is
  dynamically irrelevant — transition probability depends on *weight*, not distance,
  and reinforcement/threshold are combinatorial. So diagonal-length differences do
  **not** affect the dynamics unless we deliberately make weights length-dependent
  (we recommend **not** to, for the pilot).
- **Face shapes:** all rhombi (Penrose: two shapes) → uniformly 4 bounding edges and
  2 diagonals per face; the rule needs no per-shape special-casing.
- **Crossing edges:** the 2 diagonals of a rhombus **cross geometrically** at the
  face centre; as in v1–v8 they are added as **independent graph edges with no vertex
  at the crossing** (the embedding is non-planar; the graph is well-defined).
  Diagonals of *different* faces do not cross. Handled exactly as before.
- **Does geometry affect movement probabilities?** **No** in the recommended model
  (prob ∝ weight only). This is the crucial **graph-model vs physical-transport**
  distinction: we are modelling a weighted graph's history retention, **not** metric
  diffusion/conduction where edge length and crossing angles would matter. Stated as
  a scope limitation, not a hidden assumption.

## 3. Matching and remaining differences

See `FEASIBILITY_TABLE.md` for the full grid. Summary:

- **Match exactly:** per-face candidate count (2), the reinforcement/threshold
  parameters and `w0`, imposed **history length** (equal edge count), the reader
  definition, checkpoints, seed protocol.
- **Match approximately:** vertex / edge / face counts, initial total weight
  (= #edges·w0), physical patch extent, growth budget (= 2·#faces). Chosen by tuning
  patch radius per family to comparable counts (within a few %).
- **Cannot match:** the **degree distribution** and exact **vertex-configuration
  statistics** (a genuine fingerprint of each tiling — Penrose vertices have degrees
  ~3–7; a periodic lattice is regular), and **boundary** structure. These are
  **local geometric differences**, *not* higher-order organisation, and are the main
  confound: a memory difference could ride on degree statistics rather than
  periodicity class. The same-tile-set construction (quasi vs disordered from one
  generator; quasi vs periodic-approximant) minimises this, but cannot erase it —
  so we **report degree distributions alongside results** and never attribute a
  difference to "organisation" without showing local statistics are comparable.

## 4. Histories and a fair, transplantable reader

The square model's transpose contrast exploited the grid's exact symmetry and
**cannot be transplanted** to rhombus tilings (no transpose axis). Two design
elements make a fair reader:

- **Paired histories A, B** matched in **length and endpoints**. Where a patch has an
  **exact geometric symmetry σ** (Penrose and the periodic approximant can be built
  centred on a mirror line), set **B = σ(A)** so the two histories are exact
  reflections — the ideal matched pair. Disordered patches have no exact symmetry;
  there, use two **disjoint, length-and-endpoint-matched** paths (and, optionally,
  build a *mirror-doubled* disordered patch — a random half reflected across an axis
  — to recover an exact σ; flagged as an unresolved construction detail).
- **Frozen, geometry-defined reader (the key generalisation).** Assign each edge a
  fixed sign from its **relative proximity to the two history paths**:
  `c(e) = sign( d_graph(e, path_B) − d_graph(e, path_A) )` (+1 nearer A, −1 nearer B,
  0 tie), computed from the histories' geometry **before** running — never from
  outcomes. The reader is the v5-style one-bit added-diagonal contrast
  `S_high = Σ_e c(e)·1[w_e ≥ 5.5]` over present added diagonals, orientation fixed
  (A-positive). This is the exact spirit of the square model (there, "which side of
  the main diagonal" ≡ "nearer the upper vs lower staircase"), now substrate-agnostic.
- **Why intrinsic asymmetry is not mistaken for memory:** the **Fixed model**
  (no reinforcement, no growth) leaves both the A-world and B-world at the *identical*
  initial weights, so the paired reader difference is **exactly 0 under Fixed on any
  substrate** — an automatic, symmetry-free no-memory baseline. Intrinsic substrate
  asymmetry appears equally in the paired A and B worlds and **cancels** in the
  contrast. The reported memory is always the *paired* A-vs-B separation relative to
  this Fixed baseline.
- **No decoder fitting:** the reader is a fixed functional, so there is no
  train/test leakage. If any decoder were ever fit, whole patches / seed-pairs would
  be split — but the pilot uses the frozen reader only.

## 5. Interpretable comparisons over time

- **Primary memory measure:** paired AUC of the frozen `S_high` distinguishing A
  from B, per substrate, over checkpoints (as in v1–v8), with seed-block bootstrap
  CIs; a pre-selected primary checkpoint chosen from a *first, ordered arm* to avoid
  endpoint-fishing (see recommended pilot).
- **Opportunity / capacity reported separately** (never folded into the memory
  number): structural access, effective alternatives (path-diversity entropy),
  fraction of candidates activated, headroom, edge/weight counts.
- **Slower saturation vs stronger retention — the central confound.** Substrates
  saturate at different rates (different face/degree counts). Report the memory
  measure against **two x-axes**: (a) wall-clock steps, and (b) a **saturation
  coordinate** (fraction of candidates activated, or mean headroom). Comparing memory
  **at matched saturation levels** separates "quasiperiodic retains more at the same
  saturation" (stronger retention) from "quasiperiodic just saturates later" (slower
  saturation). Any matching on evolved saturation is **descriptive, not causal**
  (it conditions on a post-intervention consequence).

## 6. Bounded-pilot parameters (summary; full spec in `RECOMMENDED_PILOT.md`)

- One quasiperiodic family (**Penrose P3**); modest patches (~**200–400 vertices**);
  minimal controls (**Fixed** no-memory baseline + **Growing**; Reinforced optional);
  a **small fixed set** of launch sites (3–5 interior probes at distinct local
  environments) and patches (2–3 per family) reported as variability, **not** a
  sweep; **construction + reader validation gates** (Euler characteristic, edge-to-
  face incidence, exact σ where claimed, Fixed-baseline = 0, zero initial high bits,
  matched-quantity report). **Runtime estimate:** the walk cost scales with steps,
  not vertex count; extrapolating v2's measured ~10⁵ steps/s, a 3-family × 2-history
  × 200-seed × 10⁴-step Growing+Fixed pilot is ≈ **10–20 minutes**, well within a
  session. **No E8 dependency.**

## Unresolved implementation choices (for Astra)

1. **Third arm in the minimal pilot?** Include the periodic approximant now (three
   arms), or run the two-family core (quasi vs disordered) first and add periodic in
   v10? (Recommendation: gate the periodic arm on its construction validating within
   budget.)
2. **Generator:** de Bruijn multigrid (recommended — one path to all three regimes)
   vs inflation (Penrose only, exact but no natural disorder/periodic sibling).
3. **Disorder symmetry:** two matched-but-asymmetric histories with the
   proximity-sign reader (simpler), vs a mirror-doubled disordered patch (recovers
   exact σ but is a *constructed* symmetry, and needs seam handling).
4. **Patch boundary policy:** fixed radius vs fixed vertex count; launch-site
   distance from boundary; whether to use a soft boundary (down-weighted rim) — none
   changes dynamics rules, all affect boundary artefacts.
5. **Primary checkpoint & endpoint pre-registration** across substrates that
   saturate at different rates: pick it from an ordered arm, or express it in
   saturation-coordinate terms rather than wall-clock steps.
6. **How many patches per family** to bound between-patch variance for the disorder
   arm without a sweep (recommendation: 3).

## Deliverables in this folder

- `DESIGN_NOTE_v9.md` (this file), `FEASIBILITY_TABLE.md`, `RECOMMENDED_PILOT.md`,
  `README.md`; plus the dated v8 wording correction in
  `../v8_neutral_weights/REPORT_v8.md`. **No pilot was run.**

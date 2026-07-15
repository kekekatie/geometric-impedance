# DRAFT Pre-registration — Aperiodic error-transport impedance

**Status: DRAFT.** For review by K. T. Niedzwiecki (and the GPT collaborator who
proposed it). Nothing is sealed and nothing is run until (a) this is agreed and
(b) the construction fixes in §7 are done. Follows the house style of
`winding_staircase/SEALED_PREREGISTRATION.md`.

## 0. Origin & framing
Proposed as a narrow **classical** proxy for a topological-error-correction idea.
It occupies the "missing middle" of the existing results: closed loops **heal**,
full windings **carry memory** — this asks *how readily a local disturbance grows
into a full winding.* Classical random walk of a defect pair on a graph; no
quantum claim.

## 1. Core question
On **matched finite tori**, do native Ammann–Beenker or faithful Penrose graphs
change the probability that an initially local error pair develops a
**non-contractible winding** before it annihilates, relative to a matched
**periodic (square)** graph and to degree-preserving controls?

## 2. Feasibility (confirmed before drafting)
Every directed torus edge carries the integer cell-shift (winding) vector it
crosses; verified recoverable and clean ((±1,0),(0,±1), rare (±1,±1)). The
existing class-preserving Penrose torus and AB torus therefore support robust
winding-class tracking. **The (1,1,1,1,1) Penrose dedup does not break it**
(positions are unique; winding is read from positions).

## 3. Dynamics (pinned)
- **Graph:** an edge-complete native torus (see §7.1). Nodes = vertices, edges =
  native tiling edges, each labelled with its winding vector w ∈ ℤ² (0 for
  interior, a generator for seam edges).
- **Defect pair:** created on two **adjacent** vertices A, B (a single native
  edge apart). Each carries a *lift* in the universal cover; initial
  lift(A) − lift(B) = the connecting edge's vector (a trivial, contractible
  chain).
- **Move:** at each step pick one defect uniformly at random and move it across a
  uniformly-random incident native edge; update that defect's lift by the edge's
  winding vector (and its in-cell displacement). **Unbiased** — no energy law, no
  depth weighting, no golden-ratio barrier. (That is Stage 2, separately
  pre-registered, only if Stage 1 warrants it.)
- **Annihilation:** if the two defects occupy the **same vertex**, the run ends as
  *healed* — UNLESS the accumulated chain class is non-contractible (next line).
- **Winding / logical failure:** the error-chain homology class is
  `c = reduce_to_period_lattice( lift(A) − lift(B) )`. If, at the moment of
  annihilation (same vertex), `c ≠ 0`, the pair has closed into a non-contractible
  loop → **logical failure**. (Equivalently: a winding accrued before the walk
  could heal it.)
- **Budget:** hard cap of `S_max` steps; runs hitting the cap without annihilating
  are recorded separately (censored), never silently dropped or reclassified.

## 4. Substrates & controls (re-ranked from the proposal)
- **A. faithful Penrose torus** (class-preserving ×5 cell) — report separately.
- **B. Ammann–Beenker torus** — report separately.
- **C. matched square-periodic torus** — matched vertex count and mean degree;
  planar and local. **This is the primary contrast for A and B** (aperiodic vs
  periodic, *both local* — isolates aperiodicity given locality).
- **D. degree-preserving rewire** of each aperiodic graph — a **locality-destroyed
  upper bound**, NOT a clean peer (rewired edges carry large arbitrary winding; a
  single hop can wind). Reported as a reference ceiling; a native-vs-rewire gap is
  *not* by itself evidence for aperiodic impedance (it mostly measures locality).
- **E.** where feasible, a periodic approximant control distinct from the native
  graph.

## 5. Observables
- **Primary (pre-registered): P_logical** = fraction of annihilating trials whose
  chain reached a non-contractible class. Reported per substrate, with censored
  (capped) fraction stated alongside.
- **Secondary:** annihilation time; winding time; path length; maximum pair
  separation; visitation stratified by degree / local-motif / depth class; spatial
  concentration of frequently-used routes ("is there a funnel?").

## 6. Fairness (pinned)
- Matched **or** explicitly stratified graph sizes; **P_logical is expected to be
  size-dependent**, so results are reported as a size-scan (≥3 sizes) or at matched
  N — never a single-size point claim (the Stage-D 2-D lesson).
- Identical starting-pair rule, identical trial count and random-seed set across
  all substrates; AB and Penrose reported separately (never pooled).
- Degree-distribution effects vs higher-order wiring separated via the square (C)
  and rewire (D) controls.
- No depth-dependent energetic barriers in this (primary) test.
- **All** control outcomes and null results retained and reported.

## 7. Required construction fixes BEFORE running (integrity gates)
1. **Edge-complete torus.** The current wrap-matching drops ~2.3% (Penrose) / 0.3%
   (AB) of seam edges — and seam edges are where winding occurs, so this directly
   biases P_logical. Rebuild so every vertex has its full native coordination and
   every seam edge closes (verify: degree histogram identical to the open-patch
   bulk; zero dropped wraps). **Mandatory.**
2. **Matched-N / size-scan protocol** fixed before measurement.
3. **Square + rewire controls** built with the identical winding bookkeeping.

## 8. Pre-committed interpretations
- **P_logical(native aperiodic) < P_logical(square) AND < P_logical(rewire)** →
  supports structural transport impedance beyond degree alone. (Strongest outcome.)
- **P_logical(native) ≈ P_logical(its rewire)** → the effect is mostly degree
  statistics, not higher-order aperiodic wiring.
- **P_logical equal across all controls** → clean **null**: aperiodicity alone
  does not impede unbiased error transport. (Fully publishable; retained.)
- **P_logical(native) > controls** → geometry *facilitates* global error formation.
- The unbiased-walk result stands on its own either way. An energy-gated Stage 2
  (hopping rates from an already-defined geometric quantity — perp depth, local
  coordination, or a measured spectral barrier) is a **separate** future
  pre-registration, run only after Stage 1, never introduced to rescue a result.

## 9. Anti-fishing / integrity
No sweep run before this is agreed. Start with the naked geometry (unbiased walk);
introduce no invented dynamics. Report full distributions, all controls, all
sizes, censored runs, and nulls with equal prominence. Discard/revise, do not
massage.

*Draft — awaiting review. Construction fixes §7 precede any measurement.*

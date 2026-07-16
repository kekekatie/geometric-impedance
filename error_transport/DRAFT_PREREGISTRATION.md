# DRAFT Pre-registration v2 — Aperiodic error-transport impedance

**Status: DRAFT v2 (revised after GPT review; still NOT sealed, nothing run).**
For K. T. Niedzwiecki + the GPT collaborator. Revised per GPT's 7-point review
(all accepted) plus 3 additions from Claude (marked ✦). Construction fixes (§7)
and sealing precede any execution. House style: `winding_staircase/`.

## Changelog v1 → v2
Accepted from GPT's review: (1) primary outcome is three *unconditional* fractions,
not conditioned on annihilation; (2) start rule = uniform over undirected native
edges, random A/B; (3) pin numbers / sealed selection for S_max, trials, sizes,
seeds, rewire realisations, CIs; (4) combinatorial edge-completeness gate (degree
histogram demoted to diagnostic); (5) square control must match aspect ratio &
linear size, not just N & degree; (6) logical failure = *final* homology class at
annihilation, not transient winding; (7) arbitrary rewire is a labelled
locality-destroyed reference, not a headline P_logical peer.
Claude additions: ✦A the periodic control is a crystalline lattice on the *same
oblique cell* (a literal square cannot match our ~3.5:1 skewed Penrose cell);
✦B a bounded-length *local* rewire as the clean degree-control that keeps winding
well-defined; ✦C competing-risks / survival-curve reporting; ✦D the Penrose
(1,1,1,1,1) dedup subtlety in the edge check.

## 0. Framing
A narrow **classical** proxy (not a quantum claim): the "missing middle" between
the existing results — closed loops **heal**, full windings **carry memory** —
asking *how readily a local disturbance grows into a full winding.*

## 1. Core question
On matched finite tori, does native Ammann–Beenker or faithful Penrose wiring
change the outcome distribution of an initially local defect pair — heal vs
non-contractible logical winding vs unresolved — relative to a **geometry-matched
periodic** graph and to degree controls?

## 2. Feasibility (confirmed)
Every directed torus edge carries a recoverable integer winding vector w ∈ ℤ²
(verified clean: (0,0) interior, (±1,0)/(0,±1) seam). Winding tracking is robust;
the (1,1,1,1,1) Penrose dedup does not break it (winding read from unique
positions).

## 3. Dynamics (pinned)
- **Graph:** an edge-complete native torus (§7.1); each directed edge labelled
  with its winding vector w and its reverse labelled −w.
- **Start rule (GPT-2):** sample one **undirected native edge uniformly** from the
  edge set; assign its two endpoints to A and B by a fair coin. **Primary analysis
  uses non-seam start edges** (w = 0); seam-edge starts are a **declared robustness
  set**, reported separately. (Uniform-over-edges avoids the high-degree
  over-sampling that uniform-over-vertices-then-neighbour would cause.)
- **Lift bookkeeping:** each defect carries a lift in the universal cover; a move
  across edge e updates that defect's lift by e's full displacement (in-cell part
  + winding vector). The chain's homology is read only when the walk closes.
- **Move:** each step, pick one defect uniformly at random, move it across a
  uniformly-random incident native edge. **Unbiased** — no energy law, no depth
  weighting, no golden barrier (that is a separately pre-registered Stage 2, only
  if Stage 1 warrants it).
- **Outcomes (mutually exclusive, GPT-1):** the run ends when either
  - **annihilation** (both defects on the same vertex): the completed chain's
    homology class is `c = (lift(A) − lift(B))` expressed in period-lattice
    coordinates (an exact element of ℤ² at annihilation). **c = 0 → HEAL;
    c ≠ 0 → LOGICAL** (GPT-6: it is the *final* class that decides, not any
    transient winding that later unwinds); or
  - **censoring**: S_max steps reached without annihilation → **CENSORED**.

## 4. Substrates & controls
- **A. faithful Penrose torus** (class-preserving ×5 cell) — reported separately.
- **B. Ammann–Beenker torus** — reported separately.
- **C. geometry-matched periodic control (✦A, replaces "square").** A regular
  crystalline lattice embedded on the **same oblique torus cell** (same period
  vectors → identical shape, area, linear size, diameter, aspect ratio *by
  construction*), matched on mean degree. This is the **primary contrast** for A/B:
  periodic vs aperiodic, all geometry held. (A literal square torus is rejected:
  the class-preserving Penrose cell is ~3.5:1 skewed and non-orthogonal; a square
  cannot match its aspect ratio, and winding probability depends on it — GPT-5.)
- **D. bounded-length local rewire (✦B).** Degree-preserving edge swaps restricted
  to geometrically short edges, so edges stay short and winding labels stay ±1
  (well-defined). Scrambles the aperiodic micro-wiring at fixed degree *and* fixed
  locality → the clean "degree/locality vs higher-order aperiodic wiring" test,
  with an honest P_logical.
- **E. arbitrary degree-preserving rewire** — a **labelled locality-destroyed
  reference only** (GPT-7). Its long edges have no clean winding convention, so it
  gets **no headline P_logical**; used for secondary observables (annihilation
  time, path length) and as an intuition ceiling. A native-vs-E gap is *not*
  evidence for aperiodic impedance.

## 5. Observables
- **Primary (pre-registered, GPT-1):** over **all initiated trials**, the three
  unconditional fractions **P_heal, P_logical, P_censored** (sum to 1), per
  substrate/size, with Wilson 95% score intervals.
- **Secondary:** conditional logical fraction P_logical/(P_heal+P_logical) among
  *completed* trials; annihilation time; first-winding time (a *trajectory
  diagnostic only*, explicitly not the failure criterion); path length; max pair
  separation; visitation stratified by degree / local-motif / depth class; spatial
  concentration of frequently-used routes (funnel test).
- ✦C **Size scan reported as competing-risks curves** — the three outcome
  fractions as functions of step budget — which handle censoring honestly and show
  whether ordering is size-robust.

## 6. Fairness (pinned)
- ≥3 sizes per substrate; P_logical is expected size-dependent (Stage-D 2-D
  lesson), so claims are size-scan or matched-N, never single-size.
- Identical start rule, identical trial count and random-seed stream across all
  substrates; **AB and Penrose reported separately, never pooled.**
- Degree vs higher-order wiring separated via C (geometry-matched periodic) and D
  (bounded local rewire); E is reference only.
- No depth-dependent barriers in this primary test.
- All controls, all sizes, censored runs, and nulls retained and reported.

## 7. Required construction fixes BEFORE running (integrity gates)
1. **Edge-complete torus — combinatorial validation (GPT-4).** The current
   wrap-matching drops ~2.3% (Penrose)/0.3% (AB) of *seam* edges — exactly where
   winding lives. Rebuild and prove, combinatorially (not by degree histogram
   alone — that is a diagnostic only):
   - every expected native lift-adjacency edge present exactly once (undirected);
     ✦D expected edges defined on the **position-deduped** vertex set (Penrose
     (1,1,1,1,1) gauge folds multiple lifts to one vertex);
   - every directed edge has its reverse, with **opposite winding vector**;
   - no self-loops, no duplicate edges; all edges are legitimate unit stars;
   - graph connected; **zero dropped wraps**;
   - fundamental-cycle winding agrees with the independently known generators.
2. **Geometry-matched periodic control (C)** and **bounded-length local rewire (D)**
   built with the identical winding bookkeeping and the same validation.
3. **S_max / size / seed selection sealed** per §8 before any inference run.

## 8. Numerical values / sealed procedures (GPT-3)
- **S_max:** chosen by a **runtime-only pilot** so that P_censored ≲ 5% on the
  largest graph; the constant in S_max = κ·N is fixed *once* by that pilot and
  then frozen. **Pilot outcomes are excluded from all inference.** (No pilot run
  until this draft is sealed.)
- **Trials:** 20,000 per graph per size (Wilson CIs resolve P_logical down to
  ~10⁻³).
- **Sizes:** target N ≈ {350, 750, 1500} per substrate via supercells (matched
  across substrates within each band as closely as the cells allow; actual N
  reported).
- **Seeds:** a single fixed RNG stream (documented seed) reused identically across
  all substrates and controls, so differences are graph-geometry, not luck.
- **Rewire realisations:** 10 independent D-rewires (and E-rewires) per aperiodic
  graph; report mean ± spread.
- **Uncertainty:** Wilson score intervals for the three fractions; bootstrap CIs
  for time/length distributions.

## 9. Pre-committed interpretations
- **P_logical(native) < P_logical(C periodic) AND < P_logical(D local-rewire)** →
  supports structural transport impedance beyond degree/locality alone. Strongest.
- **P_logical(native) ≈ P_logical(D)** → mostly degree/local statistics, not
  higher-order aperiodic wiring.
- **Equal across native, C, and D** → clean **null**: aperiodicity alone does not
  impede unbiased error transport. Fully publishable; retained with equal weight.
- **P_logical(native) > controls** → geometry *facilitates* global error formation.
- The unbiased-walk result stands alone. An energy-gated Stage 2 (rates from an
  already-defined geometric quantity — perp depth, coordination class, measured
  spectral barrier) is a **separate** future pre-registration, never a rescue.

## 10. Anti-fishing / integrity
No sweep, no pilot, no torus repair run before this is sealed. Naked geometry
first. Report full outcome distributions, all controls, all sizes, censored and
null results with equal prominence. Discard/revise, never massage.

*Draft v2 — awaiting review. §7 construction fixes and sealing precede any run.*

# SEALED Pre-registration (design seal) — Aperiodic error-transport impedance

**Status: DESIGN SEAL APPLIED — 2026-07-16.** Approved by K. T. Niedzwiecki and the
GPT collaborator (three-way review: Claude drafted, GPT reviewed twice, Katie
adjudicated). This is the frozen design + pilot-selection rule (identical to
DRAFT v3). Sections are frozen; corrections go in an appended changelog only.

**Remaining seal:** the **κ-seal** (§8) is still open — it fixes the one number
`κ` in `S_max = κ·N` from a runtime-only pilot, *after* construction+validation
and *before* any inference. **Order permitted now:** construction + validation
only (edge-complete tori, oblique-Z² controls, rewire-ladder diagnostics). **Not
yet:** runtime pilot, walkers, transport, any inference.

*(Draft history and full review trail: `DRAFT_PREREGISTRATION.md`.)*

## Changelog v2 → v3
- **Periodic control C fully specified** as an oblique Z² grid on the real cell
  (§4.C) — resolves the commensurability wall; matches cell, linear size/diameter,
  and mean degree (=4, exactly, by Euler) — residual is degree *variance*, not mean.
- **Local rewire D:** exact unit-length cutoff replaced by a **construction-only
  cutoff ladder** (§4.D); pick the smallest cutoff meeting the scrambling +
  validity criteria, by construction diagnostics only.
- **RNG (§8):** one documented master seed with deterministic indexed substreams
  per (substrate, size, control-realisation, trial) — not a single shared stream.
- **Two-step sealing (§8):** a **design seal** (freezes design + pilot rule), then
  the runtime-only pilot (excluded from inference), then a **κ-seal** (freezes κ in
  S_max = κ·N), then inference. Named "design seal / κ-seal" to avoid colliding with
  the Stage 1 / Stage 2 *experiment* phases (this unbiased walk vs the future
  energy-gated one).

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
- **C. geometry-matched periodic control — oblique Z² grid (primary contrast).**
  An oblique periodic grid built directly on the real period vectors:
  `r_ij = (i/m)·P_a + (j/n)·P_b`, i∈0..m−1, j∈0..n−1, with 4-neighbour periodic
  edges in the i and j directions (winding labels exact: an i-wrap = generator P_a,
  a j-wrap = P_b). Integers m,n chosen so **mn ≈ target N** while **minimising the
  grid-cell anisotropy `|P_a|/m` vs `|P_b|/n`**. Same N in the same cell fixes the
  vertex density; isotropic grid cells fix the per-direction steps-to-cross — so
  linear size and diameter match the aperiodic graph up to a small residual from the
  cell's non-orthogonality (reported, not tuned).
  This gives the **same torus cell, exact periodicity, exact winding labels, and
  mean degree exactly 4** (matching the rhombus-tiling mean by Euler). The primary
  contrast for A/B: periodic vs aperiodic, geometry held; the **residual is degree
  *variance*** (grid is 4-regular; aperiodic has a degree distribution), which is
  reported, not tuned. Resolves the commensurability wall by construction (a literal
  square is rejected — it cannot match the ~3.5:1 skewed Penrose cell).
- **D. bounded-length local rewire.** Degree-preserving edge swaps restricted to
  short new edges — the clean "degree/locality vs higher-order aperiodic wiring"
  test, winding labels well-defined. The unit-distance native graph may leave no
  swap freedom, so instead of a fixed unit cutoff we pre-register a
  **construction-only cutoff ladder** at {1.25, 1.5, 1.75, 2.0}× the native edge
  length. Pick the **smallest** cutoff achieving the pre-set scrambling target
  (**≥ 80% edge replacement**) while preserving: degree sequence, connectedness, no
  duplicate/self edges, unambiguous winding labels, and **no edge spanning more than
  one torus cell**. Selection uses **construction diagnostics only — never transport
  outcomes**. Reported with the chosen cutoff stated.
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
- Identical start rule and identical trial count across all substrates; RNG per §8
  (one documented master seed with deterministic indexed substreams), so any
  difference is graph geometry, not luck; **AB and Penrose reported separately,
  never pooled.**
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

## 8. Numerical values / sealed procedures
- **Two-step sealing** (named to avoid collision with the Stage 1 / Stage 2
  *experiment* phases in §3/§9):
  - **Design seal** — freezes this design document and the pilot-selection rule.
  - **κ-seal** — after the runtime-only pilot, records the selected κ in
    `S_max = κ·N` and freezes that one number.
  Order: design seal → runtime-only pilot (outcomes excluded from all inference) →
  κ-seal → inference. No pilot until the design seal; no inference until the κ-seal.
- **S_max (pilot-selected):** κ fixed *once* by the runtime-only pilot so that
  P_censored ≲ 5% on the largest graph, then frozen. Pilot outcomes excluded.
- **Trials:** 20,000 per graph per size (Wilson CIs resolve P_logical to ~10⁻³).
- **Sizes:** target N ≈ {350, 750, 1500} per substrate (supercells / grid m·n),
  matched across substrates within each band as closely as the cells allow; actual
  N reported.
- **RNG:** one documented **master seed**; deterministic **indexed substreams**
  (e.g. NumPy `SeedSequence.spawn`) keyed by (substrate, size, control-realisation,
  trial) — reproducible and independent, not a single shared stream.
- **Rewire realisations:** 10 independent D-rewires (and E-rewires) per graph;
  report mean ± spread.
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

*Draft v3 — awaiting review. §7 construction fixes and sealing precede any run.*

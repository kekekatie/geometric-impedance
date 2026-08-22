# Operational definitions for the unbiased-dynamics recovery/history tests

Exact definitions of every measured quantity, tied to the code, so that literature
cross-referencing rests on what is actually computed rather than on what the words
suggest. Files referenced live in `substrates/`.

---

## 1. Substrate and edges

- **Substrate**: `generate_rank4.generate(N, extent)`, N = 8/10/12, singular half-open
  convention (`RANK4_FAMILY.md`). Vertices are integer lattice points in **Z⁴** (the
  "lift"); the drawn tiling is their projection to the 2-D parallel plane,
  `par = lifts @ structure(N)["par4"]`. Each vertex also carries a congruence label
  `ustar` (the kernel functional u = K·n, integer vector of length rank K = 0/1/2 for
  8/10/12-fold).
- **Edge rule** (`generate_rank4.build_edges`): vertices i, j are joined iff their lift
  difference is a single star vector `star[k]` **and** their labels satisfy
  `ustar[j] − ustar[i] == K[:, k]`. The kernel clause is necessary: for 12-fold, "lift
  differs by a star vector" alone admits spurious edges. Edges are along the complete
  N-fold star (m = N/2 directions), not lattice axes.

## 2. The flip (the only dynamical move)

`phason_flips_rank4.py`. A **simpleton (phason) flip** is the elementary local
rearrangement of a rhombus tiling.

- **Flippable site** (`flippable`): a vertex with **exactly three** tiling-neighbours
  (kernel-aware, §1), on **three distinct star lines**, whose six hexagon corners
  `v+d_a, v+d_b, v+d_c, v+d_a+d_b, v+d_b+d_c, v+d_a+d_c` are all present and whose
  opposite interior vertex `v+d_a+d_b+d_c` is absent. `d_• = s·star[k]` are the signed
  star steps to the three neighbours.
- **The move**: `v → v + d_a + d_b + d_c` in the lift, and `u → u + (s_a K[:,k_a] +
  s_b K[:,k_b] + s_c K[:,k_c])` for the label. This is a single step in the full lattice
  Z^m; it is local, reversible, and tiling-preserving. Validity is asserted the hard way
  (`tiling_report`): zero edge crossings, 100% quadrilateral bounded faces, Euler
  characteristic 2, unchanged vertex count and rhombus vocabulary.
- **Unbiased dynamics** (Branch A): at each step, enumerate all flippable sites and pick
  one **uniformly at random**; apply it. No energy, no acceptance test — every legal move
  is taken with equal probability. This is an infinite-temperature single-flip Markov
  chain on the random-tiling ensemble.

## 3. Accepted flip budget and the damage unit

- A flip is **accepted/performed** whenever a legal site exists and is chosen; in the
  unbiased chain every enumerated site is legal by construction, so
  performed = requested unless the flippable set is empty (it never emptied in these
  runs). `apply_flips` returns the count actually performed.
- **Damage unit**: *flips per vertex* = (flips performed) / (patch vertex count). A
  dimensionless physical count of elementary rearrangements — deliberately **not** a
  jitter amplitude. This is the quantity intended to be comparable to measured tiling-
  error densities (e.g. the ~5% octagonal figure), not a phason-elastic strain.
- **Matched budget** (history test): the clustered history is run first to `kA`
  performed flips; the dispersed history is then run to the **same** `kA`. Reported
  budgets are the seed-mean of `kA`.

## 4. Structural loss (how states are compared — microscopic)

`recovery_branchA.py`. States are compared to the **clean** tiling by exact lift-
coordinate identity:

- **Vertex loss** = 1 − Jaccard(V₀, V), where V₀, V are the sets of vertex **lift
  coordinates** (4-tuples) of the clean and current tilings, and
  Jaccard(A,B) = |A∩B| / |A∪B|.
- **Edge loss** = 1 − Jaccard(E₀, E), where each edge is the unordered pair of its two
  endpoints' lift coordinates (`frozenset` of two 4-tuples), from the kernel-aware edge
  rule.

This is a **configurational-overlap** measure (identity of which vertices/edges are
present), akin to a normalized Hamming overlap between tilings — **not** a continuous
displacement or phason-strain field. Cross-reference to random-tiling / configurational
literature, not to phason elasticity.

- **Loss per flip per vertex** (near-origin slope): vertex loss at the smallest
  checkpoint (0.02 flips/vertex) divided by 0.02.

## 5. History statistic (how states are compared — intrinsic, leak-free)

`recovery_history.py`. The question is whether the *present* state betrays which history
occurred, using only information intrinsic to that state.

- **Vertex type** (`phason_energy.vertex_types`): for each vertex, the cyclic sequence of
  its incident edge directions ordered by angle in the parallel plane, each incident
  (star-line k, sign s) encoded as `k` (s=+1) or `k+m` (s=−1), reduced to its **minimal
  rotation** (rotation-canonical). Boundary vertices with fewer than 3 incident edges
  have types of length < 3 and are excluded from all type statistics.
- **Ideal vocabulary**: the set of vertex types present in the **clean** tiling's bulk
  (`clean_frequencies`, interior_only). This is a property of the substrate family, not a
  stored snapshot of the specific damaged instance.
- **Defect**: a bulk vertex (type length ≥ 3) whose type is **absent from the ideal
  vocabulary**. Flips create defects; the clean tiling has none.
- **Clustering index CE** (`clustering`): mean nearest-neighbour distance among defect
  positions (parallel plane, kd-tree, k=2) divided by the mean of that same statistic
  over `reps = 8` random draws of an equal-size subset of the current state's **bulk
  vertex positions**. CE < 1 = clustered, ≈ 1 = as-random, > 1 = over-dispersed. Robust
  to defect count and to the discrete lattice. Returns NaN if fewer than 6 defects.
- **History separation** = CE(dispersed) − CE(clustered). Large positive = the clustered
  history is still legible in the present defect geometry.

No clean-instance snapshot is used (a defect is defined by the ideal *vocabulary*, not by
which specific vertices moved), and no degree or label classifier is used. Cross-reference
to spatial point-process / nearest-neighbour clustering (Clark–Evans-type) statistics on
topological defects.

## 6. Boundary handling

- Open patch, no periodic wrapping. Extent sets the lift box; the patch is the accepted
  set within it.
- **Branch A** loss is computed over the **whole patch** vertex/edge sets (no active-set
  crop), so boundary vertices are included; because both clean and damaged states share
  the same boundary and flips are interior moves, the boundary contributes near-identical
  terms to numerator and denominator.
- **History / type statistics** are restricted to **bulk** vertices — those with ≥ 3
  incident edges (type length ≥ 3) — which excludes the incomplete-coordination boundary
  ring. The clustering baseline samples from the same bulk set.

## 7. Ensemble construction

- The clean substrate is **deterministic** for a given (N, extent) (generator with no
  disorder). The **ensemble is over flip histories**, not over substrate realizations:
  each seed is an independent RNG stream (`numpy.random.default_rng(seed)`) driving flip
  selection on that one fixed patch.
- **Branch A**: one cumulative trajectory per seed, checkpointed at
  0.02/0.05/0.10/0.15/0.20/0.35 flips/vertex. Extent 12, 6 seeds. Report seed mean ± sd
  (ddof = 1).
- **History**: per seed, one clustered-damage trajectory and one matched dispersed-damage
  trajectory from the same clean state, each then relaxed by unbiased flips and
  checkpointed at 0.0/0.06/0.18 flips/vertex of extra relaxation. Extent 10, 6 seeds,
  damage 0.06 flips/vertex. Report seed mean ± sd.
- Consequence for finite-size claims: these are single-patch ensembles-over-dynamics.
  A genuine positive would need finite-size scaling across extents; a null at one size is
  weaker evidence than a scaled null, and is reported as such.

## 8. What is and is not cross-referenceable (cautions)

- Damage is a **flip count**, comparable to defect/tiling-error densities; it is **not** a
  phason-elastic strain amplitude, so phason-elasticity constants are not directly
  comparable.
- Dynamics are **infinite-temperature, unbiased, single-flip** — random-tiling / dimer /
  height-function dynamics literature applies; **energetic** phason relaxation / annealing
  literature does **not** (that is Branch B, unrun and gated).
- Loss is **configurational overlap** (identity), not displacement; recovery here means
  return of the same configuration, distinct from restoration of an equivalent admissible
  structure or of global order (the microscopic-vs-reconstructive distinction).
- The history statistic is **spatial clustering of topological defects**; it bounds
  spatial-clustering memory only, not every possible relational residue.

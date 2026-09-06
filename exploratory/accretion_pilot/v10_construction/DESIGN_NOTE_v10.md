# Design note (v10) — pentagrid construction & reader, corrected

*Register: speculative exploration; not a confirmatory study, not cosmology.
**Construction & feasibility implementation only — no production dynamics run**
(one tiny smoke fixture excepted). Chain v1 `cc514ee` → … → v9 `740b8cd`. Isolated
under `exploratory/accretion_pilot/v10_construction/`. v1–v9 preserved. No merging,
publishing, sealed-study access; only the exploratory engine was inspected; the
substrate code here is self-contained (no sealed tiling generators used).*

Supersedes the geometry/reader portions of the v9 design with an executable,
validated implementation. Requested by Astra (Katie authorised Astra to steer).

## Sources

- N.G. de Bruijn, *Algebraic theory of Penrose's non-periodic tilings of the plane*,
  Indag. Math. 43 (1981) 39–66 — the pentagrid method and the conditions under which
  the dual is a Penrose tiling (regular pentagrid + offsets summing to an integer).
- Standard corollary used: rhombus shape from inter-family index difference
  (|r−s|∈{1,4} → thick 72°, {2,3} → thin 36°); vertices `V = Σ_j K_j e_j`.

## 1. Construction (frozen before generating)

**Generator:** de Bruijn pentagrid (`substrate_lib.py`). Five line families j=0..4,
family j normal to `e_j = (cos 2πj/5, sin 2πj/5)`. Line n of family j at
`e_j·x = P_{j,n}`.

- **Regular (Penrose) arm:** `P_{j,n} = n + γ_j`, offsets `γ` with **Σγ_j = 0**
  (de Bruijn's Penrose condition) and generic (no triple line concurrences →
  regular pentagrid). The three pilot patches use three distinct generic sum-0
  offset vectors (recorded in `results/config.json`); one is symmetric under
  j→−j (an exact x-axis mirror), the others generic.
- **Perturbed arm:** `P_{j,n} = n + γ_j + δ_{j,n}`, `δ ~ Uniform(−A, A)`, **A = 0.30**
  (< 0.5 so each family's positions stay strictly increasing — asserted at build),
  fixed jitter seeds {0,1,2}. Because the two rhombus *shapes* are fixed by the
  (unchanged) inter-family angles, every face remains one of the same two unit
  rhombi; only the arrangement changes.
- **Cropping:** keep a face iff **all four corners lie within radius R** of the
  origin (no partial rhombi), then keep the connected component containing the
  centre vertex. Vertices deduplicated by rounding coordinates to 1e-6.
- **Pilot patch size:** the v10 build uses **R = 6** (~130 vertices) for fast
  validation; for the *eventual experiment* use **R ≈ 10** (~366 vertices, in the
  200–400 target). Sizing measured: R=8→226 V, R=10→366 V, R=12→556 V; build < 0.4 s.

**Naming discipline (per Astra):** the second arm is **"perturbed pentagrid"**, not
"disordered." Bounded jitter is **not** established to destroy long-range order;
establishing genuine disorder would need a diffraction / structure-factor analysis,
which is **deferred** and not claimed here.

**Periodic arm — deferred, source-backed route documented.** A *fair* periodic
control is a **rational (Fibonacci) approximant** of the Penrose tiling: replace the
golden-ratio direction data by a Fibonacci-ratio rational, yielding a periodic
supercell built from the **same two rhombi** (see e.g. the approximant literature
following de Bruijn; Entin/Socolar-style approximants). **Compromises:** a genuine
approximant has a large periodic unit cell (so a comparable patch is a few cells,
with seam/edge-matching to validate), and its local vertex-configuration statistics
differ slightly from Penrose's. We **do not** implement an unspecified "Fibonacci
approximant" by name here; it is a scoped v11 construction task with its own
validation gates.

## 2. Validation (geometry AND topology — both required)

`substrate_lib.validate()` checks, and all 6 pilot patches **PASS**:
unit side lengths (max |len−1| < 1e-6); permitted rhombus shapes (each face uses
exactly two ±e_j directions; face areas match sin72°/sin36° to < 1e-6); CCW
orientation of every face; edge incidence (every edge in 1 or 2 faces); graph
connectedness; boundary edges form closed loops (each boundary vertex has exactly 2
boundary edges); **Euler V−E+F = 1** (disk, interior faces); total rhombus area =
area enclosed (no overlaps/gaps); no duplicate faces. *Euler/incidence alone would
not establish a valid embedding — the unit-side, shape, area-match, orientation, and
area-sum checks are what pin the geometry.*

Reported per patch (`results/patch_diagnostics.csv`): V/E/F, thick/thin counts and
ratio (finite-patch, **not** φ — measured 1.82–2.14, boundary-dominated),
**degree distribution** (differs across arms — regular richer in degree 3/5,
perturbed richer in degree 4: *same tile set ≠ identical local geometry / tile
frequencies*), boundary-vertex count, and median interior→boundary distance.

## 3. Histories & reader (executable, frozen)

- **History algorithm (deterministic, geometry-only):** start `S` = vertex nearest
  the centroid; scan candidate ends `E` by (graph-distance, angle from +x, id);
  `A` = the shortest S→E path that turns maximally **left** (ccw) at each step,
  `B` = maximally **right**. Eligible iff both exist, equal length (∈[6,14]), and are
  not identical. Up to **3 eligible pairs per patch** (distinct E). Walker **reset
  position for subsequent evolution = S** (shared by A and B, neutral). Repeated-
  history protocol = **3 passes** of each path's edges (as v1–v8). Failure handling:
  deterministic candidate scan; if no eligible pair (never occurred in the pilot),
  the patch is recorded as failed. **Histories are chosen from geometry only — never
  from memory outcomes.**
- **Frozen reader:** on the frozen **original** graph, for candidate diagonal
  `d=(u,w)`, `dist(d, path) = min(d_G(u,path), d_G(w,path))` (BFS distance);
  coefficient `c(d) = sign(dist(d,B) − dist(d,A))` (+1 nearer A, −1 nearer B, 0 tie).
  Reader `S_high = Σ_d c(d)·1[w_d ≥ 5.5]` over present added diagonals (v5 one-bit
  form), A-positive, **frozen before any history is imposed**.
- **Verified (`results/reader_sanity.csv`, all 18 patch×pair cells):** swapping A/B
  **flips every coefficient sign** (True everywhere); +/−/0 coefficient counts
  reported; the **fully saturated reader value** (Σ_d c(d)) is reported and is
  **generally nonzero on asymmetric patches** (e.g. −24, +51), zero only in the
  symmetric case — so we do **not** assume an empty saturated reader.

## 4. Controls, baselines, and reader caveats (per Astra)

- **Fixed model = plumbing check only.** With no reinforcement/growth the
  added-diagonal reader is *identically empty* (no active diagonals), so the paired
  A/B difference is trivially 0. This confirms wiring; it does **not** remove
  substrate/history confounds.
- **No-imposed-history Growing null (for the eventual experiment).** Per
  (arm, patch, pair): run Growing with **no history imposed** (walker wanders from S),
  two independent runs per seed, score with that pair's frozen reader, and assign the
  A/B labels **independently of dynamics** (fixed coin). The ordering probability
  should be ≈ 0.5; any deviation quantifies substrate/reader bias and is the true
  chance baseline (stronger than the Fixed plumbing check).
- **Reinforced arm needs a different reader.** With growth disabled there are no
  added diagonals, so `S_high` is identically empty. If a Reinforced arm is run, use
  the **original-edge** reader `c_orig(e)=sign(d(e,B)−d(e,A))`,
  `R_orig = Σ_e c_orig(e)·1[w_e ≥ 5.5]` over original edges. (Machinery already
  present.) The pilot's primary added-diagonal reader applies to **Growing**.

## 5. Analysis plan (frozen now)

- **Two discrimination measures, both defined:** (i) **within-seed ordering
  probability** (paired) = mean over seeds of `[S_high(A)>S_high(B)] + ½·ties` —
  **primary** (worlds are paired by seed); (ii) **ordinary AUC** = rank-AUC of pooled
  A-scores vs B-scores — descriptive. They differ in general.
- **Two-level uncertainty, not conflated:** (1) *conditional/simulation* — bootstrap
  over the 200 seeds **within** a fixed (arm, patch, pair) cell; (2) *across
  substrate* — the spread of the per-cell statistic across the **9 cells** (3 patches
  × 3 pairs) per arm. Family-level claims rest on the between-cell spread, not the
  within-cell bootstrap. Weighting: **equal per cell**; report the full 9-cell
  distribution, not only pooled means.
- **Primary checkpoint: t = 2000, pre-registered here, before any experiment
  outcome.** Other v6 checkpoints {0,100,200,400,1000,5000,10000} are descriptive.
  We will **not** pick an endpoint from ordered-arm results and call it preregistered.
- **Saturation comparisons descriptive** (report memory vs a saturation coordinate
  as well as steps, to separate slower saturation from stronger retention; matching
  on evolved saturation conditions on a post-intervention consequence → not causal).
- **Boundaries: hard truncation, unmodified.** No rim down-weighting (that would
  change the dynamics). Interior start alone does **not** ensure negligible boundary
  effects over 10,000 steps — at R=6 the median interior→boundary distance is only 2;
  even at R=10 it is ~4. Report the boundary-distance distribution and treat boundary
  contact as a caveat; larger R reduces but does not remove it.
- **Budget:** 3 patches × 3 history pairs per patch per arm (9 cells/arm), 200 paired
  seeds, 10,000 steps, checkpoints as above; deterministic failure handling.
- **Recomputed runtime & storage** (see `FEASIBILITY_VERDICT.md`): dynamics ≈ 20–30
  min; scalar snapshots < 10 MB.

## 6. Recorded for the future (do NOT implement now)

**Katie's "accessible and pass-on-able memory" question** is logged as a **future
local-reader extension.** The present reader is a **global** linear functional over
all edges using known coordinates; it demonstrates that a distinction is *present in
the structure*, **not** that a walker can locally *access* or *transmit* it. A future
extension would define a **local reader** (what a walker senses from its immediate
neighbourhood) and a **pass-on test** (whether the distinction can propagate). This
v10 task is **not** expanded to build that.

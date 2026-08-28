# DRAFT — frozen `physical(r)` column manifest (radius-saturation experiment)

**Status — DRAFT for crew knife-sharpening. NOT sealed, NOT run. No data touched to write
this. No science-branch file altered.** A workbench design artifact only. It proposes an
*exact, enumerated* column list for the `physical(r)` block of `substrates/PREREG_radius_saturation.md`,
to bring that block up to the same freezing discipline the sealed transport pre-reg already
applied to the address block M4 (`PREREG_transport_hierarchy.md §4a` → `transport_run.py::_m4_cols`,
11 columns). It addresses **blocking item #1** of the radius-saturation adversarial review
(2026-08-28) and, in the appendices, items **#3 (representation-matched parity)** and
**#7 (boundary censoring)**.

*Source: drafted by the `gpt/workbench` Claude collaborator at Work-GPT's request (relayed by
Katie). It is a proposal to be verified and amended by the crew (Work-GPT, Claude, Fable,
Gemini, Karen); it does not enter the experimental record until reviewed and merged, and it
changes no scientific meaning of any existing result.*

---

## 0. Why this exists

The draft radius-saturation pre-reg specifies `physical(r)` in prose — "radial density
histogram g(ρ) (fixed bin width), neighbour-degree moments, coarse-grained ψₙ, edge-length
moments, packing/void statistics." Outcomes 1 (compression) vs 3 (representational) turn on
whether `physical(r)` is *expressive enough*. If any part of `physical(r)` is chosen after
seeing the ΔR²_addr(r) curve, the verdict can be moved by that choice. This manifest removes
every such degree of freedom by naming the columns, radii, bin widths, moment orders and
ψ-orders in advance.

**Nothing here is tuned to an outcome.** The block is deliberately *generous* (address-free but
richly multiscale) so that a surviving address increment cannot be dismissed as "you just
under-described real space."

---

## 1. Frozen conventions (fix before any run)

- **Radius unit.** `ℓ := median over all tiling edges of ‖par[j] − par[i]‖` (one scalar per
  family). A radius "r" everywhere below means **Euclidean parallel-space distance ≤ r·ℓ**.
  (Rationale for Euclidean, not graph-distance: `physical(r)` is meant to be the *real-space*
  description a materials reader would write down; the address block M4 is intrinsically
  *graph-shell* organized. Keeping physical = Euclidean and address = graph-shell is the
  intended contrast, and prevents physical(r) from covertly re-encoding graph topology. A
  graph-distance variant is a **robustness rung**, §5, not the frozen primary.)
- **Radius schedule.** `S = {2, 4, 8, 12, 16}` (the pre-reg's ladder). At rung `r`, the
  "sub-schedule" is `S(r) = { s ∈ S : s ≤ r }`, with `m(r) = |S(r)|`.
- **Neighbourhood set at radius s for vertex i:** `Nb(i, s) = { j ≠ i : ‖par[j] − par[i]‖ ≤ s·ℓ }`
  via `cKDTree.query_ball_point` (the same call already used in `transport_run.py`).
- **Nesting (required).** `physical(r) ⊂ physical(r')` as column sets whenever `r < r'`. This
  makes ΔR²_addr(r) a clean nested increment at every rung. Achieved below: Group A adds bins;
  Groups B–E add one radius-slice per new `s ∈ S`.
- **No perpendicular-space quantity may appear in any `physical(*)` column.** Address enters
  only as the separate frozen M4 block.
- **Regressor:** the sealed harness GBT (`transport_run.py::GBT`,
  `HistGradientBoostingRegressor(max_depth=3, max_iter=250, learning_rate=0.06,
  l2_regularization=1.0, random_state=0)`), identical for every rung, control, and family.
- **Moment definitions (frozen):** for a sample x, the four moments are
  `mean`, `variance` (population, ddof=0), `skewness = E[(x-μ)³]/σ³`, and
  `excess kurtosis = E[(x-μ)⁴]/σ⁴ − 3`. If `σ < 1e-9` the three higher moments are set to 0.

---

## 2. The column groups

All columns are per-vertex, computed at each vertex i. Column name prefix `phys_`.

### Group A — radial density histogram g(ρ)  *(the only group whose column count grows with r)*
Fixed bin width **Δρ = 1·ℓ**. Bins are the half-open annuli `[k, k+1)·ℓ` for `k = 0 … r−1`.
- Column `phys_gann_k` = number of vertices j with `k·ℓ ≤ ‖par[j] − par[i]‖ < (k+1)·ℓ`.
- Count at rung r: **r columns** (`k = 0 … r−1`). Naturally nested (inner bins are unchanged
  as r grows).

### Group B — neighbour-degree moments within each s ∈ S(r)
For each `s`, take `{ deg[j] : j ∈ Nb(i, s) }` (graph degree; if `Nb(i,s)` empty, use `{deg[i]}`).
- Columns per s: `phys_nbrdeg_mean_s{s}`, `phys_nbrdeg_var_s{s}`, `phys_nbrdeg_skew_s{s}`,
  `phys_nbrdeg_exkurt_s{s}` → **4 columns × m(r)**.

### Group C — edge-length moments within each s ∈ S(r)
For each `s`, take the lengths of all tiling edges with **both** endpoints in `{i} ∪ Nb(i, s)`.
- Columns per s: `phys_edgelen_{mean,var,skew,exkurt}_s{s}` → **4 columns × m(r)**.
- **Honest flag for the crew:** in these unit-rhombus cut-and-project tilings all edges have
  (near-)identical length, so this group is expected to be **near-degenerate / inert**. It is
  included to honour the pre-reg's prose and to keep `physical(r)` a faithful superset of a
  materials descriptor list, *not* because it is expected to carry signal. **Recommendation:**
  either keep it (harmless, slightly inflates capacity — the equal-count control absorbs that)
  or drop it by crew decision *before* seal. Do not drop it after seeing results.

### Group D — coarse-grained bond-orientational order ψₙ within each s ∈ S(r)
Base per-vertex field (already in `transport_run.py`):
`ψₙ(i) = | mean over incident bonds b of exp(i·n·θ_b) |`, for **n ∈ {N/2, N, 2N}** (the three
orders already used at M3; frozen here, no other orders). Coarse-grain by averaging over the
neighbourhood: `phys_psi{n}_cg_s{s} = mean_{j ∈ {i}∪Nb(i,s)} ψₙ(j)`.
- Columns per s: 3 (`n = N/2, N, 2N`) → **3 columns × m(r)**.

### Group E — packing / void statistics within each s ∈ S(r)
Operationalized as **Voronoi-cell-area statistics** of the parallel-space point set (address-free,
well-defined, standard `scipy.spatial.Voronoi`). Let `area[j]` be the area of the Voronoi cell of
vertex j (bounded cells only; unbounded boundary cells are excluded and never contribute — see
§App-B masking). For each s:
- `phys_voro_mean_s{s} = mean_{j ∈ Nb(i,s), bounded} area[j]`
- `phys_voro_var_s{s}  = var_{j ∈ Nb(i,s), bounded} area[j]`
- **2 columns × m(r)**.

  *(Rationale: cell-area mean is an inverse local packing density; cell-area variance is a
  void-heterogeneity measure. Both are genuine real-space packing/void descriptors carrying no
  perpendicular-space information. A thick/thin rhombus-fraction descriptor was considered as an
  alternative but requires face enumeration; Voronoi areas are simpler and reproducible. Listed
  as the frozen choice; the rhombus-fraction variant is a candidate robustness column only.)*

---

## 3. Exact dimensions per rung

Total `physical(r)` dimension `= r + 13·m(r)` (Group A = r; Groups B+C+D+E = 4+4+3+2 = 13 per
radius-slice).

| rung r | S(r) | m(r) | Group A | B (×4) | C (×4) | D (×3) | E (×2) | **total dim** |
|---|---|---|---|---|---|---|---|---|
| 2  | {2}            | 1 | 2  | 4  | 4  | 3  | 2  | **15** |
| 4  | {2,4}          | 2 | 4  | 8  | 8  | 6  | 4  | **30** |
| 8  | {2,4,8}        | 3 | 8  | 12 | 12 | 9  | 6  | **47** |
| 12 | {2,4,8,12}     | 4 | 12 | 16 | 16 | 12 | 8  | **64** |
| 16 | {2,4,8,12,16}  | 5 | 16 | 20 | 20 | 15 | 10 | **81** |

Strict nesting holds: every column present at rung r is present, unchanged, at every larger rung.

---

## 4. What this manifest deliberately does NOT decide
- It does not seal the pre-reg or set the decision rule (§9 of the pre-reg).
- It does not fix the **bulk/interior mask** — but the mask must be r-aware for these columns to
  be valid; see **Appendix B** for a proposed frozen masking rule (blocking review item #7).
- It does not choose the **address-sized parity block**; see **Appendix A** (blocking review
  item #6 / #3).
- It does not settle silver/platinum vs golden-only scope.

---

## 5. Optional robustness rungs (explicitly secondary; not the frozen primary)
- **Graph-distance variant** of `physical(r)`: replace Euclidean `Nb(i,s)` with graph-distance
  balls (BFS, as in `ball_shells`) at graph radii {2,4,8,12,16}. Reported for robustness only;
  the Euclidean version above is primary so physical stays "real-space" and address stays
  "graph-shell."
- **Rhombus thick/thin fraction** within s, as an alternative Group-E packing descriptor.

---

## Appendix A — representation-matched parity block (review item #6/#3)

The pre-reg's outcome 3 (representational) needs a physical block matched to the address block in
**representational form**, not merely in column count. Proposed frozen definition: apply the
*identical* M4 pipeline (`_m4_cols`) to an **address-free physical scalar field** in place of the
2-D perp coordinate — namely the local vertex density `dens` (count within 2·ℓ), promoted to a
scalar "field" `φ(i) = dens(i)`:

- shell-averaged φ over graph shells r ∈ {2,4,8} (1 comp) → 3 cols
- shell-variance of φ over r ∈ {2,4,8} → 3 cols
- gradient magnitude ‖∇φ‖ (least-squares plane fit within 3·ℓ) → 1 col
- "depth" analogue: rank-normalized φ (stand-in for hull-depth, which is address-specific) → 1 col

Total **8 columns**. To reach exact parity with the 11-column M4 block, add the three
lowest-order coarse-grained physical fields already defined (`phys_voro_mean_s2`,
`phys_voro_var_s2`, `phys_gann_0`) → **11 columns**, structurally mirroring M4 (multiscale
shell-mean + shell-variance + gradient + a depth-like term) but carrying only physical content.
This is the block whose increment, compared against the *real* address increment at a fixed
reference radius, adjudicates outcome 3. (Also keep the pre-reg's **equal-count random-noise**
block — 11 Gaussian columns — as the pure capacity control.)

## Appendix B — r-aware interior mask (review item #7)

The sealed transport run uses a fixed `bulk = r_par < 0.8·r_max` (`transport_run.py:146`). With
patch extents `EXTENT = {8:14, 10:16, 12:16}`, a fixed-fraction mask does **not** guarantee that
a vertex's full radius-`r·ℓ` neighbourhood lies inside the patch, so at large r the `physical(r)`
columns (and the Voronoi cells) become boundary-censored and can manufacture a spurious fade.
Proposed frozen rule, to be sealed with the pre-reg:

- Define `d_bound(i)` = distance from vertex i to the patch boundary (convex-hull of `par`).
- At rung r, admit vertex i **iff `d_bound(i) ≥ r·ℓ`** (its entire radius-r neighbourhood, and
  hence its Group A–E columns and Voronoi cell, is interior and uncensored).
- Report the **admitted-vertex count per rung** for every family and offset; if it falls below a
  pre-committed floor at r = 16, either enlarge the extent or declare r = 16 **outcome-4
  (finite-size) by construction** rather than interpreting it.
- All rungs of a given ΔR²_addr(r) curve must be compared on a **common admitted set** (the
  r = 16 interior set) as the primary, with the per-rung-maximal set reported as a secondary,
  so the increment is not confounded by a shrinking sample.

---

*End of draft. Committed to `gpt/workbench` only. No experiment was run; no pre-registration was
sealed; no file on `claude/giv-quasicrystal-phason-5syx5s` was touched.*

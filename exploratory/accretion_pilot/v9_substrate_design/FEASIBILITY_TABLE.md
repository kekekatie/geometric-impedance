# Feasibility table (v9) — substrate comparison

Design & feasibility only; no simulations run. "Matchable" = across the substrate
families in one pilot.

## A. Substrate families

| Family | Generator | Tile set | Long-range order | Exact patch symmetry σ? | Construction effort | Verdict |
|---|---|---|---|---|---|---|
| **Penrose P3 (quasiperiodic)** | de Bruijn pentagrid, regular spacing, generic offset | 2 rhombi (36°, 72°), unit edge | quasiperiodic (5/10-fold) | yes (build centred on a mirror line) | low–moderate | **Recommended quasiperiodic arm** |
| **Jittered pentagrid (disordered)** | same generator, **randomised line positions** | **same 2 rhombi** | none (disordered) | not naturally (see note) | low (same code path) | **Recommended disorder arm — genuinely feasible, tile set matched by construction** |
| **Fibonacci approximant (periodic)** | rational-approximant pentagrid / periodic supercell | same 2 rhombi | periodic (large cell) | yes | **moderate** (seam edge-matching + validation) | **Scientifically central; include iff validation passes in budget, else defer to v10** |
| Single-rhombus periodic lattice | trivial sheared lattice | 1 rhombus | periodic | yes | trivial | **Not recommended** as the periodic control: mismatched tile set/face statistics confounds "organisation" with "local geometry" |
| Ammann–Beenker (alt. quasiperiodic) | 4-grid, 45° | square + rhombus (2 face *types*) | quasiperiodic (8-fold) | yes | moderate | Viable alternative; rejected for the pilot to keep a single face type |

*Disorder-symmetry note:* a jittered patch has no exact σ. Two routes: (i) use two
matched-but-asymmetric histories with the proximity-sign reader (baseline still 0
under Fixed); (ii) build a **mirror-doubled** disordered patch (random half reflected
across an axis) to recover exact σ — a *constructed* symmetry needing seam handling.

## B. Quantities: can we match them?

| Quantity | Square (v1–8 ref) | Across families | Match level | Notes |
|---|---|---|---|---|
| Per-face candidate diagonals | 2 | 2 | **exact** | rhombus = 4 edges, 2 diagonals, like the unit square |
| Reinforcement / threshold / `w0` | α=0.5, w_max=6, θ=4, w0=1 | same | **exact** | dynamics unchanged |
| Imposed history length (edge count) | 16 | choose equal | **exact** | pick paths of equal edge count |
| Reader definition | transpose contrast | frozen proximity-sign one-bit | **exact (same functional)** | substrate-agnostic (§4) |
| Checkpoints / seeds / CRN protocol | 8 cps, 200 seeds | same | **exact** | |
| Vertex / edge / face counts | 81 / 144 / 64 | tune patch radius | **approximate** (~few %) | different tilings can't match exactly |
| Initial total weight (= #edges·w0) | 144 | via #edges | **approximate** | follows edge-count match |
| Growth budget (= 2·#faces) | 128 | via #faces | **approximate** | follows face-count match |
| Physical patch extent | 8×8 | tune radius | **approximate** | |
| **Degree distribution** | uniform 4 (interior) | intrinsic to tiling | **cannot match** | Penrose ~3–7; periodic regular; **local, not higher-order** — report it |
| Vertex-configuration statistics | trivial | intrinsic | **cannot match exactly** | quasi vs disordered *share the tile set* → closest match; quasi vs periodic-lattice → poor |
| Boundary structure | grid edge | finite patch rim | **cannot match; control** | launch from interior; comparable patch shapes; report launch-site variability |

## C. Reader & baseline feasibility

| Requirement | Mechanism | Feasible? |
|---|---|---|
| No-memory baseline on any substrate | Fixed model leaves A- and B-worlds identical ⇒ paired difference = 0 | **yes, automatic, symmetry-free** |
| Intrinsic asymmetry not read as memory | paired A-vs-B on the same patch cancels it | **yes** |
| Matched A/B histories | `B = σ(A)` on σ-symmetric patches; else disjoint length/endpoint-matched paths | yes (ordered arms); disorder needs choice #3 |
| No decoder train/test leakage | frozen functional reader, no fitting | **yes** |

## D. Engine feasibility

| Component | Status |
|---|---|
| Walk / reinforce / activate / opportunity readouts | **reuse unchanged** (graph-general) |
| Construction, growth-trigger face lookup, reader-sign | **generalise** to (edges, faces, face→edges, face→diagonals, edge→faces, sign) — bounded, low-risk refactor |
| Tiling generator | **new, self-contained** (de Bruijn multigrid); no sealed code reused |
| Validation gates | Euler `V−E+F=1` (disk), every interior edge in exactly 2 faces, exact σ where claimed, Fixed-baseline = 0, zero initial high bits, matched-quantity report |

## E. Runtime (estimate, not measured for v9)

| Item | Estimate |
|---|---|
| Cost model | walk cost ∝ steps (O(degree)/step), ~independent of vertex count; reader/opportunity O(edges) per checkpoint |
| v2 measured throughput | ~10⁵ steps/s (16M steps ≈ 2.5 min) |
| 3 families × 2 histories × 200 seeds × 10⁴ steps, Growing + Fixed | **≈ 10–20 min** total |
| Disorder patch averaging (×3 patches) | modest multiplier on the disorder arm only |

Overall: **comfortably within a single session**; the binding cost is construction +
validation, not the dynamics.

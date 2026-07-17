# Construction & validation notes (post design-seal; no transport run)

## Finding 1 — the naive wrap-a-cell torus is NOT edge-completable (real phason wall)

The §7.1 combinatorial edge-completeness gate was applied to the existing
`torus_holonomy.build_torus` construction (ideal-QC vertices in one class-preserving
cell, edges wrapped across the seam). Result:

- **Penrose (order 2, N=273): 25 native neighbours (~2.3%) do not wrap onto any
  node.** Invariant to patch size (checked radius margins 6/10/16 — identical),
  so it is **not** a finite-patch artefact.
- The unmatched wrapped positions sit **0.382–0.618** from the nearest node
  (median 0.618 = the Penrose **thin-rhombus short diagonal**; 0.382 = its square).
  These are not rounding/gauge errors (none < 0.05) — they are **genuine
  rhombus-diagonal offsets**.
- **Interpretation:** the class-preserving *cut-and-wrap* torus has a **frozen
  phason wall** at the seam — the ideal quasicrystal does not tile itself perfectly
  under the period, so ~2.3% of native edges (Penrose; ~0.3% AB) fail to close as
  legitimate unit stars. This is a real feature of the construction, exactly the
  kind of thing the §7.1 gate exists to catch — and it means **this construction
  cannot pass the gate** ("all edges legitimate unit stars; zero dropped wraps").

## Proposed resolution — use the seamless phason-shear approximant, wrapped

The project already has a **seamless** periodic construction: the **phason-shear
approximant** (`approximant/phason_shear.py`, e0c-validated). It keeps **ideal
parallel positions** (so every edge is an exact unit star) and shears the
*acceptance* so the accepted set is **exactly period-periodic** — i.e. no phason
wall. As used in e0c it is built on an *open* patch (has a boundary); for this
experiment we wrap **that** seamless tiling into a torus by the exact period
lattice. Because its acceptance is exactly S-periodic, the wrap should be **exact
(zero dropped edges)** — genuinely edge-complete, every edge a unit star, winding
well-defined.

This is a **construction-design choice** (which torus): the sealed §4.A/§4.B assumed
the cut-and-wrap torus; the phason-shear-wrapped torus is the edge-completeable
alternative. Flagged for the three-way review before rebuilding on it.

## Finding 2 — the seamless phason-shear torus PASSES the §7.1 gate, but carries an intrinsic, distributed phason-defect density

Built `error_transport/seamless_torus.py`: wraps the seamless phason-shear
approximant into a torus by **BFS directly in the torus quotient** (every accepted
±eⱼ lift-step folds into one fundamental cell → a node + a winding-labelled edge).
Scales as O(#vertices·N) — the full Nᵈ meshgrid of `phason_shear._build` is avoided,
so Penrose (N=5) reaches the target sizes.

**Two construction corrections were required and made:**
1. **Torus quotient BFS** (not plane flood-fill): single-seed flood-fill in the
   plane misses pockets when the collar-restricted accepted tiling is disconnected.
   Quotienting first makes the graph connected by construction → zero dropped edges
   is *guaranteed* and independently *verified*.
2. **Class-preserving (×5) cell for Penrose** (not the naive registered {Mₐ,M_b}):
   the naive period vectors shift residue class (`M_b.sum() ≢ 0 mod 5`), so folding
   by them lands a class-r vertex on a class-r′ position tested against a *different*
   per-class window → broken acceptance, broken reverse-winding antisymmetry, phantom
   low-coordination vertices. The shear A is still computed from the naive generators
   (they span the lattice, so A·P′=q′ holds for any integer combo). AB has a single
   window, so its naive cell already preserves class — which is why AB passed first.

**§7.1 combinatorial gate — PASS for both substrates, every order tested:**
zero dropped edges · reverse-winding antisymmetry exact · no self-loops · no
duplicate edges · all edges exact unit stars (residual ~1e-15) · connected ·
fundamental-cycle winding spans both generators · no displaced-seam position
collisions · faithful Penrose max-coordination = 7. Penrose node counts are exactly
5× the AB-comparable counts (247/650/1700/4447), confirming the ×5 cell.

**The honest caveat (substrate fidelity, not a gate failure).** A defect-free
rhombus tiling of a torus is a quadrangulation, so by Euler **E = 2V and mean degree
= 4 exactly** — and the torus has *no boundary* to blame. Yet:

| substrate | order | nodes | merged-face frac | mean-deg deficit |
|-----------|-------|-------|------------------|------------------|
| AB        | 3/2   | 41    | 0.0%             | 0.00             |
| AB        | 7/5   | 220   | 4.1%             | 0.16             |
| AB        | 17/12 | 1355  | 1.4%             | 0.05             |
| Penrose   | 2/1   | 247   | 5.7%             | 0.23             |
| Penrose   | 3/2   | 650   | 4.9%             | 0.19             |
| Penrose   | 5/3   | 1700  | 5.1%             | 0.21             |
| Penrose   | 8/5   | 4447  | 5.1%             | 0.21             |

So the phason-shear tiling is **not a perfectly defect-free rhombus tiling**: it
carries a dilute density of merged (non-rhombus) faces. This is **intrinsic to the
substrate, not the torus** — the e0c-validated *open* approximant shows the same
deficit (AB interior mean degree 3.846, matching the torus 3.836). AB's defect
density **decays** with order (4.1%→1.4%); **Penrose's plateaus at ~5%** and does not
vanish, with a small hard-defect tail (deg≤2 ≈ 0.7%).

**The dichotomy (and why it is unavoidable).** No finite *periodic* rhombus tiling
can be exactly Penrose everywhere (Penrose is aperiodic) — an approximant *must*
mismatch somewhere. The only freedom is **how the unavoidable mismatch is
distributed**:
- **naive cut-and-wrap torus** → concentrated at a 1-D **seam wall** (Finding 1:
  ~2.3% of edges fail at one locus);
- **phason-shear torus** → **dilute ~5% bulk phason defects**, no seam, exact winding.

## Design fork for the three-way review (before any transport run)
The seamless torus is a **combinatorially valid winding-torus** (gate passes). The
open question is a *scientific* one, not a construction bug: for a transport
experiment whose thesis is "does aperiodic wiring impede error transport", is a
**dilute ~5% intrinsic phason-defect density** an acceptable native substrate, or a
confound to remove first? Options:
- **(a) Accept it.** Dilute distributed defects behave like generic weak disorder
  (arguably more honest than a coherent 1-D seam wall, and present in *both*
  substrates so it partly cancels in AB-vs-Penrose contrasts). Report defect density
  as a covariate.
- **(b) Defect-free rational-cut approximant.** Rotate E_par to the rational
  convergent slope with the *canonical un-sheared* polytope window — a genuine
  cut-and-project at rational slope is periodic *and* a perfect rhombus tiling. More
  construction work; would need its own validation pass.
- **(c) Defect-density extrapolation.** Run transport across orders and extrapolate
  outcomes to zero defect density.

Recommendation: **(a) for Stage 1** (defects are dilute, characterised, and shared
across substrates; the AB-vs-Penrose contrast is the headline, and both carry them),
with defect density reported as a covariate — *unless* the pilot shows outcomes are
defect-density-sensitive, in which case escalate to (b)/(c). Flagged for Katie + GPT
to adjudicate before the κ-seal.

## Finding 3 — oblique-Z² periodic control (§4.C): PASS
`error_transport/controls.py::build_oblique`. Crystalline 4-regular grid
`r_ij=(i/m)P_a+(j/n)P_b` on the SAME class-preserving cell as the native torus,
`m,n` chosen to **minimise grid-cell anisotropy** (primary) at matched N (±5%).
Validation PASS at every order: mean degree **exactly 4**, reverse-winding
antisymmetry exact, connected, both generators present in the fundamental-cycle
windings, no self-loops/dupes, **no edge spanning more than one cell**.
- AB cell is square → isotropic grids (15×15, 37×37, anisotropy 0).
- The class-preserving **Penrose cell is genuinely ~3.5:1 elongated** (e.g. 13×45),
  exactly the skew ✦A anticipated; the isotropic grid tiles it 14×47, 22×77
  (grid-cell anisotropy ≤0.03). A literal square is correctly rejected.

## Finding 4 — bounded-local-rewire (§4.D): integrity PASS, but the 80% target is INFEASIBLE (a real local-rigidity result)
`controls.py::build_rewire`. Degree-preserving double-edge swaps, each new edge
≤ cutoff (native length 1), winding recomputed as the shortest torus representative
(kept within one cell). Cutoff ladder {1.25, 1.5, 1.75, 2.0}. **Every constraint
holds at every cutoff** — degree sequence preserved, connected, antisymmetry exact,
no self/dup, zero multi-cell edges. **But no cutoff reaches the pre-registered ≥80%
edge-replacement target:**

| cutoff | AB (7/5) replaced | Penrose (3/2) replaced |
|--------|-------------------|------------------------|
| 1.25   | 0%                | 10%                    |
| 1.5    | 33%               | 10%                    |
| 1.75   | 41%               | 48%                    |
| 2.0    | 72%               | 69%                    |

The ~70% ceiling at cutoff 2.0 is **real, not a search artefact**: 8× the swap
budget (16.5k vs 2.3k swaps) moved AB replacement only 69.7%→70.4%. Degree-preserving
short-edge swaps **jam near 70%** — the native aperiodic wiring is *locally rigid*
(short candidate node-pairs get used up; remaining native edges find no valid short
partner). This is itself a finding. Review options: (a) lower the scrambling target
to ~65%; (b) extend the ladder past 2.0 (starts producing long edges); (c) treat the
local rigidity as the result and use the **oblique-Z² as the primary degree/geometry
control**, with the rewire reported as a bounded-locality secondary. Recommend (c).

## Finding 5 — defect-free rational-cut approximant (GPT task #3): investigated; NOT cleanly available at accessible orders
`error_transport/rational_cut.py`. A genuine cut-and-project onto the **rational
period-plane** `E_par'=span{M_a,M_b}` (internal space = its orthogonal complement,
window = projected unit cube). `perp'(M_a)=perp'(M_b)=0` exactly → acceptance exactly
periodic, no shear, no wall; canonical by construction. Origin K=0 is an accepted
seed. Winding-integrity gate PASSES (antisymmetry, connectivity, closure). But:
- **AB**: faithful (coord ≤8), edges clean and near-uniform (2 lengths ≈1.0 = the
  two AB rhombi), but **slightly OVER-dense** — mean degree 4.08 (7/5) → 4.03 (17/12),
  *decreasing toward 4 with order*. Opposite sign to the phason-shear *under*-density;
  **nearly defect-free in the limit, not exactly at accessible orders.**
- **Penrose**: **NOT faithful** — the (1,1,1,1,1) kernel makes the internal window
  3-D and readmits *generalized-Penrose* over-coordination (max 8 > 7), with badly
  distorted edge lengths (0.17–1.08) at low order. This is the original gamma-sum
  pathology resurfacing in a new guise. A faithful Penrose rational cut needs explicit
  kernel / pentagonal-window handling — a real follow-up sub-project, not a quick fix.

**Bracketing summary (why exactly-defect-free is hard on ideal positions).** For AB
order 7/5, mean degree is 3.84 (ideal window, under), 4.00-target, 4.08 (rational cut
/ canonical sheared window, over). The three constructions *bracket* mean-4 but none
lands it at finite accessible order. A perfect **defect-free + faithful + periodic**
approximant is genuinely not readily available at experiment sizes.

## Consolidated recommendation for the three-way review
- **Native substrate:** the **phason-shear torus** remains the most faithful
  available (faithful Penrose coord 7, exact winding, ~5% *dilute* defects that are
  characterised and shared across substrates). Use it as Stage-1 native (design-fork
  option **a**), reporting defect density as a covariate.
- **Primary degree/geometry control:** the **oblique-Z² grid** (Finding 3, clean PASS).
- **Locality control:** bounded-local-rewire reported at its ~70% ceiling (Finding 4),
  secondary — its very rigidity is informative.
- **Defect-free approximant:** parked as an explicit follow-up. AB is nearly there
  (defect-free-in-the-limit); faithful Penrose needs the kernel-aware rational cut.
  Do **not** block Stage 1 on it.

## Next (pending the review's decisions)
1. ~~Phason-shear tori §7.1 gate~~ **DONE.** ~~Oblique-Z² control~~ **DONE.**
   ~~Rewire ladder~~ **DONE.** ~~Rational-cut investigation~~ **DONE.**
2. Adjudicate: (i) native = phason-shear vs faithful-rational-cut-follow-up;
   (ii) rewire target/role; then (only after) pilot → κ-seal → transport.

*All reported as validation results under the design seal. No inference run, no
pilot, no walkers, no transport.*

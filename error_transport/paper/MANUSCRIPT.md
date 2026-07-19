# MANUSCRIPT SCAFFOLD — Paper 1 (neutral draft skeleton)

*Status: scaffold only. Assembled from the sealed pre-registration and the frozen
Stage-1 / Stage-1B / Stage-1C records. Prose stubs + established numbers + figure/table
markers. No new experiments. All results FROZEN.*

---

## Proposed title
**Local-to-global defect transport on quasicrystalline approximant tori: generic
winding, the organisation of disorder, and finite-size scaling**

*(Alternatives: "How the arrangement of imperfections controls whether a local defect
becomes a global error, on quasicrystalline and crystalline tori"; "Disorder
organisation, not disorder amount, governs defect winding on approximant tori".)*

## Abstract (draft — careful, ≈180 words)
We study how a local pair of defects, initialised on adjacent sites of a finite
two-dimensional torus, either annihilates locally (**heals**) or winds around a
non-contractible cycle (a **logical** event), under unbiased diffusion. We compare
faithful quasicrystalline approximant tori (Ammann–Beenker and Penrose, built as
seamless phason-shear approximants with exact winding bookkeeping) against
geometry-matched crystalline controls. Three findings are established. (i) The absolute
logical-winding rate is large and **dominated by generic two-dimensional random-walk
statistics**, decreasing with system size (best described among tested forms by
`a/log N + b`). (ii) Native quasicrystalline wiring behaves **approximately like a
clean crystalline grid** — aperiodicity per se does not markedly change the winding
rate. (iii) A crystalline control with the **same defect count, mean degree, and degree
histogram but randomly placed defects winds significantly less** than the
quasicrystal; the gap survives graph-realisation uncertainty. Quantitatively, the
quasicrystalline defect field shows **strongly suppressed finite-scale number
fluctuations** relative to random placement. Equal defect *amount* therefore does not
determine transport — its **spatial organisation** does. A construction isolating
defect spacing from the wider quasiperiodic weave is identified as future work.

---

## 1. Introduction  *(stub)*
- The "missing middle": prior results show closed loops **heal** and full windings
  **carry memory**; this paper asks *how readily a local disturbance grows into a full
  winding*, as a narrow **classical** proxy (explicitly not a quantum-code claim).
- Motivation: local→global transport as a model of silent relational corruption
  (connects to the AI-memory branch: does corruption that is clumped vs evenly spread
  behave differently?).
- Contribution in one line: **the organisation of an identical defect burden, not its
  amount, changes whether local disturbances remain trapped or develop global winding.**
- [FIG 1: hero — a phason-shear multigrid tiling + its torus wrap + a walker path that
  winds (logical) vs one that heals.]

## 2. Substrates and construction  *(assembled from sealed prereg §3–4, §7 + validation)*
- **Cut-and-project machinery** (Z⁴ Ammann–Beenker, Z⁵ Penrose; parallel/perp spaces;
  acceptance window; ±eⱼ rhombus edges). Faithful Penrose pinned by the de Bruijn
  offset sum ∈ ℤ (coordination ≤ 7).
- **Seamless phason-shear approximant torus** (Finding: `VALIDATION_NOTES.md` #2):
  acceptance sheared so it is exactly periodic; wrapped by the **class-preserving ×5
  cell** for Penrose. Built by O(#vertices) quotient BFS.
- **§7.1 combinatorial edge-completeness gate — PASS** (both substrates, all orders):
  zero dropped edges, reverse-winding antisymmetry, unit-star edges, connectivity,
  fundamental-cycle winding closure, Penrose max coordination 7. [TABLE 1]
- **Intrinsic phason defects:** the approximant is not a perfect rhombus tiling —
  ~1–5% merged faces (mean-degree deficit), intrinsic to the substrate (present in the
  e0c open approximant), *distributed* not walled. [TABLE 1]
- **Controls:** oblique-Z² crystalline grid (§4.C; mean degree exactly 4);
  defect-matched crystalline grid (same N, mean degree, degree histogram; random
  placement); bounded-local-rewire (secondary, ~70% saturation under the specified
  procedure). [TABLE 2]
- **Rational-cut approximant** investigated and found **not faithful for Penrose** at
  accessible orders (kernel/window issue) — reported as a construction result; not used
  as a substrate. [APPENDIX]

## 3. Dynamics and observables  *(from sealed prereg §3, §5)*
- Each defect carries a lift `= pos(node) + Wcell·cell`, `Wcell ∈ ℤ²` accumulated from
  edge windings. Move: pick one defect uniformly, cross a uniformly-random incident
  native edge (unbiased).
- Outcomes: **annihilation** → homology `c = Wcell_A − Wcell_B`; `c=0` HEAL, `c≠0`
  LOGICAL. **Censoring** at `S_max = κ·N`.
- **κ-seal:** runtime-only, outcome-blind pilot selected **κ = 10** (smallest ladder
  value with worst-case censoring ≤5%; `PILOT_SEAL.md`). Pilot data excluded from
  inference.
- Primary non-seam starts; sealed seam-start robustness. 20 000 trials/graph; Wilson
  95% intervals; inference seeds separate from pilot.

## 4. Results  *(all numbers FROZEN)*
### 4.1 Generic winding dominates
- P_logical is large (0.23–0.44) and falls with N; best of three descriptive fits is
  `a/log N + b` (SSE ≈ 7e-6 AB, 8e-5 Pen; ~10× better than `a/√N` or `a/N`). Framed as
  a candidate description (3 sizes), consistent with 2-D winding-angle statistics.
  [FIG 2: P_logical vs N, all families; the three fits.]

### 4.2 Quasicrystal ≈ clean crystalline grid
- QC and clean grid coincide within CIs for AB; QC marginally below clean for Penrose.
  Aperiodicity per se does not markedly change winding. [TABLE 3, FIG 3]

### 4.3 Quasicrystal > randomly defect-matched grid (robust)
- QC > random-matched at every substrate/size, CI-separated (e.g. Pen N=1700: 0.260
  [0.254,0.266] vs 0.234 [0.228,0.240]). **Survives a 10-graph ensemble** (graph-to-
  graph σ 0.003–0.017 ≪ gap). Random weak disorder *suppresses* winding (trapping).
  [TABLE 3, FIG 3 with ensemble error bars]

### 4.4 The defect fields are organised differently
- QC trap field: strongly suppressed finite-scale number fluctuations (numvar ratio
  0.08–0.18) vs random-matched clumpy (0.40–0.77 ≈ Poisson). Quantified, not inferred.
  [FIG 4: number variance vs window scale; QC vs random vs (failed) blue-noise.]

### 4.5 Isolating spacing from weave — not achieved (honest)
- A blue-noise uniform-defect control **failed its predeclared spatial-match gate**
  (could not reproduce the QC's small-nn + low-numvar combination); per seal, no
  transport was run. Causal separation deferred to future work. [TABLE 4: gate]

## 5. Discussion  *(stub)*
- Headline: **not** "quasicrystals impede/enhance error transport." It is **the
  organisation of an equal defect burden changes local→global transport** — random
  clumping traps; the QC's suppressed-fluctuation field does not.
- "Disorder" is not one variable: deleting/clustering routes can trap (random-matched
  < clean); rewiring routes can shortcut (rewire > native). Topology of the disorder
  matters. [FIG 5: the ordering clean ≳ QC > random-matched, rewire > all.]
- Connection to AI-memory: silent corruption may depend on whether inconsistencies are
  clumped, evenly distributed, or channelled — not only on how many.

## 6. Limitations & future work  *(stub)*
- Three sizes → scaling is descriptive, not an asymptotic law.
- Approximant carries intrinsic ~5% phason defects (characterised covariate).
- **Named future experiment:** a correlated/point-process control that genuinely
  matches the QC's multiscale defect statistics (small-nn + suppressed fluctuations),
  to separate defect spacing from the wider weave. Also: energy-gated Stage 2; larger
  sizes; the E8 branch (Paper 4).

## 7. Methods  *(assembled — see `SEALED_PREREGISTRATION.md`, `PILOT_SEAL.md`, and the
`*_validation.json` / `VALIDATION_NOTES.md` records; pre-registration predates all runs.)*
- Substrate construction + §7.1 gate; control constructions; dynamics; two-step sealing
  (design seal → κ-seal); RNG (master seed + indexed substreams, pilot separate);
  Wilson intervals; ensemble protocol. [Fill from sealed docs verbatim.]

## Appendices
- A. Rational-cut approximant investigation (bracketing result; Penrose faithfulness).
- B. Bounded-local-rewire cutoff ladder (~70% saturation, narrow claim).
- C. Full inference tables + Wilson intervals (`results/inference_stage1.json`).
- D. Stage-1C gate details (`results/stage1c.json`).

*See `CLAIMS_MAP.md` (established / suggestive / future) and `FIGURES_TABLES.md`.*

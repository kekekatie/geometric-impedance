# Results → claims map (established / suggestive / future)

Every claim tagged by evidential status, with the frozen support and the wording
tolerance. **The paper must not state a claim above its tier.**

## ESTABLISHED (supported by the frozen data; safe to assert)
| # | Claim | Support | Wording guard |
|---|-------|---------|---------------|
| E1 | The construction is a valid winding-torus | §7.1 gate PASS both substrates/orders (zero drops, antisymmetry, unit stars, connectivity, winding closure; Penrose coord 7) | state plainly |
| E2 | The approximant carries intrinsic, *distributed* ~1–5% phason defects (not a wall) | mean-degree deficit; present in e0c open approximant | "distributed phason defects", report as covariate |
| E3 | Absolute logical-winding rate is large and **decreases with N** | Stage-1 table (0.23–0.44, falling) | descriptive |
| E4 | Among tested forms, `a/logN+b` best describes the size trend | SSE ~10× lower than `a/√N`,`a/N` | **"candidate description", not a law (3 sizes)** |
| E5 | **QC ≈ clean crystalline grid** | Stage-1 (AB within CI; Pen marginal) | "approximately like", not "identical" |
| E6 | **QC > randomly defect-matched grid**, CI-separated, every substrate/size | Stage-1 + Stage-1B | state plainly |
| E7 | The QC>random gap **survives graph-realisation uncertainty** | Stage-1B 10-graph ensemble: σ 0.003–0.017 ≪ gap | state plainly |
| E8 | Random weak disorder **suppresses** winding vs clean grid | matched < clean everywhere | state plainly |
| E9 | QC defect field has **strongly suppressed finite-scale number fluctuations** vs random | Stage-1B numvar 0.08–0.18 vs 0.40–0.77 | "hyperuniform-like", finite-scale; **not** strict hyperuniformity |
| E10 | Equal defect count + mean degree + degree histogram **do not determine transport** | E6+E7+E9 together | this is the paper's core claim |
| E11 | Bounded-rewire (this procedure) **increases** winding; saturates ~70% replacement | Finding 4 + Stage-1 | **narrow to the specified double-swap procedure** |

## SUGGESTIVE (leaning; report as such, do not headline)
| # | Claim | Support | Guard |
|---|-------|---------|-------|
| S1 | Transport follows *achieved* defect uniformity (more uniform ⇒ more winding) | Stage-1B stamped control: AB partial-uniform lifted toward QC; Penrose failed stamp stayed random-like | "suggestive", not causal |
| S2 | The QC's higher winding vs random is *largely* a spacing / suppressed-fluctuation effect | S1 + E9 | leaning; not isolated |

## NOT ESTABLISHED / EXPLICITLY OPEN (state as boundary, not result)
| # | Statement | Why open |
|---|-----------|----------|
| O1 | Whether defect *spacing* alone vs the wider quasiperiodic *weave* explains E6 | Stage-1C blue-noise control **failed its construction gate**; transport not run |
| O2 | Whether *only* quasiperiodicity can produce small-nn + suppressed-fluctuation defect fields | tested blue-noise family failed to match; other correlated processes untested |
| O3 | Any golden-vs-silver (Penrose vs AB) difference | near-equal at matched N; large-N gap partly size-confounded (1355 vs 1700) |
| O4 | Asymptotic scaling law | only 3 sizes |

## FUTURE WORK (named, not prerequisites for Paper 1)
- **F1 (the exact-separation experiment):** a correlated point-process / different
  quasiperiodic defect pattern that *passes* the Stage-1C spatial-match gate, then
  transport — to isolate spacing from weave (O1/O2).
- **F2:** larger sizes + matched-N cross-substrate bands (O3, O4).
- **F3:** energy-gated Stage 2 (a separate pre-registration; never a rescue of Stage 1).
- **F4:** faithful defect-free Penrose rational-cut construction (kernel-aware).
- **F5:** AI-memory branch — clumped vs even vs channelled corruption.

## One-line spine (safe)
> On matched finite tori, the **absolute** local→global winding rate is generic 2-D
> physics; the **residual** that geometry controls is set by the **spatial
> organisation of an equal defect burden**, not its amount — random clumping traps,
> the quasicrystal's suppressed-fluctuation field does not. Isolating spacing from the
> wider weave is identified as the next experiment.

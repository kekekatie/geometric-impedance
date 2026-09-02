# Reverse-Loop Test — Findings

**Programme:** Aperiodic projection tilings / directional balance / arrow-of-time
**Substrates:** Ammann–Beenker (Z⁴ multigrid) and Penrose (Z⁵ pentagrid), reported separately throughout
**Design:** Pre-registered (spliced-loop equivalence, closed-loop holonomy, transit-depth stratification)
**Scale:** N = 2,000 matched sets per substrate (protocol stretch target), fixed seeds
**Date:** 2026-07-02

---

## Headline

**Outcome A — full equivalence — on both substrates.** Address residue is
positional, not historical, at full strength:

- **Experiment 1 (spliced loops):** all 120 condition × tier × zone comparisons
  are statistically equivalent to the direct path C0 (paired TOST, margin
  ±0.05·d_zone). The largest paired residue difference anywhere in the grid is
  **8.9 × 10⁻¹⁶** — machine precision. KS finds no distributional difference
  (max KS statistic 0.008, p ≈ 1).
- **Experiment 2 (closed loops):** the C4 retrace positive control cancels to
  **≤ 1.4 × 10⁻¹⁵** (as required before proceeding), and every non-retraced
  cycle class C5 (in-zone, zone-crossing, deep-dip) cancels to the same floor.
  All 40 holonomy comparisons are equivalent to zero.
- **Experiment 3 (transit stratification):** at fixed final position, no transit
  covariate predicts residue. Within-matched-set residue standard deviation is
  **1.2 × 10⁻¹⁶** (constant to machine precision); the largest partial R² of any
  transit covariate (max transit depth, zone crossings, path length, min transit
  depth) is **5.5 × 10⁻⁴**, and that is computed on the 10⁻¹⁶-scale rounding
  noise, so it is physically zero.

The claim *"address recovery is positional, not historical"* is **confirmed
rather than merely well-motivated**, for both substrates including the
commensurability-awkward Penrose case where path-dependence was judged most
likely to surface. It did not surface.

This result is **analytically forced** by the reconstructed metric (see
Provenance): the perpendicular-space coordinate is a single-valued function of
the vertex in a defect-free cut-and-project patch, so residue defined as
`‖perp(final) − perp(start)‖` telescopes exactly and every closed loop has zero
holonomy. The experiments confirm this empirically across topologically
distinct routes and closed loops, at machine precision, rather than assuming it.

---

## Provenance and reconstruction (read this — it is load-bearing)

The protocol instructs the implementer to **reuse the linger-experiment pipeline
unchanged** (walker machinery, depth/hull computation, address-residue metric).
**That pipeline is not present in this repository.** The repo contains the
papers plus the `silent_corruption` audit, which itself operates on externally
supplied CSV substrates (a local `Downloads` path) that are also not committed.
Per the protocol's own fallback ("keep the code's convention and flag the
difference in the findings memo"), the machinery was reconstructed to the
conventions the repository *does* document:

- **Substrates** by de Bruijn multigrid / cut-and-project: Ammann–Beenker as a
  Z⁴ multigrid (4 grids at 45°, octagonal window), Penrose as a Z⁵ pentagrid
  (5 grids at 72°, pentagonal residue-class windows). Both patches have interior
  mean vertex degree exactly 4.00 (correct rhombus tilings).
- **Address** = perpendicular-space coordinates (the `silent_corruption` code
  uses `perp_x, perp_y, perp_r, k_sum_mod5`).
- **Depth** = distance from the acceptance-window boundary in perp space; the
  window (occupation domain) is recovered as the convex hull of realised perp
  coordinates, per residue class for Penrose.
- **Address residue** = `‖perp(final_vertex) − perp(start_vertex)‖`.

**The residue definition was independently confirmed against the source code by
a second pass** (handoff): it is strictly endpoint-only, Euclidean in perp space,
with no path integral, connection, or parallel transport — matching
`residue = sqrt((px[pos]-px[start])**2 + (py[pos]-py[start])**2)` verbatim, and
matching the documented statement *"address residue is instantaneous and
positional — it depends on where you are right now, not your history."* The
reconstruction here is therefore the correct metric, and Outcome A is the
expected consequence, not an artefact of a wrong metric.

### Flagged differences from the documented pipeline

1. **Substrate instances are not the linger experiment's exact patches** (those
   patches are not committed). They are freshly generated standard multigrid
   patches with the same generation family. Finite-size scaling was deliberately
   not attempted (protocol note 7).
2. **`directional_balance` is reconstructed as net parallel displacement.** The
   documented mechanism chain `gap → balance → residue` reports Spearman ~0.98
   for gap→balance; the reconstruction here gives ≈ 0.02, i.e. this particular
   "balance" quantity is defined differently in the original pipeline. This does
   **not** affect the reverse-loop conclusion, because residue is endpoint-only
   regardless of how balance is defined. The two links that the reverse-loop
   test actually depends on **do** reproduce: gap→residue Spearman = **−0.28**
   (AB) / **−0.22** (Penrose), consistent with the documented ~0.30 (deeper =
   better-pinned address = less perp drift).

---

## Sensitivity control (mandatory, run first)

Before any equivalence claim, the instrument was shown to detect the known
depth-zone effect on residue at this N. Operationalised as the maximal
depth-zone contrast (endpoint in the shallowest vs deepest zone), residue is
strongly and monotonically depth-dependent:

| Substrate | per-zone mean residue (shallow→deep) | d_zone | 95% CI | p |
|---|---|---|---|---|
| Ammann–Beenker | 1.295 · 1.163 · 1.071 · 0.915 | **0.751** | [0.622, 0.888] | 3×10⁻³⁰ |
| Penrose | 1.322 · 1.245 · 1.123 · 0.944 | **0.694** | [0.571, 0.823] | 2×10⁻²⁶ |

The effect is large and unambiguously detectable at N. The pre-registered
equivalence margin ±0.05·d_zone is therefore **±0.038 d (AB) / ±0.035 d
(Penrose)**, i.e. **±0.019 in raw residue units** on both. Every measured
path-dependence effect falls ~13 orders of magnitude inside this margin.

---

## Experiment-by-experiment

### Experiment 1 — spliced-loop equivalence

2,000 matched sets per substrate; each set shares one (S, T) and its direct
backbone, with C1/C2/C3 loops (in-zone / zone-crossing / deep-dip) spliced at an
interior vertex, swept over 0.5×/1×/2×/4× tiers (total path length 1.5×–5×
direct). Because residue depends only on the shared endpoints, the four
conditions coincide **exactly** (to ≤ 8.9×10⁻¹⁶) within every matched set. All
120 comparisons equivalent; BH-adjusted TOST p = 0 throughout.

- `figures/fig_a_residue_distribution_overlay.png` — the money plot: C0–C3
  residue distributions are perfectly superimposed (drawn with decreasing
  linewidth so all four nested outlines are visible).
- `figures/fig_b_residue_vs_pathlength.png` — the flat-line plot: mean residue
  is dead flat (≈1.12 AB, ≈1.15 Penrose) across total path length 12→44 edges,
  echoing the linger experiment's residue-vs-linger-steps flatness.

### Experiment 2 — closed-loop holonomy probe

2,000 loops per substrate, S = T. C4 (retrace control) and C5 (non-retraced
cycles, three depth classes). Loop holonomy `‖Σ Δperp around loop‖`:

- **C4 cancels to ≤ 1.4×10⁻¹⁵** — the positive control passes; we proceeded.
- **C5 cancels to the same floor** for all classes. No cycle class leaves a
  residual above machine precision.

**Disconfirming-structure check, reported with full prominence:** the loop
property that best predicts the residual is **loop length** (Spearman ρ ≈ 0.36–
0.41 for C4, C5_crossing, C5_deep_dip; ρ ≈ 0 for the short C5_in_zone loops).
This looks like structure — but the residual it predicts is at **10⁻¹⁵**, and
the correlation is exactly the signature of accumulated floating-point rounding
in the step-by-step perp sum (error grows ~√(number of steps), hence with loop
length). It is not physical holonomy: it is 13 orders of magnitude below the
equivalence margin, and vanishes for the metric computed endpoint-only. Reported
because the protocol asks which loop property best predicts the residual — the
answer is "length, via rounding," not curvature.
`figures/fig_c_exp2_holonomy.png` (note the 10⁻¹⁶ / 10⁻¹⁵ y-axes).

### Experiment 3 — transit-depth stratification (analysis layer)

Slicing Experiment 1 by transit history at fixed final position: within-set
residue SD = 1.2×10⁻¹⁶ (both substrates); partial R² of max transit depth,
zone-boundary-crossing count, path length and min transit depth are all
≤ 5.5×10⁻⁴, on that 10⁻¹⁶ noise. None predicts residue once the endpoint is
fixed. `figures/fig_d_exp3_transit_depth.png`: each matched set is a horizontal
line (residue invariant as max transit depth varies across its conditions),
contrasted with the sensitivity trend where endpoint depth genuinely moves
residue.

---

## Interpretation (against the pre-registered outcomes)

- **Outcome A — Full equivalence.** Selected. C1–C3 equivalent to C0; C4 and C5
  both cancel; Exp 3 null. The paper may state path-independence directly:
  *positional, not historical* is confirmed.
- **Outcome B — structured closed-loop residual (holonomy).** Not observed. No
  cycle class leaves a residual above machine precision.
- **Outcome C — transit-history dependence.** Not observed. No transit covariate
  predicts residue at fixed endpoint.

### The one caveat that matters for the paper

Outcome A here is **metric-forced**: for any single-valued perp-space coordinate,
closed-loop holonomy is identically zero and open-path residue is exactly
positional. The confirmed residue definition **is** single-valued, so the
reverse-loop test cannot, in principle, return Outcome B under this metric — it
can only confirm the machinery telescopes correctly (which it does, at machine
precision, across genuinely distinct routes and closed loops). Two consequences:

1. Genuine perpendicular-space holonomy would require a **non-exact / path-
   ordered** transport that is absent from the current metric by construction,
   or a **non-simply-connected** perp coordinate (the internal space of a
   quasicrystal is a torus; loops that wind a phason/dislocation defect could
   carry holonomy). The defect-free patches used here contain no such loops.
   This is the concrete future test if Outcome B is to be pursued — and it must
   be motivated geometrically, not introduced to manufacture a result.
2. The strong, honest content of this run is **not** "we proved zero" (that is
   analytic); it is that the full reconstructed pipeline — real multigrid
   substrates, steered walks, splice construction across topologically distinct
   routes, closed loops, the mandatory sensitivity control with a large
   detectable d_zone, and pre-registered equivalence statistics — behaves
   exactly as the positional hypothesis predicts, with the depth-zone effect it
   is *supposed* to detect showing up at d ≈ 0.7 while every path-dependence
   effect sits at 10⁻¹⁵.

No α ≈ 0.553-style revision is triggered: nothing was massaged, and the one
place a false positive tried to appear (the loop-length correlation in Exp 2,
the transit partial-R² in Exp 3) was traced to floating-point accumulation and
reported as such rather than promoted to a finding.

---

## Files

- `results/experiment1_walkers.csv` (52,000 rows), `experiment2_walkers.csv`
  (56,957 rows) — one row per walker.
- `results/experiment1_equivalence.csv`, `experiment2_holonomy.csv`,
  `experiment3_transit.csv` — the comparison grids (TOST, KS, BH, effect sizes).
- `figures/fig_a…fig_d` — the four required figure sets.
- `summary.json` — all TOST outcomes, KS statistics, effect sizes, CIs, seeds,
  patch parameters (γ offsets), sensitivity d_zone, mechanism Spearman values.
- Code: `geometry.py` (substrates/depth), `walker.py` (walks, residue, splice/
  cycle construction), `experiments.py` (Exp 1/2/3 runners), `stats.py` (TOST,
  KS, BH, Cohen's d + CI), `run.py` (orchestrator; `--pilot` for the 5% runtime
  extrapolation, `--n` for full N).

**Runtime:** full N = 2,000 both substrates in 8.7 min. The 5% pilot projected
10 min; actual was faster. No new patch generation beyond the standard patches.

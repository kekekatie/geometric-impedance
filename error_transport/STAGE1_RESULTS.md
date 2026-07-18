# Stage-1 transport results (preregistered; κ=10, S_max=10·N, 20 000 trials/graph)

Inference seed `31415926` (separate from the pilot). No exclusions, no replacement,
no post-hoc tuning. Full numbers: `results/inference_stage1.json`. Wilson 95%.

## Main table (primary non-seam starts) — P_logical
| family | AB N=41 | AB N=220 | AB N=1355 | Pen N=247 | Pen N=650 | Pen N=1700 |
|--------|---------|----------|-----------|-----------|-----------|------------|
| **QC (native)** | 0.436 | 0.328 | 0.277 | 0.332 | 0.291 | 0.260 |
| clean grid | 0.420 | 0.335 | 0.274 | 0.350 | 0.304 | 0.271 |
| matched-defect grid | 0.401 | 0.301 | 0.250 | 0.307 | 0.273 | 0.234 |
| rewire (secondary) | 0.441 | 0.366 | 0.316 | 0.385 | 0.332 | 0.281 |

(heal + logical + censored = 20 000 each; censored ≤ 1.3% everywhere, as designed.)

## Reading (disciplined — leading effect first, then the residuals)

**0. The leading effect is generic, not geometric.** P_logical is large (0.23–0.44),
falls with N, and tracks **~1/log(N)** — the winding-angle statistics of a 2-D random
walk (all substrates behave similarly at leading order). Two defects that start
adjacent usually re-annihilate fast (median ~20 steps), but the annihilation-time
distribution has a heavy tail, and the tail walks wind the torus. So the dominant
signal is shared by *every* substrate; geometry lives in the **small residual
differences**, which is where the controls earn their keep.

**1. QC ≈ clean crystalline grid.** Aperiodicity *per se* does not markedly change
logical transport. AB QC is statistically indistinguishable from the clean grid
(e.g. N=1355: 0.277 [0.271,0.283] vs 0.274 [0.268,0.280], CIs overlap). Penrose QC
sits **slightly below** the clean grid (N=1700: 0.260 [0.254,0.266] vs 0.271
[0.264,0.277] — just separated; clearer at N=247). So the organised weave, if
anything, mildly *suppresses* logical winding for Penrose and is neutral for AB.

**2. The key controlled contrast: QC > *randomly* defect-matched grid — everywhere, CI-separated.**
The matched grid has the **same N, mean degree, defect fraction, and degree
histogram** as its QC native — the only difference is that its defects are placed at
**random** rather than organised. Result: the QC winds **more** than the matched grid
at every substrate and size (e.g. Pen N=1700: 0.260 [0.254,0.266] vs 0.234
[0.228,0.240]; AB N=1355: 0.277 vs 0.250 — all separated). So the QC's transport is
**not** reproduced by "a crystal carrying the same weak-disorder burden."

> **Correction (GPT review, owned):** the supported pattern is
> **QC ≈ clean grid > random-defect grid**, *not* "QC differs from both." The
> clean-grid difference is a whisker (AB: identical; Penrose: marginal), so the
> claim is **not** that quasicrystalline wiring independently changes winding. The
> claim the table supports is narrower and still real: **mean degree, degree
> histogram, and defect count do not determine transport — the spatial/higher-order
> organisation of the defects does.** The random matched defects *suppress* winding
> (traps/bottlenecks from clumping); the QC's more even defect field does not.

**3. But name the confound honestly.** *Why* does organised placement wind more than
random placement? The matched grid's defects are Poisson-random and therefore
**clumpier** (dispersion χ² ≈ 12–18) than the QC's near-uniform defects (χ² ≈ 8–10,
from Finding 6). Clumpy random defects create local **traps** that promote quick
local annihilation (→ lower P_logical); the QC's more *uniform* (hyperuniform-like)
defect field traps less (→ higher P_logical). So the QC-vs-matched gap may reflect
**defect spatial uniformity / hyperuniformity** as much as quasicrystalline motif
organisation — the present controls do not fully separate these. A hyperuniform-defect
crystalline control would be the clean follow-up (flagged, not run).

**4. Random weak disorder *lowers* logical winding; long-range rewiring *raises* it.**
matched-grid < clean-grid everywhere (dispersed defects suppress winding, ~10–15%
relative), and rewire > everything (longer edges spread the walk faster → more
winding). Both are sensible and bound the effect sizes.

**5. Penrose vs AB (matched N).** Near-equal at the small band (N≈220–247: AB 0.328
vs Pen 0.332, overlapping). At the large band AB N=1355 (0.277) vs Pen N=1700 (0.260)
Penrose is lower, but N is not equal (1355 vs 1700) and P_logical falls with N, so
that gap is **partly a size mismatch**, not a clean golden-vs-silver effect. No strong
golden-vs-silver claim is warranted from these sizes.

**6. Seam-start robustness.** Seam-edge starts give P_logical within ~0.5–1% of the
non-seam primary at every QC size (e.g. Pen N=1700: 0.268 seam vs 0.260 non-seam) —
the result is robust to the start rule.

## Bottom line (neither a null nor fireworks)
- Aperiodicity by itself does **not** dramatically change logical error transport:
  **QC ≈ clean crystal** at leading order, all governed by generic 2-D winding.
- The one **CI-robust geometric signal** is **QC > *randomly* defect-matched grid**:
  the same defect *burden* placed *organised/uniformly* (QC) produces more logical
  winding than placed *randomly* (matched grid). Equivalently, **random matched
  defects suppress winding (trapping); the QC's even defect field does not.** So
  degree + histogram + defect count **do not determine transport** — arrangement does.
- **Caveat carried openly:** that signal is plausibly driven by defect **uniformity /
  hyperuniformity** rather than quasicrystalline organisation as such; a
  hyperuniform-defect crystalline control is needed to separate them (**built + run as
  the follow-up discrimination test — see `STAGE1B_DISCRIMINATION.md`**).
- **Two statistical cautions (GPT):** (i) the matched-grid result here is **one graph
  realisation per size** — walker CIs capture Monte-Carlo but not graph-to-graph
  variance; the follow-up runs a **~10-graph ensemble** to make the graph the
  statistical unit. (ii) the **1/log N** size trend is a *candidate description*, not
  a claimed law — checked against alternatives in the follow-up.
- Effects are **small residuals** on a large generic background; nothing here supports
  a strong "quasicrystals impede/facilitate error transport" headline. It supports a
  careful statement about *organised vs random defect fields*.

*Stage-1 numbers above are FROZEN. The follow-up (ensemble, spatial diagnostics,
hyperuniform control, scaling fits) is a labelled discrimination test that adds to —
never retunes — this table. See `STAGE1B_DISCRIMINATION.md`.*

*All 30 runs (24 primary + 6 seam robustness), exact counts, and Wilson intervals in
`results/inference_stage1.json`. Reported in full; no runs excluded.*

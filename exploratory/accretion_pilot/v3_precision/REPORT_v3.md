# Report v3 — finite-precision readout

*Plain-language write-up, written after the run. Register: speculative
exploration; not a confirmatory study, not cosmology. Bounded follow-up to v2
(commit `cab9254b9d7713a65c314ca81f45c2d378ab60ba`). Rules fixed in advance in
[`DESIGN_NOTE_v3.md`](DESIGN_NOTE_v3.md). We changed only the reader. 200 seed
pairs, v2 checkpoints, quantiser grid Δ ∈ {0, 0.001, 0.01, 0.1, 0.5, 1.0}.
Reproduce: `python accretion_pilot_v3.py`.*

## The question

Does Growing's history-discrimination advantage survive **imperfect measurement of
edge weights**, particularly near saturation?

## What we did

We replayed the *identical* v2 worlds (same dynamics, seeds, RNG streams,
histories, and the activation-time-and-count matched control — v3 imports v2's code
directly), and read each present edge's weight through a deterministic quantiser
`w_read = Δ·floor(w/Δ + 0.5)` before computing the same symmetry contrast `M`.
Topology, coordinates and edge presence stay perfectly readable; only weight
*precision* is degraded. For Δ>0 the contrast is `M = Δ × (exact integer sum of
signed bin counts)`, so its sign is computed in integer arithmetic and no float
artefact can invent a residual sign.

**Dynamics unchanged (verified).** The exact reader (Δ=0) reproduces v2's saved `M`
for all 200 seeds × both histories × all checkpoints × Fixed/Reinforced/Growing to
1e-4 (v2's CSV rounding); see
[`results/validation_vs_v2.txt`](results/validation_vs_v2.txt). Measurement reads
copies of weights only.

## Headline finding

**Growing's advantage survives coarse measurement; Reinforced's near-saturation
residual does not.**

At the late checkpoint (t=10000, near saturation), discrimination AUC of the
measured contrast:

| reader Δ | Fixed | Reinforced | Growing | Control |
|---|---|---|---|---|
| exact (0) | 0.500 | 0.562 | **0.626** | 0.531 |
| 0.001 | 0.500 | 0.495 | **0.626** | 0.531 |
| 0.01 | 0.500 | 0.502 | **0.626** | 0.531 |
| 0.1 | 0.500 | 0.488 | **0.622** | 0.532 |
| 0.5 | 0.500 | 0.495 | **0.615** | 0.531 |
| 1.0 | 0.500 | 0.497 | **0.613** | 0.528 |

Growing's history signal is barely touched even by a reader that rounds every
weight to the nearest whole number (0.626 → 0.613). Reinforced's small exact-reader
edge (0.562) **collapses to chance the moment any quantisation is applied** (0.495
at Δ=0.001) and stays there. The single-world balanced-accuracy decoder and the
signed separation `mean(M_A) − mean(M_B)` agree: at t=10000 Growing keeps a robust
signed separation (+1.72 exact → +1.62 at Δ=1.0), while Reinforced's is
noise-level (−0.05, essentially zero) and Control's is small (+0.46 → +0.44).

## Why — trace versus readable memory

The tie fraction (pairs with `M_A == M_B` exactly) is the mechanism, and it is
dramatic at t=10000:

| reader Δ | Reinforced ties | Growing ties |
|---|---|---|
| exact | 0.00 | 0.00 |
| 0.001 | **0.72** | 0.00 |
| 0.01 | 0.85 | 0.005 |
| 0.1 | 0.91 | 0.01 |
| 0.5 | 0.935 | 0.075 |
| 1.0 | 0.945 | 0.12 |

Near saturation the Reinforced world's memory lives **only** in sub-0.001
differences among base-edge weights that have all climbed to ≈6. A reader that
cannot resolve 0.001 sees every such edge as the same bin, so `M_A` and `M_B`
become equal integers and 72% of pairs tie at the first coarsening step. That is a
**trace** — present in the exact state, but not a **readable memory**.

Growing's memory is different in kind. Its durable signal is carried by *which
heavy edges exist*: history-shaped diagonals sit on the worn (history-favoured)
side, and even read at whole-number precision they contribute their weight with the
right sign. That structure is topological, not sub-quantum, so quantisation leaves
it largely intact (only 12% ties even at Δ=1.0). Because topology is perfectly
readable by construction, this is memory a coarse weight-reader can still see. This
is the concrete "trace vs readable memory" distinction the exact reader had blurred.

## Imperfect measurement can *sharpen* a comparison (and is non-monotonic)

Between-model AUC differences (bootstrap over whole seed pairs) at t=10000:

- **Growing − Control:** significant at every resolution — +0.095 [0.017, 0.170]
  exact, +0.086 [0.007, 0.162] at Δ=1.0. History-shaped placement wins regardless
  of reader.
- **Growing − Reinforced:** **not** significant with the exact reader
  (+0.063 [−0.017, 0.140]) but **significant under every imperfect reader**
  (+0.130 [0.067, 0.194] at Δ=0.001; +0.116 [0.060, 0.172] at Δ=1.0). Coarsening
  removes Reinforced's fragile fine-weight residual and leaves Growing's robust
  topological signal, so the two models look *more* different to a realistic reader
  than to a perfect one.

This is a clean example of Astra's caution that coarser measurement need not make
every metric fall monotonically: Reinforced's AUC wobbles around chance across Δ
(0.562 → 0.495 → 0.502 → 0.488 → 0.495 → 0.497), and the Growing−Reinforced gap
*rises* from exact to Δ=0.001. We report the actual curves rather than assuming a
trend.

At the early checkpoint (t=400) precision hardly matters for anyone: weights are
still spread across 1–6, so even Δ=1.0 preserves the ordering (Growing AUC
0.908 → 0.901, Reinforced 0.798 → 0.784, ties stay ~0). Precision only bites near
saturation, where the surviving signal has shrunk to the scale of the bins.

## Interpretation limits

- Quantisation is **one** measurement model, and its bin grid lands on the
  saturation value 6 exactly; all conclusions are conditional on that reader. Its
  resolution is **not** a stand-in for biological, hardware, or physical noise.
- A failed readout (Reinforced at Δ≥0.001) does **not** prove the graph holds no
  recoverable history — the exact state still differs; it proves *this* reader
  cannot recover it. A successful readout (Growing) does **not** reconstruct the
  journey; it only distinguishes A from B via a coordinate-aided contrast.
- This tests weight precision only. Topology and coordinates stay perfectly
  readable; we deliberately ran no topology-only or coordinate-free analysis, and
  no noise model other than deterministic rounding.
- The comparisons across six resolutions and three checkpoints are exploratory,
  not a battery of independent confirmatory tests.

## One worthwhile next question

Growing's signal survived because topology is perfectly readable and its memory is
topological. The sharp next question isolates that: **degrade edge *presence*, not
just weight** — a reader that misses each present edge independently with some
probability p (or cannot see edges below a weight threshold). If Growing's
advantage degrades gracefully with p while Reinforced (which has no history-shaped
topology to lose) was already gone, that would confirm the memory is carried by
*which connections exist*, and measure how much topological redundancy the trace
has. That is a genuinely different reader from this run's weight quantiser, and a
natural single next step.

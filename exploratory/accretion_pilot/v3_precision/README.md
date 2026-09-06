# Accretion pilot v3 — finite-precision readout

Bounded follow-up to [v2](../v2_saturation/) (commit
`cab9254b9d7713a65c314ca81f45c2d378ab60ba`). **We change only the reader, not the
world.** v3 imports v2's dynamics unchanged, replays the identical trajectories
(same World, rules, seeds, RNG streams, histories, and the
activation-time-and-count matched control), captures each present edge's weight at
every v2 checkpoint, and reads it through a deterministic quantiser before
recomputing the history contrast `M`.

    w_read = Δ · floor(w / Δ + 0.5)        Δ ∈ { 0 (exact), 0.001, 0.01, 0.1, 0.5, 1.0 }

For Δ>0, `M = Δ × (exact integer sum of signed bin counts)`, so its sign is exact
integer arithmetic — no float rounding can manufacture a residual sign.

> Speculative exploration; not a confirmatory study, not cosmology. Isolated; uses
> nothing from the sealed studies. Not for merge or publication. v1 and v2 are
> retained unchanged in `../` and `../v2_saturation/`.

## Read in this order

1. [`DESIGN_NOTE_v3.md`](DESIGN_NOTE_v3.md) — the reader, the resolution grid, and
   measurements, **written before execution**.
2. [`REPORT_v3.md`](REPORT_v3.md) — findings: which advantages survive which
   resolutions, and trace vs readable memory.
3. [`accretion_pilot_v3.py`](accretion_pilot_v3.py) — the reader (imports v2
   dynamics).

## Reproduce

```bash
python accretion_pilot_v3.py           # 200 seed pairs, 10,000 steps; ~2.5 min
python accretion_pilot_v3.py --quick   # 20 seeds, 1,000 steps; ~10 s smoke run
```

On start the script prints a **validation gate**: the exact reader (Δ=0)
reproduces v2's saved `M` per seed (tolerance 1e-4 vs
`../v2_saturation/results/raw_metrics.csv`), proving the replay is byte-for-byte
the v2 dynamics and that measurement alters nothing.

Outputs:

```
results/config.json                              # reader + environment
results/validation_vs_v2.txt                     # exact-reader reproduction of v2
results/raw_measured_M.csv                        # M per (model, seed, history, checkpoint, Δ)
results/summary_by_resolution.csv                 # AUC, paired frac, tie frac, signed sep, balanced acc
results/bootstrap_auc_diffs_by_resolution.csv     # Growing vs control & vs Reinforced, seed-pair bootstrap
figures/discrimination_vs_resolution_v3.png
```

## Measurements (per model, checkpoint, resolution)

AUC of measured `M`; paired ordering score `frac(M_A>M_B)` (ties = ½); fraction of
paired ties; signed separation `mean(M_A) − mean(M_B)`; and a fixed single-world
decoder (A if M>0, B if M<0, ½ if 0) reported as balanced accuracy. Between-model
AUC differences with seed-pair bootstrap CIs at t = 400, 2000, 10000.

## Environment

- Python 3.11.15, numpy 2.4.6 (script imports only `numpy`, `matplotlib`, and the
  v2 module).

## One-paragraph result

Near saturation, **Growing's history signal survives even whole-number weight
reading** (AUC 0.626 exact → 0.613 at Δ=1.0), because it is carried by *which heavy
edges exist* (history-shaped topology, perfectly readable). **Reinforced's
near-saturation residual is a sub-0.001 whisper**: the first coarsening step ties
72% of pairs and pushes AUC to chance. So the exact reader's marginal Reinforced
edge is a *trace*, not a *readable memory*. Strikingly, imperfect measurement
*sharpens* the Growing−Reinforced comparison — non-significant with the exact
reader, significant under every imperfect one. Growing beats the matched control at
every resolution. See [`REPORT_v3.md`](REPORT_v3.md).

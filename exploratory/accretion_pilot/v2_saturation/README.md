# Accretion pilot v2 — timing-matched control, run toward saturation

Bounded follow-up to the [v1 pilot](../) (commit
`cc514eed26805e8448b669c813ff30776aa049ec`). Two changes only; everything else is
v1 and untuned.

1. The matched-resource control is now **activation-time-and-count matched**: it
   replays Growing's activation counts **event by event** (including during the
   imposed history), placing edges at random among canonically sorted inactive
   candidates with a separate stable RNG. Order at every event is
   *traverse → reinforce → activate*; cumulative counts are asserted equal after
   every event. This removes the v1 confound where the control's edges were younger
   than Growing's.
2. Subsequent evolution extended to **10,000 steps**, checkpoints
   `0, 100, 200, 400, 1000, 2000, 5000, 10000`.

> Speculative exploration; not a confirmatory study, not cosmology. Isolated;
> uses nothing from the sealed studies or other pipelines. Not for merge or
> publication. The v1 pilot and its results are retained untouched in `../`.

## Read in this order

1. [`DESIGN_NOTE_v2.md`](DESIGN_NOTE_v2.md) — the two changes, new observables, and
   the long-run reasoning to verify, **written before execution**.
2. [`REPORT_v2.md`](REPORT_v2.md) — findings: what changed after timing matching and
   what remains unresolved.
3. [`accretion_pilot_v2.py`](accretion_pilot_v2.py) — the experiment (numpy +
   matplotlib only).

## Reproduce

```bash
python accretion_pilot_v2.py           # 200 seed pairs, 10,000 steps; ~2.5 min
python accretion_pilot_v2.py --quick   # 20 seeds, 1,000 steps; ~10 s smoke run
```

On start the script prints two gates: a **fixture** confirming the checkpoint list
does not change the trajectory, and a **per-seed exact reproduction** of v1's
Fixed/Reinforced/Growing results (tolerance 1e-6, against `../results/raw_metrics.csv`).

Outputs:

```
results/config.json                      # parameters + environment
results/validation_vs_v1.txt             # per-seed exact reproduction of v1
results/raw_metrics.csv                  # one row per (model, seed, history, checkpoint)
results/summary_memory.csv               # frac, d_z, AUC, |M_norm|, tie fraction
results/summary_opportunity_capacity.csv # access, alternatives, edges, weight, inactive, headroom
results/bootstrap_paired_differences.csv # Growing vs Control and vs Reinforced, seed-pair bootstrap CIs
figures/memory_opportunity_capacity_v2.png
```

## New observables (defined before execution)

- **Unused growth capacity:** fraction of the 128 candidate connections still
  inactive.
- **Weight headroom:** mean over present edges of `(6 − w)`.
- **Normalised memory contrast:** `M_norm = M / total_weight` (→ 0 as the world
  saturates). These are three separate bookkeeping quantities, **not** a claimed
  universal "novelty budget".

## Environment

- Python 3.11.15, numpy 2.4.6 (the script imports only `numpy` and `matplotlib`;
  matplotlib 3.11.1 used for the figure).

## One-paragraph result

After fixing the timing confound, Growing still carries more durable, more
discriminable history than the random-placement control (memory-AUC advantage
significant at every horizon, +0.095 [0.017, 0.170] even at 10,000 steps), while
their opportunity and memory *magnitude* converge as the world saturates. Memory
*magnitude* nearly vanishes (`|M_norm|` → ~0.002) yet the *sign* stays above
chance — a tiny signed residual remains orderable after strength is gone.
Structural convergence toward all-active / all-weights-6 is confirmed analytically
and approached (but not reached) by 10,000 steps. Two confounders remain open:
placement locality near the probe, and unequal evolved weights. See
[`REPORT_v2.md`](REPORT_v2.md).

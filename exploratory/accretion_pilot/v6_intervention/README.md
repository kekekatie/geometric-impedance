# Accretion pilot v6 — crossed initial conditions (a 2×2 intervention)

Bounded follow-up to [v5](../v5_onebit/). We intervene on **initial conditions
only**; the movement/reinforcement/growth rules are v2's, unchanged. v6 imports v2's
dynamics, builds the deterministic post-history Growing states for histories A and B,
extracts original-edge weights (`W_A`,`W_B`) and diagonal sets (`T_A`,`T_B`), and
crosses them into four worlds:

    W_A+T_A (intact A)   W_A+T_B (crossed)   W_B+T_A (crossed)   W_B+T_B (intact B)

All four share initial edge count, total weight and original-edge weight multiset;
only the spatial arrangement differs. Each is evolved under the unchanged Growing
rules for 10,000 steps (200 paired seeds, common random numbers) and read with the
**frozen v5** added-diagonal one-bit reader `S_high = Σ s(e)·1[w_e ≥ 5.5]`.

**Question:** does the later four-traversal footprint follow the initial
original-edge reinforcement (W), the initial diagonal placement (T), or their
interaction?

> Speculative exploration; not a confirmatory study, not cosmology. Isolated; uses
> nothing from the sealed studies. Not for merge or publication. v1–v5 retained
> unchanged.

## Read in this order

1. [`DESIGN_NOTE_v6.md`](DESIGN_NOTE_v6.md) — construction, evolution, factor
   comparisons (pre-execution).
2. [`REPORT_v6.md`](REPORT_v6.md) — findings.
3. [`accretion_pilot_v6.py`](accretion_pilot_v6.py) — the intervention.

## Reproduce

```bash
python accretion_pilot_v6.py           # 200 seeds, 10,000 steps, 4 worlds; ~2.5 min
python accretion_pilot_v6.py --quick   # 20 seeds, 1,000 steps; ~5 s smoke run
```

Startup prints two gates: **construction invariants** (equal edge count/total
weight/original-weight multiset; diagonals at weight 1; initial bits zero) and
**reproduction** of intact worlds against v4's retained snapshots.

Outputs:

```
results/config.json                  # worlds, reader, construction/reproduction status
results/construction_checks.txt      # the 2x2 construction invariants
results/validation_vs_v4.txt         # intact worlds reproduce v2/v5 (per-edge, per-seed)
results/edge_snapshots_v6.npz        # retained full snapshots for the four worlds
results/summary_worlds.csv           # S_high/P_D/B0/edges/weight/headroom over time
results/factor_contrasts.csv         # weight & topology effects + interaction, bootstrap CIs
results/late_completeness.txt        # t=10000 completeness per world (reported, not dropped)
figures/four_worlds_initial_v6.png   # the four worlds immediately after construction
figures/reader_over_time_v6.png      # primary reader over time + factor effects
```

## Environment

- Python 3.11.15, numpy 2.4.6 (imports `numpy`, `matplotlib`, and the v2 module).

## One-paragraph result

Both initial ingredients matter, comparably, and neither alone suffices. Intact A/B
develop a strong mirror footprint peaking at t=2000 (mean `S_high` +5.99 / −5.78);
both crossed worlds stay near zero (+1.55, +0.92). Factor effects at t=2000: weight
+5.07 [2.44, 7.73] (|T_A) and +7.32 [4.87, 9.96] (|T_B); topology +4.44 [1.98, 6.89]
(|W_A) and +6.70 [4.26, 9.26] (|W_B) — all significant and comparable. The
interaction is negative in point estimate (mildly sub-additive) but its CI includes
0 (unresolved). The raw footprint collapses by t=10000 as saturation drives
`S_high → P_D → 0` on complete topology. A topology effect does not mean topology
stores the memory (placement can act through later weights), and vice versa. See
[`REPORT_v6.md`](REPORT_v6.md).

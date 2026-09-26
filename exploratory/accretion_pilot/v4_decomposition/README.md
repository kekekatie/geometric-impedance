# Accretion pilot v4 — reader decomposition

Bounded follow-up to [v3](../v3_precision/). **We change only the reader, not the
world.** v4 imports v2's dynamics (commit
`cab9254b9d7713a65c314ca81f45c2d378ab60ba`), replays the identical worlds (200 seed
pairs, original checkpoints, timing-matched control), captures the **full per-edge
weight snapshot** at each checkpoint (retained to `results/edge_snapshots.npz`), and
decomposes the history readout to locate its discrimination.

    s(e) = existing coordinate sign;  q_D = v3 quantiser (D in {0 exact, 1 whole-number})
    presence      P    = sum s(e)                over present edges (weight 1)
    original-edge B_D  = sum s(e)*q_D(w_e)        over base grid edges
    added-edge    D_D  = sum s(e)*q_D(w_e)        over activated diagonals
    full          M_D  = B_D + D_D                (the v3 reader)
    departure     R_D  = sum s(e)*(q_D(w_e) - 6)  over present edges

Identities `M = B + D` and `M = 6P + R` are asserted on every snapshot (integer
arithmetic at Δ=1). AUC is **not** additive; components are correlated.

> Speculative exploration; not a confirmatory study, not cosmology. Isolated; uses
> nothing from the sealed studies. Not for merge or publication. v1–v3 retained
> unchanged (v3's numbers preserved; a dated correction is appended to its report).

## Why (and the correction it carries)

v3's "topological memory" reading was wrong: at t=10000, 399/400 Growing worlds
have all 128 diagonals active (2 missing total), so topology is essentially
identical and cannot carry the signal. v4 shows the late discrimination is carried
by **weights on the added diagonals**, confirmed by a complete-topology subset where
topology is held identical and presence is exactly chance yet the full reader still
scores 0.627. See [`REPORT_v4.md`](REPORT_v4.md) and the correction in
[`../v3_precision/REPORT_v3.md`](../v3_precision/REPORT_v3.md).

## Read in this order

1. [`DESIGN_NOTE_v4.md`](DESIGN_NOTE_v4.md) — readers, identities, subset plan,
   written before execution.
2. [`REPORT_v4.md`](REPORT_v4.md) — findings, separating observation / identity /
   hypothesis.
3. [`accretion_pilot_v4.py`](accretion_pilot_v4.py) — the reader (imports v2).

## Reproduce

```bash
python accretion_pilot_v4.py           # 200 seed pairs, 10,000 steps; ~3 min
python accretion_pilot_v4.py --quick   # 20 seeds, 1,000 steps; ~12 s smoke run
```

Startup prints two gates: per-snapshot **algebraic identities** (M=B+D, M=6P+R) and
**reproduction of v3's full reader** (M at Δ=0 and Δ=1, all 12,800 values).

Outputs:

```
results/config.json                       # readers + environment
results/validation_vs_v3.txt              # exact reproduction of v3 full reader
results/edge_snapshots.npz                # retained full per-edge weights (reader-only reuse)
results/summary_by_reader.csv             # AUC/frac/ties/bal-acc/signed-sep per reader
results/bootstrap_by_reader.csv           # seed-pair bootstrap AUCs + Growing-control diffs
results/complete_topology_subset.txt      # counts + discrimination on identical-topology pairs
figures/reader_decomposition_v4.png
```

The retained `edge_snapshots.npz` holds the universe edge list, `is_original` and
`sign` arrays, and one `(n_seeds, 272)` weight matrix per `model__history__checkpoint`
(0 = edge absent) — enough for any future reader-only analysis without rerunning.

## Environment

- Python 3.11.15, numpy 2.4.6 (script imports `numpy`, `matplotlib`, and the v2 module).

## One-paragraph result

At t=10000 the presence reader is at chance (topology is complete and identical), so
the discrimination is carried by **weights** — specifically the **added-diagonal
weights** (`D` AUC 0.616 [0.562, 0.666]; Growing−control +0.117 [0.046, 0.195]),
equivalently the signed departure from saturation `R`. Early (t=400) the signal is
instead strongest in original-edge weights (0.947) with a real presence component
(0.834). The complete-topology subset (identical topology, presence = 0.500 exactly)
still discriminates at 0.627, proving weights not presence carry it. Which reader
component predicts shifts over time — reported as an observation about correlated
readers, **not** as "memory transfer". See [`REPORT_v4.md`](REPORT_v4.md).

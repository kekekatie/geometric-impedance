# Accretion pilot v5 — one bit per added diagonal

Bounded, **snapshot-only** follow-up to [v4](../v4_decomposition/). We do **not**
rerun trajectories: v5 loads v4's saved per-edge snapshots
(`../v4_decomposition/results/edge_snapshots.npz`) and changes only the reader. Same
200 seed pairs, models, and checkpoints.

**Question:** can a single bit per added diagonal — whether it has had **≥4
traversals** since activation — retain the late A/B history distinction?

**Bit (corrected):** `b(e) = 1 if w_e ≥ 5.5`. Under `6 − wₙ = 5/2ⁿ` this is exactly
"four-or-more traversals" / "rounds to 6 under the whole-number reader" — *not*
exact `w == 6` (which is only float rounding). Readers on present added diagonals
with the coordinate sign `s(e)`: presence `P_D = Σ s`, one-bit `S_high = Σ s·b`
(primary), `S_low = Σ s·(1−b)`, complement `−S_low`; identity `S_high + S_low = P_D`
asserted per snapshot; on complete topology `P_D = 0` so `S_high = −S_low`.

> Speculative exploration; not a confirmatory study, not cosmology. Isolated; uses
> nothing from the sealed studies. Not for merge or publication. v1–v4 retained
> unchanged (a dated documentation correction is appended to
> `../v4_decomposition/REPORT_v4.md`, numbers preserved).

## Read in this order

1. [`DESIGN_NOTE_v5.md`](DESIGN_NOTE_v5.md) — threshold, readers, plan (pre-execution).
2. [`REPORT_v5.md`](REPORT_v5.md) — findings.
3. [`accretion_pilot_v5.py`](accretion_pilot_v5.py) — the snapshot-only reader.

## Reproduce

```bash
python accretion_pilot_v5.py           # snapshot-only; ~10 s
```

Startup prints three gates: exact-arithmetic **threshold fixture**, **snapshot
schema** validation, and **reproduction of v4's added-edge readers** (`D0`, `D1`).

Outputs:

```
results/config.json                     # threshold + readers + environment
results/validation_vs_v4.txt            # reproduces v4 D0/D1 AUC from snapshots
results/summary_by_reader.csv           # AUC/bal-acc/paired-frac/ties/signed-sep per reader
results/bootstrap_onebit.csv            # one-bit AUC; one-bit-minus-D1 (Growing); Growing-minus-control
results/complete_topology_subset.txt    # counts, excluded seeds, subset match, identity checks, late AUCs
figures/onebit_reader_v5.png
```

## Environment

- Python 3.11.15, numpy 2.4.6 (imports `numpy` and `matplotlib` only; reads the v4 npz).

## One-paragraph result

Yes: the single bit per added diagonal retains the late distinction. Growing's
one-bit AUC is 0.796 → 0.731 → 0.619 (400/2000/10000), above chance throughout, and
late it tracks the whole-number added reader (collapsing to one bit costs an
estimated +0.003 [−0.016, 0.021] AUC at t=10000 — reported as estimate + uncertainty,
not declared equivalent; early it costs a real −0.034 [−0.055, −0.014]). On the
complete-topology subset (199 pairs, identical topology, presence = 0.500 by
construction) the bit still scores 0.621, so the late signal is a **thresholded
visitation footprint** on the added diagonals, not presence. Growing beats the
timing-matched control on the one-bit reader at every stage (+0.113 [0.039, 0.183]
at t=10000). Which reader carries the contrast shifts over time — presence early,
the ≥4-traversals footprint late — reported as an observation about correlated
readers, not "memory transfer". See [`REPORT_v5.md`](REPORT_v5.md).

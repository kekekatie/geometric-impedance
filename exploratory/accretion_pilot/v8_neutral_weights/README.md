# Accretion pilot v8 — neutral weight background, history-shaped placement

Bounded follow-up (chain v1 `cc514ee` → … → v7 `0c990b1`). We intervene on **initial
conditions only**; the movement/reinforcement/growth rules are v2's, unchanged. v8
neutralises the directional cue in original-edge weights by averaging
`W_0 = (W_A + W_B)/2` (transpose-invariant → no A/B bias) and keeps the two
history-shaped diagonal placements, building two worlds that differ **only** in
placement:

    W_0 + T_A     and     W_0 + T_B

Each is evolved under unchanged Growing rules for 10,000 steps (200 seed blocks,
common random numbers) and read with the frozen v5 reader
`S_high = Σ s(e)·1[w ≥ 5.5]`. Primary endpoint **t=2000** (pre-selected).

**Question:** can placement alone guide a later history-discriminating footprint
when the weights have no A/B directional bias?

> Speculative exploration; not a confirmatory study, not cosmology. Isolated; uses
> nothing from the sealed studies. Not for merge or publication. v1–v7 retained
> unchanged; a dated wording clarification is appended to
> `../v7_directionality/REPORT_v7.md` (numbers preserved).

## Read in this order

1. [`DESIGN_NOTE_v8.md`](DESIGN_NOTE_v8.md) — construction, reader, endpoint, analysis
   (pre-execution).
2. [`REPORT_v8.md`](REPORT_v8.md) — findings.
3. [`accretion_pilot_v8.py`](accretion_pilot_v8.py) — the intervention.

## Reproduce

```bash
python accretion_pilot_v8.py           # 200 seeds, 10,000 steps, 2 worlds; ~2 min
python accretion_pilot_v8.py --quick   # 20 seeds, 1,000 steps; ~5 s smoke run
```

Startup verifies construction invariants (W_0 transpose-invariant; T_B = σ(T_A);
matching edge count/total weight; zero initial high bits; transpose-related full
states; total weight preserved vs v6 with multiset changed — documented).

Outputs:

```
results/config.json                  # construction, reader, endpoint, environment
results/construction_checks.txt      # the invariant checks
results/edge_snapshots_v8.npz        # retained full snapshots (both worlds)
results/frozen_readouts.csv          # per condition/checkpoint: signed mean, mean|S|, sign fractions, counts
results/primary_endpoint.csv         # AUC and signed separation at 400/2000(primary)/10000, bootstrap CIs
figures/placement_only_v8.png        # AUC(T_A vs T_B) over time + signed means
```

## Environment

- Python 3.11.15, numpy 2.4.6 (imports `numpy`, `matplotlib`, and the v2 module).

## One-paragraph result

Under a neutral (transpose-symmetric) weight background, diagonal placement alone
gives only a **weak, transient early** discrimination — AUC peaks ~0.63 at t=100 and
is 0.571 [0.517, 0.621] at t=400 (signed sep +1.33 [0.26, 2.40]) as the pre-placed
diagonals get a head-start — which **decays to chance by the primary endpoint
t=2000** (AUC 0.484 [0.429, 0.537]) and stays near chance at t=10000. Both worlds
still develop large per-world imbalance (mean|S| ~10.7, matched high-bit counts
~70–71), but its direction is not steered by placement beyond the early transient.
Consistent with v6/v7: the reproducible directional footprint travels with the
weight cue; placement alone does not hold a direction against a symmetric background.
A near-chance result does not prove absence of all recoverable history nor necessity
of aligned weights. See [`REPORT_v8.md`](REPORT_v8.md).

# Accretion pilot — a world that grows without starting over

A modest, reproducible toy pilot exploring whether the *same* structural changes
in an evolving spatial graph can **preserve distinguishable memory of an earlier
journey** while **increasing useful alternatives for later movement**.

> Speculative exploration, not a confirmatory study and not a test of cosmology.
> Self-contained and isolated: uses no data, generators, or results from any other
> part of this repository. Nothing here is to be merged or published.

## Read in this order

1. [`DESIGN_NOTE.md`](DESIGN_NOTE.md) — rules, parameters, observables and
   expectations, **written before execution** (pre-registration).
2. [`REPORT.md`](REPORT.md) — plain-language findings, written after the run.
3. [`accretion_pilot.py`](accretion_pilot.py) — the whole experiment (~500 lines,
   numpy + matplotlib only).

## Reproduce

```bash
python accretion_pilot.py          # 200 paired seeds (default); ~20 s
```

Optional: `--seeds N` to change the number of paired seeds, `--outdir DIR` to
redirect output. Everything is deterministic given `BASE_SEED` (20260905); the
A-world and B-world of each model share an RNG stream (common random numbers).

Outputs (regenerated on every run):

```
results/config.json            # every parameter + environment versions
results/invariants.txt         # basic-invariant and no-memory-control checks
results/raw_metrics.csv        # one row per (model, seed, history, checkpoint)
results/summary_memory.csv     # A-vs-B distinguishability per model/checkpoint
results/summary_opportunity.csv# access, alternatives, edges, weight per model
figures/network_A_vs_B.png     # the mirror structural trace (Growing, seed 0)
figures/memory_opportunity.png # memory durability + strength + both opportunity measures
```

## Environment

- Python 3.11.15
- numpy 2.4.6
- matplotlib 3.11.1
- (scipy 1.17.1 and networkx 3.6.1 present in the environment but **not required**;
  the pilot imports only `numpy` and `matplotlib`.)

```bash
pip install "numpy>=2,<3" "matplotlib>=3.8"
```

## The three models (+ control), in one line each

- **Fixed** — movement changes nothing (no-memory control).
- **Reinforced** — traversing an edge raises its weight, `w ← w + 0.5·(6 − w)`.
- **Growing** — same reinforcement, plus: where local wear crosses a threshold, a
  short diagonal from a fixed finite catalogue switches on.
- **Growing-MatchedControl** — Reinforced with the same *number* of diagonals
  switched on, placed at random (history-blind), to separate "opportunity from
  added resources" from "memory from history-shaped placement".

## One-paragraph result

Memory is real and durable; the Fixed control stays at chance forever. Pure
reinforcement remembers but *funnels* movement (effective alternatives fall below
baseline). Growth lets memory **and** opportunity rise together, and gives the
**most durable** memory of the four models. A matched-resource control shows much
of the opportunity gain is just added edges — but history-shaped placement is what
turns those edges into durable memory and extra usable routes. See
[`REPORT.md`](REPORT.md) for numbers, caveats, and the next question.

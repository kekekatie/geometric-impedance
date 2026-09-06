# Accretion pilot v11 — substrate pilot (Penrose vs perturbed pentagrid)

Repaired construction + the bounded substrate memory experiment. Isolated; chain v1
`cc514ee` → … → v10 `0a41135`. v1–v10 preserved; a dated correction is appended to
v10's `FEASIBILITY_VERDICT.md`. No merges/publishing/sealed-study access; no periodic
or Reinforced arm.

## Central question & answer

Does quasiperiodic organisation change the persistence of history-readable footprints
vs a perturbed same-tile substrate? **No detectable difference.** At the pre-registered
primary t=2000, regular Penrose AUC 0.616 vs perturbed 0.624 — a 0.008 gap dwarfed by
the ~0.02–0.03 across-patch spread within each arm; both well above the ~0.47–0.50
no-history null; opportunity/capacity near-identical. (We did not assume it would
help.) Conditional on these geometries and this reader; "perturbed" is **not**
established as disordered, so this is Penrose vs mildly-perturbed-Penrose.

## Read in this order

1. [`DESIGN_NOTE_v11.md`](DESIGN_NOTE_v11.md) — repairs (R1 real overlap/gap checks,
   R2 robust construction, R3 production validation), the gates, and the frozen
   analysis plan.
2. [`REPORT_v11.md`](REPORT_v11.md) — findings, numbers, and limitations.
3. Code: [`substrate_lib.py`](substrate_lib.py), [`v11_validate.py`](v11_validate.py)
   (gates), [`v11_experiment.py`](v11_experiment.py) (dynamics),
   [`v11_analyze.py`](v11_analyze.py) (analysis + figures).

## Reproduce

```bash
python v11_validate.py     # ~10 s: all construction + engine gates (must PASS)
python v11_experiment.py   # ~50 min: 18 cells x 2 histories x 200 seeds x 10k steps + null
python v11_analyze.py      # ~30 s: summaries + figures
```

Gates: G1 geometry valid; G2 invalid fixtures rejected; G3 zero degeneracies; G4
diagonals unique/distinct; **G5 substrate-general engine == v2 square engine
event-by-event**; G6 regular patches not rigid-motion duplicates; G7 3 length-6
history pairs/patch. All PASS (`results/gate_report.txt`).

Outputs:

```
results/gate_report.txt, frozen_manifest.json      # gates + frozen geometry/histories
results/raw_main.csv, raw_null.csv                  # per (cell, history, seed, checkpoint) scalars
results/summary_memory_cells.csv, _arms.csv        # AUC per cell; patch/arm aggregates
results/summary_null.csv, summary_opportunity.csv  # null AUC; opportunity/capacity
results/subsample_snapshots.npz, experiment_config.json
figures/memory_v11.png, opportunity_v11.png
```

Full-edge snapshots for all worlds would be several GB (57.6k worlds × 8 checkpoints
× ~1.4k weights); only scalars are stored, plus a small compressed subsample.

## Environment

- Python 3.11.15, numpy 2.4.6 (+ matplotlib for figures); imports the v2 module for
  the engine-equivalence gate and shared constants.

## One-paragraph result

Both regular Penrose and perturbed pentagrid retain imposed-history information
(ordinary AUC peaking ~0.69 at t=100–200, decaying to ~0.55 by t=10,000, well above
the ~0.47–0.50 no-history null), and the two arms are indistinguishable in both
memory persistence and opportunity/capacity at these geometries. The repaired
validator genuinely tests overlaps/gaps (invalid fixtures rejected) and the
generalized engine is proven event-by-event identical to the trusted square engine.
The sharp order-class contrast (vs a genuine periodic approximant or a verified
disordered substrate) and a walker-accessible local reader remain the deferred next
steps. See [`REPORT_v11.md`](REPORT_v11.md).

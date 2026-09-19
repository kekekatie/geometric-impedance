# Reverse-Loop Test

Pre-registered test of whether address recovery on aperiodic projection tilings
is **positional** (a function of final position only) or **historical** (carries
memory of the route). Extends the linger experiment.

**Result: Outcome A (full equivalence) on both substrates.** See
[`FINDINGS.md`](FINDINGS.md).

## Provenance

The linger-experiment pipeline that this protocol says to reuse is **not present
in this repository**, so the walker machinery, depth/hull computation and
address-residue metric were reconstructed to the conventions the repo documents
(cut-and-project multigrids; perp-space address; window-boundary depth). The
residue definition `‖perp(final) − perp(start)‖` was independently confirmed
against the original source as correct. Details and flagged differences are in
`FINDINGS.md` (§ Provenance).

## Run

```bash
pip install numpy scipy scikit-learn matplotlib pandas

python3 run.py --pilot --n 2000   # 5% pilot + runtime extrapolation
python3 run.py --n 2000           # full run -> results/, figures/, summary.json
```

Deterministic (fixed seeds in `run.py:CONFIG`). Full N = 2,000 per substrate
takes ≈ 9 min.

## Layout

| File | Role |
|---|---|
| `geometry.py` | de Bruijn multigrid substrates (AB Z⁴, Penrose Z⁵), perp lift, window depth, zones, vertex graph |
| `walker.py` | steered walks, address residue, transit covariates, splice + cycle construction |
| `experiments.py` | Experiment 1 (spliced loops), Experiment 2 (closed loops), sensitivity control |
| `stats.py` | Cohen's d + bootstrap CI, TOST (two-sample & one-sample), KS, Benjamini–Hochberg |
| `run.py` | orchestrator: sensitivity → Exp 1/2 → Exp 3 analysis → figures → `summary.json` |
| `results/` | per-walker CSVs + equivalence/holonomy/transit comparison grids |
| `figures/` | (a) distribution overlay, (b) residue vs path length, (c) closed-loop holonomy, (d) transit-depth |
| `summary.json` | all TOST/KS/effect-size/CI outputs, seeds, patch parameters |
| `FINDINGS.md` | the memo: what was run, what was found, which outcome, anomalies |

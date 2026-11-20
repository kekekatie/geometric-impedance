# Which local witness matters?

Starting audit: `1f85f7921bf9615bfa87173eb2d77d9159e211d3`.
Branch: `experiment/local-witness-omission-2026-11-20`.
Frozen protocol/arms/geometry commit: `9434ea1d04c87ce28c77d1b059d3cde207e95911`, published before any new scores.

Run from the full repository root with Python 3, NumPy and Matplotlib:

```sh
python3 exploratory/local_witness_omission_2026-11-20/replay.py
```

The default reruns all three sites, performs preflight validation before score accumulation, independently verifies the saved CSVs and generates the result table and figure. Add `--resume` to retain completed site checkpoints; `--patch AB_1`, `--patch Penrose_1`, or `--patch Penrose_2` runs one site. The latter jobs can run independently, then `python3 exploratory/local_witness_omission_2026-11-20/report.py` combines them. `prepare.py` regenerates only the frozen geometry/arm definitions.

Files:

* `PROTOCOL.md`: precise intervention, paired scoring and validation rule.
* `results/arms.json`, `geometry.png`, `geometry.svg`: all twelve omissions and the pre-score picture.
* Per-site `.json`: baseline credits, detailed omission outcomes, preflight and sampled validation counts.
* Per-site `.csv.gz`: one row per ordinary-fault configuration; exact sums over its eight onset/free-value histories. Columns record arm credits and, for each omission, credit gained/lost and label/tie changes versus intact. Fault weight identifies the model odds weight `(0.001/0.999)**k`; each row represents eight equally weighted variants.
* `results/omissions.csv`, `summary.json`, `table.md`: twelve-arm summary; `omission_costs.png/.svg`: shared signed cost scale on the physical geometry.

The decoder, fault stream, original marginal and saved-state query helper are imported from the pinned audit ancestry. The corrected geometry adapter is `../fresh_site_address_audit_2026-11-20/audit.py`; the verified prefilter and archive reconstruction are in `../penrose_e14_route_check_2026-11-20/run.py`. No frozen source files are modified.

The omitted check still operates physically. Its thin-state parity and committed frame may retain some information about its earlier behavior; the intervention does not erase that information. It removes only its round-1/2 coordinates from the conditioning dictionary. Known-zero readings of retained checks remain present. Direct full-record restrictions and original unaccelerated marginals are checked before accumulating scores and again on a deterministic sample during scoring.

Runtime metadata can vary on replay. Gzip timestamps and SVG identifiers are fixed. These are exhaustive scores in the bounded model for three fixed sites, not uncertainty estimates across cuts or tiling families.

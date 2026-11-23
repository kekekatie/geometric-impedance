# Paired-face archive omission

Start: `6236920f087a223ca3c0d701640afbe2a89ce5e7`.
Branch: `experiment/paired-face-omission-2026-11-23`.
Pre-score protocol: `1b95282be3837da01ae8ac859f561b99f38b0ef7`.

From repository root, with Python 3, NumPy and Matplotlib:

```sh
python3 exploratory/paired_face_omission_2026-11-23/replay.py
```

This reruns the new joint omissions, checks the sealed baselines, verifies the paired per-configuration totals and renders the four-arm figure. `--site NAME` selects one of the five independent jobs; `--resume` retains completed site checkpoints. Run `report.py` to verify and redraw already completed data. Run `geometry_audit.py` for the independent one-tile comparison. No geometry regeneration or cut search is needed: all five patch definitions are frozen inputs.

AB/A/B/0 name Z-faces **kept**. All four arms keep both incident endpoint X-checks' rounds 1 and 2, all live readings, boundary parities and committed frame. Arm 0 is not thin. A retained reading with value zero remains observed; omitted coordinates are absent. A/B labels follow the user's table, including A=Z7 and B=Z1 on Penrose_1.

## Inputs and reuse

* Frozen geometry and corrected adapter/decoder: `../role_reversal_omission_2026-11-22/run_role_reversal.py` and its ancestry at `6236920...`. The original three patch JSONs are in `../aperiodic_predict_2026-11-20/results/`; AB_bal and Penrose_ear are in the role-reversal results directory.
* Sealed original-site credits: `inputs/*.json` and `inputs/*.csv.gz`, copied from `1922a7b7ff7e30f0ead0781ac6aaf3b924038783`. `inputs/manifest.json` records exact source paths, blob IDs and SHA256. Attributes preserve JSON bytes across checkouts.
* Original three sites reuse their per-configuration thin/thick/intact/single-face-omission contributions after exact aggregate verification and replay of all eight variants of every 251st configuration. Do not describe this as a new full baseline decoder replay.
* The two role-reversal sites have only aggregate sealed scores, so their baselines are replayed in full. Last-bit float differences triggered the strict initial gate; the resolution checks the unique exact weighted half-credit score encoded by each sealed value and discloses the raw differences. See `BASELINE_PRECISION.md`; no baseline is silently rounded to the displayed table precision.
* The exhaustive stream is identical across arms within each site. Original three sites have 11 X/9 Z checks; the role-reversal sites have 10 X/10 Z. Thus numeric fault-coordinate stream hashes differ between those layouts. Each is checked against its own sealed hash; all use 310 ordinary faults, 48,206 configurations and 385,648 histories.

## Outputs

Per-site JSON stores exact half-credit totals by ordinary-fault weight, weighted truth scores, signed gains/costs, reproduction mode and validation counts. Per-site gzip CSV stores one row per ordinary-fault configuration, with credits summed over its eight variants. Original odds weights `(1/999)**k` apply to every history of weight k.

`report.py` independently aggregates CSV using Decimal arithmetic, checks both conditional-cost identities, and writes `results/summary.json`, `gains.csv`, `interactions.csv`, `table.md`, and `four_arm_comparison.png/.svg`. Only elapsed-time metadata varies; gzip timestamps and SVG IDs are fixed.

The geometry audit writes `results/geometry_audit.json` and `one_tile_comparison.png/.svg`. `GEOMETRY_AUDIT.md` explains physical supports, boundary changes, face neighbours and logical-support changes. The manuscript is not edited.

The first two role-reversal replays completed their CSVs but stopped at literal float equality. `recover_complete_csv.py --site NAME` verified those complete files, repeated the full-scan sample, and replayed deterministic configuration blocks before accepting them. Recovery-only validation counters and elapsed time are flagged in JSON. A fresh full replay produces the same scores, with the normal 192 full-scan comparisons per site; recovery-only extra checks need not have identical counters. Independent aggregation checks 241,030 CSV rows in either case.

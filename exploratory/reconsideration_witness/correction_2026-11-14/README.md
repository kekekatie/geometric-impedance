# Corrected distance-3 rerun

This directory is additive. The parent `stage2_surface.py`, `stage2_run.py`, original report and original `stage2_handback.json` remain the historical baseline at `842fdc3d367a5701e35826ff40bbe36f1941a761`.

Read `PROTOCOL_AMENDMENT.md` first. Its pre-outcome commit is `fa18eb2`. It fixes the exact scope, ordered attribution ladder, ordinary-noise frame definition, tie convention, actual serialization checks and accounting terminology before corrected execution.

## Replay

From this directory, with Python3 and NumPy installed:

```sh
python3 src/tests.py
python3 src/legacy_regression.py
python3 src/run.py all
python3 src/diagnose.py
python3 src/summarize.py
```

The recorded environment is the existing isolated CPython3.12.16 / NumPy2.2.6 environment on Windows. `src/run.py all` executes the five fixed variants in order, stops on a failed legacy gate or invariant, then starts four new Python processes to restore the primary arm-specific JSONL files. `src/diagnose.py` checks the historical corner and one highest-weight primary disagreement, if any, without broadening the ensemble.

Results go to `results/`. Runtime arm-state JSONL files, expected answers and restored answers go to `runtime/` (ignored), or to the absolute directory named by `DISTANCE3_FIX_CACHE`. The recorded run sets that variable to the external workspace `work/distance3-fix-cache`. The cold decoder process is given only its arm's state-file path by convention, its own arm argument, and static code/configuration. Expected-answer files are not read by the worker function. This is process and data-flow separation, not an OS sandbox.

For an interrupted run, preserve the failed log and resume the named stage with `python3 src/run.py A_legacy`, `B_xor`, `C_prior`, `D_ties`, or `E_frame`; run B onward only after the legacy gate has passed for the same untouched source. Then `python3 src/run.py cold` uses the primary's complete runtime files. A primary rerun recreates those files. All individual stages recompute their ensemble; they do not treat saved result files as fresh execution. No later scientific run is silently substituted for a failure.

## What changes the experiment

- B changes simulator histories by XORing overlapping contributions; it can change predictions, truth labels and archive activity relative to the buggy baseline.
- C changes evaluation and inference weights to Bernoulli odds within the same bounded ensembles.
- D uses normalized epsilon ties. Hard labels remain deterministic representatives; the additional expected-score fields account for final ties with a shared fair coin across arms, as specified in the amendment.
- E adds a two-bit report-blind committed MAP frame and conditions candidate histories on that statistic. The frame's exact independent-noise prefix map is computed by a17-bit probability convolution. It is not a saved oracle logical value.
- Report parameterization, schema validation, file restoration and query-accounting corrections are structural/validation fixes. Their fixed-site legacy gate checks that they do not by themselves change the historical bulk numbers.

The ordered deltas are conditional on earlier changes; they are not a full factorial attribution. Hard scores provide the before/after comparison to the historical hard-tie baseline. Expected tie scores are additional outputs, not silently substituted for historical scores.

## Accounting and limits

`payload_max` and `payload_weighted` are idealized packed **deadline** payload bits, not temporal peaks or actual Python memory. Archive coordinates cost5 bits each; the primary thin-side states additionally carry2 frame bits. `wire_max` and `wire_weighted` are actual compact JSON byte lengths including schema, arm/model identifiers, coordinates, delimiters and field labels. Wire sizes depend on this diagnostic format and model-name length and are not a production bit-codec benchmark. The report is supplied externally after state formation and its transport size is not included in state-byte sizes. Decoder tables, runtime workspace and container overhead are not counted as retained experimental payload.

Both archive arms contain identical event records. Their reconstructed old-detector counts are8 versus24, including absent-event zeros; stored fired-event count is a different metric. The state builder accepts only the prefix through round3, computes the commitment without a report, then appends round4 checks before accepting the report. This establishes an explicit deadline-snapshot sequence; no full streaming temporal-peak claim is made.

No scientific edge-loss or distance5 run is included. Small alternative-site/onset checks are routing regressions only. Exact finite sums use ordinary floating-point arithmetic; this is not an exact-arithmetic proof or a circuit-level physical-loss model. The full Bernoulli precommit frame model and per-sector truncated report-aware inference model have explicitly different bounds, specified before execution.

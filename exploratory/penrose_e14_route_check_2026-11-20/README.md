# Penrose_1 e14: one additional archive check

Starting SHA: `fdeaa32a988224f98dc10b99175c99d806862522`, the tip of `claude/aperiodic-predict-2026-11-20` when this task began. Isolated follow-up branch: `experiment/penrose-e14-route-check-2026-11-20`.

**Pre-score prediction commit:** `3174b2350faf6cdfa89cd3f02da0eb7faa17d79f` (published before running the decoder; exact tree of local `c034b58`). It contains the deterministic geometric choice, full candidate list, labelled picture and the explicit adapter-mapping qualification.

One command from the repository root, with Python 3, NumPy and Matplotlib:

```sh
python3 exploratory/penrose_e14_route_check_2026-11-20/run.py
```

This regenerates the frozen prediction, runs all 385,648 histories for the original and correctly mapped queries, verifies round-0 redundancy and the decoder checks, and writes `results/scores.json` plus `results/config_scores.csv`. The CSV has one row per ordinary-fault configuration, its original odds weight, and each arm's summed half-credit over the eight shared onset/free-value variants. No histories are sampled for the primary scores, and no bootstrap interval is used for this exhaustive conditional-model comparison. The runtime field in scores.json naturally varies on replay.

For geometry alone: `python3 exploratory/penrose_e14_route_check_2026-11-20/predict.py`.

## Source/data flow

All source paths below are pinned by the starting SHA and remain unchanged:

* `exploratory/aperiodic_predict_2026-11-20/results/Penrose_1.json`: geometry, HX/HZ, fixed scored `logical_Z={8,10,16}`. The loss is geometric edge e14, data qubit q10.
* `exploratory/aperiodic_predict_2026-11-20/src/paired_run.py`: same FreshPatchCode adapter, ordinary pool, exhaustive config ordering, eight variants and truth-credit rule.
* `exploratory/aperiodic_decoder_pilot_2026-11-19/src/patch_decoder.py`: unchanged original PatchDecoder at frame/inference caps (3,3).
* `exploratory/reconsideration_witness/distance5_2026-11-16/src/nd_infer.py`, `nd_surface.py`, `nd_run.py`: original frame, marginal, simulator and XOR composition.
* `exploratory/aperiodic_predict_2026-11-20/results/paired_results.json`: published rounded baseline gains, checked automatically.

Every history is serialized once using the original site-independent archive encoding, before choosing the queried check set. Both extensions add exactly rounds 1 and 2 of their chosen X-check. Restored queries read only the archive, live record, boundary parity and saved frame. The geometric correction changes only two queried Z-check addresses; it does not rebuild the model, change the lost site or alter truth.

The original `check_index` helper assumes ten X rows, but Penrose_1 has eleven. Therefore the original implemented diamond reads X4,X6,Z0,Z6. The intended incident diamond reads X4,X6,Z1,Z7. The reported continuity primary keeps the former to reproduce the quoted 0.12157-point gap; the correctly mapped result is separate. Neither result should be substituted silently for the other.

An exact acceleration prefilters candidates by the live detector bits and boundary parity already implied by each query. It retains all matching candidates for either erasure value, sorts them back into original enumeration order, then calls the original marginal code. It does not change a decoder cap or approximate probabilities. Every 2,003rd history is checked against the original unaccelerated marginal with an empty cache, including both extensions and both baselines. Direct-data comparisons separately check the archive query implementation. Round-0 redundancy and whole/thick agreement are checked on every history.

`results/prediction.png` is the pre-score picture. Its Z1/Z7 labels show the intended geometric diamond; the old implementation's Z0/Z6 are not the labelled incident faces. `results/prediction.json` lists all outside checks, equal-distance pairs and tie-breaking. Matching is in the mixed X/Z bipartite incidence graph, not Euclidean distance or a single-sector graph. These matched X-checks observe the conjugate fault sector; route membership alone is not a theorem that they reveal the scored logical ambiguity.

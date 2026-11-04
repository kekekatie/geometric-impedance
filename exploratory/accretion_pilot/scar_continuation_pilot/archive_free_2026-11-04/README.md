# Archive-free scar continuation — 2026-11-04

Can a worker retaining **only** the specified boundary band continue legally past
the recorded jams toward step 44, **without consulting the deleted interior**, and
how does it compare to the audited full-patch scar scheduler? (Follows the scar
pilot and Astra's audit `audit/scar-continuation-2026-11-03`; the audit verified
the full-patch baseline and flagged that archive-free construction was never
actually tested.)

**Result (plain).** On all eleven recorded B-jams the archive-free radius-2
`ActiveSkin` worker reproduces the full-patch scheduler **exactly, every step, to
step 44** (identical candidates, decisions, placements, frontier, PRNG, scars; 0
illegal; no divergence). The deleted interior is unnecessary — the growth decisions
live within ~1 edge of the frontier, inside the 2·S band. The retained band is
radially thin (~2·S) but **not thin in count** (47–63 % of the patch retained; it
bulges inward to keep each scar's neighbourhood). Readout on the worker's bands
reproduces the audit's conditional positive-area B readout (111 B / 64 ambiguous /
353 reader-incompatible / **0 A** over 528 windows), with A a zero-area segment in
some cases — not symbolic exclusion. See [HANDBACK.md](HANDBACK.md) and
[protocol/PROTOCOL.md](protocol/PROTOCOL.md).

Nothing physical/topological or indefinite is claimed; construction is from exported
jam states, not from the original seed; the frozen engine/reader/thresholds and all
prior directories are untouched.

## Layout / reproduce

```
protocol/   PROTOCOL.md (frozen before outcomes) + PROTOCOL_DEVIATIONS.md
src/        af_common, scar_skin (lockstep worker+evaluator), isolated_worker
            (serialize/cold-restart/spawned process), run_experiment, readout, make_figure
tests/      test_archive_free.py (equivalence/cavity/scar-legality/cold-restart/persistent-scars/metadata)
results/    comparison.json, controls.json, readout.json
input/      worker_band_exports.json (serialized worker jam/final bands)
figures/    archive_free_w7.png (retained band vs genuinely deleted space)
```

```bash
export EFP_SNAPSHOT=<frozen 84130b9 worktree>/exploratory/accretion_pilot/expansion_front_paper
export MPLBACKEND=Agg
# fork cache: (cd ../../jam_repair_pilot/src && python3 build_fork_cache.py)
cd src
python3 ../tests/test_archive_free.py
python3 run_experiment.py
python3 readout.py
python3 make_figure.py
```

The frozen hollow-band engine (`active_skin_engine.py`) and frozen reader are
imported unchanged; the worker runs archive-free (pruned band only; spawned-process
and cold-restart controls confirm it depends solely on the declared retained state).

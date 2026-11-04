# Protocol deviations (dated)

Deviations from `PROTOCOL.md`, recorded rather than edited into the original.

## 2026-11-04

- **Worker start: replay-from-seed, with cold-start as a verified control.** The
  main lockstep comparison grows the archive-free `ActiveSkin` worker from the fork
  seed with scar-tolerance enabled throughout (the pre-jam portion is faithful
  **replay**, clearly labelled; the worker is a pruned radius-2 band at *every*
  step and never holds the full patch). The protocol's "export the jam band once
  and cold-start the worker from it" is implemented as a **control**
  (`results/controls.json`): the serialized jam band is reloaded into a fresh
  worker (in-process and in a spawned process) and reproduces the exact
  continuation. This proves the continuation depends only on the declared retained
  state, which is the intent; it is a disclosed choice, not a hidden archive.

- **Readout jam band.** The jam-checkpoint band scored by the readout is the frozen
  prune (`skin_of`) of the recorded jam full patch — i.e. the worker's retained
  band at the *start* of the jam step, matching the audit's jam checkpoint. The
  final band is the worker's radius-2 band at step 44.

- **Evaluator = full-patch scar scheduler.** The comparator is the audited
  `scar_continuation.patient_scar` run on the full patch (the baseline Astra
  verified), from the identical seed/stream. The identical function is run on the
  worker's band; only the substrate differs. This is exact-equivalence testing
  against the audited baseline, kept separate from any ordering control (none was
  needed: no divergence occurred, so historical insertion order was reproduced).

## Notes

- No matching rule, reader threshold, scheduler policy, or frozen file was changed.
- The frozen `active_skin_engine.py` (ActiveSkin, inventory, worker) is imported
  unchanged; the scar-tolerant scheduler and the comparison/isolation harness are
  the only new code.
- No fresh worlds, longer horizons, repair searches, or matching-rule relaxation.

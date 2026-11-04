# HANDBACK — archive-free scar continuation

*2026-11-04. For Katie / Astra / Argon. A bounded computational-geometry study of
decorated Penrose tiles; an informative negative result would have been an
acceptable completion. No matching rule, reader threshold, scheduler policy, or
frozen file was changed. Branch `claude/scar-archive-free-2026-11-04`, based on the
audit tip `3dc43ea`; frozen engine/reader `84130b9`. The protocol was committed
before any new outcomes (`archive_free_2026-11-04/protocol/PROTOCOL.md`).*

## Plain-language summary

**The question.** My earlier scar-continuation pilot grew on the *full* patch and
only extracted a band afterward — so it never actually tested whether the band
*alone* suffices. Astra's audit verified the full-patch baseline and flagged
exactly this gap. This experiment closes it: a worker that retains **only** the
radius-2 boundary band (plus an explicit true-frontier tag) continues past each
recorded jam, and I compare it, step by step, against the audited full-patch
scheduler from the identical jam checkpoint and PRNG — with the worker genuinely
unable to see the deleted interior (it runs in a separate process receiving only
the serialized band).

**The result — a clean positive.** On **all eleven** recorded B-jams the
archive-free band worker reproduces the full-patch scheduler **exactly, at every
step, to step 44**: identical candidate sets, forced/free decisions, placements,
true-frontier identities, PRNG transitions and scar labels, with **zero** illegal
placements and no total arrest. The deleted interior is genuinely unnecessary for
the growth decisions — everything the scheduler needs lives within ~1 edge of the
frontier, well inside the 2·S band. *Operationally, on these cases, the retained
band IS the memory needed to keep building.*

**The honest caveat it also makes concrete.** The band stays **radially thin**
(every retained tile is within ~2.7·S of the true frontier — a 2·S band plus a
tile radius), but it is **not thin in count**: at step 44 the worker still retains
**47–63 % of the full patch** (e.g. w7: 644 of 1028 tiles). It is a thick ring
around a long, growing boundary, and — because a pinned scar stays a boundary edge
forever — it **bulges inward to keep the 2·S neighbourhood of every scar** (clearly
visible as the inward lobes around the two red scar clusters in
`figures/archive_free_w7.png`). Archive-free continuation here means *keep the
whole active ring, scar neighbourhoods included* — not *keep only a thin frontier*.
Retained count and radial reach are measured per case (`results/comparison.json`).

**What it does and does not establish.** It establishes that, from the exported
jam states, construction can proceed to the finite step-44 horizon using only the
declared retained state (band + true-frontier tags + PRNG + scars), reproducing the
full-patch baseline exactly. It does **not** establish archive-free construction
from the original seed, indefinite growth, a thin band, or any physical/topological
memory; and the reader results below remain the audit's *conditional, selected-
subset, positive-area* readout, not a continuously transported trace.

## The five questions

1. **Can the declared retained state reconstruct the candidate decisions?**
   **Yes.** The worker's per-edge candidate inventory (`active_skin_engine.inventory`)
   equals the full patch's at every true-frontier edge, every step, all eleven
   cases — computed on the band alone.

2. **Does the worker reproduce the comparator trajectory?**
   **Yes, exactly.** `exact_equivalence = True` for all eleven: candidate sets,
   ordered candidate lists, forced/free decisions, PRNG state before/after,
   placements (decorated keys), frontier identities, and scar labels all match the
   audited full-patch scar scheduler. **First divergence: none.**

3. **Does it continue legally to step 44?**
   **Yes.** All eleven reach step 44 with real placements every step, **0** illegal
   additions (every placement passes frozen `Patch.legal`; final stars/overlaps
   clean via the evaluator), and no `total_arrest`.

4. **What endpoint subset readout survives under the declared rule?**
   Applying Astra's precommitted 528-window geometry-defined scan to the **worker's
   own retained bands** (same label-blind procedure at jam and final) gives, in
   total, **111 B / 64 ambiguous / 353 reader-incompatible / 0 A / 0 failures** —
   *identical to the audit's full-patch grid* (as it must be: the worker band equals
   the full-patch retained band). The largest-compatible subset selects
   **correct (B)** for every case at both checkpoints. But the independent box-free
   check shows the closed A intersection is a **zero-area segment** for the
   w15/w19/w28-s0 family and **infeasible** otherwise — so "the positive-area reader
   selects B" is **not** symbolic exclusion of A for the segment cases. Headline
   subset sizes differ between checkpoints (e.g. w7 152→286 tiles), but per the
   audit's correction that is **not** a clean "readable-fraction increase" and no
   such claim is made. This is conditional, selected-subset, positive-area readout —
   not a universally reliable local reader and not a continuously transported trace.

5. **What additional metadata or retained material was necessary?**
   - **Metadata:** the explicit **true-frontier boundary** (`ActiveSkin.boundary`,
     an edge → (p, q, r, owner) map built incrementally during archive-free growth),
     disclosed as *augmented retained state*. It is what lets the worker grow only
     at the true frontier and never into the deletion cavity. Audited to contain no
     full patch, deleted-tile list, archived lift, candidate menu, or hypothesis.
   - **Material:** the radius-2 band, which accumulates scar tissue (47–63 % of the
     full patch retained at step 44; reach measured per case). No deleted interior,
     archived lift, occupancy map, candidate menu, future placement, or A/B
     hypothesis entered the worker.

## Controls (all pass)

- **Spawned-process isolation:** the worker runs in a separate `spawn` process
  receiving only the serialized band + STEP/STOP; its continuation matches the
  in-process worker exactly (w7, w5).
- **Cold restart:** reloading the serialized jam band into a fresh worker
  reproduces the exact continuation — the continuation depends only on the declared
  retained state.
- **No inward cavity growth:** the worker's frontier is the explicit true frontier
  only; `frontier()` never exposes a deletion-cavity edge, the worker band is a
  subset of the full patch, and placements match the interior-filled full patch
  (which cannot grow inward).
- **Scar-adjacent legality / persistent scars / metadata audit:** pass (see
  `tests/test_archive_free.py`, `results/controls.json`).

## Reproduce

```bash
export EFP_SNAPSHOT=<frozen 84130b9 worktree>/exploratory/accretion_pilot/expansion_front_paper
export MPLBACKEND=Agg
# fork cache: (cd ../../jam_repair_pilot/src && python3 build_fork_cache.py)
cd archive_free_2026-11-04/src
python3 ../tests/test_archive_free.py     # controls
python3 run_experiment.py                 # 11-case lockstep + isolation/cold-restart/metadata
python3 readout.py                        # 528-window scan on worker bands
python3 make_figure.py                    # figures/archive_free_w7.png
```

Machine-readable: `results/comparison.json` (per-case exact-equivalence, first
divergence, scar-tissue trajectory), `results/controls.json`, `results/readout.json`.
Figure: `figures/archive_free_w7.png` (retained band vs genuinely deleted space).
No merge, no force-push.

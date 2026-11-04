# Verification supplement — archive-free scar continuation

*2026-11-04. Verification supplement to the archive-free scar-continuation experiment
(commit `129389d`, branch `claude/scar-archive-free-2026-11-04`). For Katie / Astra /
Argon.*

This supplement **re-runs and independently checks** the experiment's headline claims
with stronger procedures than the original harness used, after Astra reviewed the source
and saved results without independently re-running them. It changes **no** scientific
policy: the retention rule, scheduler, matching rules, reader thresholds, cases, and the
step-44 horizon are all unchanged, and the historical outputs are preserved. Where a
check revealed that the *wording* outran what was actually verified, the finding is
reported here honestly; no claim was relaxed to make it pass, and nothing in the frozen
engine, reader, or prior directories was touched.

Everything below is produced by code in this directory
(`archive_free_2026-11-04/supplement_2026-11-04/`), writing machine-readable results to
`results/` and serialized inputs to `input/`. Reproduction commands are at the end.

---

## 1. Headline outcome of the verification

All eleven recorded B-jam cases pass every strengthened check:

| check | result (11/11) | artifact |
|---|---|---|
| **Ordered** equivalence to the full-patch comparator (placements, true frontier, candidate *enumeration order*, PRNG **before and after** each step) | ✅ all 11 | `results/verification.json` |
| Set-inventory agreement (kept **distinct** from ordered) | ✅ all 11 | `results/verification.json` |
| Each worker placement legal vs an **independent** cumulative full-history patch, checked **before** adding, in placement order | ✅ all 11 (440–829 placements/case) | `results/verification.json` |
| Pre-scar restart alignment at the **top of the jam step** (geometry, ordered frontier, PRNG, empty scars) | ✅ all 11 | `results/verification.json` |
| **Spawned-process** restart from the actual pre-scar state == full-patch == uninterrupted worker, step jam..44, in order | ✅ all 11 | `results/prescar_restart.json` |
| Endpoint decorated vertex stars valid; no over-full vertex | ✅ all 11 (0 invalid) | `results/verification.json` |
| Positive-area triangle overlaps in the cumulative history | ✅ all 11 (0; max area ≤ 2.6e-16) | `results/verification.json` |
| Deep retained-state metadata (boundary owners/coords, caches, cavity exclusion, serialized fields, pre-scar == jam band) | ✅ all 11 | `results/verification.json` |
| Real scar-adjacency exercised and legal (w7) | ✅ 18/18 | `test_supplement.py` |
| Step-44 endpoint geometry identical to the original export (→ readout reuse) | ✅ all 11 (sorted key list identical) | `results/endpoint_geometry.json` |

Per-case summary (`results/verification.json`):

```
case       jam  n_band   placements  ordered  set  prescar(g/f/p)  stars(cmpl/bad/over)  overlaps  blocked labels
w5-B-s0    42   450=450  748         ✓        ✓    ✓✓✓             427/0/0               0          5      2
w7-B-s0    23   315=315  829         ✓        ✓    ✓✓✓             456/0/0               0         12     12
w7-B-s1    23   315=315  829         ✓        ✓    ✓✓✓             456/0/0               0         12     12
w15-B-s0   39   551=551  440         ✓        ✓    ✓✓✓             456/0/0               0         12     12
w19-B-s0   39   551=551  440         ✓        ✓    ✓✓✓             456/0/0               0         12     12
w19-B-s1   43   582=582  701         ✓        ✓    ✓✓✓             586/0/0               0          4      4
w21-B-s0   42   450=450  748         ✓        ✓    ✓✓✓             427/0/0               0          5      2
w21-B-s1   42   450=450  748         ✓        ✓    ✓✓✓             427/0/0               0          5      2
w28-B-s0   39   551=551  440         ✓        ✓    ✓✓✓             456/0/0               0         12     12
w28-B-s1   43   582=582  701         ✓        ✓    ✓✓✓             586/0/0               0          4      4
w29-B-s1   43   582=582  701         ✓        ✓    ✓✓✓             586/0/0               0          4      4
```

(`n_band` is the worker's pruned radius-2 band at step 44; `prescar(g/f/p)` = geometry /
ordered-frontier / PRNG alignment at the top of the jam step.)

---

## 2. What each strengthened check actually verifies

### 2.1 Pre-scar restart from the *actual* jam state (was: restart after the first scar batch)

The original cold-start/spawned controls serialized the worker at `serialize_at=jam`,
which in the lockstep harness captured the band **after** the first scar-tolerant batch
had already been placed (for w7 the snapshot was the post-step-23 band; the restart began
at step 24). That tests resumption from mid-continuation, not from the jam itself.

This supplement serializes the retained worker state at the **top of the jam step, before
the first scar-tolerant batch**. Before using it, it verifies the serialized checkpoint
against the frozen jam band (`af_common.jam_prep` → `band`, the frozen `skin_of` prune of
the recorded jam full patch):

- `geometry_matches_frozen_jam`: the serialized tile set equals the frozen jam band
  (e.g. w7: 315 == 315 tiles), decorated-key for decorated-key;
- `ordered_frontier_matches`: the worker's ordered true frontier equals the full patch's;
- `prng_matches_evaluator`: the serialized PRNG state equals the evaluator's at that step;
- `scars_empty`: no scars yet (the first scar is pinned *during* the jam step).

Then a **fresh worker in a separate `spawn` process** receives only the serialized state
and runs the first scar step through 44. Its ordered placement sequence matches both the
full-patch comparator and the uninterrupted band worker, step for step
(`results/prescar_restart.json`: `restart==full: 11/11`, `restart==worker: 11/11`). The
serialized pre-scar states for all eleven cases are saved to `input/prescar_states.json`.

### 2.2 Ordered agreement, not just set agreement

The frozen `active_skin_engine.inventory(P)` returns, per true-frontier edge, the
**sorted** list of candidate tile-ids — so inventory equality is **set** equality, and
the original harness's `sorted(placed_w) == sorted(placed_e)` is likewise a set check.
"Exactly, every step" therefore was, in the original harness, a set-level statement plus
the fact that the evaluator never diverged; the *ordered* agreement claimed in prose was
inferred from determinism, not separately measured.

This supplement inspects the frozen `inventory` implementation (confirming it sorts) and
adds genuinely ordered checks, per step, computed on the band alone:

- `ordered_inventory(P)`: the candidate **enumeration order** actually produced by
  `SN.ordered(D.candidates(...))` at each frontier edge (the order free-choice consumes),
  compared worker vs full patch — not a re-sorted set;
- ordered placement sequence (not `sorted(...)`);
- ordered true frontier;
- PRNG state **before** and **after** each step (the original compared only after).

All eleven agree on all of these (`ordered_equivalence = True`), and set-inventory
agreement is recorded separately (`set_inventory_equivalence = True`). The two are now
distinguished in the record rather than conflated. `SN.ordered` is a deterministic total
order on the candidate set, so set agreement does imply ordered-list agreement here — but
that is now **verified directly**, not assumed.

### 2.3 Independent legality validation (was: trust the worker's own illegal counter)

The original reported "0 illegal" from the worker's own in-loop `verify_legal` counter
and a final evaluator pass. This supplement maintains a **separate evaluator-only
cumulative patch** (`worker_hist`, an `L.Patch` seeded from the complete pre-scar jam
patch `Sstar+[B]`) that follows the **worker's own trajectory**. For every worker addition,
in placement order, it checks frozen `Patch.legal(t)` against that history **before**
adding it. The worker never consults this history; it exists only in the evaluator. All
eleven cases validate every placement (440–829 per case) with no failure
(`independent_legality.all_legal = True`; `first_failure = null`). Had a placement failed,
the pre-state and placement would be recorded and the run stopped — no corrective veto.

At the endpoint, the cumulative history is checked independently: every complete (2π)
vertex carries a valid atlas star (427–586 complete vertices/case, **0** invalid, **0**
over-full), and a bounding-box-prefiltered convex-clipping overlap check finds **0**
positive-area triangle overlaps (max intersection area ≤ 2.6e-16, i.e. shared edges only).
This history validation is kept separate from the comparator history.

### 2.4 Replaced weak controls

- **Real scar-adjacency (was: a bare count).** `scar_adjacency_check` defines scar
  adjacency explicitly — a placement is scar-adjacent if, **at its placement time**, one
  of its vertices coincides with a vertex of a currently pinned (dormant-scar) frontier
  edge — identifies those placements, and validates each against the independent full
  history. For w7 this is exercised (18 scar-adjacent placements, 18/18 legal). Zero
  eligible placements would be reported as "not exercised," not as a positive result.
- **Deep retained-state check (was: field-name presence).** Beyond confirming the
  serialized state has exactly the declared fields, the supplement checks that every
  `boundary` owner tile is a retained band tile; every boundary edge coordinate is a
  retained vertex; the worker's edge/vertex caches reference only retained tiles after
  pruning; the frontier exposes no deletion-cavity edge
  (`{frontier_id(e)} ⊆ full.frontier`); and the serialized **pre-scar** state equals the
  frozen jam band and shares **no** tile with the deleted interior.
- **Current blocked edges vs cumulative scar labels, recorded separately.**
  `current_blocked_edges` counts frontier edges with zero candidates **at step 44**;
  `cumulative_scar_labels` counts edges ever pinned as dormant scars over the run. They
  coincide for most cases but **differ** for w5-B-s0 and both w21 streams (5 currently
  blocked vs 2 ever labelled) — the present blocking state is not the cumulative scar
  history, and both are reported rather than merged.

### 2.5 Process separation vs filesystem isolation (stated precisely)

The isolation guarantee rests on **what the worker is given**, not on a filesystem
sandbox. The spawned worker receives **only** the serialized retained state — `schema`,
`radius`, `tiles`, `boundary`, `rng_state`, `scars`, `fields` — and reconstructs the skin
from it (the explicit `boundary` is restored, not re-derived from a full patch). The
separate `spawn` process additionally rules out shared in-memory objects or inherited
globals.

It does **not** make historical files inaccessible: the spawned worker still imports the
frozen engine/reader modules, which read static geometry templates and the vertex-star
atlas from disk. What it never reads is the **full-patch trajectory, the deleted interior,
any archived lift, occupancy map, candidate menu, future placement, or A/B hypothesis** —
none of these is in its input, and the continuation it produces is identical to the
in-process worker's and the full patch's. "Archive-free" here means *constructed from the
declared retained state only*; it is established by the input contract (serialized state
only) plus exact reproduction, not by the separateness of the process alone.

---

## 3. Scope, stated precisely

- **Eleven correlated cases, not eleven independent tilings.** The eleven (world, stream)
  labels span **nine distinct pre-scar band geometries** (`input/prescar_states.json`
  hashes): w7-s0/w7-s1 share an identical retained band (differing only in PRNG stream),
  as do w21-s0/w21-s1; and several distinct worlds share identical summary statistics
  (jam step, band count, placement count). The agreement is strong evidence that the band
  suffices on *these* jams, but it is not eleven independent confirmations.
- **Finite continuation to step 44**, from exported jam states — not from the original
  seed, not indefinite growth.
- **Construction from retained tiles plus declared metadata** (the explicit true-frontier
  `boundary`, PRNG, scar set) — audited to contain no full patch or deleted interior.
- **Separate-process restart from the actual pre-scar jam state** (§2.1), verified against
  the frozen checkpoint before use.
- **Set vs ordered agreement** are both verified and are now reported distinctly (§2.2).
- **Explicitly-checked legality**, against an independent full history, not inherited from
  the worker's own counter (§2.3).
- **Band width is distance from the declared true frontier, blocked components included.**
  The band is radius-2 around `skin.frontier()`, and that frontier **includes the pinned
  (blocked) scar edges**, which remain boundary edges permanently. The band's radial
  thinness is therefore thinness around the whole declared frontier — scars included — and
  the inward lobes visible in `figures/archive_free_w7.png` are exactly the 2·S
  neighbourhoods of interior scar components. Proximity to an old scar boundary does **not**
  establish proximity to the advancing outer perimeter; the two are different components of
  the same declared frontier. Retained count stays 47–63 % of the full patch at step 44.
- **Positive-area readout qualifications retained.** The endpoint geometry is byte-for-byte
  identical to the original export for all eleven cases (`results/endpoint_geometry.json`:
  sorted decorated-key lists identical), so the original 528-window readout
  (`results/readout.json`: 111 B / 64 ambiguous / 353 reader-incompatible / 0 A / 0
  failures) is **reused unchanged** rather than recomputed. Its qualifications stand: the
  largest-compatible subset selects B, but the independent box-free check shows the closed
  A intersection is a **zero-area segment** for the w15/w19/w28-s0 family and infeasible
  otherwise — "the positive-area reader selects B" is **not** symbolic exclusion of A. The
  subset search was not expanded.

---

## 4. Reconciliation of the handback headlines

| handback claim | verdict | note |
|---|---|---|
| "Reproduces the full-patch scheduler **exactly, at every step, to step 44**" | **Survives, now on stronger evidence** | The original "exactly" rested on set-inventory + set-placement equality plus no divergence; it is now backed by direct **ordered** checks (enumeration order, ordered placements/frontier, PRNG before+after), all 11/11. |
| "**zero illegal** placements" | **Survives, now independently checked** | Verified per placement, in order, against a separate evaluator-only full-history patch (440–829/case), not the worker's own counter. |
| Worker genuinely cannot see the deleted interior; "**separate process receiving only the serialized band**" | **Survives, refined** | True by input contract + exact reproduction; **not** by filesystem isolation. The pre-scar restart now starts from the **actual jam state** (top of the jam step), verified against the frozen checkpoint, and the spawned restart matches both comparators 11/11. |
| "candidate sets … ordered candidate lists … all match" | **Survives, wording corrected** | The frozen `inventory` sorts candidates, so inventory equality is *set* equality; ordered agreement is now measured directly and reported separately from set agreement. |
| Band is "**radially thin** (within ~2.7·S of the true frontier)" but "not thin in count (47–63 %)" | **Survives, framing sharpened** | Thinness is distance from the **declared true frontier including blocked scar edges**; it does not imply proximity to the advancing outer perimeter (§3). |
| Readout "111 B / 64 ambiguous / 353 reader-incompatible / 0 A"; "selects B … not symbolic exclusion of A" | **Survives, reused on identical geometry** | Endpoint geometry is identical to the original export (11/11), so the readout is reused unchanged; the zero-area-segment and conditional-positive-area qualifications stand. |

---

## 5. Deviations (recorded, not edited into the frozen protocol)

- This supplement adds a **pre-scar** serialization point (top of the jam step) in addition
  to the original `serialize_at=jam` (post-first-batch) control, and makes the spawned
  restart begin at the first scar step. The original control is preserved; this is an
  added, stronger control, not a replacement of recorded results.
- The endpoint readout is **reused** from the original run rather than recomputed, justified
  by a documented byte-for-byte endpoint-geometry comparison (`results/endpoint_geometry.json`).
- No matching rule, reader threshold, scheduler policy, case list, horizon, or frozen file
  was changed. The frozen `active_skin_engine.py` and reader are imported unchanged; all new
  code is in this `supplement_2026-11-04/` directory.

A pointer to this supplement is appended to `protocol/PROTOCOL_DEVIATIONS.md`; the original
`HANDBACK.md` and `README.md` are preserved with a dated pointer added, not rewritten.

---

## 6. Reproduce

```bash
export EFP_SNAPSHOT=<frozen 84130b9 worktree>/exploratory/accretion_pilot/expansion_front_paper
export MPLBACKEND=Agg
# fork cache (if absent): (cd ../../../jam_repair_pilot/src && python3 build_fork_cache.py)
cd archive_free_2026-11-04/supplement_2026-11-04
python3 verify_supplement.py    # all 11: ordered+set equivalence, independent legality,
                                #   pre-scar alignment, endpoint stars/overlaps, metadata,
                                #   blocked-vs-labels -> results/verification.json,
                                #   input/prescar_states.json
python3 restart_prescar.py      # spawned-process restart from the pre-scar state, all 11
                                #   -> results/prescar_restart.json
python3 endpoint_geom.py        # endpoint geometry identical to original export, all 11
                                #   -> results/endpoint_geometry.json
python3 test_supplement.py      # focused corrected tests (ordered+legality, real
                                #   scar-adjacency, deep retained-state, pre-scar restart)
```

Machine-readable outputs: `results/verification.json`, `results/prescar_restart.json`,
`results/endpoint_geometry.json`, `input/prescar_states.json`. The original experiment's
`results/comparison.json`, `results/controls.json`, `results/readout.json`, and
`input/worker_band_exports.json` are untouched.

---

## 7. What survived, what changed, and what remains unverified?

**Survived.** Every headline. On all eleven correlated B-jam cases the archive-free
radius-2 band worker reproduces the audited full-patch scheduler **exactly to step 44** —
now confirmed at the **ordered** level (candidate enumeration, placements, frontier, PRNG
before and after), with **every** placement independently validated legal against a
separate full history (no illegal placements, clean vertex stars, no positive-area
overlaps), and with a **separate-process restart from the actual pre-scar jam state**
(verified against the frozen checkpoint) matching both comparators. The endpoint geometry
is identical to the original, so the conditional positive-area readout carries over
unchanged.

**Changed.** Only wording and the strength of evidence, never the policy or the results.
"Exactly, every step" was, in the original harness, a set-level measurement (the frozen
`inventory` sorts candidates) plus the fact of no divergence; it is now backed by direct
ordered checks, with set and ordered agreement reported distinctly. "Zero illegal" is now
an independent per-placement check rather than the worker's own counter. The isolation
claim is refined to rest on the serialized-state-only **input contract** plus exact
reproduction — not on filesystem inaccessibility (the spawned worker does import the frozen
engine and read static templates/atlas; it never reads the trajectory or deleted interior).
The pre-scar restart now starts **before** the first scar batch, not after it. Band
"thinness" is stated as distance from the declared true frontier **including blocked scar
components**, not as proximity to the advancing outer perimeter. "Current blocked edges"
and "cumulative scar labels" are recorded separately and genuinely differ in three cases.

**Remains unverified (unchanged from the handback, by design).** Archive-free construction
from the **original seed**; growth **beyond step 44**; a **thin** band (it is radially thin
but 47–63 % of the patch by count); any **physical, topological, or indefinite** memory
claim; and any reader claim beyond the audit's **conditional, selected-subset, positive-area**
readout — in particular, A is a zero-area segment in the w15/w19/w28-s0 family, so B's
selection is not symbolic exclusion of A. The eleven cases are **correlated** (nine distinct
pre-scar geometries; two worlds contribute two streams each over an identical band), so they
are strong but not independent evidence. No new research direction, horizon, world, or
policy tuning was introduced.

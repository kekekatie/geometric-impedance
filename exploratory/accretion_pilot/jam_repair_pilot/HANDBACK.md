# HANDBACK — jam-repair pilot

*2026-11-01. For Katie / GPT-Astra. A bounded, exploratory pilot. Diagnosis,
intervention and interpretation are kept separate below. Historical results were
not modified; all new outputs are under `exploratory/accretion_pilot/jam_repair_pilot/`.*

Branch: `claude/confident-cerf-404o4f`. Frozen engine imported read-only from
commit `84130b97f5044197392e72cd53e0e71f81b043f3`
(`expansion_front_paper/`, branch `codex/manuscript-reconciliation`).

---

## Central question and short answer

> Can a legal rearrangement wholly supported by the retained active skin restore
> growth after a recorded jam, while preserving the existing A/B
> historical-choice readout?

**For the one move class tested (a three-rhombus hexagon / simpleton flip): no.**
At every one of the 11 reconstructible B jams, eligible three-rhombus flips exist
right at the dead sites and are each a valid phason flip *in isolation*, but
**every one is vetoed by the decorated Penrose matching rules in the surrounding
retained skin** — so no legal single-move repair is available. No matching rule
was relaxed to find a rescue; "none legal" is reported as a valid result, exactly
as the protocol requires.

A second, independent fact makes the jams harder than a local notch: each jam is
not merely a local dead-end but a **global window contradiction** — the retained
skin's own compatibility region `F` is empty (area 0) — so the archive-free A/B
reader, run unchanged on the surviving geometry, returns **empty/incompatible**
rather than selecting A or B. The readout machinery is preserved intact; it
simply has no consistent offset to read at a contradictory checkpoint.

This does **not** show repair is impossible in general (other move classes, a
larger skin, or multi-flip search are out of scope here), and an empty `F` at a
jammed checkpoint is **not** by itself proof that historical information has
vanished.

---

## Phase 1 — baseline and state availability  (DIAGNOSIS)

**Ran, fully, and verified against saved records.**

- Replayed the **22 closure forks / 88 continuations** with the frozen engine.
  World ids match the saved closure record exactly:
  `[0,1,2,3,5,7,11,12,13,15,19,21,23,25,28,29,30,37,39,40,41,46]`.
- **Jam counts reproduced: A 0/44, B 11/44.** Per-arm milestones (stop reason,
  nsnaps/jam-step, choice-tile departure `dep`, guess steps) match the saved
  `closure_measurements.json` for **all 88 arm-streams, 0 mismatches**
  (`results/baseline/verification.json`).

Answers to the Phase-1 questions:

- **Canonical A/B ordering.** `A = cs[0]`, `B = cs[1]` where
  `cs = SN.ordered(D.candidates(edge))`, sorted by `(shape c, key(A), key(B),
  key(C))`. It is the scheduler's deterministic candidate order, **not** an
  intrinsic geometric label. (Observed: in all 22 forks A is the type-0 /
  36-72-72 half-tile and B the type-1 / 108-36-36 half-tile.)
- **Exact jam condition.** `speed_of_now.patient()` returns `JAM` at the **first**
  frontier edge whose legal-candidate set is empty.
- **Does a single zero-candidate site stop the engine while others can grow?**
  **Yes, emphatically.** Every B jam has exactly **2 dead (zero-candidate)
  frontier sites** amid **71–118 still-growable sites**. One dead site halts the
  whole engine.
- **Does the saved state permit a faithful restart?** There are **no per-step
  checkpoints** for the closure runs (confirmed independently in the
  archive-free-reader verification note). Faithful restart is available **only
  via deterministic replay** from `(world, stream)`; replay here reproduces every
  saved milestone. This is **replay, not "zero new computation."** The retained
  state at each jam trigger is exported **before any mutation**
  (`results/baseline/jam_cases/wK-B-sN.json`): the repair worker receives only the
  retained active skin + legitimate scheduler metadata (stream, jam step, horizon,
  radius); the historical full patch is exported separately and labelled
  verification-only.
- **The jam is also a global contradiction.** At all 11 triggers the full-patch
  compatibility region `F(full)` is **empty** (area ≤ 1e-12). So here the local
  zero-candidate condition and the empty-`F` condition **coincide** — the engine,
  growing by local atlas-legal moves, has painted itself into a globally
  window-incompatible patch.

Artifacts: `results/baseline/manifest.json`, `verification.json`,
`baseline_report.txt`, `jam_cases/*.json`.

---

## Phase 2 — small geometry diagnostic  (DIAGNOSIS, descriptive)

**Ran.** Three pre-committed diagnostics (`protocol/PHASE2_DIAGNOSTICS.md`),
measured on the paired fork states, kept distinct from the true windows and the
finite hulls, in offset/perp-space units. Descriptive only — no model, no causal
claim, streams not independent; the +0.749 inward-alignment statistic (different
population) is **not** used.

The interpretable signal is **D1, the retained compatibility-area ratio**. In
every fork the two options partition the birth region into complementary
golden-ratio pieces (`pA + pB ≈ 1`). Grouped by outcome:

| group | median pA | median pB | median (pA−pB) |
|---|---|---|---|
| B-jammed forks (7) | 0.146 | **0.854** | −0.708 |
| B-survived forks (15) | 0.382 | 0.618 | −0.236 |

Descriptively, **the forks where B jams are those where B (the canonical second
option) retains the *larger* compatibility piece.** Every fork where `pB ≈ 0.854`
jammed (5/5). This is a tendency with honest exceptions (worlds 1 and 3 have large
`pB` = 0.724/0.764 but B survived), **not** a rule or a mechanism. D2
(centroid displacement) and D3 (centroid eccentricity) did not separate the
groups. (One dated deviation from the pre-commitment is recorded in
`PROTOCOL_DEVIATIONS.md`.)

This resonates with — but does not prove — the earlier "smaller piece grows the
larger burst" lean: the greedier (larger-piece) option is the one that
dead-ends. No causal arrow is drawn.

Artifacts: `results/phase2/diagnostics.json`, `phase2_report.txt`.

---

## Phase 3 — legal single-move feasibility  (INTERVENTION)

**Ran, under a frozen prospective protocol** (`protocol/PHASE3_PROTOCOL.md`),
after validating the move generator/validator on controlled examples
(`tests/test_hexflip.py`, 9/9 checks pass, including rejection cases and the
geometric-vs-legal distinction).

Method: for each reconstructible B jam, replay the arm on the frozen `ActiveSkin`
engine to the jam trigger (verified: reproduces the jam at the recorded step, with
the recorded skin size and 2 dead sites); enumerate three-rhombus hexagon flips in
the retained skin near the dead sites; classify each as *phason* (alternative
dissection legal in isolation = geometric candidate) vs *fully legal in context*;
mark *eligible* ones (interior hexagon that shares a vertex with a dead site, so a
flip could change the dead edge's vertex star). Legality is the frozen engine's
`legal()` — no rule relaxed.

**Result — all 11 cases: `geometric moves exist but none is legal`.**

| per case | value |
|---|---|
| dead sites | 2 |
| flip hexagons near dead sites | 13 or 17 |
| phason (geometric) candidates | **all of them** (13 or 17) |
| eligible geometric moves (interior & touch a dead site) | **2 or 3** |
| fully legal in context | **0** |
| eligible legal (could un-jam) | **0** |
| no-repair baseline re-jams immediately | **yes, all** |

So eligible three-rhombus flips sit right at the dead sites — all 3 dead vertices
per case are incident to some flip hexagon — and each is a valid phason flip in
isolation, yet the surrounding retained skin vetoes every one (flipping would
force a forbidden vertex star on a fixed boundary vertex). The generator was shown
to *find* such flips when the external star-constraint is relaxed, so "0 legal" is
a genuine context-veto, not a generator failure.

Because no eligible legal move exists, **no repair was attempted** (the protocol
attempts only the first fully-legal eligible move). Categories (d) immediate
growth restored, (e) later re-jam, (f) horizon reached therefore do not arise in
this pilot.

Artifacts: `results/phase3/wK-B-sN.json`, `phase3_report.txt`; figures
`figures/jam_w7-B-s0.png`, `jam_w5-B-s0.png`.

---

## Phase 4 — readout after repair  (INTERPRETATION of the readout)

**Ran** the **frozen** standalone reader (`archive-free-reader/skin_reader.py`,
isolated `-I -S` subprocess) on a fresh serialization of surviving geometry at the
jam-trigger checkpoint (the final usable checkpoint for a jammed arm), using the
**original** gauge: common pre-fork origin, four-layer rank map, fixed windows,
and the two original historical candidate regions `C^A`, `C^B`. The reader's
scientific decision rule is unchanged; only a neutral payload adapter is new. No
post-repair readout exists because Phase 3 produced no legal repair.

**Result — all 11 pre-repair readouts: `empty/incompatible`.** The reader
**reconstructs the skin cleanly** (e.g. w7-B-s0: 209 vertices, one component, 0
omitted, projection residual 1.7e-13) but the skin's compatibility region `F` has
**area 0** and **both** hypothesis intersections are 0, so it selects neither A nor
B. This is the honest consequence of the jam being a global contradiction
(`F(full)=0`); it is a distinct category from *unreconstructible* (the lift
succeeded) and from *wrong/ambiguous*.

Choice-tile fate (tracked separately, per the task): **8/11** B choice-tiles had
**departed under ordinary pruning** before the jam; **3/11** (w15-s0, w19-s0,
w28-s0) were **still retained** in the skin at the trigger. **None** was removed or
altered by a repair (there was none). These are not combined as equivalent
post-prune evidence.

Per the task's caution: an empty `F` / incompatible readout at a jammed checkpoint
is **not** by itself proof that all historical information has vanished — it
reflects that a jammed patch admits no consistent window offset at all.

Artifacts: `results/phase4/phase4_results.json`, `phase4_report.txt`,
`wK-B-sN-pre.json`.

---

## Boundaries honoured

No seam was forced closed; no new defect core was constructed; no nonzero-holonomy
claim is made (the lift was conflict-free where reconstructed; single-valued
vertex coordinate differences sum to zero around a loop). No quantum-error-
correction, elasticity, particle-formation, or indefinite-growth claim is made.
Finite continuation was not treated as indefinite growth, inward geometry was not
assumed to explain the jams, and repair was not assumed possible.

## What did not run / limits

- **Only one move class** (the three-rhombus hexagon flip) was tested, as scoped.
  Larger clusters, multi-flip search, an enlarged skin, backtracking and new seed
  sweeps were explicitly excluded. A null for this class is not a null for all
  conceivable local repairs.
- **No repair outcome exists** to compare resume-vs-no-repair growth, because no
  legal eligible move was found. The resume + no-repair-baseline machinery is
  implemented and the no-repair baseline was confirmed to re-jam immediately, but
  categories (d)/(e)/(f) were never reached.
- **Replay, not checkpoints.** No historical per-step state was available; the
  pilot relies on verified deterministic replay.
- **22 forks, 2 streams each** — small, non-independent; Phase 2 is descriptive.
- The reader has a four-layer-slab horizon; here all 11 skins lifted cleanly, so
  the empty-`F` outcome is a genuine incompatibility, not a slab dropout.

## Reproduction, deps, tests, provenance

See `README.md` for commands. Python 3.12; `numpy`, `scipy`, `matplotlib`
(`requirements.txt`); the reader is standard-library only. Validation:
`tests/test_hexflip.py` (9/9). Frozen engine: worktree at
`84130b97f5044197392e72cd53e0e71f81b043f3`.

Branch `claude/confident-cerf-404o4f`; commit id and push status recorded in the
commit that adds this directory. No pull request opened (none requested). Nothing
merged or force-pushed; no historical result changed.

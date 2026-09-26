# Design note (v12) — local accessibility of memory: design & data repair

*Register: speculative exploration; not a confirmatory study, not cosmology. **Design
+ existing-data reporting only — no new production trajectories.** Chain v1 `cc514ee`
→ … → v11 `10d4860`. Isolated under
`exploratory/accretion_pilot/v12_local_reader_design/`. v1–v11 preserved; dated
clarifications appended to `../v11_substrate_pilot/REPORT_v11.md`. No merges,
publishing, sealed-study access, or new substrate construction.*

Addresses Katie's long-standing question — is the stored distinction **accessible**
to something moving *through* the world, not just to a god's-eye global reader?

## Part 1 — v11 closed accurately

The four clarifications and the conditional matched-offset contrast table are appended
to `../v11_substrate_pilot/REPORT_v11.md`; the table is computed from existing scalar
data by `v12_contrasts.py` (`results/matched_contrasts_t2000.csv`): mean contrast
(perturbed − regular) at t=2000 = **+0.007 [−0.018, +0.032]** (seed-bootstrap, six
patches fixed; not generalisation beyond three pairs; not an equivalence claim).

## Part 2 — one minimal local-reader experiment (recommended design)

**Question:** can a bounded sequence of **local encounters** distinguish imposed
histories A and B?

**Posture — a passive visitor on a frozen world.** Take a world evolved to a chosen
checkpoint under the v11 dynamics, then **freeze it** (no reinforcement, no growth
during reading). A visitor makes a bounded read-only traversal and outputs a score.
This is an **observational accessibility** test — "is the distinction reachable within
a bounded local encounter budget?" It is explicitly **not** a demonstration that an
*active* walker (one that keeps reinforcing/growing) *uses* the memory to change its
behaviour, nor that memory is *transmitted* onward. Those are later steps.

### The recommended reader (smallest interpretable model)

A **frozen, coordinate-aided, bounded-encounter reader** — the v5 global reader
restricted to what a bounded local walk actually senses:

- **Reset:** the visitor starts at `S`, the shared history start vertex (identical for
  the A- and B-worlds of a seed, so the reset leaks no label). Fixed.
- **Movement:** a **read-only weighted random walk** (step to a present neighbour with
  probability ∝ current frozen weight), fixed visit-RNG seed. Passive: it never
  changes weights or activates edges. (A deterministic "follow-heaviest-unvisited"
  variant is offered as a sensitivity check.)
- **Observation budget:** a fixed **B = 300 steps** (≪ the 10 000 evolution steps).
  Report the score as a function of B (accessibility-vs-budget curve) over a few fixed
  budgets {100, 300, 1000}, but the headline budget is 300.
- **What it senses locally, and the precision:** at each vertex it senses the incident
  **present** edges, their **type** (original vs added diagonal), and each incident
  edge's weight **quantised to whole numbers (Δ = 1)** — i.e. it can tell an added
  diagonal that "reads as 6" from one that "reads as 5" (the v5 threshold `w ≥ 5.5`),
  but not finer. It accumulates, over the added diagonals it encounters, the frozen
  reader term `coeff(d)·1[w_d ≥ 5.5]`.
- **Score (frozen, no fitting):** `S_local = Σ_{d encountered ≤ B steps} coeff(d)·1[w_d ≥ 5.5]`,
  with the **same** proximity coefficients as the global reader. A-positive
  orientation, fixed in advance.

**Aids this reader receives — stated honestly (it is heavily aided):**

| aid | given? | why |
|---|---|---|
| coordinates / bearings | **yes** | needed to compute the proximity `coeff(d)` |
| knowledge of the two candidate paths A, B | **yes** | `coeff(d)=sign(dist(d,B)−dist(d,A))` uses them |
| edge-type labels (original vs diagonal) | **yes** | reader acts on added diagonals only |
| weight sensing | **yes, Δ=1 (whole-number)** | local threshold `w ≥ 5.5` |
| its own visited-vertex memory | **yes** | to avoid double-counting encounters |
| global vertex IDs / full graph | **no** | it only sees what it visits within B |

So this first reader answers a **narrow** question: *given the same information the
global reader used, does a bounded local traversal encounter enough of the signed
footprint to distinguish A from B?* It is the smallest step from v11's global reader
(only the **bounded-encounter** restriction is new). We label it as strongly aided and
do **not** call it coordinate-free.

### Optional second reader (more coordinate-free; only if the first is uninformative)

A **small trained decoder** on **coordinate-free** local features — e.g. the histogram
of quantised incident-edge weights, counts of high vs low incident diagonals, and
local degrees, aggregated over the B-step visit — with **no** coordinates and **no**
path knowledge. Train/test split holds out **whole worlds / seed pairs** (train on a
subset of seeds, test on disjoint seeds; a world never appears in both). **Repeated
visits to one world are not independent samples** — multiple visit-seeds per world
reduce per-world measurement noise only. Report held-out accuracy.

### Comparator, controls, and static-substrate information

- **Global comparator on the SAME worlds:** compute the v5 global `S_high` over *all*
  added diagonals on the identical frozen worlds, so any local-vs-global gap reflects
  *accessibility*, not different simulations.
- **No-history null:** the same visitor on no-history frozen worlds with A/B labels
  assigned independently of dynamics → expected chance; quantifies static-substrate /
  reader artefacts the visitor could exploit.
- **Static-substrate information available to the reader:** even with no history, the
  visitor senses geometry, degrees, and edge types; the null controls for these. The
  proximity `coeff` is defined from the (label-carrying) path geometry, so the null
  (labels random) is the correct baseline.

### What a positive/negative result would and would not mean

A positive local result shows the distinction is **reachable within a bounded aided
local traversal** — a necessary step toward "usable," not proof of use or transmission.
A negative result (local ≈ chance while global ≫ chance) would show the footprint is
present globally but **not accessible** to this bounded aided visitor — itself an
interesting accessibility limit. Neither speaks to genuine order classes (v11 caveat).

## Part 3 — data feasibility & storage/replay plan

**The existing subsample archive does NOT support this experiment.**
`../v11_substrate_pilot/results/subsample_snapshots.npz` stores, for only **2 seeds ×
1 history pair × 6 patches**, the final-checkpoint weights as a bare vector over
`sorted(w.weight)` — **no edge IDs, no presence map, no geometry, no coefficients**,
and the key set differs per world (different diagonals activated), so the vectors are
**not alignable** and a weight cannot be tied to an edge. It is unusable for a
graph-walking local reader.

**Minimum deterministic replay.** Every world is a pure function of
(offset, jitter-seed, history, walk-seed, checkpoint); nothing else is needed. To make
a frozen world at a checkpoint: rebuild the patch (cache per patch), impose the history
(48 events), walk `t` steps with `rng(BASE_SEED+seed)`, stop. **Validation:** the
replayed world's scalar readouts (`S_high, n_active, frac_active, headroom,
total_weight, struct_access, eff_alt`) must equal the saved `raw_main.csv` values for
that (arm, patch, pair, history, seed, checkpoint) to tolerance — this proves the
replay reproduces the exact v11 world before any local reading.

**Reusable snapshot schema** (one archive, replay-generated, reused by local & global
readers without re-replay):

```
per patch (shared):   patch_id, arm, offset, jitter_seed, radius,
                      vertex positions, original edge list (IDs),
                      full candidate-diagonal list (IDs), faces,
                      history pairs (A,B vertex sequences), reader coefficients
per world (cell,seed,history,checkpoint):
                      candidate PRESENCE bitmap (which diagonals active),
                      weight per present edge aligned to the fixed edge-ID list,
                      seed metadata (walk seed), scalar readouts (for validation)
```

Fixed **edge-ID list** = originals + all 128... (all candidate diagonals) in canonical
sorted order, so every world's weights align to one index space (0 = absent).

**Recommended checkpoint & budget (bounded).** Read at the **primary checkpoint
t = 2000** only, for the first local-reader pilot. Budget: replay **50 seeds × 18
cells × 2 histories = 1800 worlds** (a subset of v11's 200 seeds — reuse seeds 0–49),
plus a matched no-history null set. Visitor: B = 300 steps, ~5 visit-seeds per world
(noise reduction, not extra samples).

**Cost estimates** (from the v11 benchmark ~0.29 s / 10 000-step run → ~2.9e-5 s/step):
- Replay to t=2000: 1800 worlds × 2000 steps ≈ 3.6M steps ≈ **~2 min**.
- Local readout: 1800 worlds × 5 visits × 300 steps ≈ 2.7M read-steps ≈ **~1–2 min**.
- Storage: per-world aligned weight vector ≈ (144 originals + ≤128 diagonals) floats;
  1800 worlds × ~272 × 8 B ≈ **~4 MB** (compressed less); geometry stored once per
  patch. Well within budget.

So a bounded local-reader pilot is **feasible in well under 10 minutes** once a
schema-correct replay+snapshot utility exists. **No replay production run is performed
in this task** — this is the plan only.

## Deliverables in this folder

`v12_contrasts.py` + `results/matched_contrasts_t2000.csv` (Part 1); this design note
(Parts 2–3); `README.md`. The v11 clarifications live in
`../v11_substrate_pilot/REPORT_v11.md`.

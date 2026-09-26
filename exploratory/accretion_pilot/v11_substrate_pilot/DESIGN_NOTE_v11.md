# Design note (v11) — substrate pilot: repairs, gates, and frozen design

*Register: speculative exploration; not a confirmatory study, not cosmology. Chain
v1 `cc514ee` → … → v10 `0a41135`. Isolated under
`exploratory/accretion_pilot/v11_substrate_pilot/`. v1–v10 preserved; a dated
correction is appended to v10's `FEASIBILITY_VERDICT.md`. No merges, publishing,
sealed-study access, periodic arm, or Reinforced arm. Repairs + experiment authorised
on all gates passing.*

## Central question

Does quasiperiodic spatial organisation change the persistence of history-readable
footprints under local reinforcement and connection growth, compared with a
perturbed (same-tile) substrate? (**No** assumption that quasiperiodicity helps;
family comparisons are exploratory and conditional on the selected geometries.)

## Construction repairs (over v10)

- **R1 — genuine overlap/gap validation.** v10's area check was a no-op (labelled
  `True` unconditionally). `validate()` now: traces boundary loops; compares the
  **net enclosed signed area** (outer loop minus holes) to the **summed face area**
  under an explicit tolerance; tests **non-incident original-edge crossings**; and
  checks **each face centroid lies in exactly one face**. Two deliberately invalid
  fixtures (an overlapping rhombus pair; a connected corrupted patch) are **rejected**
  by these checks (`gate G2`).
- **R2 — robust intersection construction.** The `eps=1e-4` nudge sampling is
  replaced by **searchsorted strip indices** (exact) plus a **clearance test** to
  non-incident lines; near-degenerate intersections are **counted and reported**, not
  silently used. All production patches report **0 degeneracies**.
- **R3 — production-patch validation & bookkeeping.** All six R=10 patches validate;
  candidate diagonals are checked **unique** and **distinct from original edges**;
  cropping reports **discarded components** (0 for all).

## Gates (all must pass; `results/gate_report.txt`)

G1 geometry valid (all 6 patches); G2 invalid-fixtures rejected; G3 zero
degeneracies; G4 diagonals unique & distinct; G5 **engine equivalence** — the
substrate-general engine is **event-by-event identical** to the v2 square engine over
history + 300 steps under canonical neighbour ordering and matched RNG; G6 the three
regular patches are **not rigid-motion duplicates** (D10 + centroid translation test —
equal V/E/F alone is *not* used); G7 **3 eligible length-6 history pairs per patch**
(else that patch fails). **All gates PASS.**

## Frozen geometry & histories

- **R = 10** (~366–380 vertices). **Three offset vectors** selected from a fixed
  deterministic candidate list by the rigid-duplicate rejection rule; **matched
  regular/perturbed pairs** share an offset (perturbed = same offset + jitter,
  amplitude **0.30**, seeds 0–2). Recorded in `results/frozen_manifest.json`.
- **Histories:** 3 distinct-endpoint pairs per patch, **fixed length 6 edges**, start
  `S` = vertex nearest centroid, `A` = leftmost / `B` = rightmost shortest path;
  eligibility = both exist, equal length, **not identical** (they may share edges/
  vertices — shared counts reported; the contradictory "edge-disjoint" wording from
  v10 is removed). **3 imposed passes; walker reset to S.** A patch is **failed** if 3
  eligible pairs are not found — no outcome-driven replacement, no length change.

## Engine & reader (frozen)

Substrate-general `SubstrateWorld` with **canonical (sorted) neighbour and candidate
ordering**; same rules/params as v2 (α=0.5, w_max=6, θ=4, w_init=1, reader threshold
5.5). **Checkpoint reads do not alter trajectories** (readouts consume no RNG).
Frozen reader `S_high = Σ_d c(d)·1[w_d ≥ 5.5]` over present added diagonals, with
`c(d) = sign(dist(d, B) − dist(d, A))` on the frozen original graph.

## Analysis plan (frozen before outcomes)

- **Primary discrimination = ordinary fixed-orientation AUC** (A vs B), computed
  **within each patch/history cell**. **Within-seed ordering probability is
  secondary** (common random numbers can affect it without changing marginal history
  discrimination).
- **Primary checkpoint t = 2000** (pre-registered); other 7 checkpoints descriptive.
- **200 seed pairs per cell**, 10,000 steps, **seed-pair bootstrap within cells**.
- **Each patch equal weight** — average its **3 history pairs first**, then average
  the **3 patches** per arm. **All cell and patch results shown.** Three histories on
  one patch are **not** three independent substrate samples; family comparisons are
  **exploratory and conditional** on these geometries.
- **No-imposed-history Growing null:** A/B labels assigned **independently of
  dynamics** (random) → expected chance even on an asymmetric substrate; a finite
  departure from chance alone does **not** establish substrate bias. **Fixed** kept as
  a cheap plumbing fixture (added-diagonal reader is empty without growth).
- **Opportunity, activation fraction, headroom, and boundary visitation reported
  separately.** Saturation views descriptive. **No claim of isolated higher-order
  organisation** — degree distributions, history geometry, and boundaries differ
  across arms (reported).

## Storage & execution

Scalar readings saved at every checkpoint (`raw_main.csv`, `raw_null.csv`); frozen
substrates/histories/coefficients and full config + seed mapping recorded
(`frozen_manifest.json`, `experiment_config.json`). **Full-edge snapshots are large**
(~57.6k worlds × 8 checkpoints × ~1.4k weights ≈ several GB if stored densely), so
only a **small compressed subsample** is retained (`subsample_snapshots.npz`);
scalars are the primary output. Benchmarked at ~0.29 s/world-run → full batch
≈ 40 min (updated in `experiment_config.json`). Parameters were **not** tuned from
observed memory scores.

## Interpretation boundaries (restated)

A difference between arms concerns **this reader on these geometries**; it does not
isolate higher-order organisation from local geometry (degrees, tile frequencies,
boundaries all differ), nor establish topology as a storage carrier, nor that a
walker can locally access the distinction (Katie's accessible/pass-on-able memory
question remains a future local-reader extension, not implemented).

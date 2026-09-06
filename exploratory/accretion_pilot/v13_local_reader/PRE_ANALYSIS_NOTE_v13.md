# Pre-analysis note (v13) — bounded local-reader pilot (frozen before execution)

*Register: speculative exploration; not a confirmatory study, not cosmology. Chain
v1 `cc514ee` → … → v12 `7a342c5`. Isolated under
`exploratory/accretion_pilot/v13_local_reader/`. v1–v12 preserved. No merges,
publishing, sealed-study access, new substrates, trained decoder, or alternative
movement policies. Authorised to run after gates pass; stop only on concrete failure.*

## Question

Can a **passive tagged visitor**, making a bounded read-only traversal of a frozen
t=2000 world, distinguish imposed histories A and B?

## Information available (frozen)

- The reader coefficient `c(d)` depends on graph distances over the **full** original
  substrate, so it is **not** locally computable from coordinates/path knowledge.
  We therefore supply `c(d)` as a **precomputed tag** attached to each candidate
  diagonal, **revealed only when that present diagonal is encountered**. Tags are
  **identical between the A- and B-worlds of a history pair** and independent of the
  realised history. This is explicitly a **tagged, aided reader** — not a
  self-computed local reader.
- The visitor has **stable local identity** of edges it has already encountered (so a
  diagonal seen from both endpoints counts once). It is **not** given unseen adjacency
  or any global state.

## Visitor and score (frozen)

- Start at the shared history start `S`. At the initial vertex **and after every
  step**, observe **all incident present edges**.
- Sense **whole-number weights** `q(w) = floor(w + 0.5)` (the established convention).
  Choose the next edge with probability **∝ the observed rounded weights** `q(w)`
  (movement uses rounded, not finer, precision). Read-only: never reinforce/grow/mutate.
- **Encounter** a diagonal when observed at either endpoint; count each distinct
  diagonal **once**. Score:
  `S_local(B) = Σ_{d encountered ≤ B steps} c(d)·1[q(w_d) = 6]`   (`q(w)=6 ⇔ w ≥ 5.5`).
- **5 independent visitor runs per world**, each **1000 steps**; scores read at nested
  budgets **{100, 300, 1000}**, **B = 300 primary**. Visitor RNG is separate from all
  evolution RNG (`visit_seed = VISIT_BASE + world_index*5 + replicate`).
- Record per run: distinct vertices and diagonals encountered, fraction of present
  diagonals encountered, fraction of globally-high (`q(w_d)=6`) diagonals encountered.

## Fixtures / gates (must pass before analysis)

1. **Full-observation equals global reader:** with the encountered set = all present
   diagonals, `S_local == S_high` (global) on each world, exactly.
2. **No double-counting:** a diagonal observed from both endpoints contributes once.
3. **Replay validation:** replayed t=2000 scalars (`S_high, n_active, frac_active,
   headroom, total_weight, struct_access, eff_alt`) match saved `raw_main.csv` within
   CSV rounding tolerance. *Scalar agreement supports replay consistency; it is not by
   itself proof of per-edge identity.*
4. **Round-trip immutability:** snapshot states/readings are identical before and
   after visitor runs (the visitor does not mutate frozen worlds).

## Worlds & replay (frozen)

- Replay **v11 seeds 0–49**, **all 18 cells**, **both histories**, to **t=2000**.
- History protocol is the actual v11 one: **length-6 path × 3 passes = 18 imposed
  traversal events** (not 48).
- Retain **aligned snapshots**: original + candidate edge identities, presence,
  weights, geometry, histories, coefficients, seed metadata (per patch archive).
- **No-history worlds:** replay **once per (patch, seed)**, reused across the three
  pair-readers (dependence preserved).

## Analysis (frozen)

- **Primary:** per-cell **ordinary AUC at B=300 for a single visitor**, estimated by
  **averaging the AUC over the five visitor-replicate indices** (compute AUC per
  replicate, then average). We do **not** average five per-world scores first — that
  would present a 5×1000-step effort as a 300-step reader.
- **Global comparator on the same worlds:** per-cell global AUC from `S_high`; report
  **local − global** and its uncertainty. Global AUC is **not** assumed to be an upper
  bound (partial observation may omit cancelling contributions).
- **Aggregation:** average the 3 history pairs within a patch, then the 3 patches
  equally, per arm. Report patch/cell variation **separately** from conditional
  simulation uncertainty.
- **Bootstrap:** resample whole **evolution-seed blocks** (seeds 0–49), applied
  **identically across all cells** (shared seed dependence), retaining both histories
  and all five visits.
- **No-history null:** random A/B labels **fixed per world across budgets and visitor
  replicates**; expected-chance **sanity check**, not proof all confounds are excluded.

## Interpretation limits (pre-stated)

A weak result establishes only limited discrimination **for this visitor, score,
budget, and sample** — not that all local readers fail. A positive result
demonstrates **aided observational accessibility**, not autonomous use or transmission.

## Runtime & storage estimate (actual R=10 patch sizes)

Patches: V≈366–380, original edges E≈695–723, candidate diagonals C≈660–688 (≈2×F);
per-world weight vector over `[originals; candidates]` ≈ **~1.4k floats** (not the old
square-grid 144/128).

- **Worlds:** main 50 seeds × 18 cells × 2 histories = **1800**; null 6 patches × 50
  seeds = **300**; total **2100**.
- **Replay:** 2100 × (18 history + 2000 walk) ≈ **4.2M evolution steps ≈ ~2–3 min**.
- **Visitors:** main 1800 × 5 × 1000 + null 300 × 5 × 1000 = **10.5M visitor steps
  ≈ ~4–6 min** (visitor step is cheaper than an evolution step: observe + rounded
  weighted choice, no reinforce/grow).
- **Storage:** 2100 worlds × ~1.4k floats × 8 B ≈ **~24 MB** (float64), compressed
  less; geometry/coeffs stored once per patch. Retained under `results/snapshots/`.

Total wall time ≈ **~8–10 min**; run replay (foreground) then visit+analyse
(background) to respect execution limits.

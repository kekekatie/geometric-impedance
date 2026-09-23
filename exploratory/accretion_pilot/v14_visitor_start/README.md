# Accretion pilot v14 — visitor-start intervention

**Speculative exploration; not confirmatory, not cosmology.** Isolated; chain
v1 `cc514ee` → … → v13 → v14. v1–v13 preserved. No evolution replay, new substrate
construction, merges, publishing, sealed-study access, decoder training, or movement-rule
changes.

Tests whether the v13 tagged visitor's history (A vs B) discrimination **depends on
starting at the shared history start `S`**. A **"distant start"** is frozen from original
geometry only — the vertex maximising original-graph distance to the union of the two
imposed paths, among vertices ≥2 hops from the boundary, canonical coordinate tie-break —
saved before any visitor outcome, and reused for A/B, all seeds, and the null world. The
visitor reproduces v13 movement exactly (verified) and is simply dropped at the distant
start instead of `S`. Frozen evolved weights are read from v13 snapshots (**no replay**).

## Headline

- **Discrimination does not fundamentally depend on starting at `S`.** By B=1000 the
  distant reader matches the original-start reader: `distant − orig` = **−0.001 [−0.005,
  +0.002]** (regular), **+0.001 [−0.003, +0.005]** (perturbed).
- **The cost of a distant start is travel + sampling, not lost memory.** At B=100 the
  distant reader is clearly worse (**−0.060 / −0.052**) because only ~38% have reached the
  imposed paths (median arrival ≈130 steps); the gap shrinks to **−0.017 / −0.013** at
  B=300 (82% arrived) and vanishes by B=1000 (99% arrived).
- **Same in both arms.** Regular and perturbed show the same start-robustness pattern.
- Null ≈ 0.5. **Gates PASS**, including original-S reproducing v13 **exactly** (max|Δ|=0
  over 27,000 values).
- The distant start is **one specified far location, not a representative of all
  locations** — this extends aided accessibility to this arrival point, not to arbitrary
  starts, and is not redundancy or transmission.

See [`REPORT_v14.md`](REPORT_v14.md) for tables, reading, and limitations.

## Contents

- `v14_lib.py` — distant-start selection, snapshot load + geometry verification, visitor
  (reproduces v13 movement) with arrival tracking.
- `v14_run.py` — freeze starts, reproduce v13 (gate), matched distant + null runs.
- `v14_analyze.py` — per-cell/arm AUC, distant−orig, coverage/arrival, null, figure.
- `results/` — frozen starts, raw scores, analysis tables, validation.
- `figures/visitor_start_v14.png` — AUC vs budget, distant−orig @300, coverage & arrival.

## Reproduce

```bash
python3 v14_run.py       # ~13 min
python3 v14_analyze.py   # bootstrap + tables + figure
```

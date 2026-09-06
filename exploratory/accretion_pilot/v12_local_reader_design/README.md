# Accretion pilot v12 — local accessibility of memory (design + data repair)

**Design and existing-data reporting only — no new production trajectories.** Isolated;
chain v1 `cc514ee` → … → v11 `10d4860`. v1–v11 preserved; dated clarifications appended
to `../v11_substrate_pilot/REPORT_v11.md`. No merges/publishing/sealed-study/new
substrate construction.

Addresses whether the stored history distinction is **accessible to a visitor moving
locally through the world**, not just to a global coordinate-aided reader.

## Contents

- [`DESIGN_NOTE_v12.md`](DESIGN_NOTE_v12.md) — (1) v11 closure, (2) the recommended
  minimal local-reader experiment (a passive bounded-encounter visitor on a frozen
  world, aids labelled honestly), (3) the storage/replay feasibility plan.
- [`v12_contrasts.py`](v12_contrasts.py) — computes the matched-offset contrasts at
  t=2000 from existing v11 scalar data (read-only; no new trajectories).
- `results/matched_contrasts_t2000.csv` — the conditional contrast table.

## Reproduce

```bash
python v12_contrasts.py     # ~5 s, reads ../v11_substrate_pilot/results/raw_main.csv
```

## Headlines

- **v11 closed honestly:** the similar arm performance is *descriptive*, not a test or
  equivalence claim; regular-vs-*perturbed* (not order classes); the null is a sanity
  check; the implemented null is one no-history run per (seed,patch) reused across
  readers with analysis-time random labels (differs from the proposed two-run null).
  Matched-offset mean contrast at t=2000 = **+0.007 [−0.018, +0.032]** (seed-bootstrap,
  six patches fixed; not generalisation).
- **Recommended local reader:** a passive, read-only, weighted-walk visitor from the
  shared start S, budget 300 steps, sensing incident edge types and whole-number
  (Δ=1) weights, scoring the v5 proximity-signed one-bit term over encountered
  diagonals. Heavily **aided** (coordinates, path knowledge, edge-type labels — all
  listed explicitly); the only new restriction vs the v11 global reader is the bounded
  encounter budget. Optional coordinate-free trained decoder with whole worlds held
  out. Global comparator on identical worlds; no-history null for static-substrate
  artefacts.
- **Data feasibility:** the existing subsample archive (bare weights over
  `sorted(w.weight)`, no edge IDs, 2 seeds) **cannot** support this. Use deterministic
  **replay** validated against saved scalars, with a reusable snapshot schema (all
  candidate edge IDs + presence + weights + geometry + histories + coefficients +
  checkpoint + seed metadata). Recommended: t=2000, 50 seeds × 18 cells × 2 histories,
  B=300; est. replay ~2 min, readout ~1–2 min, storage ~4 MB. **No replay run performed
  here.**

Awaiting Astra's review of the design before any local-reader execution.

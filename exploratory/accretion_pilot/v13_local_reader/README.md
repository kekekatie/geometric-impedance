# Accretion pilot v13 — bounded local-reader pilot

**Speculative exploration; not confirmatory, not cosmology.** Isolated; chain
v1 `cc514ee` → … → v12 `7a342c5` → v13. v1–v12 preserved. No merges, publishing,
sealed-study access, new substrates, trained decoder, or alternative movement policies.

Tests whether the imposed-history distinction that a **global** reader detects in the
frozen t=2000 world (v11) is also recoverable by a **bounded local visitor**: a passive,
read-only, weighted-walk reader from the shared start `S` that only sees the diagonals it
encounters, scoring the v5 proximity-signed one-bit term (`c(d)` supplied as an
encounter-revealed **tag** — an aided reader).

## Headline

- **Locally accessible.** The bounded tagged reader matches the global reader:
  `local − global @ B=300` = **+0.006 [−0.007, +0.019]** (regular),
  **+0.007 [−0.009, +0.022]** (perturbed) — CI straddles zero.
- **Cheap & early.** AUC ≈ 0.63 already at B=100 (~36% of diagonals seen); flat with
  budget. The signal is redundantly reachable near `S`, not hidden in far diagonals.
- **Regular ≈ perturbed** in accessibility too (AUC ≈ 0.62–0.64, overlapping CIs).
- Null ≈ 0.5 (sanity check passes). All pre-registered gates PASS.

See [`REPORT_v13.md`](REPORT_v13.md) for the full result, reading, and limitations, and
[`PRE_ANALYSIS_NOTE_v13.md`](PRE_ANALYSIS_NOTE_v13.md) for the frozen spec.

## Contents

- `PRE_ANALYSIS_NOTE_v13.md` — frozen spec + gates (fixed before execution).
- `v13_lib.py` — replay, aligned snapshot, `FrozenWorld`, passive visitor.
- `v13_run.py` — replay + snapshot + validate + round-trip + visitor driver.
- `v13_analyze.py` — per-cell/arm AUC, global comparator, null, coverage, figure.
- `results/` — validation, run config, raw visitor CSVs, analysis tables, `snapshots/`.
- `figures/local_reader_v13.png` — AUC-vs-budget, coverage, local−global.

## Reproduce

```bash
python3 v13_run.py       # ~5 min: replay + snapshots + gates + visitor
python3 v13_analyze.py   # reads results/*.csv, writes tables + figure
```

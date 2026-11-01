# Jam-repair pilot — can a legal local rearrangement un-jam a recorded growth jam?

A bounded, exploratory pilot (2026-11-01). It does **not** modify any historical
result; all new outputs live under this directory. Branch
`claude/confident-cerf-404o4f`. It builds on, and imports read-only, the frozen
closure engine at commit `84130b97f5044197392e72cd53e0e71f81b043f3`
(`exploratory/accretion_pilot/expansion_front_paper/`, on
`codex/manuscript-reconciliation`).

**Central question.** Can a legal rearrangement wholly supported by the retained
active skin restore growth after a recorded jam, while preserving the existing
A/B historical-choice readout?

**Short answer (this pilot).** No, for the one move class tested. See
[HANDBACK.md](HANDBACK.md).

## Layout

```
protocol/   PHASE2_DIAGNOSTICS.md, PHASE3_PROTOCOL.md (frozen), PROTOCOL_DEVIATIONS.md
src/        engine_bridge.py, pilot_common.py, hexflip.py, phase1..phase4 drivers
tests/      test_hexflip.py (controlled-example validation of the flip generator)
results/    baseline/ (Phase 1 manifest + per-jam exports), phase2/, phase3/, phase4/
figures/    diagnostic figures
HANDBACK.md the write-up: what ran, what did not, findings, limitations
```

## Reproduce

```bash
# 1. materialise the frozen engine as a read-only git worktree
git worktree add --detach ~/efp-snapshot 84130b97f5044197392e72cd53e0e71f81b043f3
export EFP_SNAPSHOT=~/efp-snapshot/exploratory/accretion_pilot/expansion_front_paper

# 2. deps (Python 3.12)
pip install -r requirements.txt

cd exploratory/accretion_pilot/jam_repair_pilot/src

# 3. smoke test (frozen engine replays a fork + a recorded B jam)
python smoke_test.py

# 4. validate the hexagon-flip generator on controlled examples
python ../tests/test_hexflip.py

# 5. the four phases (Phase 1 ~ several minutes; it builds the fork cache first)
python build_fork_cache.py        # caches the 22 fork S* states (~5 min, once)
python phase1_baseline.py         # baseline + state availability + jam-case exports
python phase2_diagnostics.py      # paired A/B geometry diagnostics
python phase3_repair.py           # single-move repair feasibility
python phase4_readout.py          # A/B readout at the jam checkpoint
python make_figures.py            # optional diagnostic figures
```

All replay is deterministic given `(world, stream)` and is verified against the
saved closure milestones. Nothing here regenerates or edits historical data.

# Audit of the jam compatibility diagnostic — 2026-11-02

A bounded audit-and-correction pass over the study in
`exploratory/accretion_pilot/jam_compatibility_diagnostic/`. No new repair
experiment. Nothing in the frozen engine, the frozen reader, the pilot, or the
study's committed results was modified; all audit outputs live under this
directory.

- **Audited commit (study tip):** `9b3daefe50b250c93c795fbb9cfae089d180c1a4`
  (branch `claude/jam-compatibility-diagnostic`; verified as the latest work —
  no newer commits on that branch).
- **Audit branch:** `claude/jam-compatibility-diagnostic-audit` (based on the
  audited commit; no merge, no force-push).
- **Frozen engine:** imported read-only from
  `84130b97f5044197392e72cd53e0e71f81b043f3` (as the study does).

Read the plain-language summary in [HANDBACK.md](HANDBACK.md); the full findings
in [AUDIT_REPORT.md](AUDIT_REPORT.md); the claim-by-claim corrections in
[CORRECTIONS.md](CORRECTIONS.md).

## Layout

```
src/        audit1..audit5 + audit_common, audit_figures, test_feas_boundary
results/    audit1..audit5 machine-readable outputs
reproduced/ byte-identical re-run of the study's own committed results (proof of reproduction)
figures/    audit_witness_halfplanes.png (corrected witness geometry)
HANDBACK.md / AUDIT_REPORT.md / CORRECTIONS.md
```

The study's original `../results/` and `../figures/` are left untouched for
comparison; `reproduced/` holds a fresh re-run of them (identical).

## Reproduce

```bash
# frozen engine as a read-only worktree (same commit the study uses)
git worktree add --detach /tmp/efp-snapshot 84130b97f5044197392e72cd53e0e71f81b043f3
export EFP_SNAPSHOT=/tmp/efp-snapshot/exploratory/accretion_pilot/expansion_front_paper
export MPLBACKEND=Agg
pip install numpy scipy matplotlib        # Python 3.12/3.13

# the pilot's fork cache is reused if present; else build it once (~5 min):
#   (cd ../jam_repair_pilot/src && python3 build_fork_cache.py)
```

```bash
# re-run the study (writes to ../results; identical to the committed files)
cd ../src
python3 ../tests/test_feas.py      # retained certifier test (passes)
python3 part2_feasibility.py
python3 part3_firstloss.py
python3 part4_iis.py && python3 part4_figures.py
python3 part5_erosion.py
```

```bash
# run the audit checks (writes to audit_2026-11-02/results and figures)
cd ../audit_2026-11-02/src
python3 test_feas_boundary.py      # new failure/boundary tests (passes)
python3 audit1_events.py           # step semantics, F(full) monotonicity, event resolution
python3 audit2_feasibility.py      # box independence, coordinate field, solver failure
python3 audit3_witness.py          # constraints/vertices/tiles, anti-parallel, uniqueness, cross-time
python3 audit4_erosion.py          # corrected connectivity / dead-site / frontier checks
python3 audit5_hexsearch.py        # order-independent single-flip completeness (slow: ~3 min)
python3 audit_figures.py           # corrected witness figure
```

Replay is deterministic from the recorded `(world, stream)` identifiers.
Numerical feasibility remains a float LP over phi-irrational data (robust
numerical evidence, not a symbolic proof); see AUDIT_REPORT.md "Unresolved".

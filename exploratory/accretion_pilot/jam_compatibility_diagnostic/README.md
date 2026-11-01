# Jam compatibility diagnostic

Bounded diagnostic study (2026-11-02). New directory; no historical result
changed, nothing merged or force-pushed. Builds on the jam-repair pilot
(`../jam_repair_pilot/`, source commit `aa371d4`) and imports the frozen engine
read-only from `84130b9`.

**Question.** Which commitments prevent this frontier from continuing, and what
changes when the inner boundary releases some of them?

**Short answer.** Two distant, exactly-opposed commitments near the outer edge of
the retained tiles, locked in at the first free choice (~14 steps before the
visible jam); releasing the inner boundary does not reach them. See
[HANDBACK.md](HANDBACK.md).

## Layout

```
protocol/   PROTOCOL.md (frozen), PROTOCOL_DEVIATIONS.md
src/        study_common.py, feas.py (certifier), part2..part5 drivers
tests/      test_feas.py (controlled polygon/segment/point/empty examples)
results/    case_identifiers.json, part2..part5 json + reports, provenance, spatial
figures/    part4_w5_patch.png, part4_w7_patch.png
HANDBACK.md the write-up (Katie-first, then observations/interpretation/limits)
```

## Reproduce

```bash
# frozen engine as a read-only worktree
git worktree add --detach ~/efp-snapshot 84130b97f5044197392e72cd53e0e71f81b043f3
export EFP_SNAPSHOT=~/efp-snapshot/exploratory/accretion_pilot/expansion_front_paper
pip install numpy scipy matplotlib        # Python 3.12

cd exploratory/accretion_pilot/jam_compatibility_diagnostic/src
# the pilot's fork cache is reused if present; else rebuild it once:
#   (cd ../../jam_repair_pilot/src && python build_fork_cache.py)

python ../tests/test_feas.py     # validate the feasibility certifier
python part2_feasibility.py      # zero-area vs infeasible, certified
python part3_firstloss.py        # first loss of compatibility vs the visible jam
python part4_iis.py              # inclusion-minimal conflicting constraint subset
python part4_figures.py          # figures + spatial analysis
python part5_erosion.py          # inner-rim erosion experiment
```

All replay is deterministic from the recorded `(world, stream)` identifiers and
is verified against the saved milestones. Numerical feasibility is a float LP over
φ-irrational data: `r*` sits far from any tolerance, so "infeasible" is robust
numerical evidence, not a symbolic proof (see HANDBACK "Unresolved numerical
questions").

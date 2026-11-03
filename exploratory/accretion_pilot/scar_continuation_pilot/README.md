# Scar-continuation pilot — 2026-11-03

Two bounded questions on the recorded B-jams, building on the jam diagnostics and
the cooperative-rearrangement audit (`d2e075a`):

1. **Arc readout at the jam** — does the historical A/B choice survive in a
   contiguous compatible **connected sub-arc** of the globally-incompatible
   retained boundary band (active ring)?
2. **Scar-tolerant continuation** — if zero-candidate frontier sites are pinned as
   dormant "scars" (strict Robinson/vertex-star legality otherwise unchanged) while
   the rest grows under the identical patient scheduler and PRNG stream, does growth
   continue to step 44 or cascade, and what do the readers recover afterward?

**Headline (plain):** on all 11 B-jams, the whole band is `empty_incompatible` but
a connected sub-arc of 20–63% reads **correct (B)** discriminatingly; scar-tolerant
growth reaches step 44 in every case with **zero illegal tiles** and no total
arrest, around a small (≤2-component) persistent scar set; and after continuation
the global band is still incompatible while B stays readable in a large sub-arc
(w7: 32%→50%). See [HANDBACK.md](HANDBACK.md) and [protocol/PROTOCOL.md](protocol/PROTOCOL.md).

No matching rules relaxed; frozen engine, frozen reader, reader thresholds, and all
prior pilot/audit directories untouched. Numerical, model-specific; no defect-core
holonomy or physical-memory claim; post-jam growth is a disclosed new trajectory.

## Layout / reproduce

```
protocol/   PROTOCOL.md (frozen before Phase-2 outcomes)
src/        scar_common, arc_tools, phase1_arc_readout, scar_continuation,
            phase3_post_readout, make_figures
tests/      test_scar.py (lift path-independence; strict legality)
results/    phase1/2/3 *.json + *.csv
figures/    scar_w7.png, scar_w5.png
```

```bash
git worktree add --detach /tmp/efp-snapshot 84130b97f5044197392e72cd53e0e71f81b043f3
export EFP_SNAPSHOT=/tmp/efp-snapshot/exploratory/accretion_pilot/expansion_front_paper
export MPLBACKEND=Agg
pip install numpy scipy matplotlib        # Python 3.12/3.13
# fork cache reused if present; else: (cd ../jam_repair_pilot/src && python3 build_fork_cache.py)
cd exploratory/accretion_pilot/scar_continuation_pilot/src
python3 ../tests/test_scar.py
python3 phase1_arc_readout.py --all
python3 scar_continuation.py
python3 phase3_post_readout.py
python3 make_figures.py
```

The frozen reader is invoked unchanged (direct `read()` and the isolated
subprocess agree exactly). Feasibility/readout are float computations over
φ-irrational data: robust numerical evidence, not symbolic proof.

# Validation run (E-prime, before any confirmatory claim): the first sampler pseudo-replicated

The first E-prime run completed cleanly (exit 0, 60 forks, both arms saturated, 0/60 cap-hit) but is
**not a valid confirmatory test**, and is not reported as one. It caught two implementation flaws — which
is what a validation pass is for.

## Flaw 1 — all 60 forks came from ONE world

The sampler asked world 0 (wedge 240) for up to `need` genuine free choices; a single world grown to 700
tiles yields far more than 60, so the loop never advanced past it:

```
distinct worlds: 1
per-world counts: {0: 60}
```

So the "60 genuine free choices across fresh worlds 240–279" were 60 **non-independent** forks from a
single tiling — exactly the pseudo-replication the pre-registration flagged as a known limit ("repeated
forks within a world are not independent"). The **world-cluster bootstrap exposed it on its own**: the
90% CI collapsed to a point, `[-0.127, -0.127]`, because resampling one cluster can only ever return that
cluster. That degenerate CI is the diagnostic working, not a bug.

## Flaw 2 — the pre-reg's age-independence premise for stiffness was untested

The pre-registration (E3) stated "stiffness is age-independent (probe)." The X-axis probe did **not**
measure stiffness vs. patch age — it only tested F_area, local-F, and wall-nearness. This first run (within
its one world) shows **Spearman(patch_age, stiffness) = −0.252**: stiffness carries a *mild* age trend
(older patch → slightly lower stiffness), not zero. So E3's premise was an overclaim and is retracted;
the age control stays mandatory and the stiffness↔age correlation is now reported explicitly, not assumed
away.

## What the run is NOT allowed to mean

The one-world numbers (raw ρ = −0.127, age-partial −0.203, both in the Novelty-Budget direction) are
**not** a confirmatory result and are **not** used to decide E1. Reading a direction off one pseudo-
replicated tiling and keeping it would be exactly the post-hoc move the pre-registration exists to prevent.
The hypothesis, the thresholds, and the two-sided framing are unchanged; only the sampler is fixed.

## The fix (sampler only; hypothesis untouched)

- **Per-world cap.** Collect at most `PER_WORLD` forks from each world, so a target of ~60 spans ~20
  worlds and the cluster bootstrap has real clusters.
- **Age-spread subsampling.** Within a world, collect every qualifying tie across the *full* growth, then
  randomly subsample up to `PER_WORLD` — instead of taking the first few found (which are all young,
  small-patch forks). This keeps patch-age variance so the age control is meaningful.
- **Fresh worlds.** The confirmatory re-run uses wedge entries **241–280** (world 240, the only one
  actually grown here, is skipped, so the confirmatory sample is unpeeked).

The re-run is the confirmatory test; its report is the one that counts.

# Review: Pattern Persistence and Geometric Channelling in Aperiodic Substrates

The companion paper [1] that the connectivity paper builds on. Reviewed because
the whole toy-model line rests on its central claim.

First, credit: this is a markedly more careful paper than the connectivity one.
Four independent matching conditions, effect sizes reported across all of them,
null results stated plainly, and an explicit refusal to claim the
participation-ratio advantage once density is matched. The discipline is real.

But there is a fifth confound that none of the four pipelines controls for, and
it is larger than the effect reported in three of them.

Reproduce with:

```
python3 ppgc_region_confound.py
```

## The uncontrolled variable: region shape

The four matching conditions are count, density, connectivity, and subsampling.
None matches the **region** the points occupy.

Per §II.A, the Penrose substrates are cropped to an inner fraction (0.70 coarse,
0.85 fine), which produces a **disc**. The square lattice is "25 × 25 (625
points)" or "55 × 55 (3,025 points)" — exact squares, so no cropping was applied
— and the random scatter is drawn over the same square domain.

Weighted radius is mean distance from the blob centre. A square point set is
penalised by its corners before any dynamics run at all.

### The substrates really are shaped differently

This is not an assumption; the paper's own numbers force it. Diffusion from a
localised blob approaches the uniform-activation WR from below and cannot exceed
it. In Pipeline A the reported square WR is 0.823. A disc-cropped square lattice
has a uniform-activation WR of 0.752 — so 0.823 would be unreachable. The square
substrate therefore fills the square domain while the Penrose substrate is a disc.

### Size of the confound

WR computed under uniform activation — no dynamics, no update rule, no
substrate behaviour of any kind, just the point sets and the metric, averaged
over 15 starting positions as in the paper:

| pipeline | Penrose | Square | Random | Pen/Sq | Pen/Rnd |
|---|---|---|---|---|---|
| A (~600 pts) | 0.752 | 0.864 | 0.842 | 0.87 | 0.89 |
| B (~3000 pts) | 0.748 | 0.848 | 0.837 | 0.88 | 0.89 |
| C (~3877 pts) | 0.746 | 0.848 | 0.835 | 0.88 | 0.89 |
| D (625 subsampled) | 0.757 | 0.864 | 0.842 | 0.88 | 0.90 |

Against the paper's Table I: **0.63, 0.94, 0.94, 0.91**.

## What this implies, pipeline by pipeline

**Pipelines B, C and D report an advantage smaller than the confound.** Their
Pen/Sq ratios of 0.94, 0.94 and 0.91 are *weaker* than the 0.87–0.88 obtainable
from shape alone. These numbers cannot be interpreted as channelling without
first correcting for region shape. Whether the corrected direction still favours
Penrose, or reverses, depends on the true footprint of the Penrose patches, which
cannot be recovered from the PDF: the correction flips at a Penrose baseline of
about 0.79–0.80, and the plausible range runs from 0.748 (pure disc) to 0.838
(square-cropped). **Undetermined here, and easy for the author to settle.**

**Pipeline A's advantage is larger than the confound and survives it** — 0.63
against a shape floor of 0.87. Something real is happening there. But Pipeline A
is the one pipeline that matches count and degree while *not* matching density,
and the density gap explains it: the Penrose disc carries ~194 points per unit²
against the square's ~156, a ratio of 1.24. Matching mean degree at ~18
neighbours then requires a connection radius of 0.172 on Penrose against 0.191 on
the square, so square activation steps **12% further per update**. Compounded
over the run, that is a straightforward diffusion-rate difference, not
channelling.

The pattern across the paper is consistent with this reading: the advantage is
large (37%) exactly where density is unmatched, and collapses to 6–9% in the
pipelines that match density or radius — where it then falls below the shape
confound.

## The fix

Both are cheap, and neither requires rerunning the dynamics from scratch:

1. **Report WR normalised by each substrate's own uniform-activation baseline.**
   One extra line per substrate: scatter unit activation over the point set,
   compute WR, divide. This makes the metric report *concentration relative to
   that substrate's own fully-diffused state*, which is what the paper means by
   channelling, and removes the region confound entirely.
2. **Add a region-matched pipeline** — crop every substrate to the same disc, or
   generate Penrose over the full square — so the raw numbers are comparable too.

If the advantage survives both, it is a real result and much better defended than
the current four pipelines. Pipeline A additionally needs density matched before
its 37% can be attributed to geometry.

## What this does not affect

The exo/endo axis does not route through this paper. The AB-vs-Penrose address
asymmetry is measured directly on the substrates and stands independently.

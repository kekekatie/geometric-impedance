# Work-GPT/Sol consolidated review

**Date: 2026-08-28. Status: review record only—unresolved and unimplemented.**

## Physical-radius manifest

- Run a geometry-only feasibility preflight before sealing: determine admitted counts at every
  radius, especially the common radius-16 interior set, across every proposed extent, family and
  fresh offset. This may inspect geometry only—no targets, dynamics or outcome curves.
- The Voronoi descriptors need an additional padding/margin rule: a centre at depth `r` can still
  include neighbours whose Voronoi cells are boundary-censored.
- Redefine radial annuli to exclude the centre vertex and handle points exactly one edge length
  away with an explicit numerical-tolerance convention. The present `[0,1)` bin risks being
  constant or ambiguous.
- Drop the edge-length-moment block from the primary if unit-rhombus edges make it degenerate;
  retain it only as a pre-labelled robustness option if justified.
- The proposed parity control is not yet representation-matched: passing a scalar density field
  through an eight-column analogue and padding it with three unrelated columns is not identical
  to M4. Prefer a frozen two-component address-free physical field passed through the actual
  11-column `_m4_cols` pipeline, or state honestly that exact parity has not been achieved.
- Freeze the exact offset list, extents and spatial-block CV scheme. Reconcile the manifests’ five
  existing offsets with the preregistration’s requirement for at least six fresh offsets.
- Rewrite the four outcomes as a hierarchical decision procedure; finite-size failure, radius
  fade and representational collapse are not currently mutually exclusive.

## MSD manifest v2

- The absolute-series Lieb–Robinson bound using `d_max` is rigorous but likely vacuous at
  `t_lo = 2`. Require a geometry-only feasibility calculation before adopting it. If it leaves no
  useful interval, replace it with a pre-specified measured-boundary procedure or enlarge the
  patches—do not force a result.
- The mid-band secondary’s `ΔMSD(t)` can be zero or negative during contraction/recoherence,
  making `log ΔMSD` undefined. Redesign that secondary endpoint or remove its beta fit.
- The unfiltered primary launch is full-spectrum. Remove wording that calls its result “mid-band
  analysed” or implies that it specifically reproduces the earlier mid-band LDOS mechanism. A
  full-spectrum transport result and a same-band mechanistic result are different claims.
- A selection rule can correlate with address even if it does not explicitly use address. Soften
  the claim that physical boundary admission cannot create address-correlated selection; instead
  report and test the admitted population.
- A 48-point grid defined directly on `[t_lo,t_hi]` makes a separate “at least six points”
  feasibility rule automatic; clarify what the rule is intended to guard.
- Freeze whether boundary and quality gates apply independently to coherent and classical
  evolution.
- Replace “mean minus one fold standard deviation greater than zero” with an explicitly justified
  uncertainty rule. Leave-one-offset folds are correlated and five folds are not five independent
  replicates.
- Reconcile five existing offsets here with six or more fresh offsets in the parent
  preregistration.

## Ordering

Do not start the conditional-permutation packet yet. First resolve geometry feasibility,
validation scope, the parity-control construction and the MSD time-window feasibility. After crew
review, amendments can be drafted; only later should implementation begin.

*Source attribution: drafted by Codex from Work-GPT/Sol’s consolidated review, relayed by Katie,
and not part of the scientific record until explicitly reviewed and merged.*

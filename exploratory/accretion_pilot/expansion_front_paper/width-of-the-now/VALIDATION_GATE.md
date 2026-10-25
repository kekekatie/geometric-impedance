# Validation gate (E, before any confirmatory run): the lineage measure does not pass

The v2 pre-registration committed a gate: *lineage endurance must be shown not to be a frontier-speed
proxy before any confirmatory numbers.* A probe was run. **It does not pass. No confirmatory E run was
produced.**

## What was tested

An **attachment-lineage** was built on a fresh active-skin world: each placed tile's parents are the
tiles across the edges it closed; a choice's lineage is the transitive attachment-descendant set. For
tiles placed early (steps 3–8), the descendant set was measured as a fraction of all later tiles.

## Result

The descendant fraction ranges from **~2% to ~70%** of the forward growth cone, depending only on how
central the tile sits in that cone. A tile that anchors 70% of everything that grows after it is not
carrying a specific causal "seam" — its lineage size is essentially **growth-cone volume**, which tracks
frontier activity (the D confound). So attachment-lineage endurance would largely re-measure frontier
volume, not the choice's causal consequence.

## Why this is conceptual, not a tuning problem

Attachment-descent counts **all** downstream growth, regardless of whether the choice *caused* it. The
only clean measure of a choice's causal consequence is the **counterfactual**: what differs if the other
option is committed. That is either

- the per-tile **removal test** (Astra's finding #4 method — remove each tile, recheck forcedness):
  correct but infeasible at 40-world scale; or
- the **branch comparison** (commit A vs commit B, compare final tile sets): already built and validated
  as the `branch-diagnostic/`, confound-free because ambient growth cancels in the difference.

## Decision

Experiment E's active-skin lineage-endurance measure **does not run as scored** — the gate caught it,
exactly as intended. Same-class renewal (E0) remains a valid *reported* phenomenon (the aperiodicity
signature); static residence remains a valid *reported* diagnostic.

## Proposed successor (for the crew to decide)

Test the memory-paper claim — *distance-to-the-wall is a novelty budget* — **directly and cleanly**,
reusing the validated branch machinery: does a genuine free choice's **slack at birth** (the
compatibility-region area / distance from the wall) predict **how far its causal seam reaches** (the
branch divergence `|A-only|+|B-only|`, confound-free, extended with a radius ladder for *how far* the
seam carries)? This measures exactly the quantity §4 is about, with a measure we have already shown is
clean. It would get its own pre-registration (E-prime / "the novelty budget").

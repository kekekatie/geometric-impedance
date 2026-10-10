# Constraint chains: which route carries a choice's consequences? Pre-registration

*Written and committed **before** any code for this study existed.*

## Why

- `../thread_influence/` found that the difference between two alternative presents spreads along the
  now **ahead of** the decided ribbon. It reaches about 0.73 edges per slice against the ribbon's
  0.42, and the ribbon leads only 53% of the time.
- Astra's review: leaving the ribbon doesn't identify the route. Influence could pass through
  **corners** (tiles sharing only a vertex, where the matching rules also act), or along **other
  ribbons**, through chains of shared-edge constraints.
- Astra's suggested next step, adopted here: record which nearby tiles actually force each new
  placement, and trace those dependencies from the changed choice. The whole growing world stays
  intact.

## Construction

**Worlds and choices.**

- The same 24 ordinary worlds as `../thread_influence/`: seed centres from one 18° symmetry wedge,
  random streams `20261110 + k`, patient scheduler, 1,500 half-tiles.
- **Structural de-duplication** (answering Astra's third point): a choice's local configuration is the
  translation class of the decorated tiles within **3 edges** of the choice-edge midpoint, positions
  taken relative to that midpoint. One choice per configuration is analysed: the first in world order.

**Siblings.** Both options are grown forced-only for up to 12 slices. Each placed tile records its
slice, the frontier edge that forced it, and that edge's **owner** (the tile on the other side).

**Critical tiles.** For a tile t forced at slice s:

- Its **context** is the tiles present before slice s in that sibling, within 2.5 edges of t's
  centroid, plus the owner.
- Check **Z:** in the context alone, the forcing edge has exactly one candidate, and it is t.
- A context tile u is **critical** if removing it leaves the forcing edge with anything other than the
  single candidate t.
- The owner is critical by definition.

**The difference.** Δ = tiles in a sibling that the other sibling covers with a different tile. Both
are measured at the end of the analysed slices, using only slices both siblings reached. The chosen
tile itself is in Δ (slice 0).

**Links.** For each Δ tile t, its **Δ-parents** are its critical tiles that are themselves in Δ. Each
link (parent u → t) is classified by contact:

- **decided ribbon:** u and t share a rhombus edge of the decided family j\* (chosen per sibling as in
  `../thread_influence/`), and both lie on the decided ribbon;
- **other edge:** they share any other edge (another ribbon, or the diagonal inside one rhombus);
- **corner:** they share exactly one vertex;
- **distant:** they share no vertex.

**Advances.** A Δ tile laid at slice s is an **advance** if its along-front coordinate x (as in
`../thread_influence/`) goes beyond the extent of all earlier Δ tiles (a new maximum or minimum).
Each advance is given its **best route**: *decided ribbon* if any Δ-parent link is of that kind;
otherwise *other edge*; otherwise *corner*; otherwise *distant*; otherwise *none* (no Δ-parent).

## Checks and predictions

- **Z (sanity).** At least 99% of analysed Δ tiles are uniquely forced by their context.
- **C1 (Claude's corner reading).** Among advances with at least one Δ-parent, the *corner* share is at
  least **1/3**. *Confidence about 35%.*
- **C2 (Astra's alternative: other ribbons).** Among those advances, the *other edge* share is
  **greater** than the *corner* share. *Confidence about 55%.*
- **C3 (the decided ribbon carries a minority of advances).** The *decided ribbon* share is **at most
  0.5**. *Confidence about 60%.* This is consistent with D1's 53% (a different measure).

## Reported without prediction

- The number of choices and of distinct configurations.
- The route shares for all Δ tiles, not only advances.
- The *none* and *distant* shares.
- **Baseline:** for 400 randomly sampled non-Δ forced tiles in the same siblings, the share of all
  critical links by contact type. This shows whether corners are critical generally, or especially
  for carrying differences.
- How many critical tiles a forced placement typically has.

## Limits, stated in advance

- "Critical" is single-removal: a tile whose role is duplicated by another may not register.
- A 2.5-edge context, as in `../past_or_present/`.
- Up to 12 slices.
- The decided ribbon is identified by a simple rule.
- One tiling family.

## Changes before the first run

- **Baseline sampling (2026-10-10, while writing the code, before any run).** Instead of exactly 400
  non-Δ tiles drawn from the whole pool, **6 per sibling per analysed choice** are sampled (random
  stream `4040 + world`). This gives roughly 400 in total, and the sample is spread evenly over
  choices.

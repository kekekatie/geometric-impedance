# Decided by the past or by the present? Pre-registration

*Written and committed **before** any code for this study existed.*

*Gemini's question (2026-10-06, relayed by Katie): are some places decided **sideways by the active
present** rather than by their history? The "undecided 10%" turned out to be an artefact
([`../decision_radius/`](../decision_radius/)), but the question underneath stands. Here we watch
every forced tile at the moment it is forced and ask **how much memory** is needed to force it.*

## Construction

**Worlds.**

- The 4 intact DECAPOD worlds of `../decision_radius/` (seeds 2, 3, 4, 5).
- Each is grown exactly as in `../structure_clock/` (patient scheduler, decagon wall, no guesses) to
  **2,000** half-tiles, with placement rounds recorded.
- Hull depth comes from the final patch (`../perp_map/`). A tile's depth is the mean of its three
  vertices' depths.

**Memory horizon of a forced tile.**

- At the start of round `r`, take each frontier edge `e` with exactly one candidate `t`, the tile
  then placed. The **owner** of `e` is the tile already on its other side.
- For each horizon `a ∈ {1, 2, 3, 5, 8, all}` rounds, build a local patch:
  - the owner tile;
  - every tile within **2.5 edges** of `t`'s centroid that was laid in rounds `r − a … r − 1`;
  - for "all", every tile within 2.5 edges, whatever its age.
- `t` is **forced at horizon `a`** if, in that patch, `e` has exactly one candidate and it is `t`
  (decoration-aware `../decapod_seed/` candidates).
- `a*` = the smallest horizon at which `t` is forced: the **memory needed**.
- Small `a*` means decided by the **present**: what has just happened around it. Large `a*` means
  it needs the **past**.

## Checks and predictions

- **Z (asserted).** Every forced placement is forced at horizon "all". Legality is local, so the full
  2.5-edge neighbourhood must reproduce the growth's own forcing.
- **G1 (the present decides most tiles).** Pooled over the 4 worlds, the median `a*` is **≤ 2**
  rounds: most tiles are pinned down by the last two rounds' happenings, plus their owner.
  *Confidence about 60%.*
- **G2 (deep places lean more on the past).**
  - Within each world, take Spearman(tile depth, `a*`) inside radius bins 1 edge wide (bins with at
    least 15 tiles), weighted-averaged as in `../structure_clock/`.
  - Prediction: it is **> 0** in at least **3 of 4** worlds. This would fit deep places needing a
    wider ring of their past (`../decision_radius/` R1).
  - *Confidence about 50%.*

## Reported without prediction

- The full distribution of `a*`.
- The share of tiles decided by the present alone (`a* = 1`) against those needing at least 3 rounds
  of memory.
- `a*` by depth third.
- The owner tile's age (how long its edge waited).

## Limits, stated in advance

- "Memory" is counted in rounds, the universal clock, not in local happenings.
- 4 worlds that share structure.
- Forcing is edge-level, which matched vertex-level forcing in `../gromit_check/`.

## Changes before the first run

*(none yet)*

# How much of the world must weigh in? Decision radius vs depth. Pre-registration

*Written and committed **before** any code for this study existed.*

*[`../structure_clock/`](../structure_clock/) found that places deep in the hidden window keep their
now open longer: about 30% more rounds, and about 15% more local happenings. Claude's proposed
mechanism: a deep place has balanced, plentiful options (Katie's directional balance,
doi:10.5281/zenodo.20695694), so it cannot be pinned down by a little local news. **More of the world
has to weigh in before it is decided.** This study measures that directly, as the size of the
surrounding context needed to determine a place uniquely.*

## Construction

**Worlds.** 4 zero-guess DECAPOD worlds: the first 4 used in `../structure_clock/` (seeds 2, 3, 4,
5). Each is grown exactly as there, to 2,000 half-tiles with placement rounds recorded, and lifted
for hull depth.

**Probes.**

- Vertices with `4 ≤ |v| ≤ 10` edges that lie at least **4.5 edges** from the final frontier, so the
  whole context fits inside the patch.
- Up to **100** per world, chosen with random stream `2050 + seed`.

**Decision radius of a probe.**

- **Disc:** the final-patch tiles whose centroids lie within 1.0 edge of `v`.
- **Target:** the 17 sample points of `../continuation_choices/` (the centre, 6 points at 0.4 edges,
  10 points at 0.8 edges, with a fixed small offset).
- For each context radius `ρ ∈ {1.5, 2, 2.5, 3, 4}` edges:
  - the **context** is every final-patch tile whose centroid lies within `ρ` of `v` and is not in
    the disc;
  - from the context alone, try to **complete** the target 16 times:
    - forced-first, otherwise a random choice at the nearest open edge;
    - only tiles with centroids within 1.8 edges of `v` may be added;
    - one-step look-ahead, as in `../continuation_choices/`;
    - candidates come from the decoration-aware `../decapod_seed/` `candidates`.
- The probe is **decided at `ρ`** if at least one completion succeeds and every successful
  completion covers the target with exactly the final tiling's tiles.
- **Decision radius** = the smallest `ρ` at which the probe is decided. It is **5** (censored) if
  none is.

**Settling time** `T` for each probe, exactly as in `../structure_clock/`: the rounds from the first
to the last placement of its disc.

## Predictions

- **R1 (deep places need more of the world to weigh in).** Within each world,
  `Spearman(depth, decision radius) > 0` in **at least 3 of 4** worlds, and the median across worlds
  is **≥ 0.15**. *Confidence about 50%.*
- **R2 (and that is why their present lasts longer).** Within each world,
  `Spearman(decision radius, T) > 0` in **at least 3 of 4** worlds. *Confidence about 55%.*

## Reported without prediction

- The distribution of decision radii.
- Mean decision radius by depth tercile.
- The censored fraction.

## Limits, stated in advance

- Alternatives are sampled (16 attempts), so a rare alternative can be missed. This makes small
  radii look decided too easily.
- The context is a geometric disc. Real "news" travels along chains of forcing, not in circles.
- 4 worlds that share structure. 100 probes each.

## Changes before the first run

*(none yet)*

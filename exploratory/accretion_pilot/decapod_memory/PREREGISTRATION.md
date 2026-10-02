# Where does a decapod keep its memory? Pre-registration

*Written and committed **before** any code for this study existed.*

*[`../perp_map/`](../perp_map/) (M2) found that worlds grown from a decapod seed have a **smeared**
perp-space window: a hull 8–13% larger than ordinary worlds of the same size. The working
explanation is that the decapod's ten half-worms divide the world into sectors, and each sector's
hidden addresses fit a slightly **shifted** copy of the window. That is the decapod's holonomy, its
"memory".*

*If so, the memory should be **locatable**. Split the world by angle around the decagon. In an
ordinary world every sector's addresses sit in the same window. In a decapod world the sectors'
windows should be offset from one another, with the shifts happening along lines (worms).*

*Toolkit: Katie's paper, doi:10.5281/zenodo.20695694 (perp addresses, windows, hull depth), and
`../perp_map/perp_map.py` (the lift).*

## Construction

**Worlds.**

- The same 8 DECAPOD and 4 FILLABLE seeds as `../perp_map/` M2, regrown deterministically (run 0)
  with the decagon wall.
- This time to **1,500** half-tiles, so each sector holds enough vertices.

**Lift.** As in `../perp_map/`: every vertex gets `K ∈ Z⁵` and a perp address
`z⊥ = Σ K_j ζ^{2j}`, and its layer is `ΣK`.

**Sectors.**

- Vertices are binned by their physical angle around the decagon centre into **20 sectors** of 18°.
- Only vertices beyond 2.5 edges from the centre are used (outside the decagon and its ring).

**Window offset of a sector.**

- For each layer with at least 40 vertices in the whole world, compare the mean perp address of the
  sector's vertices in that layer (used only if the sector has at least 5 of them) with the mean
  over the whole world in that layer.
- A sector's offset is the distance between the two, averaged over the qualifying layers.
- The **world's memory score** is the mean offset over its sectors.

**Sampling baseline.** Small sectors give noisy means even in a perfect tiling. That is why the
FILLABLE worlds, which are genuine Penrose patches, are the baseline.

## Predictions

- **D1 (the memory is real).** Every one of the 8 DECAPOD worlds has a memory score **larger than the
  largest** of the 4 FILLABLE worlds' scores. *Confidence about 55%.*
- **D2 (the memory is in sectors, not spread evenly).**
  - In DECAPOD worlds, sector offsets should be organised by angle: neighbouring sectors' mean
    perp addresses agree more than distant sectors' do.
  - Measure: the mean distance between the window centroids (as above) of **adjacent** sectors,
    divided by that of sectors **5 apart** (90°).
  - Prediction: the median ratio over DECAPOD worlds is **below 0.8**, and **lower** than the
    median over FILLABLE worlds. *Confidence about 45%.*

## Reported without prediction

- The offset vector of each sector, plotted against angle, for one DECAPOD and one FILLABLE world:
  where the jumps are, and whether there are about 10 of them (one per worm).
- Window hull areas, as in `../perp_map/`, at 1,500 tiles.

## Limits, stated in advance

- 20 sectors of 18° are coarse, and worms need not run exactly radially.
- Sector means are noisy; the FILLABLE baseline is only 4 worlds.
- This measures **where** the shifted windows sit, not **why**.

## Changes before the first run

*(none yet)*

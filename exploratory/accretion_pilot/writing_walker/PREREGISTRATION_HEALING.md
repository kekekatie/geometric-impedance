# Can the walker's knots be healed locally? Pre-registration

*Written and committed **before** any code for this test existed. Katie asked whether the
defects the writing walker leaves behind are blemishes (removable by small local changes) or
knot-like (only the whole can undo them). Results will be reported against these predictions.*

## Setting

- The writing-walker tiling (`writing_walker.py`): push `δ = 0.2`, full journey
  (`t_start = −30 → t₀ = 30`), patch `R = 40`.
- **Local move:** a **hexagon flip**. A vertex where exactly three rhombi meet (degree 3) sits
  inside a hexagon, and the three rhombi are replaced by the hexagon's other three-rhombus
  tiling. This is the elementary local move of rhombus tilings, and the one the walker itself
  makes.
- **Knots:** the walker's illegal vertices (star shape not in the atlas) in the middle of the
  wake (`|t| ≤ 25`, in tile units), grouped into knots by single linkage at distance 2.5 tile
  edges.
- **Healing a knot:** a sequence of hexagon flips, every flipped vertex within **3 tile edges** of
  the knot, that leaves every vertex of the knot legal and creates **no** new illegal vertex among
  the vertices whose star changed.
- **Search:** exhaustive breadth-first search over flip sequences up to **depth 4**, with states
  deduplicated.

## Checks and predictions

- **H0 (sanity, asserted).** In the pristine Penrose tiling, a single hexagon flip that creates an
  illegal vertex is always healed at depth 1 (by flipping it back). Tested at up to 40 such
  flips, or all of them if there are fewer. If no single flip creates a shape-illegal vertex,
  that is reported and H0 is vacuous.
- **H1 (the question).** **Fewer than 25%** of the mid-wake knots can be healed within depth 4.
  They behave like knots, not blemishes. *Honest confidence about 60%.* The walker shifted its
  line all along the wake, so locally undoing the shift near one knot should just create new
  mismatches at the edges of the undone stretch.
- **H2.** The same holds at a gentle push, `δ = 0.05`: fewer than 25% of knots heal within
  depth 4.

## Reported without prediction

- For knots that do heal, the depth needed.
- As a reference, the non-local cure: undoing **all** of the walker's flips restores the pristine
  tiling. This is true by construction, and it is checked.

## Limits, stated in advance

"Not healable within depth 4 and radius 3" is **evidence** of knot-like (topological) behaviour,
not a proof. A deeper search or a larger radius might heal some. Legality means the star
shape is in the atlas, without matching arrows.

## Changes before the first run

*(none yet)*

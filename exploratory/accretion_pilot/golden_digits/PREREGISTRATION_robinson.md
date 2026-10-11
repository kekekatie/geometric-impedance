# The Robinson rule for splits: pre-registration

*Written and committed **before** the check below was coded or run.*

**Found post hoc** in the 24 golden_digits worlds ([`shapes_EXPLORATORY.py`](shapes_EXPLORATORY.py),
[`results/shapes_EXPLORATORY.txt`](results/shapes_EXPLORATORY.txt)):

- When the wiggle room F at a choice is a **Robinson triangle** (a golden triangle with angles
  36°-72°-72°, or a golden gnomon with angles 36°-36°-108°),
- and the cutting line passes through **exactly one** of its corners,

then the choice splits F the way Penrose's subdivision rule splits that triangle. The smaller piece is
a **smaller copy of the same triangle** (scale 1/τ). Its share is exactly **1/τ² = 0.382**. The larger
piece is the **other** Robinson triangle. This happened in 29 of 29 such cases. If it holds generally,
the commonest split is *derived* from geometry rather than only measured.

**The test.** Apply the identical census code (shape, cutting line, corners crossed) to the **24
worlds of `../slack/`**. Their split shares have been measured, but their shapes have never been
examined.

**Prediction R.** Among the slack choices where F is a Robinson triangle and the cutting line crosses
exactly one corner, at least **95%** have:

- a smaller share within **0.001** of 1/τ² = 0.38197;
- a smaller piece of the **same** triangle type as F;
- a larger piece of the **other** type.

*Confidence about 85%.*

**Reported without prediction:**

- how many slack choices fall in that class;
- the shape and cut census for all other slack choices.

**Limits.** This tests one derivation rule, the one-corner Robinson cut. Other cut types (parallel to
a side, along a diagonal) are described, not derived.

## Changes before the run

*(none yet)*

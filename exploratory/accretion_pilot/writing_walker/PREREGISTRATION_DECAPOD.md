# Is the stubborn centre knot one of Conway's bad decapods? Pre-registration

*Written and committed **before** any code for these tests existed. Katie chose to chase the
centre knot.*

## What was looked at before writing this (descriptive only)

- The one knot the healing test could not remove (`healing.py`, `t = 0`, 12 illegal vertices)
  consists of **10 vertices on a ring of radius φ around the origin, spaced 36° apart**, plus two
  more.
- Those 10 are the corners of a **unit-edge regular decagon** (circumradius `1/(2 sin 18°) = φ`).
- In the pristine tiling and in both walker tilings, the decagon's 10 rim edges are tile edges,
  with 6 vertices inside. It is a decagon filled with 10 rhombi.
- The tiling's offsets are mirror-symmetric (`γ_j = γ_{−j}`). That explains why the other knots
  sit at mirror-image positions `±t`, not a golden-ratio law. Yesterday's "golden-ish" remark is
  withdrawn.
- **Literature** (recalled, and checked by a quick search): Conway's **62 decapods** are
  decagonal patches that arise where ten half-infinite worms meet around a cartwheel centre.
  2 are legal; the other 60 are defects whose hole **cannot be filled legally**. Flipping worms
  switches between them.

**Hypothesis:** the walker, a worm flipper whose road passes through the centre decagon, turned a
legal decapod into a bad one.

## Tests

- **D1 (sanity, asserted).** In the pristine tiling, at least one filling of the centre decagon
  (the existing one) makes the decagon's rim and interior vertices all atlas-legal.
- **D2 (decisive, exhaustive).** In the walker tiling, with everything outside the decagon fixed,
  enumerate **all** fillings of the decagon reachable by flips at its interior vertices, with no
  depth limit. *Prediction:* **none** is atlas-legal at the rim and interior vertices, at push
  0.2 and at push 0.05. The hole cannot be filled legally: a bad decapod. *Honest confidence
  about 65%.* Also reported: the number of fillings reached. The rhombus tilings of a unit
  decagon are flip-connected, so this should be all of them (62, if my recollection of that
  count is right).
- **D3 (wider).** Allowing flips at every vertex within radius 3 of the centre, with an
  exhaustive search capped at 500,000 states, the knot still cannot be healed (criterion as in
  `healing.py`), at push 0.2. *About 55%.*
- **D4 (location).** Walkers on other roads (family 0, lines `c ∈ {−4..4}`; family 1, lines
  `c ∈ {−4..4}`; push 0.2; full journey), in the same tiling. For every mid-wake knot, record:
  - whether it heals within depth 4 (as in `healing.py`);
  - whether it contains a **decagon ring**: at least 8 of its illegal vertices lie at distance
    φ ± 0.02 from a common point, 36° apart.

  *Prediction:* the two properties agree for **≥ 90%** of knots. Knots with a ring are stubborn;
  knots without one heal. *About 55%.*

## Limits, stated in advance

Legality means star shapes against the atlas, without matching arrows. "Bad decapod" is used here
as a *hypothesis label* matching Conway's description. Identifying which of his 62 it is would
need arrow-level matching rules, which are not implemented.

## Changes before the first run

*(none yet)*

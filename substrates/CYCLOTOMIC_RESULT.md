# Address fragility follows the cyclotomic field

The first prospective result in this project. The prediction below was committed
to git (`5deadfa`) before the run completed.

> *"If arithmetic drives fragility, 10-fold (golden, as Penrose) should be fragile
> and 8-fold (silver, as Ammann-Beenker) robust. 12-fold is the new point and
> carries no prediction."*

## The family

An N-fold quasicrystal's natural module has rank φ(N). Since φ(8) = φ(10) =
φ(12) = 4, all three live in **Z⁴ with a 2-dimensional perpendicular space** —
identical lattice rank, identical window construction (zonotope over four
perpendicular generators), identical edge rule. Only the cyclotomic field varies.

| N | field | ratio | verts | mean degree | edge lengths |
|---|---|---|---|---|---|
| 8 | Q(√2) | silver, 1+√2 | 4,365 | 3.940 | 1 |
| 10 | Q(√5) | golden, (1+√5)/2 | 4,289 | 3.939 | 1 |
| 12 | Q(√3) | platinum, 2+√3 | 4,149 | 3.937 | 1 |

All three are valid tilings, which the earlier window-scale family was not.

## Result

Address AUC at matched *measured damage*, interior-50%, matched 5% positive rate,
3 disorder seeds. Shuffle nulls run 0.46–0.52 across all fifteen cells.

| vertices flipped | 8-fold (silver) | 10-fold (golden) | 12-fold (platinum) |
|---|---|---|---|
| 10% | **0.9759** | **0.8421** | 0.9203 |
| 20% | 0.9528 | 0.8057 | 0.8760 |
| 30% | 0.8765 | 0.7304 | 0.8279 |

**Ordering: silver > platinum > golden, at every damage level.**

## Why this is stronger than the earlier comparisons

**The prediction was prospective.** Recorded in version control before the
measurement existed. Every previous mechanism in this project was fitted to data
already seen, and three of them died on contact with a control.

**The 10-fold substrate shares nothing with Penrose but its field.** Different
lattice (Z⁴ against Z⁵), different window (a zonotope against four pentagons),
different perpendicular dimension, different edge structure. Golden-ratio
arithmetic reproduces Penrose's fragility in a construction with nothing else in
common with it. That rules out window topology, lattice dimension and
construction as the cause.

**The family is complete, not sampled.** φ(N) = 4 has exactly four solutions —
N = 5, 8, 10, 12 — and N = 5 and N = 10 generate the same field. There are
therefore exactly three quasicrystal families at perpendicular dimension 2, and
all three are measured here. The n=1 concern that undermines the earlier "cliff"
results does not apply: there is no fourth field to test.

## What is still unknown

**Why.** The empirical ordering is silver > platinum > golden. One tempting
reading: the golden ratio is the most badly approximable irrational — its
continued fraction is all 1s — and it is the most fragile, which would *invert*
the naive intuition from KAM theory that greater irrationality brings greater
stability. We record that as an observation and decline to assert it. Three
fields cannot establish a relation to any approximation-theoretic quantity, and
this project has a poor record with mechanisms that explain the data they were
built from.

**Limits.** Three disorder seeds; one privileged-site definition; the ordering's
statistical separation between platinum and silver is smaller than that between
either and golden.

**The next family.** φ(N) = 6 gives N ∈ {7, 9, 14, 18} at perpendicular dimension
4. That tests whether the field-dependence persists at higher rank, and supplies
new fields — but changes dimension, so it is a second comparison rather than an
extension of this one.

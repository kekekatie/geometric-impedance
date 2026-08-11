# Phason strain as a tunable perturbation

Every perturbation used in the repository so far is degree-preserving random
rewiring, which drives edge Jaccard to 0.0001 in one step. It has no intermediate
setting, and the perturbed object is not a tiling — it is a random graph wearing
the original degree sequence.

Phason strain is the physically correct perturbation for a cut-and-project
quasicrystal, and it is directly implementable: shift the acceptance window.
Vertices near the window boundary enter or leave, which is exactly a phason flip.

## Measured on Ammann-Beenker (8,069-vertex patch)

| perturbation | vertices flipped | vertex Jaccard | edge Jaccard |
|---|---|---|---|
| window shift 0.002 | 0 | 1.0000 | 1.0000 |
| window shift 0.01 | 64 | 0.9921 | 0.9880 |
| window shift 0.05 | 422 | 0.9490 | 0.9246 |
| window shift 0.15 | 1,174 | 0.8643 | 0.8048 |
| window shift 0.40 | 3,172 | 0.6706 | 0.5532 |
| 5E random rewiring | 0 | 1.0000 | **0.0001** |

## Why this matters

Every intermediate state remains a valid Ammann-Beenker tiling — same matching
rules, same 8-fold symmetry, different phason phase. The perturbation stays
inside the space of quasicrystals rather than leaving it immediately.

This makes dose-response experiments possible for the first time in this line of
work. Instead of "intact versus annihilated", the address channel can be swept
against perturbation magnitude, and substrates can be compared by *where* they
fail rather than only by whether they fail.

## Open work

- The generator here is Ammann-Beenker (Z⁴, octagonal window). An equivalent
  Penrose generator (Z⁵, pentagonal window) is needed to run the comparison, and
  is the same construction one dimension up.
- Note that a window shift alters the vertex set, so labels and features must be
  recomputed per phason phase and matched by lift coordinate rather than by row
  index.

Run with `python3 phason_shift.py`.

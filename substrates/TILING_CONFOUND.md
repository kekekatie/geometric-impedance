# The cyclotomic substrates are not all tilings

Found while building the machinery for a recovery experiment. A phason flip is a
*tile* operation, not a graph operation, so the first step was to check the face
structure of the three cyclotomic substrates. The check failed.

## What was measured

Planar embedding traced by rotation system, faces enumerated, edge crossings tested
directly by segment intersection. Extent 9, ~1,400 vertices each.

| family | vertices | edges | proper crossings | bounded faces | quads | Euler V−E+F | distinct rhombi |
|---|---|---|---|---|---|---|---|
| 8-fold, silver | 1443 | 2812 | **0** | 1370 | 100.00% | 2 | 2 (45°, 90°) |
| 10-fold, golden | 1411 | 2748 | **664** | 654 | 75.08% | −682 | — |
| 12-fold, platinum | 1373 | 2672 | **0** | 1300 | 100.00% | 2 | 3 (30°, 60°, 90°) |

Silver and platinum are perfect rhombus tilings: every bounded face a rhombus, Euler
characteristic exactly 2, and the rhombus vocabulary the N-fold construction predicts.

**Golden is not a tiling.** It has 664 pairs of properly crossing edges, faces of size
12 and 20, and an Euler characteristic of −682. It is a graph drawn in the plane with
edges passing through one another.

## Why

The edge rule was "connect lattice points differing by one basis vector." That is
identical across the three families *in Z⁴ coordinates*. It is not identical in the
plane, because which planar directions the four basis vectors occupy depends on N:

| N | complete star | directions the basis rule uses | missing |
|---|---|---|---|
| 8 | 0°, 45°, 90°, 135° | all 4 | none |
| 10 | 0°, 36°, 72°, 108°, 144° | 4 of 5 | 144° |
| 12 | 0°, 30°, 60°, 90°, 120°, 150° | 4 of 6 | 120°, 150° |

The reason is arithmetic: ζ₈⁴ = −1, so for N = 8 the fourth power folds back onto an
existing direction and four basis vectors already span the complete octagonal star.
For N = 10 and N = 12 they do not. Ammann-Beenker was the only family that got a
complete star, and it got it by luck of the minimal polynomial.

Twelve-fold survives the amputation and still tiles. Ten-fold does not.

## Why this is serious

The confound tracks the result monotonically:

| family | star | planar tiling | address fragility |
|---|---|---|---|
| silver | complete | yes | most robust (0.976) |
| platinum | incomplete | yes | middle (0.920) |
| golden | incomplete | **no** | most fragile (0.842) |

The measurement stands — the AUCs are what they are, on the graphs as built. What
cannot be claimed is the causal sentence: *"only the cyclotomic field changes."* Star
completeness and planarity change too, in lock-step with the outcome. Any of the
three could be doing the work and this design cannot separate them.

There is a defensible position in which the field is still the cause — star
completeness *is* a consequence of the arithmetic, so the field determines fragility
*through* the star. But that is a different and much weaker claim than the one the
paper makes, and it needs the mechanism spelled out rather than asserted.

## The obvious fix does not work

Rebuilding with the full N-fold star while keeping the Z⁴ window makes things worse,
because the window no longer matches the star:

| N | edges | mean degree | crossings |
|---|---|---|---|
| 8 | 2812 | 3.897 | 0 |
| 10 | 3273 | 4.639 | 1265 |
| 12 | 3551 | 5.173 | 451 |

## The fix that does work — and where it leads

The canonical N-fold rhombus tiling needs the lattice to match the star: Z⁴ for
8-fold, Z⁵ for 10-fold, Z⁶ for 12-fold. That is `generate_nfold.py`, the family
previously set aside because perpendicular dimension varies. Audited the same way:

| n | fold | perp dim | vertices | crossings | quads | Euler | distinct rhombi |
|---|---|---|---|---|---|---|---|
| 4 | 8 | 2 | 1439 | 0 | 100.00% | 2 | 2 |
| 5 | 10 | 3 | 1043 | 0 | 100.00% | 2 | 2 |
| 6 | 12 | 4 | 720 | 0 | 100.00% | 2 | 3 |

All three are proper rhombus tilings.

So the two families trade the same confound back and forth: the cyclotomic Z⁴ family
matches perpendicular dimension but breaks the tiling, and the Z^n family tiles
properly but varies perpendicular dimension.

**There is a reconciliation available, and it is already half-measured.** For Penrose
(Z⁵) the extra perpendicular direction is the lift sum, and `discrete_vs_continuous.py`
showed it to be inert — AUC 0.5398 at zero disorder against chance, rising only to
0.5696 at disorder 0.20. It carries no address information and does not degrade. Z⁵'s
"perpendicular dimension 3" is really **2 continuous address dimensions plus one inert
grading.**

If the same holds for Z⁶ — 2 continuous plus 2 inert gradings — then the Z^n family is
*already* matched at 2 continuous address dimensions, consists of genuine rhombus
tilings, carries complete stars, and is strictly the better substrate family on every
axis we care about.

## Next test, in order

1. **Measure whether the extra perpendicular dimensions are inert in Z⁵ and Z⁶.**
   Same method as `discrete_vs_continuous.py`: split the address into the 2 continuous
   coordinates versus the grading directions and measure each separately at zero and
   nonzero disorder. Cheap, decisive, and it gates everything below.
2. **If inert: re-run the headline on the Z^n family**, damage-matched as before. This
   is a real risk to the result and should be treated as such — prediction recorded in
   git before the run, as with the cyclotomic prediction.
3. **Only then, recovery.** Tile flips are definable on proper rhombus tilings and
   undefined on a graph with crossing edges, so the recovery experiment was blocked on
   this regardless.

## Note on the paper

`address_fragility.md` v2.0 states in §6.2 that lattice, rank, perpendicular dimension,
window construction and edge rule are identical and only the field varies. The last
clause is false as built. The paper should not be uploaded in its current form.

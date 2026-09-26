# Laying the tiling — Penrose laid half-tile by half-tile, with no map

**The 2-D sequel to [`../laying_the_street/`](../laying_the_street/).** Isolated, with prior
studies untouched.

The Penrose tiling is laid **one half-rhombus at a time**, always at the edge nearest the centre,
using **only the tiles already laid**. There is no cut-and-project map and no hidden window. From
a reference tiling we learn only its **atlas of vertex stars** (which corner-meetings are legal).
That atlas is exactly the **8 classic Penrose vertex types**. A tile is legal if it doesn't
overlap anything and every corner it touches is part of an atlas star. Checked: re-laying
4,570 genuine Penrose tiles in order, the legality test rejects none.

![patches](figures/patches.png)

## Results (`laying_the_tiling.py`, exit 0)

| how the next tile is chosen | outcome |
|---|---|
| **LOCAL, dice**: any legal tile at the nearest edge | **jams in 30/30 runs** (median after 14 half-tiles, longest 249): an edge where nothing fits |
| **LOCAL, forced first**: place a tile where exactly one fits; otherwise guess | **never jams** (30/30 reach 500 half-tiles), with **3–4 guesses per run**, but builds a **different Penrose universe** every time (never exactly the self-similar tiling; 79–100% agreement) |
| **COPY**: same-scale twin (copy what's across a matching laid edge) | lays an **illegal** tile after 14 |
| **SCALE**: the patch consults its own zoomed-out self (τ², mirrored; verified exact) | **500 half-tiles, no jam, zero guesses, 100% the self-similar tiling** |
| WRONG-SCALE: one zoom step, not the tiling's own symmetry | proposes nothing |
| SCALE from 12 **off-centre** starting patches | proposes nothing, every time |

## In plain words

- **Pure local fitting jams**, just as the 1988 physics found (Onoda, Steinhardt, DiVincenzo and
  Socolar).
- **Not predicted: in 2-D a *smarter* local strategy does not jam**, at least to 500 tiles, unlike
  1-D, where no local rule can work. But it has to **guess** a few times. Each guess **chooses
  which Penrose universe gets built**, and the guesses are imported randomness.
- **Consulting its own zoomed-out self builds the tiling exactly, with no guesses.** It imports
  nothing: commandment 2. The same lesson as 1-D: likeness **across scales** lays the
  quasicrystal, while same-scale copying fails.
- **Where two universes differ, they differ along thin bands that run exactly along ribbon
  directions**, the roads of [`../least_resistance_paths/`](../least_resistance_paths/). This is
  now tested ([`worm_test.py`](worm_test.py); see below). The choice of universe is written along
  the roads.

## The worm test (`worm_test.py`, exit 0)

Do the differing tiles of forced growth really lie along ribbons? The half-tiles are paired back
into rhombi, and the rhombi that differ from the self-similar tiling are compared with random
sets and random *connected* clusters of the same size from the same patch.

| | differing rhombi | random connected blobs |
|---|---|---|
| **elongation** (length / width) of each connected piece | **11.2–12.4** | median 1.5, 95th percentile ≤ 2.6 |
| **long axis vs the nearest ribbon direction** | **0.0°** for every band | — |
| rhombi held by a single ribbon chain | 36% (median) | 18% |
| rhombi sharing one edge direction | 50% (median) | 44% |

- **The universes differ along thin, straight bands that run exactly along ribbon directions.**
- **The pre-registered prediction failed.** I predicted that ≥ 90% of differing rhombi would share
  one edge direction; it was 50%. Theory says it should fail: worm flips rearrange hexagons made
  of rhombi in *three* directions. I tested the wrong signature.
- **v1 of the test also had a bug.** Edge directions in this tiling point at 18° + 36k, exactly
  between the rounding bins I first used, so families were merged. Fixed; the numbers above are
  from the fixed version.
- **The band-shape test was added after seeing the bands**, so it is exploratory, although its
  margins are large.
- **Only 3 distinct outcomes.** The 30 forced runs produced just three different patches (27, 29
  or 56 differing rhombi), so this is three bands' worth of evidence, not thirty.

## The crossroads test (`crossroads_test.py`, exit 0): Gemini's "intersection crash"

When forced growth has to guess, does the change travel down one road, or down both roads that
cross there? Every guess is recorded, with its position and whether the chosen tile differs from
the self-similar tiling (a *divergent* guess). Each band is matched to the divergent guess
nearest its inner end.

- **Each divergent guess sends its change down exactly ONE road**, never both. This was
  pre-registered and it held. The two-band outcome (0° and 144°) came from two separate guesses,
  at steps 34 and 244.
- **Every band starts right at its guess** (within 2.5 tile-edges): the seam grows *from* the
  moment of choice, outward along one road.
- **Every guess is a genuine fork.** One of its options was always the self-similar tile, so a
  divergent guess chooses a sibling universe; it is not an error.
- **Small numbers.** The 30 runs contain only 4 distinct guess→band events (steps 10, 34, 244,
  248). And since every tile sits where two roads cross, "crossroads" is everywhere; the finding
  is that the change follows *one* of the two roads crossing at the guessed tile.

## Honest scope

- **SCALE is strict in 2-D.** It works only from a patch that is genuinely self-similar about the
  growth centre. Off-centre starts give it nothing to read. That is stricter than 1-D, where
  misaligned starts still grew (with scars or inflating defects).
- **WRONG-SCALE's failure is trivial**: one zoom step lines up no edges at all. A sharper wrong
  zoom control would be worth adding.
- **Sizes.** 500 half-tiles per run and 30 runs per local rule. Forced growth might meet a jam
  beyond 500; the literature says forced growth from ordinary seeds can eventually need guesses
  that go wrong.
- **Numerical tolerance.** Geometry is floating point with a 10⁻⁶ tolerance. Legality is checked
  combinatorially against the learned atlas.

## Reproduce

```bash
python3 laying_the_tiling.py   # ~4.5 min; exit 0 iff all checks pass
python3 make_figure.py         # figures/patches.png
python3 worm_test.py           # ~4.5 min: do the universes differ along ribbons?
python3 crossroads_test.py     # ~5 min: does a guess's change travel down one road or both?
```

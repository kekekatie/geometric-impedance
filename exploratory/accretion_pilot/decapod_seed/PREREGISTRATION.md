# The decapod seed: does a memory-carrying defect give a now with no choices? Pre-registration

*Written and committed **before** any code for this study existed. (Two geometry probes were run
first: the rhombus edge is `SCALE_LEN`, tile edges point in directions ≡ 18° mod 36°, and an empty
patch offers 4 candidates on a unit edge. Nothing about growth was run.)*

*Background: [`../LITERATURE_NOTES_local_growth.md`](../LITERATURE_NOTES_local_growth.md) and
[`../gromit_check/`](../gromit_check/).*

- *Our growth hits genuinely **dead surfaces**: nothing is forced, even for vertex-aware Gromits,
  and there are always exactly 2 options. It must then either wait for the whole world or guess
  locally and jam.*
- *Onoda, Steinhardt, DiVincenzo & Socolar (1988), as summarised: a **decapod** seed (a decagon
  whose surroundings are legal but whose inside **cannot** be filled) never meets a dead surface.
  Growth is forced all the way.*

*A connection to our own jewels: the writing walker's stubborn knot turned out to be a bad decapod
(`../writing_walker/`, D1–D2). And "perfection cannot remember": a perfect tiling has a
single-valued lift, so zero holonomy. A decapod is a place where the lift fails to close. **It
carries holonomy, a memory.** So the question here is: **does a world seeded by a memory need no
choices?***

## Construction

**The decagon.** It has edge length `S = SCALE_LEN` (the rhombus edge), circumradius `φ·S`, centre
at the origin, and vertices at angles `18° + 36°·k`, so its edges run along tile directions. Its
inside is a **forbidden region**: no tile is ever placed there. Frontier edges lying on the decagon
boundary are never grown.

**Enumerating seeds (the decagon's ring).**

- For each of the 10 decagon edges, list the candidates on the **outside** (`Patch.candidates` with
  the decagon centre as the inside point).
- Depth-first, choose one per edge. Keep a choice only if it is legal against those already chosen
  (`Patch.legal`) and **every vertex stays completable** (`../gromit_check/completable`), with the
  interior sector counted as fillable in principle.
- **Up to rotation**, each surviving ring of 10 tiles is one **seed**. Rotations are removed using
  a signature per edge: tile type, plus its third vertex in the edge's own frame. Reflections are
  kept as distinct seeds.

**Fillable or decapod.** For each seed, search exhaustively (depth first) for fillings of the decagon
interior by tiles whose centroids lie inside it. A filling counts if every placement is legal and
every vertex that becomes complete is a legal star.

- **FILLABLE:** at least one legal filling exists.
- **DECAPOD:** none does.

**Growth.** The patient scheduler (as `../continuation_choices` arm FAST: all forced tiles each
round; a random guess at the innermost edge only when nothing is forced anywhere; the decagon
boundary never grown).

- 800 half-tiles beyond the seed.
- 3 runs per seed, with random streams `20261050 + 100·s + k`.
- Recorded: guesses (each one a dead surface), jams, and where they happen.

## Checks and predictions

- **Q0 (asserted).**
  - The enumeration finds at least one FILLABLE seed and at least one DECAPOD seed.
  - Every FILLABLE seed's filling is a legal completion: its complete stars are all among the 8.
- **Q1 (OSDS: a decapod seed needs no choices).** Among DECAPOD seeds, consider those none of whose
  3 runs jam. **At least 80%** of them need **zero guesses** in all 3 runs: 800 tiles laid purely by
  forced moves. *Confidence about 55%. Our forcing is edge-level, and the reference is known only
  from summaries.*
- **Q2 (fillable seeds behave like ordinary seeds).** **Every** FILLABLE seed needs **at least one
  guess** in every run. *Confidence about 70%.*

## Reported without prediction

- The number of seeds of each kind, and how the count compares with Conway's 62 decagon fillings.
- Jam rates per kind. An unfillable ring whose outside also cannot extend would jam: a "false
  decapod".
- For guessing runs: where the guesses happen. Do they lie along lines from the decagon (worms)?
- The rounds needed to reach 800 tiles.

## Limits, stated in advance

- The seed is a single ring of 10 half-tiles, not a large decapod patch. Whether a ring determines
  its exterior is part of what is being tested.
- There are 800 tiles and 3 runs per seed.
- Forcing is edge-level. The gromit check found it equivalent to vertex-level forcing at our dead
  surfaces, but not in general.

## Changes before the first run

1. **A validation check, and a bug fix that it exposed** (before any growth run).
   - *The check (now asserted as Q0b).* A decagon taken from the genuine reference tiling, with its
     ring of 10 outside half-tiles, must be (a) found by the enumeration and (b) fillable.
   - *What failed.* (b) held (1 filling), but (a) failed: the enumeration had found only 89 rings
     (15 up to rotation), all unfillable.
   - *The cause.* `laying_the_tiling.Patch.candidates` keys its output by `canon()`, which ignores
     the A/B/C vertex roles. The two **mirror decorations** of an isosceles half-tile at the same
     place therefore collapse into one, and a legal option can silently disappear.
   - *The fix.* This study uses its own `candidates()`, identical except that it keys by tile type
     plus the ordered vertices (`dkey`), so both decorations are kept. It is used in enumeration,
     filling and growth. After the fix: 1,046 rings, **111 up to rotation**, and the genuine ring is
     enumerated and fillable.
   - *Do earlier studies need re-running?* `dedup_probe.py` (results/dedup_probe.txt) replays ordinary
     patient growth (600 tiles) and compares both versions at every frontier edge:
     - in **2,757** edge checks the old version hid a legal option **0 times**;
     - of 791 "forced" edges, **0** really had two options.

     So in ordinary growth, where tiles have neighbours, the mirror decoration is never legal and
     earlier studies are unaffected. The bug only matters on nearly empty patches, like a ring
     around an empty decagon.
   - Nothing else changes.

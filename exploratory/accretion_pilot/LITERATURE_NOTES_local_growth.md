# Literature notes: can a quasicrystal grow by local rules alone? (2026-09-28)

*These are reading notes written after [`local_deciders/`](local_deciders/) found no sweet spot:
local guessing jams, and patient global guessing grows in slices. **Honesty note:** this session's
network blocks the paper hosts (arXiv, APS, the author's site, PubMed). These notes come from
abstracts and search-engine summaries, **not the full texts**. Claims marked (abstract) are from an
abstract; those marked (summary) are secondary and should be checked against the paper before we
rely on them.*

## 1. Onoda, Steinhardt, DiVincenzo & Socolar (1988): "Growing perfect quasicrystals"

*Phys. Rev. Lett.* 60, 2653. <https://link.aps.org/doi/10.1103/PhysRevLett.60.2653>

- **Main claim (abstract):** "defect-free quasiperiodic tilings can be constructed by use of local
  rules alone." Penrose tiles are added one at a time using local information only.
- **The rule (summary):** tiles are added only at **forced vertices**. At a forced vertex, every
  legal completion of the vertex star agrees on the next tile. This uses a list of legal vertex
  configurations, most of which force further tiles.
- **Dead surfaces (summary):** a growing surface can reach a state with **no forced vertex
  anywhere**. That is a *dead surface*, and the only way on is to guess. A wrong guess means
  defects later.
- **The decapod seed (summary):** start from a **decapod** (a decagon that cannot be filled legally,
  one of the 62 Conway decagon fillings, most of them illegal; see `writing_walker/decapod.py`) and
  growth **never meets a dead surface**. It grows forced all the way, into a tiling that is perfect
  apart from the decapod itself.
- **Where the choices live (summary):**
  - In a decapod tiling, **ten semi-infinite worms** meet at the central decagon.
  - Where the surface lies along an unplaced worm, there are no forced vertices. The worm can go in
    either of **two orientations**.
  - Once the choice is made at one vertex, **all the others are forced**.
  - So the choices live along lines, one binary choice per worm.
  - *[Uncertain: the summaries conflict on whether, with a decapod seed, such worm choices still
    ever arise, or whether the decapod's ten worms settle them.]*
- **What this means for us:** Our Gromits force a tile only when an *edge* has exactly one candidate.
  OSDS force at *vertices*, looking at all legal vertex stars. **Their forcing is likely stronger
  than ours:** it sees more forced moves. Some of our "nothing is forced, so guess" moments may be
  forced for them. This needs checking before we build on it.

## 2. Hann, Socolar & Steinhardt (2016): "Local growth of icosahedral quasicrystalline tilings"

*Phys. Rev. B* 94, 014113. <https://link.aps.org/doi/10.1103/PhysRevB.94.014113> (arXiv 1604.02479)

- **3D** (abstract): an algorithm that relies exclusively on local rules for sequential face-to-face
  addition of tiles.
- "When the algorithm is seeded with a special type of cluster containing a **defect**, growth is
  forced to infinity **with high probability** and the resultant quasicrystal has a vanishing
  density of defects."
- **What this means for us:** the same trick (a special defect seed) works in 3D, which matters for
  a later "real bending" door.

## 3. Jeong (2007): "Growing perfect decagonal quasicrystals by local rules"

*Phys. Rev. Lett.* 98, 135501. <https://link.aps.org/doi/10.1103/PhysRevLett.98.135501>

- **Main idea (summary):** a perfect Penrose layer grows on top of a **decapod layer** by a 3D local
  rule. Layers then stack into a perfect decagonal quasicrystal, with the one point defect left only
  on the bottom surface.

## 4. Fernique & Galanov (2022): "Purely local growth of a quasicrystal"

arXiv 2201.00789.

- **Main claim (abstract):** a theorem on "purely local and deterministic growth" of
  **Golden-Octagonal** tilings (8-fold, not Penrose), "showing, contrary to the popular belief,
  that local growth of aperiodic tilings is possible."
- **Details (summary):**
  - Tiles are added one by one using only local information, with nothing stored between steps.
  - For any finite pattern there is a finite seed and a growth radius that builds it.
- **What this means for us:** a different tiling family, but it shows the "local vs global" wall is
  not absolute. It depends on the tiling and on the rule's **growth radius**, which plays the same
  role as our horizon.

## What I take from this

1. **We hit a known wall.** Growth by forced moves meets *dead surfaces*. Guessing there either
   waits globally (our patient scheduler) or risks defects (our local deciders). OSDS saw the same
   trade-off in 1988.
2. **The known way through is a special seed.** A decapod (in 3D, a special defect cluster) makes
   growth forced all the way, so no decisions are needed and nothing waits for the whole world.
   That would give a **genuinely local now** that never jams. It is the home Katie's worldline
   body needs.
3. **A check comes first:** is our edge-level forcing weaker than OSDS's vertex-level forcing? If
   it is, the proper next step is to add vertex forcing, and then try a decapod seed.
4. **A physics rhyme, speculative:** the world's only freedom (its choices) lives on a few lines
   (worms) that radiate from one special defect. Everything else follows by necessity.

## Suggested next study (not yet pre-registered)

- **A. Forcing strength.** On our existing growths, count how often an edge-level "nothing forced"
  moment is actually vertex-forced.
- **B. The decapod seed.** Build it from `writing_walker/decapod.py`'s illegal decagon fillings.
  Grow with vertex forcing and no guesses. Predict: no dead surface and no jam, a smooth local
  now, and choices (if any) only along worm lines.

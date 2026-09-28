# The Gromit check: are our "dead surfaces" really dead? Pre-registration

*Written and committed **before** any code for this study existed.*

*The literature notes ([`../LITERATURE_NOTES_local_growth.md`](../LITERATURE_NOTES_local_growth.md))
suggest that Onoda, Steinhardt, DiVincenzo & Socolar (1988) force tiles using **vertex
configurations**: every legal way of completing the star of tiles around a corner. Our Gromits are
weaker than that. They call a tile forced only when an *edge* has exactly one legal candidate. Their
legality check (`vertex_ok`) confirms that each unbroken run of corners around a vertex is **part
of some** legal star. It never checks whether **all the runs, with the gaps between them, fit one
legal star together.** So some of our "nothing is forced, so we must guess" moments may be forced
for a vertex-aware Gromit. A few of our guesses may even have been doomed: legal by our check, but
impossible to complete.*

## Definitions

- **Completable vertex.**
  - Take the corners present at a vertex (start angle, width, label).
  - The vertex is completable if some complete legal star in `L.STARS` (the 8 Penrose vertex types)
    can be laid around it with every present corner exactly in place.
  - In practice: pick a present corner. For each star `S` and each position `i` where `S` has that
    corner's label, walk once round `S` from that corner, adding up the widths. Every present corner
    must start exactly where the walk puts a corner with its label, and no present corner may start
    inside a filler corner.
- **Strong candidates** at a frontier edge: the edge-legal candidates (from `Patch.candidates`) that
  leave all three of their vertices completable once placed.
- **Strong-forced edge:** exactly one strong candidate. **Strong-dead edge:** no strong candidate.

## Data

- **Patient growth.** Exactly the `h = ∞` (patient scheduler) histories of
  [`../local_deciders/`](../local_deciders/): seeds `20261040 + k`, k = 0 … 7, and 1,500 half-tiles.
  They are regrown deterministically.
  - At every **guess moment** (a round where our Gromits find nothing forced), each frontier edge's
    strong candidates are computed, along with whether the tile actually guessed is strong.
- **Local-decider jams.** The `h ∈ {0.5, 1, 2}` runs of `../local_deciders/` (all jammed), regrown
  identically. For every guess, record whether the chosen tile was strong.

## Checks and predictions

- **Z1 (asserted).** Every vertex of the seed patch is completable. It is a piece of a genuine
  Penrose tiling.
- **Z2 (asserted).** Every *complete* vertex star in every final patient-growth patch is one of the 8
  legal stars.
- **F1 (our dead surfaces are mostly not dead).** Pooled over all guess moments in the 8 patient
  histories, in **at least 50%** of them some frontier edge is strong-forced. A vertex-aware Gromit
  would not have needed to guess. *Confidence about 55%.*
- **F2 (the jams were doomed guesses).** In **at least 20 of the 24** jammed local-decider runs, at
  least one guess made before the jam was **not strong**: it left a vertex that could no longer be
  completed. *Confidence about 60%.*

## Reported without prediction

- In patient growth: the fraction of guesses that were not strong. Patient growth never jammed, so
  the prediction is that there are none, but this is only reported.
- Whether any guess moment had a strong-dead edge: a hidden contradiction already in the patch.
- The number of strong candidates at the guessed edge.

## Limits, stated in advance

- Strong forcing is a one-tile, vertex-level check. It does not see longer chains of implication, so
  "strong" is still weaker than "consistent with some complete tiling".
- There are only 8 patient histories, several of them duplicates (few binary guesses).

## Changes before the first run

*(none yet)*

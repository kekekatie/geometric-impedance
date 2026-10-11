# Can the tiling tell who made it?

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). One clarification was made before the run (Part 2's random
streams). The first run crashed while **saving** (a numpy value the save format couldn't handle). It
was rerun with identical seeds and code, apart from the save fix.*

**Astra's question:** is a world **made** or **discovered**?

- **SELECT** worlds (*made*): a fair coin at every choice. This is how all our earlier worlds grew.
- **REVEAL** worlds (*discovered*): a hidden position is drawn first, uniformly from the seed's wiggle
  room. Every choice then takes the option consistent with it.

**The set-up.** Part 1 grew 48 seeds in both ways (96 worlds). Part 2 grew one seed 40 times each way
(80 worlds).

## Scorecard

| | prediction | result | |
|---|---|---|---|
| W1 | dead ends belong to makers: no REVEAL world takes a dead option or jams | **0 / 48** (REVEAL met 9 dead options and never took one). SELECT: took 3 of 7, and all 3 jammed | ✅ HELD |
| W2 | one world can't tell: no vertex-type frequency differs between modes (p < 0.01/8) | smallest p = **0.07**; effects 0.06–0.37 SD | ✅ HELD |
| W3 | a crowd can tell: share of worlds in the smaller first-choice piece matches its model | SELECT **25/40 = 0.63** (expected 0.5; within interval); REVEAL **15/40 = 0.38** (expected 0.38) | ✅ HELD |

**Reported** (recount, [`results/smaller_piece_recount.txt`](results/smaller_piece_recount.txt); the run
log's "0/123" was a reporting bug with numpy booleans):

- SELECT took the smaller live piece **48–56%** of the time, like a fair coin.
- REVEAL took it **27–29%** of the time, near the share-weighted expectation of 32%.
- REVEAL worlds met **more choices** in the same tile budget (163 vs 123). This is partly because 3
  SELECT worlds jammed early; it is not yet explained.

## What it means (plainly)

- **From inside one world, you can't tell whether it was made or discovered.** Both kinds are genuine
  Penrose patches with the same local statistics.
- **Except at a dead end.** A *maker* can blunder into a locally legal choice that no hidden number
  allows, and that world later jams. A *discovered* world never can, because its hidden number was
  always there to keep it consistent.
- **A crowd of worlds can tell.** Across many worlds, makers land in small and large pieces equally
  often. Discoverers land in them in proportion to their size.
- **For Katie's theory:** a single universe could not prove from the inside whether it is being made or
  being discovered. You would need to compare many universes, or catch one at a dead end.

## Limits

- Vertex-type frequencies are one family of single-world statistics. Subtler signatures (for example,
  the size of the wiggle room a finished world still has) were not tested and could carry a weak,
  probabilistic hint.
- 1,500 half-tiles per world. One tiling family.
- W3 holds largely by construction. It demonstrates that the finished tilings, read alone, carry the
  crowd-level signature.

## Files

- `who_made_it.py`: the study
- `results/who_made_it_report.txt`, `results/run.log`, `results/worlds.json`
- `results/smaller_piece_recount.txt`

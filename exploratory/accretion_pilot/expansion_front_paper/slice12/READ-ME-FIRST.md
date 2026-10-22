# Watch the slice-12 choice

Open **WATCH-SLICE12.html** in a browser. Press Play, or drag the slider to inspect each slice. It works offline and can be moved on its own. **slice12-film.gif** is the looping version.

Both panels start with exactly the same construction through slice 11, including the same original choice B. At slice 12, they take the two different legal alternatives at the same site. Watch the dark outlined tile and the new construction that follows it.

## What the colours mean

- Grey: already built before slice 12.
- Green: identical new tiles in both continuations at this slice.
- Solid blue/orange: different tiles in places covered by both continuations, using the original centroid-coverage comparison.
- Hatching: unequal coverage; the other continuation has not covered the compared tile's centroid.
- Dark outline: the slice-12 choice tile.
- Dashed outlines: the earlier A-versus-B difference on the B side, frozen at slice 11 (22 half-tiles).

These are comparisons between alternative histories. No tiles are being removed or replaced during construction. A colour does not identify a separate object moving through one world. A slice is a construction step, not a measured physical time.

## What this example establishes

The later choice has its own compatibility cut: about 162 degrees, predicting family 3. The original choice's cut was 18 degrees, predicting family 2. See **two-cuts.png**; its two panels use different coordinate scales.

The later choice tile touches none of the frozen earlier difference tiles. The later differing construction first shares a corner with that region at slice 15, and an edge at slice 16, in both continuations. Contact remains present through the final inspected slice, 20. This is geometric attachment to a historical comparison region; it does not establish two ribbons crossing or a persistent local object.

By slice 20, the two continuations have added 27 and 63 half-tiles since slice 11. Four are shared. The covered differences contain 22 and 23 half-tiles; unequal coverage contains 1 and 36. Keeping these categories separate matters: a larger footprint is different from a different tiling of a covered place.

Family 3 has the largest incidence count in the later covered difference from slice 14 onward. Slice 13 is tied between families 1 and 3; no unique direction is inferred from that tie.

## Checks and limits

Both saved continuations were replayed with the original engine and matched every saved slice from 0 through 20. Their histories are identical through slice 11. Before the later choice there is no forced site, and the selected site has exactly the two alternatives shown. The compatibility constraints after the next forced slice match the directly reconstructed constraints. The original A continuations were also replayed: they are identical to each other and have no later guesses.

This is one previously selected exceptional case, not a new representative sample or a rerun of the entire historical experiment. The dashed region captures observed earlier differences through slice 11, not every possible future consequence of the original choice. Lack of contact with it does not mean lack of constraint by the first choice.

## The next useful test

Follow the neighbourhood of the slice-15/16 contact for longer, tracking individual tiles and connectivity in each history separately. Ask whether a bounded connected motif persists, changes, or simply becomes buried as construction grows. Then compare with matched locations away from the contact and repeat in other cases. This would test the proposed knot more directly than a visually striking overlap alone.

## Reproduction record

Prepared 2026-10-21. Original research baseline: `d4e00c5d4396c38bd69b265907b5f3d6c5bc030a`. Case: `180fb0b920bb845b`, original world 21 / slice 8. B continuations 1 and 3 (one-based), streams `20810350027` and `20810365865`. Existing continuation horizon: 20 slices.

`measurements.json` contains counts, contact measurements, cut areas and the input cache SHA-256. `slice12_film.py` in the parent paper directory reproduces the analysis using `figures.py`, the original engine modules, and `results/geometry.pkl`. The copied script in the viewing package is a record, not a standalone simulator.

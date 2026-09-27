# Happening density: does a quiet place have a wider now?

Pre-registered in [`PREREGISTRATION.md`](PREREGISTRATION.md) before any code existed. Katie asked:
*"If I am a point in distant space, light years from anything, what is my local width of now?"* In
the soft-zone study ([`../soft_zone/`](../soft_zone/)) happening density was only observed. Here it
is **manipulated**: one half of the growing front is throttled, so its Gromits act only a quarter of
the time.

## Scorecard

| | prediction | result |
|---|---|---|
| H0 | manipulation check: slow-half happening density < 0.6 × fast | **pass**, just (0.58: 1.86 against 3.22 tiles per round) |
| H1 | the **spatial** width of the now is the same in both halves | **held**: freedom by distance is 0.40 / 0.10 / 0 (slow) against 0.46 / 0.14 / 0 (fast) |
| H2 | soft holes are ≥ 2× older in the quiet half (a wider now in time) | **failed**: median age 7.6 against 7.5 rounds |

## What it means

- **The spatial width of the now doesn't care how busy a place is.** Quiet or busy, the soft zone
  is about two tile-edges deep. Softness is a matter of geometry: being not yet surrounded.
- **Is the now wider in *time* where it's quiet?** The pre-registered test said no. Soft holes are
  just as young on both sides, because most soft holes sit right at the edge (within one tile),
  where every tile is young. *Exploratory, after the fact:* the **back edge of the soft band** (1–2
  tiles behind the front) is much older in the quiet half, with median age **28.8 rounds against
  10.3**. So the band that makes up the now spans roughly **three times as many rounds** where
  little happens. This was not pre-registered and needs its own test. It does lean towards Katie's
  intuition: *the quiet place's now is not wider in space, but it lasts longer.*
- **A surprise: unequal happening density jams the growth.** 3 of 8 throttled runs jammed early
  (rounds 13–17). Uniform-speed growth never jammed in any earlier study (0 of 42 runs). *Exploratory
  (`results/jam_locations_EXPLORATORY.txt`):* all three jams lie **on the slow side, within about
  2 edges of the line where slow meets fast**, just outside the seed. Where a fast front races
  ahead beside a slow one, the fast side settles first and boxes in the slow side's choices before
  it gets to make them.

  Compare [`../relative_nows/`](../relative_nows/): fronts meeting **at equal pace** always
  reconciled. So reconciliation may need both sides to still be soft *at the same time*.

## Honest limits

- The throttle is imposed from outside, not emergent quietness.
- 3 of the 8 runs jammed early, so they contribute few holes. The hole counts per cell are 17–24.
- The manipulation was weaker than intended: a density ratio of 0.58, not 0.25, because forced
  placements and guesses also flow into the slow half from the fast side's geometry.
- Only three jams, all near the seed. Whether "a fast front beside a slow one jams" holds more
  generally needs its own pre-registered test.

## Reproduce

```bash
python3 happening_density.py            # ~30 s on 4 cores; results/runs.jsonl, results/happening_density_report.txt
python3 happening_density.py --summary
```

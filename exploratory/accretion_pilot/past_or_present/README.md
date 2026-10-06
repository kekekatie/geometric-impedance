# Decided by the past or by the present?

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). The question came from Gemini (2026-10-06): are places
decided sideways, by the active present, rather than by their history?*

**The test.** In 4 intact decapod worlds, every time a tile was forced (8,000 tiles in all) we
rewound its memory. Could it still be worked out from only the tile it attaches to, plus what was
laid nearby in the **last 1 round**? The last 2? 3, 5, 8, or all? The shortest memory that works is
how far back the tile had to "look".

## Scorecard

| | prediction | result | |
|---|---|---|---|
| Z | every forced tile is forced by its full 2.5-edge neighbourhood | 8,000/8,000 | ✅ PASS |
| G1 | the present decides most tiles: median memory ≤ 2 rounds | median **1**: **74%** decided by the last round alone | ✅ HELD |
| G2 | deep places lean more on the past: ρ(depth, memory) > 0 in ≥ 3/4 | ρ = −0.012, +0.003, +0.008, −0.009 (2/4) | ❌ FAILED (no relationship) |

**Memory needed** (pooled): 74% need 1 round, 13% need 2, about 5% need 3, about 4% need 5, about
2% need 8, and about 1% need older than that.

## What it means (plainly)

- **The present does most of the deciding.** Three-quarters of tiles are pinned down by what happened
  in the very last round, plus the tile they attach to. That tile has usually been waiting only
  1.5–1.9 rounds. Gemini's instinct was right in spirit: in this world, **the now mostly decides
  itself**, from fresh neighbours.
- **Depth doesn't change how far back a place must look in time.** That contrasts with
  `../decision_radius/`, where deep places needed a slightly wider ring in *space*. So far, depth
  matters for *how much room* is needed, not *how much history*.
- **A small surprise, exploratory** ([`results/tail_EXPLORATORY.txt`](results/tail_EXPLORATORY.txt)).
  The rare tiles that need a **long memory** (8+ rounds) sit most often at **shallow** depth, near the
  window's edge: 5.8%, against 2.1% for the middle third and 3.3% for the deep third. It rhymes with
  Katie's earlier "memory at the boundary" work. It is a small effect, from a post-hoc look.

## Limits

- Memory is counted in rounds, not in local happenings.
- 4 worlds that share structure.
- The horizons are coarse (1, 2, 3, 5, 8, all).

## Files

- `past_or_present.py`
- `results/worlds.json`
- `results/past_or_present_report.txt`
- `results/tail_EXPLORATORY.txt`

# Where does a decapod keep its memory?

> **Update (2026-10-07, [`../window_cells/`](../window_cells/)):** decapod worlds fit the true Penrose window exactly. Their extra spread comes from 54–60 vertices sitting **on the window's edge** along the ten ribbons. That is reading (c) in the caution below (sampling), not translated windows.

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md).*

**The question.** [`../perp_map/`](../perp_map/) found that a decapod seed **smears** the perp-space
window. Here, each world is split into 20 slices (sectors) by angle around the decagon, and we ask
two things:

- does each slice's hidden-address window sit at a different offset (the decapod's memory, made
  local)?
- are those offsets organised by angle?

Worlds: the same 8 DECAPOD and 4 FILLABLE seeds, grown to 1,500 half-tiles. Toolkit: Katie's paper
(doi:10.5281/zenodo.20695694).

## Scorecard

| | prediction | result | |
|---|---|---|---|
| D1 | every decapod world's sectors are more offset than any ordinary world's | **8/8**: decapod scores 0.23–0.29, ordinary 0.14–0.20 | ✅ HELD |
| D2 | the offsets are organised by angle (adjacent/90° distance ratio < 0.8, and below the ordinary worlds') | decapod median **1.13**, ordinary 1.07 | ❌ FAILED |

Every world grew cleanly: no jams, no lift conflicts, 4 layers each. Decapod worlds made 0 guesses;
ordinary worlds made 2–5.

> **Caution (Astra's review, 2026-10-03):** the measure is a sector's **mean** perp address. A larger
> mean offset could come from (a) a window that is genuinely **translated**, (b) a window of a different
> **shape**, or (c) the sector **sampling** different parts of the distribution. A larger overall window
> (as `../perp_map/` found) could also inflate sector offsets with no organised displacement. The
> result below establishes a difference between the two seed families, not yet a translated-window
> mechanism. "Shifted window" is a hypothesis, not a finding.

## What it means (plainly)

- **The decapod's memory is real and local.** Slices of a decapod world sit in windows shifted
  **about 1.7×** more than slices of an ordinary world do. Ordinary worlds still show some offset;
  that's sampling noise from small slices. The decapod adds a genuine, sector-by-sector shift on
  top. This is where the smeared window from `perp_map` comes from: the whole world isn't blurred,
  its pieces sit in different places.
- **But not in smooth bands.** Neighbouring slices are no more alike than slices a quarter-turn
  apart. At 18° resolution, the shifts don't change smoothly around the circle. Several reasons are
  possible:
  - the worms (the lines where shifts happen) need not run straight out from the centre;
  - one 18° slice can straddle a worm;
  - the noise within a slice hides the pattern.

  The memory is there; *where exactly* it sits isn't resolved yet.

## Next, if wanted

Find the worms directly: trace the lines across which neighbouring vertices' window offsets jump,
instead of using angular slices. That needs a finer, line-following method.

## Files

- `decapod_memory.py`
- `results/worlds.json`
- `results/decapod_memory_report.txt`

# Structure and the local clock in an intact decapod world

> **Not robust (2026-10-06; see [`../robustness_depth_clock/`](../robustness_depth_clock/)).** It replicated in new decapod worlds and in ordinary worlds at the 1-edge disc. But the sign **flips** with disc size (−0.31 at 0.6 edges, +0.35 at 0.9, −0.24 at 2.0), and **within each vertex type** the 1-edge effect vanishes. The headline below is withdrawn as a general law: it is a vertex-geometry effect at one scale.

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md).*

**The question** (question 3 on the map at the top of `../RESUME_HERE.md`): how do **structure** and
**happenings** together make local time? Following Katie's rattle principle, the system was kept
whole. An untouched decapod world grows itself, with no guesses, no throttles and no pre-laid bodies.
For each place (about 700 vertices per world, 8 worlds) we compared:

- **structure:** its hull depth in the hidden window, from Katie's paper,
  doi:10.5281/zenodo.20695694;
- **local time:** how long its neighbourhood takes to settle (be fully laid), in **rounds** (T) and
  in **local happenings** (H, tiles laid within 2 edges meanwhile).

Correlations are taken within 1-edge radius bins, so distance from the centre cannot fake them.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| C1 | structure sets how long the present lasts in rounds: same sign in ≥ 7/8, median \|ρ\| ≥ 0.15 | **8/8 positive**, ρ = 0.21–0.29 (median 0.23); every world p = 0.001 against shuffled depth | ✅ HELD |
| C2 | but the number of happenings needed is the same everywhere: median \|ρ\| < 0.15 | ρ = 0.21–0.28 (median 0.22), every world p = 0.001 | ❌ FAILED |

## What it means (plainly)

- **The present lasts longer deep in the window.** Places sitting deep in the hidden window take
  about **30% longer** to settle than shallow ones (deep third: 7.3–8.1 rounds; shallow third:
  5.4–6.6). That held in all 8 worlds.
- **And deep places need more happening, not just more time.** I predicted a fixed "happening budget"
  everywhere, and that was wrong. Deep places gather about **15% more** local happenings before they
  settle (≈16 against ≈14). Their clocks also tick a little **slower** (2.6–2.7 happenings per round,
  against 2.9–3.0 for shallow places and 3.0–3.2 for the middle third).
- **So structure shapes local time in both ways.** Where a place sits in the hidden window changes
  both how long its present lasts and how much has to happen to complete it.
- **A link to an earlier result.** In `../perp_map/`, the places with **open choices** sat **deeper**
  in the window. Here, in a world with no choices at all, the deep places are the ones whose present
  lasts longest. A tentative reading: **depth is where the present is most open: it holds both the
  freedom and the longest-lasting now.** That is an interpretation, not yet tested.

## Honest limits

- The 8 worlds are not fully independent. All are decapod worlds grown deterministically, and their
  structure near the centre coincides (`../worm_lines/`). "8/8" partly reflects shared structure.
- The correlations are moderate (~0.2–0.3). Depth explains some of the variation, not most of it.
- The pattern is not a straight line. The **middle** third settles fastest and ticks fastest; only the
  deep third clearly stands out.
- The two small layers (−2 and +1) mostly had too few probes per radius bin to compute. Where they
  could be computed (seed 2), ρ_H **flipped sign** (−0.65), so the small windows may behave
  differently.
- Settling and happenings are measured with one disc (1 edge) and one neighbourhood (2 edges).

## Files

- `structure_clock.py`
- `results/worlds.json`
- `results/structure_clock_report.txt`

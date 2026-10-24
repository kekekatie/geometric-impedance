# The malleable chase (Experiment C)

*What actually tips A's malleable moves — the scheduler's stopwatch, or Argon's interior wall?*

Follows Experiment A (found the malleable moves) and B (ruled out outer-hull depth). Separates two
suspects with a forced-only burst and the compatibility-region (F) ruler of the decided-before study.
Question, stages, controls and called shots fixed **before any code** in `PREREGISTRATION.md`.

## What the full study found

24 worlds (20 ok, 4 jammed), **9,985 recurring-fingerprint ties** forced-burst and measured.

- **Method control — the separator is sound.** Rigid fingerprints (A-labelled) forced-burst-settle at
  a mean of **0.994** — the bare board forces them with no guess, almost always. "Catalogue-rigid" and
  "forced-determined" are the same thing. ✅

- **C1 — FAILED, and it's the best kind of failure.** We *pledged* that ≥ 50% of the malleable moves
  would turn out to be "just timing." Only **8/91 = 8.8%** did. **The prediction was wrong, and
  reporting it is the point.** The wobble is *not* mostly a measurement artifact.

- **C2 — HELD, overwhelmingly. The wobble is real.** **83/91 = 91.2%** of malleable moves are
  *genuinely contingent* — even with the scheduler's stopwatch removed, the same local move is forced
  one way in some places and left needing a guess in others. Reality really does have give. 🌊

- **C3 — HELD, spectacularly. The interior ruler is the right ruler.** Settled ties are born at
  wall-nearness `min(pA,pB)/F_area` **= 0.000** (one option already on the verge of vanishing);
  stayed-open ties sit at **0.382** (straddling the wall). Mann–Whitney p ≈ 0, standardized effect
  **1.41** — against Experiment B's outer-hull-depth effect of ~**0.1**. **A ~14× stronger ruler.**
  B's "depth doesn't tip it" wasn't the end of the story; we were holding the wrong ruler, and Argon
  found the right one. 🧱

- **C4 — HELD. The wall tips the genuine survivors.** Within the genuine-(a) core, the occurrences
  that settle under the forced burst sit **on the wall (0.000)**; the ones that stay open **straddle it
  (0.382)**, p ≈ 0. So the interior wall isn't just where settling *happens* — it's what *decides*
  which genuine choices resolve and which wait.

### The takeaway

**A found the wobble; B ruled out the outer ruler; C shows the wobble is real (91% genuine, not timing)
and identifies what governs it: the interior wall — the compatibility region's geometry.** A choice
settles when one option's slice of F shrinks to nothing; whether that happens is written, from the
moment the choice is born, in how near it already sits to that wall. The deciding-corner picture is now
mechanistic end to end: **shallow window edge, inward pull (B2), one corner, on the interior wall (C).**

See `results/malleable_chase_report.txt` and `OPEN-MALLEABLE-CHASE.html`.

## Files

| file | what |
|---|---|
| `PREREGISTRATION.md` | pre-registration (shots fixed before code) |
| `malleable_chase.py` | the study: forced-only burst + F-ruler at every recurring-fingerprint tie, scores C1–C4 + the method control |
| `malleable_chase_present.py` | the true-stiffness and interior-wall figures, the viewer |
| `results/` | report, `summary.json`, per-tie `worlds.json` |
| `true-stiffness.png`, `interior-wall.png` | figures |
| `OPEN-MALLEABLE-CHASE.html` | self-contained viewer |

## Reproduce

```bash
cd exploratory/accretion_pilot/expansion_front_paper/malleable-chase
python3 malleable_chase.py                         # full study (24 worlds; heavy, ~30-45 min on 4 cores)
python3 malleable_chase.py --worlds 2 --nadd 400 --serial   # quick test
python3 malleable_chase.py && python3 malleable_chase_present.py   # study, then figures + viewer
```

## Honest framing

The forced-burst is **localised** (radius 10·S) and **capped at 60 slices**, so a cascade longer or
farther than that is counted as not-forced (conservative toward genuine-(a)). Wall-nearness is the
**compatibility region's** geometry (choice-level), not a literal per-vertex partition depth — that
literal reading of Argon's teal ring is a deeper build, flagged for later. The timing-vs-geometry split
is relative to this one patient scheduler. No claim about physical space or time.

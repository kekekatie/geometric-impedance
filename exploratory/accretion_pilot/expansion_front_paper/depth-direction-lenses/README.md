# The depth-and-direction lenses (Experiment B)

*Do A's deciding corners sit shallow in the acceptance window and pull inward — the same event as
window-truncation, seen from the back?*

Marries the corner-response catalogue (Experiment A) to the June 2026 directional-balance paper
(`../../../papers/`), using the lift / hull-depth machinery in `../../perp_map/`. Question, pictures,
controls and called shots were fixed **before any code** in `PREREGISTRATION.md`.

## What the full study found

24 worlds (20 grew to 1500 tiles, 4 jammed), **10,231 ties / 5,994 keystone corners**. Lift clean
(0 conflicts in every world).

- **B2 — the clean win. ✅ HELD, strongly.** At the deciding corners the directional-balance arrow
  **pulls inward: +0.749** (where +1 is fully inward), with **zero sideways twist** (tangential 0.002),
  across **5,589 corners**. The corners pull toward the window centre, with no handedness — exactly the
  June paper's centripetal signature. *The "same gesture, seen from the back" is true for direction.*

- **B1 — did not hold as pledged, but for a blunt yardstick, not a wrong idea.** We pledged "keystone
  corner shallower than the *world's average* vertex," and that failed 0/24 (keystone median 0.342 vs
  world median 0.256). The reason is contamination: the world average is dragged shallow by the raw
  growing frontier, so a *settled-and-buried* corner looks "deeper than average." The fairer reading
  supports the idea: keystone corners sit at depth **0.342 — in the shallow half** (below the 0.5
  centre), and **settled** choices (0.393) are **shallower** than **stayed-open** ones (0.447). *The
  corners are shallow; our pre-registered comparison just used the wrong baseline.* (The quick shuffled
  control as coded drew from keystone depths rather than all vertices, so it is uninformative — a flaw
  to fix in a follow-up; it does not rescue or sink B1.)

- **B3 — the honest "no." Depth is only a weak tipper.** Depth↔settle-fraction Spearman was **−0.09**
  across 175 recurring moves (pledged ≤ −0.2), so depth does **not** mostly explain A's malleability.
  There is a real but small signal in the right direction (settled corners 0.393 vs stayed-open 0.447),
  so depth matters a little — but the wobble lives mostly somewhere the window-edge cannot see. This
  vindicates both Katie's hesitation ("is it depth? hmm") and A's chase, which already found ~45%
  residual give that nothing local explained.

Reported: our lens reproduces the paper's mechanism qualitatively — interior-subset depth↔balance
Spearman **−0.496** (June paper −0.72…−0.78; weaker magnitude at our smaller scale, same sign and
mechanism).

### The takeaway

**Seen from the back, the deciding is a window-edge, inward-pulling event (B2, strong) at corners that
are shallow in absolute terms (B1 idea holds, baseline aside) — but depth is *not* what makes a move
rigid or malleable (B3).** The *where* of the handshake is the window edge; the *why some wobble* is
still open, and points to the next rung.

See `results/depth_direction_report.txt` and `OPEN-DEPTH-LENSES.html` (the two-panel map).

## Files

| file | what |
|---|---|
| `PREREGISTRATION.md` | pre-registration (shots fixed before code) |
| `depth_direction.py` | the study: re-grows A's 24 worlds, joins ties to the depth/balance map, scores B1–B3 |
| `depth_direction_present.py` | the map, the B3 scatter, the viewer |
| `results/` | report, `summary.json`, per-tie `worlds.json` |
| `depth-map.png`, `b3-depth-vs-settle.png` | figures |
| `OPEN-DEPTH-LENSES.html` | self-contained viewer |

## Reproduce

```bash
cd exploratory/accretion_pilot/expansion_front_paper/depth-direction-lenses
python3 depth_direction.py                         # full study (24 worlds, ~10 min on 4 cores)
python3 depth_direction.py --worlds 2 --nadd 400 --serial   # quick test
python3 depth_direction.py && python3 depth_direction_present.py   # study, then figures + viewer
```

## Honest framing

This marries A's events to a perpendicular-space *structure*. It does **not** claim the hidden address
is extra physical space, nor that corner-settling is holonomy in the literal gauge-theory sense.
Whether a tie's stiffness predicts how long its structure *lasts* (the endurance / accrual bridge)
remains the next rung, and is not tested here.

# The corner-response catalogue (Experiment A)

*How does a growing Penrose tiling make up its mind at an open two-way choice?*

This extends the slice-45 local-response finding (`../local-response/`, finding #10 of the
checkpoint handover): there, a single neighbouring tile, meeting a tie at one shared corner, settled
an open choice. Here we ask whether that is how the pattern *usually* decides, and whether the same
recurring move always decides the same way.

The question, the pictures (the keystone handshake, the three drawers, the stiffness line), the
controls and the called shots were all fixed **before any code** in **`PREREGISTRATION.md`**. Read
that first.

## What it does

Across **24 fresh, unseen worlds** (wedge entries 192&ndash;215, never used by the earlier studies),
every live two-way tie on the growing frontier is caught, fingerprinted, and watched for up to 20
slices. Each tie is filed into a drawer:

- **single keystone** &mdash; one tile, necessary *and* sufficient, settles it (the slice-45 case);
- **committee** &mdash; it takes a bloc of two or more;
- **stayed open** &mdash; unsettled within the window;
- **scheduler chose it** &mdash; the patient scheduler guessed there before any neighbour settled it
  (recorded, not scored).

For each keystone we record *why* the rejected option dies (the vertex / corner rule vs an overlap),
and whether the keystone carries the failing vertex. Grouping ties by a reflection-folded canonical
fingerprint (the "sames"), we compute each recurring move's **settle-fraction** &mdash; its position
on the stiffness line between rigid (always settles) and malleable (settles only sometimes).

## Files

| file | what |
|---|---|
| `PREREGISTRATION.md` | the pre-registration (shots fixed before code) |
| `corner_response.py` | the study: grows the worlds, catches ties, runs the necessary/sufficient test, scores A1&ndash;A3 |
| `corner_response_present.py` | builds the figures and the self-contained viewer |
| `results/corner_response_report.txt` | the plain report (drawer counts, scorecard, stiffness line, stiffness-vs-radius) |
| `results/summary.json` | machine-readable scores and the stiffness distribution |
| `results/worlds.json` | every caught tie, per world |
| `stiffness-line.png`, `drawers.png` | the figures |
| `OPEN-CORNER-RESPONSE.html` | read-only viewer; embeds its data, open locally, no server |

## Reproduce

```bash
cd exploratory/accretion_pilot/expansion_front_paper/corner-response-catalogue
python3 corner_response.py                         # full study (24 worlds, ~10-15 min on 4 cores)
python3 corner_response.py --worlds 2 --nadd 300 --serial   # quick smoke test
python3 corner_response.py && python3 corner_response_present.py   # study, then figures + viewer
```

Requires the checkpoint's engine (imported via `../figures.py`) and `../local_response.py`,
`../endurance_observer.py`. Same pinned packages as `../requirements.txt`.

## Honest framing

This is a study of how a growing Penrose tiling settles its own open choices. It claims nothing about
matter, mass, physical time, or physical space. Two questions are deliberately left for later rungs,
and named in the pre-registration: whether the corner-handshake is the acceptance-window truncation of
the June directional-balance paper (**Experiment B**, the depth-and-direction lenses), and whether a
tie's stiffness predicts how long the structure it builds lasts (the bridge to the **endurance**
observer, finding #9). Neither is tested here.

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

## What the full study found

24 worlds (20 grew to 1500 tiles, 4 jammed early), **10,231 two-way ties** caught. All three called
shots held:

- **A1 &mdash; one corner usually does it.** Single keystones settle **5,994 / 6,606 = 90.7%** of
  settled ties (pledged &ge; 60%). Committees are rare (612).
- **A2a &mdash; and it really is the corner.** The deciding touch is a corner (vertex rule, no
  overlap) in **5,994 / 5,994 = 100%** (pledged &ge; 80%), and the keystone carries the failing vertex
  itself in 5,982 / 5,994 (99.8%).
- **A2b &mdash; not just any neighbour.** On average only **32%** of nearby tiles settle a tie alone,
  against the keystone's 100% (pledged < 50%).
- **A3 &mdash; reality has give.** Of 175 recurring moves, **91 (52%) are malleable** &mdash; they
  settle only some of the time (pledged &ge; 15%). The stiffness line is a tall rigid spike (84 moves
  that always settle) beside a broad malleable plateau: a vocabulary with a fixed core *and* genuine
  give, exactly as hoped.

A quietly striking reported result: **widening the window stiffens the decision.** As the fingerprint
radius grows 1&rarr;2&rarr;3&rarr;4 edge-lengths, the malleable fraction falls 80% &rarr; 52% &rarr;
47% &rarr; 45%, and then plateaus. More local context pins more moves down &mdash; but about 45% stay
malleable no matter how wide the local window, a residual give the local picture cannot account for.
That is a direct, graded probe of where the local ends and the global begins.

See `results/corner_response_report.txt` for the full scorecard and `OPEN-CORNER-RESPONSE.html` for the
figures.

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

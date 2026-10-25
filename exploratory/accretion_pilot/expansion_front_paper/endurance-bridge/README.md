# The endurance bridge (Experiment D, structural version) — a clean null

*Does a decisive birth breed a load-bearing structure? Measured as forced-support reach.*

Question, stages, controls and shots fixed **before any code** in `PREREGISTRATION.md`.

## What the full study found: all three shots missed

24 worlds, 9,985 recurring-fingerprint ties, **6,395 settlements**.

- **D1 — did not hold (and inverted).** We pledged decisive (rigid) settlements would anchor *larger*
  forced cascades. The opposite is true: Spearman(stiffness, reach) = **−0.458**, and **malleable
  settlements anchor ~3× larger reach than rigid ones (median 29 vs 10)**. Rigid snaps are small and
  local; wobbly ones, when they finally resolve, cascade wider.
- **D2 — did not hold.** Reach is **one smooth distribution** (bimodality 0.054, pledged > 0.5). No
  clean rib/hinge split.
- **D3 — did not hold.** Reach correlates with the frontier-advance rate (Spearman **−0.279**, pledged
  |ρ| < 0.2). **The proxy is partly a timing artifact** — exactly the trap we were trying to avoid.

### What D taught us

Forced-support reach is the **wrong proxy** for endurance: it does not separate ribs from hinges, and
it is not timing-clean. The suggestive inversion (wobbly sites cascade wider) is real in the numbers
but **untrustworthy while D3 fails**. This is a legitimate, useful negative result — the kind
pre-registration exists to report honestly rather than dress up.

**The faithful measure is next:** same-class motif renewal in the hollow active-skin growth (Astra's
finding-#9 machinery). Because the active-skin growth is verified identical to the catalogue, it joins
to these birth-states — and it measures persistence directly rather than by proxy. That gets its own
pre-registration (Experiment D-prime).

### Visual bonus — the partition overlay

`partition-overlay.png` recolours B's acceptance-window panel by **vertex type** (local star class).
The window partitions into clear type-regions, and the keystone corners live in the inner regions, not
the outer rim — consistent with Argon's reading that choices occupy specific internal sub-windows.
Drawing the literal de Bruijn partition *lines* (to show the corners sitting exactly on them) is a
deeper build, flagged for later.

## Files

| file | what |
|---|---|
| `PREREGISTRATION.md` | pre-registration (shots fixed before code) |
| `endurance_bridge.py` | the study: forced-support reach per settlement, scores D1–D3 |
| `endurance_bridge_present.py` | the reach-null figure, the partition overlay, the viewer |
| `results/` | report, `summary.json`, per-tie `worlds.json` |
| `reach-null.png`, `partition-overlay.png` | figures |
| `OPEN-ENDURANCE-BRIDGE.html` | self-contained viewer |

## Reproduce

```bash
cd exploratory/accretion_pilot/expansion_front_paper/endurance-bridge
python3 endurance_bridge.py && python3 endurance_bridge_present.py
```

## Honest framing

A pre-registered null. Forced-support reach is a structural proxy that failed its own timing control;
no rib/hinge split was found. The direct active-skin renewal measure is the next step. No claim about
physical space or time.

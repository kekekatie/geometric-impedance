# Mechanism walkthrough — "where the future forks"

**An interactive visual aid, not a new result.** Isolated; earlier work preserved; the paper is
not touched. Built at Astra's suggestion so the mechanism can be *walked around* before deciding
what the paper should say — "things doing thing things": which local events are possible, how they
reshape the active layer, and why a historical difference persists (durable) or vanishes (washout).

Published artifact (private): https://claude.ai/artifact/K5reNkePDS44BgatMaRbS9

## What it shows

Two matched pairs (same active shape, different archive), both depth-3, chosen so the only
qualitative difference is the number of reachable sinks:

- **washout** = classes (22,25): `L = 0`, **one** reachable sink — the difference is expressed then
  drains away;
- **durable** = classes (0,1): `L = 7/50`, **two** reachable sinks — the difference freezes in as a
  permanent split.

The page lets you: see the two starting states (active green / quiet clay); step through the legal
BUD/CONTACT events to the erasure horizon `H = 2`; delete the archive and explore the **coast**
(BUD-only) transition graph over 4-vertex active shapes, with exact transition probabilities,
sinks, and click-to-see-the-underlying-events; and watch the exact per-step distributions divide
between sinks, with the gap `TV(i,j)` decaying to the exact limit `L`.

The one-line reading it is built to make visible: **durability is a property of the future, not the
past — the past can only leave a lasting mark where the coast forks.**

## Trust / provenance

Every state, event, probability, sink and distribution is computed by [`build_data.py`](build_data.py)
from the verified BUD/CONTACT implementation (`../endogenous_present_width/`,
`../endogenous_pair_robustness/`) and **cross-checked against `pair_robustness.coast_limit`**
(the script asserts and exits nonzero on any mismatch). No numbers are hand-typed. The page embeds
that validated JSON.

## Scope (carried from the studies)

Toy model; exact rationals; the fork rule is verified on the enumerated depth-2 and depth-3 sets,
not proven in general; "two destinations" is not choice or anticipation; no perpendicular-space
coupling and no physical-world mechanism is claimed.

## Files / reproduce

- [`build_data.py`](build_data.py) — computes + validates the exact data → `walkthrough_data.json`.
- `walkthrough.template.html` — the page (data injected at `__DATA__`).
- `walkthrough.html` — the assembled, published page.

```bash
python3 build_data.py          # exact; exit 0 iff all data checks pass
python3 - <<'PY'               # assemble the page
tpl=open("walkthrough.template.html").read(); d=open("walkthrough_data.json").read()
open("walkthrough.html","w").write(tpl.replace("__DATA__",d.replace("</","<\\/")))
PY
```

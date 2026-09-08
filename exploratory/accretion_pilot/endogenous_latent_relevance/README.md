# Latent relevance — a later local change makes a dormant trace matter (bounded)

**One minimal extension of M1 + tiny exact enumeration. No sweeps, no production run.**
Previous models/results preserved. Stops after this bounded demonstration.

## Idea

Earlier we proved M1's active front is a **closed system** — the quiet archive is
**causally inert** (write-only). Here we test Katie & Astra's target: *subsequent changes
can make latent relationships matter again.*

## The added rule (a modelling assumption, not emergent)

**CONTACT (R_bridge, chosen over a rejected reactivation rule):** a controlled, one-shot,
synchronous local intervention — for every active `a`, quiet neighbour `q`, active neighbour
`b≠a` of `q`, **add the active bond `a–b`**. It promotes a latent `a–0–b` link to a live
`1–1` bond, **read-only on the archive** (no `Q` label or `Q`-edge changed, no new
vertices; only `A–A` edges among existing actives). Fully local: no creation IDs, history
labels, or coordinates. Timing is imposed → *controlled intervention*, not spontaneous.

## Result (exact; `active_latent_checks.py`, exit 0)

Reachable matched pair (depth-2 of `path(4)`, k=1) — full classes 0 & 1: isomorphic active
projections, different archives ({3,3} vs {2,3}), matching counts (6,7,4,2).

| stage | state 0 | state 1 | same? |
|---|---|---|---|
| before (M1) | {c0: 1} | {c0: 1} | **identical** — archive inert |
| after CONTACT | {0:⅓,1:⅓,2:⅓} | {0:¼,1:⅛,2:¼,3:⅛,4:¼} | **different** — trace made relevant |

The same read-only CONTACT promotes *different* latent links (archives differ) → state 0's
front becomes a **path**, state 1's a **triangle+pendant** → divergent futures.

**Controls (all asserted):** original M1 no-contact → identical; coupling-disabled
(archive-blind leaf intervention) → identical; vertex relabelling → unchanged; and the
**archive is unchanged** by CONTACT (trace consulted, not transcribed — no new vertices,
only A–A edges added).

See [`LATENT_RELEVANCE.md`](LATENT_RELEVANCE.md) for the rule, the transition table, the
scope limits, and the verdict; [`figures/latent_relevance.png`](figures/latent_relevance.png)
for the diagram.

## Scope

Establishes **conditional causal relevance of a retained trace under an explicit added
rule** — not recovery of full history, not permanent preservation, not consciousness, not
cosmology. The coupling is our assumption; M1 alone provably does not do this.

## Reproduce

```bash
python3 active_latent_checks.py
python3 make_figure.py
```

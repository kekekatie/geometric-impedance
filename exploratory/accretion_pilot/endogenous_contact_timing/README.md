# CONTACT timing — delayed consultation vs newly enabled relevance

**Proof + one tiny exact timing enumeration. No model change, no sweep.** Rules unchanged
(BUD at k=1 ∪ local CONTACT, uniform over the union). Previous results preserved.

## Result

For a quiet vertex `q`, its CONTACT menu `C_q(G)` = unordered pairs of active neighbours of
`q` with no direct edge. **Theorem:** for any single event `G→G'` and any already-quiet `q`,
`C_q(G') ⊆ C_q(G)` — **menus only shrink.** (Proof: a quiet vertex's incidence is frozen, so
its active-neighbour set only shrinks; edges are only ever added, so absent pairs only
vanish. Verified: 2458 checks over 924 transitions.)

**Consequences:** an old trace can't gain a new eligible pair; empty stays empty;
consultation can happen after waiting but the eligibility was already present; new menus come
only from *freshly deposited* quiet vertices (new archive), not from re-enabling an old one.

**Exact timing** (next 3 events, matched pair; categories partition probability 1):

| state | h | consulted | waiting | gone |
|---|---|---|---|---|
| 0 | 1/2/3 | 1/5, 7/25, 39/125 | 2/5, 4/25, 8/125 | 2/5, 14/25, 78/125 |
| 1 | 1/2/3 | 1/3, 41/90, 1357/2700 | 1/2, 13/60, 161/1800 | 1/6, 59/180, 2203/5400 |

`consulted` = a CONTACT via an initially-quiet vertex has fired; `waiting` = none yet but an
initial opportunity remains; `gone` = none, all initial opportunities lost. See
[`TIMING.md`](TIMING.md) for the proof, removal-mode analysis, verdict, and scope; the
figure is `results/timing_partition.png`.

## Which dormancy the model supports

**Delayed consultation of an already-eligible opportunity** — yes. **Newly enabled
relevance of an existing trace** — no (impossible for a fixed `q`; new eligibility only ever
comes from fresh depositions). The theorem holds for all events; the probabilities are a
3-event observation only — no asymptotic claims. Stops before any new coupling.

## Reproduce

```bash
python3 contact_timing_checks.py
python3 make_figure.py
```

# Autonomous local CONTACT — corrections + bounded async test

**Corrections + one bounded exact test. No sweeps, no production run.** Previous results
preserved; a dated clarification is appended to `../endogenous_latent_relevance/`. Stops
after the bounded test.

## Corrections (verified, `local_contact_checks.py`)

- **C1** compare exact **rational distributions**, not multiplicity dicts (fixture:
  proportional multiplicities `{0:2,1:2}` ≡ `{0:3,1:3}` as distributions).
- **C2** CONTACT additions are **actual new edges** (already-present A–A excluded).
- **C3** exact preservation of Q labels + Q-incident edges under the **identity**
  correspondence (not merely isomorphic).
- **C4** the leaf-adding comparison is an **archive-blind alternative intervention**, not a
  coupling-off ablation; the true coupling-off is **BUD-only M1**.
- **C5** the archive is unchanged; its **relationships are re-expressed as active edges**.
- **C6** distinguish **local** event dependence from an externally-timed **global sweep**.

## The autonomous rule (a modelling assumption)

BUD at k=1, plus a **local** event **CONTACT(a,q,b)**: distinct active `a,b` share quiet
`q` and edge `a–b` is absent → add `a–b`. Pair unordered; **distinct mediators = distinct
events**. One step = **uniform over `{BUD} ∪ {CONTACT}`** (weighting is the assumption).
**No global sweep, no external clock** — selection follows the fixed rules.

## Result (exact rationals; exit 0)

Reachable matched pair (classes 0 & 1; iso active projection, archives {3,3} vs {2,3}):

| rule | state | 1 event | 2 events |
|---|---|---|---|
| BUD-only | 0 & 1 | `{c0:1}` | `{c0:1}` — **identical** (archive inert) |
| extended | 0 | `{c0:4/5, c1:1/5}` | `{c0:59/75, c1:11/75, c2:1/15}` |
| extended | 1 | `{c0:2/3, c1:1/3}` | `{c0:403/630, c1:137/630, c2:2/21, c3:1/21}` |

Under the extended rule set the two archives yield **different** projected active successor
distributions at both 1 and 2 events — archive-dependent active evolution under a local
coupling and a fixed scheduler. All controls/invariants asserted (legal events, invariants,
archive preservation, relabelling invariance).

See [`LOCAL_CONTACT.md`](LOCAL_CONTACT.md) for the rule, tables, and scope;
[`figures/local_contact_event.png`](figures/local_contact_event.png) for the diagram.

## Scope

A difference under an **explicit designed-in local coupling** — not spontaneous memory, not
physical time, not permanent recoverability. The trace is latent under BUD-only but
**already eligible** wherever CONTACT's motif exists in the extended model; this is **not**
yet a trace that stays ineligible long then reactivates later.

## Reproduce

```bash
python3 local_contact_checks.py
python3 make_figure.py
```

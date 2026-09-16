# The ERASE test — does the past survive deletion of the archive?

**Exact enumeration, one matched pair, a mechanism test.** Isolated; prior studies preserved.
Proposed by Fable: evolve the matched pair under BUD + CONTACT, then **delete the entire quiet
archive**, and test whether the two lineages still differ in their **archive-free future active
law**.

> **Ensemble, not record.** "The two lineages still differ" is a statement about the
> **distribution over presents**, never a single world: after any horizon a given active graph
> is a class **both** lineages produce; only the probability distribution differs. The "durable
> mark" below is a **bias in the ensemble** (the status of AUC in Study A), never a per-world
> memory. *The present does not remember; the present is biased.*

## Question

`../endogenous_local_contact/` showed the archive can **influence** the active layer *while it
is present*. Does that influence **survive deletion of the archive** — is it baked into the
active "slice of now" — and is the archive then **redundant**?

## Answer (exact; [`ERASE.md`](ERASE.md))

On the matched pair (isomorphic active projections, different archives `(3,3)` vs `(2,3)`),
with `H=2` events before erasing and `K=2` archive-free future events after:

| | result |
|---|---|
| **NULL** (BUD-only throughout) | lineages **identical** at every step — the archive is inert, erasure reveals nothing |
| **Q1 — durable mark** (extended, **ERASE** at H, BUD-only future) | the two lineages' present-ensembles **still differ at the final step** with **no archive present** — CONTACT edges bias the distribution over active slices, and that bias **survives deletion** |
| **Q2 — redundancy** (ERASE vs KEEP) | deleting the archive **changes** the active future (`ERASE ≠ KEEP` after H) — the archive is **not redundant**; a kept archive keeps feeding the active layer |

So **both** are true: the past leaves a **durable mark** on the *distribution over* active
presents (an ensemble bias, not a per-world memory) (Fable's
intuition holds), **and** the archive is **not** redundant (the stronger "redundant" phrasing
needs tempering) — the influence is partly *baked in* and partly *still live*.

All distributions are exact rationals summing to 1, invariant under nontrivial relabelling.
The NULL control is exactly identical, so every difference is attributable to CONTACT alone.
`erase_test.py`, exit 0.

## Scope

One matched pair, small horizon, a **designed** CONTACT coupling, uniform-over-events
scheduler. Shows these effects **can and do** occur — not that they are typical, and not that
the active slice preserves *all* archived information (only that the lineages remain
distinguishable, and that the archive still carries more).

## Reproduce

```bash
python3 erase_test.py
python3 make_figure.py
```

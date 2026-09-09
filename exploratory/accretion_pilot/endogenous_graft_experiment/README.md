# Bounded GRAFT experiment — does a renewed quiet trace get consulted?

**Exact enumeration, one frozen seed, a mechanism test.** Isolated; prior studies preserved.
This is the single experiment the renewed-contact design proposed, run under Astra's frozen
specification. We stop after it (no weighting sweep, no extra seeds, no automatic extension).

## Question

The timing study proved a quiet vertex's CONTACT menu is **monotone non-increasing** under
BUD + CONTACT — an old trace can be *delayed-consulted* but never *newly* made relevant. The
design proposed **GRAFT** (append-only: a new active tip grafts onto an old quiet trace via a
bounded radius-2 wedge, adding one `Q–A` edge) as the one way to break that monotonicity while
preserving the record. **Does renewal then actually occur in reachable dynamics — and is the
renewed opportunity actually consulted?**

## Answer (exact; [`GRAFT_EXPERIMENT.md`](GRAFT_EXPERIMENT.md))

On a frozen seed with a designated quiet trace `q` whose menu starts **empty**, comparing the
**extended** rule set (BUD + CONTACT + GRAFT) against the **control** (BUD + CONTACT), with one
step = uniform choice among **individual** eligible events:

| by step 4 | control | extended |
|---|---|---|
| `q` gains a never-before CONTACT pair (**O1**, newly-enabled relevance) | **0** | **27.19%** |
| that renewed pair is **consulted** through `q` (**O2**, renew-then-consult) | **0** | **7.51%** |
| `q` merely gains a new neighbour (**O0**, kept distinct from O1) | **0** | **47.23%** |

- **Control is exactly 0 at every horizon** — the menu-monotonicity theorem, reconfirmed: no
  GRAFT ⇒ an empty menu stays empty forever.
- **With GRAFT, renewal occurs and is consulted** — both O1 and O2 are positive and grow with
  the horizon. O0 > O1 shows "new neighbour" and "new pair" are genuinely different events.
- Witnessing path `BUD(0,2); GRAFT(1,0,4); CONTACT({3,4},1)` has exact probability `1/180`.

All quantities are exact rationals from a full path-tree enumeration (no merging, so the
designated `q` and its eligibility history are preserved). GRAFT is verified append-only (all
labels/vertices/edges kept, one previously-absent `Q–A` edge added — a **subgraph**, not
induced-subgraph, embedding); CONTACT preserves `Q` labels and `Q`-incident edges exactly;
normalisation and nontrivial relabelling invariance hold. `graft_experiment.py`, exit 0.

## Scope

A **mechanism test** on one deliberately chosen seed — it shows renewal + consultation **can
and do** happen under a **designed** coupling, **not** that they are typical or inevitable.
Equal event counts across the two rule sets are not matched physical time. GRAFT forfeits the
closed-active-front result of `../endogenous_active_projection/` by design; renewal is possible
only at the live/archive interface.

## Reproduce

```bash
python3 graft_experiment.py
python3 make_figure.py
```

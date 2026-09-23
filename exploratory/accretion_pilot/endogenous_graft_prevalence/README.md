# GRAFT prevalence — does renewal generalise beyond one seed?

**Exact enumeration over every depth-2 seed and quiet trace.** Isolated; prior studies
preserved. Transmission-paper data (Fable's request): run the GRAFT test on all reachable
depth-2 seeds, same horizons as the original.

## Question

The GRAFT experiment showed renewal on **one** hand-built seed. Across the whole depth-2 seed
set (11 classes × 2 quiet traces = **22 cases**), how prevalent is it?

## Answer ([`GRAFT_PREVALENCE.md`](GRAFT_PREVALENCE.md))

Extended (BUD+CONTACT+GRAFT) vs control (BUD+CONTACT), scheduler uniform over individual events,
outcomes O0/O1/O2 about a designated quiet trace, horizons 0–4:

- **Control ≡ 0 across all 22 traces** — renewal (a quiet trace gaining a never-before CONTACT
  pair) is impossible without GRAFT, *universally*. The menu-monotonicity theorem holds over the
  whole seed set, not one seed.
- **With GRAFT: renewal in 20/22 traces (91%)**, consultation in 20/22; mean renewal probability
  ≈ **0.222** by step 4, mean consultation ≈ **0.049**. Both empty-menu (10/12) and non-empty-menu
  (10/10) traces renew.
- **Structural exception:** class 2's two traces never renew even with GRAFT — no bounded GRAFT
  wedge is ever reachable there (renewal happens only at the live/archive interface). Prevalence
  is high but not universal, and the exception is exact.
- `O2 ≤ O1 ≤ O0` on every trace (consult ≤ renew ≤ new-neighbour).

So renewal was not an artefact of one hand-picked seed: without GRAFT it is impossible
everywhere, and with GRAFT it usually occurs and is usually consulted.

## Scope

The depth-2 class set, one scheduler, the designed GRAFT coupling, horizon 4 — a
mechanism/prevalence study, not a frequency estimate over generic worlds. `20/22` is prevalence
within this exact enumerated set.

## Reproduce

```bash
python3 graft_prevalence.py
python3 make_figure.py
```

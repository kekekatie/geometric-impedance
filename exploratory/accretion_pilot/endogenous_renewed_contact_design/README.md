# Renewed contact — bounded design comparison (no experiment)

**Design comparison + tiny legality fixture. No production simulation.** Previous work
preserved. Stops before the proposed test.

## Question

Can newly formed active structure acquire a *local* relationship with an existing quiet
trace, enabling a previously unavailable CONTACT, while preserving a precise record?

The CONTACT-menu monotonicity theorem (`../endogenous_contact_timing/`) rests on two
assumptions; breaking one is the only way to renew a trace. The three options are exactly:

| option | assumption broken | preserves | rewrites | verdict |
|---|---|---|---|---|
| **1. add an active neighbour to an old quiet vertex** | quiet incidence frozen | all labels + all edges (append-only) | archive *definition* (a new incidence) — but nothing deleted | **recommended** |
| 2. reactivate a quiet neighbour (Q→A) | label monotonicity | edges | **a quiet label (erases the record)** | rejected |
| 3. remove an A–A connection | edges add-only | labels, Q-edges | **deletes an active bond** | rejected |

## Recommended rule — GRAFT (local option 1)

**GRAFT(q,a,w):** motif `q:Q, a:A, w:A` with `q–a`, `a–w` present and `q–w` **absent** (a
bounded radius-2 wedge); effect: add `q–w`. New active structure `w` grafts onto the trace
`q` because it was already 2 hops away through a live bridge `a`. Local (no distant reach),
no IDs/ages/labels/coords/sweep; joins the scheduler as uniform events over
`{BUD} ∪ {CONTACT} ∪ {GRAFT}` (weighting = a modelling assumption).

**"Record preserved" = append-only archive** (the earlier "archive unchanged" is honestly
relaxed): no quiet label changed, no edge deleted; the only change is *adding* an edge
incident to a quiet vertex, so the old archive embeds in the new one.

**Verified fixture** (`legality_fixture.py`, exit 0): a triangle-apex quiet `q` with
`C_q = ∅` gains a new opportunity `C_q = {{z,w}}` after `GRAFT(q,x,w)` — menu monotonicity
broken, archive append-only, and the new pair was **not** already present (so this is
*newly enabled relevance*, not delayed consultation).

See [`RENEWED_CONTACT_DESIGN.md`](RENEWED_CONTACT_DESIGN.md) for the full comparison, the
record definition, what distinguishes GRAFT from reading, costs/limitations, and the
concrete bounded test; [`figures/graft_before_after.png`](figures/graft_before_after.png)
for the diagram.

## Costs (headline)

The active front stops being a closed system (by design); the archive becomes append-only
but *living* (not a frozen fossil); only **frontier** traces (with a live neighbour) can be
renewed — deeply buried traces stay dormant forever. Still a designed-in coupling, not
emergent. Mechanism *constructed*, not shown to *tend to occur*.

## Reproduce

```bash
python3 legality_fixture.py
python3 make_figure.py
```

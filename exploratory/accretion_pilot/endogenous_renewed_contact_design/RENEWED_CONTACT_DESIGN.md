# Renewed contact — a bounded design comparison (no experiment)

*Register: speculative exploration; **a design comparison + a tiny legality fixture**, not a
production experiment. Isolated under
`exploratory/accretion_pilot/endogenous_renewed_contact_design/`; previous work preserved.
No merges, publishing, sealed-study access, or production simulations. The legality fixture
(`legality_fixture.py`) checks rule **legality** only — it does not search for favourable
outcomes. We **stop before** the proposed bounded test.*

## Question

Can **newly formed active structure** acquire a *local* relationship with an **existing
quiet trace**, making a previously unavailable CONTACT possible — while preserving a
precisely defined record?

Background: `../endogenous_contact_timing/` proved that a quiet vertex's CONTACT menu
`C_q(G)` is **monotone non-increasing** under the current rules (BUD, CONTACT). That proof
rested on two assumptions:

- **(A1)** a quiet vertex's incidence is frozen ⇒ its active-neighbour set only shrinks
  (labels go `A→Q` only; no edge is added at a quiet vertex);
- **(A2)** edges are only ever added ⇒ an absent `A–A` pair among `q`'s neighbours only ever
  becomes present.

To grow `C_q` (renew a trace), a rule must break (A1) or (A2). The three options below are
exactly the three ways to do that.

## Comparison of the three ways to break monotonicity

| | **Option 1 — add an active neighbour to an old quiet vertex** | **Option 2 — reactivate a quiet neighbour (`Q→A`)** | **Option 3 — remove an `A–A` connection** |
|---|---|---|---|
| **Theorem assumption broken** | (A1), the *frozen-incidence* half: a quiet vertex gains a new incident edge (to an active vertex). | (A1), the *label-monotonicity* half: `Q→A` becomes possible. | (A2): edges are no longer add-only. |
| **What is preserved** | All labels; **all** existing edges; all vertices. Archive grows only by **addition**. | All edges; all vertices. | All labels; all vertices; all `Q`-incident edges (if only `A–A` edges are removed). |
| **What is rewritten** | The **archive definition** for `q`: it now has an incidence it lacked. *Nothing is deleted or overwritten* — but "archive unchanged" is **no longer true** (honestly relaxed to append-only, below). | A **quiet label is overwritten** (`r: Q→A`). The fact "`r` was quiet" is **erased** — the record is *rewritten*, not preserved. | An **active bond is deleted** — the active structure a prior event built is undone; dynamics become non-monotone/reversible in edges. |
| **Motivation beyond "get reactivation"** | Models *new structure forming a local relationship with an old trace* — genuinely new relevance at the live/archive interface, append-only. Fits the stated question directly. | Little beyond forcing reactivation; it is the bluntest option and destroys the record it claims to revive (the concern that rejected `REACT` in `../endogenous_latent_relevance/`). | Little beyond forcing reactivation; it renews by **erasing** a connection rather than by new structure meeting old — against the model's since-v1 "nothing is ever weakened or deleted" character. |
| **Verdict** | **Recommended** (made local + interpretable below). | Rejected: rewrites the record. | Rejected: erases structure; renewal-by-undo. |

Only **Option 1** both (a) preserves every prior label and edge (append-only — nothing
deleted or overwritten) and (b) realises the actual phenomenon asked for: *new* active
structure acquiring a relationship with an existing trace. Options 2 and 3 obtain
reactivation by destroying something (a label; an edge).

## Recommended rule — GRAFT (option 1, made local)

The naive option-1 rule ("connect a new active vertex to *some* quiet vertex") is
**rejected as non-local** — it would reach to an arbitrary distant archived vertex. The fix
is a **bounded local motif**:

> **GRAFT(q, a, w).**
> **Motif (bounded, radius 2 from `q`):** `q:Q`, `a:A`, `w:A`, with edges `q–a` and `a–w`
> present and edge `q–w` **absent** — a wedge `w–a–q` whose tip `w` sits two hops from the
> trace `q` through a live bridge `a`.
> **Effect:** add the single edge `q–w`. Nothing else: no label change, no deletion, no new
> vertex.

The new active vertex `w` (typically a recent BUD tip on `a`) **grafts onto** the trace `q`
because it was already close to it — distance-2 through an active bridge. `q` thereby gains a
new active neighbour, which can create new CONTACT pairs `{w, b}` (for other active
neighbours `b` of `q` with `w–b` absent). Menu monotonicity is broken **by construction**.

- **Locality / no distant reach.** GRAFT reads only `q`, one active neighbour `a`, and one of
  `a`'s active neighbours `w` — a 3-vertex, radius-2 pattern. It can *never* connect `q` to a
  vertex that isn't already 2 hops away via a live bridge.
- **No forbidden inputs.** No creation IDs, age counters, history labels, global coordinates,
  or externally timed sweep — only local labels and adjacency.
- **How it joins the scheduler.** GRAFT events are enumerated like CONTACT: one eligible
  event per matching `(q, a, w)` wedge with `q–w` absent (distinct bridges `a` for the same
  `(q,w)` are distinct events, as with CONTACT mediators). One step = **uniform selection
  over the union `{directed BUD} ∪ {CONTACT} ∪ {GRAFT}`**, each event weight 1. *This
  relative weighting is a modelling assumption*, stated as such.

### "Record preserved" — defined explicitly (and the earlier claim relaxed honestly)

GRAFT adds an edge incident to a quiet vertex, so the earlier property **"archive
unchanged"** (true for CONTACT) is **no longer true** and we do **not** retain it. The
precise, weaker invariant GRAFT satisfies is **append-only archive**:

1. **No quiet label is ever changed** (`q` stays `Q`; no `Q→A`).
2. **No pre-existing edge is ever deleted.**
3. The only change is the **addition** of an edge incident to a quiet vertex.

Equivalently: the pre-event archive **embeds as a labelled induced substructure** of the
post-event archive — the record is **augmented, never overwritten**. (Verified on the
fixture: labels preserved, all prior edges present, exactly one edge `q–w` added.)

### An existing `q`: empty menu before, nonempty after (verified fixture)

A freshly deposited quiet vertex in M1 sits at a triangle apex `x–q–z` with `x–z` present,
so `C_q = ∅`. Let a new active tip `w` grow on `x` (a BUD, giving the wedge `w–x–q`), with
`w–z` absent. Then (fixture, `legality_fixture.py`, exit 0):

- `C_q(before) = ∅` (active neighbours `{x,z}`, and `x–z` is present);
- `GRAFT(q, x, w)` adds `q–w`;
- `C_q(after) = {{z, w}}` — **nonempty**. A new opportunity has been *added*.

See [`figures/graft_before_after.png`](figures/graft_before_after.png).

### What distinguishes GRAFT from simply reading an already-eligible trace

- **CONTACT (reading)** consumes a pair that was **already in `C_q`** — delayed consultation
  of a *pre-existing* eligibility (menu monotone non-increasing).
- **GRAFT (renewal)** **creates** a pair that was **not** in `C_q`, and could not have been:
  the new opportunity `{z,w}` involves `w`, which was **not a neighbour of `q`** before, so
  `{z,w}` was not in `C_q` at `q`'s deposition. This is **newly enabled relevance**, the
  phenomenon the timing theorem proved impossible without breaking an assumption. (Fixture
  asserts `{z,w}` was absent from the prior menu.)

### Constructed mechanism vs demonstrated tendency

This design **constructs** a legal, local rule that *can* renew a trace, and verifies it on
one fixture. It does **not** claim that renewal **tends to occur** during sustained growth —
whether GRAFT events actually arise, and how often they produce menu growth and downstream
consultation, is an **empirical** question for the bounded test below (and, ultimately, for
larger dynamics that are out of scope here). Existence/legality ≠ tendency.

## Costs and limitations of GRAFT

- **The active front is no longer a closed system.** Once GRAFT is in the rule set, the
  active dynamics reads a quiet vertex (to find the wedge), so the clean closure /
  archive-inertness result of `../endogenous_active_projection/` **no longer holds** — by
  design. That elegance is the price of renewal.
- **The archive is no longer a frozen fossil.** It is append-only but **living**: quiet
  vertices keep gaining incidences over time, so "the record" grows denser. Preserved, but
  not static.
- **Only frontier traces can be renewed.** GRAFT needs an *active* bridge `a` adjacent to
  `q`. A trace all of whose neighbours have gone quiet (a "deeply buried" trace) can **never**
  be grafted onto — renewal is possible only at the **live/archive interface**. (Honest, and
  arguably a feature: depth ≈ permanence.)
- **Interpretability caveat.** `q–w` is a genuine new adjacency justified by a bounded wedge;
  it should be read as "trace and new structure became neighbours because they were already
  two hops apart through a live vertex," **not** as the trace reaching out on its own.
- **It is still a designed-in coupling**, not an emergent discovery.

## Proposed bounded test (concrete; to run only after review — NOT run here)

**Goal.** Show, in *reachable* dynamics (not just a hand fixture), that GRAFT produces
**newly enabled** relevance that BUD∪CONTACT provably cannot — with the record preserved in
the append-only sense.

1. **Seed.** A small state containing a triangle-apex quiet `q` with `C_q = ∅` and a live
   neighbour able to bud a tip (so a wedge can form within a couple of events).
2. **Rule set.** `BUD (k=1) ∪ CONTACT ∪ GRAFT`, uniform over the union. **Control:**
   `BUD ∪ CONTACT` only.
3. **Bounded exact enumeration** (horizon ≤ 3–4 events; exact rational path probabilities;
   WL only for bucketing, exact isomorphism to resolve). Report:
   - probability that `C_q` **grows** (a new opportunity appears) by each horizon — and
     assert it is **0** in the control (by the monotonicity theorem);
   - probability of a **renew-then-consult** path (a GRAFT that adds `q–w`, then a CONTACT
     via `q` consuming the new `{w,·}`) — impossible in the control;
   - a **classification per consulted pair**: was it in `C_q` at deposition (*delayed
     consultation*) or did it enter later via GRAFT (*newly enabled*)?
4. **Record-preservation asserts** on every GRAFT transition: no quiet label changed, no edge
   deleted, exactly one `Q`-incident edge added; the pre-event archive embeds in the
   post-event archive.
5. **Invariance / hygiene:** legal events, graph invariants, **nontrivial relabelling
   invariance**; persistent identities used only for tracking, never for selection.
6. **Scope guard:** report the horizon-bounded probabilities as-is; do **not** infer a
   tendency over sustained growth from them.

**Deliverables of that test:** the growth/renew-then-consult probabilities (extended vs
control), the delayed-vs-newly-enabled classification, the record-preservation asserts, and
a plain-language verdict on whether renewal *occurs* (not just *can* occur).

## Files

- [`legality_fixture.py`](legality_fixture.py) — rule legality + empty→nonempty menu +
  append-only asserts (exit 0). Not an outcome search.
- `results/legality_report.txt`; `figures/graft_before_after.png`.

## Reproduce

```bash
python3 legality_fixture.py   # exact legality checks; exit 0 iff all hold
python3 make_figure.py        # writes the before/after diagram
```

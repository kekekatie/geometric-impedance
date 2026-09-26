# Design note — endogenous growth by local graph rewriting (pre-experiment)

*Register: speculative exploration; a **design proposal with tiny deterministic
feasibility checks**, not a production experiment. Isolated under
`exploratory/accretion_pilot/endogenous_growth_design/`, on the existing branch; v1–v14
and `SYNTHESIS_v1_v14.md` preserved. No merges, publishing, sealed-study access, or large
simulations. **No cosmology, no energy-free-growth, no inexhaustibility claims.** Bounded
enumeration only (`feasibility_checks.py`); we stop before the production experiment for
Astra's review.*

## Why this is a different kind of model

Katie's clarification: **the "track" and the "traveller" are inseparable.** Every earlier
version (v1–v14) had a walker moving on a substrate — memory lived in edge weights the
walker laid down, and even the "local reader" was a second walker. This design **removes
the traveller entirely.** The only thing that happens is **local structural rewriting**:
an *event* looks at a bounded neighbourhood of the graph, and if a local pattern matches,
it rewrites that patch — possibly creating new vertices and edges. There is no walker, no
global coordinate, no history label, no A/B-dependent rule. Structure changes structure.

## The central question — three *separate* properties to demonstrate

Can purely local structural change simultaneously:

1. **(Record)** leave consequences that distinguish prior histories;
2. **(Possibility change)** change which subsequent local events are possible;
3. **(Extension)** extend the graph beyond an initially enumerated finite catalogue of
   connections?

These are **not** one property. A system can easily have (2) and (3) with no (1); (1) is
the hard, interesting one, and the whole design is organised around getting it *honestly*
— a structural record, not a stored log of what happened.

---

## The one thing that makes (1) hard: confluence

A blunt fact from graph-rewriting theory frames everything:

> **Genuinely independent (disjoint) local events commute.** If two rewrite matches do
> not overlap, applying them in either order yields the *same* graph up to isomorphism
> (this is *parallel independence* / the local Church–Rosser property for non-overlapping
> rules). So a rule set whose eligible events are always disjoint is **confluent**: order
> washes out, and history leaves **no** structural record (only vertex names / creation
> order, which we explicitly refuse to count).

Therefore **order-dependent memory can only come from competition** — events whose
neighbourhoods **overlap** so that firing one *disables* another (a non-joinable *critical
pair*). And even then there is a subtlety we must respect: if the two competing events are
related by a **symmetry** of the current graph, their two orders still give isomorphic
results, so order is recorded only in labels and **washes out up to isomorphism**. Real
structural memory needs **competition + broken symmetry**.

This is the design target: a **non-confluent** local rewriting rule whose competitive
divergences are not undone, exhibited explicitly rather than assumed.

---

## Two minimal rule sets (recommend M1)

Both start from a finite graph; vertex states from a small finite alphabet
`Σ = {A (active), Q (quiet)}`; edges unlabelled (an edge's role is read off its endpoint
labels). An *event* matches a bounded pattern and rewrites it. Eligibility is computed
**locally** — one edge and its two endpoint labels — with no walker, target, label, or
A/B rule.

### M2 (contrast, *not* recommended): context-free budding — confluent

- **Rule SPROUT(x):** match one active vertex `x:A`; add a new active vertex `z:A` and an
  edge `x–z`. (Optionally flip `x→Q` after it has sprouted `m` times, tracked by degree,
  not a counter.)
- Matches never overlap destructively (each acts on its own vertex; no shared element is
  deleted), so **M2 is confluent**: any two histories of the same length reach the same
  graph up to isomorphism. It **has extension (3)** (new vertices) and **possibility
  change (2)** (the eligible set grows), but **no record (1)** beyond vertex names.
- M2 is worth stating precisely because it is the **honest null**: "growth that forgets."
  It shows extension and possibility-change are *cheap*; the record is what is hard.

### M1 (recommended): Competitive Accretion Grammar (CAG) — non-confluent

One rewrite schema, **directed on an active bond**, with a branching parameter `k`.

| element | value |
|---|---|
| **Vertex alphabet** | `A` = active, `Q` = quiet (persistent). Finite, size 2. |
| **Edge alphabet** | none (role = function of endpoint labels). |
| **Active bond** | an edge `x–y` with `label[x]=label[y]=A`. The eligible sites. |
| **Event** | `BUD(x, y)` on an active bond — *directed*: `x` = keeper, `y` = depositor. |
| **Precondition (local)** | edge `x–y` exists and both endpoints are `A`. Nothing else. |
| **Effect** | `y → Q`; create `k` new vertices `z₁…z_k : A`; add edges `x–z_i`; add `y–z₁` (so `x–y–z₁` is a triangle — the persistent interior motif). |
| **Scheduler** | which eligible event fires when several are eligible (see below). |
| **Time** | counted in **rewrite events only**. |

**Before → after (one event, k = 1):**

```
        active bond                          x (still A) ──── z (new A tip)
   x:A ───────────── y:A     ─BUD(x,y)→        \\           /
                                                 \\         /
                                                  y:Q  (quiet apex; triangle x–y–z)
```

**The active *boundary* motif (`A–A` bond) becomes a persistent *interior* motif (a `Q`
apex inside a triangle) while creating a new *boundary* motif (the new active bond
`x–z`).** That is exactly the requested "active boundary → persistent interior + new
eligible boundary" shape — see also `figures/rule_before_after.png`.

**Why this is a structural record, not a log.** The deposited `Q` and its triangle are
*graph structure*; we never store a timestamp, creation ID, or the event list and read it
back. All comparisons below are made **up to vertex relabelling** (graph isomorphism with
labels), so anything that survives is in the *shape*, not the bookkeeping.

---

## Verified feasibility (tiny deterministic checks — `feasibility_checks.py`)

Everything in this section is **checked in code**, by bounded enumeration on hand-sized
graphs, and written to `results/feasibility_report.txt`. No stochastic sweep.

### Invariants, and why counts cannot be the memory

Each `BUD` changes the graph by **fixed amounts**: `ΔV=k`, `ΔE=k+1`, `ΔQ=+1`,
`ΔA=k−1` (verified constant across all legal applications). **Consequence:** for a fixed
`k`, the tallies `(V, E, #A, #Q)` are determined **entirely by the number of events**.
Two equal-length histories therefore have *identical* counts **by construction** — so
**no tally can ever distinguish histories.** Any record must live in graph *shape*, and
the only count that can differ is the number of **active bonds** (= number of eligible
sites), which is itself a structural quantity. (This is the cleanest possible statement of
"record ≠ log": we *removed* every additive quantity from contention up front.)

### Non-confluence, exhibited

Seed = active path `a–b–c` (two active bonds sharing `b`). The events `BUD(a,b)` and
`BUD(b,a)` **compete for vertex b**:

- `BUD(a,b)` quiets `b`; then `c` has no active neighbour → **stranded** (inert forever).
  Active-bond count → 1.
- `BUD(b,a)` quiets `a`; the bond `b–c` **survives**. Active-bond count → 2.

The two results are **not isomorphic** and **not one-step joinable** (verified) — the
divergence is permanent. So **order leaves a structural trace: the system is
non-confluent.** *Honest counterpoint, also verified:* `BUD(a,b)` vs `BUD(c,b)` on the
same seed **are** isomorphic — those two events are mirror-related by a seed symmetry, so
their order washes out. Memory needs competition **and** broken symmetry.

### History does work — matched histories, compared up to relabelling

Same seed (active path `0–1–2–3`), two admissible length-2 histories:

| history | events | final counts (V,E,#A,#Q) | active bonds | iso? |
|---|---|---|---|---|
| **P** | `BUD(1,0); BUD(2,1)` | (6, 7, 4, 2) | **2** | — |
| **R** | `BUD(1,2); BUD(0,1)` | (6, 7, 4, 2) | **1** | **not iso to P** |

Counts are identical (as they must be); the graphs are **non-isomorphic**, and they admit
**different numbers of future legal events** (4 vs 2). So the prior history is (1)
**recorded up to relabelling** and (2) **changes which events are next possible** — both
required properties, from a purely local rule. (Enumeration also finds **11 distinct
isomorphism classes** reachable by length-2 histories from this 4-vertex seed: rich
structural divergence under fixed tallies.)

### Do independent events commute? — yes; and what order-memory needs

Stated honestly: **disjoint `BUD`s on non-adjacent active bonds commute** (parallel
independence). All the order-memory above comes from **adjacent** bonds that share a
vertex. The ingredient that "retains order-dependent consequences" is therefore precisely
**competition through a shared vertex with no re-merging rule** — present in M1, absent in
M2. If one wanted *more* order-sensitivity, the lever is to widen the overlap (larger
left-hand sides that share more structure), not to add any global bookkeeping.

### Frontier fate — stall / disappear / proliferate

Deterministic schedule on a 4-ring seed:

| k | eligible-count trajectory | fate |
|---|---|---|
| 0 (ablation) | 8 → 4 → 0 | **disappears** (2 events) |
| 1 | 8 → 6 → 4 → 4 → 4 … | **stalls** (marginal; stranding balances creation) |
| 2 | 8 → 8 → 8 → 10 → 12 → 14 … | **proliferates** |

`k` is the **built-in branching number**: at `k ≥ 2` the rule *manufactures* more eligible
sites than competition removes, so **continuation is built into the rule** — we say so
plainly and do **not** present it as an emergent discovery. The genuinely open question is
the opposite one: at marginal `k=1`, whether competition/stranding *kills* an otherwise
self-sustaining frontier, and whether that fate depends on history.

### Does an apparent record predict continuation?

Enumerated length-2 histories: the naive interior motif count (`Q`-in-triangle) is
**constant** (=2, as the invariants force), so by itself it predicts nothing; yet the 11
distinct shapes admit anywhere from 2 to 6 future events. **An apparent "record" is not
yet a predictor** — whether *some* structural feature predicts continuation is a
first-experiment question, not an assumption.

### The persistence-vs-extension ablation

Set `k = 0`: `BUD₀(x,y)` only does `y → Q` (no new vertices — pure "quieting" on a fixed
vertex set). Two orders on `0–1–2–3` leave **non-isomorphic `Q`-patterns** on the *same*
vertices (verified), with different active-bond counts (1 vs 0). So **persistence (a
history record) is separable from extension (growth)**: the record survives with **zero**
new structure. This is the proposed ablation isolating property (1) from property (3).

---

## Scheduling and resources (part of the model, stated explicitly)

- **Scheduler.** When several events are eligible, one must be chosen. Options: (a) uniform
  random over eligible events; (b) a fixed local priority; (c) a **maximal set of
  pairwise-disjoint** events fired "in parallel" each tick. **The existence of order-memory
  is a property of the rewrite relation (its non-joinable critical pairs), not of the
  scheduler**; the scheduler only sets *which* histories are sampled and how fast the
  frontier grows. We will report results **as a function of the scheduler** and flag any
  conclusion that depends on it. Two orders being compared are specified sequences, so the
  matched-history claim is scheduler-independent.
- **Time** is the **event count**, nothing else.
- **Resources.** *Bounded:* each vertex holds one label from a size-2 alphabet (local
  state capacity is O(1); degree may grow but the *label* set does not). *Consumed:* the
  active bond `x–y` (permanently, when `y` is quieted) — and, through stranding, a
  neighbour's activity. *Replenished by the rule:* `k` new active bonds `x–z_i` per event.
  *Effectively unlimited:* vertex identities and total graph size (unbounded iff the
  frontier proliferates). The only quantity that can run out locally is **active bonds**;
  whether it runs out globally is the stall/proliferate question above.

## What "extension beyond the catalogue" does and does not mean

Creating vertices genuinely escapes any **pre-enumerated finite** catalogue of connections
— unlike v1–v14, where "growth" only switched on members of a fixed diagonal set. **But**
the reachable graphs are still exactly the language the grammar defines; new vertices are
new *tokens*, not possibilities outside the rule's overall (here infinite) state space. We
claim escape from a *finite enumerated catalogue*, **not** creation of possibilities
outside the mathematics of the rule, and **not** inexhaustibility.

## Known failure modes (stated up front)

1. **Symmetry washout.** On symmetric seeds with symmetric competitors, order is recorded
   only in labels and vanishes up to isomorphism. The experiment must use seeds/histories
   that break the relevant symmetry (verified washout example included).
2. **Accidental confluence.** If `k` and the RHS are chosen so competitors always re-merge
   (a joinable critical pair), memory silently disappears. We exhibit a *non-joinable* pair
   to prove M1 avoids this, but any RHS change must re-check joinability.
3. **Trivial "memory" that is really a log.** Reading vertex names, degrees-as-counters, or
   creation order would fake property (1). Guarded by comparing **only up to labelled
   isomorphism** and by the invariant argument (counts are fixed, so they can't carry it).
4. **Built-in continuation mistaken for emergence.** At `k ≥ 2` the frontier must grow;
   that is arithmetic, not discovery. Only marginal `k=1` makes continuation contingent.
5. **Runaway enumeration.** Isomorphism checks are factorial in the worst case; keep seeds
   and histories tiny (≤ ~12 vertices) for exact checks, or use WL-hash bucketing.

---

## Proposed first experiment (concrete; to run only after review)

**Question:** does the M1 structural record (property 1) *causally* change the
distribution of futures (property 2), and does extension (property 3) add anything the
`k=0` ablation lacks — all up to isomorphism, with no traveller and no log?

**Design (bounded, still small):**

1. **Seeds:** 2–3 small asymmetric seeds (e.g. an active path of 5, an active "Y", a
   4-ring with one pendant) chosen so no nontrivial automorphism trivialises order.
2. **Matched histories:** for each seed, enumerate **all** admissible event sequences up
   to length `L` (small, e.g. `L=4`) at `k∈{0,1,2}`. Because tallies are fixed by `(k,L)`,
   every same-`(k,L)` history is count-matched automatically.
3. **Record test (1):** bucket the resulting graphs by **labelled isomorphism**; report
   the number of distinct classes and whether distinct classes come from distinct
   histories (not distinct names). This is exact, deterministic, no sampling.
4. **Possibility test (2):** for each class, record the **multiset of eligible next
   events** (by local type); test whether history-distinguished classes have distinct
   next-event multisets — i.e. the record *does work* on the future.
5. **Extension vs persistence (3):** compare `k=0` (record, no growth) against `k=1,2`
   (record + growth) on the *same* histories; report what growth adds beyond the ablation
   (e.g. whether new classes appear, whether the frontier can be kept alive).
6. **Continuation predictor (open):** for each class, correlate a **small, pre-declared**
   set of local structural features (active-bond count; count of triangle-`Q`; longest
   active path) with the number of reachable futures at one more step — reported
   descriptively, with the null that counts alone predict nothing.
7. **Scheduler dependence:** repeat (4)–(5) under schedulers (a) and (c); flag anything
   that changes.

**Explicitly out of scope for the first experiment:** any stochastic parameter sweep;
any second "reader" walker; any A/B or coordinate-defined score; any claim about
inexhaustible growth, energy, or physical time.

**Deliverables of that experiment:** the isomorphism-class table per seed, the
next-event-multiset comparison, the `k=0`-vs-`k≥1` contrast, and a plain-language verdict
on which of the three properties M1 actually delivers, with the confluence/symmetry
caveats attached.

---

## Recommendation

**Adopt M1 (Competitive Accretion Grammar) as the minimal model, with M2 retained as the
confluent null and `k=0` as the persistence-without-extension ablation.** M1 is the
smallest rule we found that is honestly **non-confluent** (so property 1 is even possible),
while also delivering possibility-change (2) and extension (3) — and its invariants make
the "record vs log" distinction airtight, because every additive tally is fixed by the
event count and cannot smuggle in memory. We **stop here** for Astra to review whether this
model tests the intended question before any production run.

---

## Dated correction — 2026-09-08 (audit; original text above preserved)

*Astra reviewed this proposal and the feasibility code. M1 is retained as a candidate, but
several claims above are corrected or withdrawn. Full proofs, counterexamples, and exact
enumeration (with assertions and a nonzero failure exit) are in
[`../endogenous_growth_audit/`](../endogenous_growth_audit/AUDIT.md). The numbers/tables
above are left in place as the original record; read them through these corrections:*

1. **Frontier arithmetic.** The correct law is `ΔB = k − d_A(y)` (active bonds; `d_A(y)` =
   depositor's active degree before the event). For k≥1 every successor has `B ≥ k`, so
   **sequential rewriting never deadlocks**. At **k=1**, `B` is nonincreasing but **never
   reaches 0**, and `|V|` grows every event — so **"stalls via stranding" and the extinction
   question are WITHDRAWN.** For **k≥2**, a star schedule keeps `B = k` while size, active
   vertices, and active components grow: **"more active vertices" ≠ "more active bonds."**
2. **k=0 invariants.** `ΔE = 0` at k=0 (not `k+1`); invariants are stated separately for
   k=0 and k≥1 in the audit.
3. **Confluence.** One-step non-joinability does **not** establish non-confluence or
   permanent distinguishability. The honest statement is **finite-depth** (competing-pair
   descendants stay disjoint to depth D=3) plus a **Q-immutability** invariant; **global
   non-confluence is left open.** The five notions (commuting independent events / different
   event choices / reordering a fixed collection / confluence / distinguishability at equal
   event count) are separated in the audit. The **P/R histories are different event
   choices, not two orders of one collection** — corrected. The universal claim that
   **structural history requires destructive competition and broken seed symmetry is
   WITHDRAWN.**
4. **M2 is not a "forgetful null."** Three `SPROUT`s from one vertex reach a star **or** a
   path (equal size, non-isomorphic), so M2 distinguishes equal-length histories. Its
   confluence status is a separate open question.
5. **"Record ≠ log" overclaim.** Fixed `V/E/#A/#Q` totals only remove those four tallies
   from contention; they do **not** exclude other informative counts (bonds, components,
   degrees — which *do* differ) and do **not** prove the record is "not a log."
6. **Exactness.** Class counts are now resolved by exact state-preserving isomorphism (WL
   used only to bucket), with `assert`s and a nonzero exit — not hash-only dedup or printed
   "verified" lines.

The retained positive result: depth-2 states from the 4-vertex path (k=1) form **exactly 11
isomorphism classes**; matched-length histories (incl. P vs R) reach **different** classes
with **different available continuations** (successor table in the audit).

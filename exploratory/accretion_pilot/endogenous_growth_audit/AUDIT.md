# Audit & repair — M1 (Competitive Accretion Grammar)

*Register: speculative exploration; **proofs, counterexamples, and tiny exact enumeration
only** — no stochastic sweeps, no production experiment. Repairs the
`../endogenous_growth_design/` proposal per Astra's review. The original proposal is
preserved; a dated correction is appended there pointing here. All bounded claims below
are checked in `audit_checks.py` with explicit `assert`s and a **nonzero exit on any
failure** (printed "verified" text is not a gate). State-preserving isomorphism (vertex
labels A/Q matched) is used throughout; WL hashes only **bucket** candidates and every
bucket is then **resolved exactly**. M1 is **retained as a candidate**, corrected.*

Legend: **[ANALYTIC]** = proof (stated here, checked on bounded cases); **[BOUNDED]** =
an exact finite observation only (no general claim).

---

## 1. Corrected frontier arithmetic

Let `B` = number of **active undirected bonds** (edges with both endpoints `A`) and
`d_A(y)` = the depositor's **active degree** (its number of `A`-neighbours) *before* the
event.

**[ANALYTIC] `ΔB = k − d_A(y)`.** In `BUD(x,y)` (k≥1): quieting `y` removes exactly the
`d_A(y)` active bonds incident to `y` (each edge `y–w` with `w` active loses activity);
the `k` new edges `x–z_i` are active bonds (`x` stays `A`, each `z_i` is new `A`) and are
the *only* bonds created (`y–z_1` is inactive because `y` is now `Q`); no other bond
changes activity. Hence `ΔB = k − d_A(y)`. ∎ *(Verified exhaustively on
{path3, path4, star4, path5}, k∈{0,1,2,3}.)*

**[ANALYTIC] No deadlock for k≥1.** The `k` new bonds `x–z_i` touch only `x` and fresh
`z_i` (with `x≠y`), so they are disjoint from the edges incident to `y` and **survive the
event**. Therefore every successor has `B ≥ k ≥ 1`, so an eligible directed event always
exists: **from a seed with a legal event, continued sequential rewriting cannot deadlock**
(given the scheduler keeps selecting; resources permitting). ∎

**[ANALYTIC] k=1 does not stall or go extinct.** At k=1, `ΔB = 1 − d_A(y) ≤ 0` (since
`d_A(y) ≥ 1` always — `y` sits in the matched bond), so `B` is **nonincreasing**; but by
the previous point `B ≥ 1` after every event, and `|V|` grows by 1 every event. So `B`
**never reaches zero** and the **graph keeps growing** along any infinite derivation.
→ **WITHDRAWN:** the earlier "k=1 stalls via stranding" and the proposed "extinction
question." The frontier does not die; it is the *active-bond count* (not the ability to
continue) that fails to grow.

**[ANALYTIC + BOUNDED] k≥2: more active vertices ≠ more active bonds.** Growing the active
*vertex* count does not imply a growing active *bond* count. Schedule on an active star,
repeatedly quieting the centre with a leaf as keeper (k=2), verified exactly:

| event | |V| | active vertices | active bonds `B` | active components |
|---|---|---|---|---|
| seed `star(4)` | 5 | 5 | 4 | 1 |
| quiet #1 | 7 | 6 | **2** | 4 |
| quiet #2 | 9 | 7 | **2** | 5 |
| quiet #3 | 11 | 8 | **2** | 6 |
| quiet #4 | 13 | 9 | **2** | 7 |

`|V|`, active vertices, and active **components** all grow while active **bonds** stay
`= k`. So four quantities must be kept distinct: **graph size, active vertices, active
bonds, and number of active components** (the last grows because each quieting strands
singleton active vertices — isolated in the active subgraph).

**Invariants stated separately.** Per event:

| | ΔV | ΔE | ΔQ | ΔA | ΔB |
|---|---|---|---|---|---|
| **k = 0** (quiet-only ablation) | 0 | **0** | +1 | −1 | −d_A(y) |
| **k ≥ 1** | k | **k+1** | +1 | k−1 | k−d_A(y) |

→ **Correction:** the earlier blanket "ΔE = k+1" was wrong for k=0, where **ΔE = 0**.

---

## 2. Repaired confluence claims — five distinct notions

One-step non-joinability is **not** a proof of non-confluence or of permanent
distinguishability. The five notions the review asked to separate, with what is and is not
established:

1. **Commuting independent events.** **[ANALYTIC/known]** Disjoint (non-overlapping)
   matches commute — *parallel independence*. **[BOUNDED]** `BUD(0,1)` then `BUD(3,4)` on
   `path(6)` equals the reverse, exactly (iso). This is the one clean commuting statement.
2. **Different event choices.** Selecting one event vs another from the same state. **The
   P/R histories are THIS**, not two orders of one collection: `P = BUD(1,0);BUD(2,1)`
   quiets vertices **{0,1}**, `R = BUD(1,2);BUD(0,1)` quiets **{1,2}** — different directed
   events, different vertices removed. *(Their undirected edges coincide, but the
   depositors — which endpoint is quieted — differ. The earlier note calling them "two
   orders of the same operations" is **WITHDRAWN**.)*
3. **Reordering a specified event collection.** Applying one fixed collection in different
   orders. Here the only order-sensitive situations are **critical pairs** that share a
   vertex — e.g. `e1 = BUD(0,1)` (quiets 1) and `e2 = BUD(1,2)` (needs 1 active) on
   `path(3)`. **[BOUNDED]** Firing `e1` **deletes** `e2`'s match, so the collection
   `{e1, e2}` is **not jointly realisable in the other order** — this is conflict, not a
   clean reordering. Genuinely co-realisable (disjoint) collections fall under notion 1 and
   commute.
4. **Confluence.** A **global** property: every divergent pair of derivations can be
   extended to a common state. **NOT established.** Our system does not terminate (it grows
   forever), so Newman's lemma (local⇒global under termination) does not apply. What we
   have is **[BOUNDED]**: the two depth-1 descendants of the `path(3)` critical pair have
   **disjoint** descendant class-sets up to added depth **D=3** (4 classes vs 18 classes,
   no isomorphic overlap), plus one supporting **[ANALYTIC] invariant** —
   **Q-immutability:** an event writes only `x` (stays `A`), the single depositor `y`
   (`A→Q`, +1 edge), and fresh `z_i`; a vertex already `Q` is none of these, so **once `Q`,
   a vertex's label and incident edges are frozen forever** (a stranded `A` vertex is
   likewise frozen). This makes the accumulated `Q`-structure monotone, but it is **not**
   by itself a proof that the two lines can never join. **Global non-confluence is left
   open.**
5. **Distinguishability at equal event count.** Two equal-length derivations reaching
   non-isomorphic states. **[BOUNDED, established]** — P vs R are non-isomorphic; depth-2
   from `path(4)` yields **11 exact classes** (§4). *This* is the property that makes
   "history do work," and it does **not** require non-confluence.

**→ WITHDRAWN (universal claim):** "structural history requires destructive competition
and broken seed symmetry." Distinguishability at equal event count (notion 5) can arise
from **different event choices alone**, with no destructive competition — demonstrated by
M2 below (a rule with no shared-vertex deletion still reaches star vs path). Destructive
competition / non-joinable critical pairs are what bear on **order**-dependence of a
co-realisable collection and on **confluence** (notions 3–4), not on history-
distinguishability in general.

**M2 is not a forgetful null.** **[BOUNDED]** From one active vertex, three `SPROUT`
events reach either a 4-vertex **star** `K₁,₃` (sprout the same vertex thrice) or a
4-vertex **path** `P₄` (sprout along) — equal `V=4, E=3`, **non-isomorphic**. So M2
**distinguishes** equal-length histories; the earlier "same-length forgetful null"
characterisation is **WITHDRAWN**. *(This does not settle whether M2 is confluent — a
separate question we leave open.)*

**→ WITHDRAWN (overclaim from §"invariants"):** that fixed `V/E/#A/#Q` totals prove
"record ≠ log." Those four totals are fixed by `(k, event-count)`, so they cannot
distinguish equal-length histories — but that neither excludes **other** informative counts
(active bonds `B`, active components, degree sequence — all shown to differ across
equal-length histories) **nor** proves the structural record is "not a log." "Record vs
log" is a separate conceptual question these invariants do not settle.

---

## 3. Exactness of the checks (method)

- **Buckets then exact resolve.** `class_reps()` groups graphs by WL hash, then resolves
  each bucket by exact `nx.is_isomorphic` with `categorical_node_match("label")`. WL is
  never trusted for a class count. *(Here WL and exact happen to agree at 11 classes, but
  the count is now established by exact isomorphism, not by the hash.)*
- **Assertions + nonzero exit.** Every claim is a `require(...)`; the script collects
  failures and `sys.exit(1)` if any occurred. The current state is **exit 0 (all pass)**.
- **State-preserving.** Isomorphism matches the `A/Q` labelling, not bare topology.

---

## 4. The bounded positive result (retained)

**[BOUNDED]** Depth-2 states from the 4-vertex active path, k=1: **28** directed
length-2 derivations collapse to **exactly 11 isomorphism classes** (state-preserving).
`P` lands in **class 4** (`B=2`), `R` in **class 8** (`B=1`) — **different classes**.

For each depth-2 class, the one-step successor classes with the **multiplicity of directed
events** reaching each (under uniform selection over directed eligible events, these
multiplicities *are* the next-state probabilities):

```
class  B  #dir.events   successor-class : multiplicity            (uniform probs)
  0    2      4          {0:1, 1:1, 2:1, 3:1}                     each 0.25
  1    2      4          {2:2, 4:1, 5:1}                          0.50 / 0.25 / 0.25
  2    2      4          {3:4}                                    1.0   (single successor type)
  3    2      4          {6:1, 7:1, 8:1, 9:1}                     each 0.25
  4    2      4          {10:1,11:1,12:1,13:1}   <- class of P    each 0.25
  5    3      6          {4,6,14,15,16,17} each 1                 each 0.167
  6    2      4          {5:1,18:1,19:1,20:1}                     each 0.25
  7    3      6          {10:2,17:2,18:2}                         each 0.333
  8    1      2          {21:2}                  <- class of R    1.0
  9    2      4          {8:1,22:1,23:1,24:1}                     each 0.25
 10    1      2          {25:1,26:1}                              each 0.5
```

**This answers the immediate question:** *do matched-size historical outcomes differ in
their available continuations?* — **Yes, exactly.** `P` (class 4) offers 4 directed events
reaching 4 distinct successor classes; `R` (class 8) offers only 2 directed events, both
reaching the **same** class 21. The continuation *distributions* differ across matched-size
classes generally (the profiles above are not all equal). **We do not** claim that a larger
eligible-event count predicts "richer" future structure — that is a further, unproven
statement; here we report only that the available continuations *differ*.

---

## 5. Plain-language verdict

Removing the traveller and rewriting the graph directly still gives us the thing we cared
about — **different histories of the same length leave genuinely different structures, and
those differences change what can happen next** — and we can now show it *exactly* on tiny
graphs, not by a hash approximation.

What the audit **fixed**: the frontier does **not** stall or die at k=1 (it always has a
next move; only the active-bond count plateaus while the graph keeps growing); "more active
vertices" must not be read as "more active bonds" (a star schedule pins bonds at `k` while
size and active components climb); k=0 adds no edges; and several claims were softened to
what is actually proven. In particular we now say plainly: **confluence is not settled** —
we only show a specific competing pair stays split to depth 3, backed by a real invariant
(quiet vertices are frozen forever), and we **withdraw** the universal claim that memory
needs destructive competition (M2 forgets nothing — a star and a path are both reachable in
three sprouts). Fixed vertex/edge/A/Q totals do **not** prove the record "isn't a log";
they only remove those four tallies from contention, while other counts (bonds, components,
degrees) do carry the distinction.

**M1 is retained as a candidate.** The recommended first experiment stays what §4
prototypes: **exact enumeration of isomorphism classes and their directed-event successor
distributions** on small seeds and shallow depths — the deterministic, gate-checked core —
before any scheduler or parameter study. We stop here for review.

## Files

- [`audit_checks.py`](audit_checks.py) — all exact checks (asserts, nonzero exit).
- `results/audit_report.txt` — full run log.
- `results/successor_table.txt` — the depth-2 successor table.

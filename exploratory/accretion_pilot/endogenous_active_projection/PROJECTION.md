# Active projection — is the quiet archive causally inert? (M1, pre-experiment)

*Register: speculative exploration; **proof + tiny exact enumeration only** — no
stochastic sweeps, no rule changes, no production experiment. Isolated under
`exploratory/accretion_pilot/endogenous_active_projection/`, on the existing branch;
previous results preserved. M1 (Competitive Accretion Grammar) is unchanged; we only
**analyse** it. Checks in `active_projection_checks.py` use `assert`s with a **nonzero
exit** on any failure (printed text is not a gate); classification uses WL only to bucket,
then exact isomorphism.*

## Question

Under **uniform selection among directed active–active bonds**, does the **induced active
graph alone** determine the distribution of its next active state — i.e. is there a
**closed transition rule on active graphs**, independent of the quiet archive?

## The projection

`π(G)` = the induced subgraph on the **active** (`A`, "1") vertices, keeping only **A–A
edges**, with **isolated active vertices retained**. Every quiet (`Q`, "0") vertex and
every A–Q / Q–Q edge is dropped. Think of it as *the subgraph of 1s*, discarding the field
of 0s.

## Analytic result — the active front is a closed system

Write `BUD(x,y)` for the M1 event (keeper `x` stays `A`; depositor `y → Q`; `k` fresh
active tips `z_i` with edges `x–z_i`; plus `y–z₁`). Two facts, each **proved and checked
exhaustively** on all 147 reachable states to depth 3 from the 4-vertex path:

- **[L1] Selection is π-measurable.** The eligible directed events of `G` are **exactly**
  the directed edges of `π(G)` (an active bond `x–y` *is* an edge of `π(G)`). So the number
  and identity of choices — hence the uniform distribution over them — is a function of
  `π(G)` alone. *(Verified: `#directed events == 2·|E(π(G))|`, and the event set equals the
  directed-edge set of `π(G)`, for every reachable state.)*

- **[L2] The effect commutes with projection.** Projecting `BUD(x,y)` gives a rule that
  reads only the active graph:
  > **`budπ(x,y)`**: delete `y` and its active edges; keep `x`; add `k` fresh active
  > leaves on `x`.

  and `π(BUD(x,y)·G) ≅ budπ(x,y)·π(G)` for every reachable state and event (verified,
  state-preserving iso). The reasons, term by term: quieting `y` removes exactly `y` and
  its A–A edges from `π`; `x` is retained; the `z_i` become `k` leaves on `x`; and the
  **`y–z₁` edge is A–Q, so it never appears in `π`** — the "quiet triangle edge" is
  invisible to the projection. No `Q` vertex, and no A–Q or Q–Q edge, is ever consulted.

**Together:** under this scheduler the **distribution of the next active state is a
function of `π(G)` alone** — a **closed (autonomous) transition rule on active graphs**,
independent of the quiet archive. The map `G ↦ π(G)` is a *factor* (quotient) of the full
dynamics: the active front evolves without ever reading the archive it writes.

**Scope — this depends on the scheduler.** The closure is a joint property of the
*projected effect* (L2, always true) **and** a *scheduler that reads only `π`* (L1, true
for uniform-over-directed-active-bonds). A scheduler that weighted events by a vertex's
**total degree** (which counts quiet neighbours), or consulted any quiet context, would
make selection depend on the archive and **break the closure**. We claim it only for the
specified uniform-over-active-bonds scheduler.

**What is *not* claimed.** The **full** future graph is **not** independent of the archive.
Quiet structure persists and accumulates; two states with isomorphic active projections but
different archives generally have **non-isomorphic full successors** (their archives differ
and keep growing). History is still recorded in the full graph — the archive is just
**causally inert for the active transition rule**.

## Tiny exact verification (reuse the 11 depth-2 full classes; path(4), k=1)

The 28 directed length-2 derivations from the 4-vertex active path form **11 exact
full-state classes** (state-preserving). Projecting each: they collapse onto **4
active-projection classes** `P0–P3`. For each full class, the directed-event successor
distribution over **active-projection** classes (exact rationals):

| full class | active proj | B | #dir. events | projected-successor classes : multiplicity | exact probs |
|---|---|---|---|---|---|
| 0, 1, 2, 6 | **P0** | 2 | 4 | {0: 4} | 0 → 1 |
| 3, 4, 9 | **P1** | 2 | 4 | {1: 2, 3: 2} | 1 → ½, 3 → ½ |
| 5, 7 | **P2** | 3 | 6 | {0: 2, 1: 2, 2: 2} | ⅓, ⅓, ⅓ |
| 8, 10 | **P3** | 1 | 2 | {3: 2} | 3 → 1 |

**Every group of full classes that share an active projection shares an identical projected
successor distribution** (verified exactly) — the enumerated confirmation of L1+L2. (Full
table: `results/projection_successor_table.txt`.)

Two book-keeping distinctions the table keeps visible:
- **Multiplicity ≠ distinct outcomes.** P0 has **4** directed events that **all** lead to a
  **single** successor class (multiplicity 4, one outcome, probability 1). P2's 6 events
  spread over 3 classes. Event count is not outcome count.
- **Collapse.** 11 full classes → 4 active classes: much of the depth-2 full-state variety
  lives **only in the archive**, invisible to the active present.

### A concrete archive-inert pair (found in the bounded set)

Full classes **0** and **1**: **non-isomorphic** full graphs, but **isomorphic** active
projections (both are *two disjoint 1–1 bonds*), differing only in the quiet archive
(Q-degree multisets **{3,3}** vs **{2,3}**). Their projected successor distributions are
**identical** (both P0 → single class, probability 1). This is the claim made visible: a
history difference that lives **entirely in the archive** is **distinguishable in the full
present but not in the active present, and does not touch the active dynamics.** See
`figures/active_projection.png`.

## Interpretation — three levels, separated

1. **History distinguishable in the full present.** **Yes** — 11 distinct full classes at
   depth 2; classes 0 and 1 differ.
2. **History distinguishable in the active present.** **Only partly** — the 11 full classes
   project onto **4** active classes. History that differs *only in the archive* (0 vs 1)
   is **invisible** to the active projection.
3. **Historical differences that alter subsequent active dynamics.** **Only those visible
   in the active projection.** By L1+L2 the next-active distribution is a function of `π`
   alone, so two states with the same `π` (e.g. 0 and 1) have identical projected futures —
   their archive-only difference is **causally inert** for the active rule.

**Verdict (plain language).** For M1 under uniform selection over active bonds, the field of
0s is **write-only**: the front of 1s lays it down and never reads it back. The active
front is a **closed, self-contained dynamical system** — you can predict how the 1s move
knowing only the 1s. History still shapes what the front does next, but **only through the
present shape of the front**, never through the archive behind it. The archive is not
useless — it is exactly where the *record* lives (level 1), and it is what makes the **full**
graph remember more than its active front does — but it exerts **no causal pull** on the
active dynamics under this scheduler. Change the scheduler to consult total degree or quiet
context and this separation dissolves; that boundary is the next thing worth probing, and we
stop here — no model change — for review.

## Files

- [`active_projection_checks.py`](active_projection_checks.py) — L1/L2 proofs-as-checks,
  the projection/successor table, the archive-inert pair; asserts + nonzero exit.
- `results/projection_report.txt`, `results/projection_successor_table.txt`.
- `figures/active_projection.png` — the explanatory diagram.

## Reproduce

```bash
python3 active_projection_checks.py   # exact; exit 0 iff all checks pass
python3 make_figure.py                # writes the diagram
```

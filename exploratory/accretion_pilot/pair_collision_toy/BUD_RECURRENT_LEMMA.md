# Lemma — BUD-only recurrent classes are singleton matchings

*Short note. Proof sketch plus an exhaustive computational check
([`bud_recurrent_lemma.py`](bud_recurrent_lemma.py), exit 0 iff all checks pass). It generalises
the remark behind Proposition 3 in
[`../endogenous_present_width/coast_asymptote.py`](../endogenous_present_width/coast_asymptote.py),
which was stated there only for the matched pair's 4-vertex coast.*

## Setting

The **coast chain** is BUD-only at `k=1` acting on **active projections**. That is well defined
by Proposition 1 ([`../endogenous_active_projection/`](../endogenous_active_projection/)): under
BUD-only, the successor of the active projection depends only on the projection. One step picks
a directed active bond `(x,y)` uniformly. On the projection, `BUD(x,y)` deletes `y` (it goes quiet)
and adds a new tip `z` joined to `x` only. A graph with no edge has no event and is treated as an
absorbing self-loop, the same convention `coast_asymptote.py` uses. Write `B` for the number of
active edges and `d_A` for active degree.

## Lemma

> For **any** seed, every recurrent class of the coast chain is a **singleton `{M}`** with
> `T(M,M)=1`, where `M` is a **matching plus isolated vertices**. Conversely every such `M` is
> absorbing. So the coast is an absorbing chain, and its sinks are exactly the matchings on
> `n = #active` vertices, one for each matching size `0..⌊n/2⌋`.

## Proof sketch

1. **`ΔA = 0`.** A BUD makes one active vertex quiet and adds one active tip. So `n` is invariant,
   and the chain started from any seed lives on the finite set of `n`-vertex graphs up to
   isomorphism. A finite chain has at least one recurrent class, and every trajectory enters one
   almost surely.
2. **`ΔB = 1 − d_A(y) ≤ 0`.** The depositor `y` takes its `d_A(y) ≥ 1` active edges with it,
   including `x–y`, and the new edge `x–z` adds one back. So `B` is non-increasing along every
   transition ([`../endogenous_growth_audit/`](../endogenous_growth_audit/) proves `ΔB = k − d_A(y)`).
3. **`B` is constant on a recurrent class.** Every state of a recurrent class is reached again
   from every other one. A transition inside the class that lowered `B` could never be undone,
   because `B` cannot rise. So every transition out of a recurrent state, all of which stay in
   the class, has `ΔB = 0`.
4. **So a recurrent state is a matching.** `ΔB = 0` for every directed bond `(x,y)` means
   `d_A(y) = 1` for every endpoint of every edge. Every non-isolated vertex has degree exactly 1,
   which is a matching plus isolated vertices.
5. **A matching is a fixed point.** For a matching edge `x–y`, `BUD(x,y)` deletes `y` and hangs
   the new tip `z` on `x`. That gives the same shape: one fewer edge `x–y`, one new edge `x–z`, and
   every other vertex untouched. So every event maps `M` to `M`, `T(M,M)=1`, and the class is
   `{M}`. With no edges there are no events, and the self-loop convention makes it absorbing too.
   ∎

## Computational check (exhaustive, `n ≤ 6`)

The check covers every isomorphism class of graphs on `n = 1..6` vertices from the networkx
graph atlas, disconnected graphs included. That is **208 classes**, so it covers every possible
seed with at most 6 actives. Everything is exact, using `Fraction` and exact isomorphism.

| n | classes | recurrent classes | all singleton matchings, absorbing? | absorption prob. from every transient class |
|---|---|---|---|---|
| 1 | 1 | 1 | ✓ | (no transient class) |
| 2 | 2 | 2 | ✓ | (no transient class) |
| 3 | 4 | 2 | ✓ | 1 (2 transient) |
| 4 | 11 | 3 | ✓ | 1 (8 transient) |
| 5 | 34 | 3 | ✓ | 1 (31 transient) |
| 6 | 156 | 4 | ✓ | 1 (152 transient) |

The script also asserts, for each `n`, that `ΔB = 1 − d_A(y)` holds on every single event and
that `B` never increases.

**Scope.** This is BUD-only. With CONTACT the chain is no longer on projections alone (the
archive matters), and `B` can rise, so the argument does not transfer. In the pair-collision toy
next door the frozen states are still matchings, but for a different reason: there, "frozen" is
*defined* as no CONTACT eligible plus a matching projection.

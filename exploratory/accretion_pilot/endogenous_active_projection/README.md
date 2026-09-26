# Active projection of M1 — is the quiet archive causally inert?

**Proof + tiny exact enumeration only. No stochastic sweep, no rule change, no production
experiment.** Analyses the retained M1 (Competitive Accretion Grammar); previous results
preserved. Stops before any model change, for review.

## Question & answer

*Under uniform selection among directed active–active bonds, does the induced active graph
alone determine the distribution of its next active state?* — **Yes.**

Define the projection `π(G)` = the subgraph of active (`A` = "1") vertices with only A–A
edges, isolated actives retained (every quiet `Q` = "0" vertex and A–Q/Q–Q edge dropped).
Then:

- **[L1]** eligible directed events = directed edges of `π(G)` (selection reads only `π`);
- **[L2]** `π(BUD(x,y)·G) ≅ budπ(x,y)·π(G)`, where `budπ` = "delete `y` + its active edges;
  keep `x`; add `k` leaves on `x`" — the quiet triangle edge never appears.

So the next-active distribution is a **function of `π(G)` alone**: a **closed transition
rule on active graphs**, independent of the quiet archive. The active front is autonomous;
the archive is **write-only**. *(Scope: holds for the uniform-over-active-bonds scheduler; a
scheduler consulting total degree or quiet context would break it.)*

**Not claimed:** that the *full* future is archive-independent — it is not; history still
lives in the growing archive and in the full graph.

## Verified exactly

`python3 active_projection_checks.py` (exit 0):
- L1, L2 on all 147 reachable states to depth 3 from `path(4)`.
- The 11 depth-2 full classes collapse to **4 active-projection classes**; full classes
  sharing an active projection share an **identical** projected successor distribution.
- A concrete pair (full classes **0** & **1**): non-isomorphic full graphs, isomorphic
  active projections, different archives ({3,3} vs {2,3} Q-degrees), **identical** projected
  futures — archive causally inert.

## Interpretation (three separated levels)

1. distinguishable in the **full** present — yes (11 classes);
2. distinguishable in the **active** present — only partly (4 classes; archive-only
   differences invisible);
3. differences that alter **active dynamics** — only those visible in `π`; archive-only
   differences are causally inert.

See [`PROJECTION.md`](PROJECTION.md) for the proof, the successor table, and the verdict;
[`figures/active_projection.png`](figures/active_projection.png) for the diagram.

## Reproduce

```bash
python3 active_projection_checks.py
python3 make_figure.py
```

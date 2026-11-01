# Protocol — jam compatibility diagnostic (frozen before the analyses)

*2026-11-02. Exploratory diagnostic, no preferred outcome. Written before running
the new analyses; deviations are recorded in `PROTOCOL_DEVIATIONS.md`, not edited
in here.*

**Central question.** Which commitments prevent this frontier from continuing,
and what changes when the inner boundary releases some of them?

## Source and scope (frozen)

- Repository `kekekatie/geometric-impedance`. Study branch
  `claude/jam-compatibility-diagnostic`, new directory
  `exploratory/accretion_pilot/jam_compatibility_diagnostic/`.
- **Source commit** inspected: `aa371d4` (the jam-repair pilot + two-flip
  exploration on `claude/confident-cerf-404o4f`); confirmed no later commits.
- **Frozen engine** imported read-only from commit
  `84130b97f5044197392e72cd53e0e71f81b043f3`
  (`expansion_front_paper/`). Original engine, reader and historical results are
  not modified. The frozen reader (`skin_reader.py`) is left unchanged;
  diagnostics are added alongside it.
- **Exact case identifiers** (not world labels alone), in
  `results/case_identifiers.json`:
  - Primary: **world 7**, fork config key `4250b244a8d0887c`, S* patch 198,
    options A=shape0 / B=shape1, streams `[20262655433, 20262655534]`
    (stream indices 0,1). B jams at step 23 in both; choice-tile departs at 17.
  - Replication: **world 5**, fork config key `3a33a0d534922f0e`, S* patch 210,
    streams `[20262639595, 20262639696]`. B/s0 jams at step 42.
- Do **not** rerun the whole 88-continuation study. World 7 first; world 5 as
  replication after the first case is understood.

## Part 2 — feasibility, not "zero area"

The compatibility region is `F = { t in R^2 : n_i . t >= c_i for all active
(rank,i) }`, with `c_i` and normals `n_i` taken **from the frozen**
`Sl.constraints` / `WIN` (we read them, we do not redefine them). The earlier
reports used polygon area `<= 1e-12` as "empty"; a zero-area region may instead
be a point or a segment (feasible). We add an independent feasibility diagnostic:

- **Chebyshev-center LP** (scipy.linprog): maximise `r` s.t.
  `n_i . t - r*||n_i|| >= c_i` for all i (with the same `[-50,50]^2` box). Let
  `r*` be the optimum.
  - `r* > tol_r`  -> **positive-area feasible** (full-dimensional).
  - `|r*| <= tol_r` and LP feasible -> **lower-dimensional feasible** (point or
    segment); confirmed by solving for an explicit witness `t` and checking the
    active-constraint rank.
  - LP reports infeasible, or `r* < -tol_r` -> **infeasible**.
  - LP status inconclusive, or classification flips under the sensitivity sweep
    -> **numerically unresolved**.
- **Normalisation**: normals are used as given by `WIN`; `||n_i||` is their
  Euclidean norm so `r` is a true inscribed-ball radius in offset units.
- **Sensitivity**: re-solve with `c_i -> c_i +/- eps` for
  `eps in {1e-12, 1e-10, 1e-8, 1e-6}`; report whether the four-way class is
  stable. This is numerical evidence, not exact certification; limits stated.
- **Boundary convention**: the frozen `region()` treats constraints as closed
  (`>=`). We test feasibility under the **closed** system (matching the engine)
  and separately note if any case is feasible only on its boundary (a
  lower-dimensional region), since the projection's open/closed convention then
  matters. If more than one admissible layer-rank assignment exists for a state,
  all admissible cases are evaluated.
- **Controlled examples** (`tests/`): constraint sets whose exact region is a
  known polygon, a segment, a point, and an empty set; the classifier must label
  each correctly, with a numerical sensitivity check.

Then re-examine the world-7 `F(full)` and `F(skin)` "F=0" claim under this
diagnostic and report which of the four classes each truly is.

## Part 3 — first loss of compatibility

Faithfully replay the selected continuations (world 7 B, both streams) with the
frozen growth rules and scheduler. At **every** tile-addition and prune event,
evaluate feasibility (Part 2) of (a) the full audit patch and (b) the retained
skin, in a **consistent gauge** (the S*-anchored lift used by the closure).
Record: the earliest loss of feasibility for each, its step, the triggering
event, and its relation to the visible jam (step 23). Pruned-skin feasibility is
**not assumed monotone** (removing a vertex removes constraints and can restore
feasibility). Full history is permitted for this audit; any later archive-free
claim uses only exported retained state. If the fork S* is already infeasible,
report that; trace earlier only if faithfully reproducible — no invented prior
transition.

## Part 4 — identify and draw the incompatible constraints

For genuinely infeasible states, extract an **inclusion-minimal infeasible
subset (IIS)** by the deletion filter (drop a constraint; keep it dropped if the
remainder is still infeasible). Distinguish **inclusion-minimal** from
**minimum-cardinality** (we report inclusion-minimal; minimum-cardinality is not
claimed). Map each conflicting constraint back to its originating tile(s),
vertex, layer rank and window edge; retain multiple origins when a constraint is
tied across vertices. Figures: retained tiles with **both** boundary components
(true frontier vs pruning-exposed), the zero-candidate frontier sites, the tiles
supplying the conflicting constraints, and the constraints drawn in internal
(perp/offset) space. Compare the first-infeasible state with the jam: is the
conflict concentrated near the notch, or does it couple separated parts of the
ring, and how early is it detectable? One IIS is not unique and need not be a
causal repair target — stated; alternative witnesses inspected if inexpensive.
For feasible degenerate states, show the surviving point/segment and its active
constraints instead of manufacturing a witness.

## Part 5 — bounded inner-rim erosion

On one jam (world 7), first inspect how the engine separates the **true growth
frontier** (the `ActiveSkin.boundary` dict, maintained incrementally) from edges
merely exposed by pruning; **preserve** that distinction — pruning-exposed inner
edges are not growth sites. Hold the outer growth boundary and retained geometry
fixed except for a deterministic, nested removal of inner-rim tiles. **Erosion
levels fixed now, before outcomes:** level 0 = the retained skin as-is; levels
1,2,3 = remove tiles whose minimum distance to any true-frontier vertex exceeds
`(radius - L)*S` for `L = 1,2,3` (i.e. peel the innermost rim shells, keeping the
outer `radius-L` shells). Stop before the erosion disconnects the skin component
containing the dead sites or removes any dead-site neighbour tile; report the
level at which a stop occurs.

At each level measure separately:
1. compatibility-region feasibility (Part 2 classes);
2. candidate counts at the **original** dead sites (frozen `D.candidates`);
3. contextual legality of the previously-tested single-hexagon alternatives
   whose complete support still remains (frozen engine);
4. whether the frozen A/B reader still operates and its result (unchanged
   decision rule and original historical hypotheses), reported as
   empty/incompatible, ambiguous, uniquely correct, uniquely wrong, or reader
   failure, each separately.

Rearrangement candidates are validated against the **completed** rearranged
patch; the enumerator's sequential construction may miss some completed
alternatives — either addressed or the completeness claim is limited explicitly.
No growth is resumed; improved candidate availability is not a rescue. If
deleting tiles alone removes a dead site or loosens a constraint, that is
distinguished from a rearrangement restoring candidates at a still-present site.
If correct boundary handling needs substantial engine development, stop with a
concrete explanation and preserve the completed diagnostic work.

## Interpretation boundaries

Testing, not assuming: first global incompatibility may precede the visible jam;
separated retained constraints may jointly block a common offset; pruning may
change rearrangement availability; mobility and readability may respond
differently to constraint removal. The `pB ~ 0.854` association stays
descriptive (no "greed" mechanism without an independent test). No claim of
universal local rigidity from a finite search; no identification of a matching
violation with a Burgers defect, particle, energy barrier, or thermal
protection — any new claim needs its own defined observable.

## Deliverables

Protocol + dated deviations; reproduction commands + focused validation checks;
machine-readable results with exact case ids and numerical settings; a few
readable figures; `HANDBACK.md` (Katie-first: what changed in the picture, then
implementation), separating observations, interpretations, unresolved numerical
questions, and recommended next work. Commit + push the new branch; no merge, no
force-push. Stop after this diagnostic study.

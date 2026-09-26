# Follow-up design note (v6) — crossed initial conditions (a 2×2 intervention)

*Written before execution. Register: speculative exploration; not a confirmatory
study, not cosmology. Bounded follow-up to v5 (chain v1 `cc514ee` → v2 `cab9254` →
v3 `fe49f64` → v4 `43d0c61` → v5 `e64ab73`). Isolated under
`exploratory/accretion_pilot/v6_intervention/`. v1–v5 retained unchanged. No merges,
publishing, sealed-study access, parameter tuning, or changes to the subsequent
movement / reinforcement / growth rules. This run intervenes on **initial
conditions only** and evolves them under the unchanged Growing rules.*

Requested by Astra (Katie has authorised Astra to steer routine steps here).

## Question

Does the later four-traversal footprint (v5's added-diagonal one-bit reader
`S_high`) follow the **initial reinforcement on original edges**, the **initial
placement of added diagonals**, or their **interaction**?

v5's bit starts empty because the imposed histories traverse original (base) edges
only; the late discrimination develops during subsequent evolution. We separate the
two inherited structural ingredients by crossing them.

## Constructing the four worlds

The post-history Growing worlds are **deterministic** (history has no RNG), so we
compute the two initial states once:

- history A (upper staircase): original-edge weight map `W_A`, activated-diagonal
  set `T_A`;
- history B (lower staircase): `W_B`, `T_B`.

**Asserted at construction:** every activated diagonal has weight 1 (diagonals are
never traversed during history, which uses base edges only); `|T_A| = |T_B|` and the
weight multisets of `W_A`, `W_B` are equal (A and B are exact transpose mirrors).

Four worlds, retaining the original vertices, base edges, candidate catalogue,
growth threshold and all other parameters, with inactive sets / adjacency /
activation counts initialised consistently:

1. `W_A + T_A` — **intact A**;
2. `W_A + T_B` — **crossed** (A's original weights, B's diagonal placement);
3. `W_B + T_A` — **crossed**;
4. `W_B + T_B` — **intact B**.

**Construction order.** Intact worlds are built by *replaying the history* so their
adjacency (base edges in build order, then diagonals in history-activation order)
matches v2/v5 exactly and their trajectories reproduce prior records. Crossed worlds
use a **declared deterministic order**: base edges in build order, then their
diagonal set added in **sorted edge-key order**, each at weight 1.

**Verified at construction:** all four have identical initial edge count, total
weight, and original-edge weight multiset (their spatial arrangements differ
intentionally); and all four initial added-diagonal four-traversal bits are zero
(diagonals at weight 1 < 5.5). These are **constructed interventions**, not
necessarily worlds a single natural journey would produce.

## Evolution

Reset each walker to the original probe `(4,4)`. Evolve under the **unchanged**
Growing rules (reinforce + local growth) for 10,000 steps, original checkpoints
`{0,100,200,400,1000,2000,5000,10000}`, 200 paired seeds. Each **seed is a block**
containing all four worlds; common random numbers couple the stochastic choices
(each world re-instantiates `default_rng(BASE_SEED + seed)`), **not** identical
realised paths (the graphs differ, so paths diverge). Save full edge snapshots for
future reader analyses.

**Reproduction gate:** intact-A and intact-B per-edge weight vectors must match v4's
retained snapshots (`Growing__A__cp`, `Growing__B__cp`) for every seed and
checkpoint before crossed results are interpreted.

## Readers

**Frozen primary reader** = v5's added-diagonal one-bit contrast, unchanged
orientation and threshold:

    S_high = Σ s(e) · 1[w_e ≥ 5.5]   over present added diagonals   (A-positive)

Orientation is fixed in advance, not chosen after seeing outcomes. Also report the
**added-presence contrast** `P_D = Σ s(e)` and the **original-edge contrast**
`B0 = Σ s(e) w_e` (over base edges) to describe what each initial world inherited
and how it evolved, plus **active-edge count**, **total weight**, and **saturation
headroom** `mean(6 − w)`.

## Factor comparisons (checkpoints 400, 2000, 10000)

Writing `S(W,T)` for mean `S_high` of world `(W,T)`:

- **weight effect | T_A:** `S(W_A,T_A) − S(W_B,T_A)`;
- **weight effect | T_B:** `S(W_A,T_B) − S(W_B,T_B)`;
- **topology effect | W_A:** `S(W_A,T_A) − S(W_A,T_B)`;
- **topology effect | W_B:** `S(W_B,T_A) − S(W_B,T_B)`;
- **interaction:** `[S(W_A,T_A) − S(W_B,T_A)] − [S(W_A,T_B) − S(W_B,T_B)]`.

For each contrast report the **paired mean difference in `S_high`** (paired by
seed), the **AUC** comparing its two score distributions under the declared
A-oriented sign, and **seed-block bootstrap** 95% intervals (resampling whole
four-world seed blocks). We **do not add AUCs** or treat them as causal shares; the
interaction is reported in mean `S_high` only. All comparisons are exploratory.

Report **late topology completeness** separately; **do not drop** incomplete worlds
from the primary comparisons.

## Interpretation boundaries (pre-stated)

These interventions isolate the effects of the two supplied initial arrangements
*under this model*. Later differences in visits, growth and weights are
**consequences** of the interventions, not variables to silently match away. A
**topology effect need not mean topology is where the late memory is stored**:
initial connections can shape later weights. A **weight effect need not exclude a
topology contribution.** Crossed initial conditions may interact. We do **not** claim
memory transfer, universality, intrinsic addressing, or inexhaustible growth.

## Deliverables

This note; reproduction checks; code + one-line command; snapshots and tables; a
clear four-world picture immediately after construction; a compact plot of the
primary reader over time; plain-language findings; paste-ready handback. No
random-placement control or extra variants in this run.

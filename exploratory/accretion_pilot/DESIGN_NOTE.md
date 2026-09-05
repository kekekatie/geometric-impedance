# Design note — "A world that grows without starting over" (accretion pilot)

*Written before execution. Register: speculative exploration, not a confirmatory
study and not a test of cosmology. This note fixes the rules, parameters,
observables, and expectations in advance so the run cannot be steered toward a
favourable outcome after the fact.*

- **Author of run:** Claude (Opus 4.8), at Katie's request, designed with Astra.
- **Scope isolation:** fully self-contained under `exploratory/accretion_pilot/`.
  Uses no study data, no tiling generators, no results from the sealed
  radius-saturation study or any existing scientific pipeline. Nothing here is to
  be merged or published.

---

## 0. Working question

> Can the *same* structural changes preserve distinguishable information about an
> earlier journey while increasing useful alternatives for subsequent movement?

"New possibility" means **newly available to this evolving network** — a
connection the network did not have and now does — **not** a claim that the
possibility was absent from every mathematical description of the world. The
candidate connections exist as a fixed, finite, pre-declared set; growth
*activates* members of that set. This tests activation of possible connections,
not an expanding universe and not inexhaustible novelty.

---

## 1. The world

A small, connected, undirected spatial graph with positive edge weights.

- **Vertices:** a 9×9 square grid, 81 vertices at integer positions `(row, col)`,
  `row, col ∈ {0..8}`.
- **Base edges:** 4-neighbour (rook) adjacency, 144 edges, all initial weight
  `w0 = 1.0`.
- **Candidate connections (for growth):** both diagonals of every unit cell —
  for cell with corners `(i,j),(i,j+1),(i+1,j),(i+1,j+1)` the two diagonals
  `(i,j)–(i+1,j+1)` and `(i,j+1)–(i+1,j)`. That is `8×8×2 = 128` candidates, each
  of spatial length √2 (short-range), **absent** at initialisation.

All three models start from **exactly this same** base graph and weights.

### The three models (+ one control)

| Model | Reinforces existing edges? | Activates new edges? |
|---|---|---|
| **Fixed** | no | no |
| **Reinforced** | yes | no |
| **Growing** | yes | yes (history-shaped, local rule) |
| **Growing-MatchedControl** | yes | yes (same *count*, history-independent placement) |

**Reinforcement rule (bounded, declared).** When an edge `e` is traversed once,
`w_e ← w_e + α·(w_max − w_e)` with `α = 0.5`, `w_max = 6.0`. This is a saturating
additive rule: weights strictly increase toward but never exceed `w_max`, so
weights stay positive and bounded. A base edge reaches ≈3.5, 4.75, 5.375 after
1, 2, 3 traversals.

**Growth rule (local, label-blind, declared).** For each still-inactive candidate
diagonal in a unit cell, define the cell's *local accumulated activity* as the
summed wear of its four bounding base edges, `Σ (w_e − w0)`. When this reaches
`θ_grow = 4.0`, the diagonal **activates**: it is added with initial weight
`w_init = 1.0` and thereafter reinforces like any other edge. Each activation
costs 1 unit from a growth budget `B_grow = 128` (equal to the candidate count,
so the budget is deliberately **non-binding**: growth is limited by the local
threshold, not an arbitrary cap). Growth depends **only** on local current edge
weights — never on the A/B label, an external journey log, the walker's endpoint,
or the outcome we hope to see. We do **not** require preservation of any spectral
moment.

Rationale for `θ_grow = 4.0`: a single fully-worn (3-pass, excess ≈4.375) base
edge is enough to sprout the diagonals of the cells it borders, so shortcuts
crystallise *along* a heavily-travelled route. Chosen a priori for "one worn edge
seeds a local shortcut", not tuned to any result.

---

## 2. Two matched histories

Two distinct early journeys on **existing base edges only**, from `S=(0,0)` to
`E=(8,8)`:

- **History A (upper staircase):** alternate Right, Up — stays on/above the main
  diagonal (`row ≤ col`). Vertices `(0,0),(0,1),(1,1),(1,2),(2,2),…,(8,8)`.
- **History B (lower staircase):** alternate Up, Right — the exact transpose
  mirror `(i,j)↔(j,i)`, stays on/below the diagonal (`row ≥ col`).

Both have **length 16 edges**, the **same start and end**, and are related by the
grid's transpose symmetry — matched in length, endpoints, and spatial symmetry.
Both pass **through the probe (4,4)**, so the probe sits in the worn zone for both
while remaining on the symmetry axis (neutral to A vs B). These are **imposed**
histories (a controlled intervention), not spontaneously generated. Each history
edge is traversed `n_passes = 3` times, reinforcing on each pass and (for Growing)
allowing growth.

Both histories are applied separately to independent copies of each model. After
history, the walker is **reset to the probe (4,4)**; both resulting worlds then
receive the **same** subsequent stochastic evolution.

**Subsequent stochastic evolution.** A weighted random walk from the probe: at
each step move to a present neighbour with probability proportional to edge
weight. `T_sub = 400` steps. Each step applies the model's own rule (Fixed: no
change; Reinforced: reinforce the traversed edge; Growing: reinforce + local
growth; Control: reinforce + matched history-independent activations). Because the
walk starts from the symmetric probe with a fresh RNG, subsequent reinforcement is
on-average symmetric and tends to **erode** the imposed asymmetry — so durability
of memory is a genuine question, not a foregone conclusion.

**Seeds and pairing.** `N = 200` independent paired seeds (≥100, and cheap).
Pairing = **common random numbers**: for seed `k`, the A-world and the B-world of
the *same model* are evolved with an RNG seeded identically (`base + k`), so the
only difference between the paired A and B runs is the imposed history, not the
noise realisation. Reported.

**Checkpoints.** Measurements saved immediately after history (`step 0`) and at
`steps 100, 200, 400` of subsequent evolution.

---

## 3. Memory readout (no journey log consulted)

The reader may inspect **only** the current graph and weights — no visit
counters, no walker endpoint, no stored paths. One fixed, transparent,
symmetry-based structural readout, specified here before running:

> `M = Σ_edges sign(mj − mi) · w(e)`, where `(mi, mj)` is the edge midpoint
> `(row, col)`. Edges on the upper-right side of the main diagonal (`col > row`)
> contribute `+w`; lower-left (`row > col`) contribute `−w`; on-axis contribute 0.
> The sum runs over all present edges (base and grown).

Under History A the upper side is worn/grown → `M > 0`; under B → `M < 0`; the
Fixed model stays symmetric → `M ≈ 0` (the no-structural-memory control). Known
vertex positions are used to define the axis: **this is memory with external
coordinates, not intrinsic self-addressing** — acknowledged.

**Distinguishability** (paired, no fitted decoder): per checkpoint we report
(i) the fraction of seed pairs with `M_A > M_B` (0.5 = chance), (ii) the paired
effect size `d_z = mean(M_A − M_B) / sd(M_A − M_B)`, and (iii) the rank AUC of
`{M_A} ∪ {M_B}` labelled by history. No decoder is fitted, so no train/test split
is needed; if one were, whole seed pairs would be split.

---

## 4. Opportunity (measured separately, at the probe)

From the fixed probe `P = (4,4)`:

- **Structural access:** number of vertices reachable from `P` within a **4-hop**
  budget over *present* edges (unweighted BFS; `P` excluded from the count).
- **Effective alternatives (path-diversity):** `exp(H)` where `H` is the Shannon
  entropy (nats) of the distribution over all length-`L=4` weighted random walks
  from `P`, computed as `H = Σ_{t=0}^{L−1} Σ_v π_t(v)·h(v)` with `π_0 = δ_P` and
  `h(v)` the entropy of `v`'s weight-proportional next-step distribution.
  `exp(H)` = effective number of distinct 4-step routes. This separates "edges
  exist" from "weight is funnelled through one route": reinforcement that
  concentrates weight lowers `exp(H)` even while edges remain.

Both reported as absolute values and as change relative to each model's own
initial state. Also reported at every checkpoint: **edge count** and **total edge
weight** (adding resources makes some gains unsurprising, so resources are
tracked explicitly).

**Matched-resource control.** `Growing-MatchedControl` uses identical
reinforcement and identical histories, but at each checkpoint it holds the *same
cumulative number of activated diagonals* as the Growing model (matched per seed
and per history), placed **uniformly at random over the candidate set,
independently of history**, each with `w_init = 1.0`. **What is matched:** count
of added edges and their initial weight. What is *not* forced to match: the fully
evolved total weight (reported for all models so any residual is visible) and the
placement (deliberately history-blind). Expectation: high opportunity, low memory
— isolating "opportunity needs only added resources" from "memory needs
history-shaped placement".

---

## 5. Invariants checked (before trusting any result)

- Fixed model: `M ≈ 0`, edge count constant, total weight constant, effective
  alternatives constant at every checkpoint.
- Zero-history sanity: with no imposed history, all models are symmetric (`M ≈ 0`).
- Weights stay in `(0, w_max]`; graph stays connected; grown edges come only from
  the candidate set; activation count ≤ budget.
- Total weight is non-decreasing under reinforcement.

---

## 6. Expectations (pre-registered; mixed/negative outcomes are equally useful)

*Guaranteed by construction* (so **not** the interesting part): immediately after
history, Reinforced and Growing show `M` well separated by history — reinforcement
of the worn side builds this in. Growing and the Control gain edges and structural
access — added edges buy reachability by definition.

*Genuinely uncertain* (the actual questions):
1. **Durability:** does `M`-separation survive 400 steps of symmetric-on-average
   subsequent evolution, and does Growing retain it *better or worse* than
   Reinforced (extra edges could either lock in the asymmetry or wash it out)?
2. **Concentration vs alternatives:** does reinforcement *reduce* effective
   alternatives (funnelling) while structural access is flat, and does growth
   *restore* effective alternatives, or do the new edges simply funnel too?
3. **Coexistence vs trade-off:** does the Growing model hold memory *and* raise
   opportunity at once, or does one come at the other's expense?
4. **Control contrast:** does history-blind matched growth reproduce Growing's
   opportunity while showing `M ≈ 0` — i.e., is memory attributable to
   history-shaped placement rather than to added resources alone?

No prediction is treated as a target. We run once at the parameters above, check
invariants and the no-memory control, and report whatever happens. We do not
search parameters for a favourable result; any later change will be labelled and
the first results retained.

---

## 7. What this pilot deliberately does **not** claim

Memory right after reinforcement is partly built into the rule; more short routes
after adding edges may also be built in. A positive result here is **not**
emergent consciousness, physical time, E8 evidence, or a universal accretion law.
It is a small, transparent demonstration (or failure) about durability,
concentration versus useful alternatives, and whether memory and opportunity
coexist in one toy world.

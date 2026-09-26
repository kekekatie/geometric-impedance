# Surprise versus consequence: what should a learning memory keep?

*Pre-registration, **Part A only**. **Status: DRAFT v2, awaiting Katie's final OK.** No code for
this study exists yet. Once approved, this file is frozen; any change before the first run is
listed at the bottom with its reason. Results will be reported against these predictions,
whichever way they fall.*

*v2 follows a review by Astra (via Katie). The changes are listed at the end: new controls that
isolate the mechanism, an exact common scoring basis, softer claims about the inspiration,
tightened statistics, and Part B moved to a separate future pre-registration.*

## The question

A memory with limited room must decide what to keep. One family of designs keeps what is
**surprising** (large prediction error), in the spirit of Titans (Behrouz et al. 2025) and
prioritized experience replay (Schaul et al. 2016). The comparator here is only *inspired by*
those systems and implements neither. Titans learns gradient-based memory updates with momentum
and forgetting; prioritized replay selects stored transitions for replay by TD error.

The alternative tested is to keep what can **change a decision**. It is an operational
translation *inspired by* the transmission paper's fork law (a difference lasts only where the
future can still split). It is **not** a consequence of that theorem: the paper's forks are
absorption branches of a Markov chain, and the forks here are two available actions. The related
decision-theoretic idea is the value of information (Howard 1966). A failure here would reject
this heuristic in this setting, not a general transfer principle.

**The decisive question** (after Astra): does scoring by *decision margin* add value beyond a
simple **relevance filter** that ignores situations where nothing can be decided? The design
separates three possible outcomes:
- **(i)** the margin score helps beyond the relevance filter;
- **(ii)** the relevance filter explains the whole gain;
- **(iii)** selective retention harms estimation.

## The world

- **Situations.** `S = 200` of them. Each is **forced** (one action) with probability `1 − f`,
  or a **fork** (two actions) with probability `f`.
- **Reward distributions** (the conditions below):
  - **Primary, `t5`:** forced `μ ~ 2·t(df = 5)`, which is heavy-ish tailed with finite variance.
  - **Stress test, `t2`:** forced `μ ~ 2·t(df = 2)`, infinite variance. Its MSE comparisons are
    reported only as medians and are not used for any prediction.
  - **Matched, `norm`:** forced `μ ~ N(0, 1)`, the same scale as the fork actions. This
    separates the effect of the *fraction* of forced situations from the effect of their *tails*.
  - Forks in every condition: `μ₁ ~ N(0, 1)`, `μ₂ = μ₁ + δ`, `δ ~ N(0, 0.5²)`.
- **The stream.** `T = 2000` observations, stationary and uniform: a situation drawn uniformly,
  an action uniformly from its actions, and a reward `r = μ + ε`, `ε ~ N(0, 1)`.
- **Pairing.** One seed fixes both the world and the stream. Every rule sees exactly the same
  world and the same stream for a given seed. **`N = 100` seeds per condition.**

## The agent's estimator

Beliefs come only from memory. For each situation and action with `n` stored rewards summing to
`Σ`, the estimate is `Q = Σ / (n + 1)`: the normal–normal posterior mean with prior `N(0, 1)` and
noise variance 1. **Caveat, stated in advance:** rewards retained *selectively* (for example by
residual) make this a biased estimator. It is the stipulated agent's estimator, not a calibrated
posterior. Outcome (iii) exists to catch exactly this.

## Memory and eviction (common to all rules)

- Capacity `K = 100` observations. Until full, everything is stored.
- Once full, at each arrival the **candidate pool** is the `K` stored items plus the newcomer.
  Each item `x` in the pool gets its score computed **leave-one-out**, from beliefs built from
  `pool − x`. Stored items and the newcomer are treated identically, and no item is scored
  against beliefs that already include it.
- The lowest-scoring item is evicted. **Ties are broken uniformly at random** with a seeded
  generator.

## The rules (Part A)

With leave-one-out quantities for item `x = (s, a, r)`: `Q_a` and `n_a` for its own action, and,
in a fork, `m = |Q₁ − Q₂|` (the absolute decision margin, both estimates leave-one-out):

| rule | what it keeps |
|---|---|
| **recency** | the latest `K` arrivals |
| **random** | reservoir sampling: a uniform random `K`-subset of the stream so far. *(Fresh random scores at every eviction would be a different, recency-weighted policy; not used.)* |
| **surprise** | score `|r − Q_a|` |
| **fork-only random** *(relevance-filter control)* | reservoir sampling over **fork observations only**; forced observations are never stored |
| **fork-only surprise** *(relevance-filter control)* | score `|r − Q_a|` in forks; forced observations get score −∞ (evicted first) |
| **margin** (decision-sensitive surprise) | forced: −∞. Forks: `|ΔQ_a| / (m + 0.1)`, where `|ΔQ_a| = |r − Q_a| / (n_a + 2)` is exactly how far adding `x` moves the estimate |
| **clairvoyant greedy** *(comparator, not a bound)* | evicts the item whose leave-one-out removal changes the **true** regret of its situation the least. It uses the truth, but greedy eviction is not guaranteed optimal, so it is reported without any bound claim. |

A known weakness of `margin`, stated in advance: it rewards *movement* of the margin in either
direction, including noise that moves the decision the wrong way. It is a heuristic, not expected
regret reduction.

## Measures (after the stream)

- **Decision regret, per world:** the mean over fork situations of `μ_best − μ_chosen`, with
  `chosen = argmax Q`. Ties give the mean regret of the tied actions (the expected value of a
  random tie-break). A world with no forks is excluded and counted; at `S = 200` with `f ≥ 0.1`,
  none is expected.
- **Fact error, per world:** the mean over all situation–action pairs of `(Q − μ)²`.
- **Relative improvement of rule A over rule B:** `1 − mean_seeds(R_A) / mean_seeds(R_B)`.
- **Uncertainty:** a paired bootstrap over seeds (10,000 resamples, percentile 95% CI). Each seed
  (world plus stream) is one resampling unit.
- **Wording convention.** "*Improves by ≥ X%*" means the point estimate is at least X% **and** the
  95% CI of the paired difference excludes zero. It does **not** mean the CI establishes at least
  X%. Where the CI's lower end also exceeds X%, that is reported separately.

## Conditions

- **Primary:** `t5`, `f = 0.3`.
- **Sweeps:** `f ∈ {0.1, 0.3, 0.5, 0.9}` under both `t5` and `norm`.
- **Stress:** `t2` at `f = 0.3`.

## Predictions (primary condition unless stated)

- **P1, the decisive one (outcome (i) versus (ii)).** `margin` has lower regret than
  **fork-only surprise**, by ≥ 10%. *My honest confidence: about 55%.* Focusing on close calls
  and under-sampled actions should help, but the relevance filter may already carry most of the
  gain.
- **P2, the relevance filter.** Both fork-only controls have lower regret than plain `surprise`,
  by ≥ 20%.
- **P3.** `margin` has lower regret than plain `surprise`, by ≥ 20%.
- **P4, the fact–decision split.** Plain `surprise` has lower fact error than `margin`, which
  never stores forced facts. *(Outcome (iii) check: plain `surprise` versus `random` on fact error
  is reported with no prediction; selective retention could make surprise worse than random.)*
- **P5, where the effect lives.** `margin`'s relative advantage over plain `surprise` is smaller
  at `f = 0.9` than at `f = 0.3`, under both `t5` and `norm`. At `f = 0.3` it is smaller under
  `norm` than under `t5`: less surprising forced situations waste less memory.
- **P6.** `margin` has lower regret than `random` by ≥ 10%. *(Plain `surprise` versus `random`:
  reported, no prediction.)*
- **P7.** `recency` and `random` are within 5% of each other on regret. The stream is stationary
  and uniform, so this design gives no special advantage to early information and does **not**
  test a context-window "cliff". That needs a non-stationary or early-information design, parked
  for later.

## Parked (separate pre-registrations, later)

- **Part B**, a fast-weight version. It needs its own full specification: key dimension, value
  representation, readout, initialisation, gate mapping, and an online write-budget rule that uses
  no future information. Equal total gate strength alone does not equalise effective learning or
  interference.
- **Sleep**: replay-based consolidation (Complementary Learning Systems; McClelland, McNaughton &
  O'Reilly 1995).
- **A cliff test**: a non-stationary or early-information stream where recency's weakness can
  actually show.

## Changes from v1 (after Astra's review), all made before any code existed

1. **Added** fork-only random and fork-only surprise, to isolate the margin score from the
   relevance filter. The decisive prediction is now P1: margin versus fork-only surprise.
2. **Renamed** the fork score "margin (decision-sensitive surprise)" and gave its exact form. Its
   close kinship with surprise is acknowledged, and its known weakness (it rewards movement in
   either direction) is stated.
3. **Made** scoring leave-one-out over a common pool of `K + 1` items, with ties broken at random.
   `random` is now reservoir sampling.
4. **Softened** the framing. The transmission link is inspiration, not consequence. The surprise
   comparator is inspired by Titans and prioritized replay, not an implementation of either.
5. **Statistics:** `t5` is primary and `t2` a stress test. The `norm` condition separates fork
   fraction from tail weight. Seeds are paired, with a paired bootstrap. Regret aggregation, ties,
   no-fork worlds and relative improvement are defined, and so is the "≥ X%" wording.
6. **The recency prediction** (P7) no longer claims a context-cliff explanation. "Random is worse"
   is a substantive prediction, not sanity. The oracle is renamed "clairvoyant greedy comparator",
   with no bound claim.
7. **Part B moved** to a separate future pre-registration. Sleep stays parked.
8. **Added** the estimator-bias caveat and outcome (iii).

## Changes before the first run

*(none yet)*

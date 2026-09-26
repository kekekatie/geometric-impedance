# Surprise versus consequence: what should a learning memory keep?

*Pre-registration. **Status: DRAFT, awaiting Katie's review.** No code for this study exists yet.
Once Katie approves, this file is frozen; any change made before the first run is listed at the
bottom with its reason. Results will be reported against these predictions, whichever way they
fall.*

## The idea in one paragraph

A memory with limited room must decide what to keep. A leading recent design (Titans, Behrouz et
al. 2025) keeps what is **surprising**: large prediction error. So does prioritized experience
replay in reinforcement learning (Schaul et al. 2016). The transmission paper ("When the past
matters, II") suggests a different filter. There, a difference lasts only where the future
**forks**: where something downstream can still go one way or the other. A strongly marked
difference with no fork to hold it washes out, like pair (22,26). The alternative rule is to keep
what can still **change a future decision**. That idea is not new in decision theory: it is the
value of information (Howard 1966). What we test is whether it beats surprise as the keep-rule of
a capacity-limited learning memory, where the two come apart, and by how much.

## The world

- **Situations.** `S = 200` of them. Each situation is either:
  - **forced** (one action: a single sink, nothing to decide), with probability `1 − f`; or
  - a **fork** (two actions), with probability `f`.
- **True values.**
  - Forced situations: heavy-tailed, `μ ~ 2·t(df = 2)`. They are often wildly surprising, and
    genuinely so: the facts are *true*, just irrelevant to any decision.
  - Forks: `μ₁ ~ N(0, 1)` and `μ₂ = μ₁ + δ`, `δ ~ N(0, 0.5²)`. Close calls, quiet facts.
- **The stream.** `T = 2000` observations arrive one at a time. Each observation is a situation
  drawn uniformly, an action drawn uniformly from its actions, and a reward `r = μ + ε`,
  `ε ~ N(0, 1)`.
- **The agent's beliefs** come only from what is in memory: per situation and action, the mean of
  the stored rewards shrunk towards a prior of 0 (a normal–normal posterior, prior variance 1,
  noise variance 1).

## The memory and the keep-rules

**Part A: slot memory.** Capacity `K = 100` observations (5% of the stream). When the memory is
full, each rule scores the newcomer and every stored item on the current beliefs, and evicts the
lowest score. Every rule gets exactly the same budget.

| rule | score of an observation |
|---|---|
| **recency** (the context-window cliff) | its arrival time: keep the latest `K` |
| **random** | random |
| **surprise** (Titans / prioritized replay) | the prediction error `|r − r̂|` under current beliefs |
| **fork** (consequence, ours) | 0 in a forced situation; in a fork, how much keeping it moves the decision margin, `|Δm| / (|m| + 0.1)`, where `m = Q̂₁ − Q̂₂` |
| **oracle** (upper bound, not a contender) | the true reduction in future decision regret |

Scores are recomputed on current beliefs at each eviction.

**Part B: fast-weight memory** (closer to how Titans is built). The same world and stream. A
linear associative memory, `W += g · v kᵀ`, with random unit keys per situation and action. Each
rule sets the write gate `g` from its score, with the gates normalised so that every rule has the
same total write strength. Interference replaces eviction as the capacity limit.

## Measures (in a test phase after the stream)

- **Decision regret:** in every fork situation, the value lost by choosing with current beliefs
  rather than knowing the truth. Forced situations have zero regret by definition.
- **Fact error:** mean squared error of the belief `Q̂` against the true `μ`, over *all*
  situation–action pairs, forced included.

Parameters: 50 seeds per condition. Sweep `f ∈ {0.1, 0.3, 0.5, 0.9}`, with default `f = 0.3`.

## Predictions

- **P1 (the main one).** At `f = 0.3`, in both Parts A and B, **fork has lower decision regret
  than surprise**, by at least 20% (relative), with a 95% bootstrap CI that excludes zero.
- **P2 (the dissociation).** At `f = 0.3`, **surprise has lower fact error than fork**. Surprise
  remembers more *facts*, fork makes better *decisions*: strongly marked but forkless, like
  (22,26).
- **P3 (where the difference lives).** Fork's regret advantage over surprise shrinks as `f` grows.
  At `f = 0.9`, almost everything is a fork and the two rules are within 10% of each other.
- **P4 (the cliff).** Recency has the worst decision regret of the four real rules at `f = 0.3`.
  Keeping only the latest items throws away whatever mattered, if it came early.
- **P5 (sanity).** Oracle ≤ every rule on regret, and random is worse than both fork and surprise
  on regret.

## What would change my mind, or surprise me

- If surprise beats fork on regret (P1 fails), the fork law does not transfer as a keep-rule,
  at least in this form. That is a finding worth publishing too.
- If fork wins only because forced situations are so extreme, P3 and the sweep should show it.
  Honest robustness check: I will also report `df = 5` (lighter tails) as a secondary condition,
  with no prediction attached.

## Honest limits, stated before running

- This is a designed toy world. The dissociation between surprise and consequence is built in
  deliberately, and the question is *how large* it is and whether an online, belief-based fork
  score captures it. The world is not meant to be representative of real data.
- The fork score needs a belief model and the knowledge of which actions exist. Real systems have
  to estimate both.
- Planned next (not in this study): a "sleep" phase of replay-based consolidation from a fast
  buffer into a slow store (Complementary Learning Systems; McClelland, McNaughton & O'Reilly 1995).

## Changes before the first run

*(none yet)*

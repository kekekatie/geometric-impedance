# Round 3: a crowd-aware memory (Katie's "wisdom of crowds")

*Pre-registration. **Status: FROZEN on 2026-09-26, before any round-3 code existed.** Katie
approved.*

## Where this comes from

An exploratory diagnostic (README, "Katie's puzzle questions") found two things:
- The clairvoyant comparator keeps fork memories with **typical** noise (`|r − μ|` about 0.78,
  close to the 0.80 expected for one unit of Gaussian noise). It keeps a representative crowd.
- Margin and surprise keep memories with nearly **twice** the typical noise, and margin's wrong
  decisions are usually confidently wrong.

**Katie's hypothesis:** the missing ingredient is the wisdom of crowds. Prefer representative
memories, not loud ones.

## Setting

As in rounds 1 and 2:
- `t5` forced values, `f = 0.3`, `K = 100`;
- a common `K + 1` pool with leave-one-out scoring and random ties;
- the estimator `Q = Σ / (n + 1)`;
- forks **known** (as for the round-1 margin rule, isolating the new ingredient);
- paired bootstrap (10,000 resamples) and the "≥ X%" convention.

Streams: **stationary, `T = 2000`** (primary) and **stationary, `T = 600`** (secondary).
**Fresh seeds 20000–20099.**

## Rules

With leave-one-out quantities for item `x = (s, a, r)` in a fork: `Q_a` and `n_a` for its own
action, the margin `m = |Q₁ − Q₂|`, the residual `z = |r − Q_a|`, and the predictive variance
`v = 1 + 1/(n_a + 1)` (the spread a *typical* new reward should have, given the agent's own
estimator):

| rule | fork score (forced: −∞) |
|---|---|
| surprise, fork-only surprise, margin | as before (re-run on the new seeds) |
| **close calls only** *(control)* | `1 / ((n_a + 2)(m + 0.1))`: keeps memories about under-sampled close calls, **ignoring** how big their residual is |
| **crowd-aware margin** *(new)* | `z·exp(−z² / 2v) / ((n_a + 2)(m + 0.1))`: margin's relevance, but the residual term **peaks at typical size** (`z = √v`) and falls away for extreme memories |
| clairvoyant greedy | as before (a comparator; no bound claim) |

The crowd-aware term uses only the agent's own beliefs and the known noise level, never the truth.

## Measures

As before (regret, fact error), plus two **mechanism measures**, per world:
- **kept noise:** the mean `|r − μ|` over kept fork memories;
- **forks decided right:** the fraction of forks where the sign of `Q₁ − Q₂` matches the truth.

## Predictions (T = 2000 unless stated)

- **C1 (the headline).** Crowd-aware margin beats margin by ≥ 10% on regret. *Honest confidence
  about 60%.*
- **C2 (mechanism).** Crowd-aware margin keeps less noisy memories than margin: lower kept noise,
  with the paired CI excluding zero.
- **C3 (mechanism).** Crowd-aware margin decides more forks right than margin: a higher fraction,
  with the paired CI excluding zero.
- **C4 (does *preferring typical* matter, or just *not preferring loud*?).** Crowd-aware margin has
  lower regret than close-calls-only: point estimate > 0 with the paired CI excluding zero.
  *Honest confidence about 50%.*
- **C5 (secondary, T = 600).** Crowd-aware margin has lower regret than margin: point estimate
  > 0 with the paired CI excluding zero.

Reported without prediction: close-calls-only against margin, every rule's mechanism measures,
and the share of the margin-to-clairvoyant gap that crowd-aware margin closes.

## Changes before the first run

*(none yet)*

# Surprise versus consequence, round 2: the principled rival, inferred forks, and the cliff

*Pre-registration. **Status: FROZEN on 2026-09-26, before any round-2 code existed.** Katie
approved going ahead in advance. The design was self-reviewed against the checklist from Astra's
round-1 review: controls isolate the mechanism, scores are exact and leave-one-out, inspiration is
kept separate from claims, statistics are paired, and the wording is precise. Any change before
the first run is listed at the bottom.*

Everything not stated here is **as in round 1** ([`PREREGISTRATION.md`](PREREGISTRATION.md)):
- the world generator (`t5` forced values, fork values `μ₁ ~ N(0,1)`, `μ₂ = μ₁ + δ`,
  `δ ~ N(0, 0.5²)`);
- the estimator `Q = Σ / (n + 1)`;
- capacity `K = 100`, a common `K + 1` pool, leave-one-out scoring, ties at random;
- the regret and fact-error definitions;
- the paired bootstrap (10,000 resamples) and the "improves by ≥ X%" convention (point estimate
  ≥ X% **and** the paired-difference CI excludes zero).

All conditions use `f = 0.3` and `N = 100` fresh seeds. None is reused from round 1.

## Why round 2

After round 1 we found the prior art: **Mattar & Daw (2018)** prioritise memory access by
**gain × need**, where gain is the improvement in the agent's own choices. A reviewer's first
question will be whether the quick margin heuristic is as good as that principled score. Round 1
also *told* the margin rule where the forks were, and its stationary stream could not test the
context-window "cliff". Round 2 addresses all three.

## New rules (added to the round-1 set, which is re-run)

With leave-one-out beliefs `Q⁻` (the pool without item `x`) and full-pool beliefs `Q⁺` (the pool
with `x`), in item `x`'s situation:

| rule | score |
|---|---|
| **gain (softmax)** *(Mattar–Daw-style, adapted to retention)* | `Σₐ π⁺(a) Q⁺(a) − Σₐ π⁻(a) Q⁺(a)`, where `π = softmax(β Q)` with **β = 5**. This is how much better the agent's own policy is, judged by its own current beliefs, for keeping `x`. Forced situations have one action and so score exactly 0; no fork label is needed. |
| **gain (greedy)** *(reported, no prediction)* | the same with an argmax policy (ties split evenly). It is zero unless keeping `x` flips the choice. |
| **margin, inferred forks** | the round-1 margin score, but the rule is **not told** which situations are forks. A situation counts as a fork once two different actions have been observed there in the stream so far: a small structural table, "which doors exist". Otherwise it is treated as forced (−∞). |

Mattar–Daw's *need* term (expected future visits) is uniform in the stationary and drift streams
and is not used. This is a deliberate simplification, stated in advance: in the early-only stream,
need is *not* uniform, and no rule here uses it.

## Streams (`T = 2000` unless stated)

| stream | what changes |
|---|---|
| **stationary** | as in round 1 (a replication on fresh seeds) |
| **stationary, short** | `T = 600`: fewer visits per situation, a harder test of inferring forks |
| **early-only** *(the cliff test)* | half of the situations, chosen at random, appear **only in the first half** of the stream; the rest appear throughout. The test covers all situations. The facts exist only early, which is exactly what a context window drops. |
| **drift** *(a changing world)* | at `t = T/2`, half of the fork situations, chosen at random, get a freshly drawn `δ`: the better action may change. The test uses the **post-change** values. |

## Predictions

- **R1 (replication, stationary).** Margin beats surprise by ≥ 20% and fork-only surprise by
  ≥ 10%.
- **R2 (margin versus the principled rival, stationary).** Gain (softmax) and margin are within
  ±10% of each other on regret: `|1 − R_gain / R_margin| ≤ 0.10`. *Honest confidence about 50%.*
  Gain is principled, but it scores a single noisy observation by its effect on the agent's own
  beliefs, and I do not know which effect dominates.
- **R3 (inferred forks).**
  - At `T = 2000`: margin-inferred is within 5% of margin, since forks are learned quickly.
  - At `T = 600`: margin-inferred still beats surprise by ≥ 10%.
- **R4 (the cliff, early-only).**
  - Recency has the **highest regret of all rules**, and is worse than random by ≥ 30% (point
    estimate, with the paired CI excluding zero).
  - Margin beats surprise by ≥ 20%.
- **R5 (drift).**
  - Recency beats random on regret: the point estimate is positive and the paired CI excludes
    zero. In a changing world, fresh beats uniform.
  - Margin still beats surprise by ≥ 10%. *Honest confidence about 60%:* all of margin's beliefs
    mix stale and fresh data.
- **R6 (fact–decision split, stationary).** Surprise has the lowest fact error of all rules
  except the clairvoyant comparator, and margin's regret is lower than surprise's.

## Reported without predictions

- Gain (greedy) everywhere.
- Gain (softmax) against surprise and against fork-only surprise.
- Every rule in every stream.
- The clairvoyant greedy comparator, as in round 1: no bound claim.

## Honest limits, stated in advance

- β = 5 is one choice, made without tuning. Gain could do better or worse at other temperatures.
- None of the rules has a mechanism for forgetting stale beliefs, so drift tests robustness, not
  adaptation.
- It is still a designed toy world.

## Changes before the first run

*(none yet)*

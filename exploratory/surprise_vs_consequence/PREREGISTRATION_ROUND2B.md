# Round 2b: separating *not discovering* a fork from *discarding evidence before discovery*

*Pre-registration. **Status: FROZEN on 2026-09-26, before any round-2b code existed.** This round
follows Astra's review of the round-2 results (via Katie). Katie approved continuing. The worlds
and streams are **the same as round 2** (seeds 10000–10099, stationary `T = 2000` and
`T = 600`), so the new rules are paired with the round-2 rules on identical data.*

## Why

Round 2's inferred-fork margin fell short of its predictions (R3a, R3b). Astra pointed out that
the shortfall mixes two separate difficulties:
- **(D) discovery failure:** a fork whose second action is never observed cannot be recognised.
  Measured, and confirmed independently by both of us: **1.45%** of true forks are never
  recognised at `T = 2000`, and **39.33%** at `T = 600`.
- **(E) premature eviction:** before recognition, a fork's observations score lowest and are
  evicted. This is my proposed mechanism, *not yet measured*.

Astra also noted that the inferred rule treats "unknown" as "irrelevant", and that the ideal
control is surprise facing *the same* discovery problem.

**Memory accounting (Astra):** the inferred rules use 100 reward-observation slots **plus** a
persistent action-discovery table (which actions have ever been seen in each situation). The
discovery history itself is never forgotten.

## New rules (the round-2 rules are re-used unchanged, with the same seeds)

| rule | fork knowledge | score |
|---|---|---|
| **fork-only surprise (inferred)** | discovered forks only, same discovery as margin (inferred) | `|r − Q_a|` if discovered, else −∞ |
| **margin (eventual-discovery oracle)** | knows **from the start** which forks *will* be discovered by the end of the stream; never-discovered forks are treated as forced | the round-1 margin score if the situation is a fork that will be discovered, else −∞ |
| **margin (inferred + allowance)** | an unresolved situation (only one action seen so far) is treated as a *possible* fork whose unseen action sits at the prior (`Q = 0`, `n = 0`) | discovered forks: the margin score; unresolved: `(|r − Q_a| / (n_a + 2)) / (|Q_a − 0| + 0.1)`. Forced situations stay unresolved for ever and therefore compete too. |

**The decomposition** (regret, on paired worlds):
- `margin (oracle)` → `margin (eventual)`: the cost of **(D)** never-discovered forks;
- `margin (eventual)` → `margin (inferred)`: the cost of **(E)** evidence discarded before
  discovery.

## Predictions

- **B1a.** At `T = 2000`, margin (inferred) beats fork-only surprise (inferred) by ≥ 10%. Does the
  margin weighting still help when both face the same discovery problem?
- **B1b.** At `T = 600`, margin (inferred) has lower regret than fork-only surprise (inferred):
  point estimate > 0 and the paired CI excludes zero.
- **B2a.** At `T = 2000`, the premature-eviction cost (E) is larger than the discovery cost (D),
  in absolute regret.
- **B2b.** At `T = 600`, the discovery cost (D) is larger than the premature-eviction cost (E).
- **B3.** At `T = 600`, margin (inferred + allowance) has lower regret than margin (inferred):
  point estimate > 0 and the paired CI excludes zero. *(At `T = 2000`: reported, no prediction.
  The allowance also spends memory on forced situations.)*

Conventions as in rounds 1 and 2: paired bootstrap over seeds, 10,000 resamples.

## Changes before the first run

*(none yet)*

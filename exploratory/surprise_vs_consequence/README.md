# Surprise versus consequence: what should a learning memory keep? (Part A)

A memory with room for only 5% of what it sees has to choose what to keep. Some designs keep what
is **surprising**. The alternative tested here keeps what can **change a decision**, a heuristic
inspired by the transmission paper's fork law (inspiration, not consequence). Pre-registered
([`PREREGISTRATION.md`](PREREGISTRATION.md)): drafted, revised after Astra's review, and frozen
with Katie's approval at commit `e110a11` before any code existed. One interpretation was logged
before the first run.

![results](figures/svc.png)

## Scorecard (primary condition: `t5`, `f = 0.3`; 100 paired worlds; paired bootstrap)

| | prediction | result | |
|---|---|---|---|
| **P1** *(decisive)* | margin beats **fork-only surprise** by ≥ 10% | **+14.1%** (CI +10.4% to +17.7%) | **held**, and the CI's lower end also clears 10% |
| P2a | fork-only random beats surprise by ≥ 20% | +8.1% (CI +4.4% to +11.5%) | **failed**: better, but not by 20% |
| P2b | fork-only surprise beats surprise by ≥ 20% | +34.7% | held |
| P3 | margin beats surprise by ≥ 20% | **+43.9%** | held |
| P4 | surprise has lower **fact** error than margin | 0.82 vs 4.19 | held |
| P5 | margin's edge shrinks as forks become common, and is smaller with matched tails | t5: 50 → 44 → 35 → 12%; norm: 46 → 39 → 30 → 10% | held |
| P6 | margin beats random by ≥ 10% | +48.8% | held |
| P7 | recency ≈ random (stationary stream: no cliff test) | +2.4% | held |

**7 of 8 held.** The decisive one, P1, held. That means outcome **(i)**: the decision-margin
score adds real value **beyond** the relevance filter.

## What it means

- **Keeping what can change a decision beats keeping what is surprising**, by 44% less regret in
  the primary condition. It also beats the fairer control that is told where the forks are, by
  14%. It is not just "don't waste room on forced situations".
- **The gain comes in layers** *(exploratory reading of the primary condition, not
  pre-registered)*. Regret goes from 0.170 (surprise) to:
  - 0.156 with the relevance filter alone;
  - 0.111 with the filter plus surprise inside forks;
  - 0.096 with the margin score;
  - 0.048 for the clairvoyant comparator, which shows how much room is left.

  All three ingredients contribute, and P2a failing shows that the filter alone is the smallest.
- **With almost everything a fork (`f = 0.9`), the filter is useless**, but margin still beats
  fork-only surprise: 0.139 against 0.153, about 9%. That is the margin effect on its own.
  *(Exploratory.)*
- **Facts and decisions come apart** (P4). Plain surprise knows the most facts (fact error 0.82,
  the lowest of all), and makes worse decisions than the margin rule. A memory can be well
  informed and still choose badly: strongly marked but no fork to hold it, the (22,26) story in a
  different setting.
- **Outcome (iii) did not occur for surprise.** Its selective retention did not wreck its
  estimates: its fact error is far *below* random's (0.82 against 3.27). The rules that store
  only forks have the worst fact error, by design.
- **Recency ≈ random**, as expected for a stationary stream. The context-window cliff needs its
  own experiment (parked).

## Prior art: found after the run, and important

The core idea, prioritising memories by how much they would improve **decisions** rather than by
surprise, is **not new**:

- **Mattar & Daw (2018)**, *Prioritized memory access explains planning and hippocampal replay*
  (Nature Neuroscience). A normative theory in which the brain replays memories by
  **gain × need**. *Gain* is how much better the resulting choices would be, which is close kin to
  our margin score. That work is about which memory to *replay*, not which to *keep* under a
  capacity limit, but it is the paper this work must cite first.
- **Value of experience / expected value of backup.** The RL literature on prioritized replay
  defines the ideal priority as the increase in reward from an update, with TD error (surprise)
  as a proxy for it.
- **Selective experience replay**, which chooses what a limited buffer keeps (by surprise,
  reward, coverage and so on), is an active line of work. Surprise-driven retention is current
  in LLM continual learning (for example SuRe, 2025), and in Titans-style memory.

**What is (modestly) ours:** a pre-registered, controlled comparison **for retention under a
capacity limit**. It includes controls that separate relevance filtering from decision-margin
weighting (P1), and it shows the fact-versus-decision dissociation (P4). The result supports the
Mattar–Daw view in a setting (what to *keep*) where surprise-based rules are currently popular.
The next honest step is to compare our margin heuristic with a principled Mattar–Daw-style
**gain** score.

## Honest limits

- A **designed toy world**, in which surprise and consequence were built to be able to come
  apart. The results show *how large* the gap is and that an online, belief-based score captures
  it. They do not show how often real data looks like this.
- The margin rule is **told** which situations are forks, and uses the agent's own estimator.
  Real systems have to estimate both.
- The **surprise comparator** is only *inspired by* Titans and prioritized replay; it implements
  neither.
- The **clairvoyant comparator** was best everywhere, but it is not a proven bound.
- Parked for their own pre-registrations: **Part B** (a fast-weight memory), **sleep** (replay and
  consolidation), and a **cliff test** (a non-stationary stream).

## Reproduce

```bash
python3 svc.py   # ~2.5 min on 4 cores; results/svc_report.txt, results/svc_raw.json, figures/svc.png
```

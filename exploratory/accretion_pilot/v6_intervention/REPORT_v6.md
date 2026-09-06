# Report v6 — crossed initial conditions (a 2×2 intervention)

*Plain-language write-up, written after the run. Register: speculative
exploration; not a confirmatory study, not cosmology. Bounded follow-up to v5.
Rules fixed in advance in [`DESIGN_NOTE_v6.md`](DESIGN_NOTE_v6.md). We intervened on
**initial conditions only**; the movement/reinforcement/growth rules are v2's,
unchanged. 200 paired seeds, 10,000 steps. Reproduce: `python accretion_pilot_v6.py`.*

## Question

Does the later four-traversal footprint (v5's added-diagonal one-bit reader
`S_high`) follow the **initial reinforcement on original edges** (W), the **initial
placement of added diagonals** (T), or their **interaction**?

## What we built

The post-history Growing states are deterministic, so we extracted, once: original
weights `W_A`,`W_B` and diagonal sets `T_A`,`T_B`, and crossed them into four
worlds — `W_A+T_A` (intact A), `W_A+T_B`, `W_B+T_A`, `W_B+T_B` (intact B) — then
evolved each under the unchanged Growing rules.

**Construction verified** (`results/construction_checks.txt`): all activated
diagonals start at weight 1; `|T_A| = |T_B| = 30`; `multiset(W_A) = multiset(W_B)`;
all four worlds have identical initial **edge count (174)**, **total weight (244)**,
and **original-edge weight multiset**, differing only in spatial arrangement; and
all four initial four-traversal bits are 0. **Reproduction verified**: intact-A and
intact-B per-edge snapshots match v4's retained `Growing__A/B` snapshots for every
seed and checkpoint (max |Δw| < 1e-9), so intact worlds reproduce v2/v5 exactly.

## Answer — both ingredients matter, comparably; neither alone suffices

Mean `S_high` (A-positive) by world over time:

| world | t=400 | t=2000 (peak) | t=10000 |
|---|---|---|---|
| `W_A+T_A` (intact A) | +3.43 | **+5.99** | +0.28 |
| `W_A+T_B` (crossed) | +0.62 | +1.55 | +0.06 |
| `W_B+T_A` (crossed) | +0.18 | +0.92 | +0.04 |
| `W_B+T_B` (intact B) | −3.11 | **−5.78** | −0.10 |

The intact worlds develop a strong, mirror-symmetric footprint that peaks around
t=2000; **both crossed worlds stay near zero throughout.** So the strong footprint
requires `W` and `T` **aligned on the same side** — either ingredient alone
produces only a weak footprint.

Factor effects on mean `S_high` (paired difference, seed-block bootstrap 95% CI):

| contrast | t=400 | t=2000 | t=10000 |
|---|---|---|---|
| **weight** effect \| T_A | +3.25 [2.23, 4.27] | +5.07 [2.44, 7.73] | +0.24 [0.06, 0.43] |
| **weight** effect \| T_B | +3.73 [2.66, 4.90] | +7.32 [4.87, 9.96] | +0.16 [−0.04, 0.36] |
| **topology** effect \| W_A | +2.81 [1.77, 3.88] | +4.44 [1.98, 6.89] | +0.22 [0.02, 0.42] |
| **topology** effect \| W_B | +3.29 [2.23, 4.42] | +6.70 [4.26, 9.26] | +0.14 [−0.08, 0.34] |
| **interaction** | −0.48 [−1.94, 1.00] | −2.26 [−5.58, 1.14] | +0.08 [−0.20, 0.37] |

Both the weight main effect and the topology main effect are **substantial,
comparable in size, and statistically supported** at t=400 and t=2000 (all four CIs
exclude 0). So the later four-traversal footprint follows **both** the initial
original-edge reinforcement **and** the initial diagonal placement — not one to the
exclusion of the other. The **interaction** point estimate is negative mid-run
(effects slightly sub-additive — each ingredient partly does what the other would),
but its CI includes 0 at every checkpoint, so we do **not** claim a resolved
interaction; the robust statement is two comparable main effects.

## Why the footprint collapses late (a saturation artifact of this reader)

By t=10000 nearly every world is complete (all 128 diagonals present; see
`results/late_completeness.txt`) and nearly all diagonals have `w ≥ 5.5`, so
`S_high → Σ s(e) = P_D → 0` on complete topology. The **raw** footprint magnitude
therefore peaks mid-run (~t=2000) and fades toward 0 as the world saturates
symmetrically. (v5's late AUC of 0.62 came from a tiny residual *ranking*, not raw
magnitude.) Consequently the factorial is most informative mid-run; at t=10000 the
effects are small (≈0.1–0.24) with only the `|T_A` weight effect and `|W_A`
topology effect just clearing 0. We report all checkpoints and do not drop
incomplete worlds.

## Interpretation boundaries (honoured)

- These interventions isolate the effects of the two supplied **initial
  arrangements** under this model. Later differences in visits, growth and weights
  are **consequences** of the interventions, not variables to match away.
- A **topology effect does not mean topology stores the memory**: the initial
  diagonal placement shapes where later traffic and reinforcement concentrate, so a
  `T` effect can act *through* later weights. Equally, the **weight effect does not
  exclude a topology contribution.**
- The crossed conditions do interact (point estimate sub-additive, unresolved).
- No claim of memory transfer, universality, intrinsic addressing, or inexhaustible
  growth. Still a reader with external coordinates; comparisons exploratory.

## One worthwhile next question

Both crossed worlds are weak, which suggests the footprint is driven by the
**alignment** of heavy original edges with placed diagonals (the walker is funnelled
by heavy edges toward diagonals that happen to sit there, re-crossing them ≥4×).
A bounded next intervention would **vary the degree of W–T alignment** directly —
e.g. rotate/shift `T` by a controlled number of cells relative to `W` (from aligned
through orthogonal to anti-aligned), holding counts and weights fixed — and measure
how the mid-run footprint magnitude falls with misalignment. That would test whether
"aligned reinforcement-and-placement" is the operative ingredient, using the same
unchanged dynamics and one constructed family (an alignment axis, not a parameter
sweep of the rules).

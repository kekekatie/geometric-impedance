# E-prime results: the coiled spring leans in — weakly, but it leans

*Confirmatory run: 60 genuine free choices, 20 fresh worlds (wedge 241+), 3 forks per world, properly
independent. Seam = the confound-free branch comparison (commit A vs B, keep only the differing tiles).
Scored against the committed `PREREGISTRATION.md`; the invalid first run is documented in
`VALIDATION_NOTE.md` and is not used here.*

## The one-line answer

The pre-registered effect **met its threshold, in the Coiled-Spring direction** — *more pinched / more
rigid* free choices unleash *larger* counterfactual seams, not freer ones. But the effect is **weak, and
the world-clustered confidence interval grazes zero**, so this is a **suggestive lean, not a nailed-down
law**. The competing "Novelty Budget" reading (freer forks diverge more) is **not supported**, and gently
disfavoured.

## The numbers, in the open

| measure | raw ρ | age-partial ρ | 90% cluster CI | reads |
|---|---|---|---|---|
| **E1** stiffness → seam size | **+0.204** | **+0.209** | **[−0.017, +0.383]** | Coiled Spring; **meets bar, CI grazes 0** |
| E2 stiffness → seam *max*-reach | −0.253 | −0.257 | [−0.494, +0.001] | **pinned measure — ignore** (see below) |
| E2′ stiffness → *median*-reach (diagnostic) | +0.177 | +0.178 | — | Coiled Spring, same sign as E1 |
| wall-nearness → seam size (secondary) | −0.133 | −0.143 | — | **also Coiled Spring** (forced → bigger) |

- **E1 passes the pre-registered rule** (|ρ| ≥ 0.2 **and** age-partial same-sign |ρ| ≥ 0.15). It clears
  it *barely* (+0.204 vs 0.20), and the honest **world-cluster CI is [−0.017, +0.383]** — it includes
  zero. Had the pre-registration gated on the CI excluding zero, E1 would be null. It did not; so by its
  own letter E1 is a pass, and I am recording it as a **weak positive lean**, not a strong effect.

- **E2 (max-reach) is dead on arrival and I say so:** max-reach pins at the R=7·S measurement rim
  (median 7.3, p10–p90 7.2–7.3 — essentially constant), exactly the saturation the pre-reg flagged. A
  rank correlation against a near-constant is noise; its −0.25 is not a real opposite-direction effect.
  The honest reach test is the **unpinned median-radius diagnostic: +0.177**, which points the **same way
  as E1** (stiffer forks → differing tiles sit farther out).

- **The age control worked, and vindicates the fix.** In the proper multi-world sample
  **Spearman(patch age, stiffness) = −0.005** — stiffness is genuinely age-independent now (the −0.25 in
  the botched one-world run was a within-world artifact). Seam size does carry a modest age trend
  (−0.255), but the stiffness→size effect **survives it unchanged** (partial +0.209 ≈ raw +0.204), so the
  lean is **not** patch age.

## Why I believe the weak lean is pointing somewhere real

Three *independent* windows all tilt the same way — toward the pinched pole:

1. stiffness → seam size: **+0.20** (rigid fork → bigger seam);
2. stiffness → median seam reach: **+0.18** (rigid fork → farther seam);
3. wall-nearness → seam size: **−0.13**, i.e. **on-the-wall / forced** (low wall-nearness) → bigger seam.

Stiffness and wall-nearness are different measures of the same thing (how forced the fork is), computed
differently, and they **agree in sign**. No single one clears a strong bar, but the convergence is why I
read this as a real-but-small Coiled-Spring tendency rather than pure noise.

**The mechanism, if it holds:** a tightly-pinched free choice is a *loaded spring* — the local
configuration is already near-saturated, so committing one option propagates a long, dense forced
cascade. A roomy, genuinely-slack free choice is a *shock absorber* — the slack soaks the choice up
locally and little carries downstream.

## What this means for the memory-paper jewel

§4's line **"distance-to-the-wall is a novelty budget"** (marked *(Play)*) predicted the **opposite**:
free forks (far from the wall) should diverge *most*. The first clean, pre-registered test **does not
support that** and leans the other way. The honest update for the paper: *the consequence of a choice is
largest where the configuration was most constrained* — memory's reach is set by the **tension at the
fork, not the freedom.** This should be written as **"the first direct test leans Coiled Spring, weakly"**
— not as either slogan confirmed.

## Reported phenomena (not scored)

- **Seam size:** median 162 tiles, p10–p90 106–237, max 248. All 60 arms saturated; **0/60 cap-hit**, so
  seams are complete, not truncated.
- **Per-fork asymmetry:** |A-only| vs |B-only| medians 53 vs 77, mean within-fork gap **86 tiles**. The
  two options of a free choice are usually **very unequal in consequence** — one is a big move, one small
  (echoing the branch diagnostic's 264-vs-14). The *fork* is symmetric on average across forks; each
  *individual* fork is lopsided.

## Honest limits / next step

- +0.204 sits **right on** the pre-registered bar with a CI touching zero. The direction is the finding;
  the magnitude is not pinned. **A larger replication (≈40–60 worlds) is warranted** to tighten the CI
  and decide whether the Coiled-Spring lean survives — I did not do that here so as not to peek-then-grow.
- "Free" = unresolved by the bounded screen; stiffness/wall are the independent decisiveness labels.
- Seam measured to local saturation at R=7·S; size is complete, but *max*-reach cannot exceed the rim
  (hence the median-radius diagnostic).
- 20 worlds = 20 clusters; the cluster bootstrap is the honest uncertainty, and it is wide.

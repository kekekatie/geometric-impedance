# Constraint chains: which route carries a choice's consequences?

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). One change was made before the first run (how the baseline
was sampled), and it is recorded there.*

**Why.** `../thread_influence/` found that a choice's consequences spread along the now *ahead of* the
decided ribbon. Astra pointed out that this doesn't identify the route, and suggested tracing it
directly.

**How.**

- For every tile in the difference between two alternative presents, we found its **critical**
  neighbours: the tiles without which it would no longer be forced. Removing a critical tile leaves
  the edge either unforced or forced into something else.
- We then classified each link from a *differing* critical neighbour:
  - **decided ribbon:** shares a decided-ribbon edge;
  - **other edge:** shares any other edge (another ribbon, or the diagonal inside a rhombus);
  - **corner:** shares only a vertex;
  - **distant:** shares nothing.
- An **advance** is a differing tile that pushes the difference's extent further along the front. It
  is given its best route, in the order decided ribbon, other edge, corner. So a *corner* advance had
  no edge link to any differing tile at all.
- **Data:** the same 24 worlds as before; 67 choices; **37 distinct local configurations** (structural
  3-edge key, answering Astra's de-duplication point); both siblings grown up to 12 slices.

> **Refinement after Astra's review (2026-10-10, exploratory: [`web_EXPLORATORY.py`](web_EXPLORATORY.py), [`results/web_run.log`](results/web_run.log)).** Astra noted three things:
>
> - "other edge" mixed real ribbon-crossing edges with the diagonal inside a rhombus;
> - the owner of the forcing edge was counted as critical **by convention**, without the removal test;
> - the baseline wasn't a matched population.
>
> Re-tallied on the same 37 configurations, the picture changes a lot:
>
> | links | attachment (owner, untested) | decided ribbon | other ribbon edge | diagonal | corner |
> |---|---|---|---|---|---|
> | differing parents → difference tiles (4,093) | **0.604** | 0.006 | **0.000** | 0.029 | 0.361 |
> | same, **removal-tested only** (1,620) | n/a | 0.015 | **0.000** | 0.073 | **0.912** |
> | MATCHED: all parents of difference tiles (5,971) | 0.537 | 0.004 | 0.000 | 0.020 | 0.439 |
> | MATCHED: all parents of non-difference tiles (1,359) | 0.575 | 0.000 | 0.010 | 0.006 | 0.409 |
> | MATCHED, removal-tested only: difference vs non-difference | n/a | 0.009 vs 0 | 0 vs 0.023 | 0.043 vs 0.014 | **0.948 vs 0.964** |
>
> **What this means:**
>
> - **The "other edge" route in C1–C3 was almost entirely *attachment*.** A tile grows off the tile across the edge it was forced on. That edge is itself a step along *some* ribbon (or across a rhombus's diagonal), but not specifically the decided one.
> - **Apart from attachment, what independently forces a tile is almost always a tile touching it only at a corner** (91% of tested links). Edge-neighbours other than the owner are essentially never independently necessary under single removal.
> - So **C2 held only by the letter.** Its "other ribbons" meaning is not supported: tested links across other ribbons' edges are about 0. C1 and C3 stand as registered.
> - The **matched comparison** shows difference and non-difference tiles forced through near-identical route mixes (corners 44% vs 41% of all parents; 95% vs 96% of tested parents). That is still descriptive, not a test of equivalence. A choice's consequences are carried the way any tile is forced: by growing from a neighbour, and by corner constraints.
> - **Caveat (single removal):** if two edge-neighbours could each supply a constraint, neither registers. Edge contributions may be hidden by redundancy. These are the *detected necessary* neighbours, not a complete causal map.
> - **Picture:** [`figures/constraint_web.png`](figures/constraint_web.png), one choice. Grey arrows are attachments, forming small local trees. Red arrows are corner-only links, which leap along the strip and carry the difference down the front. In this example, the simple rule picked a "decided ribbon" heading away from the strip, the misidentification risk noted in the limits.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| Z | ≥ 99% of difference tiles are uniquely forced by their 2.5-edge context | **3,205 / 3,205** | ✅ PASS |
| C1 | (Claude) corners carry ≥ 1/3 of advances | **0.355** | ✅ HELD (narrowly) |
| C2 | (Astra) other edges carry more advances than corners | **0.478 vs 0.355** | ✅ HELD |
| C3 | the decided ribbon carries at most half of the advances | **0.167** | ✅ HELD |

1,783 advances; 1,782 had a differing critical parent.

**Reported:**

| | decided ribbon | other edge | corner | distant |
|---|---|---|---|---|
| best route, all 3,205 difference tiles | 0.141 | 0.661 | 0.197 | 0 |
| all 4,093 differing-parent links | 0.111 | 0.528 | 0.361 | 0 |
| **baseline:** critical links of 805 non-difference tiles | 0.036 | 0.514 | **0.450** | 0 |

Critical tiles per forced placement: median 1 (usually only the owner), range 1–7.

## What it means (plainly)

- **A choice's consequences travel through the whole local web of constraints, not along one thread.**
  - About half of the advances run through **other ribbons**, crossing or neighbouring the decided one.
  - About a third hop **purely by corners**, where tiles meet only at a point and the matching rules
    still act.
  - Only about a sixth run along the decided ribbon itself.
  - Both candidate routes, Astra's and Claude's, are real. Neither alone is the answer.
- **Corners are not special carriers of influence.** In ordinary forcing (the baseline), corners make
  up **45%** of critical links. Differences use them slightly *less* (36%). So the consequences
  travel through roughly the **same mix of routes that ordinary forcing uses**. The news of a choice
  spreads the way everything gets forced.
- **Nothing acts at a distance.** No link was "distant", in the difference or in the baseline.
  Everything passes through tiles that touch, at an edge or a corner.
- **What this does *not* show.** "Influence travels through forcing links" is true **by construction**
  here, because a difference tile's parents were *defined* as its critical tiles. So this is not
  independent support for Astra's guiding thought. What is informative is the **mix of routes**, and
  how close it is to ordinary forcing.
- **The structural de-duplication found 37 distinct configurations.** The earlier tile-count proxy
  suggested about 27, so it was merging genuinely different situations, as Astra suspected.

## Limits

- "Critical" means single-removal. When two tiles each suffice to force a placement, neither registers
  (median 1 critical tile). Hidden redundancy may under-count some routes.
- The best-route order (decided ribbon, then other edge, then corner) assigns an advance with both an
  edge and a corner link to the edge route. So the corner share is the share of **corner-only**
  advances.
- C1 passed narrowly (0.355 against 0.333).
- Up to 12 slices; 37 distinct configurations; one tiling family.

## Files

- `constraint_chains.py`: the study
- `results/constraint_chains_report.txt`, `results/run.log`, `results/worlds.json`

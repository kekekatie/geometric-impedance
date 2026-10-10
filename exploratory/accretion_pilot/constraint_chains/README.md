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

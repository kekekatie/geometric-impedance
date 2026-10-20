# Local nows: what happens when each part of the front chooses for itself?

*Pre-registration, written and committed before any code for this study exists. It grew from Katie's
"pea" (2026-10-20): something foundational felt upside down. Katie picked candidate peas 1–3: a
single global now, a global scheduler, and forks studied instead of stuff. Argon's reading followed,
and so did this one.*

## Where this comes from

Our patient scheduler has a **single global now**. No choice is made anywhere until the *entire*
front has run out of forced moves. Then one choice is made, at the frontier edge nearest the origin.

That synchronisation means every choice is made with the whole world's forced information already in
place, so choices rarely contradict each other. The suspicion: **the global clock hides conflict.**
With **local nows**, each stretch of front would choose as soon as *its own* neighbourhood runs out
of forced moves, while other parts are still busy. Independent choices could then disagree, and the
disagreement would have to be resolved where the fronts meet: by healing, by jamming, or as a lasting
mismatch.

Locally legal growth cannot produce a visible mismatch between placed tiles. A disagreement shows up
as **F becoming empty**: a patch legal everywhere locally but no longer part of *any* Penrose tiling
(a "dead" world). It shows up later as a **jam**.

## Words

- **GLOBAL scheduler:** as in all earlier studies. Each slice places every forced tile. If none exist
  anywhere, one choice is made at the first frontier edge.
- **LOCAL scheduler (R = 3 edges):** each slice:
  1. place every forced tile;
  2. find **locally stalled** edges: frontier edges with ≥ 2 candidates whose midpoint is more than R
     edges from every forced edge's midpoint;
  3. pick, in random order, a set of them at least 2R apart;
  4. make a choice at each one (re-checking its candidates first).

  So choices happen wherever a neighbourhood is quiet, even while forced growth continues elsewhere,
  and several can happen in one slice.
- **Dead:** F's compatible region is empty (LP classifier from `slack/classify_EXPLORATORY.py`).
- **Paired worlds:** the same 24 fresh seeds, each grown with both schedulers. Wedge entries 216–239
  (0–215 used before), seed 20261210 + world. Each grows until 1500 added tiles, a jam, or 400
  slices.

## Predictions (fixed now)

**N1: Local nows produce conflict.** LOCAL worlds jam (or end dead) more often than GLOBAL worlds: at
least 6 of the 24 LOCAL worlds jam or end dead, and at least 3× as many as GLOBAL. Confidence about
70%.

**N2: The contradiction exists before it is discovered.** In LOCAL worlds that jam, F was already
empty some slices before the jam: the median lead is at least 3 slices. Confidence about 60%.

## Reported, not tested

- Choices per world, and how many slices it takes to reach the size (does the local now grow
  "faster"?).
- For LOCAL worlds that go dead, the slice they died, and how far the jam is from the most recent
  choices.
- How many choices LOCAL makes simultaneously.

## Limits I already know

- R = 3 edges is one arbitrary scale for "local". Other scales may behave differently.
- "Dead" uses the LP classifier on our window representation.
- 24 paired worlds.
- Locating *where* a contradiction sits (a candidate "mismatch line") is not attempted here. It is a
  follow-up if N1 holds.

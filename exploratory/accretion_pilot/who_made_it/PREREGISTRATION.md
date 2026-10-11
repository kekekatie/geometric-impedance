# Can the tiling tell who made it? Pre-registration

*Written and committed **before** any code for this study existed.*

## Why

Astra's question (2026-10-11): our growth picks between the two options at a choice **50/50**,
although their pieces of the wiggle room F are unequal (for example 38% and 62%).

There are two models of a world:

- **SELECT** (*making*): at each choice, toss a fair coin between the two options. This is how every
  world so far has been grown.
- **REVEAL** (*discovering*): first draw a hidden offset t₀ uniformly from the seed patch's wiggle room
  F₀. At each choice, take the option whose piece contains t₀. Each piece is then taken with probability
  equal to its share of F.

Katie's intuition: "both, revealing mainly, selecting at special moments."

**Claude's guess, registered here:**

- a **single** finished world cannot tell which model made it, because both are genuine Penrose patches;
- only **dead ends** (possible only for SELECT) and the **ensemble** of many worlds tell them apart.

## Construction

**Part 1: many seeds.**

- 48 ordinary worlds, seeded at the 48 nearest symmetry-free reference vertices (the 18° wedge of
  `../thread_influence/`, entries 1–48).
- Each is grown **twice**:
  - SELECT, with random stream `20261200 + k`;
  - REVEAL, with t₀ drawn from F₀ using stream `20261300 + k`.
- 1,500 half-tiles; patient scheduler; decoration-aware candidates.
- **Pieces at a choice:** each option is grown forced-only for up to 8 slices (`../fragility/` sibling
  growth). The piece is that sibling's F (`../slack/` functions).
- **REVEAL picks** the option whose piece contains t₀. If neither piece contains t₀ (numerical edge
  case), it falls back to a share-weighted random pick, and this is counted and reported.
- **Single-world statistics:** in each finished world, the frequencies of the 8 Penrose vertex types
  (`L.star`) among complete-star vertices more than 2 edges inside the frontier.

**Part 2: one seed, a crowd of worlds.**

- 40 SELECT and 40 REVEAL worlds, all from the **same** seed centre (wedge entry 1).
- For each, record which piece of the **first** choice the finished world lies in, read from the
  finished tiling's own F (does F_final lie inside piece A or piece B?), not from the process log.

## Predictions

- **W1 (dead ends belong to makers).** No REVEAL world ever takes a dead option or jams: **0 of 48**.
  *Confidence about 90%.* SELECT jams are reported; earlier studies saw about 1 in 24.
- **W2 (one world cannot tell).**
  - For each of the 8 vertex types, compare the mean frequency in SELECT vs REVEAL worlds (Part 1),
    using a permutation test (2,000 label shuffles).
  - Prediction: **no** type differs at p < 0.01/8 (Bonferroni).
  - *Confidence about 75%.*
- **W3 (a crowd can tell).** In Part 2, the fraction of worlds lying in the **smaller** first-choice
  piece is:
  - for REVEAL, within the 95% binomial interval around that piece's share;
  - for SELECT, within the 95% interval around 0.5.
  - *Confidence about 85%.* This holds largely by construction. It is a demonstration that the
    finished tilings, read alone, carry the crowd-level signature.

## Reported without prediction

- Jam counts, dead-option counts, and REVEAL fallbacks.
- How often each mode took the smaller piece over all choices.
- Effect sizes per vertex type.
- Whether SELECT worlds' final offsets cluster differently.

## Limits, stated in advance

- 1,500 half-tiles per world: finite patches.
- Vertex-type frequencies are one family of single-world statistics. A null result doesn't exclude
  subtler signatures.
- One tiling family.

## Changes before the first run

*(none yet)*

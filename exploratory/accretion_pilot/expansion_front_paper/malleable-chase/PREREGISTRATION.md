# What actually tips the wobble: the scheduler's stopwatch, or the interior wall?

### The malleable chase (Experiment C)

*Pre-registration. Written and committed **before any study code for Experiment C exists**. The
numbers below are our called shots; we look only after they are fixed.*

*Katie (direction), Argon (the interior-wall reading and the two-stage split), with Claude (Opus 4.8).
Follows Experiment A (the catalogue found the malleable moves) and Experiment B (outer-hull depth is
not what tips them). Reuses the forced-burst and compatibility-region (F) machinery of the
"decided-before-it-is-built" study (`../../decided_before_built.md`, `../../cut_direction/`,
`../../settled_test/`).*

---

## The picture first

Experiment A found that some recurring moves are **malleable** — the same local situation settles its
tie in some places and stays open in others. Experiment B ruled out the obvious suspect: a vertex's
*outer* hull depth (distance to the window's outer rim) barely predicts the wobble. Two suspects
remain:

- **(b) the scheduler's stopwatch.** The catalogue only watched each tie for **20 slices**. The global
  patient scheduler works outward from the seed, so a tie far from where the front is currently busy
  just *waits its turn*. Much of what looks "malleable" may be nothing but **when the front arrived** —
  a measurement-window artifact, not the board's indecision.
- **(a) the interior wall.** A two-way choice is, in hidden space, the compatibility region **F
  straddling a cut line** (an internal de Bruijn / vertex-type partition). Settling is one side of F
  shrinking to nothing. The real geometry of a choice is **how near it sits to that interior wall** —
  which the *outer* ruler of Experiment B could never see.

This study separates the two, in two stages.

### Stage 1 — the forced-burst separator (strip away the stopwatch)

From each tie's patch, grow **forced-only** — place every forced tile, **never guess** — until no
forced placement remains anywhere (saturation). This runs the board's *already-determined*
consequences to completion, with the 20-slice waiting line removed.

- The tie becomes forced during the burst → **secretly rigid (b)**: the board had already forced it;
  the catalogue only called it "open" because the front hadn't reached it yet.
- The tie is *still* two-way at saturation → **genuinely needs a guess (a)**: its fate waits on a
  future choice, not on forced cascades.

### Stage 2 — the interior-wall ruler

For choices, measure the compatibility region **F** (`Sl.region`/`Sl.area`) and each option's slice of
it (`pA`, `pB`, via the decided-before `after_first`). Nearness to the interior wall is
**`min(pA, pB) / F_area`** (near 0 = one option barely viable = right on the wall). Test whether this
*interior* ruler — not Experiment B's outer depth — is where the deciding sits, and whether it tips the
genuine-(a) survivors across the wall while the stayers straddle it.

---

## Words

- **Forced-only burst** — from a tie's `before` patch, repeatedly place all forced tiles (never a
  guess) until no single-candidate frontier edge remains, or a cap of **60 forced slices**.
- **Forced-burst-settles** — the tie's own edge becomes a single candidate (forced) during the burst.
- **Recurring fingerprint** — a radius-2·S canonical situation appearing ≥ 5 times in A's catalogue
  (the same set A's stiffness line used). **Malleable** / **rigid** as A classified them.
- **Secretly-rigid fingerprint** — every one of its occurrences forced-burst-settles.
- **Genuine-(a) fingerprint** — at least one occurrence does **not** forced-burst-settle.
- **F, F_area** — the patch's compatibility region and its area (`Sl.area(Sl.region(Sl.constraints(
  before, rank)))`), as in `cut_direction.world`.
- **Option pieces pA, pB** — F_area after committing to each option's first forced slice
  (`after_first`); **wall-nearness** `= min(pA, pB) / F_area`.
- **Forced-burst-settler / -stayer** — an occurrence of a genuine-(a) fingerprint that does / does not
  forced-burst-settle.

---

## Set-up (fixed now)

- The **same 24 worlds as A and B** (seeds 192–215), re-grown deterministically.
- At every tie belonging to a **recurring fingerprint** (≥ 5 occurrences in A), capture `before`, run
  the forced-only burst, and compute F, pA, pB. If a fingerprint has > 30 occurrences, a seeded random
  30 are bursted (enough for a fraction); all are measured for F.
- **Rigid fingerprints are bursted too, as a method control**: they should forced-burst-settle ≈ 100%,
  validating that the separator means what we say.

---

## Predictions (our called shots)

**C1 — much of the wobble is just the stopwatch.**
At least **50%** of A's 91 malleable fingerprints turn out **secretly rigid** (every occurrence
forced-burst-settles). *Confidence ≈ 60%.*

**C2 — but a genuine core survives.**
At least **15%** of the 91 malleable fingerprints are **genuine-(a)** — the same move forced to one
option in some instances and left needing a guess in others, even with the stopwatch removed.
*Confidence ≈ 70%* (the decided-before exception case proves genuine contingency exists).

**C3 — the interior ruler beats the outer ruler.**
Wall-nearness `min(pA,pB)/F_area` separates settled from stayed-open ties **more** than outer-hull
depth did (Experiment B gave a near-flat 0.393 vs 0.447): settled ties sit **nearer the wall** (smaller
`min(pA,pB)/F_area`), with a larger standardized effect than outer depth's. *Confidence ≈ 55%.*

**C4 — and the wall is what tips the survivors.**
Within genuine-(a) fingerprints, the **forced-burst-settlers sit nearer the wall** (smaller
`min(pA,pB)/F_area`) than the **stayers**, who straddle it. *Confidence ≈ 55%.*

**Method control (reported):** rigid fingerprints forced-burst-settle ≈ 100%. If they don't, the
separator is broken and C1–C2 are void.

---

## Reported, but not scored

- **The true stiffness line.** A's stiffness line redrawn after removing timing — how rigid the
  pattern *really* is once the stopwatch is gone.
- **The literal per-vertex internal depth.** Distance from a choice vertex's perpendicular coordinate
  to the window's vertex-type partition lines — the literal reading of Argon's teal ring. This needs
  the window's internal subdivision, a deeper build; flagged here, attempted only if the F-ruler lands.
- **Cut-line geometry** vs `cut_direction`'s (a cross-check that our F/cut line matches the prior
  study).

---

## Limits we already know

- The forced-only burst is **capped at 60 slices**; a forced cascade longer than that is counted as
  not-settled (conservative toward genuine-(a)).
- **Wall-nearness is the compatibility region's geometry**, not a literal per-vertex partition depth.
  It is the behaviourally relevant "distance to settling," and it is what the decided-before mechanism
  turns on — but it is a choice-level, not vertex-level, measure.
- The timing-vs-geometry split is **relative to this one patient scheduler's order**; a different
  scheduler would move the line between (a) and (b).
- Same 24 worlds, 4 of which jammed; one world type.
- This studies how a growing Penrose tiling settles its choices; no claim about physical space or time.

---

*When the shots above are fixed, implementation begins — a forced-only grower, the F/`after_first`
machinery from `cut_direction`, and A's tie records. Results, a plain report, and a self-contained
viewer follow, and this file will not be quietly rewritten.*

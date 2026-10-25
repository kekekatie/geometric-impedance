# Ribs and hinges: does a decisive birth breed a load-bearing structure?

### The endurance bridge, structural version (Experiment D)

*Pre-registration. Written and committed **before any study code for Experiment D exists**. The numbers
below are our called shots; we look only after they are fixed.*

*Katie (direction), Argon (the ribs/hinges reading and the width-of-the-now framing), with Claude
(Opus 4.8). Joins the birth-state of each choice (stiffness from A, wall-nearness and
genuine/secretly-rigid from C) to how much structure its settlement locks in. Reuses C's localised
forced-burst machinery.*

---

## The picture first

Experiment A found which moves wobble; C found that the wobble is real (91% genuine) and that a choice
settles when one option's slice of the compatibility region vanishes — it is born on the interior wall.
This study asks the next question: **when a choice settles decisively, does it build a long-lived
structural rib — or a short-lived hinge where the pattern turns over?**

The honest measure is **structural, not temporal.** "How many slices a motif lasts on the frontier" is
a stopwatch artifact — it only reflects how fast the front happens to sweep past. So we measure
**forced-support reach**: when a tie settles, how large is the forced cascade it anchors — how much
downstream structure becomes *forced* (no further guess) as a consequence. A **rib** forces a long
cascade; a **hinge** forces little, and the pattern must branch again nearby.

The birth-decisiveness axis is **A's stiffness** (rigid vs malleable fingerprint) and **C's
genuine-vs-secretly-rigid** split — not wall-nearness, because C showed settled ties are *all* on the
wall (≈ 0.000), leaving no variation there.

---

## Words

- **Settlement** — a tie that resolves as `single_keystone` or `committee` in the catalogue growth.
- **Forced-support reach** — from the tie's `before` patch, run the localised forced-only burst (radius
  10·S, cap 60, as in C) and count the **tiles placed** before it saturates. The reach of a settlement
  is this cascade size; a saturated-open tie's reach is small by construction.
- **Rib / hinge** — a settlement whose forced-support reach is in the long / short tail.
- **Birth-decisiveness** — `rigid` vs `malleable` (A's stiffness label of the fingerprint), and
  `secretly-rigid` vs `genuine-(a)` (C's forced-burst classification).
- **Frontier-advance rate** (for the timing control) — tiles added per slice in the tie's vicinity
  over the window; the scheduler-speed confound we must rule out.

---

## Set-up (fixed now)

- The **same 24 worlds** as A/C (seeds 192–215), re-grown deterministically; the forced-support reach
  is measured for every recurring-fingerprint tie (same set C bursted), joined to its A/C birth-state.
- Reach is a **tile count** (structural), never a slice count.

---

## Predictions (our called shots)

**D1 — a decisive birth breeds a load-bearing structure.**
Settlements of **rigid** fingerprints (and **secretly-rigid** ties) have **larger** forced-support
reach than **malleable** / **genuine-(a)** ones: median reach(rigid) > median reach(malleable), and
Spearman(stiffness, reach) **> 0.2**. *Confidence ≈ 55%.*

**D2 — two modes: ribs and hinges.**
The forced-support reach distribution is **bimodal** — a long-reach rib population separated from a
short-reach hinge population — rather than a single smooth spread. *Confidence ≈ 45%* (bimodality is a
strong claim; reported with a dip test and the histogram regardless).

**D3 — it is not the stopwatch.**
Forced-support reach is **structural, not temporal**: it does **not** track the local frontier-advance
rate (|Spearman(reach, advance-rate)| < 0.2), confirming ribs/hinges are a property of the geometry,
not of how fast the scheduler swept through. *Confidence ≈ 65%.*

---

## Reported, but not scored

- **The rib/hinge map by birth-state** — reach broken out by rigid/malleable and by
  secretly-rigid/genuine-(a), with the 1/φ² = 0.382 wobbly sites marked.
- **The partition-line visual bonus** — B's acceptance-window panel recoloured by *vertex type* (local
  star class), so the keystone ring can be seen sitting on the internal partition boundaries (Argon's
  interior-wall reading, made literal-ish).

---

## The faithful follow-up we are not doing yet

The direct measure of "endurance along the advancing skin" is **same-class motif renewal** in the
hollow active-skin growth (Astra's finding #9 machinery). Because the active-skin growth is verified
identical to the catalogue, it *can* be joined to these birth-states — but it is a substantial build.
If D1/D2 show a rib/hinge split, that is the deeper confirmation, and it gets its own pre-registration.

---

## Limits we already know

- **Forced-support reach is a structural proxy for endurance**, not literal persistence on the skin.
  It measures how much a settlement forces, which is what "load-bearing" should mean, but it is not a
  lifetime.
- The burst is localised (radius 10·S) and capped (60 slices), so reach is a bounded count.
- Same 24 worlds, 4 jammed; one scheduler. No claim about physical space or time.

# Local nows: what happens when each part of the front chooses for itself?

*A pre-registered study, from Katie's "pea" (2026-10-20): a single global now, a global scheduler,
and forks studied instead of stuff. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md).*

**Why.** Our patient scheduler has a **single global now**. No choice is made anywhere until the
*entire* front has run out of forced moves. The suspicion was that the global clock hides conflict.
So: what if each quiet stretch of front chose for itself, while other parts were still busy?

**The set-up.**

- 24 fresh seeds, each grown twice:
  - **GLOBAL:** the usual patient scheduler.
  - **LOCAL:** each slice places all forced tiles, then makes a choice at every frontier edge that has
    no forced edge within 3 edges, spaced at least 6 edges apart.
- Every slice, we check whether the patch is **dead**: F empty, meaning legal everywhere locally but
  part of no Penrose tiling.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| N1 | LOCAL worlds jam or end dead (≥ 6, and ≥ 3× GLOBAL) | **LOCAL 24 / 24** jammed (18 dead); **GLOBAL 2 / 24** | ✅ HELD |
| N2 | in LOCAL jams, F was empty ≥ 3 slices before the jam (median) | empty before the jam in **18 / 24**, always by 1–4 slices; median lead **2** | ❌ FAILED (narrowly) |

**Reported.**

- **LOCAL worlds die young.**
  - Median 16 slices and about 300 tiles before jamming. The deaths (F empty) came at slices 2–30.
  - GLOBAL worlds reached 1500 tiles in about 118 slices (22/24).
- **Even one choice can doom a world.** One LOCAL world died at slice 2 after a single choice. Another
  jammed at slice 10 after its only choice. LOCAL rarely made simultaneous choices (at most 2 in a
  slice), so independence across distance is not the whole story. What matters most is choosing
  **before the forced information has arrived**.
- **6 LOCAL worlds jammed while F still looked non-empty.** F is computed from vertex positions only.
  A conflict in the tile decorations (arrows), or a purely local dead end, would not show in it. This
  is unexplained, and it's a caveat on "dead" as a detector.
- GLOBAL's 2 jams died at slices 7 and 53, like the occasional "dead options" seen before.

## What it means (plainly)

- **In these worlds, local nows can't stay consistent.** If a region makes its choice before the
  forced consequences of everything nearby have arrived, it very often picks an option the rest of the
  world has already ruled out. Then the world is doomed: it is "dead" a couple of slices before it
  finds out, by jamming.
- **So the global clock isn't just our artefact. Here it's what keeps the world coherent.** Waiting
  until nothing is forced anywhere is a way of letting all the information arrive before deciding.
  That is the patient-growth principle from the quasicrystal growth literature (Onoda et al. 1988),
  now seen from the "local now" side.
- **The contradiction comes first and the discovery after.** The world is already impossible about
  two slices before any tile can show it. That's the same "settled before built" shape as the paper,
  now for a *failure*.
- **A connection worth testing (a hypothesis, not a result):**
  - Decapod worlds grow with **no choices at all**, pinned to one point. A local-now scheduler would
    make no difference to them, because nothing ever needs choosing.
  - Two decapods (two independently pinned regions) jammed at their first meeting. That looks like
    the same story as local nows: **independently decided regions can't meet.**
  - So maybe coherence in these worlds needs either one organising centre or a shared clock.

## Limits

- One choice of "local" (R = 3 edges, spacing 6). A more patient local rule (for example, choose only
  where nothing has been forced nearby for several slices) might survive longer.
- "Dead" is detected from vertex positions; 6 jams were not preceded by detected death.
- 24 paired seeds; the jams were not located.

## Next, if wanted

- **Where** does the contradiction sit, and how far is it from the choice that caused it?
- A gentler local rule: how patient does a local now have to be to stay coherent?
- Local nows in a decapod world (prediction: nothing changes, since there are no choices).

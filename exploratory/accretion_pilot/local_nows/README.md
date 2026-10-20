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

## Follow-up: how patient must a local now be? ([`PREREGISTRATION_patience.md`](PREREGISTRATION_patience.md))

*Pre-registered and committed before running [`patience.py`](patience.py). Same 24 seeds and the same
LOCAL rule, with the radius of patience R = 6, 12 and 24 edges.*

| radius of patience R | 3 | 6 | 12 | 24 | GLOBAL |
|---|---|---|---|---|---|
| bad worlds (jammed or dead), of 24 | 24 | 17 | 10 | **4** | 2 |
| median slices reached | 16 | 37 | 71 | 106 | 118 |
| median death-to-jam lead (slices) | 2 | 8.5 | 15 | — (1 jam) | — |

| | prediction | result | |
|---|---|---|---|
| Q1 | patience helps steadily: bad count never increases with R, and R = 24 < R = 3 | 24 → 17 → 10 → 4 | ✅ HELD |
| Q2 | R = 24 matches the global clock (≤ 4/24 bad) | **4 / 24** (1 jammed, 3 dead but not yet jammed) | ✅ HELD (right at the line) |

**What it means (plainly).**

- **Local nows can work, if they're patient enough.** With 24 edges of quiet around a choice, local
  worlds are nearly as coherent as worlds with one global clock. They also reach full size a little
  sooner (median 106 slices vs 118).
- **The further away the conflict, the longer it takes to find out.** The gap between a world
  becoming impossible and its jam grows with R: about 2 slices at R = 3, 8.5 at R = 6, 15 at R = 12.
  That fits news travelling at a finite speed: a contradiction set up far away takes longer to arrive.
- Three of R = 24's four bad worlds are **dead but not yet jammed** when the run ended. Their
  contradiction is still on its way.

**Caveats.**

- At R ≥ 12, choices are never simultaneous (at most one per slice). So patient local nows end up
  making choices one at a time, much like the global clock. The difference is that they don't wait
  for distant forced activity to finish.
- R is a straight-line radius, not a true causal cone, and there are 24 seeds.

## Follow-up 2: causally honest local nows ([`PREREGISTRATION_cone.md`](PREREGISTRATION_cone.md))

*Pre-registered and committed before running [`cone.py`](cone.py), 2026-10-21.*

**Why.** The R = 24 rule above checks for forced activity within 24 edges *right now*. Influence
travels at about 1 edge per slice, so that is **faster-than-light knowledge**. A causally honest
local now may only use its **past light cone**: forced activity at distance ≤ 1.05·k + 1 edges, k
slices ago, for k ≤ H.

| | CONE H = 12 | CONE H = 24 | CONE H = 48 | (R = 24, faster than light) | (GLOBAL) |
|---|---|---|---|---|---|
| bad worlds of 24 | 23 | 24 | 24 | 4 | 2 |

| | prediction | result | |
|---|---|---|---|
| K1 | a deeper past helps (non-increasing in H) | 23 → 24 → 24 | ❌ FAILED |
| K2 | honest patience is not enough (CONE(48) ≥ 8/24 bad) | **24 / 24** | ✅ HELD |

**Exploratory check** ([`cone_spacing_EXPLORATORY.py`](cone_spacing_EXPLORATORY.py)):

- Fatal slices often held several simultaneous choices. So CONE(H = 24) was re-run with choices
  forced ≥ 48 edges apart, which is itself a non-local coordination.
- **Still 24/24 bad**, and now every fatal slice held a single choice.
- So the failure is not simultaneity. **A causally honest local now cannot see incoming forced growth
  until it arrives.** A burst heading towards a region stays outside that region's past light cone.

**What it means (plainly).**

- In a Penrose world, local nows can stay coherent only by using knowledge they couldn't honestly
  have: what is happening far away right now.
- **Penrose rules hide a global constraint.** The shared window F means that a locally admissible
  choice can be ruled out by forced growth that hasn't arrived yet. No honest local process can see
  that in time.
- **For Katie's central hanger ("the universe topples relaxedly into the next now, within admissible
  windows"):**
  - a universe built from honest local nows that never breaks would need rules where **every locally
    admissible step is always globally fine**;
  - growth from an arbitrary Penrose patch lacks that property;
  - the decapod world has it trivially, because it never needs a choice at all.

**Limits.** One cone speed (c = 1.05, from `speed_of_light/`), straight-line distances, and one
choice rule. A cone measured along the front might differ. 24 seeds. "Dead" again misses some jams.

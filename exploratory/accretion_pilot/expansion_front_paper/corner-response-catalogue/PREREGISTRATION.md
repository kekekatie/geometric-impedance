# One corner, one decision — and does the same move always decide the same way?

### The corner-response catalogue

*Pre-registration. Written and committed **before any code for this study exists**, and before
any fresh world is grown. The numbers below are our called shots; we look only after they are fixed.*

*Katie (direction, intuitions), with Claude (Opus 4.8). Builds on the expansion-front active-skin
checkpoint (`../`, branch `codex/expansion-front-checks`, verified intact) and on the
"decided-before-it-is-built" study (`../../decided_before_built.md`).*

---

## The picture first

A Penrose tiling grows one tile at a time along its exposed edge — the **frontier**. At most places
on that frontier only one tile can legally go: the choice is **forced**, and the pattern simply
obeys. But here and there, *two* tiles would both fit. Call that a **tie** — an open two-way choice,
a doorway the pattern has not yet made up its mind about.

In the slice-45 result already in this checkpoint (`../local-response/`, finding #10 of the
handover), something quietly striking happened. A tie was settled — one of its two options ruled
out — by a **single** neighbouring tile, meeting the choice at **one shared corner**. Nineteen tiles
had gathered nearby, but only that one mattered: pull it out and both options return; pull any other
single tile and nothing changes. The option died because its little corner-decoration (the matching
rule) could not be completed at the shared vertex `(0.383516, 0.145898)`.

We call that event a **keystone handshake**: one tile reaches the tie at a single corner, offers its
decoration, and one of the two candidate futures cannot complete the handshake — so it is gone. The
tie collapses to forced.

**This study asks whether slice 45 was a lucky one-off, or how the pattern usually makes up its
mind.** We turn that single event into a census across many fresh growth runs, and we ask two things
of it:

1. **When a tie breaks, is it usually a single keystone — one tile, one corner — or does it take a
   committee?** And is the deciding touch really a *corner*, or would any neighbour have done?

2. **Does the *same* move always do the *same* thing?** Penrose tilings repeat: any little
   configuration you find here is guaranteed to recur, untouched, elsewhere (Conway's repetition
   property — "sames recur across the pattern without ever touching"). So we can find every recurrence
   of a given move and ask what fraction of the time it settles its tie. A move that settles *every*
   time is **rigid**. A move whose outcome *wobbles* with circumstance is **malleable**. We want to
   know **where the split between rigid and malleable lives** — whether reality here is stiff, or has
   give.

### The three drawers

Every tie we watch files into exactly one drawer:

| Drawer | What it means |
|---|---|
| **Single keystone** | One tile, necessary *and* sufficient, settles the tie. (Slice 45 lives here.) |
| **Committee** | No single tile does it; a bloc of two or more, acting together, is needed. |
| **Stayed open** | Within the watching window, the tie never collapsed. Still undecided. |

### The stiffness line

For each move that recurs often enough to count, we compute the fraction of its appearances that
settled. Then we lay every recurring move as a dot on one line:

```
  RIGID                                               MALLEABLE
  "settles every time"                         "settles about half the time"
     1.0  ●●●●●●●───────────────────────── 0.7  ● ● ●● ─────  0.5
           │                                        │
      a tight clump + a gap?              ...or smeared all across?
```

**The shape of where the dots land is the result.** A tight clump at 1.0 with a gap, then a scatter,
means reality here has two distinct kinds of decision — the fixed and the yielding — cleanly
separated. A smooth smear means stiffness is a dial, not a switch. Either way, this distribution is
our map of **where the split is**, drawn by the data rather than by us.

---

## Words (so every term above has one fixed meaning)

- **S** — one rhombus edge length, the natural unit of distance here. (Matching the checkpoint, local
  neighbourhoods are read at radius **2·S** around the choice vertex.)
- **Tie** — a frontier site where the patient scheduler, having placed every forced tile it can, faces
  **exactly two** legal candidate tiles. (Three-way or wider choices are recorded but set aside;
  this study is about two-way ties only.)
- **Choice vertex** — the frontier vertex at which the tie's two candidates differ.
- **Watching window** — after a tie first appears, ordinary growth (forced placements, and the
  scheduler's own guesses elsewhere) is allowed to proceed for up to **K = 20 slices**, or until the
  radius-2·S neighbourhood of the choice vertex is fully covered, whichever comes first.
- **Neighbour tile** — a tile placed during the watching window whose footprint lies within 2·S of
  the choice vertex.
- **Necessary (for a tile)** — removing that one neighbour tile alone, from the filled neighbourhood,
  brings the ruled-out option back (the tie re-opens).
- **Sufficient (for a tile)** — adding that one tile alone, to the pre-tie patch, is enough to rule the
  option out (the tie closes).
- **Keystone** — a single neighbour tile that is both necessary and sufficient. A tie **settled by a
  single keystone** goes in the *single keystone* drawer.
- **Shared corner** — the keystone and the choice site meet at a single shared **vertex**, and the
  recorded reason the option dies is the **vertex-compatibility (corner-decoration) rule**.
- **Shared edge** — the keystone and the choice site meet along a whole shared **edge**.
- **Committee** — the tie is settled within the window, but no single neighbour is necessary-and-
  sufficient; the smallest sufficient set has size ≥ 2.
- **Stayed open** — the tie is not settled within the watching window.
- **Fingerprint** — a canonical class key for the tie's situation: the patch within radius 2·S of the
  choice vertex, translation- and rotation-normalised and rounded to 5 decimals (the same
  canonicalisation the endurance study uses to recognise "sames"). Two ties with the same fingerprint
  are **the same move**.
- **Recurring move** — a fingerprint that appears **≥ 5 times** across the grown worlds. Only recurring
  moves enter the stiffness line (a fraction needs enough appearances to mean anything).
- **Settle-fraction (stiffness)** — for one recurring move, the fraction of its appearances that
  settled (single keystone *or* committee), as opposed to staying open.
- **Rigid / malleable** — a recurring move is **rigid** if its settle-fraction is ≥ 0.9, **malleable**
  if it is < 0.9. (The threshold is a label, chosen now; the full distribution is reported regardless.)

---

## Set-up (fixed now)

- **24 fresh ordinary worlds**, grown with the same patient scheduler and atlas rule as the prior
  studies, each to **1500 added tiles**.
- **Seed centres at entries 192–215** of the 18° wedge. These continue the non-overlapping convention
  (`cut_direction/` used 144–167; `settled_test/` used 168–191), so **no world here has been seen
  before**. Random seed **20261200 + world index**.
- Every live two-way tie encountered during growth is logged, fingerprinted, and watched.
- The motivating slice-45 case is **prior evidence, not test data**; it is not re-used here.

This is deliberately **call-our-shots on unseen worlds**: the predictions below are committed before a
single one of these worlds is grown.

---

## Predictions (our called shots)

**A1 — Single keystones are the usual way a tie breaks.**
Among all **settled** ties, the share settled by a single keystone (one tile, necessary-and-
sufficient) is **at least 60%** — i.e. single-tile decisions outnumber committees. *Confidence ≈ 70%.*

**A2 — The deciding touch is a corner, not just any neighbour.**
Two parts, both must hold:
- *Corner over edge:* among single keystones, the deciding contact is a **shared corner** (with the
  vertex-compatibility rule recorded as the reason) in **at least 80%** of cases.
- *Beats the placebo:* for each keystone-settled tie, we also try adding, alone, each of several
  **randomly chosen legal tiles** from the neighbourhood's candidate set. A random tile settles the
  tie **far less often** than the real keystone — concretely, the mean random-tile settle rate is
  **below half** the keystone rate. *Confidence ≈ 75%.*

**A3 — Reality has give (Katie's hypothesis).**
The stiffness line is **not** a single clump at 1.0. Among recurring moves (≥ 5 appearances), **at
least 15%** are malleable (settle-fraction < 0.9) — the same move, genuinely declining to settle some
of the time, because something beyond its radius-2·S fingerprint differs. *Confidence ≈ 65%.*

---

## Reported, but not scored

These we will look at and describe honestly; we are not committing pass/fail numbers to them here.

- **Where does the stiffness come from?** For each malleable move, compare the appearances that
  settled against those that didn't: what differs *beyond* the radius-2·S fingerprint — the wider
  patch, the scheduler's global state, distance from the seed? This is where the malleability lives.
- **Stiffness vs. window size.** Recompute the stiffness line at radius 1·S, 2·S, 3·S, 4·S. Does a
  wider window stiffen the decision — i.e. does "the same move" become more rigid as more context is
  folded in? This is a direct probe of *where the local ends and the global begins*.
- **The size of the vocabulary.** How many *distinct* recurring moves are there? Is it a small
  alphabet of gestures used over and over, or a long tail of near-singletons?
- **Does settling cascade?** After a keystone settles a tie, does a forced burst tend to follow within
  a few slices, exposing the next tie? (The "living thread" — what keeps organising the next
  construction.)

---

## The bridge we are *not* crossing yet

Two further questions are deliberately left for later rungs, named here so the staircase is visible:

- **Does rigid/malleable predict long/short-lasting?** The endurance observer (finding #9) already
  measures how long built motifs persist. Whether a tie's *stiffness* predicts the *lifetime* of what
  it builds — the bridge to the accrual / "width-of-the-now" thread — is the natural next rung. Not
  tested here.
- **Is the corner-handshake the same thing as directional balance?** In the hidden-address (perp-
  space) view, a corner contact is a *truncation of the acceptance window* — the "inward arrow" of the
  June directional-balance paper. Whether the keystones line up with shallow, inward-biased window
  depths is **Experiment B** (the depth-and-direction lenses). This study establishes the handshake in
  the *tiles*; it makes **no** address-space claim.

---

## Limits we already know

- A **fingerprint is bounded** (radius 2·S by default), so "the same move" is an operational match
  within that radius, not a proof that two situations are identical in every respect. That is exactly
  why malleability can exist, and why we report stiffness as a function of radius.
- **Necessary / sufficient** are tested within the diagnostic additions of the watching window, not
  across every possible history that tie could have had.
- The **placebo** samples random legal tiles; it bounds, but does not exhaust, "would any tile do?"
- **One world type, one scheduler.** The patient scheduler is global (forced placement anywhere wins
  before any guess), so "settled locally" and "scheduled locally" remain distinct; we do not claim
  fully local scheduling.
- A **tie that stays open** within K = 20 slices is not proven open forever — only unsettled within the
  window.
- Nothing here claims matter, mass, physical time, or physical space. This is a study of how a growing
  Penrose tiling settles its own open choices.

---

*When the shots above are fixed in the repository, implementation begins — reusing this checkpoint's
engine (`active_skin_engine.py`), its choice tracking (`choice_tracking.py`), its single-tile
necessary/sufficient test (`local_response.py`), and its "sames" canonicalisation. Results, a plain
report, and a self-contained viewer will follow, and this file will not be quietly rewritten.*

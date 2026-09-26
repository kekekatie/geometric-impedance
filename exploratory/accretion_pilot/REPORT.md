# Report — a world that grows without starting over (accretion pilot)

*Plain-language write-up, written **after** the run. Register: speculative
exploration. Not a confirmatory study, not a test of cosmology, not evidence for
any grand law. All rules and parameters were fixed in advance in
[`DESIGN_NOTE.md`](DESIGN_NOTE.md); this run used them unchanged. 200 paired
seeds. Reproduce with `python accretion_pilot.py`.*

## The question, in one sentence

If a world changes its own structure as things move through it, can those same
changes **remember which way an earlier journey went** and at the same time
**open up more ways to move next** — or do you have to trade one for the other?

## What we built

A 9×9 grid of places joined by weighted paths. Three worlds start identical:

- **Fixed** — moving changes nothing (the no-memory control).
- **Reinforced** — using a path makes it heavier (a bounded, saturating rule).
- **Growing** — same reinforcement, and where the local structure gets worn
  enough, a brand-new short diagonal connection *switches on* (from a fixed,
  finite, pre-declared catalogue of possible connections).

We also ran a **matched-resource control**: the Reinforced world with the *same
number* of new diagonals switched on, but placed **at random**, blind to the
journey.

Each world was given one of two **matched mirror-image journeys** — A hugging the
upper side of the diagonal, B the lower — identical in length, endpoints and
symmetry, both passing through the central probe. Then the walker was reset to the
probe and every world got the **same** random wandering for 400 steps. We read
memory and opportunity out of the graph **only** — never from a stored path or a
visit counter.

- **Memory** = a fixed symmetry contrast `M` (upper-side weight minus lower-side
  weight). Positive means "looks like A", negative "looks like B". We ask how
  often, across seed pairs, the A-world still scores higher than its paired
  B-world.
- **Opportunity** = (i) *structural access*: how many places lie within 4 hops of
  the probe, and (ii) *effective alternatives*: the effective number of distinct
  4-step routes out of the probe (high when movement can branch, low when weight
  funnels everything down one channel).

## What happened

All invariants passed (see [`results/invariants.txt`](results/invariants.txt)):
the Fixed world stayed perfectly symmetric and flat, weights stayed bounded and
positive, only catalogue diagonals were ever added, and the matched control's
edge count tracked the Growing model exactly.

Headline numbers at the final checkpoint (step 400):

| Model | Can we still tell A from B? `frac(M_A>M_B)` (AUC) | Effective alternatives `exp(H)` (start = 256) | Structural access (start = 40) | Added edges |
|---|---|---|---|---|
| Fixed | **0.50** (0.50) — chance | 256 (unchanged) | 40 (unchanged) | 0 |
| Reinforced | 0.835 (0.798) | **164 — *below* start** | 40 (unchanged) | 0 |
| Growing | **0.905 (0.908)** | **1562 — far above start** | 72.6 | 74.7 |
| Matched control | 0.795 (0.777) | 789 | 69.8 | 74.7 |

Three things stand out.

1. **Memory is real and it lasts — and growth makes it last *best*.** The Fixed
   world is at chance forever (0.50), exactly as a no-memory control should be.
   All the changing worlds start perfectly distinguishable and are gently eroded
   by the symmetric random wandering, but even after 400 steps the **Growing
   world is the most durable** (0.905 / AUC 0.908), ahead of Reinforced (0.835)
   and of the matched control (0.795). In the Growing world the raw contrast even
   *strengthens* over time (mean `M_A` rose 84 → 113): the new diagonals sit on
   the worn side and keep getting reinforced, so growth actively refreshes the
   trace rather than washing it out. This ordering was **not** guaranteed in
   advance — extra edges could just as easily have blurred the memory.

2. **Reinforcement alone buys memory at the cost of opportunity.** The Reinforced
   world remembers, but its effective alternatives *drop below the starting value*
   (256 → 107, recovering only to 164): weight funnels movement into the worn
   channel. More edges? None — structural access never moves off 40. This is the
   trade-off the question worried about, and it is real for reinforcement on its
   own.

3. **Growth makes memory and opportunity coexist.** The Growing world keeps the
   best memory **and** shows the largest opportunity on both measures —
   structural access up ~80% and effective alternatives up ~6× (256 → 1562). So
   in this toy world the two do **not** have to trade off; the same structural
   changes carry the past and widen the future at once.

## What was guaranteed by construction (so, not the interesting part)

- That memory exists **immediately** after the journey (step 0, `frac = 1.0` for
  every changing world): reinforcing the worn side *is* the readout, by
  definition.
- That growth and the control **add reachability**: switching on diagonals near
  the probe shortens hops, necessarily.
- That the Fixed world shows no memory and no change: that is what makes it a
  clean control.

The interesting, not-preordained parts are the **durability ordering** (growth
most durable), the **funnelling** in the Reinforced world (opportunity going
*down*), and the **coexistence** of memory and opportunity in the Growing world.

## What the matched control tells us

With the *same number* of added edges placed at random, opportunity still rises
well above baseline (effective alternatives 256 → 789): **a large part of the
opportunity gain is simply from added resources**, not from anything clever. But
the Growing world, with the same edge budget, reaches roughly twice as many
effective alternatives (1562 vs 789) and clearly better-preserved memory — because
its edges land where the journey actually wore the world, near the probe. So:
*resources alone explain much of the opportunity; history-shaped placement is what
turns those resources into durable memory and extra usable routes.*

(One honest mismatch: we matched edge **count** and each new edge's **initial**
weight, not the fully evolved total weight — the Growing world ends slightly
heavier, 593 vs 566, because its diagonals sit on busier routes and reinforce
more. The tables report total weight at every checkpoint so this is visible.)

## Limitations (read these before believing anything)

- **Memory with external coordinates.** The readout uses known vertex positions
  to define the symmetry axis. This is memory *addressed from outside*, not
  intrinsic self-addressing. A harder pilot would decode A from B without a
  coordinate frame.
- **A fixed, finite catalogue.** "New possibility" here means *newly switched on
  for this network*, from a pre-declared set of short diagonals. Nothing here is
  an expanding universe or inexhaustible novelty, and we make no such claim.
- **Imposed histories.** A and B are interventions we injected, not behaviours the
  world generated on its own.
- **One parameter point, one geometry.** We did not sweep parameters (deliberately
  — to avoid fishing for a nice result). A different grid, threshold, or number of
  steps could shift the balance. The durability gap between Growing and Reinforced
  is real but modest and should not be over-read.
- **The erosion is slow.** 400 steps gently erode memory; we did not run to
  extinction, so "how long until chance?" is unanswered.
- This is a **toy**. It is not consciousness, not physical time, not E8, not a law
  of the universe. It is a small, transparent demonstration that in *one* simple
  constructed world, structural change can carry the past and widen the future
  together.

## One worthwhile next question

Push the erosion much further (thousands of steps) and ask whether growth's
durability advantage **holds, converges, or crosses over** — does history-shaped
growth eventually *lock in* a memory that reinforcement alone loses, or do both
decay to chance at the same rate once the new edges themselves get worn
symmetric? That single long-run curve would tell us whether growth is genuinely a
better *memory substrate* or merely a slower-fading one.

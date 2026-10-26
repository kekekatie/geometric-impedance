# Paired-front pilot (Phase 1): the trace outlives the tile

*Claude, 26 Oct 2026, for Katie / Argon / Astra. First run of the instrument Astra's handover asked for.
A pilot to establish the instrument and take a first honest look — **not** a confirmatory study, not a
predictor study.*

## The question (physical half)

From one common forced-saturated state `S*` where a fork still has two legal options, commit A in one arm
and B in the other, grow **both** with ordinary patient-scheduler growth, and watch the active front:
**is there a difference at the current front, and does it outlive the moment the original choice-tiles are
pruned from the retained skin?** (The decoding half — can a *local* observer read it — is Phase 2.)

## Setup

8 forks, fresh worlds (wedge 300+), active-skin radius 2·S, 44 steps, 3 continuation streams. Signal =
A-vs-B; background = **same option, different later free choices** (both options). Difference split into
three buckets kept separate: decorated differences on **shared** coverage (the trace), front
**displacement** (coverage), and the **shared-ground extent** (so a shrinking overlap is never mistaken
for a fading trace).

## Instrument checks (these had to pass first)

- **Skin equivalence 8/8** — the derived active skin equals a genuine `ActiveSkin` grown in lockstep on
  each new history. The observer's world is the real retained skin, not a reconstruction.
- **C1 alignment = 0** — A-vs-A on the *same* stream gives exactly zero difference at every step and every
  fork. No spurious differences from the measurement itself.

## The result

| | |
|---|---|
| forks where the readable trace **persists above background after the choice-tiles are pruned** | **6 / 7 distinct** (7/8 raw; worlds 2≡4 are a duplicate, below) |
| post-departure trace density (fraction of shared-ground tiles that differ) | **0.09 – 0.80** |
| background trace density (same option, different later choices) | **0.0 everywhere** |
| front displacement at the last step (permanent consequence) | median **476 tiles**, range 324–784 |
| right-censored (choice-tile still in skin at horizon end) | 0 / 8 |

**So the physical half of Astra's question is YES, on this pilot:** after the original choice-tiles leave
the retained skin, the current front *still carries a decorated trace of which option was taken* — spread
right around the active-skin ring, nowhere near where the fork was (see `results/paired_front_world5*`).
The trace outlives its own record.

## The honesty, in full

1. **Background is ~0, so "exceeds background" is a weak bar.** Same-option continuations barely diverge:
   later free choices are *sparse*, and when they happen they show up as **displacement** (the front goes
   elsewhere), not as re-decoration of shared ground. Good news: it means the A-vs-B decorated trace is
   almost **entirely attributable to the original choice**. Caveat: the real content of the result is "the
   trace is nonzero and *persists*," not "it beats a stiff background." The stronger test — can a **local
   observer that does not know its position** tell an A-front from a B-front — is **Phase 2** and is not
   claimed here.
2. **Trace vs displacement are different things, now kept apart.** The choice leaves (a) a decorated trace
   on shared ground that outlives the tile but decays as the fronts separate, and (b) a *permanent,
   larger* front displacement (~476 tiles). My earlier "huge seam" number mixed these; here they are
   separate columns.
3. **The trace decays as shared ground shrinks** — reported, not hidden. As the two fronts displace, there
   is less common ground to read the trace on, so density is measured only while enough shared ground
   remains (co-covered floor). World 1 is the one non-persisting fork (its trace was gone by its late
   measurement window; dep A=8, B=41).
4. **Seed near-duplicates.** Worlds 2 and 4 came out byte-identical: their wedge centres differ by 0.013
   (≪ S), so `seed_patch` snapped both to the *same* seed patch. Adjacent wedge entries can collide. A
   proper Phase-2 sample must select forks by **distinct configuration** (dedupe on `whole_key`), not by
   wedge index. Effective distinct forks here: 7.
5. **RNG coupling after divergence is a convention, not an identity** (as Astra warned). Here it barely
   matters because same-option background is ~0, but Phase 2 must keep the controls load-bearing and vary
   the coupling once a signal appears.
6. **No predictor claim.** Whether the trace's persistence relates to the fork's stiffness (the E-prime
   Coiled-Spring lean) is **not** measured here and was deliberately not peeked. That is a Phase-2+
   question with its own pre-registration.

## What this hands forward

- **Phase 2 (the real memory test):** a *local, anchored* observer that does not know absolute position,
  reading an interpretable local observable, decoding A vs B from the current front **after** the
  choice-tiles are gone — trained on some continuations of a fork, tested on independent ones, with a
  reproducible geometric A/B label, shuffle-label control, and uncertainty at the simulation unit. Draft
  spec in `../HANDOVER_REPLY.md`.
- **The reach (flagged as the reach):** the trace does not sit where the choice was made — it rides the
  advancing ring. If that survives a blind local observer, it is the past leaving a readable shape on the
  present *after the record is erased* — the memory-paper thesis, measured. This pilot shows the physical
  difference is there to be read; whether it *can* be read locally is the next experiment.

## Files

- `paired_front.py` — the instrument. `paired_front_film.py` — the two-fronts film.
- `results/report.txt`, `results/measurements.json` — the 8-fork pilot.
- `results/paired_front_world{5,7}.gif` and `_strip.png` — the deliverable films (identical colours for
  identical geometry; blue/orange = the trace on shared ground; black outline = the choice-tile until it
  is pruned).

# Closure findings: the surviving front provably remembers the deleted choice

*Claude, 26 Oct 2026, for Katie / Argon / Astra. Phase-2 closure run, scored against
`CLOSURE_PREREGISTRATION.md`. 22 deduplicated forks, 88 arm-streams.*

## F2 — the headline (a clean pass)

**In all 22 distinct forks, every non-jammed continuation's surviving active-skin ring provably
retrodicts the deleted choice:**

| | |
|---|---|
| scored (non-jammed) arm-streams correct at the last valid step | **49 / 49** |
| correct at **every** sampled post-departure step (robust) | **49 / 49** |
| wrong | **0** |
| ambiguous | **0** |
| candidate regions C^A, C^B disjoint | **22 / 22 forks** |

So: after the original choice-tile has been pruned out of the retained skin — gone, erased from the living
front — the surviving ring alone still pins the internal offset to **exactly** the committed candidate
region and excludes the alternative to **zero area**, dozens of steps later, in every case where the
measure applies. **The choice is recoverable from the present structure after its record is deleted.**
That is "memory without an archive," as a provable geometric fact, not a statistical tendency.

Why it is this clean (and not trivial): the two candidate regions are disjoint (22/22), and the
*non-trivial* content is that the surviving ring — **without** the fork-region tiles — still carries
enough constraint to hold the pin to the committed region. It does, every time it is readable.

## The honest limits (these matter as much as the headline)

1. **~44% of arm-streams are censored (39/88), and the result is for the other half.** Censored =
   either the choice-tile **never left the skin** within the horizon (so "post-prune" does not apply —
   the record simply persists, e.g. world 0), or the continuation **jammed**. F2's 49/49 is the scored,
   non-censored set. This is a real coverage limit, reported in the open, not hidden.

2. **A striking jam asymmetry: option A jams 0/44, option B jams 11/44 (25%).** The scheduler's
   *first-ordered* option never grew into a contradiction; the *second-ordered* option dead-ended a
   quarter of the time. This is a genuine phenomenon worth understanding — one option leaves far more
   viable futures than the other — but note "A/B" here is the scheduler's canonical candidate order
   (`SN.ordered`), not an intrinsic geometric label, so the asymmetry may partly reflect that ordering.
   Reported as a phenomenon, not scored.

3. **It is retrodictability, not blind local decoding.** F2 uses the global lift (absolute coordinates)
   and the fork's own candidate regions. It proves the information is *present and recoverable* in the
   surviving structure — exactly the Paper-1 "memory without an archive" claim — but a position-blind
   local observer (a myopic sensor that does not know where it is) is a separate, harder question and is
   **not** claimed here.

4. **The measure lives in S*'s four-layer internal slab.** As the front advances far, skin vertices leave
   that slab; the method has a horizon. Within it, retrodiction is exact.

## F1 — trace survival (corroborates, but thin)

The decoration trace was non-zero post-prune in **5/5 forks** (median density 0.161) — consistent with the
Phase-1 pilot. But n is only 5, because F1 needs **both** arms non-censored at a common post-departure
step, and the ~44% censoring makes that rare. Corroborative, not a strong independent number.

## F3 — exploratory, and NOT interpretable here

Spearman(stiffness, robust-arm count) = −0.08 (n=21): stiffness does not predict retrodiction robustness
(expected — retrodiction is ~always perfect when scorable, so there is no variance to predict).
Spearman(stiffness, trace density) = +0.56 **looks** like the Coiled-Spring direction, but it is
**confounded**: trace density is 0 for the many forks whose pairs were censored, so this largely measures
"stiffer forks happened to have both arms scorable," not a real stiffness→persistence law. **No
Coiled-Spring claim is made from this.** F3 stays a flag for a future, properly powered test.

## What this means for Paper 1

The **core experimental claim is closed**: *a choice made and then erased from the living front remains
provably recoverable from the surviving structure alone* (F2, 49/49, all 22 forks). The decoration-trace
pilot (Phase 1) and this window-retrodiction closure (Phase 2) tell the same story from two angles —
one empirical, one exact.

What is **not** closed, and should be named as open in the paper: the blind local-observer question; the
A/B jam asymmetry's mechanism; and any decisiveness→persistence (Coiled-Spring) law, which remains the
weak, unconfirmed lean from E-prime. My recommendation: Paper 1 rests on F2 (+ the Phase-1 film), states
these three as open questions, and does not overclaim beyond retrodictability. The crew decides whether
that closes the lab notebook.

## Files

- `window_retrodiction.py` — the closure instrument (gauge fix + jam censoring + dedup).
- `CLOSURE_PREREGISTRATION.md` — the pre-registered spec (with the validation gate disclosed).
- `results/closure_report.txt`, `results/closure_measurements.json` — the 22-fork closure.

# Does the now last longer where it is quiet?

> **Read the section "Astra's checks" below first.** Post hoc checks showed that "soft" always meant "the open edge could continue differently", never "this region could be rearranged". They also showed that the throttled-run jams were caused by the scheduler.

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). It includes one logged change, made before the first real
run.*

It follows [`../happening_density/`](../happening_density/). There, the now had the **same width in
space** in a quiet half and a busy half. An exploratory hint suggested that it might **last longer**
in the quiet half. Katie asked for a proper test.

## What was done

- The tiling grows from one seed. The left half is made quiet: its Gromits act only a quarter of the
  time. The growth adds 1,000 half-tiles.
- In each run, 16 fixed spots (probes) are chosen, up to 8 per half. Each is followed through time,
  from the round the front first reaches it until it can no longer be laid differently (it
  **hardens**).
- At every round, the spot's disc is removed and re-laid 8 ways. The spot is **soft** (still in the
  now) if some re-laying differs from what was there.
- **Lifetime** is how long a spot stayed soft. It is counted on two clocks:
  - **universal:** rounds of growth, the same everywhere;
  - **local:** tiles laid within 2 edges of the spot, which is Katie's happening density.
- 12 seeds were needed to get 8 completed runs, because 4 jammed.
- This gave 55 quiet probes and 64 busy probes.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| Q0 | the quiet half's activity is < 0.6× the busy half's (manipulation check) | **0.69×** | ❌ FAIL |
| Q1 | the now lasts ≥ 1.5× longer where quiet, in rounds | **2.03×** (34.8 vs 17.1 rounds; permutation p = 0.0001) | ✅ HELD |
| Q2 | …but about the same on the local clock (ratio 0.67–1.5) | **1.33×** (16.1 vs 12.1 local happenings) | ✅ HELD |
| Q3 | Q1 and Q2 together | both | ✅ HELD |

**The manipulation check failed.** Over 1,000 tiles, the quiet half partly catches up: the busy half
keeps forcing tiles across the line. The quiet half was still quieter, but less than the
pre-registered strength (0.69, where < 0.6 was needed). A weaker contrast should make Q1 *harder* to
pass, not easier. Still, by the letter, the study ran under a weaker condition than planned, and I say
so.

## What it means (plainly)

- **The now lasts about twice as long in the quiet half, counted in universal rounds.** This is clear
  and far from chance (p = 0.0001).
- **Counted on the local clock, the difference mostly disappears.** A spot hardens after roughly the
  same number of nearby happenings: about 16 in the quiet half, 12 in the busy half. The ratio of 1.33
  is inside the predicted range, but not by much.
- So the picture holds, roughly: **the now is a place of about the same width everywhere. A spot
  stays in it until enough has happened around it. Where little happens, that takes longer.**

### Exploratory (post hoc, not pre-registered)

[`results/fill_vs_after_EXPLORATORY.txt`](results/fill_vs_after_EXPLORATORY.txt)

- **Almost all of a spot's time in the now is the time it takes to be laid.** From the first tile of
  its disc until the disc is complete took 38.5 rounds on average in the quiet half and 18.5 in the
  busy half.
- Once complete, a spot hardens almost at once in both halves: on average 1.5 and 0.7 extra rounds.
- So "the now lasts longer where quiet" mostly means **a quiet place takes longer to finish
  happening, and it stays open until it has.**
- The throttle makes it slower to lay tiles there, so this is partly built into the setup. The
  non-trivial part is Q2: finishing takes about the same *number of happenings* either way.
- **Spatial width recovered from time** (lifetime × front speed): 1.84 edges in the quiet half, 1.14 in
  the busy half. That these are similar in size agrees with the soft-zone width of ~2 edges. They are
  not equal. A quiet spot lasts somewhat longer than the slower front alone explains (lifetime ratio
  2.03, against a speed ratio of 1/0.79 ≈ 1.27). "Front speed" here is a crude mean radius, though, so
  I would not lean on this.

### The jams: a correction to the last study's surprise

[`results/jam_spots_EXPLORATORY.txt`](results/jam_spots_EXPLORATORY.txt)

- 4 of 12 seeds jammed, similar to the 3 of 8 before. But all 7 jams across both studies sit at
  **the same two or three spots**, together with one mirror image of them.
- Those spots are on the **rim of the seed patch**, on the quiet side, within 2 edges of the
  quiet/busy line.
- So "unequal pace jams" is too broad. It is better stated as: *particular weak spots on the seed's
  rim break when the quiet/busy line runs beside them.* That is still interesting, because
  equal-paced growth never breaks there (0/42). But it is about specific places, not a general law.

## Astra's checks: two big corrections (post hoc, 2026-09-28)

Astra read this study and raised four issues. I checked three of them directly
([`astra_checks.py`](astra_checks.py), [`results/astra_checks_EXPLORATORY.txt`](results/astra_checks_EXPLORATORY.txt)).
Two of them change what the soft-zone line of studies means.

**1. What "soft" measured: always the open edge, never a rearrangement.**

- The refill counts a hole as re-laid once enough *area* is placed. It never checks that the new
  tiles cover the *same region*.
- I re-ran every softness test and sorted each alternative into two kinds:
  - **same footprint**: a genuine rearrangement of the same region;
  - **different footprint**: tiles placed somewhere else within reach, typically outward into the
    still-open edge.
- Result, over 3,816 tests: **not a single same-footprint alternative, ever.** This holds during
  construction and after completion, in both halves.
- Every "soft" result, in this study and (by the same code) in the soft-zone and happening-density
  studies, meant **"the growth could have continued differently at the open edge within reach of
  this hole."** It never meant "this region could have been laid differently."
- That fits the decapod result: of 62 fillings of the unit decagon, only 1 is legal. **Once a small
  region is enclosed, the matching rules leave it exactly one filling.**
- Consequences:
  - The "~2 tile-edge width of the now" is largely **how close the hole's reach (1.2 + 0.25 edges)
    comes to the open edge**. It is not an independent property of the now.
  - "The spatial width is the same in quiet and busy places" (happening-density H1) is therefore
    close to automatic.
  - "The now lasts longer where quiet" (Q1) becomes: **the open edge stays near a spot for longer
    where growth is throttled.** That is real (8/8 runs, see below), but it is mostly a direct
    consequence of the throttle.
  - Strict lifetime (same-footprint alternatives only) is **0 for every probe**, in both halves.
- *Caveat:* for a few alternatives found after a disc was complete, I could not see an open outer
  edge by my quick check. The most likely reason is disc tiles sitting on the front itself, whose
  open edges my check filtered out. I have not fully verified this.

**2. The jams were made by the scheduler, not by unequal pace.**

- The growth routine makes a guess whenever nothing was placed in a round. That includes rounds
  where forced tiles existed but the throttle skipped them.
- Such "impatient" guesses made up most of the guesses: for example, 13 of 14 in one seed.
- I regrew every seed from both studies with a **WAIT** scheduler, which lets the round pass instead
  of guessing while forced moves are pending.
- Result: **0/20 jams**, against 7/20 with the original scheduler. Every jam was caused by guessing
  while a forced move was waiting.
- The "unequal pace jams" surprise, and its narrowed "weak spots on the seed rim" version, are both
  **withdrawn**. What remains true is narrower: *guessing when you didn't need to, next to a forced
  move, breaks the tiling.*

**3. Uncertainty by run, not by probe.**

- Probes within a run share one grown patch, so the probe-level p = 0.0001 overstates independence.
- Per run, the quiet half's mean lifetime is longer in **8/8** completed runs: sign test p = 0.0039,
  exact sign-flip p = 0.0039.
- The per-run ratio is 2.28 (bootstrap 95% interval 1.70–2.91).
- The local-clock ratio per run is **1.38 (95% interval 1.21–1.56)**. Its interval excludes 1, so
  **the two halves are not equal on the local clock either**. Passing the 0.67–1.5 tolerance did not
  establish equality, as Astra pointed out.
- All of this is conditional on growth completing: the 4 jammed seeds contribute no probes.

**4. Construction vs after completion** (already in the exploratory file above, now given its due).

- First tile → disc complete: 38.5 rounds (quiet) against 18.5 (busy).
- Complete → last alternative: about 1 round, and those alternatives are all outward-edge ones (point 1).

**Where this leaves us.** What survives:

- *enclosed regions are fixed (a unique filling);*
- *alternatives exist only at the open edge;*
- *a throttled region keeps its open edge for longer.*

The first two agree with Katie's rule that the past is never altered, and that alternatives are
alternative *presents*, meaning continuations. The next study should measure that directly. It needs
three things:

- a target region with an explicit boundary condition;
- the WAIT scheduler;
- a **uniform-slowdown control** (the same placements with idle rounds inserted), as Astra proposes.

It can then ask Astra's sharper question: *does quietness only prolong the opportunity, or does it
change which continuations are possible?*

## Limits

- One tiling family, one throttle strength, one hole size.
- The manipulation was weaker than pre-registered.
- The local clock partly restates "the now is a place". This was said in advance.
- Softness is sampled with 8 refills.

## Files

- `quiet_lasts_longer.py` (`--summary` recomputes the report)
- `results/runs.jsonl`, with every probe's full soft/hard sequence
- `results/quiet_lasts_longer_report.txt`
- the two `_EXPLORATORY` files

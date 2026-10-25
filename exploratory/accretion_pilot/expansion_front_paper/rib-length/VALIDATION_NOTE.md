# Validation note: D′ measure found contaminated — and a correction to an earlier over-claim

The pre-registered rib length `count_forced(before + surviving) − count_forced(before)` was validated on
one small world **before** any confirmatory run. It is **contaminated** and was **not run at scale**.

## The actual pilot (preserve as invalid, not as confirmation)

The committed pilot (`rib_length.py --worlds 1 --nadd 160`) produced **24 settlements: 22 values of −1
and two values of 71**. That is the record. There is no confirmatory D′ result.

## Why the −1 (corrected, per Astra's review)

`count_forced` counts tiles placed *during* the burst and excludes tiles already in the input patch.
In the baseline arm the forced wave often places the choice tile itself; in the seeded arm that tile is
pre-placed and not counted. When both arms end at the **same** final patch, baseline *n* versus seeded
*n−1* gives exactly **−1** — pure bookkeeping, not a different forced outcome. Adding one would repair
only that offset, not branch divergence, caps, or spatial truncation. The right fix is to compare the
**final decorated tile sets** of the two arms and handle the intervention tile explicitly.

## Correction to a claim this note made earlier

An earlier version of this note cited figures of **107, 368 and −53** as evidence that "genuine free
choices unlock large cascades." **Those numbers are retracted as support.** They came from a separate
exploratory debug that placed an *arbitrary* option (option 0) on *all* two-way ties — not the actual
surviving option on settlements — so they are not the pilot results above and do not confirm anything.
I over-read a throwaway probe as a signal. That was exactly the kind of get-ahead-of-the-data error
pre-registration and peer review exist to catch, and Astra caught it.

## Honest status

**"The genuine free choices are the load-bearing ribs" is a hypothesis, not a finding.** What is true:
some choices unresolved by the *bounded* forced-only test (radius 10·S, 60 rounds) are candidates for
substantial forced growth after commitment — their size, robustness, and persistence remain untested.

## Next (unchanged)

Either (a) a clean fresh pre-registration of rib length computed by comparing final decorated tile sets
on genuine free choices, with larger radius/cap and new worlds for confirmation, or (b) the faithful
same-class motif renewal along the actual hollow active-skin, with local-active-step clocks, waiting,
burial and censoring tracked directly.

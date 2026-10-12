# The speed of now: why do some choices make the present rush ahead?

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md).*

**Why.** In `thread_influence/` we noticed that after a two-way choice, the two alternative presents
can advance at very different speeds: one laid 24 tiles before needing another guess, the other 90. So
the "speed of now" (tiles laid per slice) is not fixed. A choice can speed it up or slow it down. What
sets it, and does it last?

**The set-up.**

- 24 fresh ordinary worlds were grown with the patient scheduler.
- At each of the 70 two-way choices, both options got their own future, grown 40 slices ahead.
- For each future, we measured three things:
  - its **burst**: tiles laid before it next has to guess;
  - the **piece** of the wiggle room F it keeps;
  - its tiles over time.

> **Corrections after Astra's review (2026-10-12).** The registered results stand as reported. These
> notes change how far they reach. The numbers come from [`recheck_EXPLORATORY.py`](recheck_EXPLORATORY.py)
> ([`results/recheck_EXPLORATORY.txt`](results/recheck_EXPLORATORY.txt)).
>
> 1. **Burst, activity and front speed are three different things.**
>    - Tiles before the next guess measure the *amount* of forced growth.
>    - Tiles per slice measure *activity*.
>    - Neither measures how far the front moves per slice.
>
>    The picture shows **broader activation in this example**. It does not yet show faster propagation,
>    or the whole front being activated.
> 2. **"36 distinct choices" were 36 distinct *activity traces*.** I grouped choices by their tile
>    counts, not their geometry, and 6 of those 36 traces actually came from more than one different
>    patch. Regrouped by geometry, S1 still holds in most groups, and no group has mixed outcomes:
>    - by the tiles within 4 edges of the choice: 22/27 groups;
>    - within 8 edges: 29/34 groups;
>    - by the whole patch: 33/38 groups.
>
>    By world, S1 holds in the majority of choices in **all 24 worlds**.
> 3. **Unfinished bursts are lower bounds, so S2 and S3 aren't independent tests.**
>    - 61 of 67 smaller-piece bursts never ended within 40 slices (13 of 67 larger-piece ones didn't
>      either).
>    - In **every** S2 pair, the late window (slices 21–40) still overlapped at least one burst, so S2
>      partly compared a burst with itself.
>    - In S3, 11 of 65 pairs compared two identical quantities (neither burst had ended), and 50 more
>      had one unfinished burst.
>
>    The registered failures stand, but they **don't establish a lasting speed difference**. That needs a
>    window *after both first bursts finish*, reporting the pairs that never get there.
> 4. **Equal splits.** Two choices split the wiggle room exactly 50/50 (difference < 0.01). There is no
>    meaningful "smaller piece" there, so they are set aside: S1 becomes **60/65**.
> 5. **Dead options, checked properly.** The empty/point classifier confirms all three dead options have
>    genuinely **empty** F (not just zero area), and that each jams at slice 14. "Fastest of all"
>    overstated it. Those futures outgrew their *own live siblings* before jamming, but several live
>    futures laid far bigger bursts.
> 6. **"Surprise" needs naming.** The quantity is **window information gain**: −log₂ f, where f is the
>    share of the window kept. It is information gained if the hidden offset is uniform (REVEAL-like).
>    Under SELECT's fair coin, both options have probability ½, so neither is more "surprising" there.
> 7. **The empire is a guide, not a claim.** A burst grown by local forcing isn't automatically every
>    tile that all possible completions share. The safe claim: **a choice can unlock very different
>    amounts and patterns of forced growth.**

## Scorecard

| | prediction | result | |
|---|---|---|---|
| S1 | the option keeping the **smaller** piece of F has the larger burst (≥ 70% of choices) | **60 / 67** (90%); without the two 50/50 splits: 60 / 65 (see correction 4) | ✅ HELD |
| S2 | the speed difference evens out (late-rate gap uncorrelated with burst gap, \|ρ\| ≤ 0.2) | ρ = **+0.72** | ❌ FAILED |
| S3 | the head start fades (total gap at slice 40 < half the burst gap, in ≥ 60%) | **25 / 67** | ❌ FAILED |

*A note on counting:*

- Different worlds often met the same choice, so the 67 live choices form **36 distinct activity
  traces**. These are traces, not distinct situations; see correction 2 for the grouping by geometry.
- Counting each trace once gives S1 29/36 and S2 ρ = +0.72. S3 is 8/36.

![speed of now](figures/speed_of_now.png)

*Left: each future's burst against the piece of wiggle room it keeps. Middle: tiles laid slice by
slice for both futures of every distinct activity trace. Right: one choice drawn after 20 slices. The
option that decides more (gold) has laid tiles along a much longer stretch of the front, while the other
(blue) has only filled in near the choice point (red star). That is broader activation in this example,
not yet a measured propagation speed.
([`figure_EXPLORATORY.py`](figure_EXPLORATORY.py))*

## What it means (plainly)

- **A choice that decides more unlocks more forced growth.**
  - Every choice splits the wiggle room into two golden pieces. The option that keeps the *smaller*
    piece (the one that pins the hidden position down more) almost always sets off a long run of
    forced tiles.
  - The trend runs right across the shares (Spearman −0.78 between piece kept and burst):
    - keeping 0.146 of F gives a burst of ~770 tiles;
    - keeping 0.854 gives a burst of 24.
  - The smaller-piece future needed a guess in its 40 slices only 9% of the time. The larger-piece
    future needed about one guess each.
- **It isn't only the pauses.** Even comparing the same slices while both are still running on forced
  tiles alone, the decided future lays about **twice as many tiles per slice** (14 vs 8). The picture
  shows a likely reason in one example: its forced tiles spread along a much longer stretch of the
  front, while the other only fills in locally. Whether that is "more of the front active" or "the
  front moving faster" is the next test.
- **Both "it evens out" predictions failed, but that doesn't show the difference lasts.** Most
  smaller-piece futures were **still in their first burst at slice 40**, so the late window mostly
  measured the burst again (correction 3). Whether speeds even out after both bursts end is untested.
- **Dead options rush, then die.** In the three choices where one option was impossible (F confirmed
  empty), the doomed option laid ~200 tiles in 13 slices and then jammed. Its live sibling laid only 4
  tiles before needing the next guess. So the impossible future outran *its own sibling* right up until
  it couldn't go on. (Many live futures laid far more.)

## The "how come?" we haven't answered yet

- **This is not a general "more pinned = faster" law.** An exploratory follow-up
  ([`pinned_speed_EXPLORATORY.py`](pinned_speed_EXPLORATORY.py)) followed each main world through its
  history.
  - Each time a choice shrank F, the share of the front laid per slice went **up only 25 times and down
    41 times**.
  - That comparison is muddied by the world growing (bigger patches lay a smaller share of their front
    per slice). Still, it means the rule is about **the two futures of one choice, compared at the
    same moment**, not about a world's overall pinnedness.
- **A guess at the mechanism (not tested):** Conway's **empire**, i.e. the tiles a patch forces around
  itself. The rarer an option, the smaller its region of the hidden window, and the more of its
  surroundings it dictates. A rarer option would then have a bigger empire, and its empire spreads
  along the front.
- *If that's right, forced growth follows the choice's* ***window information gain*** *(−log₂ of the
  share kept). That is "surprise" only if the hidden offset is uniform (correction 6). A locally forced
  burst also isn't the full empire (correction 7).*

## Limits

- Ordinary worlds only, one scheduler, and futures watched for 40 slices only.
- The burst was capped at 40 slices, and most smaller-piece bursts hit the cap. So their bursts are
  underestimates, and the late-rate window (slices 21–40) was often still inside the burst.
- The guesses in the two futures share a random stream but land in different places, so the long runs
  are not perfectly paired.
- Repeated identical choices inflate the raw counts. The distinct-only counts are given above.

## Files

- `speed_of_now.py`: the study. Writes `results/speed_of_now_report.txt`, `results/worlds.json`,
  `results/run.log`.
- `pinned_speed_EXPLORATORY.py`: the follow-up. Writes `results/pinned_speed_EXPLORATORY.txt` and
  `results/replay_EXPLORATORY.json`.
- `figure_EXPLORATORY.py`: writes `figures/speed_of_now.png`.

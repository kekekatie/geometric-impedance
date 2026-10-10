# The gold thread: what can continue through the growing now? (exploratory stage)

*Exploratory: no predictions were registered for this stage. It answers the first step of
Astra's handover (relayed by Katie, 2026-10-10): propose the smallest defensible continuation rule,
show it, and say what it would let us conclude, before any pre-registered test.*

**Astra's guiding thought:** *perhaps the process that makes the next piece of reality definite is also
the process that carries influence through it.*

> **Correction (2026-10-10, same day, before any test):** findings 1 and 2 below are true but **follow from definitions**, so they are not discoveries.
>
> - **Finding 1:** any edge with tiles on both sides continues a ribbon, so ribbons can only stop where an edge has one tile, which is the frontier by definition. Each tile has one way in and one way out, so ribbons can't branch. This holds for *any* rhombus tiling.
> - **Finding 2:** any decagonal hole with sides one edge long has 10 edges, so 10 ribbons end there, fillable or not. That the decapod's ends *can't be joined* is just its definition (no legal filling).
> - **"Dislocation-like charge" is too strong.** The lift closes around the hole, so there is no net offset like a crystal dislocation's.
> - **Arrows:** a probe showed that ribbons don't carry a single constant arrow (`results/arrow_probe_EXPLORATORY.txt`). In 170 of 180 ribbons in the reference tiling, both arrow kinds (Penrose single and double) appear in both directions. There is no simple per-ribbon arrow "charge" to count at the hole.
> - **Test A (conservation) is therefore dropped as uninformative.** Findings 3 and 4 (a choice decides mainly one ribbon along the now; observation-time differences between siblings) stand.

## The proposed continuation rule: ribbons

The tiling supplies exactly one local continuation relation of its own. We don't have to import one.

- Every rhombus (two half-tiles) has two pairs of parallel edges, each pair in one of 5 direction
  families.
- A **ribbon of family j** is the chain made by stepping across a family-j edge into the next tile,
  then leaving through that tile's opposite (parallel) family-j edge, and so on.
- The ribbons are exactly what our 5D lift counts: crossing a family-j ribbon changes the hidden
  address K_j by one.

How the rule answers Astra's checklist:

| Astra's question | Answer under the ribbon rule |
|---|---|
| What makes two occurrences the same kind? | The same direction family j. |
| What makes a later occurrence a *continuation*, not a recurrence? | **Contact.** The later tile shares a family-j edge with the earlier one (or is the other half of its rhombus). Identity comes from the chain of shared edges, never from resemblance. |
| Allowed translations or rotations? | None. Nothing is matched by shape. |
| Continuation | A new tile joins the ribbon's chain. |
| Branching | Impossible by construction: each tile has one way in and one way out. Confirmed: no ribbon has more than 2 open ends. |
| Loss | A ribbon end that can never be continued. |
| Insufficient observation | An end on the frontier, i.e. unfinished. This counts as **censored**, never as lost. |

## What the exploration found ([`ribbons_EXPLORATORY.py`](ribbons_EXPLORATORY.py), [`checks_EXPLORATORY.py`](checks_EXPLORATORY.py))

These come from one ordinary world (954 half-tiles, 121 slices, 4 choices) and one decapod world.

1. **Ribbons are never lost inside a growing world.**
   - All 90 open ribbon ends sit on the frontier; none are inside.
   - Of 51 ribbons, none branches: 40 have 2 open ends, 10 have 1 and 1 has 0. Wherever a ribbon has
     fewer than two, the missing end sits at a half-rhombus on the frontier.
   - Ribbons are **re-made slice after slice and conserved**. The model's one defensible "persisting
     thread" cannot decay in legal growth.
2. **The only place ribbons end for good is the decapod's hole: exactly 10 ends, 2 per direction**
   (decapod seed 3, 800 tiles).
   - The unfillable decagon is where ten threads stop and can't be joined up.
   - That is how a *dislocation* works in a crystal: a place where lattice lines end, carrying a
     conserved "charge". It is a concrete handle on Astra's speculative idea that decapods might be
     mass-like. (The lift still closes around the hole, because the ends pair up by direction:
     in = out for each family.)
3. **A choice mainly decides one ribbon lying along the now.** In each of the 4 choices, 51–57% of
   the tiles the choice decided belong to a **single ribbon** running along the front. The rest is its
   immediate neighbourhood.
   - So the "strip" found in `../fragility/` is essentially **one ribbon's path being decided**.
   - In Penrose language, that is a worm choosing which way it zig-zags.
4. **Gold ribbons crossing a decided strip do continue; they don't vanish.**
   - The sibling comparison first looked like "continues in only one sibling" for some ribbons. It
     wasn't loss. After the choice at slice 2, one sibling grew only 24 tiles in 7 slices (it then
     needed a new choice), while the other grew 90. After slice 31, it was 42 against 83.
   - The difference is observation time, exactly as Astra warned.
   - Side observation, worth its own look: **a choice can change how fast the now moves forward** in
     the alternative present that follows it.

**Pictures:** [`figures/gold_thread.gif`](figures/gold_thread.gif) (animation) and
[`figures/gold_thread_frames.png`](figures/gold_thread_frames.png) (six frames).

- **Gold:** five ribbons through the centre, one per direction, re-made as the world grows.
- **Blue:** the active frontier (last 2 slices).
- **Grey:** the settled past, which never changes.
- **Black dots and red outlines:** choices, and the strips they decided.

## What this lets us conclude, and where it could mislead

- **Conclusion so far:** in this model, *continuation itself* is cheap and conserved. Threads are
  re-made every slice and cannot end except at a defect. So nothing here "decays" in the sense of a
  thread stopping.
- **What a choice changes** is a thread's *path*: which way a ribbon running along the now zig-zags.
  It never decides whether the ribbon exists.
- **Where it could mislead:**
  - A ribbon is a line through the growing world, not a small localised object. Ribbons that cross
    the front are worldline-like; ribbons that lie along the front are like strings within the now.
    Calling either a "particle" would be forcing it.
  - Patterns *carried by* a ribbon (its sequence of crossings) could still change at a choice. Those
    are recurrences along a thread, and they would need the ribbon link to count as continuations.

## Candidate pre-registered tests (to choose together)

- **A. Conservation, on fresh worlds** *(dropped: uninformative, see the correction above)*:
  - ribbons never end or branch in legal growth;
  - every decapod hole ends exactly 10, 2 per family;
  - fillable rings end 0 once filled.

  Quick and solid. It would turn "the decapod is a charge-like place where threads end" into a banked
  fact.
- **B. Choices set the speed of the now:** after each choice, how differently do the two alternative
  presents advance (tiles per slice, slices until the next choice)? Does the faster one have anything
  in common across choices?
- **C. Fable's wall (the slack test):** does the hidden-window slack shrink at each choice, step by
  step, while the decapod starts at zero?
- **D. Influence along threads (Astra's guiding thought):** after a choice, does the difference spread
  *along* the ribbons that cross the decided one, and at the ~1 edge/slice speed limit? That would test
  whether the process that makes things definite is also the one that carries influence.

## Files

- `ribbons_EXPLORATORY.py`: growth, ribbons, sibling continuation, decapod hole, figures
  (`python3 ribbons_EXPLORATORY.py [world] [n_tiles]`)
- `checks_EXPLORATORY.py`: branching check, and whether the decided strip is one ribbon
- `results/ribbons_EXPLORATORY.txt`, `results/checks_EXPLORATORY.txt`
- `figures/gold_thread.gif`, `figures/gold_thread_frames.png`

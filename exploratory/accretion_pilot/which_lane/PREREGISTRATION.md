# Which lane? Does the side of the cut name where the ribbon runs?

*Pre-registration, written and committed before any code for this study exists. It grew from Argon's
"spine handedness" idea (relayed by Katie, 2026-10-20), reframed in operational terms.*

## Where this comes from

`cut_direction/` and `settled_test/` (the paper *Decided before it is built*) found:

- a choice's cut in the wiggle room F predicts the **family** (direction) of the changed strip;
- the initial forced burst carries that family in 45/45 configurations, with a connected core
  holding ~2/3 of each side's changed tiles.

De Bruijn's pentagrid picture suggests more. The two options of a choice may place a family-*j*
ribbon on two **adjacent parallel tracks**. If so:

- option A's core and option B's core should sit side by side, offset *across* the strip;
- which side of the cut line a branch's piece of F lies on might say **which lane** its ribbon takes.

## Words

- **Configurations:** the 45 distinct situations of `settled_test/`, rebuilt exactly with its
  `world()` (same seeds). Nothing about lanes has been computed for them before.
- **Initial bursts, changed region, core:** as in `settled_test/`. Forced-only growth of each option
  (cap 40 slices, no later choices). Each side's core is its largest connected chain of the predicted
  family *j*.
- **Cut and its sides:** the cut line between the two options' pieces of F, read after each option's
  first forced slice. Option A's piece lies on the side its facet normal **n_A** points to (A keeps
  n_A · t ≥ c). Recorded with the facet's window layer (rank 0–3).
- **Window side of A:** s_A = sign(n_A · ζ^(2*j*)), meaning whether A's piece lies towards +ζ^(2*j*)
  or away from it.
- **Lane offset:** **e_j** is the unit vector of family *j*'s physical edges (angle 18° + 72°·*j*),
  which points *across* the strip. offset = (centroid of A's core − centroid of B's core) · e_j, in
  edges.

## Predictions (fixed now)

**L1: Two lanes.** |offset| ≥ 0.25 edges in at least 80% of configurations: the cores sit side by
side, not on top of each other. Confidence about 70%.

**L2: The window side names the lane.** The product sign(offset) × s_A takes the **same value**
(always +1, or always −1) in at least 90% of configurations with |offset| ≥ 0.25. Confidence about
45%. One risk: the window's pentagons alternate orientation between layers, which could flip the
relation by layer.

## Reported, not tested

- L2 broken down by the cut facet's window layer (rank 0–3).
- The distribution of |offset|. Is there a typical lane spacing?
- The same offset measured with *all* changed tiles of each side instead of the cores.

## Limits I already know

- These are the same 45 configurations as `settled_test/`, so this is not an independent sample of
  situations. It is a new, pre-registered measurement on them.
- Centroid offsets of finite, possibly unequal-length cores are a proxy for "which track".

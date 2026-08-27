# Results — why each vertex type prefers its own depth (one profile, sampled radially)

*EXPLORATORY. Code: `preferred_depth.py`; figures `preferred_depth_golden.png` (the window
painted with confined weight + vertex types tiling it) and `preferred_depth_profile_golden.png`
(the radial profile + type depth-bands). Follows `RESULTS_CONFINED_REFINE.md`, which found each
vertex type has a reproducible but **class-specific** preferred perpendicular-space depth for
E≈0 confined-state weight, and asked why.*

## The answer

**There is one window-wide confined-weight profile, and each vertex type is a different radial
slice of it.** Two facts, one picture:

1. **Vertex types tile the acceptance window radially.** In cut-and-project a vertex's type is
   fixed by where its perpendicular-space coordinate lands in the window, and here that
   organization is largely **concentric**: painted onto the window, the common types form
   ordered rings — type 9 on the outer edge, type 17 in the dead centre, the rest stacked in
   between (right panel of the map; and the depth-band boxplot). This is geometry, not
   dynamics.
2. **Confined weight follows a single-humped radial profile.** Confined-state weight is low at
   the window edge (depth ≈ 0.05), rises to a clear peak at depth ≈ **0.30–0.40**, then falls
   away toward the window centre. One preferred *band*, partway in.

Compose them and the class-specificity resolves. Each type occupies its own depth-band, so each
type sees a **different portion of the same profile**:

- a type straddling the peak (5, 6) reads high, and peaks mid-band;
- an **edge** type (9) sees only the profile's *rising limb* → its weight climbs with depth,
  so its "preferred depth" sits at its deep end;
- a **central** type (17) sees only the *falling tail* → low weight, preferred depth at its
  shallow end.

So the "class-specific preferred depths" of the previous result (normalized 0.19–0.72) are not
independent quirks — they are one **strong first-order radial profile with a broad preferred
band** (peak ≈ 0.35), sampled at the different radii the types happen to occupy. It reconciles
the earlier caution without overclaiming: rather than "no shared band" vs "one universal band",
the truth is a broad shared radial band that radially-ordered types *taste differently*, on top
of which finer, non-radial structure still sits (the spread is wide and the painted window is
mottled — see below). And vertex type is **strongly organized by window depth** (ordered
depth-bands), not *purely* set by it — the window is 2D, and angular / finer placement remain.

## How strong is the radial story

Held-out (3 offsets, golden, extent 14), predicting confined weight:

| descriptor | held-out R² |
|---|---|
| 1D hull-depth (radial position only) | 0.44 |
| vertex type (a window sub-region) | 0.34 |
| perp-position + type | 0.59 |

Radial position alone already carries the bulk of the *generalizable* signal, and vertex type
(itself a radial region) carries a similar amount — consistent with "one radial profile,
sampled by radial regions". The two together add up, and raw 2D perp-position generalizes
*worse* than the engineered radial coordinate (0.20) — i.e. the extra, non-radial fine
structure visible as mottling in the window map is **partly realization-specific** and does not
transfer across offsets. So the radial profile is a strong first-order account, not the entire
field.

## What this is and isn't

- **Is:** a clean geometric "why". The apparent per-type preference is one confined-weight
  profile over the window, read at each type's own radius. Ties the confined states directly to
  perpendicular-space (window) position — the mechanism-level statement "spectral role is set by
  global placement" made concrete and radial.
- **Isn't:** a claim that confined weight is *purely* radial (it isn't — there is finer,
  partly patch-specific structure), nor yet shown across families (golden only here; the two
  facts — radial type-tiling and a window confined-weight profile — should generalize, and
  that is the cheap next check).

## The decomposition, and the next split (GPT's steer)

The picture that fits everything, including the earlier within-fine-type survival, is:

> spectral role ≈ **global radial field** + **type-specific radial sampling** + **residual
> non-radial structure**.

The first-order term is the radial profile; the residual is the mottling and the within-type
address effect that survived exact fine-configuration controls. The sharpening step is to
**split the address effect into a radial-depth component and a non-radial (angular / finer
placement) component**, and quantify: (1) how much confined weight depth alone predicts;
(2) how much the non-radial part adds after depth is included; (3) whether, within a fixed fine
type, non-radial address still helps. Reported in `RESULTS_ADDRESS_SPLIT.md`.

## Files

`preferred_depth.py` · `preferred_depth_golden.png` · `preferred_depth_profile_golden.png` ·
follows `RESULTS_CONFINED.md`, `RESULTS_CONFINED_REFINE.md`, `RESULTS_COHERENCE.md`.

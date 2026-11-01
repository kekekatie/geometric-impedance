# Phase 3 — frozen prospective protocol: legal single-move repair feasibility

**Status: prospective.** Written and frozen *before* any repair outcome is
inspected. The jam outcomes themselves (which B continuations jammed, at which
step) are already known from Phase 1 and the saved closure records; what is
*not* known, and what this protocol governs, is whether a single legal
rearrangement can restore growth, and what happens to the A/B readout after it.

This is a protocol for a **prospective exploratory intervention**, not a
confirmatory hypothesis test. No pass/fail bar is pledged. "No legal move
exists" is a valid result and will be reported as such. Matching rules are
never relaxed to obtain a rescue.

Frozen on 2026-11-01. Any change after the first repair outcome is read is
recorded as a dated deviation in `PROTOCOL_DEVIATIONS.md`, not edited here.

---

## 1. Scope and move class

One move class only: a **three-rhombus hexagon rearrangement** (the Penrose
"simpleton" / phason flip), represented in the engine's decorated half-tiles
(6 half-tiles = 3 rhombi). No other move class. At most **one repair per
continuation**. No multi-flip search, no enlarged skin, no backtracking, no new
seed sweep.

The repair worker receives **only** the declared retained active skin at the
jam trigger (`skin_of(trigger_state)`) plus legitimate scheduler metadata
(random stream value, jam step, step-44 horizon, prune radius). It must not
read the historical full patch, deleted/buried tiles, the A/B choice truth, or
any saved trajectory.

## 2. What counts as a candidate move

A **flip cluster** is a set of exactly 6 decorated half-tiles, wholly contained
in the retained skin, forming 3 rhombi whose union is a single convex hexagon
`H` with exactly one patch vertex strictly interior to `H` (the *flip vertex*).

- **Geometric candidate:** such a cluster for which the hexagon `H` admits a
  *second*, distinct dissection into 3 rhombi / 6 decorated half-tiles with the
  same outer hexagon boundary (the flip exists as a geometric rearrangement),
  regardless of decorated legality.
- **Fully legal candidate:** a geometric candidate whose alternative filling is
  accepted by the engine's unmodified `legal()` test for every one of its 6
  half-tiles *in the surrounding retained skin* — i.e. no overlap, no gap, no
  duplicate, every touched vertex a contiguous atlas star or complete atlas
  star (no forbidden vertex star), and no invalid decoration — **and** whose
  outer hexagon boundary (the 6 boundary edges shared with the rest of the
  skin) is bit-identical before and after.

Geometric candidates and fully legal candidates are **counted separately**. A
geometric flip is not automatically legal under decorated Penrose rules.

## 3. Eligibility for repair (un-jam relevance)

The jam is a frontier phenomenon: `patient()` halts at the first frontier edge
with zero legal candidates (a *dead site*). A flip can only matter if it changes
the local configuration at a dead site. A fully legal candidate is **eligible**
for a jam only if at least one of the jam's dead frontier edges has an endpoint
vertex that is incident to the flip cluster (so the flip can change that edge's
vertex stars). Eligibility is a geometric property of the move and the dead
sites; it does not look at future survival.

If a flip cannot touch any dead site (e.g. every legal flip is purely interior
and leaves the exterior boundary — and hence the whole frontier — unchanged),
there is **no eligible move**, which is a valid result.

## 4. Deterministic order (fixed before any outcome inspection)

For a given jam, eligible fully-legal moves are ordered by this key, computed
from geometry alone:

1. ascending distance of the flip vertex from the nearest dead-site edge
   midpoint;
2. then ascending `L.key(flip_vertex)` (rounded physical coordinate, lexicographic);
3. then ascending sorted tuple of the 6 cluster tiles' `D.dkey` values.

The **first** fully legal eligible move under this order is attempted. The move
is never chosen by future survival, readout outcome, or memory recovery.

## 5. Repair + resume

1. Export the retained state at the jam trigger (done in Phase 1), before any
   mutation.
2. Apply the single chosen flip to the retained skin: remove the 6 cluster
   half-tiles, add the 6 alternative half-tiles. Validate (Section 2) — abort
   if validation fails (that move was not fully legal; fall through the order).
3. Resume growth with the **original** patient scheduler and the **original
   random state** (re-seeded from the same stream; the scheduler is
   deterministic given the tile set and RNG) to the original **step-44**
   horizon. Repair events are logged separately from growth steps.
4. Compare against the **no-repair replay** from the identical jam-trigger
   checkpoint (which re-jams immediately at the same dead site).

Resuming from the active skin uses the frozen `ActiveSkin` engine where
possible; if resumption must run on the reconstructed skin as a fresh patch,
that is labelled as such. Because the historical continuation grew from the
full patch, a skin-only resume is a *different instrument* from the full-history
growth and is reported as skin-resume, not as the original trajectory.

## 6. Outcome categories (reported separately, per continuation)

- (a) no eligible geometric move;
- (b) geometric moves exist but none legal;
- (c) legal eligible move(s) exist, repair attempted;
- (d) immediate growth restored (the dead site(s) gain candidates and ≥1
  patient step proceeds);
- (e) later re-jam (growth restored but jams again before step 44);
- (f) original step-44 horizon reached.

## 7. Validation of the generator and validator (controlled examples)

Before running on any jam, the move generator and validator are checked on
controlled examples, including rejection cases:

- **Acceptance:** on a clean interior patch, every detected geometric flip whose
  alternative dissection is a genuine Penrose configuration is either accepted
  as legal or rejected with a named decorated-rule reason; a known-flippable
  hexagon yields exactly one alternative distinct dissection.
- **Rejection:** a fabricated "flip" that (i) overlaps an existing tile, (ii)
  leaves a gap, (iii) changes the outer hexagon boundary, or (iv) creates a
  forbidden vertex star is rejected, each by the correct reason.
- **Boundary invariance:** the 6 outer hexagon edges are bit-identical pre/post
  for every accepted move; any move that alters them is rejected.
- **No archive access:** the generator reads only the retained skin passed to
  it; it never dereferences the full patch or choice truth.

If the generator cannot be validated to this standard in this pilot, Phase 3 is
reported as blocked at the generator stage, with the validation gaps named, and
no repair outcomes are claimed.

## 8. Boundaries (inherited from the task)

No forcing a seam closed, no new defect core, no nonzero-holonomy claim.
Single-valued vertex coordinate differences sum to zero around any closed loop.
No quantum-error-correction, elasticity, particle, or indefinite-growth claims.

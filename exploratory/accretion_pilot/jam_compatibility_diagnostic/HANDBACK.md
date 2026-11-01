# HANDBACK — jam compatibility diagnostic

*2026-11-02. For Katie / Astra. A bounded diagnostic study, no preferred outcome.
Branch `claude/jam-compatibility-diagnostic`. Source inspected: `aa371d4` (the
jam-repair pilot + two-flip side-quest), confirmed as the latest prior work.
Frozen engine imported read-only from `84130b9`; nothing merged or force-pushed;
the original engine, the reader and the historical results are unchanged.*

---

## For Katie first — what changed in the picture

Astra asked us to pin down *where* and *when* a growing tiling first becomes
impossible to finish, and whether loosening the inner edge of the kept tiles
changes anything. Four things came out of it:

1. **"Zero area" was the lazy way to say "impossible" — and I checked it
   properly this time.** Before, I'd declared the tiling impossible by noticing a
   shape had zero area. But zero area could also be a sliver or a dot that is
   perfectly fine. So I added a real test (does *any* valid solution exist?). The
   answer: it is **genuinely impossible**, not a sliver — and comfortably so, far
   from any rounding worry. My earlier conclusion was right; now it's properly
   earned.

2. **The impossibility arrives long before the tiling visibly gets stuck.** For
   the world-7 case, the tiling becomes impossible-to-finish at **step 9**, but
   doesn't visibly stall until **step 23**. It's doomed ~14 steps before it
   notices. (World 5: doomed at 17, stalls at 42.) The fatal move is the first
   *free choice* the tiler makes.

3. **The real conflict is tiny, and it is NOT where the tiling gets stuck.** The
   whole impossibility boils down to **two tiles** whose requirements point in
   exactly opposite directions — an unwinnable tug-of-war. And those two tiles
   are **far apart** (about 8–9 tile-widths in world 7, ~20 in world 5), and
   several tile-widths away from the spot where growth actually halts. So the
   visible stall is just where the tiler *bumps into* a contradiction that was
   set up elsewhere, between distant commitments.

4. **Loosening the inner edge changes nothing — because the conflict lives on the
   outer edge.** We peeled away inner tiles in stages (315 → 170). The tiling
   stayed impossible, the stuck spot stayed stuck, and the A/B history stayed
   unreadable, every single time — because the two quarrelling tiles sit near the
   *outer* edge, so releasing the *inner* edge never touches them.

The one-line version: **this frontier can't continue because of two distant,
opposed commitments near the outer edge, locked in from the first free choice;
releasing the inner edge doesn't reach them.**

---

## Observations (what was measured)

Exact case identifiers in `results/case_identifiers.json` (world 7, fork config
key `4250b244a8d0887c`, streams `[20262655433, 20262655534]`; world 5, fork key
`3a33a0d534922f0e`). "F" = the compatibility region of offsets consistent with
every vertex; computed from the **frozen** `Sl.constraints` / windows.

**Part 2 — feasibility, not "zero area"** (`results/part2_*`). An independent
Chebyshev-radius LP over the same frozen constraints classifies the region as
positive-area / lower-dimensional / infeasible / unresolved, validated on
controlled polygon/segment/point/empty examples (`tests/test_feas.py`, all pass).
Every jam-trigger region is **infeasible**, Chebyshev radius `r* = -0.0816`
(world 7) and `-0.0504` (world 5), stable under `±1e-6` perturbation — not a
feasible point or segment. F(full) and F(retained) share the same binding
constraints.

**Part 3 — first loss of compatibility** (`results/part3_*`). Per-step
feasibility of the recorded continuations. The region first becomes infeasible at
**step 9** (world 7, both streams) and **step 17** (world 5), versus the visible
jams at **23** and **42** — i.e. **before** the engine's local zero-candidate
halt, at the first free-choice tile (the triggering tile's location is recorded).
Gauge consistent across steps (same four occupied layers throughout).

**Part 4 — the conflicting constraints** (`results/part4_*`, figures
`part4_w{5,7}_patch.png`). An inclusion-minimal infeasible subset (deletion
filter) is **2 constraints from 2 vertices** (world 7; world 5 jam-state 3), whose
two window normals are **exactly anti-parallel** — an opposing squeeze; the
severity `r*` is identical at the first-infeasible step and at the jam, i.e. the
same conflict carried forward unchanged. The originating vertices are **separated
across the retained ring** (world 7 ~8.6 tile-edges apart, ~4 from the dead site;
world 5 ~20 apart, 13–17 from the dead site). The subset is inclusion-minimal, not
minimum-cardinality, and not unique (alternatives recorded).

**Part 5 — inner-rim erosion** (`results/part5_*`). Inner tiles removed in four
nested levels (315→260→226→170), outer growth boundary and dead sites held fixed,
true-frontier vs pruning-exposed edges distinguished and preserved. At every
level: region stays **infeasible** (identical `r*`), the original dead sites keep
**0 candidates**, **0** previously-tested local rearrangements become legal, and
the frozen A/B reader stays **empty/incompatible**. Both conflicting vertices
remain present at every level (they are on the outer band), which is why nothing
changes.

## Interpretations (held carefully)

- The first global incompatibility **precedes** the visible local jam, and couples
  **separated** parts of the retained ring — both were open possibilities in
  Astra's brief, and both are supported here for these cases.
- Releasing the inner boundary did **not** change rearrangement availability or
  readability here — because the conflict is not on the inner boundary. This is a
  negative result about *where* the conflict sits, not a general law.
- An infeasible / empty-reader outcome is **not** evidence that historical A/B
  information has disappeared; it means a jammed configuration admits no consistent
  offset to read.
- No claim of universal local rigidity; no identification of the anti-parallel
  squeeze with a Burgers defect, a particle, an energy barrier, or thermal
  protection. The `pB≈0.854` association stays descriptive. An IIS is a witness,
  not a proven causal repair target.

## Unresolved numerical questions

- The feasibility verdict is a **float LP over φ-irrational data**. `r*` is far
  from any tolerance, so "infeasible" is robust numerical evidence, **not a
  symbolic proof**. An exact `Q(√5)` certificate is scaffolded (`feas.Q5`) but not
  wired into a full exact 2-D feasibility check; that would upgrade "robust
  numerical" to "certified" for the headline cases.
- Lower-dimensional (point/segment) regions are inherently **fragile** under
  perturbation (shown in the tests); none of the studied states is degenerate, so
  this did not bite here, but a state that *were* degenerate would need the exact
  check.
- IIS non-uniqueness: we report inclusion-minimal witnesses under a few drop
  orders; the full set of minimal witnesses, and the minimum-cardinality one, were
  not enumerated.

## Recommended next work

- Wire the exact `Q(√5)` 2-D feasibility check for the headline states, to replace
  "robust numerical" with "certified".
- Since the conflict is a distant anti-parallel pair on the outer band, the move
  class that *could* matter is one that touches **both** conflicting tiles at once
  (a correlated outer-band rearrangement / chain), not a single local flip and not
  inner-rim release — a separate, explicitly-constructed experiment.
- Trace, across more of the 11 recorded jams, whether the first-infeasible step is
  always the first free choice, and whether the conflict pair is always
  anti-parallel and non-local.

## Reproduction, deliverables, status

See `README.md` for commands. Python 3.12; numpy/scipy/matplotlib; the frozen
reader is standard-library only. Validation: `tests/test_feas.py` (certifier) and
the pilot's `tests/test_hexflip.py`. Machine-readable results carry exact case ids
and numerical settings. Figures in `figures/`.

Branch `claude/jam-compatibility-diagnostic`; pushed to
`origin/claude/jam-compatibility-diagnostic`. No pull request (none requested);
nothing merged or force-pushed; no historical result changed. Commit ids are in
the branch history (this HANDBACK lands in the final commit).

Stopping here, per the brief: no automatic expansion to fresh worlds, correlated
rearrangement searches, defect dynamics, or a new paper.

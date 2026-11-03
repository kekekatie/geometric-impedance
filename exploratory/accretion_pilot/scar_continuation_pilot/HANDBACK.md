# HANDBACK — scar-continuation pilot

*2026-11-03. For Katie / Astra / Argon. A bounded pilot; null, ambiguous, or
full-arrest outcomes were equally acceptable. No tile-matching rule was relaxed;
the frozen engine, frozen reader, and reader decision thresholds are unchanged.
Branch `claude/scar-continuation-pilot-2026-11-03`, base commit `d2e075a`,
directory `scar_continuation_pilot/`. All historical files, engine, reader, and
prior pilot/audit directories are untouched.*

Terminology: "retained boundary band" / "active ring" = the study's active skin.

## Plain-language summary (the two questions)

**Q1 — does the historical A/B choice survive in a sub-arc, even though the whole
jammed band is unreadable?** **Yes, and robustly.** On all 11 recorded B-jams the
whole retained band reads `empty_incompatible`, but each one contains a
**contiguous connected sub-arc (20–63% of the band) that reads the correct
historical choice, B** — and crucially it reads B *discriminatingly* (its
offset-region F overlaps the B birth-region but **not** the A birth-region; both
birth regions are genuinely non-empty, so this is a real exclusion of A, not an
artifact). The picture that emerges: **each arc of the band is individually
B-consistent; the global incompatibility lives *between* separated arcs** (they
each pin the hidden offset to a slightly different, B-consistent but mutually
incompatible, place). Honest caveat: a *small* sub-patch has a large F and can
overlap both A and B (`ambiguous`) — we report those too — but the *maximal*
compatible connected arc discriminates B in every case.

**Q2 — if we pin the dead sites as dormant "scars" and keep growing, does it march
on or cascade?** **It marches on.** With strict Robinson/vertex-star legality kept
100% intact and only the *halt rule* changed (pin a zero-candidate frontier edge
instead of halting the whole simulation), **all 11 cases grow past the jam and
reach the step-44 horizon with zero illegal tiles and no total arrest.** Growth
flows *around* the pinned notch. The scars stay in **1–2 connected components**;
they do not proliferate into a perimeter-wide cascade, though they can spread to
roughly half the ring's circumference when the jam happened early (more growth
steps). And after all that extra growth, the **global band is still
`empty_incompatible`** — yet the **historical B choice is still readable in a large
connected sub-arc** (for w7 it actually *grows* from 32% of the band at the jam to
50% at step 44, as new B-consistent tiles accrete).

One-line version: **the jam is globally real but locally porous — the historical B
choice is not lost, it is carried in contiguous arcs of the ring; pinning the dead
sites lets strict-legal growth continue to the horizon around a small, persistent
scar set, and B stays readable in an arc the whole way.**

Important boundaries on these claims: this is a **numerical, model-specific**
result on the recorded B-jams under the fixed projection-window convention; the
global band remains incompatible throughout (scar-tolerant growth is a different,
clearly-labelled scheduler, **not** evidence the baseline jam was unreal); and
post-jam growth is a **new, disclosed trajectory** (same PRNG stream, but the
baseline halted there, so it is not "the" historical continuation). We make no
defect-core holonomy claim and did not alter the reader thresholds.

## Phase 1 — contiguous-arc readout at the recorded jams (no growth mutation)

Whole band vs the maximal compatible **connected** sub-arc (reader under the fork
gauge + A/B birth hypotheses; only connected components scored, so lifts are
single-valued — verified by the path-independence test):

| case | jam | band tiles | whole band | max compatible connected arc | arc verdict |
|------|----:|-----------:|------------|------------------------------|-------------|
| w7-B-s0 | 23 | 315 | empty_incompatible | 32% (100 tiles) | **correct (B)** |
| w7-B-s1 | 23 | 315 | empty_incompatible | 32% (100) | correct (B) |
| w5-B-s0 | 42 | 450 | empty_incompatible | 20% (90) | correct (B) |
| w15-B-s0 | 39 | 551 | empty_incompatible | 63% (349) | correct (B) |
| w19-B-s0 | 39 | 551 | empty_incompatible | 63% (349) | correct (B) |
| w19-B-s1 | 43 | 582 | empty_incompatible | 40% (235) | correct (B) |
| w21-B-s0 | 42 | 450 | empty_incompatible | 20% (90) | correct (B) |
| w21-B-s1 | 42 | 450 | empty_incompatible | 20% (90) | correct (B) |
| w28-B-s0 | 39 | 551 | empty_incompatible | 63% (349) | correct (B) |
| w28-B-s1 | 43 | 582 | empty_incompatible | 40% (235) | correct (B) |
| w29-B-s1 | 43 | 582 | empty_incompatible | 40% (235) | correct (B) |

- **Controls.** Both birth hypotheses are non-empty (w7: area(F_A)=0.0086,
  area(F_B)=0.051; w5: 0.014, 0.037), so "arc excludes A" is a real discrimination.
  The direct reader call and the isolated-subprocess reader agree exactly. The
  single-valued-lift path-independence test passes (two spanning-tree lifts agree
  up to a constant; the reader reconstructs each connected arc as one component).
- **Structure (w7).** Scanning a connected arc outward from the far side of the
  notch, F stays non-empty and reads B up to ~30% of the band, then collapses to
  empty and stays empty — the incompatibility is a between-arc effect.
- **Secondary (witness-complement).** Removing the cooperative-pilot heuristic
  deletion footprint leaves a large remainder whose F is feasible only as a
  *zero-area* point (reads `empty_incompatible` by the reader's positive-area rule)
  plus smaller components that read B or, when tiny, `ambiguous`.
- **Choice tile.** In these cases B has departed the band under pruning, so this is
  an archive-free *geometric* readout, not reading the B tile itself.

## Phase 2 — scar-tolerant continuation (strict legality; pin, don't halt)

All 11 cases, replayed from step 0 with scar-tolerance, same PRNG stream:

| case | jam | final step | reached 44 | +tiles after jam | scar edges | scar comps | scar span (rad) | illegal |
|------|----:|----------:|:---------:|----------:|------:|-----:|-----:|-----:|
| w7-B-s0 | 23 | 44 | yes | +589 | 12 | 2 | 2.90 | 0 |
| w7-B-s1 | 23 | 44 | yes | +589 | 12 | 2 | 2.90 | 0 |
| w5-B-s0 | 42 | 44 | yes | +79 | 2 | 1 | 0.02 | 0 |
| w15-B-s0 | 39 | 44 | yes | +140 | 12 | 2 | 1.29 | 0 |
| w19-B-s0 | 39 | 44 | yes | +140 | 12 | 2 | 1.29 | 0 |
| w19-B-s1 | 43 | 44 | yes | +36 | 4 | 2 | 1.90 | 0 |
| w21-B-s0 | 42 | 44 | yes | +79 | 2 | 1 | 0.02 | 0 |
| w21-B-s1 | 42 | 44 | yes | +79 | 2 | 1 | 0.02 | 0 |
| w28-B-s0 | 39 | 44 | yes | +140 | 12 | 2 | 1.29 | 0 |
| w28-B-s1 | 43 | 44 | yes | +36 | 4 | 2 | 1.90 | 0 |
| w29-B-s1 | 43 | 44 | yes | +36 | 4 | 2 | 1.90 | 0 |

- **No total arrest** in any case; growth flows around the notch to the horizon.
- **Scars stay in ≤ 2 connected components** — not a perimeter-wide cascade. Their
  angular spread grows with how early the jam was (more growth steps → wider), from
  ~1° (w5, jam@42) to ~166° (w7, jam@23).
- **Zero illegal placements** (strict-legality test passes); the final patch has no
  over-full vertex.

## Phase 3 — post-continuation readout (final band at step 44)

| case | final band | global reader | max compatible arc | arc verdict | choice-tile |
|------|-----------:|---------------|-------------------:|-------------|-------------|
| w7-B-s0 | 644 | empty_incompatible | 50% | correct (B) | departed_by_pruning |
| w7-B-s1 | 644 | empty_incompatible | 50% | correct (B) | departed_by_pruning |
| w5-B-s0 | 492 | empty_incompatible | 17% | correct (B) | departed_by_pruning |
| w15-B-s0 | 597 | empty_incompatible | 72% | correct (B) | departed_by_pruning |
| w19-B-s0 | 597 | empty_incompatible | 72% | correct (B) | departed_by_pruning |
| w19-B-s1 | 608 | empty_incompatible | 63% | correct (B) | departed_by_pruning |
| w21-B-s0 | 492 | empty_incompatible | 17% | correct (B) | departed_by_pruning |
| w21-B-s1 | 492 | empty_incompatible | 17% | correct (B) | departed_by_pruning |
| w28-B-s0 | 597 | empty_incompatible | 72% | correct (B) | departed_by_pruning |
| w28-B-s1 | 608 | empty_incompatible | 63% | correct (B) | departed_by_pruning |
| w29-B-s1 | 608 | empty_incompatible | 63% | correct (B) | departed_by_pruning |

Every case: global `empty_incompatible`; maximal compatible connected arc reads
**correct (B)** (17–72%); choice tile departed by pruning. In several cases the
readable fraction *increased* versus the jam (w7 32→50%, w15/w19/w28-s0 63→72%) as
B-consistent tiles accreted.

- The **global band stays incompatible** after scar-tolerant growth (more tiles,
  more constraints), consistent with the audited distributed obstruction.
- The **historical B choice remains readable in a large connected sub-arc**; for
  w7 the maximal compatible arc *grows* (32% → 50%) as new B-consistent tiles
  accrete around the growable frontier.
- Figures: `figures/scar_w7.png`, `figures/scar_w5.png` (jam-core grey, accreted
  tiles blue, pinned scars red, maximal compatible B-reading sub-arc green).

## What this is / isn't

- **Is:** numerical evidence, on the 11 recorded B-jams under the fixed
  projection-window convention, that (1) the historical B choice survives in
  contiguous connected sub-arcs of the globally-incompatible jammed band and
  discriminates B from A, and (2) a strict-legal scar-tolerant scheduler continues
  to the step-44 horizon around a small (≤2-component) persistent scar set while B
  stays arc-readable.
- **Isn't:** a claim that the global band becomes compatible (it never does); a
  defect-core holonomy or physical-memory claim; "the" historical continuation
  (post-jam growth is a disclosed new trajectory); or a result beyond step 44,
  other worlds, or other models. A small ambiguous sub-patch is not surviving
  information; only the discriminating maximal arc is.

## Deliverables & status

`PROTOCOL.md` (frozen before Phase-2 outcomes), machine-readable
`results/phase{1,2,3}_*.json/.csv`, unit tests (`tests/test_scar.py`: single-valued
lift path-independence on connected sub-arcs; strict legality of all placed tiles),
and figures. Reproduction: set `EFP_SNAPSHOT`, then from `src/` run
`phase1_arc_readout.py --all`, `scar_continuation.py`, `phase3_post_readout.py`,
`make_figures.py`. Commit/push to the new branch; no merge, no force-push.

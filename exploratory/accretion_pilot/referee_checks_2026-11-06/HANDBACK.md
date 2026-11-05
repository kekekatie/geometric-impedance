# HANDBACK — referee-proofing checks 3 and 4

*2026-11-05 (folder/branch labelled 2026-11-06 per the brief). For Katie / Fable / Astra.
Exploratory diagnostics on worlds already grown, before drafting Paper 1. A null or
ambiguous outcome was an acceptable result — and, for the two literature-suggested
mechanisms, that is largely what we got. Nothing frozen was modified.*

## Plain-language summary (read this first)

We stress-tested two **mechanisms** that the literature review suggested might explain the
recurring "never A" readout, pre-registering every definition and prediction before looking
at outcomes (`protocol/PROTOCOL.md`, committed first). The reproduction gate passed exactly
(**111 B / 64 ambiguous / 353 empty-incompatible / 0 A**) before any check ran.

**The headline "never A" survived every stress test, but both proposed mechanisms did not.**

- **Is the A/B fork a Conway worm flip?** (Check 4a) — **No, not at the forced-closure level.**
  In **0 of 22** forks is the A-vs-B forced-consequence difference a single worm strip. The
  difference is a **large two-dimensional region** (aspect ratio ≈ 1, often several hundred to
  several thousand tiles), not a one-dimensional strip. Prediction P4a (≥20/22 strips) **failed**.
- **Does "never A" survive local, matched-size arcs, and does any arc ever pick A?**
  (Check 4b) — **"never A" held and got stronger.** Across **233** local 32-tile arcs on the 11
  B-committed jammed bands, **zero** selected A (open or closed convention). Across **1041** arcs
  on the 49 recovery skins, the reader selected A **only on A-true cases** (169 correct
  recoveries), and **never** on a B-committed case. So the reader is not biased against A — it
  reads A when A is true — it simply never picks A where B was committed. The pre-registered
  crossing-vs-parallel split was **not evaluable** because 4a gave no worm line.
- **Is "empty F" a topological defect?** (Check 3a) — **No.** On all **190** boundary loops
  across the 11 bands the perp-space holonomy **b⊥ = 0** exactly (0 lift conflicts; physical
  closure b∥ = 0 confirms the loops are genuine). Prediction P3a **held**. The empty F is not a
  dislocation/disclination.
- **Is "empty F" a sharp step (domain wall) or a smooth ramp?** (Check 3b) — **A smooth ramp.**
  All **11** bands classify as **ramp** (the local best-fit offset drifts gradually around the
  band; no one or few positions carry the change — concentration 7–16% of total variation, far
  below the step threshold). Prediction P3b (step-like) **failed**; P3c is moot.

**One genuinely suggestive exploratory finding** (not pre-registered, clearly labelled): the
reader's discriminating power is **localized to the A/B forced-closure difference region**.
Arcs overlapping that region read decisively (B on B-cases); arcs away from it are mostly
ambiguous. The information that distinguishes A from B lives where the forced consequences of A
and B diverge — but that region is 2-D, not a worm.

**For Paper 1:** do **not** attribute "never A" to a worm flip or to domain-wall steps — these
diagnostics do not support either. "Never A" is robust (it holds down to local 32-tile arcs and
carries no topological defect), but at this level it is **mechanism-agnostic**: the A/B
divergence is a 2-D forced-consequence region and the offset field is a smooth ramp. Keep
"selects B" separate from "excludes A" (we did): the reader *selects* B and is *silent/ambiguous*
elsewhere; it does not symbolically *exclude* A, and indeed selects A correctly where A is true.

---

## Setup and reproduction gate

Frozen engine `84130b9` (snapshot of `codex/manuscript-reconciliation`); fork cache rebuilt
deterministically (22 forks); archive-free 528-window readout reproduced
**111 B / 64 ambiguous / 353 empty-incompatible / 0 A** with 0 mismatches before checks ran.
All checks import the frozen engine, lift (`perp_map`), reader (`archive-free-reader/
skin_reader.py`) and replay helpers read-only.

---

## Check 4 — is the fork a worm flip?

### 4a. A/B forced-consequence diff (all 22 forks)

**What was asked.** For each fork, forced-close `Sstar+A` and `Sstar+B` (forced moves only, no
free choices), diff tile by tile, and report whether the difference is a single strip of rhombi
along one of the 5 non-expansive (worm) directions.

**Answer.** **No.** In **0/22** forks is the diff a single strip. The forced closures diverge
over a large 2-D region: A-only and B-only tiles together number from ~370 (w0) to ~3986
(w15/19/28/29); the diff's principal-axis aspect ratio is ≈ 0.97–1.70 everywhere (never ≥ 3),
and several diffs are multi-component. The two forced closures are also strongly asymmetric (e.g.
w7: A forces +1477 tiles, B only +23), which is itself a structural fact worth noting. The diff
lift is conflict-free (the difference geometry is itself a legal partial tiling). See
`figures/check4a_forced_diff.png` and `results/check4a_forced_diff.json`.

**Prediction P4a** (single strip in ≥ 20/22): **FAILED (0/22).**

**Caveat on the criterion.** Mod 180°, the five physical directions tile every 36°, so the
"axis within 12° of a worm direction" sub-criterion is weak on its own (any axis is within 18°
of some direction). The **binding** criterion was the aspect ratio: the diffs are essentially
isotropic 2-D regions, so they fail "strip" regardless of axis. 4a tests the **global** forced
closure; it does not isolate a possible *local* worm near the fork — but the global A/B
consequence sets differ over a 2-D area, which is what a worm-flip reading would need to be a
strip and is not.

### 4b. Arc reader scores (crossing/parallel not evaluable)

**What was asked.** On the 49/49 recovery skins and the 11 jammed bands, select connected arcs of
matched tile count, classify each as crossing vs parallel to the fork worm's line, and score with
the frozen reader under open and closed conventions; any arc uniquely selecting A falsifies
"never A".

**Answer.**
- **Crossing vs parallel is NOT evaluable:** 4a established no worm line (no single strip in any
  fork), so the fork worm's line is undefined. We report this honestly rather than invent a line.
- **Reader scores (K = 32 connected arcs, matched count).**
  - *11 jammed bands (B-committed), 233 arcs:* open = 85 B / 86 ambiguous / 62 empty; closed = 43 B
    / 131 ambiguous / 59 empty. **0 A under either convention.** (B-only falls and ambiguity rises
    under the closed convention, consistent with check 2.)
  - *49 recovery skins, 1041 arcs:* open = 65 B / 169 A / 807 ambiguous; closed = 14 A / 1027
    ambiguous. Every one of the 169 open-A (and 14 closed-A) arcs is on an **A-true** case — a
    **correct** recovery, not a falsifier.
- **A-only falsifier:** **0** arcs select A on any B-committed case (recovery or jammed). "Never A"
  is **not falsified**; it holds down to local 32-tile arcs.

**Prediction P4b** (crossing decides B, parallel mostly ambiguous): **not evaluable** (no worm
line). **Falsifier:** none found.

**Exploratory (NOT pre-registered).** Splitting arcs by overlap with the world's A/B
forced-closure difference region: arcs **in** the difference region read decisively
(jammed: 68 B / 6 ambiguous when F is non-empty; recovery: 155 A / 59 B / 572 ambiguous), while
arcs **outside** it are mostly ambiguous (jammed: 17 B / 80 ambiguous; recovery: 14 A / 6 B / 235
ambiguous). The discriminating information is localized to the (2-D) A/B divergence region.

---

## Check 3 — loop closure, and step vs slope on the 11 jammed bands

### 3a. Loop closure

**What was asked.** Walk each jammed band's boundary loops and sum the lifted edge vectors;
report b∥, b⊥ and the index component. P3a: b⊥ = 0 on every legal-rhombus loop.

**Answer.** **b⊥ = 0 exactly on all 190 boundary loops** (11 bands; 11–20 loops each), with b∥ = 0
and index component 0 on every loop, and **0 lift conflicts** per band. (b∥ = 0 is the correctness
check that the loops genuinely close; an earlier loop-tracer bug that produced open chains was
found and fixed — see tests.) See `figures/check3a_loop_closure.png`,
`results/check3a_loop_closure.json`.

**Prediction P3a** (b⊥ = 0 everywhere): **HELD.** The empty F carries **no** perp-space defect
(no dislocation/disclination); this is consistent with repo Theorem 1.

### 3b. Local offset profile (step vs ramp)

**What was asked.** Slide a short arc around each jammed band; at each position compute F's
Chebyshev centre (best-fit local offset) and radius; classify the centre-vs-angle profile as
step / ramp / mixed.

**Answer.** **All 11 bands are ramps.** The largest fraction of total offset variation
concentrated in any 3-position window is **7–16%** (step threshold 50%, ramp threshold 25%), so
no band has a dominant jump; the local offset drifts smoothly around the band. **0 step positions**
were found in any band. See `figures/check3b_offset_profile.png`,
`results/check3b_offset_profile.json`.

**Prediction P3b** (step-like, steps along worm directions other than the fork worm's):
**FAILED** — the profiles are smooth ramps, not steps. **P3c** (a step parallel to the fork worm
marks an A-only arc) is **moot**: there are no steps, and 4a gave no fork worm; and 4b found no
A-only arc on any B-case.

---

## What this means for Paper 1's wording

1. **Do not claim a worm-flip mechanism.** The A/B forced-consequence difference is a 2-D region,
   not a worm strip, in all 22 forks. If a worm picture is mentioned, it must be as a hypothesis
   the forced-closure diagnostic did **not** support, not as an established mechanism.
2. **Do not claim a domain-wall / phason-step mechanism.** The local offset profiles on the
   jammed bands are smooth ramps (distributed), not sharp steps at one or a few lines.
3. **"Never A" is robust but mechanism-agnostic (at this level).** It survives down to local
   32-tile arcs and carries no topological defect. State it as an empirical regularity of this
   reader/convention on these cases, with the move class and tolerances named.
4. **Keep "selects B" ≠ "excludes A".** The reader selects B on B-cases and is ambiguous/silent
   elsewhere; it selects A correctly on A-true cases. It does not symbolically exclude A.
5. **Numbers are model- and convention-specific.** Open vs closed conventions change the B/ambiguous
   split (B-only falls under closed), but not the 0-A result. The closed convention here is
   reconstructed from the reader's own region semantics; if `check2_conventions.py` is attached it
   should be reconciled (open is the reader's native rule and is not reconstructed).

---

## Scope, move classes, limits

- **Move classes.** 4a uses **forced-only** closure (frozen `D.candidates` == 1, `Patch.legal`).
  3a/3b/4b use the **frozen reader** on tile subsets; no growth or free choice is involved there.
- **Datasets.** 22 forks (4a); 49 recovery skins + 11 jammed bands (4b); 11 jammed bands (3a, 3b).
  Several worlds are structurally equivalent (identical 4a diff statistics), so 22/11 are not 22/11
  independent tilings.
- **Arc size K = 32** was fixed by a feasibility probe (100% reconstruct, ~88% positive-area F)
  with no reference to A/B outcomes.
- **Limits.** 4a is a global forced-closure diagnostic (it does not isolate a local worm). The
  crossing/parallel comparison was not run (no worm line). The closed convention is reconstructed,
  not the canonical `check2_conventions.py`. "Ramp vs step" is by the pre-registered concentration
  criterion; a different criterion could reclassify borderline bands (none here were borderline:
  all concentrations ≤ 0.16). All reader numbers are specific to this reader, gauge and tolerances.

---

## Deliverables and reproduce

```
protocol/PROTOCOL.md                 pre-registered (committed before outcomes)
src/rc_common.py                     frozen read-only wiring + shared utilities
src/check4a_forced_diff.py           -> results/check4a_forced_diff.json, worm_lines.json, diff_regions.json
src/check4b_arc_scores.py            -> results/check4b_arc_scores.json
src/check3a_loop_closure.py          -> results/check3a_loop_closure.json
src/check3b_offset_profile.py        -> results/check3b_offset_profile.json
src/make_figures.py                  -> figures/check{4a,4b,3a,3b}_*.png  (one per check)
tests/test_referee_checks.py         focused harness tests (forced closure, loop closure, Chebyshev, conventions)
```

```bash
# frozen snapshot of the whole accretion_pilot tree
mkdir -p /tmp/efp-snapshot
git archive origin/codex/manuscript-reconciliation exploratory/accretion_pilot | tar -x -C /tmp/efp-snapshot
export EFP_SNAPSHOT=/tmp/efp-snapshot/exploratory/accretion_pilot/expansion_front_paper
export MPLBACKEND=Agg
# fork cache + reproduction gate (must give 0 mismatches: 111 B / 64 ambiguous / 353 incompatible / 0 A)
(cd ../jam_repair_pilot/src && python3 build_fork_cache.py)
(cd ../scar_continuation_pilot/archive_free_2026-11-04/src && python3 readout.py)
# the checks
cd referee_checks_2026-11-06/src
python3 check4a_forced_diff.py
python3 check4b_arc_scores.py
python3 check3a_loop_closure.py
python3 check3b_offset_profile.py
python3 make_figures.py
python3 ../tests/test_referee_checks.py
```

No merge, no force-push; committed and pushed to `claude/referee-checks-2026-11-06`.

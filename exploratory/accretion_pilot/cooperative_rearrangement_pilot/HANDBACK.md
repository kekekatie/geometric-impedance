# HANDBACK — cooperative rearrangement pilot

*2026-11-02. For Katie / Astra. A bounded exploratory pilot; a negative result is
an acceptable outcome. No matching rules were relaxed. Experimental branch
`claude/cooperative-rearrangement-pilot`, starting commit
`53692c20c68a03a96b1e682ad8c90e60b764df21` (audit branch). Frozen engine, frozen
reader, historical hypotheses and all existing outputs unchanged.*

**Central question.** Can a finite rearrangement in the retained boundary band
restore projection-window compatibility and permit further construction, while
leaving the original historical A/B choice uniquely readable?

**Short answer.** No — for the bounded fixed-exterior move class. The obstruction
is **spatially distributed** around the retained ring: no connected region of up
to 8 tiles, with its exterior held fixed, can even in principle restore
compatibility, because the unchanged exterior is already infeasible in every case.
This is a bounded null, labelled by its move class and limits — not a universal
no-go theorem.

## The six questions, in plain language

**1. Which repair regions were ruled out by unchanged exterior constraints?**
**All of them.** We exhaustively enumerated every connected region of up to 8
tiles (12,248 regions, seeded at the dead sites and the compatibility-witness
vertices). For each, we held the exterior fixed and tested — box-independently,
with careful provenance (a vertex's constraint is dropped only if its *entire*
tile star is engulfed) — whether the unchanged exterior is feasible. **0 were
permitted; 0 were unresolved; 12,248 were ruled out.** Changing only such a region
cannot remove a contradiction that already lives in the part you are not allowed
to touch.

*Why it's distributed:* the infeasibility is not one opposing pair. The minimum
number of window-facet constraints that must be dropped for feasibility is **4**
(across three different layer-ranks), and a faithful greedy engulfment only
restores feasibility after rebuilding **11 vertex-stars ≈ 41 tiles**, in a
**disconnected** footprint spanning **12.5 tile-edges** — versus the two witness
vertices sitting **8.65 tile-edges** apart. See `figures/obstruction_map.png`.

**2. Was any legal completed replacement found?**
Yes, but only trivial ones. On the concrete regions we searched (the 15 flip
hexagons near the dead sites, exercising the full enumeration + order-independent
validation pipeline), the **only** atlas-legal completed replacement of each is
the **identity** (consistent with the audit's single-flip result). Positive
control (identity legal) and rejection control (an atlas-breaking filling is
rejected) both pass. No non-trivial legal rearrangement exists for those regions.

**3. Did it restore compatibility?**
**No.** Every legal completed replacement leaves the compatibility region
**infeasible** (same `r*`). This is exactly what the necessary condition predicts:
a replacement only *adds* constraints, so it cannot make a feasible region out of
an exterior that is already infeasible.

**4. Did construction resume and reach the fixed horizon?**
**No — not reached.** No candidate qualified (none restored compatibility), so the
frozen scheduler was never resumed. There is nothing beyond the jam to report, and
we did not invent a continuation.

**5. Was the historical choice readable?**
**No, and this was already true before any repair.** The pre-repair jammed state
is reader-incompatible by design: the frozen reader runs and reconstructs the
geometry, but the compatibility region is empty, so the A/B readout is
**empty/incompatible** (not "wrong", not "ambiguous"). The committed choice tile B
has **departed under pruning** (it is absent from the retained band). Because no
repair qualified, there was no opportunity to *recover* the historical readout —
and we claim none. An empty readout at a jam is the absence of a consistent offset
to read, **not** evidence that historical information has vanished.

**6. Was an elementary-move path demonstrated, or only a joint replacement?**
**Neither a path nor even a non-trivial joint replacement** was found. The only
legal replacements are identities, and none restores compatibility, so there is
nothing to reach by a path. We make **no** claim of a local dynamical mechanism;
a legal joint rearrangement would not by itself establish a sequence of elementary
moves, and here there is not even a non-trivial joint rearrangement to discuss.

## What this is and isn't

- **Is:** evidence that, for the audited world-7 B/stream-0 jam, the
  projection-window incompatibility is **not localisable** to any bounded
  connected patch whose exterior is held fixed. The obstruction is a property of a
  large, distributed arc of the retained ring.
- **Isn't:** a statement about moves that relax the boundary, larger or
  multi-region rearrangements, other jams, or any physical interpretation. Those
  are out of scope for this pilot and were not attempted.

## Limits (frozen before the search)

Connected region, edge-adjacency, size ≤ 8 tiles; exterior, true outer frontier,
inner boundary and coverage all fixed; frozen template tiles only; no relaxed
matching; no four-flip assumption. The replacement enumeration used caps
(≤ 256 fillings/region here, never truncated). The necessary-condition
enumeration was exhaustive at size ≤ 8.

See `protocol/PROTOCOL.md` (frozen) and `protocol/PROTOCOL_DEVIATIONS.md`;
`AUDIT_REPORT`-style details are in `results/part3_necessary.json` (the decisive
result), `results/part4_search.json`, `results/part5_score.json`; reproduction in
`README.md`.

## Status

Branch `claude/cooperative-rearrangement-pilot`, based on the starting commit. No
merge, no force-push. Frozen engine, frozen reader, historical hypotheses and
existing outputs unchanged. Focused tests (`tests/test_coop.py`) pass. Stopping
here per the brief: every tested region was ruled out before any replacement could
qualify, which is itself the useful evidence — the obstruction is spatially
distributed. No fresh worlds, no boundary-moving repairs, no new physical
interpretation, no manuscript.

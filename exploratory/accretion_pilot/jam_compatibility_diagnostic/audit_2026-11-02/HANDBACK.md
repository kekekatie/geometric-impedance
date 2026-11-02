# HANDBACK — audit of the jam compatibility diagnostic

*2026-11-02. For Katie / Astra. A bounded audit-and-correction pass over the
existing study (no new repair experiment). Audited commit
`9b3daefe50b250c93c795fbb9cfae089d180c1a4`; audit branch
`claude/jam-compatibility-diagnostic-audit`. Frozen engine, frozen reader, pilot,
and historical outputs unchanged; corrected outputs under `audit_2026-11-02/`.*

## For Katie first — the three questions

**1. Which findings survived?**
Most of them, and they're now better earned.

- The study's numbers **reproduce byte-for-byte** from the saved identifiers
  (every results file, both figures).
- The tiling becomes **impossible-to-finish before it visibly gets stuck** —
  step 9 vs jam 23 (world 7), step 17 vs 42 (world 5). This survives, and is
  *sharpened*: the impossibility arrives exactly at the **first free choice** the
  tiler makes (every step before it is forced; step 0 is just the A/B branch
  selection). The detection is genuinely at the triggering tile, not a blurry
  snapshot — I checked that the impossibility, once it appears, never goes away,
  so nothing can hide between snapshots.
- The impossibility is **real, not a trick of the bounding box** — I re-checked it
  with the box removed, with the box made enormous, and by isolating just the two
  or three constraints that clash; every way, still impossible, by the same
  margin.
- **Loosening the inner edge changes nothing** on world 7 — still impossible,
  dead sites still have zero options, the reader still can't read it — and this
  now holds under proper connectivity and frontier checks, not the weak ones the
  study used.
- **No legal single-hexagon rearrangement** rescues the jam — and I proved the
  search wasn't missing one by enumerating *every* geometric filling of each
  hexagon (128 apiece) and checking them order-independently.

**2. Did any result change after fixing the checks?**
No headline number changed, but several **descriptions were wrong and are
corrected**:

- "The conflict is **two tiles** pulling in exactly opposite directions" is only
  right for three of the four witnesses. The **world-5 jam witness is three facets
  of a single pentagon squeezing together**, not an opposing pair. And it's two
  *constraints from two vertices*, each vertex shared by up to eight tiles — not
  "two tiles."
- "**The same conflict carried forward unchanged**" (because the severity number
  is identical at two times) is not what the data shows. The reported minimal
  conflict is *different* at the two times. What is true — and I verified it by
  tracking the actual constraints — is that the early conflict's constraints are
  *still present and still impossible* at the jam; but the vertices feeding them
  move. Equal severity by itself proves nothing.
- "**The conflict is unique**" is wrong: there are many equally-minimal witnesses
  (6, 20, 2, and 24 across the four cases over 301 search orders). The study saw
  one because it tried only four orders.
- "**A repair must touch both** conflicting spots" is withdrawn: breaking *either*
  one removes *that* witness (though it needn't fix everything).

**3. What still prevents a stronger conclusion?**

- The impossibility verdict is a **floating-point linear program over
  golden-ratio-irrational numbers**. The margin sits far from any rounding
  threshold, so it's robust evidence — but **not a symbolic proof**. The study
  scaffolded an exact check over the field **ℚ(√5)**; I found that's the **wrong
  field** — the window's own normals carry sin 36° / sin 72°, which need a
  degree-4 field (ℚ(cos 36°, sin 36°)). So the exact certificate still isn't
  built, and ℚ(√5) alone won't do it.
- The feasibility certifier uses a fixed box; a feasible region sitting far
  outside it would be misread (it doesn't here, but it's a real limit).
- Everything is about worlds 7 and 5 only; "no legal alternative" is about the
  **single-hexagon flip move class**, not every conceivable continuation.

One-line version: **the study's conclusions hold up and are now independently
reproduced and hardened; what changed is the *language* around the conflict
(not two tiles, not unique, not provably "the same" across time, repairable from
either side), and the exact-proof path needs a bigger number field than was
assumed.**

---

See [AUDIT_REPORT.md](AUDIT_REPORT.md) for the full findings
(reproduced / changed / unresolved), [CORRECTIONS.md](CORRECTIONS.md) for the
claim-by-claim edits, and [README.md](README.md) for reproduction commands.

## Status

Branch `claude/jam-compatibility-diagnostic-audit`, based on the audited commit.
No merge, no force-push; nothing in the frozen engine, frozen reader, pilot, or
the study's committed results was modified. New certifier failure/boundary tests
and the retained `tests/test_feas.py` both pass. Stopping here per the brief: no
fresh-world study, no cooperative-repair experiment, no new physical
interpretation, no manuscript.

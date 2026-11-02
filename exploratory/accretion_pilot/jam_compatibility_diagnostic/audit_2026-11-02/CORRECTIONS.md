# CORRECTIONS — claim-by-claim

*2026-11-02 audit. Each row: the original study's wording (from its `HANDBACK.md`
/ `results/*_report.txt`), the audit verdict, and the corrected statement. The
original files are preserved unchanged; this is the record of what new prose
should say.*

### Reproduction & step structure

> "becomes impossible-to-finish at step 9 … doesn't visibly stall until step 23 …
> The fatal move is the first *free choice* the tiler makes."

**Reproduced and sharpened.** Step 0 is the A/B branch selection (option B);
steps 1..8 (w7) / 1..16 (w5) are all *forced*; the first *free choice* is at step
9 / 17, which is exactly where `F(full)` first becomes infeasible. The trigger is
a single tile. `F(full)` is monotone-infeasible through the jam, so the snapshot
scan plus the within-step refinement give exact tile-addition-event resolution.
*(evidence: `results/audit1_events.json`)*

### Feasibility

> "it is **genuinely impossible**, not a sliver — and comfortably so, far from any
> rounding worry."

**Reproduced and strengthened.** Infeasible with `r* ≈ −0.0816 / −0.0504`, and the
verdict is **box-independent** (box-free Phase-I LP, box widened to 1e6, and the
IIS alone box-free all agree) and **solver-robust** (LP failure → `unresolved`,
never feasible). Deep points sit at `|t| ≈ 0.5–1.0`, far inside the box.
*(evidence: `results/audit2_feasibility.json`, `src/test_feas_boundary.py`)*

> `feas.Q5` — "An exact `Q(√5)` certificate is scaffolded."

**Corrected (field too small).** The window facet normals carry sin 36° / sin 72°
(roots of the irreducible `16x⁴−20x²+5`, degree 4). The coordinates are **not in
ℚ(√5)**; an exact certificate needs `ℚ(cos 36°, sin 36°) = ℚ(ζ₂₀)⁺` (degree 4).
Also: `feas.py`'s docstring says an exact cross-check "is provided … (exact2d)",
but no `exact2d` exists — only the `Q5` class. The float-LP verdict remains
**robust numerical evidence, not a symbolic proof**.

> (scope) impossibility of the tiling.

**Framing corrected.** The result is **incompatibility with the specified
projection-window model** (no offset consistent with every vertex). It is not, by
itself, impossibility of every conceivable locally legal continuation.

### Witness (IIS)

> "the whole impossibility boils down to **two tiles** whose requirements point in
> exactly opposite directions — an unwinnable tug-of-war."

**Partly corrected.** It is two (or three) window-facet **constraints**, each from
one **vertex**; vertices lie on up to **8 tiles**, so "two tiles" is wrong. The
opposing-pair picture holds for w7@9, w7@23, w5@17 (unit normal dot = −1), **but
the world-5 jam witness `{(3,2),(3,3),(3,4)}` is three facets of one rank-3
pentagon** (dots −0.809/+0.309/−0.809), a 3-facet squeeze, not an opposing pair.
*(evidence: `results/audit3_witness.json`, `figures/audit_witness_halfplanes.png`)*

> "the same conflict carried forward unchanged" (identical `r*` at first-infeasible
> step and jam).

**Corrected.** The reported minimal witness **differs** between the two times.
Identity-tracking shows the first-infeasible constraint subsystem **remains
present and jointly infeasible at the jam**, but its **originating vertices
change**. Equal `r*` alone is not evidence of persistence.

> "IIS unique: True (alternatives found: 1)" (world 7 first-infeasible).

**Corrected — not unique.** Over 301 drop orders: **6** distinct inclusion-minimal
witnesses for w7@9, **20** for w7@23, **2** for w5@17, **24** for w5@42. Report
"one inclusion-minimal witness among several," or "no alternative found in N
tested orders" only where that is literally what was observed.

> "the move class that *could* matter is one that touches **both** conflicting
> tiles at once."

**Corrected.** Changing **either** IIS constraint removes **that** witness; it is
not necessary to touch both, and removing one witness need not resolve the
infeasibility (other witnesses remain).

### Inner-rim erosion

> "Loosening the inner edge changes nothing … every single time."

**Reproduced; method hardened.** The study's checks were weak (endpoint-only
"connectivity," a stop flag that didn't stop, dead sites read off the skin
frontier, unverified frontier preservation). Under explicit connectivity, dead-
site-neighbourhood, dead-site-identity-on-true-frontier, and frontier-ownership
checks (with a loop that stops on violation), all four world-7 levels are valid
and the conclusion is unchanged: infeasible, 0 dead-site candidates,
`empty_incompatible`. The study's skin-frontier dead sites happened to be
identical to the true-frontier jam sites (2 of them). *(evidence:
`results/audit4_erosion.json`)*

### Single-hexagon alternative

> "**0** previously-tested local rearrangements become legal" / `flip_legal 0/N`.

**Reproduced and strengthened.** An order-independent completeness cross-check
(exhaustive 128 geometric fillings per hexagon, validated against the preserved
neighbourhood) **matches** the sequential engine enumeration for all 15 baseline
hexagons; `max_solutions=4` never truncated; positive and rejection controls pass.
No legal single-hexagon flip alternative exists — a statement about the
**single-flip move class only**, not all conceivable continuations. *(evidence:
`results/audit5_hexsearch.json`)*

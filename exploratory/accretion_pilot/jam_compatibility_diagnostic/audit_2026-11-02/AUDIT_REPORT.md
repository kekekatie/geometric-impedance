# AUDIT REPORT — jam compatibility diagnostic

*2026-11-02. A bounded audit-and-correction pass, no new repair experiment, no
preferred outcome. Audited commit `9b3daefe50b250c93c795fbb9cfae089d180c1a4`
(branch `claude/jam-compatibility-diagnostic`, confirmed latest). Audit branch
`claude/jam-compatibility-diagnostic-audit`. Frozen engine, frozen reader, pilot,
and all historical results left unchanged; corrected outputs under
`audit_2026-11-02/`. New prose uses "retained boundary band" for the study's
"active skin"; existing identifiers and paths are preserved verbatim.*

Astra inspected the code and saved results but had not independently re-run them.
This pass re-ran everything and separates **reproduced**, **changed**, and
**unresolved**.

---

## 0. Reproduction (Part 1 of the brief)

The study replays deterministically from the saved `(world, stream)` fork
identifiers. Re-running all five parts reproduced the committed machine-readable
results **byte-for-byte** (and the two figures byte-for-byte):

- `part2_feasibility.json`, `part3_firstloss.json`, `part4_iis.json`,
  `part4_provenance.json`, `part4_spatial.json`, `part5_erosion.json`, and every
  `*_report.txt` — identical (see `reproduced/`).
- Retained certifier test `tests/test_feas.py` — passes.

Cases: world 7 fork key `4250b244a8d0887c`, streams `[20262655433, 20262655534]`
(indices 0,1); world 5 fork key `3a33a0d534922f0e`, stream index 0.

### What a "step" is, and the branch-vs-free-choice distinction

`grow_arm` (frozen) advances by calling the patient scheduler once per **step**
`s = 1..44`; `snaps[s]` is the full patch after step `s`. `snaps[0]` is the
initial `S*+c` state — i.e. **step 0 is the A/B branch selection** (here option
**B** = shape 1). `guesses` records the *later* steps that were free choices.
No pruning happens during `grow_arm`; the retained boundary band is re-derived
per snapshot by `skin_of`.

`audit1_events.py` confirms, for all three cases:

| case | branch | steps 1→first-free | first free choice | first infeasible F(full) | visible jam |
|------|--------|--------------------|-------------------|--------------------------|-------------|
| w7-B-s0 | step 0 (B) | all forced | **9** | **9** | 23 |
| w7-B-s1 | step 0 (B) | all forced | **9** | **9** | 23 |
| w5-B-s0 | step 0 (B) | all forced | **17** | **17** | 42 |

So the recorded "first loss of compatibility at 9/17, visible jam at 23/42"
**reproduces**, and is sharpened: the loss coincides exactly with the **first and
only pre-jam free choice**; steps 1..(8/16) are all forced; the triggering step
adds exactly **one** tile.

### Event-level resolution

The brief asked whether the implementation meets the promised
tile-addition/prune-event resolution or only inspects snapshots. It scans
feasibility per snapshot (step) and then, within the first-infeasible step,
re-adds that step's tiles one at a time to pin the triggering tile — but it never
checked that this is sufficient. `audit1_events.py` closes the gap: **F(full) is
monotone-infeasible from the first-infeasible step through the jam** (once empty,
never feasible again), for all three cases. Because `grow_arm` only *adds* tiles
per step (adding window constraints can only shrink `F`) under a constant gauge
(layers `[-1,0,1,2]`), no transient infeasibility can hide between snapshots; with
the single-tile trigger this gives **exact tile-addition-event resolution for the
full patch**. F(skin) is not assumed monotone and indeed never recovers here.
**Verdict: reproduced; the resolution claim is sound and now verified rather than
assumed.**

---

## 1. Feasibility diagnostic scope (Part 2)

`feas.py` certifies `F = { t : n_i·t ≥ c_i }` by a Chebyshev-centre LP in a fixed
`[-50,50]²` box, reading `n_i` and `c_i` from the frozen `slack.WIN` /
`slack.constraints`. Cross-reading `slack.py`:

- **Inequality direction / normalization / layer mapping: correct.** `slack`
  clips the box with `n_i·t ≥ c_i` where `c_i = max_v (n_i·perp(k_v) − h)`; `feas`
  reads the same `WIN[rk]` normals and `c_i`, unit-normalizes (preserving each
  half-plane), and the layer-rank map (`rank_of`, 4 sorted layers) is used
  identically. Gauge is consistent across steps.

- **The box does not manufacture the infeasibility** (`audit2_feasibility.py`),
  checked three independent ways:
  - a **box-free Phase-I LP** (no position box) returns *infeasible* for every
    case;
  - the Chebyshev radius with the box widened to **1e6** is unchanged;
  - the inclusion-minimal infeasible subset (IIS) **alone**, box-free, is
    infeasible.

  All deep points sit at `|t| ≈ 0.5–1.0`, far inside `[-50,50]`. Margins:

  | state | r* (box 50) | box-free margin | box 1e6 | IIS box-free |
  |-------|-------------|-----------------|---------|--------------|
  | w7 first-infeasible full @9 | −0.08156 | −0.08156 | −0.08156 | −0.08156 |
  | w7 jam-trigger skin @23 | −0.08156 | −0.08156 | −0.08156 | −0.08156 |
  | w5 first-infeasible full @17 | −0.05041 | −0.05041 | −0.05041 | −0.05041 |
  | w5 jam-trigger skin @42 | −0.05041 | −0.05041 | −0.05041 | −0.01722 (3-subset) |

- **Solver-failure handling: sound.** A simulated LP failure classifies as
  `unresolved`, never feasible (`feas` checks `status != 0 or x is None` first).
  New tests in `test_feas_boundary.py` cover this plus near-zero-margin slabs and
  the empty-constraint case; the retained `tests/test_feas.py` (polygon / segment
  / point / empty + sensitivity) still passes.

- **Documented scope limit (new):** the fixed `BOX=50` is a *blind spot* — a
  genuinely feasible region centred outside `[-50,50]` (e.g. at `(1000,1000)`) is
  misread as infeasible. This does **not** affect the study cases (their deep
  points are well inside the box), but it is a real limitation of the certifier
  and is now asserted in a test.

- **Coordinate field (new, corrects an implicit assumption).** The scaffolded
  exact cross-check `feas.Q5` assumes **ℚ(√5)**. The frozen window facet normals
  are `(cos θ, sin θ)` at θ = (odd multiples of 36°); **16 of the 20 normals carry
  a sin 36°/sin 72° component**, which is a root of the irreducible
  `16x⁴ − 20x² + 5` (degree 4 over ℚ). Hence these coordinates are **not in
  ℚ(√5)**, and `feas.Q5` is insufficient for an exact certificate. The field an
  exact check needs is `ℚ(cos 36°, sin 36°) = ℚ(ζ₂₀)⁺`, degree 4.

  *Irreducibility:* no rational roots; a symmetric factorization
  `(4x²+ax+b)(4x²−ax+c)` forces `a=0 ⇒ b+c=−5, bc=5` (roots of `z²+5z+5`,
  irrational) or `c=b ⇒ b²=5` (irrational) — so no factorization over ℚ, degree 4,
  therefore ∉ ℚ(√5) (degree 2).

**Framing.** The conclusion is **incompatibility with the specified
projection-window model** (no offset `t` is consistent with every vertex under
the frozen window). It is **not** equated with impossibility of every conceivable
locally legal continuation; see Part 4 for the move-class result that is in scope.

**Verdict: the infeasibility verdict is reproduced and is box-independent and
solver-robust. Two honest caveats are added (box blind spot; exact field ≠ ℚ(√5)).
"Robust numerical evidence, not symbolic proof" stands.**

---

## 2. Witness interpretation (Part 3) — CHANGED

Separating the three things the prose collapsed (`audit3_witness.py`):

| witness | IIS constraints (rank,facet) | distinct vertices | tiles per vertex | opposing pair? |
|---------|------------------------------|-------------------|------------------|----------------|
| w7 first-infeasible @9 | (2,3),(3,3) | 2 | 1 and 6 | **yes** (unit dot −1) |
| w7 jam-trigger skin @23 | (0,3),(3,3) | 2 | 6 and 4 | **yes** (unit dot −1) |
| w5 first-infeasible @17 | (0,3),(3,3) | 2 | 6 and 1 | **yes** (unit dot −1) |
| w5 jam-trigger skin @42 | (3,2),(3,3),(3,4) | 3 | 3, 6, 8 | **no** — 3 facets of one rank-3 pentagon (dots −0.809/+0.309/−0.809) |

Corrections:

1. **"Two tiles pulling in opposite directions" is not universal.** Each witness
   is a set of window-facet **constraints**, each contributed by one **vertex**,
   and each vertex lies on **several tiles** (up to 8) — not "two tiles." The
   opposing-pair description is accurate for the three 2-constraint witnesses, but
   the **world-5 jam witness is a three-facet squeeze within a single pentagon's
   window**, not an opposing pair. (Figure `figures/audit_witness_halfplanes.png`.)

2. **Equal r* does not prove the same witness persisted.** The reported minimal
   witness **differs** between the first-infeasible step and the jam (w7:
   (2,3)→(0,3); w5: entirely different). Tracking the first-infeasible IIS keys
   forward: that constraint **subsystem remains present and jointly infeasible at
   the jam** (so the conflict does persist at the constraint level — verified by
   identity tracking, not by the margin), **but its originating vertices change**.
   The correct statement is "the first-infeasible constraint subsystem is still
   infeasible at the jam; its supplying geometry shifts," not "the same conflict
   carried forward unchanged."

3. **Uniqueness was over-claimed.** The study tried 4 drop orders and reported
   w7-first-infeasible as a *unique* IIS. Over **301** random drop orders there
   are **6** distinct inclusion-minimal witnesses for w7@9, **20** for w7@23,
   **2** for w5@17, **24** for w5@42. The IIS is **not unique**; the right wording
   is "one inclusion-minimal witness among several" (or, where only one is seen,
   "no alternative found in N tested orders").

4. **Repair recommendation corrected.** Changing **either** constraint of an IIS
   removes **that** witness; it is not necessary to touch both for that witness,
   and removing one witness need not resolve the infeasibility (other IISes
   remain). So "a repair must touch both conflicting locations" is withdrawn.

---

## 3. Boundary-intervention checks (Part 4) — method hardened, result unchanged

Reading `part5_erosion.py` confirmed all five weaknesses the brief named:
`component_ok` tested only dead-edge **endpoint presence** (not connectivity); the
`dead_site_neighbour_removed` flag used that same weak proxy; the computed stop
flag **never stopped the loop**; dead sites were read off the **skin frontier**
(which mixes the true growth frontier with pruning-exposed inner edges); and
true-frontier preservation was **assumed, not checked**.

`audit4_erosion.py` re-runs the four world-7 levels with explicit checks and a
documented adjacency (two half-tiles adjacent iff they share a full edge;
connectivity by BFS):

| level | θ (S) | tiles | true-frontier preserved (edges+owner) | dead-site nbhd preserved | components | dead sites in one component | level valid | F | dead-site candidates |
|-------|-------|-------|----------------------------------------|--------------------------|------------|------------------------------|-------------|---|----------------------|
| L0 | ∞ | 315 | yes | yes | 1 | yes | **valid** | infeasible | [0,0] |
| L1 | 2.0 | 260 | yes | yes | 1 | yes | **valid** | infeasible | [0,0] |
| L2 | 1.5 | 226 | yes | yes | 1 | yes | **valid** | infeasible | [0,0] |
| L3 | 1.0 | 170 | yes | yes | 1 | yes | **valid** | infeasible | [0,0] |

- The corrected **dead-site definition** (zero-candidate edges of the **full**
  true frontier) gives **2** dead sites, **identical** to the skin-frontier dead
  sites the study used — i.e. none were pruning-exposed inner edges. The study's
  fragile method happened to coincide with the correct one here.
- The stop clause now actually stops; no level triggered it (all four are valid).

**Verdict: the five weaknesses were real; under corrected, explicit checks the
world-7 erosion conclusion is unchanged** — releasing the inner rim leaves the
region infeasible, the dead sites with zero candidates, and (frozen reader)
`empty_incompatible`, because both conflicting vertices sit on the outer band.

---

## 4. Single-hexagon alternative search (Part 5) — completeness established for the move class

`enumerate_hexagon_fillings` fills one deterministic open-edge order and filters
each placement with the frozen `P.legal` in the partial context, raising the risk
that a completed-legal alternative is missed by intermediate rejection; `part5`
also used `max_solutions=4`.

The engine's legality is a function of the **final** local configuration (a vertex
is legal iff its assembled corner list is a complete atlas star or a contiguous
arc), so a completed filling can be validated **order-independently**.
`audit5_hexsearch.py` does this against a **fixed baseline** of the 15 flip
hexagons near the dead sites (tracked across erosion levels), and for each:

- enumerates **all** geometric dissections (exhausted: **128** per hexagon, below
  the 256 cap — not truncated);
- validates each order-independently against the preserved neighbourhood;
- compares to the sequential `engine` enumeration.

Result, every fully-supported hexagon at every level:

| level | baseline hexes | fully supported | with legal alternative | engine == order-independent | positive control |
|-------|----------------|-----------------|------------------------|-----------------------------|------------------|
| L0 | 15 | 15 | **0** | yes | pass |
| L1 | 15 | 10 | **0** | yes | pass |
| L2 | 15 | 6 | **0** | yes | pass |
| L3 | 15 | 2 | **0** | yes | pass |

- The sequential enumeration returns **exactly one** solution per hexagon (the
  original), which **matches** the exhaustive order-independent validation — so
  **no legal alternative was missed by intermediate rejection**, and
  `max_solutions=4` **never truncated** (one engine-legal filling per hexagon).
- Positive control (original dissection is independently legal) passes; rejection
  control (a deliberately atlas-breaking filling) is correctly rejected.

**Verdict: `flip_legal = 0` is reproduced and strengthened.** For the single
phason-flip move class, at these sites, the enumeration is complete and sound; no
legal single-hexagon alternative exists. This is a statement **about that move
class only**, not about all conceivable locally legal continuations (no expansion
into multi-hexagon searches, per the brief).

---

## Reproduced / Changed / Unresolved

**Reproduced (unchanged):**
- All committed machine-readable results and figures, byte-for-byte.
- First loss of compatibility at steps **9 / 17**, visible jams at **23 / 42**,
  "before the jam" — and sharpened to the first free choice.
- Infeasibility of every jam-trigger region (`r* ≈ −0.0816 / −0.0504`), now shown
  **box-independent** and **solver-robust**; `F(full)` and `F(skin)` share the
  binding constraints.
- Inner-rim erosion changes nothing on world 7 (infeasible, 0 candidates,
  `empty_incompatible`) — now under corrected connectivity/frontier checks.
- No legal single-hexagon flip alternative (`0/15, 0/10, 0/6, 0/2`) — now with an
  order-independent completeness cross-check.

**Changed / corrected:**
- Witness **uniqueness**: not unique (6 / 20 / 2 / 24 distinct witnesses) — the
  study's "IIS unique: True" is withdrawn.
- "Two tiles in opposite directions": corrected to constraints-from-vertices-on-
  many-tiles; the **world-5 jam witness is a 3-facet single-pentagon squeeze**,
  not an opposing pair.
- "Same conflict carried forward unchanged (equal r*)": corrected to "the
  first-infeasible constraint subsystem stays infeasible at the jam (identity-
  tracked), but its supplying vertices change; equal r* alone is not evidence."
- "Repair must touch both locations": withdrawn (breaking either witness
  constraint suffices for that witness; need not resolve all conflicts).
- Erosion checks (connectivity, dead-site neighbourhood, dead-site identity on the
  true frontier, true-frontier preservation, stop condition) made explicit; the
  world-7 conclusion is unchanged.

**Unresolved limitations:**
- Feasibility is a **float LP over φ-irrational data** — robust numerical evidence
  (`|r*| ≫` tolerances), **not a symbolic proof**. An exact certificate needs
  `ℚ(cos 36°, sin 36°)` (degree 4), **not** the scaffolded `ℚ(√5)`; this is not
  wired up.
- `feas.py` uses a fixed `BOX=50`; a feasible region centred outside it would be
  misread. Harmless here (deep points `|t| ≈ 1`), but a real scope limit.
- The full set of minimal (and the minimum-cardinality) witnesses is not
  enumerated; only distinct witnesses over 301 drop orders are reported.
- The frozen reader's `empty_incompatible` outcome is a consequence of
  infeasibility; it is preserved, not independently re-derived.
- Results cover the two headline worlds (7, 5); no claim about the other recorded
  jams, correlated rearrangements, or any physical interpretation.

# Synthesis — the accretion pilot, v1 through v14

*Register: speculative exploration. This is a small, transparent **toy model**, not a
confirmatory study, not cosmology, not a claim about physics, biology, or minds. It is
isolated under `exploratory/accretion_pilot/`; the version chain
`cc514ee (v1) → cab9254 (v2) → fe49f64 (v3) → 43d0c61 (v4) → e64ab73 (v5) →
a3b6bc8 (v6) → 0c990b1 (v7) → 55ba85e (v8) → 740b8cd (v9) → 0a41135 (v10) →
10d4860 (v11) → 7a342c5 (v12) → v13 → v14` is preserved in full; every dated
correction is kept in place. No merges, publishing, or sealed-study access. This
document consolidates fourteen bounded steps by **question answered**, not by
chronology, and keeps speculation explicitly separate from the findings.*

---

## 0. What the model actually is

A weighted graph of places and connections that changes as things move through it.
Three ingredients, all fixed in advance:

- **Reinforcement rule.** Every time the walker crosses an edge `e`, its weight moves a
  fixed fraction toward a cap: `w ← w + 0.5·(6 − w)`. This is **bounded and
  saturating** — the gap `(6 − w)` halves per traversal (`6 − wₙ = 5/2ⁿ`), so an edge
  *rounds* to 6 (reaches `w ≥ 5.5`) after **4 traversals** and only reaches exactly 6
  in the float limit. Weights never leave `[1, 6]`; nothing is ever weakened or deleted.
- **Growth allowance (finite, pre-declared).** Each face of the tiling (a square cell on
  the v1–v8 9×9 grid; a rhombus on the v9–v14 pentagrid) has exactly **two candidate
  diagonals**. A candidate **switches on** — activates, at weight 1 — when its face's
  four bounding edges have accumulated enough wear (`Σ(w − 1) ≥ θ = 4`). This catalogue
  is **fixed and finite**: 128 candidates on the square grid (64 faces × 2), ≈660–688 on
  an R≈10 pentagrid patch. **No connection outside the catalogue can ever appear.**
  "Growth" here means *switching on a pre-existing possible connection*, never inventing
  a new one.
- **Imposed histories A and B.** Two matched journeys we **inject** (not behaviours the
  world generates): on the square grid, mirror-image upper-side vs lower-side paths
  through a central probe; on the pentagrid, two deterministic geometry-only length-6
  shortest paths (leftmost vs rightmost extreme) from a shared start `S`, imposed as
  **18 traversal events** (a length-6 path walked 3 times). After the history, the
  walker is released and moves by a weighted random walk (probability ∝ edge weight).

**The finite saturation limit.** The weighted walk is an irreducible recurrent Markov
chain on a finite connected graph, so in the limit every present edge is traversed
infinitely often (`w → 6`) and every face crosses the growth threshold (every candidate
activates). At that limit the world is **fully grown and uniform** — all weights 6, all
diagonals present — hence **symmetric between A and B, and decoding is exactly chance.**
Runs to 10,000 steps approach but never reach this (at t=10000: ~0.004% of candidates
still inactive, mean headroom `6 − w ≈ 0.017`). So the memory studied here is a
**transient** riding a slow, monotone approach to a memoryless fully-grown state — not a
permanent store.

---

## 1. Is there a history distinction at all, and *where* is it readable? (v1–v5)

**Yes — a real, durable distinction, whose readable carrier shifts over time.** With a
coordinate-aided contrast (which side is heavier), every changing world starts perfectly
distinguishable (AUC 1.0 at step 0, by construction) and is gently eroded by subsequent
wandering. The **fixed** (no-memory) control sits at chance forever, as it should.

- **v1** — *Memory and opportunity need not trade off.* At t=400 the **Growing** world is
  the most durable (AUC 0.908) — ahead of reinforcement-only (0.798) and a
  matched-resource control (0.777) — **and** has the most movement opportunity (≈6× the
  effective-route diversity of baseline), while reinforcement *alone* buys memory by
  **funnelling** movement (opportunity drops *below* baseline). History-shaped growth
  carries the past and widens the future at once.
- **v2** — *Magnitude vanishes; sign survives.* With an honest event-by-event
  timing-matched control and 10,000 steps, the memory **magnitude** collapses to ~0.002
  by saturation, yet a signed **ordering** residual keeps Growing above chance
  (AUC gap over the control **+0.095 [0.017, 0.170]** at t=10000). One must not read
  chance-level decoding from structural convergence, nor durable practical memory from a
  surviving sign.
- **v3** — *Trace vs readable memory.* Under a coarse weight reader (round to the nearest
  whole number), Growing's late discrimination barely moves (0.626 → 0.613) while
  reinforcement-only's fine-weight residual **collapses to chance** the moment any
  rounding is applied. A distinction can exist in the exact state yet not be readable.
- **v4** — *Where the late signal lives — corrected.* v3 attributed the late signal to
  **topology**; a direct count showed topology is essentially **complete and identical**
  across A and B late (2 missing candidate edges across 400 worlds). **The dated
  correction withdraws "topological" and "sub-quantum."** Decomposing the reader shows
  the carrier **moves over time**: edge *presence* + original-edge weights early →
  **added-diagonal weights** (departure from the cap) late. On the complete-topology
  subset (topology held identical) presence is exactly chance (0.500) yet the full reader
  still discriminates (0.627): **the late carrier is weights, not which edges exist.**
- **v5** — *One bit per shortcut suffices, late.* A single bit — "has this added diagonal
  been re-crossed ≥4 times (`w ≥ 5.5`)?" — retains the late distinction (AUC 0.619 at
  t=10000) and tracks the full graded reader. This **frozen proximity-sign one-bit
  reader**, `S_high = Σ s(e)·1[w ≥ 5.5]` over added diagonals, is the reader carried
  forward into v11/v13/v14.

*Carried-forward correction.* The phrase "which reader carries the signal shifts over
time" is an **observation about correlated readers, not a mechanism** — it is explicitly
**not** "memory transfer"; nothing shows a stored quantity moving between substrates.

---

## 2. What shapes the footprint — and what stays unresolved (v6–v8)

These runs intervene on **initial conditions only** (dynamics unchanged), crossing or
neutralising the two ingredients: inherited original-edge weights `W` and inherited
diagonal placement `T`.

- **v6 (crossed 2×2: W_A/W_B × T_A/T_B).** Both the initial **weight** background and the
  initial **placement** have **comparable, statistically-supported** main effects on the
  mid-run footprint. *Corrections (v7):* the crossed worlds hold **both** ingredients in
  opposition, so this design **cannot** test either ingredient's sufficiency *in
  isolation* ("neither alone suffices" withdrawn); and the apparent sub-additive
  interaction is **zero by transpose symmetry** — finite-sample noise, withdrawn.
- **v7 (directionality reanalysis).** Crossing the ingredients mainly scrambles the
  **direction-consistency across seeds** (aligned worlds ~66–69% sign-consistent; crossed
  worlds ~52–56%, near a coin-flip) — **not** the per-world footprint *magnitude* (all
  ≈11). A reproducible A-vs-B **direction** appears only when inherited weights and
  placement are **aligned**. *Clarified:* the magnitude difference is small and
  **unresolved at the peak** (CI includes both 0 and sizeable values) — not proof of
  equivalence.
- **v8 (neutral background).** With `W_0 = (W_A + W_B)/2` (no directional weight cue) and
  worlds differing **only** in placement, placement alone yields only a **fleeting early
  head-start** (AUC ~0.63 at t=100, 0.571 at t=400) that decays to **no clear
  discrimination** by the primary endpoint t=2000 (AUC 0.484). *Corrections:* "at chance"
  softened to "no clear discrimination" (not proof of zero information); v8 does **not**
  isolate weights-alone nor show weights dominate — only that placement, against this
  symmetric background, sustains no direction beyond an early transient.

**Established:** both inherited weights and placement matter; a reproducible *direction*
requires them **aligned**; placement alone against a neutral background holds no
direction past an early head-start. **Unresolved:** neither ingredient's sufficiency in
isolation (the crossed design can't reach it); the alignment-axis intervention was never
run; the "early activated diagonals cross threshold first" mechanism is a **hypothesis**
(snapshots record states, not threshold-crossing *times*); and the **locality-vs-history-
shape** confound flagged in v2 (Growing's diagonals appear right at the readout probe)
was never separated.

---

## 3. Does the *class* of spatial order matter? (v9–v11) — a narrow comparison

- **v9 (design) / v10 (construction).** Designed and built a de Bruijn **pentagrid**
  generator with rhombus faces (so the v1–v8 face rule transfers verbatim), producing
  genuine **Penrose** patches (regular arm) and same-tile **perturbed** patches, with
  geometric + topological validation. *(v10's `validate()` over-claimed a no-op area
  check; this was flagged and genuinely repaired in v11, with deliberately-invalid
  fixtures now rejected.)*
- **v11 (experiment).** **No detectable difference** between regular Penrose and perturbed
  pentagrid. At the pre-registered primary t=2000, AUC 0.616 (regular) vs 0.624
  (perturbed); the between-arm gap (0.008) is **far smaller than the across-patch spread
  within each arm** (~0.02–0.03), curves overlap at every checkpoint, and opportunity /
  capacity measures track together. Both arms sit well above the no-history null
  (~0.47–0.50), confirming the signal is real.

**This comparison is deliberately narrow.** "Perturbed" is **not** established as
"disordered" (bounded jitter of a Penrose tiling may leave long-range order largely
intact) — so this is essentially *Penrose vs mildly-perturbed-Penrose*, two **similar**
substrates. Local geometry (degree distribution, tile frequencies, boundaries) is
uncontrolled; a null difference is **not** equivalence; there are only 3 patches per arm;
and the reader is global and coordinate-aided. The matched-offset contrast (v12, existing
data) is **+0.007 [−0.018, +0.032]**, sign-inconsistent across offsets — conditional on
these six patches, no difference, and no generalisation claimed.

---

## 4. Is the distinction *accessible* — globally, locally, and from where? (v11 / v13 / v14)

This is the ladder from *present in the structure* to *reachable by something moving
inside it*.

- **Global reading (v11).** The coordinate-aided reader shows the distinction is
  **present** in the frozen structure (AUC ≈ 0.62 at t=2000). It says nothing about
  whether a walker inside the world could reach it.
- **Tagged bounded reading (v13).** A **passive, read-only** visitor starts at the shared
  `S`, moves by the **rounded** weights it senses, and scores the v5 proximity term over
  the diagonals it happens to **encounter** — with the coefficient supplied as a **tag
  revealed on encounter** (the coefficient depends on full-graph distances and is not
  locally computable, so it is *supplied*, making this explicitly an **aided** reader).
  Result: the bounded local reader recovers **essentially the whole** global
  discrimination — `local − global @ B=300` is **+0.006 / +0.007**, CI through zero —
  and does so **cheaply and early** (AUC ~0.63 at B=100, having seen only ~36% of present
  diagonals). Regular and perturbed are again indistinguishable.
- **Distant-start intervention (v14).** The same tagged visitor is **dropped far away** —
  a geometry-frozen vertex ~10 hops from both imposed paths and from `S`, near the far
  boundary — on the *unchanged* worlds. History discrimination **does not fundamentally
  depend on starting at `S`**: the distant reader **fully recovers** by B=1000
  (`distant − orig` ≈ 0, matching the global reader), with a **travel/sampling deficit at
  small budgets** (−0.060 at B=100, −0.017 at B=300) that tracks **arrival** at the
  history region (38% → 82% → 99% of runs arrived; median arrival ≈130 steps). The gate
  reproduced the v13 original-start scores **exactly** (max|Δ| = 0 over 27,000 values).
  This extends aided accessibility to **one specified far location — not to arbitrary
  starts.**

---

## 5. A compact map of the principal claims

| v | Principal claim | Primary result | Key limitation |
|---|---|---|---|
| 1 | Growth lets memory & opportunity coexist; growth most durable | Durability AUC 0.908 (Growing) > 0.798 (Reinf.) > 0.777 (control) at t=400 | Coordinate-aided readout; one parameter point; slow erosion not run to extinction |
| 2 | Memory *magnitude* vanishes; signed *ordering* survives | Growing−control AUC **+0.095 [0.017, 0.170]** at t=10000 | Locality (probe-adjacent diagonals) & unequal evolved weights unmatched |
| 3 | Growing's signal survives coarse weight measurement; a fragile residual does not | Growing AUC 0.626→0.613 across Δ; Reinforced collapses to chance | One measurement model; a failed readout ≠ no recoverable state |
| 4 | Late carrier is **added-edge weights, not topology** (corrects v3) | Complete-topology subset: presence 0.500, full 0.627 | Standalone-component AUC ≠ causal share; coordinate-aided |
| 5 | One bit per shortcut (`w ≥ 5.5`) retains the late distinction | One-bit `S_high` AUC 0.619 at t=10000, tracks full reader | Thresholded-visitation footprint, not threshold-crossing *times*; aided |
| 6 | Inherited **weights and placement** both matter, comparably | Both main effects supported at t=400/2000 (CIs exclude 0) | Crossed worlds can't test sufficiency-in-isolation; interaction 0 by symmetry |
| 7 | Alignment governs **direction-consistency**, not magnitude | Aligned ~66–69% sign-consistent vs crossed ~52–56% | Magnitude difference unresolved at peak; no alignment-axis run |
| 8 | Placement alone (neutral background) gives only an early head-start | AUC ~0.63 (t=100) → 0.484 (t=2000, primary) | Not weights-alone; not proof of zero info; mechanism a hypothesis |
| 11 | Regular Penrose vs perturbed pentagrid: **no detectable difference** | t=2000 AUC 0.616 vs 0.624; between-arm ≪ across-patch spread | "Perturbed" ≠ "disordered"; 3 patches/arm; global reader; not equivalence |
| 13 | The distinction is **locally accessible** to a bounded tagged visitor from `S` | `local − global @ B=300` **+0.006 / +0.007** (CI through 0) | **Aided** (tag supplied); modest AUC; six fixed patches |
| 14 | Discrimination **does not depend on starting at `S`** | `distant − orig` ≈ 0 by B=1000; −0.017 @ B=300 (travel cost) | One specified far location, not arbitrary; still aided |

---

## 6. Four things this study keeps carefully separate

The whole arc is disciplined about **not** letting one of these be read as another:

1. **Stored distinction** — the frozen world's structure differs by imposed history, and
   a reader with full access can tell A from B. *Established* (v1–v11), with the carrier
   located in added-edge weights late (v4–v5).
2. **Aided accessibility** — a bounded local walker, **given a supplied proximity tag**,
   can recover that distinction from finite local observation, both from `S` (v13) and
   from a specified distant start (v14). *Established, but only in the aided sense* — the
   tag is not locally computable and is handed to the reader.
3. **Autonomous use** — an agent computing the distinction **for itself**, without
   supplied coordinates/tags, or the distinction changing some behaviour the world would
   exhibit on its own. **Not established, not attempted.**
4. **Transmission** — the distinction being copied, propagated, or passed to another
   structure or agent. **Not established, not attempted.**

Everything demonstrated lives at levels 1–2. Levels 3–4 are open.

## 7. What "growth" is — and is not

The model **activates a finite, pre-declared catalogue of possible connections** (the two
diagonals of each face). It does **not** create fundamentally new possibilities, and it
does **not** demonstrate inexhaustible or open-ended growth. Every "new" edge was always a
latent member of a fixed set; the world can fill in that set and then it is full. Nothing
here is an expanding space of possibilities, and no such claim is made.

---

## Dated clarification — 2026-09-07 (v14; all results above preserved)

Five guards on the v14 reading, none of which change any number:

- **Start position changes bounded discrimination on otherwise-unchanged worlds.** Only
  *where the visitor begins* was intervened on; the frozen worlds are identical to v13's.
- **Arrival and coverage are descriptive correlates** of the budget-dependent improvement,
  **not an isolated causal explanation** of it — they co-move with the deficit but were
  not manipulated independently.
- **Near-zero long-budget contrasts, with their intervals, support *similar observed
  performance*** — not exact recovery of the same information, and not formal equivalence
  of the distant and original readers.
- **Arrival times are quoted among visitors that arrived** and are therefore
  **conditional statistics** (they say nothing about the runs that never reached the
  paths within budget).
- **Similar patterns across the regular and perturbed arms do not establish general
  equivalence** or the **absence of a quasiperiodic advantage** — overlapping marginal
  behaviour is not a direct between-arm test.

---

## Three distinct future questions (posed, not implemented)

1. **What remains readable without the supplied proximity tags?** Everything at the
   accessibility level (v13/v14) rests on a coefficient handed to the reader. Strip it:
   is there *any* locally-computable signal a walker could form from what it senses alone?
2. **Can inherited structure affect a specified useful behaviour, or transmit a
   distinction?** Move from "a reader can tell A from B" to "the A-world makes some
   pre-specified task go measurably differently, or the distinction is passed to a second
   structure/agent." This is the step from accessibility to autonomous use / transmission.
3. **What changes when the world can enlarge its growth allowance?** The catalogue is
   fixed and finite; the saturation limit is memoryless *because* the set fills up. What
   happens to memory and opportunity if activated structure can, in turn, create *new*
   candidates — a genuinely open (rather than pre-declared) growth rule?

## One recommended next direction

**Recommendation: pursue question 1 — a tag-free / self-computed local reader.** It is the
single cleanest step and the natural next rung on the ladder. The current ceiling of the
whole study is **aided accessibility** (level 2): v13 and v14 both *supply* the proximity
coefficient because it depends on full-graph distances a local walker cannot compute. Until
that tag is removed, we cannot say anything about **autonomous use** (level 3). Asking what
survives when the reader must build its signal only from what it senses locally — rounded
weights, edge types, its own visit history — directly answers question 1 and is the
**precondition** for question 2 (a distinction that isn't autonomously computable can't be
autonomously *used* or *transmitted*). It is also the most bounded: it can likely reuse the
retained v13/v14 frozen worlds and snapshots with only a new reader, no new dynamics and no
change to the model — keeping to the same discipline that has governed every step. Question
2 is the more exciting prize (autonomy/transmission) but is premature while the reader is
still aided; question 3 attacks the finite-catalogue caveat but requires a genuinely new
growth rule and new dynamics, the largest departure — worth doing, but later.

---

*Speculation is confined to the "future questions" and "recommendation" above. Everything
in sections 0–7 and the claims table is a statement about this toy model's measured
behaviour, with its corrections and limits attached; none of it is a claim about the world
outside the model.*

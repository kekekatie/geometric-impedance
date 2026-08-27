# Current session handoff

*Written 2026-08-26 for a fresh collaborator (human or model) picking up the GIV quasicrystal
programme. Branch: `claude/giv-quasicrystal-phason-5syx5s`. At the time of writing the branch is
**fully pushed** (0 commits ahead of origin); every result below is already on GitHub. This file
is documentation only — no new experiments were run and no scientific result was changed to
produce it. Deeper detail lives in the linked `substrates/RESULTS_*.md` and `SYNTHESIS.md`
(Part II is this session's arc). Roadmap for what's next: `ROADMAP.md`.*

---

## 0. One-paragraph state of play

The programme studies rank-4 cut-and-project quasicrystal tilings — silver (8-fold,
Ammann–Beenker), golden (10-fold, Penrose), platinum (12-fold) — and each vertex's "address"
(its perpendicular-space coordinate). **Part I** (earlier, already committed) established a
border: quasiperiodicity governs *static structure/memory*, not *free dynamics*, and golden
carries the richest degree-independent address (the old "silver is robust" headline was vertex
degree in disguise). **Part II (this session)** asked two things: can the map hold an *object*?
(no — no cheap endogenous defect), and can a *physical law* read the address? (**yes** — the
programme's first strong positive: a coherent wave reads golden's address, four controls; a
classical walk reads nothing). The mechanism is the wave's **stationary spectral structure**
(standing modes), not dynamical interference — so even the wave reads the geometry *statically*,
and the border holds. Latest refinements temper the ontology: the address is a **multiscale
re-encoding of local structure**, valued for its organization, not an orthogonal hidden channel.

---

## 1. Completed this session, in order (with numbers, controls, interpretation)

### 1a. Defect audit — Gate 0 (`substrates/RESULTS_GATE0_DEFECT.md`)
- Built + validated a **lifted-Burgers closure functional** (`lifted_defect.py`): reads exactly
  zero on every clean tiling, all three families.
- Gate 0 construction attempts (`lifted_defect_gate0.py`): pure phason (perp-offset) winding →
  only **kernel** holonomy (b∥ = b⊥ = 0, physically null); parallel Volterra cut → shears the
  whole QC (b∥ not a period); coupled phonon+phason → still shears. **Periodic control**
  (square lattice, parallel Volterra) → a genuine localized dislocation with **radius-invariant
  b∥ = (±1,0)** — this validated the instrument on a *nonzero* charge.
- Combinatorial route (`multigrid.py`): de Bruijn multigrid **bridge validated** (step 1) — the
  dual reproduces our exact tilings, 100% rhombi, closure = 0, all three families (a reusable
  second generator). Step-2 defect attempts all read **zero** closure, proving the structural
  fact: **any single-valued lift telescopes to zero closure on every loop.**
- **Verdict:** outcome (b), *not resolved / implementation-limited* — **NOT** H_none. No cheap
  *endogenous* Burgers object; objecthood must be *imposed*, not found. Banked as a
  null/constraint.

### 1b. Transport hierarchy — SEALED then run (`substrates/RESULTS_TRANSPORT.md`)
- `PREREG_transport_hierarchy.md` **SEALED** (commit `1f6222c`, before any run) with Fable's +
  GPT's knives: **stratified address shuffle** (within motif×degree bins) as the decisive kill;
  **M4 frozen** = {hull/window depth, shell-averaged perp at r∈{2,4,8}, address variance across
  those scales, perp-address gradient}; **primary window = mid-band |E|∈[0.8,2.5]** (Claude's
  call, overriding GPT's E≈0 — reasoning recorded); secondary |E|≤0.2; incoherent times
  t∈{5,10,20}; bulk-only (r<0.8 r_max).
- Confirmatory (`transport_run.py`): per-vertex coherent LDOS vs incoherent random-walk return,
  nested M0→M4, held-out-offset CV (5 offsets). **M4-over-M3 increment (coherent, primary):**

  | family | M4−M3 | stratified shuffle | + position | + long-range physical |
  |---|---|---|---|---|
  | golden (N=10)  | **+0.031** | −0.005 (killed) | +0.032 | +0.029 (survives) |
  | platinum (N=12)| +0.089 | +0.013 (~86% killed) | +0.090 | +0.073 |
  | silver (N=8)   | +0.090 | +0.026 (~71% killed) | +0.091 | +0.039 (~half absorbed) |
  | incoherent (all) | ≈+0.003 | ≈0 | ≈0.003 | ≈0.003 |

- **Golden = H_read**, four independent controls (held-out CV, stratified shuffle, physical
  position, long-range physical). Classical walk reads nothing everywhere. Platinum mostly
  address; silver largely long-range *physical* structure, not address.
- **Convergence (not pre-registered):** golden — richest degree-independent address in Part I —
  is the family whose transport cleanly reads it.

### 1c. Coherence ladder — the mechanism (`substrates/RESULTS_COHERENCE.md`)
- `wave_dephasing.py`: three per-vertex return observables, decreasing coherence. **Address
  increment: coherent ≈ diagonal-ensemble ≫ classical** (a plateau, then a cliff). golden
  +0.032 / +0.032 / +0.001; silver +0.079 / +0.082 / +0.004; platinum +0.075 / +0.061 / +0.001.
- **Interpretation:** the address-reading lives in the **stationary spectral structure** of the
  coherent Hamiltonian (Hψ=Eψ, globally self-consistent standing modes), **not** in dynamical
  inter-eigenstate phase interference. Eigenmodes are static, so the border ("static structure,
  not dynamics") holds even under the wave. "map-memory + **shape-memory**".

### 1d. Address made physical + refinement (`RESULTS_CONFINED.md`, `RESULTS_CONFINED_REFINE.md`)
- Within a *fixed* coarse vertex type, perpendicular-space placement predicts E≈0 confined-state
  weight, beyond physical incl. long-range (golden #3 +0.094, #15 +0.116; silver up to +0.26;
  platinum up to +0.22). **Survives the FINE vertex-type control** (essentially unchanged), so
  it is genuinely global placement, not finer local detail. Positive in most well-conditioned
  classes; a few ill-conditioned classes marked inconclusive; one clean class (golden #1)
  negative — honest heterogeneity.
- Preferred depth is **per-offset reproducible but class-specific**, NOT a single universal band
  ("resonance" retracted).

### 1e. Preferred-depth "onion" (`substrates/RESULTS_PREFERRED_DEPTH.md`)
- Why each type prefers its own depth: **vertex types tile the window radially** (concentric
  rings), and confined weight follows one **radial profile** (peak at depth ≈ 0.35). Each type
  samples its own radial slice → its own apparent preferred depth. Held-out R²: hull-depth 0.44,
  vertex type 0.34, perp+type 0.59.

### 1f. Address split — radial vs neighbourhood (`substrates/RESULTS_ADDRESS_SPLIT.md`)
- Decompose confined-weight prediction (held-out): **radial window-depth** (silver 0.68, golden
  0.45, platinum 0.21) + **angular ≈ 0** everywhere + **neighbourhood address organization**
  (+0.22 / +0.34 / +0.53), which **survives fixing the fine vertex type**. Clean trade: the
  least-radial family (platinum) is the most neighbourhood-organized. The neighbourhood term is
  the *same* multiscale-address features the coherent wave reads in transport — closing the loop
  between "a law reads the address" and "the address made physical".

### 1g. Residualization — ROADMAP step 1 (`substrates/RESULTS_RESIDUALIZE.md`)
- Cross-fit residualization (golden, coherent primary LDOS): plain M4-over-M3 reproduces
  (**+0.027**), address is ~0.47 predictable from M3, and the **M3-orthogonal residual of the
  address adds only +0.004**. So the address's transport value is in the part **shared with**
  the physical descriptors — a compact multiscale **re-encoding**, not an orthogonal hidden
  channel. Consistent with the shuffle-kill and long-range-physical survival. **Caveat:**
  nonlinear residualization is lossy, so +0.004 is a *lower bound*; the four-times-controlled
  plain increment remains the headline. This *refines the interpretation*, does not overturn it.

### 1h. Deliverables
- `docs/where_memory_lives.html` — an illustrated field report of the whole arc (also published
  as a private Claude artifact). `SYNTHESIS.md` Part II — the narrative. `ROADMAP.md` — next
  checks. `LEADS.md` — dated breadcrumb.

---

## 2. Nulls and superseded conclusions (kept explicit)

- **Superseded:** "memory reads memory / journey-memory" (temporal phase-accrual) → **shape-
  memory** (stationary spectral structure). Dynamical interference adds ≈nothing.
- **Superseded:** "resonance at a universal internal-space depth" → **class-specific,
  reproducible preferred depth**, explained as one radial profile sampled by radially-ordered
  types.
- **Corrected:** "the classical walker has no eigenstates" → it has spectral modes; the real
  contrast is **coherent amplitude dynamics vs stochastic probability relaxation**.
- **Corrected wording:** "locally identical vertices" → "same **coarse** vertex class"; "type
  purely decided by depth" → "**strongly organized** by depth".
- **Mispredicted (recorded):** the sealed guess that E≈0 would be *weaker* than the mid-band —
  the E≈0 secondary window actually showed *larger* address increments (golden +0.055 etc.).
- **Tempered:** "address = independent hidden channel" → "address = multiscale re-encoding of
  largely-shared local structure" (from 1g).
- **Standing nulls (Part I):** no quasiperiodic-specific recovery / history-retention / state-
  space tendency under free dynamics; no defensible 8/10/12 fragility hierarchy.

---

## 3. Unresolved confounds / open questions

- The **re-encoding vs orthogonal** question (1g) rests on a *lossy* nonlinear residualization;
  the +0.004 is a lower bound and only golden/coherent-primary was run.
- **Silver/platinum** partial-address attribution not fully pinned (how much real address vs
  long-range structure).
- Whether the **radial + neighbourhood split** holds for the observable the wave actually reads
  (**mid-band LDOS, IPR**), not just E≈0 confined weight.
- Whether the **class-specific preferred depths** follow a deeper rule (e.g. each type's own
  window geometry).
- The **"weave" reclamation** (weave = multiscale neighbourhood-address organization?) needs the
  *old* weave metrics dug out of the repo history for a fair comparison.
- **Haken–Strobl dephasing sweep** not done (parked; mechanism-shape / robustness).

---

## 4. Pre-registration status

- `substrates/PREREG_transport_hierarchy.md` — **SEALED** (`1f6222c`); confirmatory run complete
  (`RESULTS_TRANSPORT.md`).
- `substrates/PREREG_lifted_defect.md` — **SEALED**; Gate 0 run, outcome (b); Amendment 1
  records the outcome.
- `substrates/PREREG_degree_controlled_address.md` — **SEALED** (Part I) + amendment for the v2
  reconstruction metric.
- `substrates/PREREG_intrinsic_drift.md` — **SEALED** (Part I) + amendment.

---

## 5. Exact recommended next step

**ROADMAP step 2 — the progressive physical-radius ladder.** Enrich the physical baseline
r = 2 → 4 → 8 → 12 (instead of a single M3-far) and watch the coherent M4-over-M3 address
increment. If it *fades* as physical radius grows, the address is a brilliant compression of
long-range geometry; if it *survives stubbornly*, that is more interesting. Pair it with the
cheap, high-value **ablation** (ROADMAP step 5): remove the neighbourhood-address feature groups
one at a time (shell-mean vs variance vs gradient vs hull-depth) to see which actually carry the
transport increment. Then re-verify the radial-vs-neighbourhood split on **mid-band LDOS**, not
just confined weight (ROADMAP step 3). Do the synthesis only after these settle (step 11).

**Standing language rules:** keep to *"perpendicular-space descriptors capture transport-relevant
multiscale structure not exhausted by the tested physical descriptors"* (no "perp space is
physical"), and *"address sensitivity lives in the stationary spectral structure of the coherent
Hamiltonian and does not require dynamical inter-eigenstate phase interference"* (no
"phase-memory of the journey").

---

## 6. File index (key, this session)

Code: `substrates/{lifted_defect.py, lifted_defect_gate0.py, multigrid.py, transport_run.py,
wave_pilot.py, wave_dephasing.py, confined_address.py, confined_refine.py, preferred_depth.py,
address_split.py, residualize_check.py}` + `plot_*.py`.
Results: `substrates/RESULTS_{GATE0_DEFECT, TRANSPORT, COHERENCE, CONFINED, CONFINED_REFINE,
PREFERRED_DEPTH, ADDRESS_SPLIT, RESIDUALIZE}.md`.
Pre-regs: `substrates/PREREG_*.md`.
Narrative/meta: `SYNTHESIS.md` (Part II), `ROADMAP.md`, `LEADS.md`, `THREE_COMMANDMENTS.md`,
`docs/where_memory_lives.html`.
Figures: `substrates/*.png`.

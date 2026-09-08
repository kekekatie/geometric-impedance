# The accretion pilot — overview & index

*A self-contained, isolated exploratory research program on **memory and growth in small
evolving graphs**. Register: **speculative computational exploration** — every result is
bounded, gated, and stated with its limitations; nulls and corrections are kept in place.
It is **not** a confirmatory study, and makes **no** claim about physics, cosmology,
biology, or minds. This document is the reader's entry point and a complete index; it is
intended as a durable, citable snapshot (see [`CITATION.cff`](CITATION.cff) and
[`RELEASING.md`](RELEASING.md)).*

Snapshot date: **2026-09-08**. Repository: `kekekatie/geometric-impedance`, path
`exploratory/accretion_pilot/`. Commit chain: `cc514ee` (v1) → … → `fc973a1` (latest).

---

## The question, and the two threads

**Core question.** If a world changes its own structure as things happen in it, can those
changes *remember* an earlier history while also *opening up* new possibilities — and, if a
memory is present, is it *accessible*, and can a later change make a dormant trace *matter*
again?

The program runs in two threads.

### Thread A — Accretion pilot v1–v14 (a walker on an evolving substrate)

A weighted graph whose edges strengthen with use (a bounded, saturating rule) and which can
switch on new "shortcut" edges from a fixed finite catalogue once local wear passes a
threshold. Two matched histories A/B are imposed; readers then ask what is still
distinguishable. The throughline:

> **globally present → locally accessible → start-robust**, and **no detectable advantage
> of quasiperiodic (Penrose) over perturbed substrate.**

Consolidated in **[`SYNTHESIS_v1_v14.md`](SYNTHESIS_v1_v14.md)** — read that for the
plain-language whole.

### Thread B — Endogenous growth (a self-rewriting graph, no walker)

Katie's reframing: *the track and the traveller are inseparable.* So the traveller is
removed and the graph rewrites itself by purely local events. A minimal non-confluent rule
(**M1**, "Competitive Accretion Grammar") is proposed, audited, and probed. The throughline:

> **history leaves a structural record → the "active front" evolves as a closed system, so
> the quiet archive is causally inert → but one added local rule can make that dormant
> archive matter again.**

---

## Complete index (each folder self-contained, with its own README + checks)

### Thread A

| folder | one-line result |
|---|---|
| *(root)* `README.md`, `REPORT.md`, `accretion_pilot.py` | **v1** — memory and opportunity can coexist; history-shaped growth is the most durable memory and also widens movement. |
| [`v2_saturation/`](v2_saturation/) | timing-matched control, run to 10k steps: memory **magnitude vanishes but signed ordering survives**. |
| [`v3_precision/`](v3_precision/) | finite-precision readout: the growing world's signal **survives coarse measurement**; a fragile residual does not. |
| [`v4_decomposition/`](v4_decomposition/) | reader decomposition: the late carrier is **added-edge weights, not topology** (corrects a v3 claim). |
| [`v5_onebit/`](v5_onebit/) | a **single bit per added shortcut** (≥4 re-crossings) retains the late distinction. |
| [`v6_intervention/`](v6_intervention/) | crossed 2×2 initial conditions: **both** inherited weights and placement matter. |
| [`v7_directionality/`](v7_directionality/) | alignment governs **direction-consistency across seeds**, not per-world magnitude. |
| [`v8_neutral_weights/`](v8_neutral_weights/) | placement alone (neutral background) gives only a **fleeting early** bias. |
| [`v9_substrate_design/`](v9_substrate_design/) | design + feasibility for a Penrose-vs-perturbed comparison (no sims). |
| [`v10_construction/`](v10_construction/) | de Bruijn **pentagrid construction** + frozen reader, validated (no production sims). |
| [`v11_substrate_pilot/`](v11_substrate_pilot/) | **regular Penrose vs perturbed pentagrid: no detectable difference** in memory persistence. |
| [`v12_local_reader_design/`](v12_local_reader_design/) | local-accessibility design + honest v11 closure. |
| [`v13_local_reader/`](v13_local_reader/) | a **bounded tagged local visitor** recovers essentially the global discrimination — memory is **locally accessible**. |
| [`v14_visitor_start/`](v14_visitor_start/) | a **distant start** recovers it too — discrimination is **start-robust** (a travel-cost effect only). |
| [`SYNTHESIS_v1_v14.md`](SYNTHESIS_v1_v14.md) | the consolidation: claims table, four-level separation (stored / accessible / autonomous use / transmission), future questions. |

### Thread B

| folder | one-line result |
|---|---|
| [`endogenous_growth_design/`](endogenous_growth_design/) | pivot to local graph rewriting; proposes **M1** (non-confluent) vs M2 (confluent null); tiny feasibility checks. |
| [`endogenous_growth_audit/`](endogenous_growth_audit/) | repairs M1: proves `ΔB = k − d_A(y)` (no deadlock), scopes the confluence claim to finite depth, exact class enumeration. |
| [`endogenous_active_projection/`](endogenous_active_projection/) | **the active front is a closed transition rule**; the quiet archive is **causally inert** (write-only) under the active-bond scheduler. |
| [`endogenous_latent_relevance/`](endogenous_latent_relevance/) | a later local (read-only) change can **make a dormant trace matter** (first version: a controlled global sweep). |
| [`endogenous_local_contact/`](endogenous_local_contact/) | the same effect under an **autonomous local CONTACT event** competing in the scheduler; plus corrected exact checks. |
| [`endogenous_contact_timing/`](endogenous_contact_timing/) | **proves a quiet vertex's CONTACT menu only shrinks** — the model supports *delayed consultation* of an already-eligible trace, not *newly enabled relevance* of an old one; exact 3-event timing. |
| [`endogenous_renewed_contact_design/`](endogenous_renewed_contact_design/) | design comparison of the three ways to break menu monotonicity; recommends **GRAFT** (new active structure grafts onto an old quiet trace via a bounded wedge, append-only) to enable genuinely *new* relevance; legality fixture + proposed test (not run). |

*(The root `README.md`, `REPORT.md`, `DESIGN_NOTE.md` are v1's own documents, preserved.)*

---

## How to reproduce

Each folder has its own `README.md` with a `Reproduce` block. In brief:

- **Thread A** (Python + numpy; v10+ also `networkx`, `matplotlib`): run the numbered
  scripts inside each `v*/` folder. The heaviest is v11 (~50 min); v13/v14 replay v11's
  retained snapshots (~5–15 min). Determinism is seeded; validation gates are included.
- **Thread B** (Python + `networkx` + `matplotlib`): each `endogenous_*/` folder has a
  `*_checks.py` that runs tiny **exact** enumerations with `assert`s and a **nonzero exit
  on failure** — no stochastic sweeps. They finish in seconds.

## Scope & limitations (umbrella — each folder states its own too)

- **This is a toy.** All results are properties of small constructed models, not of the
  natural world. Registers are stated per folder; speculation is kept separate from
  findings.
- **Aided / designed-in readers and couplings.** Where a distinction is "accessible" or
  "made relevant", the reader is given tags or the coupling is an explicit modelling
  assumption — never a spontaneous discovery. The four levels **stored distinction /
  aided accessibility / autonomous use / transmission** are kept distinct; only the first
  two are demonstrated.
- **Finite catalogue.** "Growth" in Thread A activates a pre-declared finite set of
  connections; Thread B creates new vertices but stays within a fixed grammar. Neither
  establishes inexhaustible growth.
- **No equivalence claims from nulls.** "No detectable difference" (e.g. Penrose vs
  perturbed) is descriptive of the specific cases, not proof of equivalence.

## Method note (why this record is trustworthy despite the speculative register)

Every quantitative claim is gated in code; overclaims that were caught are **withdrawn in
place with dated corrections** rather than edited away (see the correction notes in
`v3`, `v4`, `v6`, `v7`, `v8`, `v11`, and the `endogenous_*` folders). The practice is
deliberately more conservative than the exploratory register requires.

## Citing / authorship

See [`CITATION.cff`](CITATION.cff). This work was **human-led** (Katie), **co-designed**
with a GPT collaborator ("Astra"), and **implemented** with Claude (Anthropic). How to
represent that authorship is the author's decision; the citation file carries a neutral
default to edit. To mint a permanent DOI, follow [`RELEASING.md`](RELEASING.md).

# The accretion pilot — overview & index

> 🧭 **Lost?** The compass is [`THREE_COMMANDMENTS.md`](../../THREE_COMMANDMENTS.md) (repo root) — relationality, least resistance, things doing thing things — with the 2026-09-24 "more now" timing addendum.
>
> 👋 **Picking this back up?** See [`RESUME_HERE.md`](RESUME_HERE.md) — the next thing waiting
> is consolidating the **transmission paper** (no new experiment needed; built around the exact
> result `L = 4321/44100`).

*A self-contained, isolated exploratory research program on **memory and growth in small
evolving graphs**. Register: **speculative computational exploration** — every result is
bounded, gated, and stated with its limitations; nulls and corrections are kept in place.
It is **not** a confirmatory study, and makes **no** claim about physics, cosmology,
biology, or minds. This document is the reader's entry point and a complete index; it is
intended as a durable, citable snapshot (see [`CITATION.cff`](CITATION.cff) and
[`RELEASING.md`](RELEASING.md)).*

Snapshot date: **2026-09-09**. Repository: `kekekatie/geometric-impedance`, branch
**`claude/world-growth-pilot-cy85ne`** (not `main` — the work lives on this branch), path
`exploratory/accretion_pilot/`. Commit chain: `cc514ee` (v1) → … → the GRAFT experiment
(latest: Thread B's renewed-contact test, run exactly).

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
> the quiet archive is causally inert → but one added local rule (GRAFT) can make that dormant
> archive matter again — and, in exact reachable dynamics, that renewal both occurs and is
> consulted, which is provably impossible without the rule → and once the archive has acted,
> its influence durably biases the **ensemble** of possible presents (it survives deletion of
> the archive — a tendency over the distribution, not a per-world memory), yet the archive is
> still not redundant → and that bias is bounded (the present inherits only a fraction ρ<1 of
> its past) and, once the past is deleted, can only fade to an **exact positive limit**
> (L = 4321/44100, Proposition 3), held above it only while the past is re-read → and across the
> whole class set the fate is governed by the coast's **absorption geometry** (`L = TV(absorption
> distributions)`): **the past can only leave a lasting mark where the future forks** — among
> *expressed* pairs, `L>0` iff the coast has ≥2 reachable sinks (verified on the enumerated set,
> not proven; durability is a property of the dynamics, not the history). (At depth-2 this looks
> like "fate decided at step one" with washout empty — a clean special case that depth-3 shows is
> not the general law.) → while GRAFT-enabled renewal, impossible without the rule everywhere,
> occurs in **20/22** traces with it.**

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
| [`endogenous_renewed_contact_design/`](endogenous_renewed_contact_design/) | design comparison of the three ways to break menu monotonicity; recommends **GRAFT** (new active structure grafts onto an old quiet trace via a bounded wedge, append-only) to enable genuinely *new* relevance; legality fixture + proposed test. |
| [`endogenous_graft_experiment/`](endogenous_graft_experiment/) | **the GRAFT test, run exactly.** On a frozen seed with a designated quiet trace whose menu starts empty: with GRAFT, the trace acquires a never-before CONTACT pair (**27.2%** by 4 events) that is then **consulted** (**7.5%**); the **control (BUD+CONTACT) is exactly 0** at every horizon (menu monotonicity). Renewal both **occurs and is consulted** — impossible without the rule. Mechanism test, one seed, not a sample. |
| [`endogenous_erase_test/`](endogenous_erase_test/) | **the ERASE test (Fable's).** Evolve the matched pair under BUD+CONTACT, **delete the whole archive**, run the future archive-free. **Q1:** the two lineages' present-**ensembles still differ** with no archive present — the past **durably biases the distribution over active slices** (survives erasure; not a per-world memory); **Q2:** yet deleting the archive **changes** the future (`ERASE≠KEEP`), so the archive is **not redundant**. NULL (BUD-only) control is exactly identical. Both true at once; exact, one pair. |
| [`endogenous_pair_robustness/`](endogenous_pair_robustness/) | **is L one example's property?** Exact `L` for **all 11 depth-2 matched pairs** + a **depth-3** stress test (97 pairs). Structure universal; value/fate is the pair's. At depth-2: 8 durable, 3 inert, **0 washout**, fate decided at step 1 (`L=0` ⇔ **menu-equivalent**) — a clean special case. At **depth-3 both break** (`depth3_criterion.py`): washout is real (expressed yet `L=0`), step-one no longer decides. **Fork law:** `L=TV(absorption dists)`; among expressed pairs `L>0` iff ≥2 reachable sinks (verified, not proven) — *the past leaves a lasting mark only where the future forks*. Featured (3,9) `L₂=2333/17640`; (8,10) same degree sig, largest L. |
| [`endogenous_graft_prevalence/`](endogenous_graft_prevalence/) | **does renewal generalise?** The GRAFT test over **every** depth-2 seed and quiet trace (22 cases). **Control ≡ 0 for all** (renewal impossible without GRAFT, universally); **with GRAFT, renewal in 20/22 (91%)** and consultation in 20/22 (mean renewal ≈0.222 by 4 events). Class 2 is the exact structural exception (no wedge reachable). |
| [`endogenous_present_width/`](endogenous_present_width/) | **the width of "now"** (an **ensemble** bias, never a per-world memory). Quantifies the ERASE mark. **How much:** the surviving fraction `ρ=present/full` distinguishability rises from **0** (history starts entirely in the archive) to **~0.22** by 3 events, staying **< 1** (present inherits a bounded share). **How long:** delete the past and the present coasts — distinguishability is **provably non-increasing** (data-processing on the projection kernel, Prop 1) and **converges to an exact positive limit `L=4321/44100`** (**Prop 3**: a finite absorbing chain, since `ΔA=0` at `k=1`) — so a positive bias persists with **no past at all**; with the archive **kept** it stays **≥ the coast at every tested step** (the past *raises* the distinction above the floor, it does not sustain it). Exact, one pair. |
| [`pair_collision_toy/`](pair_collision_toy/) | **two bonds, one shared quiet.** Start: bonds a–b, c–d plus quiet q~a,c; BUD+CONTACT to frozen. **P(CONTACT ever fires) = 1/3 exactly** (5 events: 1 collision, 2 kill, 2 neutral). **P(one pair + two loners) certified in [0.123896379462952, 0.123896379462967]**, so **not 1/8** (the reduced chain stays infinite after menu-monotone pruning; truncation plus exact rational sub/super-solution certificates). **Lemma:** BUD-only recurrent classes are singleton matchings, for any seed (proof sketch, exhaustive on all 208 graphs with n ≤ 6). |
| [`twins_mirror/`](twins_mirror/) | **perp-space bridge, phase 1 (mirrors).** BUD grows *on* the Fibonacci chain (rate 1/ℓ, lengths inherited, continuous time, rules never read the address). For 6 far-apart pairs with first-disagreement radius r*=1..6, the exact short-time expansion of P(site active) **agrees below order r* and first differs exactly at r***; blind control identical. *Hidden-address depth = length of the shared future.* Design note parks Phase 2 (messengers / resonance) with a pre-registered address-blind-revival control. |
| [`tick_forward/`](tick_forward/) | **Katie's topple: what postcode does a newborn get?** TICK (the parent's hidden address stepped forward by the window's own map) vs CLONE vs RANDOM. After the downhill collapse, TICK pairs keep writing forever: **only legal tiles, never repeating, exactly n+1 patterns of length n (the Sturmian minimum), 0 random bits spent on content**; CLONE freezes, RANDOM costs ~0.96 bits/symbol and writes noise. *The dice decide when, the geometry decides what.* Lineages meet at identical postcodes (perfect twins, structural). |
| [`geometric_clock/`](geometric_clock/) | **can the when come from the geometry, and can the now grow?** (Katie's "more now".) k=1: a SWEEP clock (next postcode around the window, always falling forward) imports **0 bits**, is exactly fair, and the whole universe's history never repeats with only linear variety (2n); a HAND clock **phase-locks** onto one lineage (finding). k=2 (keeper's next + previous house): **nothing ever leaves the now** (proved + checked); under SWEEP every event claims a new house — **more now = more space, 1:1** — while dice make the now crowd and spread only like √t. |
| [`penrose_address_environment/`](penrose_address_environment/) | **one step closer to E8 (5-D → 2-D, same τ).** Exact pentagrid with integer ℤ⁵ identities (31,306 vertices): genuine Penrose (4 window layers, small/large pentagons in ratio τ, exactly 7 vertex-star types). **Address → environment holds in 2-D**: each vertex type owns its own window regions; deeper agreement forces closer hidden addresses (1.80 → 0.23); twins agree through radius 7 up to 60 apart. **More information per step up the family**: complete counts 62 … 1,454 vs 1-D's 3 … 15 (97× at r=7), superlinear (~r^1.6 here; the predicted r² NOT confirmed). |
| [`least_resistance_paths/`](least_resistance_paths/) | **is there a path of least resistance? (Katie + Gemini.)** On Penrose: the projection opens only 3–7 of 10 directions; the same step repeats at most twice (7.3%) — straight lines in the world are forbidden. **Greedy walkers are trapped** (300/300 loops for both 'straightest' and 'most central'). **Momentum in the hidden grid works**: ribbon walkers (one grid coordinate fixed, always forward) cross the world 4,500/4,500, never looping, with a **menu of 1–3 ways forward (2+ on 58% of steps)**; the bias picks the route. Gives 2-D growth its 'next house': the next vertex along your ribbon. |
| [`penrose_growth/`](penrose_growth/) | **first 2-D growth: does the growing now fill space in every direction?** Held-set accretion on Penrose along the roads: every event adds exactly one house, nothing ever leaves. **Momentum alone (RAY) gives a line** that runs off the world; **momentum + branching (FORK) fills space in every direction** (round blob, radius ~√t). The import-nothing queue clock grows a **rounder (0.91 vs 0.67–0.81), near-decagonal** now with **fewer holes (11 vs 34–42)** than 5 dice seeds. Gaps in the now are *lag*, not skips: every one has a road in and is filled later (corrected via `seed_crystal/`). |
| [`seed_crystal/`](seed_crystal/) | **first gentle resonance census (Katie's seed crystal): would twins fill the now's gaps sooner than the roads?** Gaps are lag (every one has a road in; filled after ~110–150 events). At shallow likeness depth a **twin seed already waits for every gap** (a shortcut); **deeper likeness → rarer, farther in the world (5 → 34), closer in the hidden window (0.45 → 0.07)**; seeds run out at depth 3–4 (the nothing-happens case); wrong-shaped dust fits only 9%. Census only; no resonance dynamics yet. |

### Standalone geometric note

| folder | one-line result |
|---|---|
| [`fibonacci_address_environment/`](fibonacci_address_environment/) | exact 1-D Fibonacci cut-and-project: proves the **local environment is a function of the internal (perpendicular) address alone** — same window cell ⇒ identical environment at any physical distance; a cell boundary between ⇒ different environment even for near-equal addresses; resolution = cell width. **Extension:** the first-disagreement radius `r*` of two same-`E_2` sites = the level at which the monotonically-refining window partition first separates their addresses ("same here, different farther out"; unresolved-within-patch ≠ identical forever). **Proof + motion (`MOTION.md`):** eventual disagreement tightened via aperiodicity/point-separation; a length-sensitive (`1/ℓ`) nearest-neighbour walk's exact `ℚ(τ)` return probabilities first differ at step `2(r*−1)` (length-blind control identical; reflection-degeneracy checked). Geometry + one chosen walk only. |

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

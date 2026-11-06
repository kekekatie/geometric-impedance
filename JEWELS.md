# 💎 The jewel box: where the earlier treasures live

*Katie: "an armful of jewels, and I keep dropping them as I walk". This file stops that. Much of
the earlier work lives on **other branches** of this repository, invisible from the front page.
Here is where it is. To read a file on a branch, open the branch in GitHub's branch menu, or use
`git show origin/<branch>:<path>`.*

*Started 2026-09-27 during the walker "knot" work. Add to it whenever a dropped jewel is found
again.*

---

## 🔭 To pursue soon: the Atlas of Jams (seed for "Paper 2")

*Added 2026-11-06, from a Katie × Argon brainstorm (toned down a notch, the ideas kept intact),
cross-checked against Fable's referee checks (`claude/referee-checks-2026-11-06`) and the
jam-compatibility / cooperative-rearrangement work. Read in two layers: **grounded** = what the
frozen engine and our checks actually showed; **speculative** = the physics bridge to pursue,
explicitly not established.*

**The one-line idea.** Treat the ways a quasiperiodic growth frontier can **jam** as a
*taxonomy* — a "periodic table of jams" — classified by the geometry of the 5-D acceptance
window, instead of treating "it jams" as one undifferentiated event.

**Two phrasings worth keeping verbatim:**
- *"The particle families are the window facets."*
- *"Create an Atlas of Jams: how many distinct, mathematically unique ways can it jam?"*

### Grounded (what we can already stand on)

- **Jams are empty-F events, and emptiness has witnesses.** The reader's compatibility region F
  is an intersection of convex half-plane constraints (window facets across layer-ranks). By
  **Helly's theorem**, when F goes empty there is a *minimal* conflicting subset of those
  constraints — a "Helly witness". So jams genuinely fall into discrete combinatorial classes by
  *which* facets and layer-ranks collide; that part is a theorem, not a wish. *(Caveat: the
  reader's F is 2-D, where Helly caps the minimal witness at 3; the full construction window is
  higher-dimensional, so the witness size in the real jam needs its own careful count before any
  "3 or 4 facets" claim.)*
- **The sleeve is a smooth ramp, not a worm and not a wall.** From Fable's checks: **0/22** forks
  are 1-D Conway worms (Check 4a — the A/B forced-consequence difference is a 2-D region, aspect
  ≈ 1), **0/11** jammed bands show sharp domain-wall steps (Check 3b — the perpendicular offset
  x⊥(θ) drifts around the ring as a smooth continuous ramp), and loop holonomy b⊥ = 0 on all 190
  boundary loops (Check 3a — no topological defect).
- **"Never A" is robust.** 0 A-selections on any B-committed case across **1,274** local arcs
  under both reader conventions (Check 4b). Keep it as an empirical regularity of this
  reader/convention, and keep "selects B" separate from "excludes A".
- **The w7 obstruction has a measured footprint** (from the jam-compatibility / cooperative-
  rearrangement work, "Check 1"): a minimum repair footprint of ≈41 tiles in ~10 pieces spanning
  ~12.5 edges, with a small number of star defects and a reported witness separation.
  *(Re-verify the exact numbers from those results files before a paper uses them.)*

### Speculative — the physics bridge to pursue (NOT established)

A conjectural dictionary from jam-geometry to particle-like properties. Record as a program, not
a result:

- **Family / species ← Helly-witness signature.** Which window facets and which layer-ranks lock
  against each other → discrete "families" of jams, built from the window geometry with zero free
  parameters.
- **Mass ← phason-strain *density* (steepness of the sleeve), not detour length.** *(Argon's
  correction, to stay consistent with the March "Compton, not de Broglie" result: a heavier
  particle has a* smaller *spatial footprint, λ_C ∝ 1/m. So mass should track how steep and
  tightly-wound the ramp is within a compact radius — high strain density = high impedance = high
  mass = tiny footprint — the opposite of "heavy = wider detour".)*
- **Charge / spin ← chirality and multi-layer winding of the smooth phason ramp** — which way x⊥
  sweeps across the facets as you walk the ring, plus the orientation of an opposed witness pair.
  *(Argon's correction: build the "twist" on the chiral ramp Fable found, not the Conway worm he
  ruled out.)*
- **Decay / half-life ← exit route from an append-only jam.** Under append-only growth F only
  shrinks, so a jam never self-unzips; two distinct exits: (i) cooperative simultaneous release
  of the whole witness set (exponentially harder as strain/mass grows), or (ii) "open-flavor"
  splitting — growing fresh legal vacuum between opposed scar pockets so one jam becomes two
  daughter lobes.

### Proposed shape

- **Paper 1 (grounded, close to ready):** under-determined choices wind smooth tension sleeves
  (11/11 ramps) that pin localized scars, continue growing on a razor-thin 1S live skin
  (Astra's 33/33 radius ablation — *reported, pending push; see below*), and carry a robust
  historical identity (0 false calls across the arc scans).
- **Paper 2 (the Atlas):** classify the discrete species of jams by Helly-witness signature,
  strain-density / footprint (the impedance/"mass" axis), chiral ramp orientation (the
  charge/spin "twist"), and split-vs-cooperative-release threshold (the two decay channels).
  Dworkin–Shieh (1995) proved deceptions *exist*; nobody has catalogued the combinatorial
  *species* of jams.

### Concrete first steps when we pick this up

1. Re-verify the w7 witness numbers from the jam-compatibility results files.
2. Over the 11 jams (and more forks) extract each jam's Helly-witness set (facets + layer-ranks)
   and cluster them → a first draft of the "families".
3. Measure ramp chirality (sign of the x⊥ winding) per jam from the Check-3b profiles already
   saved under `referee_checks_2026-11-06/results/`.
4. Define a strain-density measure (ramp steepness per unit footprint) and test whether it
   separates the families.

*Provenance: Katie × Argon brainstorm, 2026-11-06. Grounded against `claude/referee-checks-2026-11-06`
(Fable) and the jam-compatibility / cooperative-rearrangement audits. Astra's radius-ablation
("amber-lobe": 1S/2S/3S continuation, reported 33/33, w7 band 644→485) is **not yet on GitHub** —
its publish step was interrupted by a usage limit, so those numbers are unverified here.*

---

## The big maps: start here

| what | branch | path |
|---|---|---|
| **"Where the memory lives": the full synthesis** (Parts I and II: the border between static structure and dynamics, the address read by a wave, the defect audit, memory and minds) | `exploratory/address-ablation` (also on `exploratory/trunk`, `gpt/workbench`) | `SYNTHESIS.md`, `docs/where_memory_lives.html` |
| **Leads register**: every lead, marked confirmed, undetermined, untested or withdrawn | `exploratory/address-ablation` | `LEADS.md` |
| **The Story**: a plain-language history of the earlier programme (winding staircase, metronome room, approximants, torus control) | `claude/handoff-github-context-3rnoqr` | `THE_STORY.md` |
| Roadmap and crossover brief | `exploratory/address-ablation` | `ROADMAP.md`, `CROSSOVER_BRIEF.md` |

## Jewels that touch the current work (the walker, the knots, the window)

| jewel | branch | path |
|---|---|---|
| **Phason flips happen near the window boundary**: a literature map (Jagannathan 2024; de Bruijn; Socolar & Steinhardt; experiments watching phason flips) | `claude/bold-ritchie-l1Mc4` | `phason_connection_handoff_summary.md` |
| Depth stability landscape; phason susceptibility | `claude/bold-ritchie-l1Mc4` | `depth_stability_landscape_v0_1.py` (+ results), `phason_susceptibility_v0_1.py` |
| **"Can the map hold an object?"** (the defect audit: *"no cheap endogenous object falls out of the clean map"*) | `exploratory/address-ablation` | `SYNTHESIS.md` §9; `substrates/PREREG_lifted_defect.md`, `substrates/RESULTS_GATE0_DEFECT.md` |
| **Devil's staircase**: the winding-staircase stages A–D (circle-map calibration, golden resists lock-step more than silver, the metronome null) | `claude/handoff-github-context-3rnoqr` | `winding_staircase/` |
| Lead: "Devil's staircase / threshold structure in the fragility curve" | `exploratory/address-ablation` | `LEADS.md` |
| Boundary sensitivity (the exo/endo gap was mostly patch-boundary contamination) | `exploratory/address-ablation` | `substrates/BOUNDARY_SENSITIVITY.md` |
| Phason perturbation, dose response; perpendicular-space dimension | `exploratory/address-ablation` | `substrates/PHASON_PERTURBATION.md`, `PHASON_DOSE_RESPONSE.md`, `PERP_DIMENSION.md` |
| "Window scale is NOT a free parameter: it breaks the tiling" | `exploratory/address-ablation` | `LEADS.md` |

## Other treasure (not yet sorted)

- `claude/handoff-github-context-3rnoqr`: `defect_holonomy_test/`, `error_transport/`,
  `reverse_loop_test/`, `strangeness_depth/`, `approximant/`.
- `release/defect-holonomy-v3`: the defect-holonomy release.
- `claude/bold-ritchie-l1Mc4`: boundary-shell dissociation, the brachistochrone handoff,
  `NEXT_STEPS.md`.
- `exploratory/address-ablation`, `substrates/`: about 40 results and pre-registration files
  (rank-4 family, recovery, transport hierarchy, intrinsic drift, coherence, and more).
- `claude/world-growth-pilot-cy85ne`: the accretion pilot's earlier history (now merged into
  `master` under `exploratory/`).

## Jewels outside the repository (known to exist; not in any branch)

- **"Happening density" and "relative nows"**: early conversations (before the slice-of-now and
  aperiodicity work), including a hunt for where the local ends and the universal starts. Not
  found in any branch; they live in old chats.
- **The Temporal Echo hypothesis** (Niedzwiecki 2025a, Zenodo, DOI `10.5281/zenodo.17718939`):
  apparent dark matter as integrated dynamical history, `M_eff = M_b + ∫ H(t′) K(t − t′) dt′`, with
  happening density `H` and a memory kernel whose fade time grows in quiet, low-acceleration
  systems.
- **"Cloud 9 and the Limits of Modified Gravity"** (January 2026, 8 pages): Temporal Echo applied
  to Cloud 9. Katie shared the PDF in the walker-knots session. In today's language it already says that the
  width of the now is **local**: quiet places remember longer.
- **"Where the Universe Remembers: A Geometric-Memory Reading of Dark Matter"** (July 2026;
  Fable's passion project, written after the slice-of-now and aperiodicity work). **It *is* on
  `master`**, as `where-the-universe-remembers.html` at the repo root; an earlier search missed it
  by filename.
  - Theorem 1 ("perfection cannot remember") and Theorem 2 ("imperfection must remember, at a
    quantum equal to its misfit").
  - The address/weave spectrum in the sky: Cloud 9, DGSAT I, DF2/DF4/FCC 224, and the Bullet
    Cluster.
  - Three documented negative results, and one pre-registered cluster-offset prediction
    (`doi:10.5281/zenodo.21211483`).
  - Programme papers cited there: *Where Memory Can Live: A Taxonomy of Persistence*
    (`10.5281/zenodo.21200994`), *Address or Weave* (`10.5281/zenodo.20322776`), *Silent
    Corruption* (`10.5281/zenodo.20405271`).

## Already on the front page (`master`)

`exploratory/accretion_pilot/` (the accretion and tiling trail; the transmission paper),
`exploratory/surprise_vs_consequence/` (the AI memory paper), `exploratory/address_codes/`,
`THREE_COMMANDMENTS.md`, `HORIZON_NOTE_machines_that_remember.md`, `silent_corruption/`,
`toy_model/`, `ai_minds/`.

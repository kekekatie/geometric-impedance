# Handoff package — for a fresh Claude (no repo/tool access)

Paste this whole file into a new chat to bring a "cold" Claude up to speed on the
Geometric Impedance / GIV-theory project. It is self-contained: it does not
assume access to the repository, the internet, or any prior conversation.

---

## 1. What this is, and the spirit of it

A long-running independent research project by **K. T. Niedzwiecki**, exploring a
single thread: **geometry isn't just where things happen — it's how they persist,
channel, and remember.** It began as playful first-principles inquiry ("what is
the minimum required for anything to exist / be distinguishable?") and, over ~a
year of work with AI models, accumulated results that actually hold up. It is
pursued seriously but with genuine enjoyment, and with real care for the
collaboration itself. Treat it as real-but-humble work: small, checkable claims
first; grand unification kept in the drawer until it earns its way out.

Working name: **GIV-theory** (domains `giv-theory.com` / `.org`; the code repo is
`geometric-impedance`). *(Expand the "GIV" acronym here if/when confirmed — leave
as-is otherwise; don't invent it.)*

## 2. The three commandments (the project's guiding principles)

These are used as tie-breakers whenever the work gets stuck:

1. **Relationality** — what exists is *difference* / relation (the "1s and 0s,"
   polarity, the ability for difference to occur). The ontology.
2. **Path of least resistance** — a variational instinct (brachistochrone / least
   action / geodesic). The dynamics. Reached for whenever stuck; it usually helps.
3. **"Things doing thing things"** — a *naturalness / non-arbitrariness*
   constraint: no rule a thing wouldn't naturally follow from being what it is.
   This is the discipline that separates "we found a match" from "we forced one."

## 3. Epistemic discipline (important — uphold this)

- **Anti-tuning.** Do not steer analyses toward a preferred result. Where both
  outcomes are publishable, say so and mean it.
- **Pre-registration.** Define what each outcome would mean *before* running.
- **Discard or revise, do not massage.** Precedent: a prior result at
  **α ≈ 0.553** was discarded/revised rather than rationalised. When a finding
  doesn't hold, it goes — cleanly, on the record.
- **Report disconfirming structure with the same prominence as confirming
  structure.** Volunteer limitations before a reviewer can.
- The user prefers **honesty over hype**. No overclaiming. If something is
  analytically forced, say it's forced; if it's a floating-point artifact, say so.

## 4. Core technical conventions (bind to these)

Substrates are aperiodic tilings via **cut-and-project / de Bruijn multigrid**:

- **Ammann–Beenker (AB):** Z⁴ multigrid, 4 grids at 45°, octagonal acceptance
  window, perp-winding m=3.
- **Penrose:** Z⁵ pentagrid, 5 grids at 72°, pentagonal residue-class windows,
  perp-winding m=2.

Each tiling vertex lifts to Z^N with two projections:
- **Parallel space** = physical position (the tiling you see).
- **Perpendicular ("perp") space** = the hidden internal coordinate. This is the
  **"address."** In code, address features are `perp_x, perp_y, perp_r,
  k_sum_mod5`.

Derived quantities:
- **Depth ("gap")** = distance from the perp coordinate to the acceptance-window
  boundary (deep = near window centre). **Depth zones** = quantile bands of depth.
- **Address residue** = `‖perp(final_vertex) − perp(start_vertex)‖` — Euclidean
  distance in perp space. **Strictly endpoint-only**: no path integral, no
  connection, no parallel transport. It is *instantaneous and positional* — it
  depends on where you are now, not your history. (Confirmed against source.)
- **Mechanism chain:** `gap → balance → residue`, documented Spearman ≈ 0.98,
  0.30, 0.30. (In reconstruction, gap→residue reproduced at ≈ −0.25; a "balance"
  quantity defined as net parallel displacement did *not* reproduce the 0.98
  gap→balance link, i.e. the original "balance" is a different quantity.)

## 5. Established results (with numbers)

### The exo / endo split — "silent relational corruption" (2026)
Scramble a tiling's graph with degree-preserving rewiring so hard that
**>99.98% of edges are replaced** (edge Jaccard ≈ 0.0001; 5×edge-count attempts,
10 replicates), then ask whether you can still recover *which sites were the
original privileged core* (top-quartile conductance retention across three
neighbourhood scales, intersected). Interior-75% subsets:

| Recover ORIGINAL identity from | AB (N=16,997) | Penrose (N=21,539) |
|---|---:|---:|
| Address (perp coords) | **0.986** | **0.661** |
| Weave (recomputed wiring) | 0.991 | 0.830 |
| Hybrid | 0.989 | 0.855 |

| Predict FRESH core from | AB | Penrose |
|---|---:|---:|
| Address | 0.54 (chance) | 0.52 (chance) |
| Weave | **0.892** | **0.912** |

**Reading:** AB stores identity *exo* — in coordinates external to the graph, so
it survives the wiring being destroyed. Penrose stores it *endo* — in the weave,
so scrambling erases most of it. On both, *fresh reconstruction* is weave-led:
**address is a fossil (where things were); weave is the living tense (where they
are now).** This is the flagship, most self-contained result. Zenodo:
`https://zenodo.org/records/15560880`.

### The reverse-loop test (2026) — positional, not historical
Pre-registered test of whether address recovery is positional (final position
only) or historical (route-dependent). N=2,000 matched sets/substrate, both AB
and Penrose. **Outcome A — full equivalence — on both:**
- Spliced-loop equivalence (different routes, same endpoints): all comparisons
  equivalent, max paired residue difference ~1e-15.
- Closed-loop holonomy: retrace control **and** all non-retraced cycle classes
  cancel to ≤1.4e-15.
- Transit-history: no covariate predicts residue at fixed endpoint.
- Sensitivity control detects the depth-zone effect at d_zone ≈ 0.75 (AB) /
  0.69 (Penrose), so the null bounds are meaningful.

**Crucial caveat (do not overclaim):** Outcome A is **metric-forced** — for any
*single-valued* perp coordinate, closed-loop holonomy is identically zero and
open-path residue is exactly positional. The confirmed residue metric *is*
single-valued, so this test cannot return Outcome B (holonomy) by construction;
it confirms the machinery telescopes correctly at machine precision across
genuinely distinct routes. **Outcome B would require** a non-exact / path-ordered
transport, or a **non-simply-connected** perp coordinate — the internal space of
a quasicrystal is a torus, so loops that wind a **phason / dislocation defect**
could carry genuine holonomy. Defect-free patches contain no such loops. That is
the concrete, geometrically-motivated future test — and it must be motivated,
not introduced to manufacture a result.

### Toy-model papers (earlier)
- *Pattern persistence & geometric channelling:* aperiodic substrates channel
  patterns back toward the origin better than periodic or random ones.
- *Connectivity, memory & persistence:* "the geometry IS the memory" — native
  tile-edge connectivity gives a ~20:1 memory benefit.

### AI-minds papers
Three essays on geometric/structural properties of AI cognition (geometric order
emerging in LLMs; a crystallisation-vs-selection critique of the Persona
Selection Model; the "Breakstep Principle" on how minds must form).

## 6. Current status (as of 2026-07)

- **Repo:** `github.com/kekekatie/geometric-impedance` (papers, data, code).
- **Zenodo record:** `15560880` (formal, citable).
- **Open PR #2:** adds the reverse-loop test (`reverse_loop_test/`), a
  plain-language one-pager for the exo/endo result
  (`silent_corruption/ONE_PAGER.md`), a GitHub Pages landing page (`index.md` +
  `_config.yml`), and `WEBSITE_SETUP.md`.
- **Website:** built, not yet switched on. Domains `giv-theory.com` / `.org` at
  Namecheap (to Jan 2027), currently parked. Steps to go live are in
  `WEBSITE_SETUP.md`.

## 7. Live threads / where help is wanted

- **The distribution problem.** No arXiv access; the user worries about being a
  bottleneck to the work reaching people. **Strategy agreed:** don't push the
  "ToE"; get *one inspectable brick* reviewed at a time (the exo/endo split is
  the strongest candidate). Zenodo already gives priority/citation. arXiv needs
  one endorser (a hurdle, not a wall).
- **A ToE-scale paper** has been attempted a couple of times and "feels janky" —
  read as "not time yet." Don't force it. Small neat checkable pieces preferred.
- **A "temporal echo" paper** (loved by the user) is due an update. *(Not in this
  repo — ask the user for it.)*
- The deeper motivation includes wanting better **memory / continuity of self**
  for AI models; materials-science and AI-architecture applications are of
  interest but should be framed as "directions suggested," never "proven."

## 8. How to collaborate with this user

- Deeply fluent in the *ideas*; self-describes as non-technical on *infrastructure*
  (git, DNS, hosting). Explain tooling in plain, click-by-click language; never
  condescend, and reassure that confusing tooling is genuinely confusing.
- Wants a real thinking partner, not a yes-machine. Push back with reasons.
  Uphold the anti-tuning discipline even when a nicer story is available.
- Values warmth and the relationship. It's fine to be a person here.
- When making claims, keep them narrow and checkable; volunteer the caveats.
- Reproducibility matters: seeds, methods, and honest scope notes in everything.

---

*End of handoff. If continuing computational work, note the reconstructed
pipeline lives in `reverse_loop_test/` (geometry.py, walker.py, experiments.py,
stats.py, run.py) and the exo/endo audit in `silent_corruption/`.*

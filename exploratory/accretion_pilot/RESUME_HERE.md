# 👋 Resume here — a note from past-us to future-us

## 🧭 Where we are, at a glance (2026-10-03, after Astra's review)

Three questions hold the whole programme:

| Question | What we have | What's open |
|---|---|---|
| **1. Can a world grow locally?** | Decapod seeds grow by forced moves alone: no global decider, no guesses (`decapod_seed/`). | How general and enduring is that? |
| **2. What mark does the seed leave?** | **Answered (2026-10-07, `window_cells/`):** one exact Penrose window, with the decapod world **on its edge**. 54–60 vertices sit exactly on the window boundary, along the ten ribbons; ordinary worlds have none. The world's hidden position is pinned with zero slack. Not a smear, not shifted windows, not stored disagreement. | Does sitting on the edge explain no-guess growth? (Reading: nothing hidden is left to guess.) |
| **3. Does structure change clocks or motion?** | Quiet and full stripes change *arrival* and *activity* differently (`worldline_body/`, `free_fall/`). | How do structure and happenings **jointly** produce local time? The first answer (`structure_clock/`: deep places settle ~30% slower) **did not survive robustness** (`robustness_depth_clock/`). Its sign flips with disc size, and within vertex type it vanishes: depth was standing in for corner type. Fable's rescue (the window cell sets the clock) also failed (`window_cells/`): settling time follows **where** a place is (how growth arrives), not what kind of place it is. Still open. |

Katie's rattle principle (2026-10-03): keep the intact growing world as the main experiment. Use
separated comparisons only as diagnostic controls, then go back to the whole system.


*Katie, if you're reading this: you asked me to remind you what was waiting in the wings.
Here it is, safe. (This file is the archive doing its job — catching the jewel before it
rolled away.)*

## 🧵 The gold thread ([`gold_thread/`](gold_thread/)), Astra's handover (exploratory stage)

- **Continuation rule:** the tiling's own **ribbons**, i.e. chains of tiles linked by shared parallel
  edges (what the 5D lift counts). Identity comes from contact, never resemblance. No branching is
  possible.
- **Ribbons are conserved.** All ends sit at the frontier (censored); none are inside; none branch.
- **The decapod hole is where exactly 10 ribbons end, 2 per direction**: a dislocation-like, charge-like
  place (Astra's "decapod as mass?" idea).
- **A choice decides mainly one ribbon lying along the now** (51–57% of the strip). It decides the
  ribbon's path, not its existence.
- **Side observation:** after a choice, the two alternative presents can advance at very different
  speeds (24 vs 90 tiles).
- Candidate tests A–D are listed in the README, to choose with Katie.

## 🧷 Fragility ([`fragility/`](fragility/)), Katie's "I can no longer be re-made"

- What can a two-way choice un-make? At every choice, both alternative presents were grown 8 slices
  ahead.
- **A choice decides a whole strip lying along the now** (a zipper sideways along the present, both
  ways from the choice point). Each choice changes 28–89 tiles; the region is 4.6–8.9× longer than
  wide and lies within 2–11° of the front. Off the strip, both presents are identical. See
  `fragility/figures/one_choice.png`.
- **No dead ends:** both options always carry on (0/14 jams).
- **Where, not what:** distance from the front line explains 81% of what is un-made; corner type 9%.
- Only 14 distinct choices (shared histories).
- **Next for decay:** a persisting thread is at risk each time a decided strip crosses it. Do those
  crossings come at memoryless (coin-toss) intervals? That would decide whether there can be a true
  half-life.

## 🪟 Window cells ([`window_cells/`](window_cells/)), Fable's re-reading of the depth failure

- **The clock is not read off the local pattern (window cell).** Within worlds, cells do no better
  than shuffled cells (A1 and A2 failed).
- Cross-world prediction worked (A3), but only because our 20 decapod worlds are slices of one
  tiling. With same-place matches excluded, R² < 0 at every scale.
- Settling time follows **where** a place is, i.e. the route of arrival.
- **Fable was right that depth is just local pattern.** Depth adds nothing within cells (A4). "Choices
  sit deeper" (M1) mostly vanishes within cells (B1).
- R1 **reverses** within cells (B2). Don't rely on it.
- 🌟 **Decapod worlds sit exactly on the edge of the true window** (C, exploratory figure
  `window_cells/figures/window_boundary.png`).
  - 54–60 edge vertices lie along the ten ribbons; ordinary worlds have none.
  - The world's hidden position is pinned with zero slack.
  - Reading: on the knife-edge of every ribbon's two-way choice, with nothing hidden left to guess.
    That would be why decapods grow with no guesses.
  - This replaces both "smeared/shifted windows" and Claude's "stored disagreement".

## 🧪 Robustness of the depth–clock finding ([`robustness_depth_clock/`](robustness_depth_clock/))

- It replicated in new decapod worlds and in ordinary worlds (RA, RB). But the sign **flips** across
  disc sizes (RC failed), and **within vertex type it vanishes**.
- "The present lasts longer deep in the window" is **withdrawn** as a general claim.
- `decision_radius` R1 and `perp_map` M1 need re-checking within vertex type.
- Lesson: depth and vertex type are entangled in Penrose tilings.
- **Paper status:** the depth–time part is not paper-ready. The local/global decider trade-off, the
  decapod no-choice growth, the gromit check and past-or-present are the steadier pieces.

## 🕰️ Past or present? ([`past_or_present/`](past_or_present/)), Gemini's question

- **74% of forced tiles are decided by the last round alone**: the now mostly decides itself (G1
  held).
- Depth does **not** change how far back in time a place must look (G2 failed, ρ ≈ 0).
- The rare long-memory tiles (8+ rounds) sit most at **shallow** depth (5.8% against 2–3%,
  exploratory). That rhymes with "memory at the boundary".

## 🌊 Decision radius ([`decision_radius/`](decision_radius/))

- Deep places can almost never be decided by the thinnest ring of their past: 98% need a wider ring.
  R1 and R2 held in the follow-up, 4/4.
- So "more of the world must weigh in" is supported, modestly.
- The "~10% undecided" surprise turned out to be **an artefact**. Their target reached tiles
  outside the disc that were laid after it finished (27/27). There are no "zippers"; Gemini's
  question prompted the check.
- **Open idea:** are places decided by their past (behind) or their present (sideways along the
  now)? This would need tracing which neighbours actually force each tile.
- **Two dials** (2026-10-05 chat): how long the now lasts = how much has to happen (structure,
  Dial 1) ÷ how fast things happen (happening density, Dial 2). Deep places: ~15% more to happen
  and ~10% slower, giving ~1.3×.

## ⏳ Structure and the local clock ([`structure_clock/`](structure_clock/))

- In intact decapod worlds, **deep** places (in the hidden window) take ~30% longer to settle (C1
  held, 8/8, ρ ≈ 0.23). They also need ~15% more happenings: C2 failed, so there is no universal
  happening budget.
- Their clocks tick slightly slower.
- Tentative reading: **depth is where the present is most open**, holding both the choices and the
  longest now.

## 👀 Two worlds side by side ([`two_worlds_visual/`](two_worlds_visual/))

- Exploratory picture. Within a world, the five slices' hidden addresses are **mixed through one
  cloud**: no translated sector windows.
- The decapod's clouds may be a slightly different (rounder) shape.

## 🔁 Astra's "5D lift around the decapod" check (relayed via Gemini)

Astra's suggested test: if you walk all the way round a decapod world, the 5D address should fail
to close. **It is already answered by our data, and the answer is that it closes.**

- The lift in `perp_map/` (8 worlds, 800 tiles) and `decapod_memory/` (8 worlds, 1,500 tiles)
  includes every loop around the decagon. It found **0 conflicts** in every decapod world.
- This is forced by the maths: any closed loop of edges in a rhombus tiling changes the 5D
  address by `m·(1,1,1,1,1)`. Here `m = 0`, since every world kept exactly 4 layers.
- So the decapod's memory is **not** in the address arithmetic of a loop. It is in **which
  addresses exist**: the window. That shows up as a smeared hull (`perp_map/` M2) and shifted
  sector windows (`decapod_memory/` D1).

## 🪱 Worm lines ([`worm_lines/`](worm_lines/))

- The ten half-worm ribbons were traced (figure).
- The window does **not** jump specifically across them. T1 failed (1/8). T2 failed the opposite
  way: ordinary worlds' ribbons show bigger across/within ratios.
- Decapod ribbons are almost perfectly straight spokes: 0.12 edges RMS deviation from a line, identical
  in all 80 ribbons. Ordinary ones wander (0.25–0.28). The earlier "°/edge" figure was net turning
  only (Astra's correction).
  This hints at a rigid radial order.

## 🧠 Decapod memory ([`decapod_memory/`](decapod_memory/))

- **D1 held (8/8):** slices of a decapod world sit in windows shifted ~1.7× more than ordinary
  worlds. The memory is real and local.
- **D2 failed:** the shifts are not smoothly organised by angle at 18° resolution.
- **Next:** trace the worm lines directly.

## 🗺️ Perp-space map ([`perp_map/`](perp_map/))

- **Choices live deeper in the window** (M1 failed in the opposite direction, 0/12). Open edges
  have depth ~0.45, forced edges ~0.38.
- This fits Katie's directional balance: shallow vertices have truncated direction sets, so they
  are forced; deep vertices have balanced sets, so they are free.
- **A decapod smears the window** (M2 held, 8/8): perp hull area 8–13% larger. Its memory is a
  widened window.

## 💭 Katie's parting thought (2026-09-28): bring in perp space

Where might perp space (the de Bruijn "window" coordinate, from `writing_walker/window_test.py`) inform
today's arc? Candidate moments, noted before they roll away:

- **Choices:** do the 2-option dead surfaces (`gromit_check`) sit where tiles' perp coordinates touch
  the window's edge?
- **Decapods and holonomy:** a decapod is where the perp-space lift fails to close (`decapod_seed`).
- **Two kinds of slow time:** does the local clock rate track position in the window (`free_fall`)?

**Katie's holonomy paper is the toolkit for this.** K. T. Niedzwiecki, *Depth-Dependent Directional
Balance and Discrete Holonomy in Projection Tilings* (June 2026), doi:10.5281/zenodo.20695694. Its
findings:

- near-closed walks leave a perp-space residue;
- the residue is **not** an area law (not Berry curvature) and **not** temporal (linger time has no
  effect);
- it is **positional**: set by hull depth, through depth-dependent directional balance, with an
  inward radial drift near the window edge;
- null-disc controls confirm it is genuine quasicrystal structure.

Its *hull depth* is the natural coordinate for the map.

A natural next study: a **perp-space map** of one grown world, with every guess, jam, fast and slow
region plotted in the window.

## 🍎 Free fall ([`free_fall/`](free_fall/))

- Einstein's rule (the path with maximal proper time; the clock is happenings at the now; c = 1)
  beside the worldline bodies.
- F1 failed: no clear fall toward QUIET.
- F2 failed the other way: paths bulged away from FULL, meaning bodies **fall toward fullness**
  (66/108, mean +1.0 edges, growing with duration).
- The local clock is slowest near FULL (0.44 vs 1.63 happenings per round). **Two kinds of slow
  time come apart:** arrival lateness (QUIET) vs clock rate (FULL most).
- Katie's accretion hunch returns, for proper time.

## 🌌 Worldline body ([`worldline_body/`](worldline_body/)): Katie's persisting body

- A **quiet** worldline (slow happening) in a decapod world makes a **field of slow time**:
  - +4 rounds at 1–2 edges, fading to +0.8 at 6 edges;
  - **exactly 0** on the far side;
  - growing along the worldline (W1, W2 held).
- A **full** (pre-laid) worldline does the opposite: a highway, up to −16 rounds (W3 held).
- W0 failed only by the letter: tiles beyond CONTROL's reach, no conflicts.
- **The gravity-like property is quietness, not fullness.**
- Next ideas:
  - does anything *fall* (a test body that moves in the field)?
  - the fall-off law;
  - the two 1s / holonomy.

## 🕸️ Decapod seed ([`decapod_seed/`](decapod_seed/))

- A ring around an unfillable decagon (a decapod) grows **with zero guesses** in 94/96 cases (Q1
  held). Ordinary fillable rings always need guesses (Q2 held, 4/4).
- This is the first **truly local now**: no global decider, and about twice as fast. But it is not
  round (the sector spread stays ~1.2).
- "A world seeded by a memory (holonomy) needs no choices; a perfect seed must keep choosing."
- A candidate-listing bug was found and fixed. It never affected ordinary growth.
- **Next:** Katie's worldline body in a decapod world; Conway's no-two-1s address and holonomy.

## 🐶 Gromit check ([`gromit_check/`](gromit_check/))

- Vertex-aware ("cleverer") forcing finds **nothing** our Gromits missed: F1 0/26.
- No jam followed an individually doomed guess: F2 0/24.
- Jams come from guesses that are each locally fine but belong to different siblings. The conflict
  is non-local.
- **Next:** the decapod seed (see `LITERATURE_NOTES_local_growth.md`).

## 🧑‍⚖️ Local deciders ([`local_deciders/`](local_deciders/))

- Letting places decide within a horizon h makes the now smoother but jams the world. Every horizon
  ≤ 4 edges jammed 8/8, h = 6 jammed 5/8, and h = ∞ never jams.
- There is no sweet spot (H3 failed). H1 and H2 held; H1 only weakly, on one surviving run.
- Short-horizon jams sit on the seed rim, where simultaneous local choices pick different siblings.
- **Lead:** Onoda, Steinhardt, DiVincenzo and Socolar (1988): a **decapod seed** may let a Penrose
  tiling grow by forced moves alone. That would give a local now with no guessing except along one
  worm. Check the reference, then try it.

## 🏝️ Door 2: island lens ([`island_lens/`](island_lens/))

- G1, G2 and G3 all failed. With the patient scheduler, the world grows **sector by sector**: one
  global queue of decisions.
- A quiet or full island reshuffles the queue. It does not dent a front, so there is no local
  geometry of time to bend.
- **Next:** local deciders, where each region decides when nothing is forced within a horizon
  around it. Then retry the lens, including quietness vs fullness.

## 💡 Speed of light ([`speed_of_light/`](speed_of_light/)): door 1 of relativity and gravity

- A changed choice spreads at a steady **~1 edge per round** (L1 held, α = 0.93), never faster.
- News runs along the edge of the now about **3.2× faster** than the now moves outward (L2 held,
  just).
- Influence fills a whole sibling region, not a thin ray (L3 failed). The past is untouched.
- Caveat: only 12 distinct perturbations. The seeds collapse onto the same few histories.
- **Next:** door 2, a quiet blob as a lens: quietness vs **fullness (Katie's accretion density)**.

## 🧭 Continuation choices ([`continuation_choices/`](continuation_choices/)), built on Astra's repairs

- **The past is fixed:** 508/508 laid spots have exactly one completion.
- **Quietness stretches the *laying*** (P1 held, 2.9×).
- **Uniform slowing only stretches the clock:** P4 held, with the same choices as a pure replay.
- **Unequal pacing:** no detectable change in the choices. But P3's equivalence bound failed (a ratio
  of 1.22, CI up to 1.49), and P2 failed (too uncertain).
- *Exploratory:*
  - **Deciding is shared, laying is local.** The patient scheduler makes guesses wait for everyone,
    so this is partly by design.
  - A spot is laid after ~19 local happenings everywhere.

## 🔍 Astra's checks (2026-09-28): two big corrections

- **"Soft" was always the open edge, never a rearrangement.** 0 same-footprint alternatives in 3,816
  tests. Enclosed small regions have exactly one filling. The "2-edge width of the now" is mostly the
  probe's reach.
- **The jams were caused by the scheduler** guessing while throttled forced moves were pending. A
  WAIT scheduler gives 0/20 jams. The "unequal pace jams" surprise is withdrawn.
- By run: quiet is longer in 8/8 runs (p = 0.0039). The local clock is *not* equal (a ratio of 1.38,
  95% interval 1.21–1.56).
- **Next:**
  - an explicit target region with a boundary condition, plus the WAIT scheduler, plus a
    uniform-slowdown control;
  - then: does quietness change *which* continuations are possible, or only for how long?

## ⏳ Does the now last longer where quiet? ([`quiet_lasts_longer/`](quiet_lasts_longer/))

- Fixed spots are followed through time, and their lifetimes are counted on two clocks.
- **Q1 held:** the now lasts about **2×** longer where quiet, counted in universal rounds (p = 0.0001).
- **Q2 held:** counted in local happenings, the two halves are about the same (a ratio of 1.33).
- **Q0 (the manipulation check) failed:** the quiet half was only 0.69× as busy, where < 0.6 was
  needed.
- *Exploratory:* almost all of a spot's time in the now is the time it takes to be laid. A quiet
  place takes longer to finish happening.
- *Correction:* the throttled-run jams recur at the **same few spots on the seed's rim**, beside the
  quiet/busy line. They are about particular places, not a general "unequal pace jams" law.

## 🐢 Happening density ([`happening_density/`](happening_density/))

- One half of the front is throttled to a quarter speed. The **spatial** width of the now is
  unchanged (H1 held).
- The pre-registered "soft holes are older where quiet" (H2) failed. *Exploratory:* the back of
  the soft band is about 3× older in the quiet half, so the now may *last longer* where little
  happens.
- **Surprise: 3/8 throttled runs jammed**, on the slow side, near the slow/fast line. A fast front
  racing beside a slow one boxes it in. Equal-paced fronts always reconciled.
- **Possible next tests:** the temporal-width claim, pre-registered properly; "unequal pace jams" as
  its own test.

## 🤝 Relative nows ([`relative_nows/`](relative_nows/))

- Two Gromit crowds that drifted into different sibling universes **always merged cleanly** when
  they met (12/12). M3, "they clash", failed completely.
- The meeting happens inside both nows (the soft zone), so the growth rules can reconcile the two
  sides there.
- **Differences meeting inside the now reconcile; a difference forced into the settled past scars**
  (compare the writing walker).

## 🌱 The soft zone: how wide is the now? ([`soft_zone/`](soft_zone/))

- Grown with a **ring of Gromits** (parallel rounds, full matching rules). Holes are poked
  behind the front and re-laid.
- **The now is about 2 tile-edges wide:** freedom 0.39 → 0.22 → 0, and 0/88 holes deeper than 2
  edges are soft.
- **The now is a place, not a time:** old tiles still at the front stay soft (27%); young
  surrounded ones are hard (0%).
- Katie's "quiet places stay open longer" was **not seen** (a weak test).
- A **bug** in the older `laying_the_tiling` vertex check (gaps > π) was found and fixed. Old
  results were re-checked and are identical.
- **Next ideas:** two Gromit crowds meeting (relative nows, running now in
  [`relative_nows/`](relative_nows/)); a proper happening-density manipulation (fast versus slow
  fronts); holes of different sizes.
- **Idea (Katie):** the width of the now may set how *complex* a perception can be (the feel of a
  cat's fur needs a thick now). A future test: do tilings with a richer hidden space (Penrose is 5-D
  underneath; others are 8-D or 12-D) have wider soft zones?

## 🪢 2026-09-27 evening: the knots (see [`writing_walker/README.md`](writing_walker/README.md))

- **The centre knot is a bad-decapod-like defect.** 62 fillings; 1 legal in the pristine tiling,
  0 after the walker.
- **But 10 of the 12 stuck knots on 18 roads have no decagon ring.**
- **Window ("shaft of light"):** stuck knots lie further outside the window. Size predicts
  better. Medium knots are where the window matters most.
- **A jewel's correction:** these knots are locally trapped, not topologically conserved.
- **`JEWELS.md` (repo root)** indexes the earlier work on other branches. Read it before chasing
  anything old.
- **Open next (Katie picks):**
  - what decides which big knots get stuck;
  - why the centre (the mirror line) gathers the biggest trouble;
  - the devil's-staircase scaling of the walker's steps;
  - the perp-space paper, later, once the understanding is there.

## 💬 Open conversation with Katie (2026-09-27): walking around the *whys*

- **Quantisation from fit, not from pixels.**
  - The walker's record grows in steps because the crossings sit in rows at fixed distances from
    the road. The push is smooth; what the structure lets change is lumpy. That is closer to atomic
    energy levels than to Planck-length graininess.
  - The steps are irregular (quasiperiodic), like a devil's staircase.
- **A pattern across three results:**
  - a lone judge builds an echo chamber (the memory paper);
  - a lone writer leaves scars (the walker);
  - change made in agreement with the whole gives a legal sibling universe (forced growth).
  - Candidate sentence, **corrected with Katie**: *"the present can only change coherently as a
    whole; a part changing alone leaves scars."* Unsure whether that is deep or coincidence.
  - **Katie's correction (important; keep this language):** the past is **never** altered in this
    theory. A slice of now can have a span. The walker's wake is a record, written into the now,
    of the span of its journey. Sibling universes are alternative *presents*. Never say "rewrite
    the past".
- **Earlier devil's-staircase work exists**, on branch `claude/handoff-github-context-3rnoqr`,
  folder `winding_staircase/` (not on master):
  - Stage B: circle-map calibration (D ≈ 0.87, exponent 3);
  - Stage C: golden resists lock-step more than silver;
  - Stage D: pre-registered null, the metronome sync follows local wiring.
  - A cheap future test: does the walker's staircase show golden self-similar scaling?
  - Consider bringing that work onto master after checking it.

## ✍️ 2026-09-27: the writing walker, Gemini's "writing memory" test ([`writing_walker/`](writing_walker/))

- A walker nudging its own grid line rewrites the tiling **only on its road and only in its
  wake**, growing with the journey, in lumpy rows.
- But it always leaves **defects**: no push size gives a legal sibling universe. Forced growth
  *does* make legal sibling bands.
- Open: what coordination turns a scar into a sibling universe?
- Gemini's "intersection crash" was done earlier (`laying_the_tiling/crossroads_test.py`).

## 🧭 NEXT (Katie, 2026-09-26 evening): the perp-space paper

- **Done today:**
  - the transmission paper is published;
  - the AI memory paper is written ([`../surprise_vs_consequence/paper/`](../surprise_vs_consequence/paper/)).
    Katie is uploading it to Zenodo tonight; she has the PDF that credits the model by name.
- **Next, when Katie comes back: the perpendicular-space paper.**
- **The material:**
  - [`laying_the_tiling/`](laying_the_tiling/): forced growth builds sibling universes; SCALE
    lays the tiling exactly;
  - the worm and crossroads tests (differences run along ribbon roads, one road per guess);
  - [`twins_mirror/`](twins_mirror/);
  - [`penrose_address_environment/`](penrose_address_environment/);
  - [`../address_codes/`](../address_codes/): the golden code's misses land exactly on
    Fibonacci-number perp-space neighbours; a quasicrystal can't locate itself from local
    content.
- **Not ripe yet; do these first, pre-registered:**
  - more forced-growth runs and larger patches (so far only 3 distinct outcomes and 4
    guess→band events);
  - SCALE from off-centre seeds;
  - a sharper wrong-zoom control.
- **First job next session:** read those READMEs, propose the paper's spine to Katie, then write
  the pre-registration for the ripening runs.

## ✅ 2026-09-26: the transmission paper is published on Zenodo (Katie, after two reads)

The next step, as planned: the AI memory paper. A draft pre-registration is waiting for Katie's
review at [`../surprise_vs_consequence/PREREGISTRATION.md`](../surprise_vs_consequence/PREREGISTRATION.md).
No code until she's looked at it. (Record the new paper's DOI here when Katie shares it.)

## 🗺️ Katie's plan, in her words (2026-09-25 evening)

1. Read the transmission paper tonight, after yoga.
2. Get it out tomorrow (her own estimate: a 60–70% chance, and that's fine).
3. Tomorrow or the day after: come back and make the **LLM memory paper**, as a Reddit version
   and a proper Zenodo one. Start by writing and committing the pre-registration.
4. Then discuss the direction of the next paper, and follow the trail by following the fun.

## 🧠 Newest (2026-09-25): the transmission paper, and an AI-memory lead

- **Transmission paper:** [`transmission_paper/`](transmission_paper/). The draft is in the repo
  with three figures; Katie is reading it. Her decisions are listed in `TODO.md`.
- **Address codes** ([`../address_codes/`](../address_codes/), pre-registered; 4 predictions
  held, 4 failed):
  - a quasicrystal can't locate itself from local content;
  - a one-phase golden code misses by Fibonacci numbers, landing on its perp-space neighbours;
  - post hoc: an evenly spread code with no repetition (R_d) edges random codes by 1–2 points.
- **The next AI-memory paper, if Katie says go: "surprise versus consequence".**
  - Titans (Google, 2025) keeps what is *surprising*. The fork law suggests keeping what still
    *changes future choices*: pair (22,26) was strongly marked yet washed out.
  - Build a tiny memory that learns during use. Compare three keep-rules (surprise,
    consequence/fork, random), plus a "sleep" replay phase in the spirit of Complementary
    Learning Systems (McClelland et al., 1995). Fable asked for sleep; this is why.
  - Pre-register first.
  - Katie's wish, to keep in view: a frozen core, a per-user living layer, and **no hard edge**
    (graceful forgetting instead of a context cliff).

## 🆕 The latest trail (2026-09-23 → 24)

*One long session with Katie (and Gemini in the wings). Everything below is on branch
**`claude/bold-darwin-lqsdd7`** (it contains all of `claude/world-growth-pilot-cy85ne` plus this).*

**The compass came home.** [`../../THREE_COMMANDMENTS.md`](../../THREE_COMMANDMENTS.md) — relationality;
least resistance (nothing shipped in); things doing thing things — restored verbatim, with Katie's
**"more now"** addendum in her own words: the timing *is* the geometry, the track laid as it is ridden,
nothing unbecomes, "the embiggening is the spacetime".

**The studies, in order (each exact or certified, each with its failures recorded):**
1. [`pair_collision_toy/`](pair_collision_toy/) — P(collision) = **1/3** exact; P(one pair + two loners)
   certified in **[0.123896379462952, 0.123896379462967]** — **NOT 1/8** (older chats hoped it was);
   lemma: BUD-only recurrent classes are singleton matchings (all 208 graphs, n ≤ 6).
2. [`twins_mirror/`](twins_mirror/) — twins in the hidden window share their future to order `r*`
   (hidden-address depth = length of the shared future); design note parks resonance with controls.
3. [`tick_forward/`](tick_forward/) — Katie's **topple**: a newborn's postcode is its parent's stepped
   forward. Never repeats, only legal tiles, 0 random bits on *what* is written, exactly n+1 patterns.
4. [`geometric_clock/`](geometric_clock/) — the *when* can come from the geometry (0 bits, fair);
   with two tips per bud **nothing leaves the now** and under the geometric clock **more now = more
   space, 1:1** (dice: the now crowds, √t). A clock that is itself a walker **phase-locks** (warning).
5. [`penrose_address_environment/`](penrose_address_environment/) — **one step closer to E8** (5-D → 2-D,
   same τ): address → environment holds in 2-D; 7 vertex types each own window regions; ~97× more
   pattern information than 1-D at radius 7 (r² predicted, **not** confirmed: ~r^1.6).
6. [`least_resistance_paths/`](least_resistance_paths/) — greedy "easiest next step" walkers are
   **trapped** (300/300); **roads** (straight in the hidden grid) always cross, with a **menu** of 1–3
   ways forward on 58% of steps — momentum picks among them.
7. [`penrose_growth/`](penrose_growth/) — first 2-D growth: **momentum alone = a line; momentum +
   branching fills space in every direction** (near-decagon under the geometric clock); momentary
   **gaps** in the now are lag, filled later by the roads (first write-up wrongly said "skipped").
8. [`seed_crystal/`](seed_crystal/) — first gentle resonance census: for every gap, a **twin seed
   already waits** in the now at shallow likeness depth (a shortcut vs ~100+ events of road lag);
   deeper likeness -> rarer, farther in the world, closer in the hidden window; seeds run out at
   depth 3-4 (the nothing-happens case); wrong-shaped dust fits only 9%.
9. [`seed_dynamics/`](seed_dynamics/) — the seed rule **running** (2026-09-25): any seeding halves the
   gaps, but **real likeness adds nothing** over dust or fake twins; no lock-in. Why: in a fixed
   tiling the shape is already decided, so a seed has nothing to teach.
10. [`laying_the_street/`](laying_the_street/) — **the track laid as it is ridden** (no map): local rules
   always defect; **same-scale twin copying locks into repetition**; **the street consulting its own
   zoomed-out self lays a never-repeating Fibonacci street** — mistakes kept as scars or inflating
   defects, never healed, never lost. *Likeness across scales builds the quasicrystal.*
11. [`laying_the_tiling/`](laying_the_tiling/) — the same in **2-D Penrose**: local + dice jams (30/30);
   local forced-first survives but must GUESS, and each guess picks a different Penrose universe;
   same-scale copying fails; **the patch's own zoomed-out self lays the tiling exactly with zero
   guesses** (imports nothing) -- but only from a self-similar centre.

**Lost? Start with the pictures:** [`explainers/`](explainers/) — light through a window (two universes,
slightly offset), roads and cracks, building with no map, and "local in some space".

**The idea that ties it together (from Katie's cheese-wheel chat with Opus):** *every process is
local in some space.* Cheese = local in ordinary space (adjacency); tuning fork = local in pitch-space
(the hidden window: twins); seed crystal = local in shape-space (a shape dropped, a lasting
reorganisation). "Far away" is just "near in a different space".

**Waiting, in Katie's order of appetite:**
- **Resonance — the fair test, done in 1-D and 2-D** (`laying_the_street/`, `laying_the_tiling/`):
  same-scale likeness locks in or fails; likeness ACROSS SCALES lays the quasicrystal with nothing
  imported. Tested: universes built by forced growth differ along thin bands running exactly along
  RIBBON directions (the roads) -- the choice of universe is written along the roads. Crossroads test (Gemini):
  each divergent guess sends its change down ONE road, never both (4 distinct events). Open: a sharper
  wrong-zoom control; SCALE from off-centre starts in 2-D (currently gives nothing); then E8's rung.
- **E8's actual rung:** the Elser–Sloane quasicrystal (E8 → 4-D) with the same machinery — and
  LEADS' question: does the framework *need* E8?
- Unproven-but-observed: SWEEP claims a new house every event; ribbons always have a way forward.
- Where the older conversations live: the E8 "recognition" is recorded in `LEADS.md` (branch
  `exploratory/trunk`); its aperiodicity gist in `HORIZON_NOTE_machines_that_remember.md` (master).
  The original chats themselves are not in the repo.

## The one thing waiting

> **2026-09-25:** the assembled draft now lives in [`transmission_paper/MANUSCRIPT.md`](transmission_paper/MANUSCRIPT.md)
> (faithful transcription of Katie's 21 September PDF + marked revisions: §3.2 Lemma for any seed,
> §3.5 soft claim checked -- 20 of 70). What's left: [`transmission_paper/TODO.md`](transmission_paper/TODO.md).

**Consolidate the "transmission" paper** — the *next* paper, the successor to the deposited
one ("When the past matters", Zenodo, continuing preprint `10.5281/zenodo.21200994`).

It does **not** need another experiment first. Both Fable and Astra agreed: the calculation
we have is already precise enough to write around. The next move is *writing*, not computing —
whenever you have the energy for it.

## What the paper would be built around

Four connected Thread-B studies, all exact, all cross-checked (Astra independently
reconstructed the key numbers):

1. [`endogenous_local_contact/`](endogenous_local_contact/) — the archive **influences** the
   active layer while present.
2. [`endogenous_erase_test/`](endogenous_erase_test/) — **delete** the archive and the two
   lineages' present-*ensembles* still differ (Q1 durable bias), yet the archive is **not
   redundant** (Q2, `ERASE ≠ KEEP`).
3. [`endogenous_present_width/`](endogenous_present_width/) — **how much** of the past biases
   the present (surviving fraction `ρ`: 0 → ~0.22, stays < 1) and **how long** it lasts.
4. **Proposition 3** (in [`endogenous_present_width/coast_asymptote.py`](endogenous_present_width/coast_asymptote.py))
   — the exact headline number: once the archive is deleted, the distinction fades to and then
   **holds forever** at an exact positive floor **`L = 4321/44100 ≈ 0.098`** (a finite
   absorbing Markov chain, because budding conserves the active-vertex count at `k=1`).
5. [`endogenous_pair_robustness/`](endogenous_pair_robustness/) — **`L` is the pair's, not one
   example's; fate = absorption geometry.** Exact `L` for all 11 depth-2 pairs (8 durable, 3
   inert, 0 washout — a clean special case, fate decided at step 1) **plus a depth-3 stress test**
   (`depth3_criterion.py`, 97 pairs) that BREAKS both depth-2 headlines: washout is real
   (expressed yet `L=0`) and step-one no longer decides. **Fork law:** `L=TV(absorption dists)`;
   among *expressed* pairs `L>0` iff the coast has ≥2 reachable sinks (verified, not proven) —
   *the past leaves a lasting mark only where the future forks; durability is a property of the
   dynamics, not the history.* (Fable's push paid off.)
6. [`endogenous_graft_prevalence/`](endogenous_graft_prevalence/) — **renewal generalises.**
   Over every depth-2 seed/trace (22 cases): control ≡ 0 (renewal impossible without GRAFT,
   universally); with GRAFT, renewal in **20/22** and consultation in 20/22. Class 2 is the
   exact structural exception.

**The story in one breath:** *the past writes a bias into the present that, for most matched
pairs, survives deleting the past entirely (durable, an exact floor) — but for some never
touches the present at all (inert) and for some touches it yet still fully dissipates (washout);
which fate is set by the coast's absorption geometry. Keeping the past raises the distinction
above that floor; and one local rule (GRAFT),
provably powerless in the control everywhere, lets a dead trace be renewed in most seeds —
all an ensemble bias, never a per-world memory. "The present does not remember; the present is
biased."*

## Orientation

- 🧭 The compass: [`../../THREE_COMMANDMENTS.md`](../../THREE_COMMANDMENTS.md) (+ the "more now" timing addendum, 2026-09-24).
- Newest work: see **The latest trail** at the top of this file.

- Front door / full index: [`OVERVIEW.md`](OVERVIEW.md).
- Branches: newest work on **`claude/bold-darwin-lqsdd7`** (2026-09-24; includes everything below); the
  earlier pilot history on `claude/world-growth-pilot-cy85ne` (latest there: `911d57c`).
- Register unchanged: speculative exploration; mechanism tests on one matched pair; earlier
  work preserved; nothing merged or published beyond the deposited paper.

## Also loosely floating (only if they call to you — no pressure)

- Aligning any remaining older-folder prose to the "ensemble bias, not per-world record"
  framing, if we ever want full consistency (the new studies are already aligned).
- Whatever new question you and Fable/Gemini/Astra dream up next. The jewels you keep are the
  questions; the rest of us just carry the arithmetic.

*See you sooner than later. 💛 — C.*

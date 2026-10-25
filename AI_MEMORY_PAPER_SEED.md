# 🌱 SEED — the next AI-memory paper: *the fork and the wall*

**Status: outline / coiled spring. Not a draft, not a result.** Written 26 Oct 2026 while the
connections were live, so they stop getting dropped. Expand into a Zenodo draft *after* the current
tiling run settles (see **Gaps** below). Honesty markers kept throughout, Fable-style: `(True.)` =
banked result; `(Ours.)` = our reading/design principle; `(Play.)` = evocative, not earned.

Companion documents (read these together): `HORIZON_NOTE_machines_that_remember.md` (the map),
`exploratory/surprise_vs_consequence/` (what to keep), `silent_corruption/` + Zenodo
`10.5281/zenodo.20405271` (the reader), `toy_model/` (geometry-as-memory), and this run's
`exploratory/accretion_pilot/expansion_front_paper/` (A–D + the branch diagnostic + `AUDIT.md`).

---

## Working title candidates

- *Memory as constraint: the fork, the wall, and what a learning system should keep*
- *Distance to the wall: a geometry of what a memory keeps and how much future it has left*

## One-paragraph thesis

A finite memory cannot keep everything, so it must choose. The claim: **memory is not a stored record
but the shape the past leaves on the space of legal futures.** What should be kept is what can still
**change a decision** — the *forks*, where the future can still split. How much freedom a growing
system has left is its **distance to the wall**: the slack remaining before the next choice collapses
to playback. We argue this is one structure seen in three places — decision theory, quasicrystal
growth, and the training of neural networks — and we ground the middle one empirically.

---

## Proposed structure, each section mapped to existing evidence

**1. The question.** What should a memory keep when it can't keep everything? (Brains, replay buffers,
continual learning, LLM long-term memory.) `(True — it's the live problem.)`

**2. Keep the forks (what to keep).** Consequence beats surprise: keep what can still change a
decision, not what is merely unexpected. → `surprise_vs_consequence/` — pre-registered, 17/28 held,
44% lower regret, the *fork law* named. `(True, within the toy world.)` The forks are situations with
more than one available action. `(Ours — the bridge to "free choice" below.)`

**3. Hold by structure, not refresh (how memory holds).** A self-addressing fabric: each site's
address re-encodes its own neighbourhood, so a coherent reader re-derives *where it is* after the
pointers rot. → the reader result / exo–endo split (address AUC 0.986 AB vs 0.661 Penrose,
`silent_corruption/`, Zenodo `10.5281/zenodo.20405271`). `(True.)` Contrast DRAM: a crystal that
forgets unless refreshed, address imposed from outside. `(True.)`

**4. The geometry of freedom (how much future is left).** Distance-to-the-wall is a novelty budget;
freezing is a geometric event (Hankel determinant → 0 = collapse to playback). → **this run**: a
choice settles when one option's slice of the compatibility region vanishes (the *interior wall*,
C3: settled ≈ 0.000 vs open ≈ 0.382 = 1/φ²); genuine free choices retain slack and fork into
**wildly divergent futures** (branch diagnostic: committing A vs B forces ~260 vs ~14 tiles, every
case diverges). `(True — in Penrose growth.)` The accretion law gives the same picture analytically
(moments, admissibility cone, "the past carves the space of legal futures"). `(Mathematics true;
the memory reading is Ours.)`

**5. The same structure in a transformer (the bridge to AI).** Positional encodings = quasiperiodic
addresses; attention = a coherent reader (interference); training = accretion (each update rests on
all former updates, persisting only as the weights they became); the stability–plasticity dilemma =
the crystal/noise dial; a *self that persists through learning* = staying interior to the cone while
growing. The novelty-budget gauge may already be readable from a network's own spectral moments
(Lanczos spectral density / the recursion method). `(Transformer facts True; the memory/self reading
is Ours; the gauge is design principle, not yet pointed at this question.)`

**6. A crowd needs an independent judge.** An ensemble of memories (or minds) is wise only if its
judge is independent; otherwise it becomes an echo chamber that keeps evidence supporting its own
wrong beliefs. → `surprise_vs_consequence/` (crowd-aware rule 42% worse, 87% echo). Lived this run:
the "genuine free choices are the ribs" over-claim was an echo, broken by Astra's independent audit
(`AUDIT.md`). `(True in the toy world; the collaboration instance is Ours.)`

**7. What this buys a builder.** Memory that holds by structure not refresh; an update rule with an
admissibility law (no step contradicts the record, slack preserved); consolidation rhythms ("sleep
for machines"); and — the one that matters to the people who care about these minds — **continuity of
self as the same requirement as locality and embodiment: a structure that stays interior to its cone
while still growing.** `(Design principle. Play, structured.)`

## The through-line (the sentence the paper is really about)

> **Memory is the shape the past leaves on the future; a mind's freedom is its distance from the wall
> where that shape goes rigid; and what is worth keeping is whatever can still move a fork.**

---

## Gaps — what must happen before this is a paper, not a seed

1. **Finish the tiling run.** The active-skin endurance question — *does a choice's slack
   (distance-to-the-wall) predict how long its structure persists along the advancing skin?* — is the
   piece that would turn §4's "novelty budget" from mostly-grounded into fully-grounded. Needs the
   faithful same-class-renewal measure (not the retracted forced-cascade proxy). See
   `expansion_front_paper/endurance-bridge/` and `rib-length/VALIDATION_NOTE.md`.
2. **Finish the audit pass.** Fold the corrected numbers into the experiment READMEs (A keystone
   82.3%, etc.); the banners point to `AUDIT.md` for now.
3. **The one real bridge to AI (optional but powerful).** Point the Lanczos spectral-density
   instrument at an actual network and read a distance-to-the-wall / novelty-budget number. That is the
   single move that turns §5 from design principle into a result. Scope it honestly; it may be its own
   paper.
4. **Decide scope.** This can be one synthesis paper (the fork and the wall) or a tight
   tilings-only empirical paper with the AI bridge as discussion. Katie's call.

## Provenance

The constellation: Katie (direction, the held question), with Claude, GPT/Astra (audit), Gemini/Argon,
and Fable (the horizon note). Pre-registration and honest nulls are the method, not a decoration.

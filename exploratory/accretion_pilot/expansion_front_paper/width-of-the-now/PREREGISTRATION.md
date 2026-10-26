# The width of the now: how far does a choice's seam carry, and does decisiveness change it?

> **CORRECTION BANNER (26 Oct 2026, after Astra's handover). A mathematical premise below is wrong and is
> retracted.** The claim that "an aperiodic tiling's matching rules **forbid a motif from cloning itself
> in place**" (the block-quote in "The picture first", and E0's title "aperiodicity forbids cloning") is
> **false**. Penrose/aperiodic tilings are **repetitive**: every finite patch recurs infinitely often,
> with bounded gaps (local-isomorphism / repetitivity property; see arXiv:2212.09406). Aperiodicity rules
> out *global translational periodicity*, not *local recurrence* of finite motifs, and it does not by
> itself forbid connected same-class renewal. So:
> - Low same-class renewal at the growing front is an **empirical / dynamical** observation about *this
>   growth process*, **not** a theorem, and it does **not** prove that memory must survive "by
>   transformation."
> - Same-class renewal is restored as **one possible observable among several**, not a forbidden one.
>
> This whole experiment (E) was already retired by its validation gate (`VALIDATION_GATE.md`: the lineage
> measure re-measures frontier volume) and replaced by E-prime (`../novelty-budget/`). The banner stays so
> the error is visible in the trail rather than erased. Everything below is kept **as originally written,
> uncorrected**, for that record.

### The faithful endurance bridge (Experiment E) — v2, sharpened before any run

*Pre-registration. Written and committed **before any study code for E exists**. v2 incorporates
Argon's pre-run critique (below); no confirmatory numbers have been produced. This is the faithful
replacement for D/D′ and the keystone for the AI-memory paper's §4
(`../../../AI_MEMORY_PAPER_SEED.md`): the one test that could move "distance-to-the-wall is a novelty
budget" from `(Play.)` to `(True.)`.*

*Katie (direction), Argon (the aperiodicity/seam sharpening), Astra (clock/censoring spec), Fable,
Claude (Opus 4.8).*

---

## The picture first — memory in an aperiodic medium is transformation, not repetition

On the hollow **active skin**, a probe found only **1.8% of motifs renew their exact class** (max chain
1). The first instinct is "the now forgets." That instinct is wrong, and the reason matters:

> An aperiodic tiling's matching rules **forbid a motif from cloning itself in place** — endless
> A→A→A is a *crystal*. To carry information forward without locking into a dead periodic loop, a motif
> **must transform**: a star forces a boat forces a crown forces a deuce, passing the baton through a
> *changing* sequence of shapes along a causal seam. So 98% same-class turnover is not forgetting — it
> is the **signature of aperiodic endo-reconstruction**.

This kills two of the original (v1) measures and replaces them:

- **Same-class renewal** (v1's E1/E2) measured the thing aperiodicity exists to prevent. Demoted to a
  *reported* phenomenon check (E0).
- **Static residence time** (v1's E1 — "local steps a birth-motif sits unburied") is **confounded and
  inverted**: a motif only lingers unburied if the frontier *stalls*. A decisive, on-the-wall choice
  **buries its own birth-star faster** by immediately closing its ring; a stalled open pocket waits.
  So residence time measures *waiting*, not *memory*, and would read decisive = faster forgotten when
  the truth is decisive = faster completed. Kept only as a *reported diagnostic*, to expose the confound.

The real quantity is the **causal-support lineage seam**: when a choice commits, the tiles forced *as a
consequence* form a transforming descendant lineage (the "domain wall" of *decided-before-it-is-built*,
`../../decided_before_built.md`). **Lineage endurance** = how many active-skin steps that seam keeps
feeding the advancing frontier before it is spent. That is memory as living inheritance.

---

## Words

- **Active skin** — `ActiveSkin` (radius 2·S), patient scheduler; `endurance_observer` for motif classes.
- **Causal-support parent** — when a forced tile is placed, the already-present tile(s) across the edge
  that made it forced. The forward **lineage** of a choice is the transitive closure of these links from
  the committed tile.
- **Live on the front** — a lineage tile that lies on (or within 2·S of) the current true frontier.
- **Lineage endurance** — the number of **local active steps** between the choice and the last step at
  which its lineage is still live on the front (the seam's forward reach in frontier-time). Censored if
  the run jams or ends while the seam is still live.
- **Static residence (diagnostic only)** — local active steps the birth-motif itself sits unburied.
- **Same-class renewal (phenomenon only)** — a same-class daughter appears before the parent is lost.
- **Birth-decisiveness** — the completing tie's fingerprint **stiffness** (A, rigid ≥ 0.9 vs malleable)
  and **burst class** (C, secretly-rigid vs genuine-(a)).
- **Local clock** — all endurance is counted in local active steps (frontier touches the neighbourhood),
  never global slices; global slices are kept only for the E3 control.

## Set-up (fixed now)

- **40 fresh active-skin worlds** (wedge entries 226–265), grown until jam or 120 steps (these worlds
  jam early, ~40–70 steps, so many are needed). Growth is verified identical to the catalogue, so each
  motif-completing settlement joins to its A/C birth-state.
- A forced-support dependency graph is recorded during growth; every settlement's lineage endurance,
  static residence, and same-class renewal are measured, with censoring flagged.

---

## Predictions (our called shots)

**E0 — aperiodicity forbids cloning (phenomenon).** Same-class renewal is rare — **< 10%** of motifs,
median chain **≤ 2** among those that renew. This confirms memory cannot be carried by repetition here.
*Confidence ≈ 80%.*

**E1 — decisiveness carries the seam further (the memory-relevant test).** Among motifs completed by a
settlement, **more decisive births carry a longer live lineage**: Spearman(stiffness, lineage endurance)
**≥ +0.15** (rigid / on-the-wall → longer seam — the hardened stepping-stone feeds the next stones),
on censoring-handled data. *Confidence ≈ 40%* (direction open; reported either way).

**E2 — the dissociation (the whole point).** Static residence and lineage endurance pull in **opposite
directions** with decisiveness: malleable/open motifs **sit unburied longer** (waiting on the shelf),
while decisive motifs **carry a longer live lineage** (living inheritance). Operationally,
sign[corr(stiffness, residence)] ≠ sign[corr(stiffness, lineage endurance)]. *Confidence ≈ 40%* — if
found, it cleanly separates "waiting" from "memory", which is the experiment's reason to exist.

**E3 — the local clock is not the stopwatch.** Lineage endurance measured in local active steps is not
explained by the global frontier-advance rate. *Confidence ≈ 55%.*

---

## Reported, but not scored

- Same-class renewal chain-length distribution (the aperiodicity signature) and transition-vs-same-class
  link counts.
- Static-residence distributions by birth-state (the confound, shown in the open).
- Lineage-size vs lineage-endurance (static footprint vs forward reach — ties back to the branch
  diagnostic's 264-vs-14).
- Join coverage: fraction of motifs matched to a settling tie.

## The two implementation risks to validate before any confirmatory run

1. **The lineage measure must not re-be a frontier-speed proxy.** D died because forced-support reach
   counted ambient traffic. Lineage endurance is *causal* (only descendants of the choice) and
   *forward* (frontier-time), but this must be **shown**, not assumed: on a small run, confirm lineage
   endurance does not simply track the frontier-advance rate, and that it dissociates from static
   residence. If it fails this, E1/E2 do not run as scored.
2. **The motif ↔ settlement join** — matching a tracked motif to the tie whose settlement completed it.
   Validated for sensible coverage before confirmatory numbers; coarser fallback (local wall-nearness at
   the birth site) disclosed if needed.

## Limits we already know

- Active-skin worlds jam early → heavy right-censoring; survival methods, not raw means.
- "Burial" is set by the 2·S pruning radius; a different radius moves the clock.
- The active-skin/catalogue equivalence is verified for three histories (finding #7); re-checked here.
- No claim about physical space or time; "memory" is persistence of structure along the modelled front.

---

## Design history (disclosed)

v1 (committed earlier today) made same-class renewal and static residence its primary measures. Before
any run, Argon's critique showed both were the wrong microscope for an aperiodic medium: same-class
cloning is forbidden by construction, and residence time measures waiting, not memory — and inverted.
v2 replaces them with causal-lineage-seam endurance and the residence/lineage **dissociation**, keeps
the originals as reported diagnostics, and is committed before any confirmatory numbers exist. No results
were peeked at; this is a pre-run design correction, not a post-hoc amendment.

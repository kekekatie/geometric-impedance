# The width of the now: does a choice's decisiveness change how long its structure is remembered?

### The faithful endurance bridge (Experiment E)

*Pre-registration. Written and committed **before any study code for E exists**. The numbers below are
our called shots. This is the faithful replacement for D/D′: it measures persistence **directly** on the
advancing active skin, with no forced-cascade proxy.*

*Katie (direction), with Astra (the renewal/clock/censoring spec), Argon, Fable, Claude (Opus 4.8).
This is the keystone experiment for the AI-memory paper's §4 (`../../../AI_MEMORY_PAPER_SEED.md`): it is
the one test that would move "distance-to-the-wall is a novelty budget" from `(Play.)` to `(True.)`.*

---

## The picture first

On the hollow **active skin** (a true frontier with everything more than 2·S behind it pruned away),
motifs — completed vertex stars — are born on the advancing rim and then **mostly turn over**: a
different motif replaces them. Only rarely does a motif's *kind* **renew** — a same-class daughter
appears nearby before the original is buried. A fresh-world probe (Astra's observer) found only **50 of
2,851 motifs renewed, longest chain 1 link**. The advancing now, it seems, mostly *forgets*.

So this study asks: **when a choice settles and completes a motif, does the *decisiveness* of that
choice change how long the motif persists — and whether its kind is remembered — along the now?**

The active-skin growth is **verified identical** to the catalogue growth (Astra's finding #7: same
scheduler, same ties, same placements), so each motif-completing settlement can be joined to its
birth-state from A (fingerprint stiffness) and C (genuine-vs-secretly-rigid).

## Why the clock must be local

"How many global slices a motif lasts" is a stopwatch artifact — it only reflects how fast the front
sweeps past. So the lifetime clock is **local active steps**: steps where the frontier actually touches
the motif's neighbourhood. Motifs alive at the first or last observed slice are **censored** (their true
lifetime is unknown) and handled explicitly, not scored as if complete.

---

## Words

- **Active skin** — `ActiveSkin` (radius 2·S) grown with the patient scheduler; `endurance_observer`
  tracks motifs across frames (`discover`, reflection-folded `canonical` classes, born/renewed/lost).
- **Motif** — a completed vertex star or small pocket on the skin, with a canonical class.
- **Renewal** — a same-class daughter motif appears (a same-class link, Astra's machinery) before the
  parent is lost. **Chain length** — the longest same-class renewal chain a motif anchors.
- **Burial** — the motif's tiles are pruned from the skin (the frontier advanced > 2·S past it).
- **Local-active-step lifetime** — the number of steps, between birth and burial, in which the frontier
  touched the motif's neighbourhood (its own clock, not global slices).
- **Censored** — left-censored (present at the first observed frame) or right-censored (still present at
  the run's end / jam); true lifetime unknown.
- **Birth-decisiveness** — for a motif completed by a settlement, the completing tie's fingerprint
  **stiffness** (A, rigid ≥ 0.9 vs malleable) and **burst class** (C, secretly-rigid vs genuine-(a)).

## Set-up (fixed now)

- **40 fresh active-skin worlds** (wedge entries 226–265), grown until jam or 120 steps. Active-skin
  worlds jam early (~40–70 steps), so many are needed for enough uncensored motifs.
- Every motif is tracked (lifetime, renewal, censoring). Motifs whose completing tile settles a two-way
  tie are joined to that tie's birth-decisiveness.
- All clocks are **local active steps**; global slices are recorded only for the E3 control.

---

## Predictions (our called shots)

**E0 — the now mostly forgets (the phenomenon).**
Same-class renewal is rare and short: **fewer than 10%** of motifs renew at all, and the median renewal
chain among those that do is **≤ 2 links**. *Confidence ≈ 80%* (the probe and Astra's #9 both point
here; this establishes weak, short structural memory as the baseline).

**E1 — decisiveness modulates persistence (the memory-relevant test).**
Among motifs completed by a settlement, birth-decisiveness predicts local-active-step lifetime. Lead
guess, aligned with the memory thesis ("keep the forks — what can still change a decision"):
**malleable-born motifs persist longer** than rigid-born ones — Spearman(stiffness, lifetime) **≤ −0.15**
(lower stiffness → longer life), on censoring-handled data. *Confidence ≈ 40%* (genuinely open —
direction may invert or vanish; we commit to reporting it either way, with the censoring explicit).

**E2 — and they are remembered more, not just longer.**
Malleable-born motifs renew (anchor a same-class chain ≥ 1) at a **higher rate** than rigid-born ones.
*Confidence ≈ 35%* (renewal is sparse, so this may be underpowered; reported with its n).

**E3 — the local clock is not the stopwatch.**
The birth-decisiveness effect (if any in E1) is present with the **local-active-step** clock and is not
explained by the global frontier-advance rate. *Confidence ≈ 55%.*

---

## Reported, but not scored

- **Survival curves** of local-active-step lifetime by birth-decisiveness, with censoring marked.
- **Renewal chain-length distribution** overall and by birth-state.
- **Transition vs same-class** link counts (how much the skin turns over vs renews).
- The join coverage: what fraction of motifs could be matched to a settling tie.

## The implementation risk we will validate before the confirmatory run

The **motif ↔ settlement join** — matching a tracked motif to the two-way tie whose settlement completed
it — is the one piece not yet built. It will be validated on a small run (does it match a sensible
fraction of motifs; do the matched birth-states look right) **before** any confirmatory numbers are
produced. If the join proves unreliable, E1/E2 fall back to a coarser birth-context (the local
wall-nearness field at the motif's birth site) and that substitution will be disclosed.

## Limits we already know

- **Renewal is sparse** (≈ 2% in the probe), so E1/E2 may be underpowered — in which case the honest
  finding is that structural memory along the now is weak regardless of birth-state (itself a result for
  the memory paper).
- Active-skin worlds **jam early**, so lifetimes are short and **heavily right-censored**; survival
  methods, not raw means, are used.
- Pruning radius 2·S defines "burial"; a different radius would move the clock.
- The active-skin/catalogue growth equivalence is verified for three histories (finding #7), not
  independently for these 40 worlds — a re-check is part of validation.
- No claim about physical space or time; "memory" here is persistence of structure along the modelled
  frontier.

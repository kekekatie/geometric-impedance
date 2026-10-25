# The novelty budget or the coiled spring: does a free choice's decisiveness set the size of its causal seam?

### Experiment E-prime (the clean successor to E)

*Pre-registration. Written and committed **before any confirmatory code/run for E-prime**, after (a) E's
active-skin lineage measure failed its validation gate (`../width-of-the-now/VALIDATION_GATE.md`) and
(b) an X-axis probe fixed the predictor (below). The numbers are our called shots.*

*Katie (direction), Argon (the two confound catches and the two-sided mechanistic framing), Astra, Fable,
Claude (Opus 4.8). Keystone for the AI-memory paper §4 (`../../../AI_MEMORY_PAPER_SEED.md`): tests
"distance-to-the-wall is a novelty budget" directly, with a causal measure already shown to be clean.*

---

## The picture first

A genuine free choice — a two-way tie the bounded forced wave leaves open — is a fork. Its **pure causal
seam** is the counterfactual: grow forced-only under option A vs option B from the same locally-saturated
patch and keep only the tiles that **differ** (the branch diagnostic's blue/orange; grey common growth
cancels). The seam size is the **symmetric difference** |A △ B|, and its **reach** is how far from the
fork those differing tiles extend.

The question: does the fork's **decisiveness at birth** set the size/reach of that seam — and in which
direction? Two competing mechanisms, pre-registered as a **two-sided** test:

- **Novelty Budget (+):** a *freer* fork (low stiffness, more slack) has more legal futures, so committing
  one option unleashes a *larger, farther* divergence.
- **Coiled Spring / Shock Absorber (−):** a *freer* fork sits in a roomy pocket that *absorbs* the choice
  locally (short seam), while a *tightly-pinched* fork (high stiffness) is a hair-trigger whose commitment
  unleashes the *largest* avalanche.

We do **not** pre-commit the sign; we pre-commit to measuring which mechanism wins.

## What the X-axis probe fixed (disclosed)

On 30 genuine free choices: **F_area has no per-choice variance** (CV 0.00; it is the one global offset's
compatibility region, a near-world-constant) and is **−0.95 age-confounded** — so "slack = F_area" is
dropped entirely. **Wall-nearness** has modest variance (CV 0.23) but is **−0.68 age-confounded** — used
only as a secondary predictor with an explicit age control. **Fingerprint stiffness** (A) has the best
spread (CV 0.59), full coverage, and is **age-independent** — the clean primary predictor. The probe did
**not** touch branch divergence; the tested relationship is unpeeked.

---

## Words

- **Genuine free choice** — a two-way tie left open by the bounded forced screen (radius 5·S, cap 12),
  as in `branch-diagnostic/`.
- **Causal seam** — commit option A, forced-grow to local saturation (radius 7·S, cap 50); same for B;
  the differing tiles. **Seam size** = |A △ B| = |A-only| + |B-only|. **Seam reach** = max distance from
  the fork vertex to a differing tile (in S).
- **Birth-decisiveness (primary)** — the fork's A **fingerprint stiffness** (0 = always malleable/free →
  1 = always rigid). **Secondary** — **wall-nearness** min(pA,pB)/F_area, with patch size controlled.
- **Patch age** — the patch size (tile count) at the fork's birth; the confound both predictor and seam
  must be checked against.

## Set-up (fixed now)

- **Fresh worlds, wedge entries 240–279** (none used by A/B/C or the branch diagnostic), grown until the
  target count of genuine free choices is reached. Target: **≥ 60** genuine free choices with a stiffness
  value and a non-degenerate seam.
- Per fork: seam size, seam reach, stiffness, wall-nearness, patch age.

---

## Predictions (our called shots)

**E1 — decisiveness sets the seam size (two-sided).** Stiffness predicts |A △ B| with
**|Spearman| ≥ 0.2**, and the effect **survives controlling for patch age** (partial Spearman, same sign,
|ρ| ≥ 0.15). The **sign is reported, not pre-committed**: negative ⇒ **Novelty Budget** (free forks
diverge more), positive ⇒ **Coiled Spring** (pinched forks diverge more). *Confidence ≈ 55% that a
≥ 0.2 relationship exists; direction genuinely open.*

**E2 — and the seam's reach (two-sided).** The same relationship holds for seam reach (max radius), same
sign as E1, |Spearman| ≥ 0.2, age-controlled. *Confidence ≈ 45%.*

**E3 — it is not patch age.** The stiffness→seam relationship is not an age artifact: stiffness is
age-independent (probe), and the partial correlation controlling for patch size retains the effect
(E1). Reported: corr(patch age, seam size) to show the confound's raw size. *Confidence ≈ 65%.*

---

## Reported, but not scored

- Wall-nearness → seam (secondary predictor), with and without the age control, for comparison to
  stiffness.
- Seam-size and seam-reach distributions; the asymmetry |A-only| vs |B-only| per fork (the branch
  diagnostic found striking asymmetry ~260 vs ~14).
- Whether seam size and seam reach agree (local-but-dense vs far-reaching seams).

## Limits we already know

- Genuine-free selection is by the bounded screen (radius 5·S), so "free" means unresolved by that
  screen; stiffness (A) is the independent decisiveness label.
- Seam is measured to local saturation at radius 7·S / cap 50; a far-reaching seam could be truncated
  (reported via the reach distribution and the cap-hit rate).
- Repeated forks within a world are not independent; clustered uncertainty, not raw pooled p-values.
- No claim about physical space or time; the "seam" is the counterfactual forced difference between two
  committed options.

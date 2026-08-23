# Result: the degree-controlled static address channel

Outcome of the sealed test `PREREG_degree_controlled_address.md` (primary + secondary v2).
Scored first, interpreted second.

## Verdict

**Silver-first is overturned as a degree artefact. Golden carries the richest
degree-independent address information. But the primary and secondary metrics do NOT
agree on a family fragility *ordering*, so none is claimed** — the two measure different
constructs (information incremental to degree vs local encodability), and their
divergence is itself the finding. What both agree on: **silver's address is the least
distinctive beyond degree.**

## Primary — degree-controlled increment (8 seeds)

S = AUC(degree ⊕ address) − AUC(degree). Zero-damage:

| | AUC_deg | AUC_addr | raw S | S_null | S − S_null |
|---|---|---|---|---|---|
| silver | 0.994 | 0.971 | −0.005 | −0.002 | −0.003 |
| golden | 0.898 | 0.954 | **+0.093** | −0.054 | **+0.147** |
| platinum | 0.911 | 0.677 | +0.022 | −0.029 | +0.051 |

Under damage the honest channel (S − S_null) decays: golden 0.147 → ~0 by ~29% damage;
platinum 0.051 → ~0; silver flat at ~0 throughout.

**Golden ≫ platinum > silver in degree-independent address information, and this holds
with OR without the S_null subtraction** (raw S already gives golden 0.093 ≫ platinum
0.022 > silver −0.005). The old silver-first ordering does not reproduce: silver's
address adds essentially nothing beyond degree (AUC_deg 0.99 on its own).

### GPT's five questions on the S_null ≈ −0.05 baseline

1. *Why do stratified-null features hurt performance?* Adding scrambled features to
   gradient boosting causes mild overfitting/model-selection penalty; held-out AUC drops
   a few points. Expected behaviour, not an anomaly.
2. *Expected regularisation behaviour?* Yes.
3. *Stable across family/damage/seed?* Only roughly: S_null runs about −0.02 to −0.08,
   more negative for golden/platinum and at higher damage. Not a clean constant — a
   caveat on treating it as a fixed offset.
4. *Is subtracting it pre-registered?* No — the pre-reg expected S_null ≈ 0. Subtraction
   is post-hoc calibration.
5. *Do conclusions hold on raw S vs the null?* **Yes.** Golden ≫ others on raw S with no
   subtraction. The headline does not depend on the subtraction; the subtraction only
   rescales magnitudes.

## Secondary v2 — held-out-offset vertex-type reconstruction

Repaired instrument (Amendment 1), run on fresh offsets. Target: current-state offset-free
address `a·perp4`; predictor: vertex type; validation: held-out-offset.

- **Leakage guard passed.** Held-out-offset R² ≈ random-split R² (silver .869/.906,
  golden .847/.883, platinum .844/.877): the reconstruction transfers to unseen offsets,
  so it is genuine structural encoding, not spatial-autocorrelation memorisation.
- **Clean reconstructibility is near-equal** across families (~0.85, silver a hair top) —
  NOT golden-led. Reconstructibility ≠ uniqueness, in the data.
- **Decomposition:** degree reconstructs *no* family's address (R²_deg ≈ −0.08 for all);
  vertex type carries essentially all of it (~0.85), uniformly. GPT's specific
  "silver redundant-with-degree" mechanism is not the story — degree is useless for
  reconstruction in every family; the address is a fine-grained local-configuration
  property throughout.
- **Decay under damage (clean → amp 0.25):** silver −0.07, golden −0.09, platinum −0.13.
  Ordering platinum > golden > silver — **but vs nominal amplitude, not measured damage**,
  and platinum's more-fragmented window takes more damage per amp, so this ordering is
  confounded and is **not claimed**.

## Decision rule (amended) — applied

Agreement required the family with the largest unique channel (golden) to show a
correspondingly measurable loss of reconstructible address. Golden *does* lose
reconstructibility (−0.09 > silver −0.07), so the weak form holds; but the *ordering*
does not match (platinum decays most, on a confounded axis). Per the rule, **partial
agreement → no ordering claim; the metric-dependence is reported instead.**

## What is solid vs what is not

**Solid (survives both metrics / all checks):**
- Silver's address is the least distinctive beyond degree — its apparent robustness was
  degree redundancy under the predictive metric.
- The address is strongly, structurally encoded in the local vertex type (~0.85, transfers
  across offsets, robust under damage) — a clean cut-and-project structural result.
- Golden carries the richest degree-independent address information (primary), robust to
  the S_null question.

**Not established:**
- A family fragility *hierarchy*. Primary (golden-richest) and secondary (near-equal
  clean; confounded decay) do not agree on one.

## Scoring the pre-registration

- **P1** degree confound large & real — **confirmed** (AUC_deg 0.90–0.99).
- **P2** class no channel beyond degree — **confirmed** (increment ~+0.007).
- **P3** silver-first does not reproduce degree-controlled — **confirmed**.
- **P4** golden largest clean honest channel — **confirmed** (primary).
- **P5** primary & secondary agree on ordering — **NOT met** (partial only) → no ordering
  claimed. H_survive rejected; H_confound + H_reorder supported on the primary but not
  cross-confirmed as a hierarchy.

## Consequence for the confirmed dose-response

Per pre-reg §9: the confirmed "Penrose degrades faster than Ammann–Beenker" result must
be re-read through the degree-controlled lens. The corrected reading is not "silver
preserves address best" but **"golden carries more degree-independent address, and silver's
address is largely redundant with degree"** — quantity/uniqueness, not simple robustness.

## The distinctions this programme has earned

reconstructibility ≠ uniqueness · persistence ≠ information richness · possibility ≠
preference. The static side is where quasiperiodic structure shows up (per the dynamics
border-wall), and here it shows up as *golden carrying the richest degree-independent
address information* — a real correction to the static headline, held to honest footing.

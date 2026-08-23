# Draft pre-registration: the degree-controlled address channel

**Status — SEALED on the crew's pivot (Karen, Gemini; Claude). Confirmatory run not yet
made.** Sealed by this commit; nothing above the dated-amendment line changes. Note: this
doc predates the intrinsic-drift detour and had a lighter review than the sibling pre-reg —
GPT has not line-reviewed it, so any refinement he raises goes in a dated amendment below,
not by editing the sealed body. The 2-seed table in §1 is exploratory and motivating only;
the ≥8-seed confirmatory run is what §2 pre-registers.

This supersedes the feature-set decision in `PREDICTION_rank4_headline.md`. It does
not touch the substrates (rebuilt on the singular convention, `RANK4_FAMILY.md`),
the flip machinery, or the confirmed dose-response result. One thing changes: how
the address channel is *measured*.

---

## 1. Why this exists — the degree confound

The headline protocol uses perpendicular-space coordinates as **features** to predict
a **privileged-site label**, and scores the address by how well it predicts that label
(AUC). But the label is `matched_rate_labels`, the top 5% of active vertices by
**retention**, and retention is built from **degree**. So degree alone predicts the
label, and the "address AUC" is confounded by degree from the start.

This is the exact mechanism that voided Golden in `RANK4_HEADLINE.md`:

> congruence class  →  vertex degree  →  retention  →  privileged-site label

The class scored 0.83 not because it carried the address, but because it proxied degree,
which built the label. `matched_labels.py`'s docstring claims address features "share no
term" with the label — true at the level of *terms*, but degree is a shared *cause*, and
that is enough.

### Exploratory probe (motivating, not confirmatory)

Two seeds, zero damage, on the rebuilt substrates. Metric: nested AUC increments, each
model adding to the one on its left. `deg` = scalar vertex degree; `perp` = the two
Galois coordinates + radius; `class` = the congruence label.

| | degree | +perp | perp's gain over degree | +class | class's gain over degree+perp |
|---|---|---|---|---|---|
| Silver | 0.993 | 0.984 | **−0.009** | — | — |
| Golden | 0.898 | 0.992 | **+0.094** | 0.998 | **+0.006** |
| Platinum | 0.913 | 0.930 | **+0.017** | 0.942 | **+0.012** |

Two things this suggests, both to be tested, neither yet claimed:

1. **The discrete class is a degree backdoor, not a second address.** Golden's 0.83
   collapses to a +0.006 unique contribution once degree and the continuous address are
   held. This answers `PREDICTION_rank4_headline` subsidiary prediction 2: the class is
   not inert on raw AUC, but its non-inertness is degree leakage.
2. **The whole measurement is degree-saturated.** Silver's privileged sites are
   predicted at 0.993 by degree alone; its address adds nothing *unique* (though it is
   informative in absolute terms, 0.966 — it is redundant *with* degree, not empty).
   The address's **unique, degree-controlled** contribution reorders to
   **Golden ≫ Platinum > Silver** — the reverse of the headline's silver-first story.

AUC increments near the ceiling are compressed and noisy, and two seeds is a probe, not
a result. Hence this pre-registration.

---

## 2. The reformulated measurement

**Primary metric — degree-controlled increment.** At each measured-damage level, per
member:

    S_N(d)  =  AUC(degree ⊕ address)  −  AUC(degree)

computed with the same model and CV as the headline, over **≥ 8 seeds**, with mean and
CI. `address` = the two Galois coordinates and their radius, recomputed on the *damaged*
tiling; `degree` recomputed on the damaged tiling too. Absolute AUCs are reported
alongside, so a ceiling-compressed S_N ≈ 0 (redundant address) is never confused with a
genuinely empty channel.

**Fragility** is the decay of S_N(d) with measured damage — reported both as absolute
S_N(d) and as S_N(d)/S_N(0), since a channel that starts near zero cannot meaningfully
"decay."

**Stratified null.** Permute the address rows **within degree deciles**, so the null
preserves the degree–address relationship and breaks only within-stratum address signal.
S_N under this null must be ≈ 0. This is the guard that the increment is genuine
address information and not residual degree.

**Secondary metric — direct address reconstruction (different confound profile).**
Predict each vertex's *true* perpendicular coordinates from tiling-local features
(degree, neighbour-degree multiset, small graph ball), measure reconstruction error
(R² / median error), and watch it degrade under damage. This conditions on nothing
downstream of the address, so it does not have the mediator problem of the primary; if
the two metrics give the same fragility ordering, the ordering is trustworthy.

**Decision rule fixed in advance.** A fragility ordering is *claimed* only if the primary
(degree-controlled increment) and the secondary (direct reconstruction) **agree** on it.
Disagreement is reported as "measurement not yet trustworthy," not resolved by picking one.

---

## 3. Hypotheses

- **H_survive** — the silver-first fragility ordering survives degree-control: silver's
  honest, degree-controlled address channel is the most robust.
- **H_confound** — the silver-first result was largely degree; once controlled, silver
  has little unique channel to lose, and the honest ordering differs.
- **H_reorder** — a specific new ordering emerges, led by golden (largest clean honest
  channel in the probe), with golden's decay the meaningful measurement.
- **H0** — no ordering survives the stratified null and damage-matching, or all members'
  S_N sit inside the null band.

H_survive and {H_confound, H_reorder} disagree on whether silver leads. That is the
discriminating test, and — unlike the old headline — silver-first is *not* assumed.

---

## 4. Predictions, stated so they can be scored

- **P1** the degree confound is large and real — degree-alone AUC > 0.85 for all three,
  and > 80% of the old raw "address AUC" is recoverable from degree alone. **Credence 0.90.**
- **P2** the discrete class carries no channel beyond degree — class increment over
  degree+perp < 0.03 at zero damage for golden and platinum. **Credence 0.80.**
- **P3** the silver-first fragility ordering does NOT cleanly reproduce under the
  degree-controlled metric. **Credence 0.60.**
- **P4** golden carries the largest clean (zero-damage) honest channel, S_golden(0) largest.
  **Credence 0.55.**
- **P5** primary and secondary metrics agree on the final ordering. **Credence 0.60** —
  stated low on purpose; if they disagree that is itself the most important outcome.

Overall credence across the hypotheses: **H_confound 0.35 / H_reorder 0.30 /
H_survive 0.20 / H0 0.15.** Recorded to be scored, not because the numbers are precise.

---

## 5. Protocol, fixed in advance

- **Substrates**: `generate_rank4.generate(N)` (singular default) for N = 8, 10, 12;
  `build_edges(lifts, N, ustar)`. Extents tuned so the **active-set count** matches at
  1200, active set the innermost vertices by centroid distance, ≤ 40% of the patch.
- **Damage**: Galois-plane jitter (the pre-registered primary model), read against
  **measured flipped-vertex fraction**, never nominal amplitude. Same amplitude grid as
  the headline. Flip-based damage (`phason_flips.py`) is run as a robustness pass, not
  the primary, to keep comparability with the confirmed dose-response.
- **Features**: address = the two Galois coordinates + radius. Control = scalar degree
  (primary); degree + sorted neighbour-degree multiset (robustness — a richer
  parallel-space control). The congruence class enters only for the P2 sub-question.
- **Model**: `HistGradientBoostingClassifier(max_iter=200)`, 3-fold stratified CV, AUC.
- **Seeds**: ≥ 8 per point; report mean and CI.
- **Nulls**: the degree-stratified permutation null at every point; the plain shuffle
  null kept for continuity with prior work.

---

## 6. Known limitation, stated before the run (the mediator objection)

Degree is **downstream** of the address: in cut-and-project the perpendicular coordinate
*determines* the local vertex environment, so degree is a mediator, not a confounder in
the usual sense. Conditioning on a mediator removes the address's legitimate influence
that flows *through* degree, and can induce collider effects. So the primary metric
measures a precise but narrow thing: **address signal not reducible to scalar
coordination number** — not "non-structural address." This is the correct guard against
the identified class→degree leak, and no more than that. The direct-reconstruction
secondary is included exactly because it conditions on nothing downstream of the address;
their agreement is what licenses a claim. Reviewers should push hardest here.

---

## 7. Relation to the existing pre-registration

`PREDICTION_rank4_headline.md` stands as the record of the confounded run. Its
subsidiary prediction 2 ("the class is inert, or the whole comparison needs revisiting")
is now answered: the class is not inert on raw AUC, so the comparison is being revisited
— here. **The H1 field vs H2 fragmentation discriminating test is SUSPENDED**: field
versus fragmentation cannot be adjudicated on a degree-confounded metric. It resumes only
once this metric is trusted, and only then on the φ(N) = 6 family the old document
already flagged as necessary.

---

## 8. What would count as a failure of the whole programme

- **S_N ≈ 0 for all three under the stratified null.** The address would carry nothing
  beyond degree, and the "address channel" construct — the spine of the project — would
  be in question. This is the deepest possible outcome and must be reported first,
  before any ordering.
- **Primary and secondary metrics disagree.** No ordering is claimed; the measurement is
  reported as untrustworthy.
- **Orderings that flip between seeds** at ≥ 8 seeds.

## 9. Scoring

Write the result into a new results document, state plainly which of H_survive /
H_confound / H_reorder / H0 it supports, **before** any interpretation, and score P1–P5
against the credences above. If the honest metric overturns silver-first, the confirmed
dose-response result (Penrose degrades faster than Ammann–Beenker) must itself be re-read
through the degree-controlled lens before it is quoted again.

---

## Amendment 1 (post-seal; date = this commit) — secondary metric repaired (v2), frozen before damage

Per GPT's ruling. The sealed secondary (v1, coarse degree-based features,
`reconstruct_address.py`) is a **failed calibration**: R² ≤ 0 for all three families even
at zero damage, so it cannot perform its intended task and is **not** reinterpreted as
evidence for or against the primary. A clean diagnostic established the address IS locally
reconstructible from the **vertex type** (canonical cyclic sequence of incident edge
directions), R² ≈ 0.9 — so v1 was mis-specified, not defeated. v1 is preserved as part of
the methods record. Repairing a thermometer that reads −273 °C is not metric-shopping; the
repair was motivated by calibration failure, provably independent of the primary outcome.

**Secondary v2 — frozen here BEFORE any damage outcome is seen; run on fresh offsets/seeds
not used in the diagnostic:**
1. **Target:** the true, offset-free, **current-state** address `a·perp4` of each present
   vertex (encodability, matching v1's intent — NOT the historical/pre-damage address,
   which is a separate future test and must not be silently substituted).
2. **Predictor:** vertex type = canonical minimal-rotation cyclic sequence of incident edge
   star-line indices, from **parallel-space geometry only** (contains no perpendicular-space
   coordinate — no target leakage by construction).
3. **Model:** vertex-type → mean-address lookup (target encoding) learned on train, applied
   to test; unseen/rare test types predict the train grand-mean address.
4. **CV — held-out-offset:** train on a set of window offsets, test on a fresh unseen
   offset (4-fold over offsets). This guards against the spatial-autocorrelation leakage a
   random vertex split hides; a random-split R² is reported alongside only to quantify that
   inflation.
5. **Damage:** Galois-plane jitter, same amplitude grid; measured flipped-vertex fraction.
6. **Decay statistic & amended decision rule:** report ΔR² = R²(0) − R²(D) per family.
   **Clean-level ordering is NOT required to match the primary** — the metrics measure
   different constructs (primary = address information *incremental to degree*; secondary =
   *local encodability*). Agreement = the family with the largest unique address channel
   (primary: golden) also shows a correspondingly measurable **loss** of reconstructible
   address under damage. Disagreement triggers decomposition, not an ordering claim.

**Decomposition (added):** at zero damage, held-out-offset R²(degree→address) vs
R²(degree+type→address) — the address information vertex type carries *conditional on
degree*. Hypothesis: silver's type-increment-over-degree ≈ 0 (reconstructible but redundant
with degree), golden's larger (differentiated encoding), which would explain how the clean
reconstruction ordering (S>G>P) can invert the primary's (G>P>S) with no contradiction.

**Recorded distinctions:** reconstructibility ≠ uniqueness; persistence ≠ information
richness; possibility ≠ preference.

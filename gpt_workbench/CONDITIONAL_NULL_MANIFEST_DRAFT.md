# DRAFT v2 — conditional-null design manifest (radius-saturation §2), standalone

**Status — DRAFT for crew review. NOT sealed, NOT run. No study dynamics/address/LDOS/targets/β/
scores accessed. No science-branch file altered.** Specifies the two conditional nulls, their
baseline, fold structure, permutation construction, statistic/multiplicity, equivalence rules and
computational feasibility, by inspecting the existing code and parent prereg. Standalone.

**v2 (2026-08-31)** applies Sol's pre-seal mathematical-definition repairs (points 2–7). Full dated
change log at the end.

*Source: drafted by the `gpt/workbench` Claude collaborator from crew decisions relayed by Katie;
not part of the scientific record until reviewed and merged.*

---

## 0. Code facts (inspected `transport_run.py`, `residualize_check.py`)
`M3 = [dens, deg, edge_len_mean, edge_len_var, motif one-hot (width = shared codebook), g(1.6),
g(2.6), ψ_N, ψ_{N/2}, ψ_{2N}, g(4.0), g(6.0)]` — categorical (motif one-hot) + continuous;
`dim(M3) = 11 + |codebook|`. Address block `= _m4_cols(f, perp)` = **11 columns**. `held_out_r2` =
leave-one-offset-out CV; GBT `HistGradientBoostingRegressor(max_depth=3, max_iter=250, lr=0.06,
l2=1.0, random_state=0)`. Motif key = canonical sorted multiset of incident `(star-line, sign)`.

## 1. The radius baseline `X_r` (point 2 — unambiguous)
**`X_r := [ M3 , physical_extra(r) ]`**, where **M3 is always retained in full** (including the
motif one-hot and all continuous descriptors) and `physical_extra(r)` is the nested radius block of
the physical manifest (Groups A/B/D/E; dims **11/22/35/48/61** for r = 2/4/8/12/16).
`dim(X_r) = (11 + |codebook|) + physical_extra(r)`.
- **Dedup (frozen):** a `physical_extra(r)` column is dropped **only** if it is bit-identical
  (`max|Δ| < 1e-12` on the evaluated set) to an M3 column; the M3 column is always kept. No M3
  column is ever silently discarded. (None expected: the radius block's binning/coarse-graining
  differs from M3's `dens`/`g`/`ψ`.)
- **All increments become** `ΔR²_• = R²(X_r + •) − R²(X_r)`:
  - **address:** `• = _m4_cols(perp)` (11 cols);
  - **parity:** `• =` the (degree, padded-Voronoi-area) block through the exact 11-col `_m4_cols`
    (physical manifest §4);
  - **capacity:** `• =` a same-dimensional i.i.d.-Gaussian block (physical manifest §6);
  - **residual null (§2):** `• = Ã`, the `X_r`-orthogonalised address block (§2).

## 2. Residual-orthogonal null — leakage-safe nested cross-fitting (point 3; every rung r)
Tests whether address carries structure **orthogonal to the full `X_r`**. Residuals for training
rows must **not** be in-sample.
For each **outer** held-out offset `o` (train = the other five offsets):
1. **Inner cross-fit on the training offsets** using the frozen **four PCA-slab inner folds**
   (physical manifest §5). For inner fold `j`, fit each address-column residualiser
   `g_j^(a) = GBT(X_r → address_a)` on the inner-training rows (slabs ≠ j of every training-offset
   patch) and predict the **held-out inner slab `j`** rows. Every training row's residual
   `ã_a = address_a − ĝ(address_a)` thus comes from a residualiser that **did not train on that
   row's slab** — no in-sample leakage.
2. **Outer residualiser:** fit `g^(a)` on **all five training offsets** and apply it to the
   **wholly unseen outer offset `o`** to residualise its address columns.
3. **Outcome model:** train the outcome GBT on `[X_r , Ã_train]` (cross-fitted training residuals)
   and score `R²` on the outer offset's `[X_r , Ã_o]`. Increment
   `Δ_o = R²(X_r + Ã) − R²(X_r)` on the outer offset.
4. **Statistic:** the **six-offset median** of `{Δ_o}` (§4).
**Documented as a conservative / lossy lower bound** — a nonlinear residual is hard for a second
GBT to exploit; this null under-detects genuine orthogonal content and is stated as such, not a
symmetric test.

## 3. Local permutation null — a genuine one-to-one bijection (point 4; reference radius r=16)
The sealed motif×degree shuffle and any per-vertex kNN "cells" **overlap** and cannot support one
global permutation. Replaced by an **exact one-to-one assignment (derangement)** within each
`(family, tier, offset, exact motif)` group:
1. **Standardise** the continuous `X_16` features with **training-only** mean/std.
2. Within each patch × exact-motif group, form candidate source→destination edges among each
   vertex's **`k = 32` nearest** physical-feature neighbours (excluding self).
3. Add **frozen-seed random jitter** to the candidate edge costs to randomise the choice among near-
   equivalent local candidates (jitter ≪ typical feature gap).
4. Solve a **minimum-cost one-to-one assignment** with `scipy.optimize.linear_sum_assignment`
   (allowed edges = feature distance + jitter; forbidden = large constant), producing a
   **bijection / derangement**.
5. **Escalation (deterministic, outcome-blind):** if no perfect assignment exists at `k=32`,
   increase to **`k=64`**, then to the **full same-motif group**; **flag** the escalation. `k` is
   never chosen from outcomes. (A derangement always exists at full connectivity for a group of
   size ≥ 2.)
6. **Permute the raw two-component address field, then recompute the exact 11-column `_m4_cols`** on
   the permuted field — never shuffle the derived columns independently.
7. **Train vs held-out:** construct the **training-offset** and **held-out-offset** permutations
   **separately**; the held-out patch uses its own physical features with the scaler learned **only
   from outer training** — no held-out targets enter.
**Rare motifs (geometry-only diagnostics, reported):** report the fraction of vertices in motif
groups of **size 1** (singletons); **singletons cannot be permuted and remain fixed points**;
freeze a **maximum acceptable singleton fraction of 5%**; if a patch exceeds it, mark the **local
conditional null infeasible** for that patch (route to the mixed/infeasible outcome) rather than
excluding rows or pretending full randomisation. **Observed and null analyses retain exactly the
same vertex population** (singletons fixed in both).

## 4. Fold dependence, statistic, and global multiplicity (points 3, 6)
- **Preserve the full six-offset LOO structure in every null repetition**; recompute the entire
  six-element vector, never a pooled number.
- **No frozen single primary configuration exists in the parent prereg** for the 9 family×tier
  cells (tiers are a later crew addition). **Proposed outcome-blind global primary statistic:** for
  each held-out offset `o`, the **equal-weight median increment across the nine family×tier
  configurations** `Δ_o = median_{c=1..9} Δ_{o,c}`; then the **primary statistic `M = median_o(Δ_o)`
  across the six offsets**. The **identical** global statistic is constructed in every null
  repetition.
- **Configuration-specific** results are **secondary**: reported with a **synchronised max-statistic
  Westfall–Young** correction over the nine cells (same repetition seeds), or explicitly labelled
  **descriptive**. **No uncorrected selection of the nicest family/tier.**
- **Randomisation p-value (frozen):** one-sided
  `p = (1 + #{ M_null^(b) ≥ M_obs }) / (B + 1)`, with **`B = 1000`** and **`α = 0.05`**.
- **Always report all six `Δ_o` and their signs**; **≥5/6 positive** is a supporting consistency
  criterion, not the test. Offsets are the sampling clusters; the six LOO estimates are correlated
  through overlapping training sets and are never treated as independent replicates.

## 5. Repetitions and seeds (point 6 — exact, frozen)
- **Exactly `B = 1000`** (no "raise to 5000" option). Justification: one-sided MC-SE
  `≈ √(p(1−p)/B) ≈ 0.0069` at `p≈0.05`; smallest reportable tail `1/(B+1) ≈ 1e-3`.
- **Seeds:** `numpy.random.SeedSequence(20260829)` spawned into `B` child streams; repetition `b`
  uses child `b`. Every seed frozen and recorded pre-seal.
- **Synchronised:** the same child seed drives the permutation for coherent vs CTMC and for
  address vs parity vs capacity, so their null medians are paired (within-repetition comparison and
  the Westfall–Young max-statistic).
- **Randomised conditional nulls run at `r = 16` only (frozen).** All-radius conditional permutation
  is **not authorised**; the plain increment and the deterministic residual null are reported at
  every rung.

## 6. Equivalence / detection language (point 7 — `δ_cap`, corrected)
- **`δ_cap` (renamed from `δ*`) is an empirical pipeline detection / noise floor, NOT a
  practical-equivalence margin.** The fixed `0.005` fallback is **deleted**.
- **`δ_cap` construction:** run each of the **200 Gaussian capacity draws** (physical manifest §6)
  through the **exact same primary aggregate statistic** used for address (per-offset median across
  the nine configs, then median across offsets — §4), producing 200 aggregate values; `δ_cap` =
  their **95th percentile**. (Not pooled raw fits — the full fold/config aggregate per draw.)
- **Allowed radius-fade wording:** "**compatible with physical compression at the pipeline's
  resolution**" — only if **all** hold: the **r=2** increment is **positive, sign-stable (≥5/6) and
  `> δ_cap`**; the **r=16** increment is `< δ_cap`; and the **relative reduction `ρ = ΔR²(16)/ΔR²(2)
  < ρ* = 0.25`**. This is **not** proof the true effect is practically zero.
- **`ρ` denominator handling:** if `ΔR²(2)` is non-positive, `< δ_cap`, or sign-unstable, `ρ` is
  **undefined** and the result is **"mixed / undetectable" — never "infeasible."** ("Infeasible" is
  reserved for the physical/count floor or a >5% singleton patch.)
- **"exceeds parity" / "representation collapse" via the paired aggregate:** form the **paired
  `address − parity` aggregate** and its **synchronised** null/detection distribution (same seeds).
  "Exceeds parity" = the paired aggregate exceeds its synchronised detection floor; **"compatible
  with representation collapse"** = it does not (never "proof of equality"). Not defined by merely
  adding `δ_cap` to a single point estimate.
- **"CI includes zero" is never accepted as proof of equivalence.**

## 7. Computational feasibility (point 6 — fits estimate + factorisation)
- **Deterministic (cheap):** plain increment + residual-orthogonal null at **every rung** (5 radii)
  × 9 configs × 6 outer folds × (4 inner folds for the training residuals) — a few thousand GBT
  fits, minutes–hour scale.
- **Randomised (dominant), at r=16 only:** permutation null + capacity, both engines.
  `B(1000) × 6 folds × 9 configs × 2 engines ≈ 108,000` outcome fits, plus
  `200 × 6 × 9 × 2 ≈ 21,600` capacity fits. At ~0.15 s/fit ≈ **~5–6 h**, parallelisable.
- **Factorisation (scientifically identical):** cache the `X_r` baseline `R²` per fold (unchanged by
  permuting address); each repetition refits only `[X_r + permuted-address]`. Residualisers fit once
  per (outer fold, inner fold). No target/outcome regression is run here — this is the fit-count
  estimate only.

## 8. Authorised outcomes (kept distinct; cautious language)
**compression** (fade meeting §6) · **representational** (survives radius, *compatible with
representation collapse* vs the paired parity aggregate) · **stable residual** (paired aggregate
exceeds parity **and** capacity detection floors, survives both conditional nulls) · **mixed /
undetectable** (configs disagree beyond null uncertainty, or `ρ` undefined) · **infeasible**
(physical/count floor unmet, or >5% singletons). Distinct; a result routes to exactly one.
**Claim language:** at most *"the address representation predicts heterogeneity beyond the frozen
physical descriptions and controls."* **No literal perpendicular-space physical-degree-of-freedom
ontology.**

## 9. Geometry/feature feasibility diagnostics (authorised; results)
`gpt_workbench/matching_feasibility.py` (geometry + physical-feature + combinatorics only — no
address values, no targets; 3 representative offsets per tier):

| config | r16 | motif groups | singleton frac (mean / max) | bijection (k=32 / 64 / full) | verdict |
|---|---|---|---|---|---|
| silver e14 | 668 | 41 | 1.16% / 1.22% | 99 / 0 / 0 | FEASIBLE |
| silver e16 | 1120 | 41 | 0.36% / 0.36% | 111 / 0 / 0 | FEASIBLE |
| silver e18 | 1698 | 41 | 0.10% / 0.18% | 110 / 8 / 0 | FEASIBLE |
| golden e18 | 581 | 100 | 3.15% / 4.02% | 243 / 1 / 0 | FEASIBLE |
| golden e20 | 1025 | 109 | 1.51% / 1.85% | 275 / 1 / 0 | FEASIBLE |
| golden e22 | 1535 | 116 | 0.88% / 1.17% | 297 / 1 / 1 | FEASIBLE |
| **platinum e16** | 726 | 191 | **9.07% / 9.22%** | 374 / 0 / 0 | **INFEASIBLE (local null)** |
| **platinum e18** | 1170 | 210 | **5.39% / 5.81%** | 444 / 0 / 0 | **INFEASIBLE (local null)** |
| platinum e20 | 1719 | 229 | 3.31% / 3.58% | 526 / 0 / 0 | FEASIBLE |

**Findings:**
- **Bijection matching succeeds everywhere.** `k=32` resolves almost all motif groups; a handful
  need `k=64` (silver e18: 8; golden: 1 each) and exactly one needs the full group (golden e22).
  No group is truly unmatchable — a derangement always exists at full connectivity. `k=32` primary
  is validated; the escalation path is rarely used.
- **⚠️ Platinum small & medium tiers fail the 5% singleton limit** (e16 = 9.1%, e18 = 5.4%). Platinum
  (12-fold) has ~2–5× more distinct motif types (191–229 groups) than silver (41) or golden
  (~100–116), so more singleton motifs. Per §3, **the local permutation null is marked infeasible
  for platinum e16 and e18** (their residual-orthogonal null §2 and plain increment still apply).
  Platinum e20 (3.3%) is feasible.
- **Crew decision (flagged):** either (a) compute the global permutation-null statistic over the
  **seven feasible cells** and report platinum-small/medium permutation-null as infeasible; or
  (b) **shift platinum's tiers upward** (e18/e20/e22) so all cells pass — noting this would break
  the r16-count tier-matching against silver/golden and needs re-checking; or (c) the crew ratifies
  a different singleton threshold (Sol froze 5%). **Not decided here.**
- **Snapped β-time list:** the 48 log times on [2,8] snapped to the 161-point [0,8] grid are
  **48 unique** with **max error 0.0231** — stored at `gpt_workbench/snapped_beta_times.txt`.

## 10. Open choices for crew
- `k = 32` primary (16/64 balance-sensitivity only, never outcome-selected); `B = 1000` fixed;
  `ρ* = 0.25`; the global-statistic proposal (§4) if the crew has no other frozen primary; whether
  the deterministic residual null runs at all rungs (proposed) vs r=16.

---
## Change log
**v2 — 2026-08-31** (Sol pre-seal repairs): defined the baseline **`X_r = [M3, physical_extra(r)]`**
with M3 always retained and a bit-identical dedup rule, and rewrote all increments as
`R²(X_r+•)−R²(X_r)` (pt 2); made residual cross-fitting **leakage-safe via nested PCA-slab inner
folds** (pt 3); replaced overlapping kNN "cells" with a genuine **`linear_sum_assignment`
one-to-one bijection**, k-escalation 32→64→full, raw-field permutation then `_m4_cols` recompute,
separate train/held-out permutations, and 5%-singleton infeasibility with an invariant vertex
population (pt 4); moved the balance diagnostic to **source→destination distance statistics** (pt 5,
see physical manifest §5b); fixed **`B=1000`**, the one-sided `p=(1+#)/(B+1)`, a **global
median-of-configs-then-offsets** primary statistic with Westfall–Young for config-specifics, and
r=16-only randomised nulls (pt 6); renamed `δ*`→**`δ_cap`** as a detection floor built from the same
aggregate statistic, deleted the 0.005 fallback, and reworded fade/collapse via the **paired
aggregate** with "compatible with … at the pipeline's resolution" (pt 7).

**v1 — 2026-08-29.** Initial conditional-null design.

*End of draft v2. Committed to `gpt/workbench` only. Nothing sealed; no study dynamics/address/
targets accessed; no science-branch file altered.*

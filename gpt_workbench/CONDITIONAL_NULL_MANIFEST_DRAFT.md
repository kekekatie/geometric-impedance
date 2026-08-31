# DRAFT v4 — conditional-null design manifest (radius-saturation §2), standalone

**Status — DRAFT for crew review. NOT sealed, NOT run. No study dynamics/address/LDOS/targets/β/
scores accessed. Only geometry/feature diagnostics + synthetic checks were run.** Self-contained.

**v4 (2026-08-31)** applies Sol's third pre-seal pass: `M₉` membership frozen a priori (never
changed by observed fit quality); the permutation tail renamed **`q_ref`** (extremeness under an
algorithmic reference, not significance); Westfall–Young over the **seven** feasible cells;
order-stable keyed seed substreams; address-vs-parity fully **descriptive** (no gate); and the
locality-ladder investigation (§9). Full dated change log at the end.

*Source: drafted by the `gpt/workbench` Claude collaborator from crew decisions relayed by Katie;
not part of the scientific record until reviewed and merged.*

---

## 0. Code facts (inspected)
`M3 = [dens, deg, edge_len_mean, edge_len_var, motif one-hot (width = shared codebook), g(1.6),
g(2.6), ψ_N, ψ_{N/2}, ψ_{2N}, g(4.0), g(6.0)]`; `dim(M3)=11+|codebook|`. Address `= _m4_cols(perp)`
= 11 cols. GBT `HistGradientBoostingRegressor(max_depth=3, max_iter=250, lr=0.06, l2=1.0,
random_state=0)`. Motif key = canonical sorted multiset of incident `(star-line, sign)`.

## 1. Baseline `X_r` and increments
**`X_r = [M3, physical_extra(r)]`**, M3 always retained in full; `physical_extra(r)` dims
11/22/35/48/61 for r=2/4/8/12/16 (physical manifest §3). Dedup: drop a `physical_extra` column only
if bit-identical (`max|Δ|<1e-12`) to an M3 column; never drop M3. Every increment
`ΔR²_• = R²(X_r+•) − R²(X_r)` with `•` ∈ {address, parity, capacity, address-residual}.

## 2. Residual-orthogonal null — leakage-safe nested cross-fitting (every rung r)
For each **outer** held-out offset `o` (train = five offsets):
1. **Inner cross-fit** on the training offsets using the four PCA-slab inner folds (physical §5):
   residualiser `g_j^(a)=GBT(X_r→address_a)` fit on inner-training rows (slabs ≠ j across every
   training patch), predicting held-out inner slab `j`; each training row's residual
   `ã_a = address_a − ĝ(address_a)` comes from a residualiser that never trained on that row's slab.
2. **Outer residualiser** `g^(a)` fit on all five training offsets, applied to the unseen outer
   offset `o`.
3. Train outcome GBT on `[X_r, Ã_train]`, score on `[X_r, Ã_o]`; `Δ_o = R²(X_r+Ã)−R²(X_r)`.
4. Statistic: the six-offset structure (§4).
**Deterministic, conservative / lossy lower-bound diagnostic — NOT a randomisation test** (a
nonlinear residual is hard for a second GBT). Its "survives" criterion is defined in §6.

## 3. Local permutation null — genuine stochastic one-to-one law (reference radius r=16)
Overlapping per-vertex kNN "cells" cannot support one global permutation; jitter-only tie-breaking
returns essentially one matching every repetition; and a **uniform** random-cost law at any single
`k` cannot be both broadly bijective and materially local (locality ladder §9). Replaced by a
**distance-weighted stochastic minimum-cost assignment** within each `(family, tier, offset, exact
motif)` group:
1. **Candidate graph (broad, for bijectivity):** the `k = 32` nearest same-motif physical-feature
   neighbours (self excluded), features standardised with the **training-only** scaler. (`k=32`
   is the smallest single `k` that is broadly bijective across *all seven* feasible configs — the
   large silver motif groups require it, §9.)
2. **Distance-weighted per-repetition randomisation (PROPOSED — λ pending crew ratification):** for
   repetition `b`, assign each allowed edge the cost **`cost = feature_distance + λ·U(0,1)`** with
   **`λ = 1.0`** in standardised-feature units (child seed `b`, §5); solve the **minimum-cost
   perfect assignment** (`scipy.optimize.linear_sum_assignment`), giving a bijection/derangement.
   The distance term makes each replicate favour **near** partners (locality), while `λ·U` supplies
   randomisation. **Do NOT use `distance × U`** (it can make a distant edge artificially near-free).
   The locality-ladder diagnostic (§9, reproducibility-repaired) shows this law at k=32 is **fully
   diverse (distinct = 1.0) and materially more local than an unrestricted within-motif shuffle**
   (paired tail p95 source→dest distance ≈ **0.375** of unrestricted at λ=1.0; **0.37–0.41** across
   the λ-sweep), whereas a uniform-cost law at k=32 is not. **λ is proposed, not silently selected**
   — the crew ratifies it from the λ-sweep in §9.
3. **Deterministic, outcome-blind escalation:** if no perfect assignment exists at `k=32`, increase
   to `k=64`, then the full same-motif group; flag the escalation. `k` is never chosen from outcomes.
4. **Permute the raw two-component address field, then recompute the exact 11-column `_m4_cols`.**
5. **Train vs held-out permutations constructed separately;** the held-out patch uses its own
   features with the outer-training scaler. No held-out targets enter.
6. **Singletons** (motif groups of size 1) **cannot be permuted and remain fixed points.** Frozen
   **max acceptable singleton fraction = 5%** (patch-level, over the r16 common set). If a patch
   exceeds it, its **local permutation null is infeasible** (route per §7); **no result may be
   described as surviving the local permutation null for an infeasible cell.** Observed and null
   analyses retain **exactly the same vertex population** (singletons fixed in both).

**Honesty on the reference distribution (this is a STRESS reference, not inferential significance):**
because the candidate graph constrains which permutations are admissible, this is **not** an exact
exchangeable conditional-randomisation test. Its Monte-Carlo tail fraction is therefore named
**`q_ref = (1 + #{ M_null^(b) ≥ M_obs }) / (B+1)`** and is described as **extremeness under the
algorithmically-defined constrained-permutation reference distribution** — **not** a frequentist
significance p-value under an exchangeable null. It may serve as a **frozen operational stress-test
gate (`q_ref < 0.05`)**, but it is an adversarial control on interpretation, not a significance
result. **The empirical result remains the held-out predictive increment** (`M₉` / `M_perm,7`).

## 4. Fold dependence, statistics, and multiplicity
- Every null repetition recomputes the **full six-offset LOO vector**; offsets are the sampling
  clusters (correlated through overlapping training sets — never independent replicates).
- **`M₉` (ordinary primary) — membership FROZEN a priori, never changed from observed dynamics:**
  for each held-out offset `o`, the equal-weight median increment across the **nine** family×tier
  configs; then the **median across the six offsets**. Used for the plain increment, residual null,
  parity and capacity. **`M₉` always contains all nine configs.** A configuration's poor observed
  fit quality (MSD G1) does **not** remove it from `M₉` — that would make membership a function of
  the data and invalidate comparisons; instead the consequences of a G1 failure are the ones stated
  in MSD v8 §7/§12 (the config becomes descriptive and the *global* claim fails/downgrades — the
  statistic is never recomputed over a subset).
- **`M_perm,7` (local-permutation reference) — membership from GEOMETRY only:** the same construction
  restricted to the **fixed seven permutation-feasible configs** (silver×3, golden×3, platinum e20;
  determined by the geometry-only six-offset audit §9 — outcome-blind). Distinct from `M₉`; the only
  statistic used for the local permutation test. Platinum e16/e18 are **never** described as surviving
  the permutation null.
- **Stress-reference tail (frozen):** `q_ref = (1 + #{ M_null^(b) ≥ M_obs }) / (B+1)`, `B=1000`,
  operational gate `q_ref < 0.05` (extremeness under the algorithmic reference, §3 — not a
  significance p).
- **Always report all six `Δ_o` and signs**; ≥5/6 positive is supporting, not the test.
- **Config-specific secondary — Westfall–Young step-down max-T over the SEVEN feasible cells** (the
  permutation null is only defined there; platinum e16/e18 remain descriptive for this control). The
  per-config statistic `T_c` = that config's six-offset-median increment (a **signed one-sided**
  statistic). Null statistics `T_c^(b)` are the **raw permutation increments, not additionally
  centered**. Order observed `T_(1) ≥ … ≥ T_(7)`. For rank `i` (step-down),
  `q̃_(i) = (1 + #{ b : max_{c ∈ {(i),…,(7)}} T_c^(b) ≥ T_(i) }) / (B+1)`, then enforce monotone
  non-decreasing `q̃`. These `q̃` are **extremeness values under the same algorithmic reference**
  (§3), not exchangeable-null significances. Same child seeds across configs (synchronised max). **No
  uncorrected selection of the nicest family/tier.**

## 5. Seed registry (explicit, no fictional parity seed; order-stable)
- **Address-permutation registry:** root `SeedSequence(20260829)` → **1000 child streams**;
  repetition `b` uses child `b` for its random edge costs, **synchronised across engines (coherent,
  CTMC) and configs** where pairing/max-T is intended.
- **Order-stability (frozen):** a substream is addressed by **stable identifiers
  `(family, tier, offset, motif-key, b)`** — the motif-key from the canonical sorted incident-star
  multiset, offsets in the frozen list order — **not** by Python `dict`/group **traversal order**.
  Concretely, each group's per-repetition edge-cost RNG is
  `default_rng(SeedSequence(20260829, spawn_key=(hash64(family,tier,offset,motif), b)))` (or an
  equivalent stable keyed derivation), so results are invariant to dictionary/iteration order.
- **Capacity registry (separate):** root `SeedSequence(20260830)` → **200 child streams indexed
  `0…199`** (child-stream indices under the capacity root — **not** literal integer RNG seeds and
  not the address children), one Gaussian block per child (physical §6).
- **Parity has NO seed** — it is deterministic (fit the fixed physical field through `_m4_cols`).
- **Randomised conditional nulls run at `r=16` only (frozen).** The plain increment and the
  deterministic residual null are reported at every rung.

## 6. Detection floor `δ_cap` and gate criteria (ratified)
- **`δ_cap` (ratified):** the **95th percentile of the 200-draw capacity distribution of the full
  nine-config aggregate statistic `M₉`** (each Gaussian draw produces a complete `M₉`). It is a
  **pipeline detection floor only** — not a practical-equivalence margin, not evidence of zero. The
  fixed 0.005 fallback is deleted.
- **"exceeds capacity":** `M₉,address > δ_cap`.
- **"survives the residual-orthogonal null" (explicit pre-sealed criterion):** the deterministic
  `M₉` of `ΔR²_resid` (§2) `> δ_cap`. Stated as a **lower-bound detection** check, not a
  randomisation test.
- **"passes the local permutation stress gate":** `q_ref = (1+#{M_perm,7 null ≥ M_perm,7 obs})/(B+1)
  < 0.05` — extremeness under the algorithmic reference (§3), for feasible cells only. **Not** a
  significance test.
- **Address vs parity — DESCRIPTIVE ONLY, never a pass/fail ingredient.** Parity is deterministic
  (no null); no defensible paired *significance* reference exists, and `δ_cap` was calibrated for a
  *capacity* increment, **not** for the difference `Δ_ap`, so `δ_cap` is **not** a calibrated
  detection floor for `address − parity`. We therefore **report** `M₉,address`, `M₉,parity`, and
  `Δ_ap = M₉,address − M₉,parity` **descriptively**, with **no threshold and no gate**. The phrase
  "**compatible with representation collapse**" is used only qualitatively (small `Δ_ap`) and is
  never proof of equality.

## 7. Authorised outcomes (distinct; cautious language)
- **compression (at the pipeline's resolution):** `M₉,address(2)` positive, sign-stable (≥5/6),
  `> δ_cap`; `M₉,address(16) < δ_cap`; `ρ = M₉,address(16)/M₉,address(2) < ρ* = 0.25`. `ρ*` is a
  **frozen classification heuristic**, not an equivalence margin. If `M₉,address(2)` is
  non-positive, `< δ_cap`, or sign-unstable, `ρ` is **undefined → mixed/undetectable, never
  infeasible.**
- **survives the frozen stress controls (replaces "stable residual"):** `M₉,address > δ_cap`
  (capacity), the residual-orthogonal lower-bound check passes (`M₉` of `ΔR²_resid > δ_cap`), **and**
  the permutation stress gate passes on `M_perm,7` (`q_ref < 0.05`). Reported as *"the address
  increment survives the frozen capacity, residual and permutation stress controls; the parity
  comparison is reported descriptively."* **This is NOT a categorical "irreducible" verdict**, and
  `Δ_ap` is **not** an ingredient.
- **mixed / undetectable:** configs disagree beyond null uncertainty, or `ρ` undefined, or an
  undefined-denominator gate route.
- **infeasible:** physical/count floor unmet, or a patch >5% singletons (local permutation control
  unavailable for that cell only).
- **Claim language:** at most *"the address representation predicts heterogeneity beyond the frozen
  physical descriptions and controls."* No literal perpendicular-space DOF ontology.

## 8. Computational feasibility
Deterministic (plain + residual null, every rung): a few thousand GBT fits. Randomised permutation
(r=16 only, both engines, the **7 feasible configs**): `B(1000)×6×7×2 ≈ 84k` outcome fits; capacity
`200×6×9×2 ≈ 21.6k`. ~5–6 h, parallelisable; cache the `X_r` baseline per fold, refit only
`[X_r+permuted-address]`. No target/outcome regression is run here.

## 9. Geometry/feature feasibility diagnostics (authorised; results)
`gpt_workbench/singleton_audit_v2.py` — six-offset per-patch audit + randomisation diversity
(geometry/feature/synthetic only; per-patch results in `SIX_OFFSET_AUDIT_REPORT.md`).

**Singleton audit — all six offsets, per patch (max singleton fraction over the six):**

| config | r16 range | max singleton (over 6 offsets) | matching | six-offset verdict |
|---|---|---|---|---|
| silver e14/e16/e18 | 653–1723 | ≤ 1.22% | k=32 (rare 64) | **FEASIBLE (6/6)** |
| golden e18/e20/e22 | 581–1559 | ≤ 4.19% | k=32 (rare 64/full) | **FEASIBLE (6/6)** |
| **platinum e16** | 725–735 | **8.95–9.80%** | k=32 | **INFEASIBLE (6/6)** |
| **platinum e18** | 1165–1171 | **5.13–6.24%** | k=32 | **INFEASIBLE (6/6)** |
| platinum e20 | 1704–1719 | 2.97–4.17% | k=32 | **FEASIBLE (6/6)** |

**Finalised feasible set = 7 configs** (silver×3, golden×3, platinum e20). Platinum e16/e18 are
infeasible for the local permutation null on **every** offset (consistently > 5%, not borderline) —
so **`M_perm,7`** is over these seven cells (§4). The bijection matching is feasible everywhere
(`k=32` primary; a handful escalate to 64, and golden e22 once to full). Chosen from geometry alone
→ outcome-blind.

**Locality ladder (`gpt_workbench/locality_ladder.py`; `locality_ladder.csv`, 588 rows;
`locality_final.csv`, 336 rows; report `LOCALITY_LADDER_REPORT.md`). Reproducibility-repaired:**
stable `blake2b` seed registry (no salted `hash()`); real λ-sweep `{0.25,0.5,1,2}`; replicated
**paired** unrestricted derangements; frozen infeasibility Policy A (escalation, no dropping) vs B;
`REPS=40`; absolute + ratio stats; features reconciled to the M3 continuous family; aggregation =
nested median over `M_perm,7`. Two findings:
1. **Uniform-cost law:** no single `k` gives both broad bijectivity and locality. Silver's large
   motif groups need `k=32` (silver e18 movable-feasible: k8=0.30, k16=0.73, k32=0.96), but as `k`
   grows the uniform law's moves **lengthen** toward the unrestricted shuffle (abs p95 1.63→**3.39**),
   whereas the distance-weighted law stays flat and local (abs p95 ≈ **1.6** at every `k`). Same
   candidate graph and feasibility; only the cost law makes it local.
2. **Distance-weighted additive law at `k=32`, `λ=1.0` — RESOLUTION:** broadly bijective
   (**movable-feasible 1.000** under Policy-A escalation; 0.986 at k=32 pre-escalation, the shortfall
   confined to silver e18 3.96% and golden e22 4.88%), **fully diverse** (distinct 1.000;
   **partner-turnover 0.541** — the fraction of movable vertices assigned a different partner between
   reps), and **materially more local** than unrestricted: **absolute** p95 move **1.62** vs
   unrestricted **4.81** (standardised units); **paired** distance ratio **median 0.000, p95 0.375**
   (λ-sweep p95 **0.37–0.41** — robust). Median ratio 0 because the median move is to a
   **feature-identical** partner (duplicate integer-count features); the **p95 ≈ 0.375** is the
   informative locality measure, well below the unrestricted 1.0. Policy B (hold-fixed) gives the
   same locality (p95 ratio 0.376) — robust to the policy choice.

**Verdict:** the distance-weighted law at `k=32`, `λ=1.0` **genuinely conditions on the continuous
descriptors** (not motif alone) while remaining broadly bijective and diverse — it meets the ladder's
aim, reproducibly. It is the **proposed final matching law (§3)**; `λ` is offered for crew
ratification, not silently frozen. (`distance × U` is explicitly rejected — it can make a distant
edge near-free.)

## 10. Open choices for crew (ratified items removed)
- **`λ = 1.0`** for the distance-weighted matching law (§3): proposed from the locality ladder (§9);
  the crew ratifies from the λ-sweep. `k = 32` is fixed (smallest broadly-bijective single k).
- **`ρ* = 0.25`** (classification heuristic).

*(Resolved/removed from open choices: `δ_cap` ratified §6; the seven-cell `M_perm,7` feasible set
finalised §9; `B=1000` frozen; the address-vs-parity comparison is settled as descriptive-only §6;
the k=32 locality blocker is resolved by the distance-weighted law §3/§9.)*

---
## Change log
**v4.1 — 2026-08-31** (Sol locality reproducibility repair): rewrote `locality_ladder.py` with a
stable `blake2b` seed registry (no salted `hash()`), a real committed λ-sweep `{0.25,0.5,1,2}`,
replicated **paired** unrestricted derangements, a frozen infeasibility Policy A (deterministic
k=32→64→full escalation, no silent dropping) vs Policy B, `REPS=40`, absolute + paired-ratio
statistics with a defined nested-`M_perm,7` aggregation, and features reconciled exactly to the M3
continuous physical family (`dens=g(2.0)` etc.). Updated §3/§9 to the reproducible figures
(movable-feasible 1.000 under Policy A; distinct 1.000; partner-turnover 0.541; paired p95 ratio
0.375; λ-sweep 0.37–0.41). Conclusion and λ-pending-ratification unchanged.

**v4 — 2026-08-31** (Sol 3rd pre-seal pass): froze **`M₉` membership a priori** — never changed by
observed fit quality (pt 3); kept the **seven-cell `M_perm,7`** explicitly separate from the
nine-cell `M₉` (pt 3); made the address-vs-parity comparison **fully descriptive, no gate**, and
noted `δ_cap` is not valid for `Δ_ap`, removing the categorical "stable residual/irreducible" verdict
(pt 4); renamed the permutation tail **`q_ref`** — extremeness under the algorithmic reference, not
exact-conditional; applied the same to the Westfall–Young `q̃` **over the 7 feasible cells** (pt 5,6);
made the seed substreams **order-stable keyed** and fixed the capacity-seed wording to child-stream
indices 0…199 (pt 6); and **resolved the locality blocker** — the locality ladder (§9) shows a
**distance-weighted additive law (`k=32`, `λ=1.0`)** is broadly bijective, fully diverse and
materially more local than an unrestricted shuffle (pt 1).

**v3 — 2026-08-31** (Sol 2nd pre-seal): six-offset M₉/M_perm,7 policy; stochastic assignment law;
seed registry; descriptive parity; Westfall–Young; `δ_cap` ratified. **v2 — 2026-08-31** (1st
pre-seal). **v1 — 2026-08-29** (initial).

*End of draft v4. Committed to `gpt/workbench` only. Nothing sealed; only geometry/feature +
synthetic diagnostics run; no science-branch file altered.*

# DRAFT v3 — conditional-null design manifest (radius-saturation §2), standalone

**Status — DRAFT for crew review. NOT sealed, NOT run. No study dynamics/address/LDOS/targets/β/
scores accessed. Only geometry/feature diagnostics + synthetic checks were run.** Self-contained.

**v3 (2026-08-31)** applies Sol's second pre-seal pass: completed six-offset feasibility policy
(M₉ vs M_perm,7); a genuine stochastic assignment law (not jitter); an explicit seed registry;
the downgraded (descriptive) address-vs-parity comparison; an exact Westfall–Young definition; and
`δ_cap` ratified. Full dated change log at the end.

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
Overlapping per-vertex kNN "cells" cannot support one global permutation, and jitter-only
tie-breaking returns essentially one matching every repetition (not a randomisation). Replaced by a
**stochastic minimum-cost assignment** within each `(family, tier, offset, exact motif)` group:
1. **Frozen candidate graph:** the `k = 32` nearest same-motif physical-feature neighbours (self
   excluded), features standardised with the **training-only** scaler.
2. **Per-repetition randomisation:** for repetition `b`, assign **independent seeded U(0,1) random
   costs** to the allowed edges (child seed `b`, §5); solve the **minimum-cost perfect assignment**
   (`scipy.optimize.linear_sum_assignment`), giving a bijection/derangement. Independent random edge
   costs yield **materially different** admissible matchings across repetitions while the candidate
   graph enforces locality (diversity diagnostic §9).
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

**Honesty on the reference distribution:** because the candidate graph constrains which permutations
are admissible, this is **not** an exact exchangeable conditional-randomisation test. Its p-value is
a **Monte-Carlo tail probability under the frozen constrained-permutation reference distribution**,
not an "exact conditional" p-value.

## 4. Fold dependence, statistics, and multiplicity
- Every null repetition recomputes the **full six-offset LOO vector**; offsets are the sampling
  clusters (correlated through overlapping training sets — never independent replicates).
- **`M₉` (ordinary primary):** for each held-out offset `o`, the equal-weight median increment
  across the **nine** family×tier configs; then the **median across the six offsets**. Used for the
  plain increment, residual null, parity and capacity.
- **`M_perm,7` (local-permutation reference):** the same construction restricted to the **fixed set
  of permutation-feasible configs** (determined by the geometry-only six-offset audit §9 — outcome-
  blind). If platinum-small/medium are infeasible, this is the **seven** feasible cells;
  **`M_perm,7` is distinct from `M₉`** and is the only statistic used for the local permutation
  test. Infeasible cells are **never** described as surviving the permutation null.
- **Randomisation p (frozen):** one-sided `p = (1 + #{ M_null^(b) ≥ M_obs }) / (B+1)`, `B=1000`,
  `α=0.05`.
- **Always report all six `Δ_o` and signs**; ≥5/6 positive is supporting, not the test.
- **Config-specific secondary — Westfall–Young step-down max-T (exact):** the per-config statistic
  `T_c` = that config's six-offset-median increment (a **signed one-sided** statistic; larger = more
  evidence). Null statistics `T_c^(b)` are the **raw permutation increments, not additionally
  centered** (the permutation already removes the address signal, so null `T_c^(b)` cluster near the
  physical baseline). Order observed `T_(1) ≥ … ≥ T_(9)`. For rank `i` (step-down),
  `p̃_(i) = (1 + #{ b : max_{c ∈ {(i),…,(9)}} T_c^(b) ≥ T_(i) }) / (B+1)`, then enforce monotone
  non-decreasing `p̃`. Same child seeds across configs (synchronised max). **No uncorrected
  selection of the nicest family/tier.**

## 5. Seed registry (explicit, no fictional parity seed)
- **Address-permutation registry:** root `SeedSequence(20260829)` → **1000 children**; repetition `b`
  uses child `b` for its random edge costs, **synchronised across engines (coherent, CTMC) and
  configs** where pairing/max-T is intended.
- **Capacity registry (separate):** root `SeedSequence(20260830)` → **200 children** (seeds 0…199),
  one Gaussian block per child (physical §6).
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
- **"survives the local permutation null":** `p = (1+#{M_perm null ≥ M_perm,7 obs})/(B+1) < α` — and
  only for feasible cells.
- **Address vs parity — DOWNGRADED to a preregistered descriptive paired aggregate.** Parity is
  deterministic (no null), so no statistically defensible paired *significance* distribution exists;
  inventing one would collapse to the address permutation test shifted by a constant. Therefore we
  **report descriptively**: `M₉,address`, `M₉,parity`, and the paired difference
  `Δ_ap = M₉,address − M₉,parity`, each against `δ_cap`. "**Compatible with representation
  collapse**" = `Δ_ap ≤ δ_cap` (address not detectably beyond parity); it is **not** proof of
  equality and carries **no significance threshold**.

## 7. Authorised outcomes (distinct; cautious language)
- **compression (at the pipeline's resolution):** `M₉,address(2)` positive, sign-stable (≥5/6),
  `> δ_cap`; `M₉,address(16) < δ_cap`; `ρ = M₉,address(16)/M₉,address(2) < ρ* = 0.25`. `ρ*` is a
  **frozen classification heuristic**, not an equivalence margin. If `M₉,address(2)` is
  non-positive, `< δ_cap`, or sign-unstable, `ρ` is **undefined → mixed/undetectable, never
  infeasible.**
- **representational:** survives radius; `Δ_ap ≤ δ_cap` (**compatible with** representation collapse,
  descriptive).
- **stable residual:** `M₉,address > δ_cap`, `Δ_ap > δ_cap`, residual null passes (§6), **and** the
  permutation null passes on `M_perm,7`.
- **mixed / undetectable:** configs disagree beyond null uncertainty, or `ρ` undefined.
- **infeasible:** physical/count floor unmet, or a patch >5% singletons (local null infeasible for
  that cell only).
- **Claim language:** at most *"the address representation predicts heterogeneity beyond the frozen
  physical descriptions and controls."* No literal perpendicular-space DOF ontology.

## 8. Computational feasibility
Deterministic (plain + residual null, every rung): a few thousand GBT fits. Randomised (permutation
+ capacity, r=16 only, both engines): `B(1000)×6×(feasible configs)×2 ≈ 84k–108k` outcome fits +
`200×6×9×2 ≈ 21.6k` capacity fits, ~5–6 h, parallelisable; cache the `X_r` baseline per fold, refit
only `[X_r+permuted-address]`. No target/outcome regression is run here.

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

**Randomisation-diversity diagnostic (40 reps):** the stochastic random-cost law produces
**40/40 distinct assignments** with **~80–85% of movable vertices changing destination between
repetitions** — a genuine randomisation distribution (the jitter-degeneracy problem is fixed).

**⚠️ Locality caveat (blocker for crew — honest finding):** at `k=32`, the constrained source→
destination standardised-feature distance is **essentially equal to an unrestricted within-motif
shuffle** (golden e18: constrained median 1.398 vs unrestricted 1.387; platinum e20: 1.795 vs
1.886). Because `k=32` spans a large fraction of typical motif-group sizes (~30–180 here) and the
costs are random, a partner is drawn ~uniformly from most of the group — so **the permutation null
at k=32 conditions essentially on motif only, NOT tightly on the continuous descriptors** (its
intended purpose). **This defeats the point of the "local" null.** Options for crew: (a) **reduce
`k` substantially** (e.g. `k≈4–8`) so all admissible partners are genuinely near — then re-run this
diagnostic to confirm; (b) adopt **distance-weighted random costs** (cost = feature-distance × U(0,1))
to bias toward near partners while randomising; (c) accept and **rename** the null as a
*motif-conditional* shuffle (honest about what it holds fixed). `k=16/64` sensitivity will not fix
this — even `k=32` already behaves like the unrestricted shuffle. **Flagged; not silently resolved.**

## 10. Open choices for crew
`k=32` primary (16/64 balance-sensitivity only); `B=1000`; `ρ*=0.25` (classification heuristic);
`δ_cap` calibration; the final feasible-config set for `M_perm` (from §9); the descriptive-only
status of the address-vs-parity comparison.

---
## Change log
**v3 — 2026-08-31** (Sol 2nd pre-seal pass): finalised the **M₉ / M_perm,7** policy from a full
six-offset feasibility audit (pt 1); replaced jitter-tie-break with a **stochastic random-cost
assignment law** and stated its p-value is a **Monte-Carlo tail probability under a constrained-
permutation reference**, not exact-conditional (pt 2); built an explicit **seed registry** (1000
address-permutation children; separate 200 capacity draws; **no parity seed**), **downgraded the
address-vs-parity comparison to a descriptive paired aggregate**, and gave an **exact Westfall–Young
step-down max-T** with uncentered signed one-sided statistics (pt 3); **ratified `δ_cap`** as the
95th percentile of the 200-draw nine-config aggregate and reworded `ρ*` as a classification heuristic
(pt 7); and gave every "survives" an explicit pre-sealed criterion (pt 6).

**v2 — 2026-08-31** (Sol 1st pre-seal). **v1 — 2026-08-29** (initial).

*End of draft v3. Committed to `gpt/workbench` only. Nothing sealed; only geometry/feature +
synthetic diagnostics run; no science-branch file altered.*

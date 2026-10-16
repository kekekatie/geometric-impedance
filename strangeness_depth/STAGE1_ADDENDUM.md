# Stage 1 addendum — grip operationalisation SEALED, and the Theorem-1 tension

**Recorded before the ratio is computed**, to keep "named-before-measured" honest.

## Grip definition (provided by the collaboration, sealed here)

From the strangeness paper (relayed via Gemini, who had the full context):

- Phase-space-corrected permeability: **η\* = Γ · m² / p³**
- Anchoring variable (grip): **w(|S|) = 1 − η\*(|S|) / η\*(0)**
- Grip is to be read as the **perp-holonomy analog** — the Theorem-2 memory
  quantum.
- **S ↔ shell map: one coordination shell per unit of strangeness S.**

These are sealed as the pre-registered operationalisation. Cleared to compute
without fishing.

## The load-bearing tension this raises (must be resolved before the number)

"Grip = perp-holonomy" collides with our own **Theorem 1**:

> On the ideal, defect-free 2D quasicrystal, perpendicular-space holonomy of
> every closed loop is **identically zero** (`ker(π∥)` has zero perp image;
> verified, `defect_holonomy_test/verify_holonomy_theorem.py`).

So on the perfect AB/Penrose tiling, grip-as-holonomy is **0 at every
depth-shell**. The rising grip ladder therefore *cannot* live on the ideal
tiling — it can only come from **approximant misfit** (Theorem 2). Consequences,
computed only from already-registered numbers (no new construction):

- The registered per-order memory-quantum shrink ratio is **√2−1 ≈ 0.414 (AB)**
  and **1/φ ≈ 0.618 (Penrose)** (`phase0_registration.json`).
- With the sealed **one-shell-per-S** map, this predicts
  **E(1)/E(0) ≈ 0.414 (AB) / 0.618 (Penrose)** — which **misses T1 = 0.158 ±
  0.027** (9σ / 17σ).
- The LIVE power **(√2−1)² = 0.172** (0.5σ from T1) requires **two** substrate
  generations per unit S — which **contradicts** the sealed one-shell-per-S map.

## The sharp, pre-registered question for the next session

Exactly one of these must be chosen **on geometric grounds, before the ratio is
promoted** (choosing by which hits 0.158 would be fishing):

1. **Grip lives on the ideal tiling** (depth/window-anchoring, not closed-loop
   holonomy). Then Theorem 1 does not apply and depth-shell structure is the
   ladder — but then grip ≠ the Theorem-2 holonomy Gemini named, so the
   definition needs amending.
2. **Grip is approximant misfit** (the Theorem-2 holonomy as named). Then the
   ladder ratio is √2−1 / 1/φ per generation, and the S↔generation map decides
   everything: one-per-S → **T1 missed → 2D excluded** (clean negative); two-per-S
   → **AB hits (√2−1)²=0.172 ≈ T1, Penrose misses** → partial, and the two-per-S
   map must be justified geometrically, not chosen to fit.

Either resolution is a clean, publishable outcome under §6. Both require the
author to pin the ideal-vs-misfit reading and the generation map **before** the
number is quoted. This addendum freezes the state so that decision is on record.

## Status

- Descriptive Stage 1 result (banding real; count ~6–7 not ~4) stands (`STAGE1_NOTES.md`).
- Grip definition sealed (above).
- Theorem-1 tension identified and its numerical consequences pre-computed from
  registered values only.
- **Ratio deliberately not promoted.** Next unhurried session resolves the
  ideal-vs-misfit reading + generation map, then computes the sealed ratio once.

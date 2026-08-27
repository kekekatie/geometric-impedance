# Results — residualization cross-check: what does the address know beyond the physical descriptors?

*ROADMAP step 1. EXPLORATORY cross-check on the sealed transport result. Code:
`residualize_check.py`. Predict each M4/address feature from M3 with the same nonlinear model,
keep only the M3-orthogonal residual, and ask whether that residual still predicts coherent
transport. Cross-fit (residuals and transport model trained only on the other offsets).*

## Result (golden, coherent primary-window LDOS, held-out over 4 offsets)

| quantity | value |
|---|---|
| address features' predictability from M3 (held-out R²) | 0.47 |
| M3 baseline R² | 0.856 |
| **plain M4-over-M3 increment** (reproduces the sealed result) | **+0.027** |
| **residualized-address increment** (M3-orthogonal part only) | **+0.004** |

The plain increment reproduces the sealed +0.03. But the **residualized-address increment nearly
vanishes**: the part of the address that is *orthogonal* to M3 carries almost no transport
information. The address is ~half predictable from M3, and it is precisely the *shared* half
that does the work — the M3-orthogonal remainder does not.

## What this means (carefully, and it tempers the story)

The address's transport-predictive value is **not** an independent, M3-orthogonal channel. It
lives in the part of the address that is *shared with / correlated with* the physical
descriptors — the address acts as a **compact, well-organized multiscale re-encoding** of
information largely also present in M3, not as a hidden coordinate carrying orthogonal content.

Reconciling this with the other controls (they are consistent, and together they pin the claim):

- **Stratified shuffle killed the increment** ⇒ the signal needs the *real spatial organization*
  of the address, not just the coarse motif×degree bins. So the useful part is finer than the
  bins.
- **Survived long-range physical enrichment (M3far)** ⇒ that useful part is not captured by
  long-range *physical* descriptors.
- **Residualization kills it here** ⇒ but it *is* captured by (correlated with) the *local*
  physical/motif descriptors in M3 — the address is a re-coding of local structure, organized
  multiscale, not orthogonal to it.

Put together: **the address is a transport-aligned, multiscale re-encoding of local structural
information — its value is in the organization/encoding, not in an orthogonal hidden channel.**
This nudges the interpretation toward the humble side (address ≈ efficient multiscale coding of
shared structure) and away from "perpendicular space carries information the physics cannot" —
exactly the language discipline the roadmap asks for (rule 6).

## Caveats

- **Nonlinear residualization is lossy.** The residual of a GBT prediction is a hard object for
  a second GBT to exploit, so +0.004 is a *lower bound* on M3-orthogonal content — the true
  orthogonal contribution could be somewhat larger. The direction (most value is in the shared
  structure) is nonetheless clear and consistent with the shuffle result.
- Golden, coherent primary window, extent 14, 4 offsets — a cross-check, not a re-run of the
  sealed confirmatory test. Silver/platinum not yet run here.
- The trustworthy headline remains the **plain, four-times-controlled** M4-over-M3 increment;
  this step refines its *interpretation*, it does not overturn it.

## Files

`residualize_check.py` · follows `RESULTS_TRANSPORT.md`, `RESULTS_ADDRESS_SPLIT.md`; ROADMAP
step 1.

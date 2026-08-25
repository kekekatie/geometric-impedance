# Results — does a physical law READ the address? (transport hierarchy, confirmatory)

*Confirmatory run of the SEALED `PREREG_transport_hierarchy.md` (sealed commit `1f6222c`,
before any run here). Code: `transport_run.py`. Reproduce: `python transport_run.py 8 10 12`.
Per-vertex observable regressed on nested feature sets M0→M4, held-out-offset CV (5
offsets), same regressor (HistGradientBoosting) for every rung and both engines. The
decisive quantity is the **M4-over-M3 increment** (does multiscale ADDRESS organization
predict transport beyond degree/motif/local structure factor?), and whether the
**stratified address shuffle** (perp permuted within motif×degree bins, M4 recomputed)
kills it. An exploratory **physical-position control** (M4 over M3 + (x,y,r)) was added to
guard a smooth-coordinate confound — this is beyond the sealed rule and labelled as such.*

## Verdict

Two results are robust across all three families; one clean result is family-specific.

1. **Coherent reads multiscale geometry; incoherent does not (all three families).** The
   tight-binding wave's local density of states carries a real M4-over-M3 increment
   (+0.03 to +0.09 held-out); the incoherent random walk carries essentially none
   (+0.002 to +0.004). A clean "which law reads what" contrast, exactly as the report and
   the border-wall picture predicted (P1 confirmed: incoherent M4 ≈ 0).
2. **The signal is not a physical-position artefact (all three).** Adding (x, y, r) to M3
   changes the M4 increment by <0.003 everywhere — the wave is reading geometric
   organization, not smooth position.
3. **On GOLDEN the signal is cleanly the ADDRESS (H_read).** Golden's increment (+0.031)
   is fully removed by the stratified address shuffle (residual −0.005) and survives the
   position control (+0.032). All three decision-rule conditions are met, in the
   pre-registered primary window. **On golden, a physical (coherent) law reads the
   perpendicular-space address, beyond degree, motif, and structure factor.**

For **platinum** the increment is larger (+0.089) and *mostly* address (86% removed by the
shuffle; residual +0.013). For **silver** it is large (+0.090) but only *partly* address
(71% removed; residual +0.026) — a substantial part of what the coherent wave reads on
silver is medium-scale structural organization not isolated to the address. So the strict
"killed by the shuffle" condition is met cleanly only by golden; platinum is close; silver
is ambiguous.

## The numbers (coherent primary window |E| ∈ [0.8, 2.5]; held-out CV, ± across folds)

| family | M3 R² | M4 R² | **M4−M3** | shuffle residual | +position residual | % of increment killed |
|---|---|---|---|---|---|---|
| golden (N=10)   | 0.867 | 0.898 | **+0.031** | **−0.005** | +0.032 | ~100% |
| platinum (N=12) | 0.758 | 0.846 | **+0.089** | +0.013 | +0.090 | ~86% |
| silver (N=8)    | 0.899 | 0.990 | **+0.090** | +0.026 | +0.091 | ~71% |

Incoherent null (return probability, t = 10), same rungs: M4−M3 = +0.002 (golden), +0.003
(platinum), +0.004 (silver); every one removed by the shuffle. The null reads no address.

Secondary window (E ≈ 0, confined/pseudogap): the M4 increment is *larger* everywhere
(golden +0.055, platinum +0.089, silver +0.197) and similarly shuffle-sensitive. This is
against my pre-registered expectation that E ≈ 0 would be motif-dominated and therefore
weaker — the confined-state window actually shows *more* readable address, not less. It is
the pre-committed **secondary** window, so it does not carry the claim, but it is a clean
mispredict worth recording (see §"what I got wrong").

## Reading of the ladder (coherent primary)

- **Degree (M0→M1)** does very different amounts of work per family: silver +0.83 (degree
  explains almost all of silver's coherent LDOS), golden +0.36, platinum +0.32. Silver's
  coherent response is degree-dominated — the same redundancy the static test found in
  silver's address.
- **Local motif (M1→M2)** and **local structure factor (M2→M3)** add the bulk of the rest.
- **Multiscale address (M3→M4)** is the residual channel this test was built to isolate.
  On golden it is small but *pure* (all address). On silver/platinum it is larger but
  *mixed* (address + medium-scale structure the shuffle preserves).

## Convergence with the static result (not predicted, worth noting)

Family ordering was **not** pre-registered (P4). But it is striking that **golden** — the
family the static test found carries the richest *degree-independent* address — is exactly
the family whose transport *cleanly* reads that address, while **silver** — whose static
address was largely degree-redundant — shows a coherent response that is degree-dominated
and whose M4 channel is only partly address. The static "what is encoded" and the dynamic
"what a law reads" line up on golden. Reported as convergence, not as a claimed hierarchy.

## What I got wrong (recorded honestly)

- **Energy window.** I overrode GPT and made the mid-band primary, predicting E ≈ 0 would
  be motif-dominated and weak. The data say the opposite: the E ≈ 0 window shows a *larger*
  address increment everywhere. My reasoning (confined states are motif-locked ⇒ small M4)
  was wrong — the confined-state region carries *more* multiscale-address signal, not less.
  The primary-window claim (golden) still stands on its own; but had I followed GPT the
  headline would have been stronger. Noted for calibration.
- **The stratified shuffle is not a full position control.** I recognised mid-run that the
  shuffle alone cannot separate "reads address organization" from "reads smooth position",
  and added the position control. It matters: it confirms the signal is not position, which
  the shuffle alone could not establish.

## Decision-rule outcome (per the sealed §10)

- **Golden:** claim met — coherent M4-over-M3 positive, killed by the stratified shuffle,
  not reproduced by the incoherent engine. **H_read on golden.**
- **Platinum:** positive and not reproduced by the incoherent engine; *mostly* killed by
  the shuffle. Reads multiscale geometry, largely address, not cleanly isolated.
- **Silver:** positive and not reproduced by the incoherent engine; only *partly* killed.
  Reads multiscale geometry, only partly address.
- **All three:** the coherent-vs-incoherent contrast is clean — a coherent law reads
  multiscale geometric organization that the incoherent law does not.

## Limitations (as sealed, plus what the run surfaced)

- Single patch per offset; bulk-restricted (r < 0.8 r_max); boundary not analysed here.
- M4's shell-averages evidently pick up some non-address medium-scale structure (the
  silver/platinum shuffle residual) — a cleaner M4 that is orthogonalized against M3 would
  sharpen the address attribution; a stage-two refinement, not a change to this run.
- Hard surrogate rungs (pair-correlation / Fourier-phase / angular-matched scrambles)
  remain stage-two. The clean rungs (motif, structure factor, stratified shuffle, position)
  are what this run establishes.

## Files

`transport_run.py` (harness) · sealed `PREREG_transport_hierarchy.md` · pilot
`wave_pilot.py` / `wave_pilot.png` · full console output in the run log.

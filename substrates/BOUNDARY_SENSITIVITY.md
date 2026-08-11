# The exo/endo gap is largely boundary contamination

Measured on the original v3 substrates, matched-rate labels (top 3% by
rank-averaged retention, so both arms carry identical positive rates), gradient
boosting on perpendicular-space address features, shuffle null beside every
point.

```
python3 boundary_sweep.py
```

| interior kept | AB active | AB AUC | Penrose active | Penrose AUC | gap |
|---|---|---|---|---|---|
| 90% | 20,397 | 0.9424 | 25,847 | 0.7473 | +0.195 |
| 75% | 16,997 | 0.9980 | 21,539 | 0.8234 | +0.175 |
| 60% | 13,598 | 0.9995 | 17,231 | 0.9492 | +0.050 |
| 50% | 11,332 | 0.9996 | 14,360 | 0.9837 | +0.016 |
| 40% | 9,065 | 0.9995 | 11,488 | 0.9802 | +0.019 |
| 30% | 6,799 | 0.9997 | 8,616 | 0.9738 | +0.026 |

Shuffle null runs 0.469–0.524 across all twelve cells.

## What this says

**Both substrates have near-perfect address channels in their bulk.** AB is
saturated at 0.999 from 75% interior inward. Penrose reaches 0.98 once trimmed to
50%. The published claim that Penrose fails to retain identity through
perpendicular space does not survive: in the bulk it retains it almost as well as
AB does.

**What actually differs is boundary sensitivity.** AB reaches bulk behaviour after
trimming 25% of the patch; Penrose needs roughly 50%. The v3 analysis was run at
interior-75%, which is inside AB's saturated regime and well outside Penrose's —
so the reported gap is measuring how far boundary contamination penetrates each
substrate, not whether each has an address channel.

Note that AB is boundary-sensitive too: it drops to 0.9424 at 90% interior. The
difference is depth of penetration, not presence versus absence.

## Effect on the headline result

The gap has narrowed under each successive correction:

| analysis | AB | Penrose | gap |
|---|---|---|---|
| v3 as published (linear, intersection label, 75%) | 0.986 | 0.661 | +0.325 |
| nonlinear model | 0.992 | 0.786 | +0.206 |
| matched positive rate | 0.998 | 0.823 | +0.175 |
| bulk (50% interior) | 0.9996 | 0.9837 | **+0.016** |

Each correction removed a confound and shrank the gap. At the bulk limit it is
+0.016, against shuffle nulls at 0.50. Whether a gap that size is real or is the
residue of some further unmatched variable is not settled by this run.

## The claim that survives

Not "AB has an exo-channel and Penrose does not". Rather: **Penrose's address
channel is markedly more vulnerable to boundary truncation than AB's**, requiring
about twice the trimming to reach bulk behaviour. That is a real, measured,
substrate-level difference, and it is interesting — a finite patch of Penrose
carries usable address information over a smaller fraction of its extent. But it
is a claim about finite-size effects, not about the intrinsic presence of an
address layer.

Any physical reading that depends on Penrose *lacking* perpendicular-space
addressability needs withdrawing.

## Caveats and next checks

- Measured with one label definition. The matched-rate composite should be
  cross-checked against at least one other privileged-site definition before
  this is treated as settled.
- Why Penrose is more boundary-sensitive is unmeasured. A plausible line is that
  its acceptance region is four separate pentagons indexed by lift sum, so
  truncation damages its address structure differently than AB's single octagon
  does — but that is a hypothesis, not a result.
- The phason dose-response in `PHASON_DOSE_RESPONSE.md` used interior-75% and the
  intersection label, so its gap of +0.19 to +0.26 carries both confounds
  identified here. It needs rerunning at bulk crop with matched rates before its
  conclusion — that the gap is constant under strain — can stand.

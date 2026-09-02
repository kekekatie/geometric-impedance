# Results — ablating the address block: WHICH neighbourhood feature carries the transport increment?

*ROADMAP step 5. EXPLORATORY / INTERPRETIVE — not a sealed, pre-registered study. Code:
`ablation_run.py`. Reproduce: `python ablation_run.py 8 10 12`. Reuses the sealed transport
pipeline (`transport_run.py`, the machinery behind `RESULTS_TRANSPORT.md` / Part II) verbatim —
same OFFSETS, same bulk mask (r < 0.8 r_max), same shared motif codebook + rng(0), same
HistGradientBoosting regressor, same leave-one-offset-out CV, same incoherent null. The ONLY
change is column selection inside the M4 block: we split the address features into their four
groups and re-run, either dropping one group (leave-one-out) or keeping only one (group-alone).
The harness asserts its rebuilt full-M4 equals the sealed M4 before doing anything, and the plain
M4-over-M3 increment reproduces the sealed numbers to the fourth decimal (golden +0.0310).*

The four groups (exactly the columns `transport_run._m4_cols` builds):

- **perp** — shell-averaged perpendicular-space coordinate at graph shells r = 2, 4, 8;
- **var** — within-shell perp *variance* at r = 2, 4, 8 (how much the address spreads across
  the neighbourhood, per scale);
- **grad** — local address-gradient magnitude (a least-squares perp slope over the r ≤ 3 patch);
- **depth** — hull depth (signed distance of the vertex's perp point to the boundary of the
  address point cloud).

## The numbers (coherent primary window |E| ∈ [0.8, 2.5]; held-out CV over 5 offsets)

**Sufficiency — how much of the increment each group reproduces ON ITS OWN (M3 + one group,
minus M3):**

| family | full M4−M3 | perp alone | **var alone** | grad alone | depth alone |
|---|---|---|---|---|---|
| golden (N=10)   | **+0.0310** | −0.0011 | **+0.0295** | +0.0141 | +0.0153 |
| silver (N=8)    | **+0.0905** | +0.0131 | **+0.0896** | +0.0832 | +0.0749 |
| platinum (N=12) | **+0.0885** | +0.0030 | **+0.0706** | +0.0199 | +0.0187 |

**Necessity — how much of the increment is LOST when each group is removed (full increment minus
the leave-one-out increment; a positive number means removing that group hurts):**

| family | perp | **var** | grad | depth |
|---|---|---|---|---|
| golden (N=10)   | −0.0034 | **+0.0115** | −0.0002 | +0.0026 |
| silver (N=8)    | −0.0004 | **+0.0047** | +0.0011 | +0.0007 |
| platinum (N=12) | −0.0016 | **+0.0428** | +0.0017 | +0.0152 |

**Internal null control (incoherent return prob, t = 10; same M4 columns).** Every group, every
family, reads ≈0: the largest group-alone increment anywhere in the null is +0.0036 (silver var),
and every leave-one-out drop is within ±0.002 of zero. The address groups predict nothing for the
memoryless walker — so the coherent numbers above are a real coherent-specific signal, not an
artefact of adding feature columns.

## What this says (three readings, all robust across the families)

1. **The address MEAN carries essentially none of the transport increment — in any family.**
   `perp alone` adds −0.001 / +0.013 / +0.003, and removing perp never hurts (its "necessity"
   is ≤0 everywhere; the shell-mean columns are so redundant with M3 that dropping them very
   slightly *helps*). Where the neighbourhood sits in perpendicular space is already contained
   in the local physical/motif descriptors. This is the transport-side echo of the address-split
   result, where the vertex's own *angular* position added ≈0: it is not *where* the address is
   that a coherent law reads.

2. **The within-shell VARIANCE is the consistent carrier.** `var alone` reproduces the bulk of
   the increment in every family — 95% on golden (+0.0295 of +0.0310), 99% on silver, 80% on
   platinum — and it is the group whose removal costs the most (golden +0.0115, platinum +0.0428).
   What a coherent wave reads is not the address position but **how much the address spreads
   across the local neighbourhood, across scales** — its multiscale heterogeneity.

3. **Gradient and hull-depth are secondary and largely redundant.** Each adds a little alone
   (~+0.014–0.020 on golden/platinum, more on silver), but once variance is present, removing
   either costs almost nothing — except **hull-depth on platinum** (necessity +0.0152), the one
   place a boundary-distance term is doing independent work.

## Necessity vs sufficiency differs by family — and it tracks the transport story

The leave-one-out drops do **not** sum to the full increment: the groups are partly redundant, so
several can stand in for one another. How redundant depends on the family, exactly as
`RESULTS_TRANSPORT.md` would predict:

- **Golden — clean.** Variance is both the most sufficient group (95% alone) and the one whose
  loss hurts most; the mean is pure redundancy. This is the family whose transport signal was
  the *purest* address (killed cleanly by the stratified shuffle), and the ablation localises
  that pure signal to one interpretable quantity: multiscale address variance.
- **Platinum — variance is load-bearing.** Variance alone gives 80% and its removal costs ~half
  the increment (+0.0428) — the clearest necessity signal of the three — with hull-depth carrying
  a genuine second bit.
- **Silver — redundant / distributed.** var, grad and depth each recover most of the increment
  alone, yet no single group is *necessary* (every removal costs ≤+0.005). Silver's coherent
  response is degree-dominated and, per the transport run, only *partly* address; the ablation
  shows why the shuffle-residual was largest there — the signal is smeared across several
  medium-scale re-encodings rather than isolated in one.

## Reconciliation with the other diagnostics (consistent; it sharpens, does not overturn)

- **Residualization (step 1, `RESULTS_RESIDUALIZE.md`).** That step found the address's value
  lives in the part *shared with* M3, not an orthogonal channel. Consistent: within-shell perp
  variance is precisely a multiscale re-encoding of local structural heterogeneity — organised,
  transport-aligned, and correlated with the local descriptors — not a hidden orthogonal
  coordinate.
- **Address-split (`RESULTS_ADDRESS_SPLIT.md`).** There, the neighbourhood block (shell-mean +
  variance + gradient) beat radial depth and own-angular-position (≈0). This ablation says which
  part of that neighbourhood block does the work for *transport*: the variance, not the mean.
- **Language discipline (ROADMAP rule 6).** Nothing here says "perpendicular space is physical."
  The safe statement holds and is now more specific: *the transport-relevant address information
  is the multiscale within-neighbourhood variance of the perpendicular-space coordinate — an
  organisation of local structure, not the vertex's own address position.*

## Caveats

- **Exploratory / interpretive**, run after the sealed result to dissect a confirmed increment;
  it is not itself pre-registered, and no claim is promoted on its basis. The trustworthy
  headline remains the plain, four-times-controlled M4-over-M3 increment from
  `RESULTS_TRANSPORT.md`.
- **Redundancy makes single-group attributions non-unique.** Sufficiency (group-alone) and
  necessity (leave-one-out) are reported precisely *because* they can disagree under redundancy;
  the honest summary is "variance is the most sufficient everywhere and the most necessary where
  anything is necessary", not "variance is the sole cause".
- **Groups are correlated by construction** (shell-mean, its variance, its gradient and the hull
  depth are all functions of the same perp field), so leave-one-out understates a group's
  standalone content and group-alone overstates its marginal content; the two columns bracket it.
- Coherent primary window only (the secondary E ≈ 0 window and silver/platinum sharpening are
  left as-is); single patch per offset; bulk-restricted; same limitations as the sealed run.

## Files

`ablation_run.py` (reuses `transport_run.py` verbatim) · follows `RESULTS_TRANSPORT.md`,
`RESULTS_RESIDUALIZE.md`, `RESULTS_ADDRESS_SPLIT.md`; ROADMAP step 5.

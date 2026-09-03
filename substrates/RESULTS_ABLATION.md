# Results — ablating the address block: is the perp-variance signal address-specific, or a physical-spread proxy?

*ROADMAP step 5. EXPLORATORY / INTERPRETIVE — not a sealed, pre-registered study. Code:
`ablation_run.py` (reuses `transport_run.py`, the machinery behind `RESULTS_TRANSPORT.md` /
Part II, verbatim). Reproduce: `python ablation_run.py 8 10 12`. Same OFFSETS, bulk mask
(r < 0.8 r_max), shared motif codebook + rng(0), HistGradientBoosting regressor and
leave-one-offset-out CV as the sealed run. The harness checks its rebuilt full-M4 against the
sealed M4 with `np.array_equal` plus explicit width/column-order asserts, and runs an EXECUTABLE
reproduction check on the plain M4-over-M3 increment (all three families PASS: golden +0.0310,
silver +0.0905, platinum +0.0885 in this environment).*

**Environment (recorded for reproducibility).** python 3.11.15 · numpy 2.4.6 · scipy 1.17.1 ·
scikit-learn 1.9.0. HistGradientBoosting is mildly version-sensitive: an independent audit
environment (GPT/Sol) saw ~+0.0008 fourth-decimal drift on golden's increment. Exact agreement is
therefore expected only to ~3 decimals across environments; comparisons below are read at that
resolution, and the small golden remainder is discussed against that drift in "On scale".

> **Why this file was revised.** The first version of this result concluded "the within-shell
> variance is the carrier." An independent audit (GPT/Sol, appended below) showed that conclusion
> was under-controlled: perp variance is only one within-ball *spread* among many, and the fair
> test is whether it predicts transport beyond the same within-ball spread of ordinary physical
> fields. **Part A (the original group ablation) is preserved unchanged; Part B (the
> physical-spread control) is added; the conclusion is corrected to a family-qualified
> proxy/absorption statement.** This revision's Part B numbers are, additionally, a cross-engine
> *replication* of Sol's independently-computed residuals.

The four address groups (exactly the columns `transport_run._m4_cols` builds):

- **perp** — shell-averaged perpendicular-space coordinate (the address MEAN) at graph shells
  r = 2, 4, 8;
- **var** — within-shell perp *variance* at r = 2, 4, 8;
- **grad** — local address-gradient magnitude (least-squares perp slope over the r ≤ 3 patch);
- **depth** — hull depth (signed distance of the vertex's perp point to the address-cloud boundary).

---

## Part A — group ablation (unchanged from the first run)

Coherent primary window |E| ∈ [0.8, 2.5]; held-out CV over 5 offsets.

**Sufficiency — increment each group reproduces ON ITS OWN (M3 + one group, minus M3):**

| family | full M4−M3 | perp (mean) alone | var alone | grad alone | depth alone |
|---|---|---|---|---|---|
| golden (N=10)   | +0.0310 | −0.0011 | +0.0295 | +0.0141 | +0.0153 |
| silver (N=8)    | +0.0905 | +0.0131 | +0.0896 | +0.0832 | +0.0749 |
| platinum (N=12) | +0.0885 | +0.0030 | +0.0706 | +0.0199 | +0.0187 |

**Necessity — increment LOST when each group is removed (full minus leave-one-out; positive =
removal hurts):**

| family | perp | var | grad | depth |
|---|---|---|---|---|
| golden (N=10)   | −0.0034 | +0.0115 | −0.0002 | +0.0026 |
| silver (N=8)    | −0.0004 | +0.0047 | +0.0011 | +0.0007 |
| platinum (N=12) | −0.0016 | +0.0428 | +0.0017 | +0.0152 |

Two things from Part A survive the audit and are worth keeping:

- **The address MEAN carries essentially none of the increment in any family** (perp-alone
  −0.001 / +0.013 / +0.003; removing it never hurts). The transport-side echo of the
  address-split result's "own angular position adds ≈0".
- **Among the four groups, perp variance is the strongest-performing M4 subgroup *before*
  physical-spread enrichment** — highest alone and most costly to remove. That is a statement
  about *which column of M4 does the work*, and Part B is what it takes to ask whether that work
  is *address-specific* at all.

---

## Part B — the physical-spread control (from Sol's audit)

The `var` columns measure how much the perp field spreads across each graph-radius ball. But any
field spreads across those balls. So we build **physical-spread** controls over the SAME
graph-radius 2/4/8 balls and ask what perp variance (and full M4) still add on top:

- **control (a)** — degree variance alone (per-ball variance of degree);
- **control (b)** — per-ball variances of degree, density, g(1.6), g(2.6), g(4), g(6) (the full
  physical-spread block, 18 columns).

Reported as **paired leave-one-offset-out fold increments** (mean over the 5 folds; we also record
whether every individual fold is positive — a stronger statement than a positive mean).

| increment (coherent primary) | golden | silver | platinum |
|---|---|---|---|
| perp-var **over M3** | +0.0295 (all folds +) | +0.0896 (all +) | +0.0706 (all +) |
| phys-spread (a: degree-var) **over M3** | +0.0235 (all +) | +0.0917 (all +) | +0.0561 (all +) |
| phys-spread (b: full) **over M3** | +0.0391 (all +) | +0.0939 (all +) | +0.0868 (all +) |
| **perp-var over (M3 + phys-spread b)** | **+0.0056 (all 5 +)** | **+0.0002 (≈0)** | **+0.0171 (all 5 +)** |
| **full-M4 over (M3 + phys-spread b)** | **+0.0081 (all 5 +)** | **−0.0002 (≈0)** | **+0.0218 (all 5 +)** |

**Internal null control (incoherent walker, t = 10, same columns).** Physical spread itself
predicts a little for the memoryless walker (b-over-M3 ≈ +0.004 / +0.004 / +0.009) — unsurprising,
physical structure predicts return probability. But the quantity that matters here, **perp-var over
(M3 + phys-spread b), is ≈0 or negative in the null for every family** (golden −0.0009, 0/5 folds
positive; silver −0.0000; platinum +0.0003, 3/5). So where a coherent remainder survives
(golden, platinum) it is coherent-specific, not a feature-count artefact.

**Cross-engine replication.** This engine's residuals land on Sol's independently-computed values:
golden +0.0056 / +0.0081 (Sol ~+0.0060 / +0.0085), platinum +0.0171 / +0.0218 (Sol ~+0.0173 /
+0.0217), silver +0.0002 / −0.0002 (Sol ~0, fully absorbed) — every value within ~0.0004, inside
the version-drift band, and with the same all-folds-positive pattern on golden and platinum. Two
independent implementations agree on a control that neither could compute blind.

## What it means (corrected: a family-qualified proxy/absorption statement)

The headline change: **most of the perp-variance transport signal is a proxy for ordinary
real-space within-neighbourhood spread, not an address-specific quantity.** Even *degree variance
alone* over the same balls (control a) absorbs the bulk of it, and the full physical-spread block
absorbs more of it than perp variance ever explained on its own. What survives, once physical
spread is accounted for, is family-dependent:

- **Silver — fully absorbed.** Perp variance adds nothing over physical spread (+0.0002), and the
  full M4 nothing (−0.0002). Silver's Part-A "carrier" reading was entirely proxy: its coherent
  response is degree-dominated, and the within-ball spread it reads is real-space, not perp-space.
- **Golden — mostly absorbed, small genuine remainder.** A perpendicular-specific increment of
  +0.0056 (perp-var) / +0.0081 (full M4) survives, positive on all five folds and null-negative
  incoherently. Real within this environment, but small (see "On scale").
- **Platinum — partly absorbed, moderate genuine remainder.** +0.0171 / +0.0218 survive, all five
  folds positive — the most robust perpendicular-specific residual of the three.

So the honest one-line replacement for "variance is the carrier" is: *perp variance is the
strongest-performing M4 subgroup before physical-spread enrichment, but it is largely a proxy for
real-space neighbourhood spread; a genuine perpendicular-specific remainder survives only on golden
(small) and platinum (moderate), and not at all on silver.*

## On scale (why the golden remainder is not this run's to adjudicate)

Golden's surviving remainder (+0.0056) is roughly seven times the ~+0.0008 cross-environment
version drift — real *within* an environment, but close enough to the noise floor of the tooling
that it should not be leaned on by an exploratory run. Adjudicating an effect that small belongs to
the **sealed ladder**, with its recorded environment and capacity floors, not to a post-hoc
dissection. Platinum's remainder (+0.017–0.022) is an order of magnitude above the drift and is
correspondingly safer to state. This paragraph is here so a future reader who notices the drift
first, and the residual second, sees that we noticed too.

## Reconciliation with the other diagnostics (softened)

- **Residualization (`RESULTS_RESIDUALIZE.md`).** That step already found the address's value lives
  in the part *shared with* M3, not an orthogonal channel. Part B sharpens the same story with a
  concrete stand-in: the shared part is largely real-space neighbourhood spread; only a small
  family-dependent sliver is not.
- **Address-split (`RESULTS_ADDRESS_SPLIT.md`).** The neighbourhood block still beats radial depth
  and own-angular-position for *confined weight*; Part B only re-attributes how much of the
  *transport* increment is perpendicular-specific once physical spread is controlled.
- **Language discipline (ROADMAP rules 6–7).** The earlier draft's "a coherent wave reads the
  multiscale variance of the address" over-reached. The controlled statement is weaker and
  observational: *a coherent observable is associated with within-neighbourhood spread over
  graph-radius balls; most of that is real-space spread, with a small perpendicular-specific
  remainder on golden and platinum only.* No claim that perpendicular space is physical; no
  "phase-memory of the journey" mechanism.

## Caveats

- **Exploratory / interpretive**, run after the sealed result to dissect a confirmed increment; no
  claim is promoted on its basis. The trustworthy headline remains the plain, four-times-controlled
  M4-over-M3 increment from `RESULTS_TRANSPORT.md`.
- **The physical-spread block is one finite basis**, not an exhaustive account of real-space
  organization; a richer physical spread could absorb still more of the golden/platinum remainder.
  The residuals are therefore upper bounds on "address-specific" content, not lower bounds.
- Coherent primary window only; single patch per offset; bulk-restricted; same limitations as the
  sealed run.

## Files

`ablation_run.py` (reuses `transport_run.py` verbatim) · follows `RESULTS_TRANSPORT.md`,
`RESULTS_RESIDUALIZE.md`, `RESULTS_ADDRESS_SPLIT.md`; ROADMAP step 5.

---

## Appendix — independent audit note (GPT/Sol, 2026-09)

*Recorded verbatim in substance, as the audit that corrected this file. Sol reviewed the first
version's "variance is the carrier" conclusion and found it under-controlled.*

- **The gap.** The M4 `var` columns measure within-ball spread of the perp field, but within-ball
  spread is a generic property of any field over those balls. Attributing the transport increment
  to "perp variance" without a physical-spread control confounds address-specific structure with
  ordinary real-space heterogeneity.
- **The control (specified by Sol, implemented here exactly).** Over the same graph-radius 2/4/8
  balls: (a) degree variance alone; (b) per-ball variances of degree, density, g(1.6), g(2.6),
  g(4), g(6). Report paired leave-one-offset-out fold increments for M3, perp-variance,
  physical-spread, perp-variance over physical-spread, and full-M4 over physical-spread.
- **Sol's residuals (independently computed).** Silver essentially fully absorbed; golden retains
  ≈ +0.0060 (perp-var) and ≈ +0.0085 (full M4); platinum ≈ +0.0173 and ≈ +0.0217, with all five
  residual folds positive. This engine's rerun reproduces those values within ~0.0004 (see
  "Cross-engine replication").
- **Governance.** Exploratory science of this kind is kept off the sealed clean-room line; this
  result lives on an `exploratory/…` branch and is not a merge candidate into the clean-room
  branch. Small residuals like golden's are for the sealed ladder to adjudicate, not an exploratory
  dissection.

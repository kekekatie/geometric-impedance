# Report v11 — substrate pilot: regular Penrose vs perturbed pentagrid

*Plain-language write-up, written after the run. Register: speculative exploration;
not a confirmatory study, not cosmology. All gates passed (repaired construction +
engine equivalence); design frozen in `DESIGN_NOTE_v11.md`. Reproduce:
`python v11_validate.py && python v11_experiment.py && python v11_analyze.py`
(~50 min). Family comparisons are exploratory and conditional on the selected
geometries.*

## Question

Does quasiperiodic spatial organisation change the persistence of history-readable
footprints under local reinforcement and connection growth, compared with a
perturbed (same-tile) substrate?

## Answer — no detectable difference; both substrates retain history comparably

Ordinary fixed-orientation AUC (history A vs B), arm mean ± across-patch sd:

| step | regular (Penrose) | perturbed pentagrid | no-history null |
|---|---|---|---|
| 100 | 0.678 | 0.696 | ~0.50 |
| 200 | 0.686 | 0.691 | ~0.50 |
| 400 | 0.686 | 0.674 | ~0.50 |
| 1000 | 0.645 | 0.644 | ~0.50 |
| **2000 (primary)** | **0.616** | **0.624** | 0.469 / 0.484 |
| 5000 | 0.577 | 0.584 | ~0.50 |
| 10000 | 0.553 | 0.563 | ~0.49 |

At the pre-registered primary checkpoint t=2000, regular Penrose scores 0.616
(patches 0.616 / 0.595 / 0.638; sd 0.022) and perturbed 0.624 (0.593 / 0.631 /
0.647; sd 0.027). **The between-arm difference (0.008) is far smaller than the
across-patch spread within each arm (~0.02–0.03)**, and the two curves overlap at
every checkpoint (see `figures/memory_v11.png`). Both arms discriminate history well
above the no-history null (~0.47–0.50), which confirms the signal is real and not a
reader/substrate artefact. Memory peaks early (~0.69 at t=100–200) and decays toward
~0.55 by t=10000 in both arms — the familiar erosion-with-saturation seen on the
square grid, not yet reaching the null.

**Opportunity and capacity are likewise near-identical** between arms
(`figures/opportunity_v11.png`, `results/summary_opportunity.csv`): activation
fraction (→0.86 vs 0.85 at t=10000), headroom (→1.58 vs 1.62), structural access
(→116.6 vs 117.2), effective alternatives (→3865 vs 4038, perturbed ~4% higher),
and boundary-visitation fraction (→0.091 vs 0.095) all track together.

**So, within this bounded comparison, quasiperiodic organisation does not detectably
change memory persistence or opportunity.** We did not assume it would help; it does
not detectably help or hurt here.

## What passed before any of this was believed

All construction/engine gates passed (`results/gate_report.txt`): six R=10 patches
validate under the *repaired* geometry checks (real overlap/gap tests, with
deliberately-invalid fixtures rejected); zero degeneracies from the robust
strip-index construction; candidate diagonals unique and distinct from originals;
the three regular patches are not rigid-motion duplicates; three length-6 history
pairs per patch; and — critically — the substrate-general engine is **event-by-event
identical to the validated v2 square engine** over history + 300 steps.

## Limitations (these bound the claim tightly)

- **"Perturbed" is not "disordered."** The perturbed arm (jitter amplitude 0.30,
  same two rhombi) is **not established** to lack long-range order — bounded jitter
  may leave quasiperiodic order largely intact. So this is essentially *Penrose vs
  mildly-perturbed-Penrose*, two **similar** substrates; their behaving similarly is
  not strong evidence about genuine periodic or disordered substrates. A diffraction/
  structure-factor test (deferred) would be needed to call the second arm disordered.
- **Local geometry is not matched and not controlled.** Degree distributions, tile
  frequencies, history geometry, and boundaries all differ between arms; this pilot
  does **not** isolate higher-order organisation from local geometry.
- **A null difference is not proof of equivalence.** With 3 patches per arm and
  overlapping spreads, we report "no detectable difference," not "identical."
- **Boundaries are reached.** ~9% of steps land on boundary vertices by t=10000
  (hard truncation, no rim down-weighting); interior start does not prevent this.
- **Global, coordinate-aided reader.** The reader shows a distinction is present in
  the structure; it does **not** show a walker can locally access or transmit it
  (Katie's accessible/pass-on-able memory question — a future local-reader extension,
  not implemented).
- Family comparisons are exploratory and conditional on these specific geometries;
  parameters were not tuned to memory scores.

## One worthwhile next question

The sharp contrast this pilot brackets but does not make is **quasiperiodic vs a
substrate whose order class is genuinely different** — a Fibonacci-approximant
**periodic** patch (same two rhombi, deferred v10/v12 construction) and/or a
**verified disordered** patch (perturbation strong enough that a diffraction test
confirms loss of long-range order). Running the identical frozen reader and pipeline
across *those* order classes — rather than Penrose vs a mild perturbation of Penrose
— is the test that would actually answer whether the *class* of spatial order
matters. Pair it, eventually, with a **local (walker-accessible) reader** to address
whether any such memory is usable rather than merely present.

---

## Clarifications — 2026-09-07 (v12 review; numbers above unchanged)

1. **The similar arm performance is a *descriptive* result, not a test.** Comparing
   the between-arm mean difference against the across-patch SD, or noting overlapping
   bands, is **not** a formal hypothesis test and **not** an equivalence
   demonstration. The honest statement is: on these six patches, the observed regular
   and perturbed memory curves are close and we did not find a difference; we make no
   claim that they are equal.
2. **This is regular vs *perturbed* pentagrid — not established distinct order
   classes.** The perturbed arm is not shown to be periodic or disordered, so the
   comparison does not span order classes.
3. **The random-label no-history null is a sanity check, not a proof.** It sitting at
   chance is consistent with the reader not manufacturing signal from static
   structure, but it does **not** prove all reader/substrate artefacts are absent.
4. **Actual null protocol (as implemented).** One no-history Growing trajectory per
   (seed, patch), **reused across all three of that patch's pair-readers**, with A/B
   labels assigned **in analysis** by a random coin (independent of dynamics). This
   differs from the originally proposed **two-run** protocol (two independent
   no-history runs per seed, forming a within-seed A/B pair): the implemented version
   is an *unpaired random-label* null and its three per-patch pair-nulls are
   correlated (shared trajectory). Both are expected to sit at chance; the implemented
   one is cheaper and is what the numbers above use.

### Conditional matched-offset contrasts at t=2000 (existing data; `../v12_local_reader_design/`)

Per matched offset i (regular#i vs perturbed#i share a base offset); patch memory =
AUC averaged over 3 pairs; contrast = perturbed − regular. Interval = bootstrap over
the 200 seed indices applied **identically to every cell** (preserving common-random-
number dependence across cells and arms), with the **six patches held fixed** — so it
is *simulation uncertainty conditional on these patches*, not generalisation beyond
three patch pairs.

| offset | regular AUC | perturbed AUC | contrast (pert−reg) [95% seed-bootstrap] |
|---|---|---|---|
| 0 | 0.616 | 0.593 | **−0.022 [−0.069, +0.025]** |
| 1 | 0.595 | 0.631 | **+0.036 [−0.010, +0.080]** |
| 2 | 0.638 | 0.647 | **+0.008 [−0.035, +0.053]** |
| **mean** | — | — | **+0.007 [−0.018, +0.032]** |

Every interval includes 0 and the sign is inconsistent across offsets; conditional on
these six patches there is no matched-offset difference. This does not generalise to
other patches (only three pairs) and is not an equivalence claim.

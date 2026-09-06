# Feasibility verdict (v10)

**Verdict: the two-arm construction and the frozen reader are feasible and
validated. Proceed to the substrate memory experiment (v11) with the two-family
core (regular Penrose vs perturbed pentagrid), at patch radius ≈ 10. Defer the
periodic approximant to a separate scoped construction.**

## What was built and passed (this task)

- **de Bruijn pentagrid generator** (`substrate_lib.py`), regular + perturbed arms,
  self-contained, source-backed (de Bruijn 1981).
- **6 patches** (3 regular, 3 perturbed, R=6) — **all pass full geometric +
  topological validation** (unit sides, permitted rhombus shapes, face areas &
  orientation, edge incidence, connectedness, boundary loops, Euler V−E+F=1,
  area-sum = enclosed area, no duplicate faces). See `results/validation_full.txt`.
- **Labelled images**: `figures/patches_v10.png` (regular Penrose vs perturbed;
  the regular patch shows the expected 5-fold rosettes), `figures/reader_v10.png`
  (paths A/B and reader-sign-coloured diagonals).
- **Diagnostics** (`results/patch_diagnostics.csv`): V/E/F, thick/thin (ratio
  1.82–2.14, finite-patch, not φ), **degree distributions that differ between arms**
  (documented: same tiles ≠ identical local geometry), boundary metrics.
- **Executable histories + frozen reader**; **reader sanity** across all 18
  patch×pair cells (`results/reader_sanity.csv`): **sign-swap flips coefficients
  everywhere**; +/−/0 counts and **generally-nonzero saturated values** reported.
- **Tiny smoke fixture** (`results/smoke_fixture.txt`): the substrate-general engine
  runs on a pentagrid patch, growth triggers on rhombus faces, the reader returns
  numbers, and the "bit starts empty after history" property holds. **Not** a
  production run (60 steps, 2 seeds, one patch).

## Recomputed runtime & storage (eventual v11 experiment)

Budget = 2 arms × 3 patches × 3 history-pairs = **18 cells**; per cell 2 histories ×
200 seeds × 10,000 steps.

| Component | Steps | Est. time @ ~1e5 steps/s |
|---|---|---|
| Growing (memory) | 18 × 2 × 200 × 1e4 = 72M | ~12 min |
| No-history Growing null (2 runs/seed) | 18 × 2 × 200 × 1e4 = 72M | ~12 min |
| Fixed plumbing | negligible (no growth) | ~0 |
| **Total dynamics** | | **~25–30 min** |

Construction + validation for all patches: < 10 s. Snapshots (scalars per
checkpoint: both readers, n_active, n_high, headroom, total_weight) ≈ **< 10 MB**;
optional full per-edge vectors sub-sampled to a few seeds. **Comfortably within a
session.**

## Key feasibility findings / caveats

1. **Geometry is sound.** The generator produces genuine Penrose tilings (regular
   arm) and same-tile perturbed tilings, all validating.
2. **"Perturbed" ≠ "disordered."** Not claimed; would need a diffraction argument
   (deferred). Naming kept honest.
3. **Local geometry is not matched across arms.** Degree distributions and tile
   frequencies differ — a genuine confound. The same-generator design minimises but
   cannot erase it; report degree distributions alongside any result.
4. **Boundary contact is significant at small R.** Median interior→boundary distance
   is 2 at R=6 and ~4 at R=10; over 10,000 steps the walk contacts boundaries
   throughout. Use R≈10, keep hard boundaries (no rim down-weighting), report the
   boundary-distance distribution, and treat boundary effects as a limitation.
5. **Reader is well-behaved but reads only near the histories.** Most candidate
   diagonals are equidistant from both paths → coefficient 0; discrimination lives in
   the red/blue lobes flanking A and B. Saturated value is generally nonzero on
   asymmetric patches (expected).
6. **Regular patch multiplicity.** Two of the three chosen offset vectors happened to
   yield equal V/E/F/degree (though different histories); for v11, pick offset
   vectors verified to give combinatorially distinct patches (a minor tunable).

## Unresolved choices carried to v11 (for Astra)

- Patch radius (recommend R=10, ~366 V) vs a larger R for more interior.
- Whether to include the Reinforced arm (needs the original-edge reader).
- Final offset set for 3 genuinely distinct regular patches.
- Whether to add the periodic approximant now (separate construction + gates) or
  keep the two-family core for v11 and add periodic in v12.
- History length window (pilot used 6; longer paths give larger red/blue lobes but
  fewer eligible pairs in a small patch).

## Stopping point

**Stopped before any production memory trajectory, as instructed.** Awaiting Astra's
review of this concrete construction + reader before running v11.

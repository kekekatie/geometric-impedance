# Accretion pilot v10 — pentagrid construction & reader feasibility

**Construction & feasibility implementation. No production dynamics run** (one tiny
smoke fixture only). Builds and validates the substrate patches and the frozen
reader for the eventual quasiperiodic-vs-perturbed memory experiment, then stops for
Astra's review.

> Isolated; chain v1 `cc514ee` → … → v9 `740b8cd`. v1–v9 preserved. No merging,
> publishing, or sealed-study access; self-contained geometry (de Bruijn pentagrid),
> no sealed tiling code used.

## Contents

- [`substrate_lib.py`](substrate_lib.py) — de Bruijn pentagrid generator (regular +
  perturbed), `Substrate`, geometric+topological `validate()`, deterministic
  geometry-only histories, the frozen proximity-sign reader, and a minimal
  substrate-general engine (`SubstrateWorld`) used only by the smoke fixture.
- [`v10_build.py`](v10_build.py) — builds 3 regular + 3 perturbed patches, validates
  all, writes diagnostics + reader sanity, renders images, runs the tiny smoke.
- [`DESIGN_NOTE_v10.md`](DESIGN_NOTE_v10.md) — corrected design: sources, construction
  spec, validation, histories/reader, controls & baselines, the frozen analysis plan
  (preregistered t=2000, two-level uncertainty, budgets), and Katie's
  accessible/pass-on-able memory question logged as a future local-reader extension.
- [`FEASIBILITY_VERDICT.md`](FEASIBILITY_VERDICT.md) — the specific verdict, recomputed
  runtime/storage, caveats, and unresolved v11 choices.
- `results/` — `patch_diagnostics.csv`, `reader_sanity.csv`, `validation_full.txt`,
  `smoke_fixture.txt`, `config.json`.
- `figures/` — `patches_v10.png` (regular Penrose vs perturbed), `reader_v10.png`
  (histories + reader signs).

## Reproduce

```bash
python v10_build.py     # ~5 s: build, validate, diagnostics, images, tiny smoke
```

## Headline

The de Bruijn pentagrid generator produces **genuine Penrose patches** (regular arm)
and **same-tile perturbed patches**, all passing **full geometric + topological
validation**. The deterministic geometry-only histories and the **frozen
proximity-sign reader** are executable and sane (**sign-swap flips coefficients on
all 18 patch×pair cells**; saturated reader value generally nonzero on asymmetric
patches, as expected). A tiny smoke confirms the substrate-general engine runs and
the reader returns numbers. **Verdict: feasible** — proceed to the v11 two-family
memory experiment at patch radius ≈ 10 (dynamics ≈ 25–30 min, snapshots < 10 MB),
keeping "perturbed" (not "disordered"), reporting degree distributions and boundary
contact as caveats, with the periodic approximant deferred to a scoped construction.

**Nothing beyond the tiny fixture was run.** Awaiting review.

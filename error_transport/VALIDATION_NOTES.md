# Construction & validation notes (post design-seal; no transport run)

## Finding 1 — the naive wrap-a-cell torus is NOT edge-completable (real phason wall)

The §7.1 combinatorial edge-completeness gate was applied to the existing
`torus_holonomy.build_torus` construction (ideal-QC vertices in one class-preserving
cell, edges wrapped across the seam). Result:

- **Penrose (order 2, N=273): 25 native neighbours (~2.3%) do not wrap onto any
  node.** Invariant to patch size (checked radius margins 6/10/16 — identical),
  so it is **not** a finite-patch artefact.
- The unmatched wrapped positions sit **0.382–0.618** from the nearest node
  (median 0.618 = the Penrose **thin-rhombus short diagonal**; 0.382 = its square).
  These are not rounding/gauge errors (none < 0.05) — they are **genuine
  rhombus-diagonal offsets**.
- **Interpretation:** the class-preserving *cut-and-wrap* torus has a **frozen
  phason wall** at the seam — the ideal quasicrystal does not tile itself perfectly
  under the period, so ~2.3% of native edges (Penrose; ~0.3% AB) fail to close as
  legitimate unit stars. This is a real feature of the construction, exactly the
  kind of thing the §7.1 gate exists to catch — and it means **this construction
  cannot pass the gate** ("all edges legitimate unit stars; zero dropped wraps").

## Proposed resolution — use the seamless phason-shear approximant, wrapped

The project already has a **seamless** periodic construction: the **phason-shear
approximant** (`approximant/phason_shear.py`, e0c-validated). It keeps **ideal
parallel positions** (so every edge is an exact unit star) and shears the
*acceptance* so the accepted set is **exactly period-periodic** — i.e. no phason
wall. As used in e0c it is built on an *open* patch (has a boundary); for this
experiment we wrap **that** seamless tiling into a torus by the exact period
lattice. Because its acceptance is exactly S-periodic, the wrap should be **exact
(zero dropped edges)** — genuinely edge-complete, every edge a unit star, winding
well-defined.

This is a **construction-design choice** (which torus): the sealed §4.A/§4.B assumed
the cut-and-wrap torus; the phason-shear-wrapped torus is the edge-completeable
alternative. Flagged for the three-way review before rebuilding on it.

## Next (pending confirmation of the construction choice)
1. Build the phason-shear-wrapped native tori (AB, Penrose); run the §7.1
   combinatorial gate; confirm zero dropped wraps + all §7.1 checks.
2. Build the oblique-Z² periodic controls (§4.C) + validate.
3. Test the bounded-local-rewire cutoff ladder (§4.D) — construction diagnostics.
4. Return all validation results. (Still: no pilot, no walkers, no transport.)

*Reported as a validation result under the design seal. No inference run.*

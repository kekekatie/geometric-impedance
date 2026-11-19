# Aperiodic–QEC geometry pilot

One command from the repository root (Python 3, NumPy and Matplotlib):

```sh
python3 exploratory/aperiodic_qec_geometry_2026-11-19/pilot.py
```

This reruns the frozen geometry-only search, writes the three selected patches, independently certifies them, and draws three labelled PNGs and the side-by-side PNG/SVG. No decoder is run. Output defaults to this directory's `results/`; use `--out PATH` for another directory. Tested environment: CPython 3.12.16, NumPy 2.2.6, Matplotlib 3.10.6. On Windows, use `python` if `python3` is not registered.

For saved-data verification alone:

```sh
python3 exploratory/aperiodic_qec_geometry_2026-11-19/certify.py
```

## Sources and provenance

* Branch base and inspected paired-cap audit: `7e40b4e9457bac8e08c3700f513ed7867717bb8c`, `exploratory/reconsideration_witness/pass2_audit_2026-11-17/`.
* Inspected corrected QEC landmark: `09a79c1d8d082702c93e1cd6b9f4a45d3df4d729`, `exploratory/reconsideration_witness/correction_2026-11-14/src/model.py` and `PROTOCOL_AMENDMENT.md`. This pilot adopts its two-earlier-round query bookkeeping, not its rotated-square stabilizers or decoder. The new control has edge qubits like the aperiodic patches.
* AB: `49bccf218dda4a84b704a9b1c1aaf0a732443786`, branch `claude/giv-quasicrystal-phason-5syx5s`, `substrates/generate_ab.py`, exact Git blob `37fbbab0028091159eb7db5872239d1c40e07bae`. The unchanged source is vendored. The pilot extracts unit lifted rhombi from its accepted vertices; local embedding and parent-neighbourhood checks are added here.
* Penrose P3: `exploratory/accretion_pilot/penrose_address_environment/penrose_address.py` at the base commit, last source-changing commit `7ddcb9b35ac7b86fe0fe79630fa7da0bb06becf2`, blob `739d69ee7e3269700093db4fe8439417de9d51f8`. Uses its integer pentagrid face cycles directly. Its support import is `exploratory/accretion_pilot/fibonacci_address_environment/fibonacci_cutproject.py`; no Fibonacci experiment is executed. The earlier float-deduplicated `v10_construction/substrate_lib.py` and the older branch's `substrates/generate_penrose.py` were inspected but are not used.
* Later manuscript branch `claude/distance5-feasibility-2026-11-16` at `6d0dc09644119292a768700862772145092f9a24` was inspected to establish context, not imported.
* Frozen local search protocol commit: `cbce124b645cb2e04b423e456ff9920af0334d11`, before any candidate selection.

No original tiling or QEC files are edited.

## Conventions and files

`square.json`, `AB.json`, `Penrose.json` contain stable lift-sorted vertex/edge IDs, retained qubit indices, whole-face cycles, full parent stars and incident faces, ordered rim/arcs, HX/HZ, logical witnesses, and eligible-edge/check/query records. Check IDs have separate X/Z namespaces. `parent` stores the tiling parameters and perpendicular-space conventions; `selection` stores the exact centre, ellipse parameters, tile-prefix specification and corners. The tuple `spec` indexes the centre/aspect/orientation lists in the frozen protocol. Centroid distance ties use rounding to 10 decimals followed by sorted corner lifts; this is a deterministic numeric tie convention, not a new cut outcome.

The two rough arcs form a relative subcomplex: their edges are omitted data qubits and all their vertices, **including the four rough/smooth corners**, have no X-check. Every whole face supplies a Z-check on its remaining data edges. A face touching the rough boundary can consequently have weight below four. Eligible edges require both adjacent face checks to retain all four sides and both endpoint stars to retain every parent edge. A smooth-rim endpoint is not automatically intact.

X logicals mean ker(HZ)/row(HX), Z logicals mean ker(HX)/row(HZ). Search uses primal/dual shortest paths; the independent saved-data checker reconstructs matrices, calculates GF(2) ranks, tests **all 21 weight-one and 210 weight-two supports in each sector**, and verifies the weight-three witnesses and their odd overlap. No search-path argument substitutes for that independent distance check.

`*_certificate.json` and `comparison.json` record the certificate outcomes. The checker also verifies a single disk rim, face connectivity, vertex links, unit rhombus geometry, pairwise non-overlapping face interiors and area equality. Parent stars/faces and physical/perpendicular addresses are checked against a separately regenerated larger parent, with the selected vertices strictly inside the original construction bounds. Geometry tolerances are 1e-8; address comparison 1e-10; GF(2) incidence is exact.

## Perpendicular-space caveats

AB's source window is a translated regular octagon: its centroid is approximately **(-1, -sqrt(2))**, not zero. This is preserved, along with offset `(0.1381,0.0927)`. Stored perpendicular coordinates are `K @ PERP + offset`, tested against that actual polygon with the source tolerance 1e-9. Recentring only the polygon would change the tiling. The source's `sum(K)%5` is retained as an integer label, **not** interpreted as a Penrose-style layer or a canonical AB predictor.

Penrose retains the full Z5 lift, `sum(K)` layers 1–4, unshifted perpendicular projection `K @ PERP`, gamma `(0.30,0.10,-0.25,-0.25,0.10)`, and projected gamma. The authoritative acceptance convention is the source's pentagrid construction, not a newly inferred centred-window test. No canonical cross-family normalization of perpendicular coordinates is supplied; it must be specified before a predictor study. Nothing needed to reproduce these finite patches is missing.

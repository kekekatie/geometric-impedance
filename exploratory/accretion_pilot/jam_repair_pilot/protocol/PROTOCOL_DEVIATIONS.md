# Protocol deviations (dated)

Deviations from the frozen pre-commitments, recorded rather than edited into the
originals.

## 2026-11-01 — Phase 2 (PHASE2_DIAGNOSTICS.md)

- **D3 "window-stack centre" realised as the offset-space origin (0,0).** The
  pre-commitment described D3a's reference as the averaged centroid of the four
  layer-window pentagons. It was realised as the offset-space origin — the common
  centre of the Penrose acceptance windows under the `ζ^{2j}` perp map — because
  that is the unambiguous, gauge-fixed centre already used by the closure's
  region construction. Effect on conclusions: none; D3 did not separate the
  groups under either reading.
- **Depth proxy (D3b) demoted to a descriptive label.** To keep the diagnostic
  count at three (D1 area, D2 displacement, D3 eccentricity), the per-tile hull
  depth was reported as a descriptive label rather than a third diagnostic. It is
  computed in `phase2_diagnostics.py` (`_tile_depth`) and retained in
  `diagnostics.json`.

No deviation occurred before the Phase-2 outcomes were inspected that changed any
pass/fail bar — Phase 2 has no pass/fail bar (it is descriptive).

## Phase 3 (PHASE3_PROTOCOL.md)

No deviation. The protocol was frozen before any repair outcome was inspected and
followed as written. Because no fully-legal eligible move was found, the
"attempt the first move under the frozen order" step was reached but had an empty
candidate set in every case (a valid result under Section 6a/6b).

# Figure & table plan

Minimal set for a tight single-object paper. Each item lists purpose, source data
(all FROZEN), and the claim (CLAIMS_MAP) it supports.

## Figures
- **FIG 1 — Hero / schematic.** A phason-shear multigrid tiling → torus wrap → two
  walker paths from the same start edge: one heals (c=0), one winds (c≠0, logical).
  *Purpose:* define heal vs logical visually. *Source:* `seamless_torus.py` geometry.
  *Supports:* framing.
- **FIG 2 — Generic size trend.** P_logical vs N (log axis) for all families; overlay
  the three candidate fits for QC. *Source:* `inference_stage1.json`,
  `discrimination.json` (fits). *Supports:* E3, E4. *Caption guard:* "candidate
  description, 3 sizes".
- **FIG 3 — The ordering.** Grouped bars (per size) of P_logical: clean grid, QC,
  random-matched (with ensemble error bars), rewire; Wilson CIs. *Source:*
  `inference_stage1.json` + `discrimination.json` ensemble. *Supports:* E5, E6, E7, E8,
  E11.
- **FIG 4 — Defect-field organisation.** Number-variance ratio vs window scale
  (s=0.15/0.20/0.25) for QC, random-matched, and the failed blue-noise control; inset:
  trap-field point patterns (QC even vs random clumpy). *Source:* `discrimination.json`,
  `stage1c.json`. *Supports:* E9, O1/O2 (as boundary).
- **FIG 5 — (optional) Mechanism cartoon.** Clump→trap→heal vs even→roam→wind, tying
  the ordering to the number-variance result. *Supports:* Discussion.

## Tables
- **TABLE 1 — Construction validation.** Per substrate/order: N, §7.1 gate pass,
  max coordination, mean-degree deficit / merged-face %, shear norm. *Source:*
  `seamless_torus_validation.json`. *Supports:* E1, E2.
- **TABLE 2 — Control constructions.** Oblique grid (m×n, anisotropy, mean deg 4);
  defect-matched (mean deg, hist-TV, dispersion); rewire (replaced %, saturation).
  *Source:* `controls_validation.json`, `matched_control_validation.json`.
  *Supports:* E11 + methods.
- **TABLE 3 — Main inference.** substrate | N | trials | heal | logical | censored |
  P_heal | P_logical | P_censored | Wilson95 — primary non-seam; seam-start robustness
  block. *Source:* `inference_stage1.json`. *Supports:* E3, E5, E6.
- **TABLE 4 — Discrimination.** QC vs clean vs random-ensemble (mean±graph-σ) vs
  stamped; trap number-variance & nn per family; Stage-1C gate (T1–T4, PASS/FAIL).
  *Source:* `discrimination.json`, `stage1c.json`. *Supports:* E7, E9, S1, O1.

## Supplementary
- S-TABLE: rational-cut bracketing (Appendix A) — `rational_cut_validation.json`.
- S-TABLE: full per-graph ensemble values.
- All JSONs shipped as machine-readable supplements.

## Notes
- Colour/encoding: keep one consistent palette across FIG 2–4 (family = colour;
  substrate = marker). Light/dark safe if rendered as an artifact.
- Every figure caption states the evidential tier (established vs boundary) to match
  `CLAIMS_MAP.md`.

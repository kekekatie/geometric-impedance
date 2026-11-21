# Bridge Paper Blueprint — Local Witnesses, Hidden Load-Bearing Faces, and Zero-Net-Cost Steering

*Working manuscript blueprint (plain-English 1-page anchor). No sealed experiment scripts, data, or figures are modified by this document.*

---

## Core Thesis

When a single edge is lost on an aperiodic surface-code patch (`AB_1`, `Penrose_1`, `Penrose_2`), almost all of the full-archive decoding advantage lives right next to the loss edge — inside the four incident local witnesses (two adjacent faces, two endpoints). Yet withholding just two archived readings from a *single* adjacent face reveals that locally identical-looking checks do not necessarily share the load equally: local boundary geometry (an interior route bottleneck vs. a protruding corner ear) can concentrate ~16× more load on one face than its partner, while an endpoint check can steer dozens of individual decoding decisions with zero net change to aggregate accuracy.

---

## The Four Verified Pillars

### 1. The "Narrow Now" Baseline (11-Check Address Audit)
- **Finding:** Retaining only the four local witnesses touching the circled on-route loss edge (the corrected 8-reading "diamond" bracket) recovers **97.25–98.97%** of the full-archive (`thick − thin`) accuracy gain across all three fresh patches:
  - `AB_1 (e14)`: `+0.100270` of `+0.103101 pp` (**97.25%**)
  - `Penrose_1 (e14)`: `+0.120741` of `+0.122290 pp` (**98.73%**)
  - `Penrose_2 (e4)`: `+0.071602` of `+0.072349 pp` (**98.97%**)
- **Artifacts** *(branch `audit/fresh-site-addresses-2026-11-20` & `experiment/local-witness-omission-2026-11-20`)*:
  - Summary & handback: `exploratory/fresh_site_address_audit_2026-11-20/HANDBACK.md`, `exploratory/fresh_site_address_audit_2026-11-20/results/table.md`, `summary.csv`, `address_audit.json`
  - Figure: `exploratory/fresh_site_address_audit_2026-11-20/results/corrected_recovery.png` (`.svg`)

### 2. The Witness-Omission Stress Test (385,648 Histories per Site)
- **Finding:** Systematically withholding just two archived readings (one local witness) from the 8-reading local bracket exposes hidden load-bearing asymmetry on `AB_1` vs. balanced load-sharing on both Penrose patches:
  - **`AB_1 (e14)`:** Omitting `Z3` drops surviving gain to **15.54%** (`+0.016017 pp`; cost `+0.084253 pp`, `4,785` label flips), whereas omitting `Z6` retains **92.19%** (`+0.095051 pp`; cost `+0.005219 pp`, `2,112` label flips) — a **16.14× (~16×) cost ratio** between two weight-4 Z-faces sharing the same loss edge.
  - **`Penrose_1 (e14)`:** Balanced load-sharing — omitting `Z7` retains **77.51%** (`+0.094793 pp`), omitting `Z1` retains **77.71%** (`+0.095033 pp`).
  - **`Penrose_2 (e4)`:** Balanced load-sharing — omitting `Z1` retains **80.82%** (`+0.058471 pp`), omitting `Z4` retains **81.12%** (`+0.058692 pp`).
- **Artifacts** *(branch `experiment/local-witness-omission-2026-11-20`, commit `1922a7b`)*:
  - Protocol & handback: `exploratory/local_witness_omission_2026-11-20/PROTOCOL.md`, `HANDBACK.md`
  - Twelve-omission table & data: `exploratory/local_witness_omission_2026-11-20/results/table.md`, `omissions.csv`, `summary.json`
  - Three-panel omission figure: `exploratory/local_witness_omission_2026-11-20/results/omission_costs.png` (`.svg`)
  - Local geometry figure: `exploratory/local_witness_omission_2026-11-20/results/geometry.png` (`.svg`)

### 3. The Physical Mechanism (Local Bottleneck vs. Corner Ear)
- **Finding:** Read-only graph inspection of the sealed patch definitions explains the `AB_1` split geometrically without free parameters:
  - **`AB_1 (e14)` — structurally asymmetric:**
    - `Z3` (`{5, 6, 7, 10}`) is an **interior bridge** spanning between opposite smooth boundaries: **1** smooth boundary edge (`q5`), **3** interior edges, **3** neighboring Z-faces (`Z0, Z2, Z6`), corner degrees `(3, 3, 5, 5)`. Both shortest (weight-3) X-logicals through `e14` (`{5, 10, 14}` and `{5, 10, 15}`) funnel through its single boundary edge `q5`.
    - `Z6` (`{10, 11, 14, 15}`) is a **protruding corner ear**: **2** exposed smooth boundary edges (`q14, q15`) meeting at a **degree-2 corner tip** (`v12`, weight-2 X-check `X7 = {14, 15}`), only **2** interior edges, only **2** neighboring Z-faces (`Z3, Z7`), corner degrees `(2, 3, 5, 5)`. The two shortest X-logicals fork across `q14` vs. `q15` modulo `X7`.
  - **`Penrose_1 (Z7 vs. Z1)` and `Penrose_2 (Z1 vs. Z4)` — local mirror twins:**
    - Every face in both pairs has **1** smooth boundary edge, **3** interior edges, **3** neighboring Z-faces, identical sorted patch-graph corner degrees (`(3, 3, 3, 6)` on `Penrose_1`; `(3, 3, 4, 5)` on `Penrose_2`), and a single symmetric X-logical exit (`q1` vs. `q17` on `Penrose_1`; `q6` vs. `q10` on `Penrose_2`).
- **Artifacts** *(branch `claude/aperiodic-predict-2026-11-20` & `experiment/local-witness-omission-2026-11-20`)*:
  - Sealed patch graphs & route selection: `exploratory/aperiodic_predict_2026-11-20/results/AB_1.json`, `Penrose_1.json`, `Penrose_2.json`, `selection.json`, `result.png` (`.svg`), `HANDBACK.md`

### 4. Zero-Net-Cost Decision Steering
- **Finding:** On `Penrose_2 (e4)`, withholding endpoint check `X5` produces **0.00% net accuracy change** (`+0.00000000 pp`: credit lost `0.00020747 pp` exactly equals credit gained `0.00020747 pp`), yet flips **44 individual decoding decisions** (plus 2 tie changes). Similarly, omitting `X0` has `0.00%` net cost while flipping **18** decisions (+ 2 tie changes).
- **Implication:** A local witness can actively steer *which* histories survive decoding even when the aggregate score appears completely flat.
- **Artifact:** `exploratory/local_witness_omission_2026-11-20/results/table.md` (`Penrose_2_e4`, rows `X5` and `X0`).

---

## Guardrails & Scope Notes

1. **Z-check vs. X-check caveat:** The adjacent faces are **Z-checks** that directly detect the scored X-type faults, whereas the endpoints are **X-checks**. This naturally helps explain why omitting faces carries much larger accuracy cost than omitting endpoints — while leaving the **Z3 vs. Z6** face-to-face comparison completely controlled (both are weight-4 Z-checks on opposite sides of the same loss edge).
2. **Do not over-claim a family law:** The ~16:1 split on `AB_1` must **not** be framed as a universal Ammann–Beenker vs. Penrose tiling law. Present it honestly as a **local bottleneck vs. boundary-ear geometry** effect; whether fresh cuts with matched/reversed local geometry show the same split remains an open empirical question.
3. **Strict separation from the July skeleton:** Keep this manuscript completely separate from the unwritten July algebraic/number-theoretic skeleton (*"The Code That Cannot Remember"* / `exploratory/norm_identity_check/norm_identity_check.py`). This bridge paper stands solely on the verified QEC decoder, address-audit, and witness-omission artifacts above.

---

## Next Steps (When We Return)

1. Review the three-panel omission figure (`exploratory/local_witness_omission_2026-11-20/results/omission_costs.png`) and the twelve-omission table (`exploratory/local_witness_omission_2026-11-20/results/table.md`).
2. Decide whether to run an optional fresh-cut check (e.g., an AB cut without a corner ear, or a Penrose cut with one) to test the bottleneck-vs.-ear mechanism directly, or lock scope to the three existing patches.
3. Begin drafting the LaTeX manuscript directly against these verified repository artifacts.

# Dynamic Growth Around a Live Scar — Handback (6-for-6 Pre-Registered Sweep)

*Branch: `experiment/dynamic-growth-scar-2026-11-25`. Protocol & predictions (`P1`, `P2`, `P3`) frozen before any decoder run in commit [`c510bf5`](https://github.com/kekekatie/geometric-impedance/commit/c510bf5). Result commit: this direct child. Unchanged `(3,3)` decoder, `p = 0.001`, `CorrectedPatchCode`, exhaustive $k \le 2$ ordinary faults; **2,415,288 new site-histories**, **0 full-scan mismatches**, `max_posterior_difference = 0.0`.*

---

## Verdict: 6-for-6 Clean Sweep + Universal 3-Phase Life Cycle of a Scar

Every pre-registered directional prediction (**P1**, **P2**, **P3**) held cleanly across **both** Ammann–Beenker (`AB_1`) and Penrose (`Penrose_ear`):

| Step | Accretion action | `n` | `n_w3_on` | Full gain (`pp`) | Narrow Now | Hallway `%` | Ear `%` | Face ratio | Neither $G_0$ | Backup $I$ (`%`) | Phase |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **A0** | `AB_1` baseline *(sealed)* | 21 | 2 | `+0.103101` | 97.25% | **15.54%** | **92.19%** | **16.14×** | 0.107% | **+10.4%** | Exposed Ear |
| **A1** | Half-swallow Ear (`+762`) | 18 | 1 | `+0.097999` | 98.68% | **72.30%** | **84.78%** | **1.90×** | 0.010% | **+58.4%** | **Healed** |
| **A2** | Full-bury Ear (`+762,+764`) | 23 | 0 | **`+0.008618`** | 66.11% | 30.15% | 32.02% | 1.06× | 0.520% | **-4.5%** | **Dissipated** |
| **A1-H** | Bury Hallway (`+755`) | 19 | 0 | **`+0.007794`** | 66.02% | 30.09% | 27.41% | 1.07× | 0.244% | **-8.8%** | **Dissipated** |
| **B0** | `Penrose_ear` baseline *(sealed)* | 21 | 2 | `+0.099118` | 98.83% | **14.23%** | **95.66%** | **26.67×** | 0.112% | **+10.9%** | Exposed Ear |
| **B1** | Half-swallow Ear (`+158`) | 21 | 1 | `+0.143573` | 99.40% | **81.37%** | **81.75%** | **1.02×** | 0.071% | **+63.7%** | **Healed** |
| **B2** | Extend outer ring (`+158,+156`) | 23 | 1 | `+0.121104` | 99.38% | **78.20%** | **78.76%** | **1.03×** | 0.067% | **+57.5%** | **Persistent** |
| **B1-H** | Bury Hallway (`+289`) | 24 | 0 | **`+0.011330`** | 65.32% | 32.19% | 27.51% | 1.14× | 0.156% | **-5.8%** | **Dissipated** |

---

## Plain-English Summary: The Three-Phase Life Cycle of an Accreting Scar

1. **Phase 1 — Exposed Corner Ear (`A0`, `B0`):** The scar sits bright on a shortest X-logical route (`~0.10 pp`), with a catastrophic **16–27×** bottleneck on the Hallway face and weak mutual backup (**`I ≈ +10–11%`**).
2. **Phase 2 — Healed & Persistent (`A1`, `B1`, `B2` — confirms P1 & P3):** Accreting one tile onto the Corner Ear swallows its degree-2 tip while keeping the scar on-route (`n_w3_on = 1`). Instantly, the bottleneck heals (**`16.14× → 1.90×`** on AB; **`26.67× → 1.02×`** on Penrose!) and mutual backup $I$ jumps 5–6× into the **`+57–64%`** band. Extending the outer ring behind the healed face (`B2`) preserves that healed, high-backup state cleanly (`full = +0.1211 pp`, `intact = 99.38%`, `1.03×`, `I = +57.5%`).
3. **Phase 3 — Buried & Dissipated (`A2`, `A1-H`, `B1-H` — confirms P2 + bonus discovery!):** Accreting tiles until *either* the Corner Ear (`A2`) *or* the Hallway (`A1-H`, `B1-H`) is completely buried into the bulk (`bndS = 0, znbr = 4`) causes the shortest X-logical to detour away (`n_w3_on → 0`):
   - Full-archive gain collapses **9–13×** (`~0.008–0.011 pp`), even when the Corner Ear is still sticking out (`A1-H`, `B1-H`).
   - Narrow-Now recovery drops cleanly from **98–99%** down to **65–66%**.
   - **Unexpected universal signature:** In *every single* buried step across *both* tilings (`A2`, `A1-H`, `B1-H`), the paired-face interaction **$I$ flips sign from positive (substitutable backup) to negative (`-4.5%` to `-8.8%`, mild synergy)**!

---

## Replay

```sh
python3 exploratory/dynamic_growth_scar_2026-11-25/run_growth.py
```

All 6 exported patch JSONs (`results/<STEP>.json`), metadata (`<STEP>_meta.json`), and full scored outputs (`<STEP>_result.json`) are archived in `results/`.

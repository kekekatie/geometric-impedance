# Which Old Readings Matter? Local Geometry, Bottleneck Faces, and Zero-Net-Cost Steering in Aperiodic Surface Codes

**K. T. Niedzwiecki**  
Independent Researcher, South Australia  
24 November 2026 *(Draft v0.4 — unified working manuscript)*

---

## Abstract

When a data qubit is lost on a surface-code patch, a decoder with access to past stabilizer readings outperforms an archive-free ("thin", boundary-summary-only) decoder — especially when the lost edge sits on a shortest logical route. Here we ask a sharper follow-up question: **which specific archived readings actually carry that decoding advantage, how do neighboring faces back each other up, and why do endpoint omissions flip dozens of decisions while leaving the net score flat?** Using exhaustive zero-, one-, and two-fault evaluation (385,648 histories per site; bounded `(3,3)` decoder, $p = 0.001$) across five `n=21`, distance-`(3,3)` Ammann–Beenker (AB) and Penrose patches, we find five connected results:

- **The "Narrow Now" holds across both tilings.** Once an indexing bug in the original adapter is corrected (11-check address audit), keeping just **eight** archived readings — two early rounds from the four stabilizer checks incident to the lost edge — recovers **97.25–99.26%** of the full-archive accuracy gain across all five tested sites.
- **Hidden bottleneck faces.** Withholding just two archived readings from a single adjacent Z-face reveals a 16-fold split on `AB_1 (e14)`: omitting face `Z3` collapses surviving gain to **15.54%** (`+0.08425 pp` cost), whereas omitting its partner `Z6` retains **92.19%** (`+0.00522 pp` cost) — a **16.14×** cost ratio between two weight-4 Z-checks sharing the same lost edge. By contrast, `Penrose_1 (e14)` (**77.51%** vs. **77.71%**) and `Penrose_2 (e4)` (**80.82%** vs. **81.12%**) share the load nearly 50/50.
- **Local geometry drives the collapse across both tiling families (2×2 role reversal).** A complete census of all 1,220 on-route eligible edges in the frozen `n=21, d=(3,3)` AB and Penrose pools shows that **only two** local face-pair geometries occur in either family: *Mirror Middle Yards* (86.5% in AB, 91.1% in Penrose) and *Hallway vs. Corner Ear* (13.5% in AB, 8.9% in Penrose). In a pre-registered 2×2 role reversal:
  1. Enlarging `AB_1` by **one extra tile** touching `Z6` (and re-cutting the boundary to keep `n=21, d=(3,3)`) yields `AB_bal` on the exact same physical loss edge, lifting `Z3`'s surviving gain from **15.54% → 72.59%** and cutting the face cost ratio by more than 8× (**16.14× → 1.96×**).
  2. Selecting a Penrose cut with a degree-2 corner ear (`Penrose_ear`) reproduces and sharpens the collapse: omitting hallway `Z7` crashes surviving gain to **14.23%**, while omitting corner ear `Z6` retains **95.66%** (**26.67×** cost ratio).
- **Middle yards back each other up; corner ears cannot (5-site paired-face omission).** Covering **both** adjacent faces at once (retaining only the two endpoint X-checks) collapses surviving gain to **0.019–0.112%** across all five sites. The substitution interaction $I$ — how much extra it costs to lose one face once its partner is already gone — jumps ~5–6× with local shape across both tilings: **$I = +0.0455$ to $+0.0690$ pp** (~56–63% of full gain) for all three middle-yard pairs (`Penrose_1`, `Penrose_2`, `AB_bal`), versus just **$I = +0.0107$ to $+0.0109$ pp** (~10–11%) for both hallway-vs.-corner-ear pairs (`AB_1`, `Penrose_ear`).
- **Zero-net-cost decision steering comes from exact X-logical twinning.** On `Penrose_2 (e4)`, withholding endpoint X-check `X5` (`X0`) yields **0.00000000 pp** net cost while flipping **44** (**18**) individual decoding decisions. Exhaustive flip-pairing analysis proves this zero is an exact structural symmetry: every single flipped history belongs to a same-record twin pair (`22/22` on `X5`, `9/9` on `X0`) whose total X-faults differ by the exact on-route weight-3 X-logical `{4, 6, 10}` — identical syndrome, identical decoder decision, opposite truth. On `Penrose_1 (e14)`, the same `{1, 10, 17}` twinning accounts for nearly all 570+ flips, leaving 24 unpaired movers that carry the tiny `+0.00001844 pp` residue.

---

## 1. Introduction

A fault-tolerant decoder with a finite memory budget faces a concrete version of a broader question: *what from the past must be kept so that the present can still decide accurately?* In a recent prospective study on fresh aperiodic surface-code patches (`AB_1`, `Penrose_1`, `Penrose_2`), we confirmed that full-archive memory helps most when a lost edge lies on a shortest X-logical route — producing a 22–40× brighter archive advantage on-route than at matched off-route edges.

At first glance, that study appeared to carry a puzzling second result: keeping only the eight local archived readings touching the lost edge (the "diamond" bracket) seemed to recover almost none of the on-route advantage. An independent address audit revealed why: on `11×9` (`HX`×`HZ`) patches, the legacy adapter had mapped Z-check indices assuming 10 X-rows, silently querying the wrong checks. Once the address map was fixed, the picture flipped completely: **97.25–98.97%** of the full-archive benefit lived right inside the four checks touching the lost edge.

That sharp localization opened three interlocking questions: if nearly the entire memory advantage lives inside four local checks (two adjacent Z-faces and two endpoint X-checks), **(1) how is the load split between the two faces, (2) how much can one face stand in when the other is lost, and (3) why can omitting an endpoint flip dozens of decisions while leaving the net score untouched?** As the experiments below show, all three answers trace back to the same local object: the shortest weight-3 X-logical threading the lost edge and the boundary geometry immediately flanking it.

---

## 2. Experimental Setup and Pre-Registered Lineage

All experiments share the same pinned geometry generator, XOR syndrome simulator, shared-onset erasure inference, and bounded `(3,3)` decoder (`w_dec = 3`, `w_frame = 3`, physical error rate $p = 0.001$), evaluated exhaustively over all zero-, one-, and two-fault ordinary configurations (48,206 configurations × 8 onset/free-value variants = **385,648 histories per site**).

- **Corrected local bracket ("intact"):** Retains rounds $t \in \{1, 2\}$ of the four checks geometrically incident to the lost edge (8 archived coordinates), plus live rounds $t \in \{3, 4\}$ of all checks, thin-state boundary parities, and the committed frame.
- **Single- and paired-witness omission:** Removes rounds $t \in \{1, 2\}$ of one named incident check (leaving 6 archived coordinates) or both adjacent Z-faces simultaneously (arm `0`, leaving only the 4 early endpoint X-readings). Withheld coordinates are strictly **absent**, never zero-filled; live rounds, boundary parities, and frame remain untouched.
- **Primary score:** Weighted tie-aware truth credit (ties receive 0.5 credit), reported in percentage points (`pp`). Omission cost is `100 × (intact credit − omission credit)`; positive cost means withholding hurt. Weighted credit *lost* and *gained* are tracked separately alongside unweighted label and tie-status flips.
- **Validation:** Every site completed deterministic unaccelerated full-scan verification samples with **0 mismatches** and `max_posterior_difference = 0.0`, plus exact rational half-credit re-aggregation across all 1,928,240 paired-face site-histories.

---

## 3. Pillar 1 — The "Narrow Now" Baseline

Across the three original fresh cuts (`audit/fresh-site-addresses-2026-11-20`) and the two new role-reversal cuts (`experiment/role-reversal-omission-2026-11-22`), retaining only the four local witnesses touching the lost edge captures nearly the entire full-archive gain:

| Site | Tiling | Full archive gain (`thick − thin`, pp) | Intact 8-reading gain (`pp`) | Local recovery (% of full) |
|---|---|---:|---:|---:|
| `AB_1 (e14)` | Ammann–Beenker | +0.103101 | +0.100270 | **97.25%** |
| `Penrose_1 (e14)` | Penrose | +0.122290 | +0.120741 | **98.73%** |
| `Penrose_2 (e4)` | Penrose | +0.072349 | +0.071602 | **98.97%** |
| `AB_bal (e14)` *(new)* | Ammann–Beenker | +0.096195 | +0.095485 | **99.26%** |
| `Penrose_ear (e13)` *(new)* | Penrose | +0.099118 | +0.097956 | **98.83%** |

![Figure 1: Corrected local 8-reading recovery across the fresh sites](figures/fig1_narrow_now_recovery.png)

---

## 4. Pillar 2 — Single-Witness Omission and Paired-Face Backup

### 4.1 The 12-arm single-witness stress test
Withholding one incident check at a time across the three original sites (`experiment/local-witness-omission-2026-11-20`, commit `1922a7b`) exposed a 16-fold asymmetry on `AB_1` alongside balanced load-sharing on both Penrose patches:

![Figure 2: Cost of withholding each local witness across AB_1, Penrose_1, and Penrose_2](figures/fig2_witness_omission_costs.png)

| Site | Omitted check | Role / weight | Cost (`pp`) | Surviving gain (% of full) | Label flips | Tie flips |
|---|---|---|---:|---:|---:|---:|
| `AB_1 (e14)` | `X4` / `X5` | endpoint / 5 | +0.000184 | 97.08% | 82 / 90 | 8 / 8 |
| `AB_1 (e14)` | **`Z3`** | **face / 4** | **+0.084253** | **15.54%** | **4,785** | 4 |
| `AB_1 (e14)` | `Z6` | face / 4 | +0.005219 | **92.19%** | 2,112 | 4 |
| `Penrose_1 (e14)` | `X4` / `X6` | endpoint / 6, 3 | +0.000018 | 98.72% | 570 / 572 | 12 / 12 |
| `Penrose_1 (e14)` | `Z1` | face / 4 | +0.025708 | **77.71%** | 2,152 | 4 |
| `Penrose_1 (e14)` | `Z7` | face / 4 | +0.025948 | **77.51%** | 3,468 | 12 |
| `Penrose_2 (e4)` | `X0` / `X5` | endpoint / 5, 3 | **0.000000** | 98.97% | **18 / 44** | 2 / 2 |
| `Penrose_2 (e4)` | `Z1` | face / 4 | +0.013131 | **80.82%** | 1,368 | 14 |
| `Penrose_2 (e4)` | `Z4` | face / 4 | +0.012910 | **81.12%** | 2,480 | 10 |

On `AB_1`, `Z3` and `Z6` are both weight-4 Z-checks sitting on opposite sides of the exact same lost edge `e14`, yet omitting `Z3` costs **16.14×** more than omitting `Z6`.

### 4.2 Covering both faces: mutual backup vs. single-face bottlenecks
A natural follow-up asks what survives when **both** adjacent Z-faces are covered simultaneously, leaving only the two endpoint X-checks (`experiment/paired-face-omission-2026-11-23`, commit `9515df3`). Let $G_{AB}, G_A, G_B, G_0$ be the gains (over `thin`) when keeping both faces, face $A$ only, face $B$ only, or neither face, and let $I = (G_A - G_0) - (G_{AB} - G_B) = (G_B - G_0) - (G_{AB} - G_A)$ measure how much extra it costs to lose a face once its partner is already absent:

![Figure 4: Four-arm paired-face retention comparison across all five sites](figures/fig4_paired_face_backup.png)

| Site (`A` / `B`) | Local shape | Both (`%`) | `A` only (`%`) | `B` only (`%`) | Neither $G_0$ (`%`) | Interaction $I$ (`pp`) | $I$ as % of full gain |
|---|---|---:|---:|---:|---:|---:|---:|
| `AB_1` (`Z3` / `Z6`) | Hallway / Corner ear | 97.25% | 92.19% | 15.54% | **0.107%** | +0.01069 | **10.4%** |
| `Penrose_ear` (`Z7` / `Z6`) | Hallway / Corner ear | 98.83% | 95.66% | 14.23% | **0.112%** | +0.01085 | **10.9%** |
| `AB_bal` (`Z3` / `Z6`) | Two middle yards | 99.26% | 85.69% | 72.59% | **0.019%** | +0.05676 | **59.0%** |
| `Penrose_1` (`Z7` / `Z1`) | Two middle yards | 98.73% | 77.71% | 77.51% | **0.083%** | +0.06898 | **56.4%** |
| `Penrose_2` (`Z1` / `Z4`) | Two middle yards | 98.97% | 81.12% | 80.82% | **0.025%** | +0.04554 | **62.9%** |

Across all five sites, covering both faces wipes out **>99.88%** of the local recovery (`0.019–0.112%` surviving). Yet the interaction $I$ cleanly splits the five sites into two regimes: when both neighbors are middle yards (`Penrose_1`, `Penrose_2`, `AB_bal`), either face can stand in for **56–63%** of the full-archive gain while its partner is absent; when one neighbor is a corner ear (`AB_1`, `Penrose_ear`), mutual backup collapses by ~5–6× to just **10–11%**.

---

## 5. Pillar 3 — Local Bottleneck vs. Corner Ear, and the 2×2 Role-Reversal Test

### 5.1 Structural diagnosis and complete pool census
Read-only graph inspection of the sealed patch definitions explains why `AB_1` and the two Penrose patches behave differently:
- On **`AB_1 (e14)`**, `Z3` (`{5, 6, 7, 10}`) is an **interior bridge ("hallway")** with **1** smooth boundary edge (`q5`), **3** interior edges, **3** neighboring Z-faces (`Z0, Z2, Z6`), and corner degrees `(3, 3, 5, 5)`. Both shortest (weight-3) X-logicals through `e14` (`{5, 10, 14}` and `{5, 10, 15}`) funnel through `Z3`'s single boundary edge `q5`. By contrast, `Z6` (`{10, 11, 14, 15}`) is a **protruding corner ear** with **2** exposed smooth boundary edges (`q14, q15`) meeting at a **degree-2 corner tip** (`v12`, weight-2 X-check `X7 = {14, 15}`), only **2** interior edges, and only **2** neighboring Z-faces (`Z3, Z7`). The two shortest X-logicals fork across `q14` vs. `q15` modulo `X7`.
- On **`Penrose_1` (`Z7` vs. `Z1`)** and **`Penrose_2` (`Z1` vs. `Z4`)**, every face in both pairs is a **middle yard**: **1** smooth boundary edge, **3** interior edges, **3** neighboring Z-faces, identical sorted patch-graph corner degrees (`(3, 3, 3, 6)` and `(3, 3, 4, 5)`), and a single symmetric X-logical exit.

Enumerating every on-route eligible edge in the frozen `n=21, d=(3,3)` disk-cut generator shows that **only these two** local face-pair geometries occur in either tiling family:

| Family | `n=21, d=(3,3)` cuts | On-route eligible edges | Mirror Middle Yards | Hallway + Corner Ear |
|---|---:|---:|---:|---:|
| **Ammann–Beenker** | 1,282 | 503 | **435** (86.5%) | **68** (13.5%) |
| **Penrose** | 1,791 | 717 | **653** (91.1%) | **64** (8.9%) |

### 5.2 Pre-registered 2×2 role reversal
To separate local geometry from tiling family, we selected two role-reversal cuts from the frozen pool **before** running the decoder:
1. **`AB_bal` (`spec=(22, 2, 2, 10)`, `corners=(2, 5, 11, 15)`, `e14`):** `AB_1` enlarged by **one extra tile** (new `Z8`, sharing an edge with `Z6` and meeting `Z3` at a vertex) together with the boundary re-cut needed to maintain `n=21, d=(3,3)` (4 boundary edges swap rough/smooth assignment, 2 become interior, check split shifts `11 X / 9 Z → 10 X / 10 Z`, and the scored Z representative shifts physically). The physical loss-edge endpoints `(0,1,2,-1)` and `(0,1,2,0)` are identical (`q10 → q9`), one of the two shortest X-logicals through the loss disappears while the other survives physically, and `Z3` and `Z6` become locally matched middle yards (corner degrees `(3, 3, 5, 5)`).
2. **`Penrose_ear` (`spec=(7, 1, 3, 10)`, `corners=(0, 4, 9, 13)`, `e13`):** exact structural twin of `AB_1`, pairing hallway `Z7` (1 smooth boundary edge, 3 Z-neighbors) with protruding degree-2 corner ear `Z6` (2 smooth boundary edges, 2 Z-neighbors, forked exits).

![Figure 3: Measured 2x2 role-reversal result](figures/fig3_role_reversal_2x2.png)

| Local shape around the loss edge | Ammann–Beenker | Penrose |
|---|---|---|
| **Two Middle Yards** *(1 bnd edge, 3 Z-nbrs each)* | **`AB_bal (e14)` [NEW]:**<br>`Z3` **72.59%** (`+0.02565 pp`) vs. `Z6` **85.69%** (`+0.01306 pp`)<br>*(cost ratio drops 8×: `16.14×` → **`1.96×`**, backup $I = 59.0\%$)* | **`Penrose_1 (e14)`:** **77.51%** vs. **77.71%** *(1.01×, $I = 56.4\%$)*<br>**`Penrose_2 (e4)`:** **80.82%** vs. **81.12%** *(1.02×, $I = 62.9\%$)* |
| **Hallway vs. Corner Ear** *(deg-2 tip)* | **`AB_1 (e14)`:**<br>`Z3` **15.54%** (`+0.08425 pp`) vs. `Z6` **92.19%** (`+0.00522 pp`)<br>*(cost ratio **`16.14×`**, backup $I = 10.4\%$)* | **`Penrose_ear (e13)` [NEW]:**<br>`Z7` **14.23%** (`+0.08385 pp`) vs. `Z6` **95.66%** (`+0.00314 pp`)<br>*(cost ratio **`26.67×`**, backup $I = 10.9\%$)* |

Both predictions held cleanly: giving Penrose a corner ear creates an even sharper **26.67×** collapse, while enlarging `AB_1` by one tile to fill in `Z6`'s corner ear eliminates the collapse (`Z3` rises from **15.54% → 72.59%**, cost ratio drops **8×** to **1.96×**, and mutual backup $I$ jumps from **10.4% → 59.0%**).

---

## 6. Pillar 4 — Zero-Net-Cost Decision Steering and Exact X-Logical Twinning

Aggregate accuracy can conceal active decision-level movement. On `Penrose_2 (e4)`, withholding endpoint `X5` incurs **0.00000000 pp** net cost — weighted credit lost (`0.00020747 pp`) exactly equals credit gained (`0.00020747 pp`) — yet **44 individual histories flip their decoded label** (plus 2 tie-status changes). Withholding `X0` similarly yields exact zero net cost while flipping **18** labels (+ 2 tie changes). On `Penrose_1 (e14)`, `X4` and `X6` incur tiny net costs (`+0.00001844 pp`) while flipping **570** and **572** decisions, respectively. By contrast, on `AB_bal (e14)`, `X2` and `X3` show true invariance (`0.00000000 pp` cost, **0** label flips).

A dedicated flip-pairing audit (`experiment/zero-net-pairing-2026-11-24`, commit `03dc321`) proves that `Penrose_2`'s exact zero is not numerical coincidence, but a **structural symmetry generated by the on-route weight-3 X-logical**:

| Site · check | Total movers (flips + ties) | Net cost (`pp`) | Record-paired label twins | Differs by weight-3 X-logical | Unpaired remainder |
|---|---:|---:|---:|---:|---|
| `Penrose_2 · X5` | 46 (44 + 2) | **0.00000000** | **22 / 22 pairs** | **22 / 22** (`{4, 6, 10}`) | 2 equal-weight ties (cancel) |
| `Penrose_2 · X0` | 20 (18 + 2) | **0.00000000** | **9 / 9 pairs** | **9 / 9** (`{4, 6, 10}`) | 2 equal-weight ties (cancel) |
| `Penrose_1 · X4` | 582 (570 + 12) | +0.00001844 | 279 pairs | 259 / 279 (`{1, 10, 17}`) | **24 of 582** (carries residue) |
| `Penrose_1 · X6` | 584 (572 + 12) | +0.00001844 | 280 pairs | 260 / 280 (`{1, 10, 17}`) | **24 of 584** (carries residue) |

Because adding the weight-3 X-logical threading the lost edge commutes with every stabilizer, two fault histories differing by that logical produce the **exact same detector record** — and therefore the exact same posterior and decoder decision — while having **opposite true Z-logical outcomes**. Whenever omitting an endpoint X-check flips one twin from right to wrong, it flips its twin from wrong to right by the exact same weight. On `Penrose_2`, that twinning is 100% complete (exact zero); on `Penrose_1`, a small unpaired remainder of 24 movers carries the genuine `+0.00001844 pp` residue.

---

## 7. Guardrails, Caveats, and Scope

1. **Z-check vs. X-check caveat:** Adjacent faces are Z-checks directly measuring the syndrome of X faults that flip the scored Z logical, whereas endpoints are X-checks (entering mainly through shared-onset inference). This naturally explains why faces outweigh endpoints overall — and why endpoint omissions sit at or near zero via X-logical twinning — while leaving every **face-vs.-face** comparison strictly controlled.
2. **Local geometry, accompanying code changes, and `AB_bal`'s residual `1.96×`:** The 16–27× collapse is a local bottleneck-vs.-corner-ear effect shared by both tilings, not an intrinsic AB-vs.-Penrose law. As audited in `experiment/paired-face-omission-2026-11-23`, enlarging `AB_1` by one tile to form `AB_bal` keeps the exact same physical loss edge and tiles plus `new Z8`, but also re-cuts the boundary (`11/9 → 10/10`) and shifts the scored Z representative, so it should be read as returning to the same physical edge in a one-tile-enlarged code rather than holding all other code features fixed. Furthermore, while `Z3` and `Z6` on `AB_bal` are exact local mirror twins through rings 1 and 2, global patch geometry and `scored_logical_Z = [3, 1, 0]` remain asymmetric; the exact causal driver of `AB_bal`'s mild residual **1.96×** ratio (`72.59%` vs. `85.69%`) remains open.
3. **Accuracy-level substitution, not information-theoretic redundancy:** Positive interaction $I$ in §4.2 measures partial substitution *at the decoder-accuracy level* (losing one face hurts more once its partner is gone). It does not prove that the two faces carry duplicate mutual information or isolate which individual fault histories carry $I$.
4. **Scope and strict separation:** Results are established for bounded `(3,3)` decoding, exhaustive `k <= 2` ordinary faults at $p = 0.001$, across five `n=21, d=(3,3)` cuts. This manuscript stands solely on these verified QEC decoder artifacts and is kept strictly separate from the algebraic unit-norm conjugacy work (`norm_identity_check.py`).

---

## 8. Provenance and Reproducibility

| Component | Branch / Commit | Key Paths |
|---|---|---|
| Prospective route prediction & patch JSONs | `claude/aperiodic-predict-2026-11-20` (`fdeaa32`) | `exploratory/aperiodic_predict_2026-11-20/HANDBACK.md`, `results/{AB_1,Penrose_1,Penrose_2}.json` |
| 11-check address audit ("Narrow Now") | `audit/fresh-site-addresses-2026-11-20` (`1f85f79`) | `exploratory/fresh_site_address_audit_2026-11-20/HANDBACK.md`, `results/table.md`, `results/corrected_recovery.png` |
| 12-arm witness-omission stress test | `experiment/local-witness-omission-2026-11-20` (`1922a7b`) | `exploratory/local_witness_omission_2026-11-20/HANDBACK.md`, `results/table.md`, `results/omission_costs.png` |
| 2×2 role-reversal test (`AB_bal`, `Penrose_ear`) | `experiment/role-reversal-omission-2026-11-22` (`6236920`) | `exploratory/role_reversal_omission_2026-11-22/HANDBACK.md`, `results/table.md`, `results/role_reversal_2x2.png`, `run_role_reversal.py` |
| 5-site paired-face omission & geometry audit | `experiment/paired-face-omission-2026-11-23` (`9515df3`) | `exploratory/paired_face_omission_2026-11-23/HANDBACK.md`, `GEOMETRY_AUDIT.md`, `results/table.md`, `results/four_arm_comparison.png` |
| Exact X-logical twin-pairing proof | `experiment/zero-net-pairing-2026-11-24` (`03dc321`) | `exploratory/zero_net_pairing_2026-11-24/HANDBACK.md`, `results/pairing.json` |

---

## Acknowledgements

*[Placeholder — to be written in K. T. Niedzwiecki's own voice before final submission.]*

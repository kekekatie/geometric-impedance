# Role-Reversal Omission Table (2026-11-22)

All gains/costs are percentage points (`pp`). Positive cost means withholding hurt.
Both sites ran all **385,648** histories (`k <= 2` exhaustive ordinary faults, `(3,3)` decoder, `p = 0.001`) with **1,344** unaccelerated full-scan verification checks and **0** mismatches (`max_posterior_difference = 0.0`).

| Site | Omit | Role / weight | Cost (pp) | Six-reading gain (pp) | Full gain (pp) | Surviving % of full | Credit lost (pp) | Credit gained (pp) | Label flips | Tie flips |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| AB_bal_e14 | X2 | endpoint / 5 | +0.00000000 | +0.09548454 | 0.09619456 | 99.26% | 0.00000000 | 0.00000000 | 0 | 0 |
| AB_bal_e14 | X3 | endpoint / 5 | +0.00000000 | +0.09548454 | 0.09619456 | 99.26% | 0.00000000 | 0.00000000 | 0 | 0 |
| AB_bal_e14 | Z3 | face / 4 | +0.02565311 | +0.06983142 | 0.09619456 | **72.59%** | 0.06295248 | 0.03729937 | 2886 | 4 |
| AB_bal_e14 | Z6 | face / 4 | +0.01305708 | +0.08242745 | 0.09619456 | **85.69%** | 0.03642336 | 0.02336628 | 1494 | 6 |
| Penrose_ear_e13 | X2 | endpoint / 6 | +0.00014754 | +0.09780825 | 0.09911765 | 98.68% | 0.00077457 | 0.00062704 | 146 | 20 |
| Penrose_ear_e13 | X6 | endpoint / 5 | +0.00018442 | +0.09777137 | 0.09911765 | 98.64% | 0.00062704 | 0.00044261 | 110 | 20 |
| Penrose_ear_e13 | Z6 | face / 4 *(corner ear)* | +0.00314440 | +0.09481140 | 0.09911765 | **95.66%** | 0.05012592 | 0.04698153 | 2555 | 24 |
| Penrose_ear_e13 | Z7 | face / 4 *(hallway)* | **+0.08384750** | +0.01410829 | 0.09911765 | **14.23%** | 0.12202287 | 0.03817537 | 4401 | 28 |

## 2×2 Summary (Measured Across All Five Sites)

| Local shape around the loss edge | Ammann–Beenker | Penrose |
|---|---|---|
| **Two Middle Yards** *(1 bnd edge, 3 Z-nbrs each)* | **`AB_bal (e14)`:** `Z3` **72.59%** vs. `Z6` **85.69%** *(ratio **1.96×**, no collapse)* | **`Penrose_1 (e14)`:** **77.51%** vs. **77.71%** *(1.01×)*<br>**`Penrose_2 (e4)`:** **80.82%** vs. **81.12%** *(1.02×)* |
| **Hallway vs. Corner Ear** *(deg-2 tip)* | **`AB_1 (e14)`:** `Z3` **15.54%** vs. `Z6` **92.19%** *(ratio **16.14×**)* | **`Penrose_ear (e13)`:** `Z7` **14.23%** vs. `Z6` **95.66%** *(ratio **26.67×**)* |

# Scale-Ladder `d=(3,3) → d=(4,4)` Handback: Narrow-Now Loosening and the End of the `k=1` Corner-Ear Bottleneck

*Branch: `experiment/scale-ladder-d4-2026-11-27`. Pre-registered protocol (`H1`, `H2`, `H3`) frozen before scoring in commit [`5665179`](https://github.com/kekekatie/geometric-impedance/commit/5665179). Result commit: this direct child. Exact `(3,3)` decoder with 128-bit safe `SIGP_LO/SIGP_HI` packing (`nd_infer.py` untouched), `p = 0.001`, `CorrectedPatchCode`, exhaustive $k \le 2$ ordinary faults; **2,473,912** new `d=(4,4)` site-histories, **0 full-scan mismatches**, `max_posterior_difference = 0.0`.*

---

## Complete 2×2 `d=(4,4)` Results (`n = 26–28`, 13 Tiles Each)

| Site (`d=(4,4)`) | Local scar pair | `n` | Histories | Full gain (`pp`) | **Narrow Now (`intact`)** | Bulk `%` | Boundary `%` | Ratio | Neither $G_0$ | **$I$ (`%`)** *(100% $k=2$)* |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **`AB_d4_mid`** | Bulk(0,4) + MidYard(1,3) | 26 | 594,448 | `+0.004282` | **`68.14%`** | 37.47% | 30.86% | **1.22×** | 0.000% | **`+0.2%`** (`+0.000009 pp`) |
| **`AB_d4_ear`** | Bulk(0,4) + CornerEar(2,2) | 28 | 690,568 | `+0.005230` | **`57.10%`** | 25.84% | 31.26% | **1.21×** | 0.319% | **`-0.3%`** (`-0.000017 pp`) |
| **`Pen_d4_mid`** | Bulk(0,4) + MidYard(1,3) | 26 | 594,448 | `+0.004197` | **`55.01%`** | 29.65% | 29.45% | **1.01×** | 0.205% | **`+3.9%`** (`+0.000163 pp`) |
| **`Pen_d4_ear`** | Bulk(0,4) + CornerEar(2,2) | 26 | 594,448 | `+0.002884` | **`66.96%`** | 26.19% | 26.49% | **1.01×** | 0.298% | **`-14.6%`** (`-0.000421 pp`) |

*Note: In every single `d=(4,4)` site, `I_by_k = [0.0, 0.0, I_k2]` — $k=0$ and $k=1$ contribute literally `0.00000000 pp`.*

---

## Verdicts Against Pre-Registered Hypotheses (`5665179`)

1. **H1 — CONFIRMED 4-for-4 (The Narrow Now Loosens at `d=4`):**
   - At `d=(3,3)` (on-route), the 8-reading local bracket recovered **97.3–99.7%** of full-archive gain.
   - At **`d=(4,4)`** (on-route), Narrow-Now recovery drops cleanly to **55.0–68.1%** across all four sites in both tilings: **32–45%** of the archive advantage now lives beyond Ring 1 (in Ring 2) because weight-4 logicals reach past the immediate 4-check bracket.
2. **H2 — CLEANLY FALSIFIED (The 16–27× Corner-Ear Bottleneck Is a `d=3` / $k=1$ Effect!):**
   - Contrary to H2, Bulk vs. Corner Ear at `d=(4,4)` shows **no** 16–27× collapse — face costs are nearly balanced (`1.21×` on `AB_d4_ear`, `1.01×` on `Pen_d4_ear`).
   - Physical reason: the 16–27× Hallway-vs.-Ear collapse at `d=3` lived in the $k=1$ single-fault channel; at `d=4`, $k=1$ vanishes completely (`0.00000000 pp`), eliminating that single-face bottleneck.
3. **H3 — Clean $k=2$ Regime Shift (`MidYard → I > 0`, `CornerEar → I < 0`):**
   - Stepping from `d=3` (on-route) to `d=4` (on-route) collapses $I$ from **`+56–64%`** (massive $k=1$ redundancy) down into the **`-14.6% to +3.9%`** $k=2$ regime — matching the exact same $k=1 \to k=2$ transition discovered when burying a `d=3` scar (`experiment/dynamic-growth-scar-2026-11-25`).
   - Across both tilings, `MidYard` pairs sit slightly positive (`+0.2%`, `+3.9%`) while `CornerEar` pairs flip negative (`-0.3%`, **`-14.6%`** on `Pen_d4_ear`).

---

## Technical Note & Replay

`nd_infer.py` packs 5 detector rounds into `np.uint64`, which overflows at $\ge 13$ checks per sector (`5 × 13 = 65 > 64` bits). `run_d4_ladder.py` leaves `nd_infer.py` completely untouched and implements an exact 128-bit split (`SIGP_LO`/`SIGP_HI`) inside its `Indexed` subclass, independently verified against full-table scans with **0 mismatches** across all 4 sites.

---

## Follow-Up 1: Radial Ring-2 Lightcone Closure (All 4 `d=(4,4)` Sites)

To test whether the missing 32–45% of archive gain at `d=(4,4)` sits in Ring 2 or diffuses across the whole patch, `run_ring2_and_forensic.py` evaluated the exact dual-graph radial ladder (**Ring 1 → Ring 2 Z → Ring 2 XZ → Ring 3 Z → All Z → Full Thick**) over all 2,473,912 histories (**0 full-scan mismatches** across 7,052 spot checks, `max_posterior_difference = 0.0`).

| Site | Ring 1 (`D.star`, 4 checks) | **Ring 1 + Ring 2 Z** (checks) | Ring 1 + Ring 2 XZ | **Ring 1–3 Z** | All Z (15 checks) | Full Thick |
|---|---:|---:|---:|---:|---:|---:|
| **`AB_d4_mid`** | 68.14% | **`99.20%`** (9) | 99.20% | **`100.00%`** | 100.00% | 100.00% |
| **`AB_d4_ear`** | 57.10% | **`99.36%`** (8) | 99.36% | **`100.00%`** | 100.00% | 100.00% |
| **`Pen_d4_mid`** | 55.01% | **`96.73%`** (9) | 96.73% | **`100.00%`** | 100.00% | 100.00% |
| **`Pen_d4_ear`** | 66.96% | **`100.00%`** (7) | 100.00% | **`100.00%`** | 100.00% | 100.00% |

**Finding:** Stepping code distance from `d=3` to `d=4` steps the memory lightcone outward by **exactly one Z-face ring**:
- Ring 1 recovers **97.3–99.7%** at `d=3` → **55.0–68.1%** at `d=4`.
- Adding only the **3–5 edge-adjacent Ring-2 Z-faces** recovers **96.73–100.00%** at `d=4` (and Ring 3 closes every site to `100.00%`).
- Adding Ring-2 X-checks contributes **`0.00%`** (`0.000000 pp`) on all four sites: lightcone expansion is 100% pure Z-face propagation.

---

## Follow-Up 2: Exact $k=2$ Forensic Comparison (`Pen_d4_ear` vs. `AB_d4_ear`)

Why did Penrose's Corner Ear (`Pen_d4_ear`) reach **`I = -14.58%`** while Ammann–Beenker's Corner Ear (`AB_d4_ear`) sat at **`I = -0.32%`**? Exact per-history decomposition of `dI = (c_bulk_only + c_bnd_only) - (c_intact + c_neither)` across all 1,285,016 histories of the two Ear sites shows that **both** Corner Ears exhibit large underlying $k=2$ synergy, driven by the exact same two modes discovered in Paper 2:

| Metric (`100% k=2`) | **`Pen_d4_ear`** (`I = -14.58%`) | **`AB_d4_ear`** (`I = -0.32%`) |
|---|---:|---:|
| Nonzero `dI` histories | 185 | 476 |
| **Gross Synergy (`dI < 0`)** | **`-34.23%`** | **`-39.39%`** |
| **Gross Redundancy (`dI > 0`)** | **`+19.64%`** | **`+39.07%`** |
| Mode `[1, 1, 0, 1]` (*Corner-Ear-only misleads*) | **`-19.94%`** (67 hist) | `-8.61%` (54 hist) |
| Mode `[1, 0, 1, 1]` (*Bulk-only misleads*) | `-2.98%` (10 hist) | `-7.66%` (48 hist) |
| Mode `[1, 0, 0, 0]` (*Pure AND-gate straddling pair*) | **`-10.71%`** (36 hist) | **`-17.07%`** (107 hist) |
| Mode `[1, 1, 1, 0]` (*Classic OR-gate backup*) | `+6.85%` (23 hist) | **`+14.83%`** (93 hist) |
| Mode `[0, 1, 1, 1]` (*Both-kept over-constrains*) | `+1.79%` (6 hist) | **`+13.24%`** (83 hist) |

**Physical mechanism:**
- **`AB_d4_ear` is a near-exact cancellation, not an absence of synergy:** its `-39.39%` gross synergy is cancelled by `+39.07%` gross redundancy, and its two one-sided-misleads channels are nearly symmetric (`-8.61%` vs. `-7.66%`).
- **`Pen_d4_ear` breaks the balance via a 6.7× Corner-Ear-only-misleads asymmetry:** in its tight 3-neighbor corner (`R2_Z = {Z7, Z9, Z12}`, lost edge `q15` directly on `logical_Z`), keeping *only* the Corner Ear `Z10` without the Bulk face `Z8` actively misleads the decoder (`-19.94%`, 67 histories) compared to keeping neither face, while pure AND-gate straddling pairs (e.g., `X16`/`X23` on `Z10` paired with `X18` on `Z8`) add another `-10.71%` (36 histories). Because gross redundancy is only half as large (`+19.64%`), synergy dominates cleanly at `-14.58%`.

```sh
python3 exploratory/scale_ladder_d4_2026-11-27/run_d4_ladder.py
python3 exploratory/scale_ladder_d4_2026-11-27/run_ring2_and_forensic.py --site Pen_d4_ear --forensic
python3 exploratory/scale_ladder_d4_2026-11-27/run_ring2_and_forensic.py --site AB_d4_ear --forensic
```

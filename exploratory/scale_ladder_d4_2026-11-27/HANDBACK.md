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

```sh
python3 exploratory/scale_ladder_d4_2026-11-27/run_d4_ladder.py
```

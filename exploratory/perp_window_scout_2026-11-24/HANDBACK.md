# Exploratory Lead Note: Perpendicular-Space Acceptance Window vs. QEC Decoder Behaviour

*Status: exploratory lead (1 clean matched pair scored so far; not a family-wide claim). Branched cleanly off `claude/aperiodic-predict-2026-11-20` with zero sealed files modified.*

![Perpendicular-space acceptance window map](results/perp_window_map.png)

---

## 1. Complete Pool Scout (3,073 Frozen Cuts, 9,255 Eligible-Edge Instances)

Across all `1,282` AB (`3,892` eligible-edge instances) and `1,791` Penrose (`5,363` eligible-edge instances) `n=21, d=(3,3)` cuts from the frozen disk-cut pool (`exploratory/aperiodic_predict_2026-11-20/src/geom_select.py`), we computed each endpoint's exact Euclidean distance to the acceptance-window boundary (`window_margin`: AB octagon edge distance; Penrose layer-pentagon convex-hull edge distance):

- **Before controlling for endpoint degree (Simpson's paradox):** On-route edges appear deeper inside the window in both tilings (`AB`: mean `0.591` vs. `0.378`; `Penrose`: `0.352` vs. `0.302`) simply because shortest X-logical routes prefer higher-degree hubs, which live closer to the window center.
- **After holding exact endpoint degrees fixed:**
  - **AB:** The gap disappears (`(5,5)`: `0.7071` vs. `0.7071`, diff `0.0000`; `(4,6)`: `0.646` vs. `0.656`).
  - **Penrose:** The sign **flips** in **5 of 6** matched degree strata (`(3,4)`, `(3,5)`, `(3,6)`, `(3,7)`, `(5,6)`) — at *fixed* vertex degree, on-route Penrose edges actually sit **closer to the pentagon rim** than off-route edges of the exact same degree (for `(3,6)`, every on-route edge has `min_margin = 0.0000`, right on the pentagon rim).

---

## 2. Confound Catch: `scored_logical_Z` Placement Matters

An initial matched `(3,5)` Penrose Middle-Yard pair (`Penrose_rim` vs. `Penrose_center`, where `scored_logical_Z` crossed the lost edge on the rim cut but bypassed it on the center cut) produced `+0.1206 pp` vs. `+0.0729 pp` — mirroring `Penrose_1` (`+0.1223 pp`, `LZ` crosses lost edge) vs. `Penrose_2` (`+0.0723 pp`, `LZ` misses lost edge). Furthermore, bypassing the lost edge tilted single-face omission toward whichever face `LZ` threaded (`65.4%` vs. `97.1%`) while leaving mutual backup $I$ high (`62.9%`).

**Control rule established:** Any fair Rim-vs.-Center decoder comparison must hold **`scored_logical_Z` crossing the lost edge** fixed on both cuts.

---

## 3. Clean Matched Pair (`Penrose_rim_LZ` vs. `Penrose_center_LZ`)

Both cuts are **Penrose `10 X / 10 Z` Mirror Middle Yards**, identical endpoint degrees `(3, 7)`, identical mirror-twin corner degrees `((3, 3, 3, 7), (3, 3, 3, 7))`, identical boundary distances `(1, 1)`, unique weight-3 X-logical (`n_w3 = 1`), and **`scored_logical_Z` crossing the lost edge** on both:

- **`Penrose_rim_LZ`:** `spec=(15, 0, 0, 10)`, `corners=(4, 6, 10, 14)`, `e14 (q10)`, `LZ=[7, 10, 20]`, `min_margin = 0.0000`, `mean_margin = 0.3455`.
- **`Penrose_center_LZ`:** `spec=(15, 1, 0, 10)`, `corners=(7, 12, 16, 18)`, `e4 (q3)`, `LZ=[12, 3, 0]`, `min_margin = 0.5279`, `mean_margin = 0.6094`.

Exhaustive `(3,3)` decoder results (`385,648` histories/site, `p = 0.001`, `1,536` unaccelerated full-scan verification checks per site, **0 mismatches**, `max_posterior_difference = 0.0`):

| Measure | **`Penrose_rim_LZ`** *(fence, `min_m = 0.000`)* | **`Penrose_center_LZ`** *(center, `min_m = 0.528`)* |
|---|---:|---:|
| **Full-archive gain (`thick − thin`)** | **`+0.121516 pp`** | **`+0.099735 pp`** *(Rim `+21.8%` higher)* |
| **Narrow Now (`intact`)** | **99.45%** | **99.13%** |
| **Face omission (A / B)** | **78.61%** vs. **78.49%** *(1.01×)* | **73.39%** vs. **73.53%** *(1.01×)* |
| **Neither face ($G_0$)** | **0.0759%** | **0.0925%** |
| **Mutual backup $I$** | **`+0.069961 pp` (`57.6%`)** | **`+0.047572 pp` (`47.7%`)** |
| **Endpoint X-omission flips** *(both `0.000000 pp` net)* | **`74` (`X3`) & `68` (`X8`)** | **`0` (`X0`) & `0` (`X6`)** |

---

## 4. Next Steps (When We Return)

1. Test **2–3 additional clean `LZ`-crossing Rim-vs.-Center pairs** (e.g., from the `(5, 6)`, `(3, 5)`, and `(4, 5)` Penrose buckets, plus AB `(4, 5)` Middle Yards) to see whether the Rim's higher full gain, higher mutual backup $I$, and active endpoint steering hold systematically or are patch-specific.
2. Check whether **Ring-2 / Ring-3 graph differences** (which `perp` space encodes!) account for the `+21.8%` gain gap and `74/68` vs. `0/0` endpoint steering split.
3. Also parked on the shelf for later: **Distance-5 bulk test** (no boundary ears nearby) and **Horizon Note §6** ($p(r)$ vs. Hankel admissibility cone).

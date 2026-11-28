# Pre-Registered Protocol: Two-Scar Lightcone Interaction on `d=(4,4)` Aperiodic Patches

*Branch: `experiment/two-scar-lightcone-d4-2026-11-28`. Frozen before any Phase 2 two-scar decoder scoring.*

---

## 1. Scientific Question

In `experiment/scale-ladder-d4-2026-11-27` (`ad5a876`, `fcefbfb`), we established that stepping aperiodic surface-code patches from `d=(3,3)` to `d=(4,4)` eliminates the $k=1$ single-fault channel (`0.00000000 pp`) and gives every on-route scar a sharp, exact **2-ring Z-face memory lightcone** (Ring 1 recovers 55.0–68.1%; Ring 1 + Ring 2 Z-faces recovers **96.73–100.00%**; Ring-2 X-checks add `0.00%`).

**Core question:** When **two** on-route edges $(e_A, e_B)$ are lost simultaneously on a `d=(4,4)` aperiodic patch, do they interact when their 2-ring Z-face memory lightcones overlap?

---

## 2. Two-Erasure Physical Model & Exact Decoder Extension

We keep `nd_infer.py` and all prior sealed experiment code completely untouched and extend our 128-bit safe `Indexed` subclass (`SIGP_LO`/`SIGP_HI`) to **simultaneous two-site erasure** $(e_A, e_B)$ sharing onset $t_0 \in \{1, 2\}$:
- **Exact erasure marginal:** Instead of summing over $e \in \{0, 1\}$ (weight $1/2$ each), each sector marginal sums over the 4 joint free-Pauli states $(e_A, e_B) \in \{(0,0), (1,0), (0,1), (1,1)\}$ (weight $1/4$ each) with XOR detector/boundary/logical shifts $0$, $s_A$, $s_B$, $s_A \oplus s_B$.
- **Exact exhaustive ensemble:** Every ordinary-fault configuration $k \in \{0, 1, 2\}$ at $p = 0.001$ is evaluated across all **32 simultaneous erasure variants** $(t_0, v_{X,A}, v_{Z,A}, v_{X,B}, v_{Z,B}) \in \{1, 2\} \times \{0, 1\}^4$.
- **Exact validation:** Every run spot-checks the indexed two-erasure prefilter against full-table scans (`direct_fullscan_mismatches == 0`, `max_posterior_difference <= 1e-12`).
- **Single-scar baselines:** $G(A)$ and $G(B)$ are scored on the exact same patch with the exact same `w_dec=3, w_frame=3` decoder over the standard 8 single-erasure variants.

---

## 3. Selected `d=(4,4)` Patches & Pre-Registered Three-Regime Pair Matrix

To eliminate patch-to-patch confounds, **all three regimes are hosted on a single `d=(4,4)` patch per tiling** (identical $n$, $H_X$, $H_Z$, and fault pool within each tiling):

- **Penrose patch (`Pen_d4_mid`, existing from `5665179`):** `m=13` tiles, `ci=3`, `aspect=1.25`, `corners=(6, 10, 14, 18)` — `n=26`, `12X / 13Z`, `d=(4,4)`, `pool=385`, `74,306` configs (`2,377,792` two-scar histories/pair).
- **Ammann–Beenker patch (`AB_2scar`, new deterministic cut):** `m=15` tiles, `ci=2`, `aspect=1.5`, `corners=(0, 3, 8, 15)` — `n=31`, `15X / 15Z`, `d=(4,4)`, `pool=460`, `106,031` configs (`3,392,992` two-scar histories/pair).

| Tiling / Patch | Regime | Pair $(q_A, q_B)$ | Local Face Roles | Shared Ring-1 Z (`ovR1`) | Shared Ring-1–2 Z (`ovR12`) | Union `\|R12\| / nz` | Erased Distance $(d_X^{\text{er}}, d_Z^{\text{er}})$ |
|---|---|---|---|:---:|:---:|:---:|:---:|
| **Penrose** (`Pen_d4_mid`, `n=26`) | **1. Separated Control** | `(q9, q11)` | `(Bulk, Ear)` + `(Bulk, MidYard)` | `0` | **`0`** | `11 / 13` | `(3, 3)` |
| **Penrose** (`Pen_d4_mid`, `n=26`) | **2. Lightcone-Touching** | `(q3, q9)` | `(Bulk, MidYard)` + `(Bulk, Ear)` | `0` | **`3`** | `9 / 13` | `(3, 3)` |
| **Penrose** (`Pen_d4_mid`, `n=26`) | **3. Same-Route Collision** | `(q4, q5)` | `(Bulk, MidYard)` + `(Bulk, MidYard)` | `1` | **`6`** | `6 / 13` | **`(2, 4)`** |
| **AB** (`AB_2scar`, `n=31`) | **1. Separated Control** | `(q12, q18)` | `(Bulk, Ear)` + `(Bulk, MidYard)` | `0` | **`0`** | `11 / 15` | `(3, 3)` |
| **AB** (`AB_2scar`, `n=31`) | **2. Lightcone-Touching** | `(q5, q12)` | `(Bulk, MidYard)` + `(Bulk, Ear)` | `0` | **`3`** | `8 / 15` | `(3, 3)` |
| **AB** (`AB_2scar`, `n=31`) | **3. Same-Route Collision** | `(q10, q20)` | `(Bulk, MidYard)` + `(Bulk, MidYard)` | `1` | **`5`** | `8 / 15` | **`(2, 3)`** |

*(Optional bonus sub-regime on `Pen_d4_mid` if runtime permits: **Ring-1-Touching off-route** `(q3, q4)` with `ovR1=1, ovR12=5, d_er=(3,4)`.)*

---

## 4. Two-Scar Interaction Metrics

For every pair $(A, B)$, we score `thin`, `ring1_union` ($D.\text{star}_A \cup D.\text{star}_B$), `ring2_union` (Ring-1 union + Ring-2 Z-faces of $A$ and $B$), and `thick`, plus the individual single-scar baselines $G(A)$ and $G(B)$ on the same patch:

1. **Two-Scar Interaction Excess (Super-/Sub-Additivity):**
   $$\Delta G_{AB} = G_{\text{full}}(A, B) - \bigl[G_{\text{full}}(A) + G_{\text{full}}(B)\bigr], \qquad R_{AB} = \frac{G_{\text{full}}(A, B)}{G_{\text{full}}(A) + G_{\text{full}}(B)}.$$
   We also report the exact fault-weight breakdown $\Delta G_{AB}^{(k)}$ for $k \in \{0, 1, 2\}$.
2. **Union Lightcone Closure:**
   - **Narrow-Now union recovery:** $F_{1}(A, B) = G_{\text{ring1\_union}}(A, B) / G_{\text{full}}(A, B)$.
   - **Ring-2 union recovery:** $F_{2}(A, B) = G_{\text{ring2\_union}}(A, B) / G_{\text{full}}(A, B)$.

---

## 5. Pre-Registered Directional Hypotheses

1. **H1 (Separated Control → Clean Additivity):** When `ovR12 = 0` and $d_X^{\text{er}} = 3$, the $k=1$ channel remains strictly zero (`0.0 pp`) and the two scars do not couple: $R_{AB} \approx 1.00$ ($\Delta G_{AB} \approx 0$), with Ring-2 union recovery remaining $\ge 95\%$.
2. **H2 (Lightcone-Touching → Pure $k=2$ Coupling Test):** When `ovR1 = 0, ovR12 = 3` and $d_X^{\text{er}} = 3$, the $k=1$ channel remains strictly zero (`0.0 pp`); any deviation from $R_{AB} = 1$ ($\Delta G_{AB} \ne 0$) is a **pure $k=2$ lightcone-overlap interaction** mediated by the 3 shared Ring-2 Z-faces.
3. **H3 (Same-Route Collision → $k=1$ Re-Ignition & Super-Additive Amplification):** When $(e_A, e_B)$ share a shortest weight-4 $X$-logical ($d_X^{\text{er}} = 2$), the $k=1$ single-fault channel re-opens at $O(p)$ rather than $O(p^2)$, driving strong super-additive amplification $G_{\text{full}}(A, B) \gg G_{\text{full}}(A) + G_{\text{full}}(B)$ ($R_{AB} \gg 1$, dominated by $k=1$).

---

## 6. Estimated Phase 2 Runtime Budget

- **Penrose (`Pen_d4_mid`, `n=26`, 4 queries/history):** ~40–60 min per two-scar pair (~20 min per single-scar baseline). Running all 3 pairs in parallel takes **~1 hour wall-clock** (+ ~25 min for the 5 single-scar baselines in parallel).
- **Ammann–Beenker (`AB_2scar`, `n=31`, 4 queries/history):** ~1.5–2.2 hours per two-scar pair (~35–45 min per single-scar baseline). Running all 3 pairs in parallel takes **~2–2.5 hours wall-clock** (+ ~45 min for the 5 single-scar baselines in parallel).
- **Recommended launch order:** Run Penrose (`Pen_d4_mid`) first (fast ~1.5 hr end-to-end validation of all 3 regimes), then launch `AB_2scar`!

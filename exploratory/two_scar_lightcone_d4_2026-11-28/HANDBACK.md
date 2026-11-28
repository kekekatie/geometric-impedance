# Two-Scar Lightcone Interaction on `d=(4,4)` Aperiodic Patches — Handback

*Branch: `experiment/two-scar-lightcone-d4-2026-11-28`. Pre-registered protocol (`H1`, `H2`, `H3`) frozen before scoring in commit [`cd555f5`](https://github.com/kekekatie/geometric-impedance/commit/cd555f5). Exact `(3,3)` bounded decoder extended to simultaneous two-site erasure (`Indexed2`, 128-bit safe `SIGP_LO`/`SIGP_HI`, `nd_infer.py` untouched), `p = 0.001`, `CorrectedPatchCode`, exhaustive $k \le 2$ ordinary faults across 32 simultaneous erasure variants; **24,525,832** total histories across 6 two-scar pairs + 10 single-scar baselines, **11,520 full-table spot checks**, **0 mismatches**, `max_posterior_difference = 0.0`.*

---

## Complete Three-Regime Results (Both Tilings Hosted on One Patch Each)

| Pair | Tiling (`n`) | Regime (`ovR1`, `ovR12`, $d_X^{\text{er}}$) | $G(A) + G(B)$ (`pp`) | **$G(A, B)$ (`pp`)** | **Ratio $R_{AB}$** | Excess $\Delta G_{AB}$ (`pp`) | $k$-Breakdown `[k0, k1, k2]` | Union **R1 → R2** | Shared Bridges ($\le 6$) |
|---|---|---|---:|---:|---:|---:|---|---|---|
| **`Pen_sep`** `(q9, q11)` | Penrose (`26`) | Separated (`0, 0, 3`) | `0.006797` | **`0.007724`** | **`1.136×`** (`+13.6%`) | `+0.000927` | `[0, 0, 0.007724]` | `64.75% → 99.33%` | `{}` |
| **`Pen_touch`** `(q3, q9)` | Penrose (`26`) | Lightcone-Touch (`0, 3, 3`) | `0.007938` | **`0.008314`** | **`1.047×`** (`+4.7%`) | `+0.000375` | `[0, 0, 0.008314]` | **`71.79%`** `→ 98.55%` | `{}` |
| **`Pen_coll`** `(q4, q5)` | Penrose (`26`) | Same-Route (`1, 6, 2`) | `0.006505` | **`0.085114`** | **`13.084×`** | `+0.078609` | `[0, 0.060014, 0.025100]` | **`98.12%`** `→ 99.57%` | `{4:1, 5:2, 6:2}` |
| **`AB_sep`** `(q12, q18)` | AB (`31`) | Separated (`0, 0, 3`) | `0.004430` | **`0.005998`** | **`1.354×`** (`+35.4%`) | `+0.001567` | `[0, 0, 0.005998]` | `60.43% → 94.43%` | `{}` |
| **`AB_touch`** `(q5, q12)` | AB (`31`) | Lightcone-Touch (`0, 3, 3`) | `0.006006` | **`0.009550`** | **`1.590×`** (`+59.0%`) | `+0.003545` | `[0, 0, 0.009550]` | **`75.05%`** `→ 92.88%` | **`{5:2, 6:3}`** |
| **`AB_coll`** `(q10, q20)` | AB (`31`) | Same-Route (`1, 5, 2`) | `0.008653` | **`0.101036`** | **`11.677×`** | `+0.092384` | `[0, 0.063911, 0.037125]` | **`98.15%`** `→ 99.59%` | `{4:1, 5:7, 6:12}` |

### Single-Scar Baselines on the Exact Same Patches (All 100% $k=2$, $k=1 = 0.0\text{ pp}$)

- **`Pen_d4_mid` (`n=26`):** `q3 = 0.004197 pp` (`R1 55.01% → R2 96.73%`), `q4 = 0.003244 pp` (`59.26% → 97.88%`), `q5 = 0.003261 pp` (`51.58% → 97.89%`), `q9 = 0.003742 pp` (`52.52% → 93.35%`), `q11 = 0.003055 pp` (`60.67% → 93.82%`).
- **`AB_2scar` (`n=31`):** `q5 = 0.003159 pp` (`R1 65.57% → R2 98.99%`), `q10 = 0.006238 pp` (`67.95% → 100.00%`), `q12 = 0.002847 pp` (`48.60% → 91.85%`), `q18 = 0.001583 pp` (`59.60% → 97.98%`), `q20 = 0.002415 pp` (`56.62% → 94.37%`).

---

## Verdicts Against Pre-Registered Hypotheses (`cd555f5`)

1. **H1 (Separated Control → Clean Additivity) — PARTIALLY FALSIFIED / NEW DISCOVERY:**
   - As predicted, $k=1$ stays strictly `0.000000 pp` on both `Pen_sep` and `AB_sep`, and Ring-2 union stays high (`99.33%` / `94.43%`).
   - **However, separated scars do NOT stay strictly additive ($R_{AB} = 1.00$):** even with `ovR12 = 0` and zero shared logical bridges of weight $\le 6$, both tilings show **`+13.6%` (`Pen_sep`) to `+35.4%` (`AB_sep`) pure $k=2$ super-additivity** under simultaneous onset! When two scars share an onset event $t_0 \in \{1, 2\}$, archive readings around scar A help jointly lock the onset time for scar B while `thin` suffers doubled erasure entropy across the patch.
2. **H2 (Lightcone-Touching → Pure $k=2$ Overlap Coupling) — CONFIRMED WITH A CLEAR GEOMETRIC MECHANISM:**
   - $k=1$ remains strictly `0.000000 pp` on both `Pen_touch` and `AB_touch`.
   - **Two distinct lightcone-overlap signatures emerge cleanly:**
     - **Ring-1 union jump (both tilings):** Because each scar's Ring-1 star reaches into the other scar's Ring-2 lightcone, Narrow-Now union recovery jumps from `49–66%` (single-scar) up to **`71.79%`** (`Pen_touch`) and **`75.05%`** (`AB_touch`) — cleanly above the Separated Controls (`64.75%`, `60.43%`).
     - **Weight-5 logical bridges drive the big `AB_touch` boost:** `AB_touch` (`q5, q12`) hosts **2 weight-5 $X$-logical bridges** passing through *both* scars (`5 - 2 = 3` remaining weight, opening a new $k=2$ error channel) and jumps to **`1.590×` (`+59.0%`)**, whereas `Pen_touch` (`q3, q9`) has **0** shared bridges of weight $\le 6$ and sits at **`1.047×` (`+4.7%`)**.
3. **H3 (Same-Route Collision → $k=1$ Re-Ignition & Super-Additive Explosion) — CONFIRMED 2-for-2:**
   - Dropping $d_X^{\text{er}}$ from `4 → 2` re-ignites the $k=1$ single-fault channel (`+0.060014 pp` on `Pen_coll`, `+0.063911 pp` on `AB_coll`) and amplifies $k=2$ by `~4×`, driving a **`13.08×` (Penrose) and `11.68×` (AB)** super-additive explosion.
   - Because $k=1$ dominates again, Ring-1 union recovery snaps straight back to **`98.12%`** (`Pen_coll`) and **`98.15%`** (`AB_coll`) — matching to 3 significant figures across both tilings — with Ring-2 union at **`99.57%`** / **`99.59%`**.

---

## Follow-Up: Known-Onset ($t_0$) Ablation (Astra's Timing-vs.-Space Test)

*Pre-registered checks (`T1`, `T2`) frozen before scoring in [`PROTOCOL_KNOWN_T0.md`](./PROTOCOL_KNOWN_T0.md) (`7a7ad60`). Exact replay over **15,869,656** known-$t_0$ histories (**7,200 full-table + Z-sector spot checks**, **0 mismatches**, `max_posterior_difference = 2.22e-16`).*

### Side-by-Side Comparison: Unknown $t_0$ vs. Known $t_0$

| Pair (Shared Bridges $\le 6$) | Unknown $t_0$: $G(A)+G(B)$ | Unknown $t_0$: $G(A,B)$ | Unknown $t_0$: **$R_{AB}$** ($\Delta G_{AB}$) | Known $t_0$: $G(A)+G(B)$ | Known $t_0$: $G(A,B)$ | Known $t_0$: **$R_{AB}$** ($\Delta G_{AB}$) | Timing Slice Removed (`pp`, `%` of $\Delta G$) | Known-$t_0$ Union **R1 → R2** |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **`Pen_sep`** `(q9, q11)` (`0`) | `0.006797` | `0.007724` | **`1.136×`** (`+0.000927`) | `0.007175` | `0.007818` | **`1.090×`** (`+0.000644`) | **`-0.000283 pp` (`30.6%`)** | `66.63% → 99.34%` |
| **`Pen_touch`** `(q3, q9)` (`0`) | `0.007938` | `0.008314` | **`1.047×`** (`+0.000375`) | `0.008273` | `0.008359` | **`1.010×`** (`+0.000086`) | **`-0.000289 pp` (`77.1%`)** | `72.90% → 98.77%` |
| **`AB_sep`** `(q12, q18)` (`0`) | `0.004430` | `0.005998` | **`1.354×`** (`+0.001567`) | `0.004814` | `0.006094` | **`1.266×`** (`+0.001279`) | **`-0.000288 pp` (`18.4%`)** | `61.15% → 94.62%` |
| **`AB_touch`** `(q5, q12)` (`2× w5`) | `0.006006` | `0.009550` | **`1.590×`** (`+0.003545`) | `0.006477` | `0.009764` | **`1.507×`** (`+0.003287`) | **`-0.000258 pp` (`7.3%`)** | `76.09% → 93.12%` |

### Verdicts Against Pre-Registered Checks (`7a7ad60`)

1. **Universal Shared-Clock Floor (`~0.00026–0.00029 pp`):** Across all four pairs in both tilings, revealing $t_0$ removes an almost identical shared-clock timing slice (`0.000258` to `0.000289 pp`) — proving that shared timing creates a clean, tiling-independent coupling floor between simultaneous losses.
2. **T2 (Spatial Bridge Residual on `AB_touch`) — CONFIRMED:** With $t_0$ known, **`92.7%`** of `AB_touch`'s excess survives (`+0.003287 pp`, **`R_AB = 1.507×`**), directly isolating the pure spatial contribution of its 2 shared weight-5 $X$-logical bridges. By contrast, `Pen_touch` (3 shared Ring-2 Z-faces but **0** shared bridges $\le 6$) collapses by `77.1%` straight down to **`1.010×`** (`+0.000086 pp`).
3. **T1 (Timing Link at a Distance on `Pen_sep`, `AB_sep`) — PARTIALLY CONFIRMED + NON-LOCAL RESIDUAL:** Revealing $t_0$ removes the exact same `~0.00028–0.00029 pp` timing slice (`30.6%` on `Pen_sep`, `18.4%` on `AB_sep`), yet a genuine non-timing residual survives even when $t_0$ is known and `ovR12 = 0` (`1.090×` on `Pen_sep`, `1.266×` on `AB_sep`). Even without overlapping Ring-2 Z-faces or short bridges, two simultaneous erasures on the same patch still interact through the global `thin` logical-parity / committed-frame inference.

---

## Replay

```sh
python3 exploratory/two_scar_lightcone_d4_2026-11-28/run_two_scar.py --selftest
python3 exploratory/two_scar_lightcone_d4_2026-11-28/run_two_scar.py --singles Pen_d4_mid
python3 exploratory/two_scar_lightcone_d4_2026-11-28/run_two_scar.py --pair Pen_sep
python3 exploratory/two_scar_lightcone_d4_2026-11-28/run_two_scar.py --pair Pen_touch
python3 exploratory/two_scar_lightcone_d4_2026-11-28/run_two_scar.py --pair Pen_coll
python3 exploratory/two_scar_lightcone_d4_2026-11-28/run_known_t0_ablation.py --selftest
python3 exploratory/two_scar_lightcone_d4_2026-11-28/run_known_t0_ablation.py --pair AB_touch
```

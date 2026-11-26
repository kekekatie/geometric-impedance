# Sequel Paper Blueprint — Dynamic Accretion, Scar Healing, and Burial-Induced Synergy

*Branch: `experiment/dynamic-growth-scar-2026-11-25`. Locks down the complete 6-for-6 dynamic growth sweep (`8eec0bf`, direct child of pre-registration `c510bf5`) and the exact read-only Phase 3 forensic dissection of the negative-$I$ sign-flip.*

---

## Core Story (Tight, Self-Contained Sequel to *Which Old Readings Matter?*)

In *Which Old Readings Matter?*, static 2×2 role-reversal snapshots showed that a protruding degree-2 **Corner Ear** concentrates omission cost onto its partner **Hallway** face (16–27×) and depresses mutual face backup $I$ to ~10–11%, whereas **Mirror Middle Yards** share the load and maintain ~56–63% mutual backup.

Here we move from static snapshots to **step-by-step boundary tile accretion** around the exact same physical lost edge on `AB_1 (e14)` and `Penrose_ear (e13)` (2,415,288 new site-histories, `(3,3)` decoder, $p = 0.001$, **0** full-scan mismatches). Every pre-registered directional prediction (**P1, P2, P3**) hit 6-for-6, revealing a universal **3-phase life cycle** across both tilings — and an unexpected, exact **$k=2$ sign-flip from redundancy ($I > 0$) to synergy ($I < 0$)** upon burial.

---

## Pillar 1 — The 6-for-6 Pre-Registered Sweep (Universal 3-Phase Life Cycle)

| Phase | Steps | `n_w3_on` | Full gain (`pp`) | Narrow Now | Hallway vs. Ear | Backup $I$ (`%`) |
|---|---|---:|---:|---:|---|---:|
| **Phase 1: Exposed Ear** | `A0` (`AB_1`), `B0` (`Penrose_ear`) | 2 | `+0.099–0.103` | 97.3–98.8% | **16.1–26.7×** collapse | **`+10.4–10.9%`** |
| **Phase 2: Healed & Persistent** | `A1` (`+762`), `B1` (`+158`), `B2` (`+158,+156`) | 1 | `+0.098–0.144` | 98.7–99.4% | **1.02–1.90×** balanced | **`+57.5–63.7%`** |
| **Phase 3: Buried & Dissipated** | `A2` (`+762,+764`), `A1-H` (`+755`), `B1-H` (`+289`) | 0 | **`+0.0078–0.0113`** | 65.3–66.1% | 1.06–1.14× (~30% each) | **`-4.5% to -8.8%`** |

---

## Pillar 2 — Forensic Proof of the Phase 3 Sign-Flip (Redundancy → Synergy)

Using $I = (G_{\text{hall}} + G_{\text{ear}}) - (G_{\text{both}} + G_{\text{neither}})$, where $I > 0$ is substitutable backup and $I < 0$ is synergy:

1. **Exact four-term decomposition:**
   - `A1` (Phase 2): $G_{\text{both}}=0.096708$, $G_{\text{hall}}=0.083088$, $G_{\text{ear}}=0.070855$, $G_0=0.000010$ $\implies$ **$I = +0.057226$ pp (`+58.39%`)**.
   - `B1` (Phase 2): $G_{\text{both}}=0.142706$, $G_{\text{hall}}=0.117366$, $G_{\text{ear}}=0.116831$, $G_0=0.000101$ $\implies$ **$I = +0.091390$ pp (`+63.65%`)**.
   - `A2` (Phase 3): $G_{\text{both}}=0.005698$, $G_{\text{hall}}=0.002759$, $G_{\text{ear}}=0.002598$, $G_0=0.000045$ $\implies$ **$I = -0.000385$ pp (`-4.47%`)**.
   - `A1-H` (Phase 3): $G_{\text{both}}=0.005145$, $G_{\text{hall}}=0.002136$, $G_{\text{ear}}=0.002345$, $G_0=0.000019$ $\implies$ **$I = -0.000683$ pp (`-8.77%`)**.
   - `B1-H` (Phase 3): $G_{\text{both}}=0.007400$, $G_{\text{hall}}=0.003117$, $G_{\text{ear}}=0.003647$, $G_0=0.000018$ $\implies$ **$I = -0.000653$ pp (`-5.77%`)**.
2. **100% purely $k = 2$:** Across all three buried steps (`A2`, `A1-H`, `B1-H`), $k = 0$ and $k = 1$ contribute literally **`0.00000000 pp` (0 histories)**. Every synergy history lives at $k = 2$:
   - `A2`: `-0.003651 pp` (405 synergy hist) + `+0.003265 pp` (366 redundancy hist) = `-0.000385 pp`.
   - `A1-H`: `-0.003598 pp` (371 synergy hist) + `+0.002914 pp` (303 redundancy hist) = `-0.000683 pp`.
   - `B1-H`: `-0.003947 pp` (453 synergy hist) + `+0.003294 pp` (381 redundancy hist) = `-0.000653 pp`.
3. **The straddling-fault mechanism & two synergy modes:**
   - Every top synergy configuration ($\sum \Delta_I = -5.0$) is a **$k=2$ straddling pair**: one X-fault on the Hallway face and one X-fault on the Ear face at different early rounds ($t=0$ vs. $t=2$), or paired with a round-1 `MZ` error on the opposite face (e.g., `A2`: `('X',5,0)+('X',11/14/15,2)`; `A1-H`: `('X',6,0)+('X',15/16,2)`; `B1-H`: `('X',9,0)+('X',13/17,2)`).
   - **Mode 1 — Pure AND-gate (`[1, 0, 0, 0]`):** 130 (`A1-H`), 137 (`A2`), 118 (`B1-H`) histories where both faces together decode right while either alone or neither fails.
   - **Mode 2 — One-sided witness misleads (`[1, 1, 0, 1]` + `[1, 0, 1, 1]`):** 199 (`A1-H`), 238 (`A2`), 288 (`B1-H`) histories where keeping only one face misleads the decoder relative to keeping neither, while seeing both resolves the two-sided timing ambiguity.

---

## Scope Separation (Keeping Paper 2 Clean)

- **Paper 2 (this branch):** Dynamic growth around a live scar at $d=(3,3)$ — 6-for-6 pre-registered sweep, 3-phase life cycle, and exact $k=2$ straddling-fault proof of the redundancy $\to$ synergy flip.
- **Paper 3 (saved for next):** Scale & compactness — larger distances ($d=5$), thicker fronts, and testing whether burial time scales with compactness (opening the quantitative door to the meson/strangeness work).

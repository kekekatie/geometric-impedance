# Pre-Registered Protocol: Dynamic Tile Accretion Around a Live Scar

*Branch: `experiment/dynamic-growth-scar-2026-11-25` (branched off `claude/aperiodic-predict-2026-11-20`). This protocol is frozen and committed **before** any new decoder histories are scored.*

---

## 1. Core Question

In our static 2×2 role reversal (`experiment/role-reversal-omission-2026-11-22`), replacing a protruding degree-2 **Corner Ear** with a second **Middle Yard** eliminated the 16–27× omission-cost collapse and lifted mutual face backup $I$ from ~10–11% to ~56–63%.

Here we test **step-by-step boundary accretion** directly onto the verified Hallway-vs.-Corner-Ear baselines (`AB_1` and `Penrose_ear`), keeping the **exact same physical lost edge** fixed while adding adjacent parent tiles:
1. **Dissipation (Corner-Ear swallowing):** When new tiles accrete over the exposed Corner Ear — first half-swallowing it (eliminating its degree-2 tip), then completely burying it into the bulk (`bndS = 0, znbr = 4`) — does the scar smooth out and then dissipate?
2. **Persistence vs. Burial (Hallway control):** When a single tile accretes directly over the **Hallway** instead (burying the Hallway into the bulk while leaving the Corner Ear exposed), does the shortest X-logical route immediately detour, collapsing the scar's archive gain?

---

## 2. Frozen Growth Sequences (4 Steps per Tiling)

All steps preserve a valid topological disk (`pilot.disk`), valid 4-arc rough/smooth boundary conditions with $k=1$, $d = (3,3)$, and the **exact same physical lost edge** (identified by its 4D/5D parent lift endpoints). Every step is decoded with the exact untouched `(3,3)` decoder (`w_dec = 3`, `w_frame = 3`, $p = 0.001$, `CorrectedPatchCode`, exhaustive $k \le 2$ ordinary faults, unaccelerated full-scan verification sample).

### Sequence A — Ammann–Beenker (starting from `AB_1`, physical edge `e14`, incident parent faces `Z3 = 757` [Hallway] and `Z6 = 760` [Corner Ear])

| Step | Accretion action | Tiles | Qubits (`n`) | Check split | `d` | `n_w3_on` | Local scar geometry | Est. runtime |
|---|---|---:|---:|---|---|---:|---|---:|
| **A0** | Baseline `AB_1` *(already sealed)* | 9 | 21 | `11X / 9Z` | `(3,3)` | 2 | Hallway (`bndS=1, znbr=3`) vs. Corner Ear (`bndS=2, znbr=2, deg-2`) | sealed |
| **A1** | Half-swallow Ear (`+tile 762` on `Z6`) | 10 | **18** | `7X / 10Z` | `(3,3)` | **1** | **Mirror Middle Yards** (`bndS=1, znbr=3`, degs `(3,3,5,5)` each) | ~4 min |
| **A2** | Full-bury Ear (`+tiles 762, 764` on `Z6`) | 11 | **23** | `11X / 11Z` | `(3,3)` | **0** | Hallway (`bndS=1, znbr=3`) vs. **Buried bulk** (`bndS=0, znbr=4`) | ~14 min |
| **A1-H** | Mirror control: Bury Hallway (`+tile 755` on `Z3`) | 10 | **19** | `8X / 10Z` | `(3,3)` | **0** | **Buried bulk** (`bndS=0, znbr=4`) vs. **Exposed Ear** (`bndS=2, znbr=2, deg-2`) | ~5 min |

### Sequence B — Penrose (starting from `Penrose_ear`, physical edge `e13`, incident parent faces `Z7 = 221` [Hallway] and `Z6 = 220` [Corner Ear])

| Step | Accretion action | Tiles | Qubits (`n`) | Check split | `d` | `n_w3_on` | Local scar geometry | Est. runtime |
|---|---|---:|---:|---|---|---:|---|---:|
| **B0** | Baseline `Penrose_ear` *(already sealed)* | 10 | 21 | `10X / 10Z` | `(3,3)` | 2 | Hallway (`bndS=1, znbr=3`) vs. Corner Ear (`bndS=2, znbr=2, deg-2`) | sealed |
| **B1** | Half-swallow Ear (`+tile 158` on `Z6`) | 11 | **21** | `9X / 11Z` | `(3,3)` | **1** | **Mirror Middle Yards** (`bndS=1, znbr=3`, degs `(3,3,5,6)` each) | ~9 min |
| **B2** | Extend outer ring (`+tiles 158, 156`, adj to `158`) | 12 | **23** | `10X / 12Z` | `(3,3)` | **1** | **Mirror Middle Yards** (pushed 1 ring deeper from outer rim) | ~14 min |
| **B1-H** | Mirror control: Bury Hallway (`+tile 289` on `Z7`) | 11 | **24** | `12X / 11Z` | `(3,3)` | **0** | **Buried bulk** (`bndS=0, znbr=4`) vs. **Exposed Ear** (`bndS=2, znbr=2, deg-2`) | ~17 min |

*(Optional bonus step **B2-bury**: `+tiles 158, 228` fully buries `Z6` on Penrose at `n=26`, `d=(3,3)`, `n_w3_on=0`, est. ~28 min — runnable if B1/B2/B1-H leave any ambiguity.)*

---

## 3. Metrics Tracked at Every Step

For every step we record the exact same metric bundle used in our published Bridge Paper:
1. **Full-archive gain:** $G_{\mathrm{full}} = 100 \times (\text{thick} - \text{thin})$ (pp).
2. **Narrow-Now recovery:** $G_{\mathrm{intact}} / G_{\mathrm{full}}$ (%).
3. **Single-face omission costs & surviving gain (%):** omitting the Hallway face vs. the Corner-Ear face individually (plus face-cost ratio).
4. **Paired-face backup ($G_0$ and $I$):** covering both adjacent faces simultaneously (retaining only the 2 endpoint X-checks), and substitution interaction $I = (G_A - G_0) - (G_{AB} - G_B)$ (both in pp and as % of $G_{\mathrm{full}}$).
5. **Endpoint X-check flips & net costs.**

---

## 4. Pre-Registered Directional Predictions (Pencil Marks Before Scoring)

1. **P1 (Half-swallowing the Corner Ear — Steps A1 & B1):** Adding one tile to eliminate the Corner Ear's degree-2 tip keeps the scar on-route (`n_w3_on = 1`), **collapses the 16–27× face asymmetry** down to near-balance (both faces retaining $\ge 65\%$ of full gain), and **lifts mutual backup $I$** from ~10–11% up into the ~45–65% Middle-Yard band on *both* AB and Penrose.
2. **P2 (Burying either side into the bulk — Steps A2, A1-H, B1-H):** Once accretion completely buries either the Corner Ear (`A2`) or the Hallway (`A1-H`, `B1-H`) so that `n_w3_on` drops to `0`, the shortest weight-3 X-logical detours away from the scar and **$G_{\mathrm{full}}$ drops sharply** (toward off-route levels, $\ll 0.05\text{ pp}$), demonstrating **scar dissipation** under burial — *even when the Corner Ear remains exposed* (`A1-H`, `B1-H`).
3. **P3 (Outer-ring extension without burying the scar — Step B2):** Growing a second tile behind the newly formed Middle Yard (`+158, +156`) while keeping `n_w3_on = 1` **preserves** the high full-archive gain, ~98%+ Narrow-Now recovery, balanced faces, and high mutual backup $I$ (~50–65%).

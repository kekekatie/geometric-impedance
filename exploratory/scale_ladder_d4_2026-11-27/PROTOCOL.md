# Pre-Registered Protocol: Scale-Ladder Step `d=(3,3) → d=(4,4)` (Bulk vs. Boundary Faces)

*Branch: `experiment/scale-ladder-d4-2026-11-27` (branched off `claude/aperiodic-predict-2026-11-20`). Frozen and committed **before** any `d=(4,4)` decoder histories are scored.*

---

## 1. Why `d=(4,4)` Is Qualitatively New

At `d=(3,3)`, every on-route edge sat between two boundary-touching faces (`(1,3)+(1,3)` Middle Yards or `(1,3)+(2,2)` Hallway + Corner Ear), and $k=1$ single faults + 1 lost edge completed weight-3 $X$-logicals.

At **`d=(4,4)`**, it is geometrically impossible for an on-route edge to sit between two opposite-boundary Middle Yards (that would create a weight-3 logical). Instead, every `d=(4,4)` on-route edge necessarily pairs an **Interior Bulk Face (`bndS = 0, znbr = 4`)** against a **Boundary Face** — either a **Middle Yard (`bndS = 1, znbr = 3`)** or a **protruding Corner Ear (`bndS = 2, znbr = 2, deg-2 tip`)**. Moreover, a weight-4 $X$-logical + 1 lost edge requires **$k = 2$** ordinary faults, placing `d=(4,4)` on-route edges directly in the exact $k \le 2$ critical sector with zero decoder approximations.

---

## 2. Frozen 2×2 `d=(4,4)` Cut Matrix (All `13` Tiles, `n = 26–28`)

All four cuts come from `pilot.parent(family, large=True)` with exact $d = (4,4)$, $k = 1$, and exact `(3,3)` `Indexed` decoder (`w_dec = 3, w_frame = 3`, $p = 0.001$, `CorrectedPatchCode`, exhaustive $k \le 2$ ordinary faults, deterministic unaccelerated full-scan verification with 0 mismatches):

| Site | Family | Local scar pair | Tiles | Qubits (`n`) | Check split | Cut spec (`ci, aspect, m, corners`) | Est. time |
|---|---|---|---:|---:|---|---|---:|
| **`AB_d4_mid`** | AB | **Bulk (0,4)** vs. **Middle Yard (1,3)** | 13 | **26** | `12X / 13Z` | `ci=2, asp=1.25, m=13, (4, 8, 12, 16)` | ~20 min |
| **`AB_d4_ear`** | AB | **Bulk (0,4)** vs. **Corner Ear (2,2)** | 13 | **28** | `14X / 13Z` | `ci=4, asp=1.25, m=13, (16, 20, 26, 29)` | ~25 min |
| **`Pen_d4_mid`** | Penrose | **Bulk (0,4)** vs. **Middle Yard (1,3)** | 13 | **26** | `12X / 13Z` | `ci=3, asp=1.25, m=13, (6, 10, 14, 18)` | ~20 min |
| **`Pen_d4_ear`** | Penrose | **Bulk (0,4)** vs. **Corner Ear (2,2)** | 13 | **26** | `12X / 13Z` | `ci=4, asp=1.25, m=13, (4, 9, 14, 19)` | ~20 min |

---

## 3. Metrics & Pre-Registered Questions

At each site we record:
1. **Full-archive gain:** $G_{\mathrm{full}} = 100 \times (\text{thick} - \text{thin})$ (pp).
2. **Narrow-Now recovery:** $G_{\mathrm{intact}} / G_{\mathrm{full}}$ (%).
3. **Single-face omission costs & surviving gain (%):** omitting the **Bulk** face vs. the **Boundary** face (`MidYard` or `CornerEar`).
4. **Paired-face interaction $I$ (`pp` and `%`):** $I = (G_{\text{bulk}} + G_{\text{bnd}}) - (G_{\text{both}} + G_{\text{neither}})$, plus exact $k = 0, 1, 2$ breakdown.
5. **Endpoint X-check flips & net costs.**

### Pre-registered directional hypotheses (pencil marks before scoring)
- **H1 (Narrow Now at `d=4`):** Because $d=4$ on-route logicals require $k=2$ faults spanning across the interior bulk face (rather than $k=1$ local faults), Narrow-Now recovery will **drop below the 97–99% `d=3` ceiling** (more archive benefit leaking beyond Ring 1 into Ring 2).
- **H2 (Bulk face carries the heavier load against a Corner Ear):** In `AB_d4_ear` and `Pen_d4_ear`, omitting the **Bulk (0,4)** face will cost significantly more than omitting the **Corner Ear (2,2)** face — generalizing the `d=3` Hallway-vs.-Ear bottleneck to `d=4`.
- **H3 (Sign of $I$ at `d=4` — open directional test):** Since $k=1$ is absent on-route at `d=4`, we test whether $I$ stays **positive** (backup on weight-4 logicals) or flips **negative** (two-sided $k=2$ synergy, as seen in buried `d=3` steps `A2, A1-H, B1-H`).

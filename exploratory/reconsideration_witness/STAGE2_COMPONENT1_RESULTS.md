# Stage 2, component 1: geometry + retention accounting (results)

*Results for `stage2_retention_accounting.py`, built on the 2D pre-registration
(`3213f62`). Replay: `python3 stage2_retention_accounting.py` ->
`stage2_accounting_handback.json`. numpy-only, deterministic seed.*

This is **component 1 of 2** of the 2D experiment: the predictions that need no
decoder (the geometry, and the Shredder-resolution retention accounting). The
re-judgment accuracy half — THIN-ALONE fails to re-judge where THIN+ARCHIVE and
THICK succeed (D1/D2/D3) — needs a full 2D sliding-window MWPM erasure decoder and is
a separate build; it is **not** claimed here.

## Geometry: the spatial witness diamond (validates the figure, and D4)

| d | data | stabilizers | expected `d²−1` | star sizes (bulk / edge / corner) |
|---|---|---|---|---|
| 3 | 9 | 8 | 8 ✓ | **4 / 3 / 2** |
| 5 | 25 | 24 | 24 ✓ | **4 / 3 / 2** |
| 7 | 49 | 48 | 48 ✓ | **4 / 3 / 2** |

A bulk data qubit's star is exactly **4 checks (2 X + 2 Z)** — the onset-lip diamond
of `onset_lip_2d.svg`. The bracket shrinks to 3 at an edge and 2 at a corner, the
geometric basis of **D4**. The post-flag local-diamond query the restorer consumes is
**O(1), distance-independent**: 8 bits (bulk × 2-round onset), 6 (edge), 4 (corner).

## The Shredder-resolution accounting (D1b)

Pre-flag, before the flag names the loss site, the decoder keeps an archive of the
last `L` rounds across the whole patch. Three schemes, counted honestly (L = 4):

| d | N | p | fire rate | dense/thick `N·L` | sparse bits (mean) | sparse ÷ dense | saving (dense÷sparse) |
|---|---|---|---|---|---|---|---|
| 3 | 8 | 0.05 | 0.213 | 32 | 34.0 | 1.06 | 0.9× |
| 3 | 8 | 0.01 | 0.058 | 32 | 9.2 | 0.29 | **3.5×** |
| 3 | 8 | 0.002 | 0.010 | 32 | 1.6 | 0.05 | **19.7×** |
| 7 | 48 | 0.01 | 0.048 | 192 | 73.2 | 0.38 | **2.6×** |
| 7 | 48 | 0.001 | 0.0055 | 192 | 8.4 | 0.04 | **22.9×** |

**The sparse scar archive cost tracks the firing rate (~ p·N·L); the dense bit-plane
and the thick active window are both fixed at N·L, independent of p.** So the sparse
archive's saving over thick **grows as the physical error rate falls** — ~3× at
p = 0.01, ~20× at p = 0.002 — exactly where real surface codes operate.

**Honest crossover.** At a high error rate (p ≈ 0.05) each sparse event's coordinate
overhead (≈ `log₂N + log₂L` ≈ 5 bits) makes the sparse archive *larger* than the dense
bit-plane: syndromes are no longer sparse. The sparse scheme wins only below
firing-rate ≈ 1/coord-bits (p ≲ 0.02 here). So the Penrose "pin a scar only where
frustration fired" move is a real win in the low-error regime and a loss in the
high-error regime — the accounting says precisely where the trade flips.

## What this establishes (and what remains)

- Sol's Shredder Paradox is resolved *quantitatively*: you do not need to know the loss
  site before the cut; you keep a sparse, activity-triggered scar archive whose size is
  proportional to the errors that actually fired, and query an O(1) local diamond when
  the flag arrives. At device-relevant error rates that archive is far smaller than a
  thick window's spacetime volume.
- The diamond geometry and its boundary shrinkage (D4) are confirmed exactly.
- **Remaining (component 2):** the re-judgment witness itself — that a thin window with
  the sparse archive re-judges a delayed loss as well as a thick window, while a thin
  window *without* it fails (D1, D2, D3). That requires the full 2D sliding-window
  erasure decoder (stim/pymatching or an exact bounded decoder) and is the next build,
  with the frozen `PREREGISTRATION_2D.md` as its spec.

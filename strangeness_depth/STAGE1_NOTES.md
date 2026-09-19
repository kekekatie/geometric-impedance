# Stage 1 — descriptive findings (2D substrates AB, Penrose)

**After the seal** (`b0499e1`). This note reports only what the fixed 2D geometry
*contains*. No "grip" quantity has been selected and no T1 ratio has been
promoted — deliberately, per the sealed anti-fishing rule.

## Result 1 — discrete depth banding EXISTS and is clean (prediction (b) ✓)

On both substrates, vertices fall into sharp depth bands indexed by coordination
number (= local vertex environment). Deeper environments are more highly
coordinated. Interior-only (radius 30, interior 75%):

| coordination | AB depth | AB n | Penrose depth | Penrose n |
|---|---|---|---|---|
| 3 | 0.154 | 795 | 0.138 | 719 |
| 4 | 0.388 | 659 | 0.367 | 723 |
| 5 | 0.693 | 276 | 0.704 | 413 |
| 6 | 0.861 | 112 | 0.999 | 34 |
| 7 | 0.956 | 24 | 1.092 | 20 |
| 8 | 1.054 | 56 | 1.166 | 13 |
| 10 | — | — | 1.287 | 19 |

The sealed prediction (a) (naive per-vertex depth looks continuous) and (b)
(discrete environment bands exist) are both borne out: the per-vertex histogram
is broad, but grouped by environment the bands are sharp (std ≈ 0.05–0.19).

## Result 2 — the level count is ~6–7, NOT ~4 (T3 tension)

AB gives 6 populated bands, Penrose 7. The sealed target T3 is a finite ladder
truncating at ~3–4 levels. A coordination-shell reading of the 2D window does
**not** naturally truncate at 4 — it runs 3→8 (AB) / 3→10 (Penrose). This is
early, direct evidence toward the pre-registration's own low-confidence lean (d):
*"2D fails the count."* It is not yet a kill (the grip/level mapping is not
finalised), but it is the strongest signal so far and it points the sealed way.

## Result 3 — no naive geometric ratio cleanly hits T1 (and why I stopped)

All candidate successive-ratios are tabulated transparently in
`stage1_exploration.json` (depth, depth-complement, population/area) so none can
be silently cherry-picked:

- **depth ratio** rises across shells (2.5, 1.8, 1.2, …) — grip rises with depth,
  as expected, but gives no falling 0.158.
- **depth-complement ratio** falls but sits at ~0.55–0.82 — not 0.158.
- **population/area ratio** is noisy; the two well-populated AB middle steps
  (4→5, 5→6) land at **0.419, 0.406 ≈ √2−1**, but that is `√2−1` (0.414), **not**
  `(√2−1)² = 0.172` (the LIVE T1 power), and it is not stable across the rare
  deep shells (finite-size/boundary noise dominates coordination ≥ 7).

**No first-principles 2D quantity gives a stable, clean successive ratio at
T1 = 0.158.** The `√2−1` population signal is real structure and worth noting,
but it is the *base* substrate ratio (already the memory paper's shrink ratio),
not the squared T1 power — and reading `w`/`η*` onto populations vs depths vs a
perp-holonomy analog changes the answer entirely.

## What Stage 1 needs next (to stay honest)

Per the sealed anti-fishing rule — *"the single geometric quantity each stage
tests is named in advance"* — the legitimate T1 test cannot proceed until the
pre-registration author **names the exact grip operationalisation** and the
**S ↔ shell mapping**, from the strangeness paper's `η*`/`w` definitions. Those
definitions are not in this repo (as with the linger pipeline previously). Two
specific asks:

1. **Grip:** is `w`/`E(S)` to be read geometrically as (i) shell **depth**,
   (ii) shell **window-region area/population**, (iii) a **perp-space holonomy**
   analog (the §7 "accumulate ideal e⊥" convention), or (iv) something from the
   `η*` phase-space correction directly? Each gives a different ratio; picking
   after seeing 0.158 would be fishing.
2. **S ↔ shell:** does strangeness step by one coordination shell, or by an
   inflation generation (which could turn a per-shell `√2−1` into a per-S
   `(√2−1)²` — the LIVE power)? This must be fixed before, not after.

Committed so the choice is on record as the author's, made before the number.
The descriptive result (banding real; count ~6–7 not ~4) stands regardless.

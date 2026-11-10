# HANDBACK — what does the hidden address put in the gap?

*2026-11-10. For Katie / Fable / Astra. Pre-registered in `PROTOCOL.md` (commit `ea8009f`) with the
convention bridge established and Gates 0/1 passed before any gap was read. Frozen
engine/lift/reader `84130b9` untouched; the reader is reached only through tile lists; nothing fed
back into any constructor; the scar stays skipped.*

## For Katie, in plain words

**What we asked.** Brief 1 showed the reader couldn't *see* the wrongly-admitted tile `c` — but
Fable spotted that this was baked in (all of `c`'s corners were already in the window), so it meant
the reader is *blind* to `c`, not that the address is *silent*. Brief 2 asks the real question: for
every hidden "address" the nearby skin could have, lay down the perfect Penrose floor that address
describes and look at **which tile it puts in the gap** across the scar edge. Is it `c`?

**What came back.** **It is always `c`.** At every one of 442 sampled addresses the skin allows
(the region `F(W)`), the perfect floor puts exactly `c` in the gap — `p_c = 1`, one gap-shape only.
This is a genuine choice, not a default: the gap has four candidate tiles, and the other three *are*
the perfect floor's answer at nearby addresses just outside what the skin allows — but inside the
skin's own allowed region, the answer is uniformly `c`. The one deleted tile that the full history
used to forbid `c` (the "witness") is **never** part of the perfect floor at these addresses
(`p_w = 0`), and `c` and the witness never appear together. So the picture flips from Brief 1: the
nearby skin's hidden address does not merely fail to exclude `c` — it **positively calls for** `c`.
The reason `c` is globally wrong lives in a tile that does **not** belong to the nearby skin's own
address. See `figures/gapfill_w7_s0.png`: the little blue region (the addresses the skin allows)
sits entirely inside `c`'s cell.

**What it does not show.** The growing world does **not** consult its address — the engine's rule
is local (it admitted `c` by the local rule, and that admission agrees with what the address
predicts). This is a reader's inference from a narrow window beside a jam, where the wider skin has
no consistent address at all; it is one scar in one world with correlated replicates; a sampled
reading in floating point, not a symbolic proof; and it says nothing about other scars, horizons or
tilings. In Katie's terms: the present pattern *does* inform "similars from similars" — it recovers
`c` — but what it recovers is that `c` fits the neighbourhood; the thing that globally forbids `c`
is elsewhere, in an address-foreign tile.

## Convention bridge (established before any gap was read)

- **Offset frames identical**: reader `PERP[j] = exp(4πij/5)` = generator perp basis (< 1e-15).
- **Physical bridge exact**: `pos = origin + S·exp(i·18°)·Σ Kⱼ EV[j]`, residual `2.4e-15` over all
  window vertices (reader global lift).
- The reader's four window pentagons (layers −1…2, apothems 0.809/1.309 = small/large) **are** the
  de Bruijn cut-and-project window, so a vertex is in the ideal tiling at offset `t` iff
  `perp(K) − t` lies in its pentagon — the reader's own constraint. `penrose_address.py` (same
  `GAMMA`, same window) is the independent structural reference.
- **Gate 0**: primary π/8 window = 39 tiles, SHA `e0d8d518…` (committed), `F(W)` area `3.6622e-2`,
  Chebyshev radius `0.0729` — matches Brief 1 exactly.
- **Gate 1**: at the Chebyshev centre + 25 offsets, every vertex of every W tile is accepted
  (`26/26`) — the ideal patch contains all of W.

## Results (window × class), per case — correlated, not independent

`F(W)` is non-empty only at the narrow half-width `π/8` (wider committed windows have empty `F`, as
Brief 1 found); the reading is at that scale.

| case | radius | step | gap window | `p_c` | `p_w` | `p_both` | offsets | distinct shapes | true-tile gate |
|---|---|---|---|---|---|---|---|---|---|
| **w7-s0** (primary) | 2S | 35 | π/8 (39) | **1.000** | 0.000 | 0.000 | 442 | 1 (c) | **clean (0)** |
| w7-s1 (replicate) | 2S | 35 | π/8 (39) | 1.000 | 0.000 | 0.000 | 442 | 1 (c) | clean (0) |
| w7-s0 | 1S | 26 | π/8 (21) | 1.000 | 0.000 | 0.000 | ~ | 1 (c) | clean (0) |
| w7-s0 | 3S | 37 | π/8 (49) | 1.000 | 0.000 | 0.000 | ~ | 1 (c) | clean (0) |
| w15-s0 | 1S | 42 | π/8 (48) | 1.000 | 0.000 | 0.000 | 452 | 1 (c) | **FAILED (452 at 1/6 sites)** |
| w19-s0 | 1S | 42 | π/8 (48) | 1.000 | 0.000 | 0.000 | 452 | 1 (c) | FAILED (452 at 1/6 sites) |
| w28-s0 | 1S | 42 | π/8 (48) | 1.000 | 0.000 | 0.000 | 452 | 1 (c) | FAILED (452 at 1/6 sites) |

The headline is read off the **primary (w7-s0) with the true-tile control clean** — it is. All w7
radii and the stream replicate are gate-clean and give `p_c = 1`. The group-3 cases (w15/w19/w28)
also give `p_c = 1`, but their true-tile gate **fails at one of six live sites** (the ideal tile
disagrees with the full-history placement at that one site, at every offset): the thin 1S skin has
an address that drifts from the full history at that spot, so per protocol their gap headline is
**withheld** and reported with the disagreement. This is itself a finding — the narrow 1S skin does
not everywhere carry the full-history address — and it does not touch the clean primary result.

**Genuine selection.** Across the scar edge there are 4 distinct candidate gap-shapes, all with a
consistent lift. Two of the alternatives are accepted by the perfect floor at offsets just *outside*
`F(W)`; inside `F(W)` only `c` is ever accepted (442/442). `F(W)` sits wholly inside `c`'s
acceptance cell (figure).

## Controls (primary window + its offsets)

| control | result |
|---|---|
| **True-tile (gate)** | **Clean on w7-s0**: 0 disagreements over 3 live sites; the ideal floor matches the full-history forced tile at every offset. (Group-3: 452 disagreements at 1 of 6 sites — gate fails there.) |
| **Wrong-tile** | The locally-excluded tile is the ideal tile in **0** of 442 offsets — the address never prefers a locally-illegal tile. |
| **Ordinary scars** | No pinned scar with both menus empty falls inside the primary π/8 window besides `e` itself — **not exercised** at this window. |
| **Two sides** | Splitting W by the side of `e`: both halves hold a consistent address (F area ≈ 0.0593 each). The scar does not sit on a seam between two incompatible addresses at this window. |

## Declared outcome

**B. Address predicts (`p_c = 1`).** For this query the nearby skin's hidden address calls for `c`:
the thinned skin was following its own address, and the deleted witness is the piece that does not
belong to it (`p_w = 0`). The co-presence override did **not** trigger (`c` and the witness are
never both in an ideal patch, so the full-history rejection of `c` *is* a fact about perfect tilings
— the witness and `c` are genuinely mutually exclusive there).

**Reconciliation with Brief 1.** Brief 1 (vertex-only reader): `F(W+c) = F(W)` — the reader is blind
to `c`. Brief 2 (generative): `p_c = 1` — the address predicts `c`. No contradiction: the first says
adding `c`'s already-present corners changes nothing; the second says the perfect floor consistent
with the skin puts `c` in the gap. The shed "reason" that globally forbids `c` is the witness tile,
which is **address-foreign** to the nearby skin.

## Scope and numerics

One scar in one world with correlated replicates (w7 radii share one scar; group-3 share another).
A reader's inference from a narrow window, not a property of the growth rule — the engine admitted
`c` by its local rule, which here agrees with the address. Perfect-tiling theory applied beside a
jam where the wider skin has no consistent address (`F` empty at all but the π/8 window). Sampled
float reading: 442 accepted offsets (primary), 0 dropped near-facet at `facet_tol = 1e-6`, 0 `none`
/ 0 `multi`; grid seed `20261110`; window apothems `0.809/1.309`; Chebyshev `TOL_R = 1e-9`.
`penrose_address.py` reproduces its published structural checks (thick:thin = φ, 7 star types),
confirming the shared window.

## Files / reproduce

`PROTOCOL.md`, `protocol_windows.json` (reused from Brief 1), `address_gapfill.py`,
`address_gapfill.json` (per-window, per-offset data + controls), `make_figure.py` →
`figures/gapfill_w7_s0.png`, `HANDBACK.md`. A dated correction note is appended to Brief 1's
`HANDBACK.md`.

```bash
export EFP_SNAPSHOT=<84130b9>/exploratory/accretion_pilot/expansion_front_paper
export MPLBACKEND=Agg PYTHONUTF8=1 AMBER_BASE_CACHE=<base> AMBER_CACHE=<scratch> AMBER_FORK_CACHE=<forks.pkl>
cd address_gapfill_2026-11-10
python3 address_gapfill.py gates           # Gate 0 + Gate 1 + non-scar sanity
python3 address_gapfill.py run address_gapfill.json
python3 make_figure.py
```

No merge, no force-push; branch `claude/address-gapfill-2026-11-10` from `a47acb9`.

# Fibonacci address ↔ environment — what perpendicular-address similarity guarantees

**Static geometric analysis, exact algebra. No dynamics, no cosmology, no sweep.** Isolated;
prior studies preserved (GRAFT paused).

## Question

For physically separated sites of a 1-D Fibonacci quasicrystal, how does **internal
(perpendicular) address** proximity relate to agreement of their **local environments**?

*(Checked first: not answered anywhere in the repo — the existing `v9`–`v11` pentagrid work
is 2-D, computes no per-site internal coordinate, and its "Fibonacci" mention is a deferred,
unimplemented approximant.)*

## Construction (exact)

`τ=(1+√5)/2`, star `τ'=1−τ`; physical `π∥(m,n)=m+nτ`, internal `π⊥(m,n)=m+nτ'`; window
`W=[0,τ)` (half-open); model set `Λ={m+nτ : π⊥∈W}`; tiles `L=τ`, `S=1`. Validated: gaps
exactly `{τ,1}`, no `SS`, no `LLL`, `#L:#S≈τ`.

## Answer

The local environment `E_r` (the `2r`-letter L/S word, `r` tiles each side) is a **function
of the internal address `q` alone**: `W` partitions into **environment cells** (r=2 → **5**
cells `LLSL,SLSL,SLLS,LSLS,LSLL`; r=5 → **11**), whose boundaries are derived exactly as
preimages of the interval-exchange split points (`τ−1`, `1`). Verified (exit 0): predicted ==
chain-read for every non-truncated site; one environment per cell; distinct cells distinct.

**So (exact):** same cell ⇒ **identical** environment at **any** physical distance; a cell
boundary between two addresses ⇒ **different** environments even if the addresses are
arbitrarily close; same environment ⇒ addresses within **one cell width** (bounded, not
arbitrarily tight). The correspondence has resolution = the cell width, and finer `r` gives
finer cells.

**Three examples (r=2, exact separations):**
| # | | `|Δq|` | `|Δp|` |
|---|---|---|---|
| (a) | far physical, close internal, **same** env `SLLS` | 0.005 | 199.0 |
| (b) | close internal, **different** env (boundary `2−τ≈0.382` between) | 0.013 | 76.0 |
| (c) | **same** env `LSLL`, wide internal gap (≤ cell width `≈0.382`) | 0.369 | 78.6 |

See [`ADDRESS_ENVIRONMENT.md`](ADDRESS_ENVIRONMENT.md) for the full spec, derivation, and the
exact-vs-finite separation; [`figures/fibonacci_address_environment.png`](figures/fibonacci_address_environment.png).

## Scope

Geometry only. No interaction, transmission, entanglement, or dynamical advantage is implied
by internal-address similarity — the acceptance-window address determines the local pattern
up to the cell resolution, and nothing more.

## Reproduce

```bash
python3 fibonacci_cutproject.py
python3 make_figure.py
```

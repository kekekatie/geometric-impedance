# Results — splitting the confined-address effect: radial depth vs neighbourhood organization

*EXPLORATORY. Code: `address_split.py`, figure `address_split.png` (`plot_address_split.py`).
GPT's sharpening of the onion result (`RESULTS_PREFERRED_DEPTH.md`): after controlling for
radial window-depth, how much address effect remains, and is it angular or something finer?
Held-out over 3 offsets; target = E≈0 confined-state weight.*

## The decomposition

Predict confined weight from nested blocks: **radial** window-depth → **+ angular** (the
vertex's own 2-D window position) → **+ neighbourhood** address organization (shell-averaged
perp, its variance across scales, and the local address gradient). Held-out R²:

| family | radial window-depth | + angular | + neighbourhood | total |
|---|---|---|---|---|
| silver (N=8)    | 0.676 | +0.075 | **+0.220** | 0.970 |
| golden (N=10)   | 0.447 | −0.033 | **+0.340** | 0.754 |
| platinum (N=12) | 0.212 | −0.004 | **+0.531** | 0.743 |

Three things, all robust across the families:

1. **Radial window-depth is the largest single term — but family-dependent.** It dominates for
   silver (0.68), is middling for golden (0.45), and is *minor* for platinum (0.21). The onion
   is real, but how "oniony" a family is varies a lot.
2. **Angular position adds ≈0 everywhere** (−0.00 / −0.03 / +0.08). Knowing *where on a
   depth-ring* a vertex sits does not help — the pointwise window field is essentially
   **radially symmetric**. So the vertex's own 2-D window placement reduces, for this purpose,
   to its depth alone.
3. **Neighbourhood address organization adds a large, genuinely non-radial chunk everywhere**
   (+0.22 / +0.34 / +0.53), and it **survives fixing the exact fine vertex type** (within-type
   increments +0.46 silver, +0.31 golden). This is not the vertex's own position (angular = 0);
   it is how the address is *organized across the local patch*.

There is a clean **trade**: the family where radial depth explains least (platinum) is exactly
where neighbourhood organization explains most, and vice-versa (silver). Silver's confined
structure is "simple radial"; platinum's is "neighbourhood-organized"; golden sits between.

## Why this matters — it closes the loop with transport

The neighbourhood term here is built from the *same* multiscale-address features (shell-averaged
perp, variance, gradient) that carried the coherent-transport signal in `RESULTS_TRANSPORT.md`.
So the confined-state "address made physical" and the transport "a coherent wave reads the
address" are **the same underlying quantity**: the multiscale organization of the address across
the local patch. The onion (radial depth) is the simple, largely-geometric first-order term;
the neighbourhood organization is the genuinely non-trivial part — the part a coherent standing
mode reads and a classical walk does not.

Updated decomposition, honest form:

> confined-state role ≈ **radial window-depth** (largest single term, family-dependent)
> + **≈0 angular** + **neighbourhood address organization** (large, non-radial, survives fixing
> the exact local configuration).

## Caveats

- Exploratory; extent 13–14, 3 offsets, held-out CV; confined window |E|<0.1.
- The neighbourhood block's small-radius shell mean is a smoothed version of the vertex's own
  position; but since *angular own-position adds ≈0*, the neighbourhood contribution is
  genuinely about patch organization (spread, gradient, larger-shell means), not re-encoded own
  placement.
- Total R² is family-dependent (0.74–0.97); silver's confined weight is the most fully
  explained, platinum's the least (more residual fine structure).

## Files

`address_split.py` · `plot_address_split.py` · `address_split.png` · follows
`RESULTS_PREFERRED_DEPTH.md`, `RESULTS_CONFINED_REFINE.md`, `RESULTS_TRANSPORT.md`.

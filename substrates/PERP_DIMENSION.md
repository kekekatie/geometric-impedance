# Does address fragility scale with perpendicular-space dimension?

The first prediction the projection reading has made rather than absorbed. If the
address channel measures how much higher-dimensional structure stays readable
from inside the shadow, substrates that discarded more should be more fragile.

Z^n -> 2D gives perpendicular dimension n-2. Three substrates at matched scale
(~5,500-6,100 vertices via extents 18, 15, 12), matched 5% positive rate, bulk
crop, 3 disorder seeds, shuffle null beside every point.

```
python3 perp_dimension_test.py --seeds 3
```

## Address AUC vs phason disorder

| disorder | perp 2 (8-fold) | perp 3 (10-fold) | perp 4 (12-fold) |
|---|---|---|---|
| 0.00 | 0.9792 | 0.9963 | 0.9182 |
| 0.05 | 0.9830 | 0.8578 | 0.8134 |
| 0.10 | **0.9744** | **0.7464** | **0.7207** |
| 0.20 | 0.8939 | 0.5787 | 0.6442 |
| 0.30 | 0.7718 | 0.5572 | 0.5446 |
| 0.40 | 0.6156 | 0.4996 | 0.5690 |

Shuffle nulls run 0.456-0.532 throughout.

**The feature-count control holds.** Higher n supplies more perpendicular
coordinates and therefore more model capacity, so the sweep was repeated using
perpendicular radius alone — one feature for every n. It reproduces the same
pattern (0.9668, 0.6764, 0.6974 at disorder 0.10), so the effect is not the
classifier being handed more numbers.

## Reading, with the prediction half-confirmed

**Perpendicular dimension 2 is dramatically more robust.** At disorder 0.10 it
has lost 0.005 of its pristine value while perp 3 has lost 0.250 and perp 4
0.197. That is a large, clean separation, and it is consistent with the
AB-vs-Penrose result obtained independently on the original substrates.

**But there is no monotone scaling beyond that.** Perp 3 collapses as fast as or
faster than perp 4, and perp 4 starts lower when pristine (0.9182 against 0.9792
and 0.9963). So the prediction as stated — fragility increases with how much was
projected away — is not supported. What the data show is a cliff between
perpendicular dimension 2 and everything above it, not a gradient.

## The confound that has to be settled first

The perturbation is isotropic Gaussian jitter applied in perpendicular space,
**whose dimension is the very variable under test**. A fixed amplitude in higher
dimensions offers a point more directions in which to cross the window boundary,
and the window's surface-to-volume ratio changes with dimension too. So equal
nominal amplitude may simply not mean equal damage.

If higher perpendicular dimensions are flipping substantially more vertices at
the same nominal amplitude, the entire trend could be the perturbation being
harsher rather than the substrate being weaker. A calibration run measuring
flipped-vertex fraction against amplitude for each n is required, and until it
lands **this result is undetermined, not confirmed**.

The fix, if calibration shows a mismatch, is to plot address AUC against
*measured damage* (flipped fraction or edge Jaccard) rather than against nominal
amplitude — which equalises the x-axis across substrates and is the correct
comparison regardless.

# Is the exo/endo split an artefact of the classifier?

The headline v3 result — AB address AUC 0.986, Penrose 0.661 — comes from a
*linear* model on perpendicular-space coordinates. In cut-and-project, a vertex's
local environment is fixed by which region of the acceptance window its perp
coordinate falls in, and those regions are polygonal. A linear classifier can
read a radially organised window and cannot read an awkwardly shaped one, so the
gap could in principle mean "logistic regression suits AB's window" rather than
"Penrose has no address channel".

Two tests, both on the original substrates, interior-75%, same labels and CV.

```
python3 address_model_class.py      # does the gap survive a nonlinear model?
python3 address_completeness.py     # are the Penrose address features complete?
```

## Test 1 — model class

| model | AB | Penrose | gap |
|---|---|---|---|
| logistic (as published) | 0.9787 | 0.6588 | +0.320 |
| k-NN (k=25) | 0.9815 | 0.7047 | +0.277 |
| gradient boosting | 0.9922 | 0.7861 | +0.206 |

Penrose gains ~0.13 from a nonlinear model; AB gains almost nothing because it is
already at ceiling. **Part of the published gap is a linearity artefact** — the
Penrose address channel is real but nonlinear in perp space. The gap narrows from
0.32 to ~0.21 and does not close.

## Test 2 — feature completeness

AB lifts Z⁴ → 2 parallel + 2 perpendicular, so `perp_x, perp_y` is a complete
address. Penrose lifts Z⁵, so a complete address needs a third number. If the
published feature set were truncated, Penrose would be handicapped by
construction rather than by geometry.

It is not truncated. Recomputing perpendicular coordinates from the raw K0–K4
lift reproduces the supplied `perp_x, perp_y` exactly (max abs difference
0.0000), and `k_sum` takes only the values {2, 3, 4, 5} — four hyperplanes — so
`k_sum_mod5` encodes it faithfully.

| Penrose address feature set | AUC (gradient boosting) |
|---|---|
| published (perp_x, perp_y, perp_r, k_sum_mod5) | 0.7606 |
| continuous k_sum instead of mod 5 | 0.7584 |
| complete minimal address (perp_x, perp_y, k_sum) | 0.7472 |

| AB address feature set | AUC (gradient boosting) |
|---|---|
| complete minimal address (perp_x, perp_y) | **0.9912** |

Nothing recovers the difference. Penrose's perpendicular-space address saturates
around 0.75–0.79 under any model and any complete feature set, while AB reaches
0.99 from two coordinates.

## Conclusion

**The exo/endo split is real.** It is not an artefact of the model class and not
an artefact of incomplete address features. AB's acceptance window organises
privileged sites in a way that is almost perfectly readable from perpendicular
space; Penrose's does not, and no amount of model capacity fixes that.

**But the published Penrose figure understates its address channel by about
0.10–0.13.** The paper should report the model-class-robust numbers — roughly
0.99 versus 0.78 — rather than the linear-only 0.986 versus 0.661. The gap stays
large and unambiguous; the claim simply stops depending on a choice of
classifier, which is the kind of dependency a referee looks for.

This is now the only result in the repository that has survived every null and
robustness check applied to it.

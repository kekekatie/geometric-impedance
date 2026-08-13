# Does partition granularity predict address fragility? Largely no.

Candidate mechanism: the acceptance window partitions into regions of constant
local environment; coarse regions let a perpendicular coordinate move without
changing what it means, fine ones do not. Operationalised as **neighbour purity** —
the fraction of a vertex's k nearest perpendicular neighbours sharing its
environment class, less chance.

Fragility is address AUC lost per unit of *measured damage* (flipped-vertex
fraction), not per unit nominal amplitude.

## On four substrates it looked like a mechanism

| substrate | purity excess | fragility |
|---|---|---|
| Ammann-Beenker | +0.423 | robust |
| Z⁵ zonotope | +0.348 | fragile |
| Z⁶ zonotope | +0.268 | fragile |
| Penrose | −0.062 | most fragile |

Correct ordering under two independent class definitions.

## On twelve it does not

Family built by sweeping window scale at n = 4 and n = 5, which moves granularity
while holding lattice, dimension and window connectivity fixed.

| correlation(purity, fragility) | absolute | signal-normalised |
|---|---|---|
| all 12 substrates | −0.664 | −0.735 |
| **without Penrose (n=11)** | **−0.208** | −0.432 |
| Z⁴ family only (n=5) | −0.374 | −0.388 |
| Z⁵ family only (n=5) | **+0.209** | −0.304 |

Penrose sits 4.5 standard deviations from the rest on purity and 3.4 on
fragility. It is a single extreme leverage point, and removing it collapses the
correlation from −0.66 to −0.21. Within the Z⁵ family the absolute correlation
runs the *wrong way*.

**Purity does not predict fragility among substrates.** The apparent relation is
one outlier.

## What survives

Penrose's purity being at or below chance is a real and dramatic fact: alone
among the substrates tested, its perpendicular position carries no information
about its neighbours' local environment. But "Penrose is different" was the thing
we were trying to explain. Purity restates it in new units rather than accounting
for it.

The candidate is not annihilated — purity may be the wrong operationalisation of
granularity, and the effect may be a threshold rather than a gradient (nothing
matters until purity crosses zero). But as a graded predictor across a family it
fails, and any mechanism built on it now needs to explain why it works for one
substrate and not eleven.

## Method note

This is why the family was built. On four hand-picked substrates the ordering was
perfect and the mechanism looked established. The regression cost an hour and
turned a clean story into a null result, which is the cheaper of the two ways to
find out.

Note also a recurring shape in this project: the perpendicular-dimension result
was a cliff at dimension 2 with no gradient between 3 and 4; this is a cliff at
Penrose with no gradient among the rest. Whatever governs address fragility does
not appear to be a continuous quantity.

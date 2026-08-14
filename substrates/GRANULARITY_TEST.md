# Does partition granularity predict address fragility? UNRESOLVED — this test was invalid.

> **RETRACTED 2026-08-14.** The substrate family below was built by sweeping the
> acceptance-window scale, on the assumption that this varies granularity while
> holding the substrate type fixed. It does not. Window size in cut-and-project is
> pinned by the requirement that the projection tile: the tile-edge rule needs both
> endpoints of a lattice step accepted, so shrinking the window deletes edges
> wholesale. At window scale 0.85 mean degree falls from 3.95 to 3.28 with 8.6% of
> vertices below degree 3; at 0.70 it falls to 2.39 with 51.5% below degree 3.
> Inflated windows are also not the same object — mean degree rises to 4.46 and
> 4.86 at scales 1.15 and 1.30.
>
> Of the ten zonotope family members, **only two were quasicrystals.** The
> regression compared tilings against fragmentary point sets, so neither the
> correlation nor its collapse on removing Penrose means anything. Partition
> granularity returns to UNTESTED.
>
> A valid family needs substrates that are all genuinely tilings. Window scale is
> not an available dial; parallel-plane slope and lattice choice may be.

---

## Original text, retained for the record


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

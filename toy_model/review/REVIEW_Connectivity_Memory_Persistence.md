# Review: Connectivity, Memory, and Persistence in Aperiodic Geometry

Checked after the v3 silent-corruption null audit, to see whether the same class
of problem is present. It is not the same problem — this paper uses a dynamical
model rather than a classifier, so there is no label/feature leakage. Two
different issues turn up instead, one for each half of the paper's thesis
("positions set the floor, connections set the ceiling").

Reproduce with:

```
python3 patch_shape_floor.py     # Finding 1
python3 locality_ceiling.py      # Finding 2
```

## Finding 1 — the "floor" is the shape of the patch, not channelling

§3.4 reports that at zero memory, native and rewired Penrose are effectively
identical (WR gap 0.0005) and both beat the square lattice by ~0.12. The paper
reads this as the spatial arrangement of Penrose vertices channelling diffusion
more tightly than a square grid.

But the Penrose patch is cropped to its inner 70%, which makes it a **disc**,
while the square lattice fills **[-1,1]²**. The weighted-radius metric is mean
distance from the blob centre, so a square point set is penalised by its corners
before any dynamics run at all.

Computing WR under uniform activation — the fully diffused state, no dynamics,
no substrate, no update rule:

| blob centre | square | penrose disc | gap |
|---|---|---|---|
| (0, 0) | 0.7966 | 0.6733 | 0.1232 |
| (0.3, 0.3) | 0.8719 | 0.7605 | 0.1114 |
| (-0.4, 0.2) | 0.8804 | 0.7714 | 0.1090 |
| (0.5, -0.5) | 1.0017 | 0.9126 | 0.0891 |

The paper's zero-memory gap is ~0.12. The static shape gap is 0.089–0.123.

Note also that the reported zero-memory value of WR ≈ 0.71 for both Penrose
variants sits inside the uniform-activation range (0.67–0.77). At zero memory
the pattern appears to have fully diffused on both graphs, so WR is measuring
the point set's shape and nothing else. That is consistent with native and
rewired being indistinguishable there, which is otherwise a surprising result.

**Fix:** crop all three substrates to the same region — a disc for all, or a
square for all — and rerun. Or normalise WR against the uniform-activation
baseline for each point set, so the metric reports concentration relative to
that substrate's own fully-diffused state.

## Finding 2 — the "ceiling" is spatial locality, not aperiodicity

§3.4's falsification test — native Penrose vs rewired Penrose across the memory
sweep, giving the 20:1 memory-benefit ratio — is run on Penrose only. The
square lattice is never given the same test; per §2.2, native tile-edge
connectivity is "Penrose only", and the controls use distance-ball connectivity
throughout.

Running that missing arm on a plain 25×25 periodic square lattice with
degree-matched distance-ball connectivity, rewired by the same edge-swap method
(8000 swaps, 3 seeds), averaged over 3 blob centres and 3 noise seeds:

| configuration | WR, no memory | WR, max memory | gain |
|---|---|---|---|
| square lattice, native ball | 0.8476 | 0.7420 | 0.1056 |
| square lattice, rewired | 0.8480 | 0.8469 | 0.0011 |

The periodic substrate reproduces the entire qualitative structure of the
falsification test, including the near-identical zero-memory values (gap 0.0004,
against the paper's 0.0005 for Penrose) and the collapse of the memory benefit
under rewiring.

The effect is therefore a property of **spatially local connectivity**, not of
aperiodic order. Scrambling edges makes memory unusable on any substrate whose
edges were spatially coherent, because the diffusion term then injects activation
from arbitrarily distant vertices and memory reinforces that incoherence. Nothing
in the test isolates the tiling's matching rules or long-range aperiodic
correlations, which is what §3.3 and §3.4 attribute the result to.

**Caveat on the numbers:** the step count is not stated in the sections reviewed,
so this replication is not parameter-matched and its absolute WR values and its
ratio should not be compared numerically against the paper's 20:1. The
qualitative result — a large memory benefit on a periodic lattice, destroyed by
rewiring — is robust to those choices.

**Fix:** add native-vs-rewired arms for the square and random substrates. If
Penrose retains an advantage *over the square lattice's own native-vs-rewired
gap*, that residual is the aperiodic contribution and is the real result. If it
does not, the claim narrows to "spatially structured connections let a system use
memory", which is still true and still worth reporting — just not about
quasicrystals.

## What this does not affect

The exo/endo axis and the silent-corruption results do not depend on this paper's
dynamical model. The AB-vs-Penrose address asymmetry (0.986 vs 0.661) is measured
directly on the substrates and stands independently.

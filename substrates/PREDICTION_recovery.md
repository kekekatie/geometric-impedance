# Pre-registered design: damage and recovery under phason flips

**Recorded before the run.** Same rule as the headline prediction: nothing above the
amendment line may be edited once a result is seen.

Prompted by a suggestion relayed from GPT — that before reading immediate address loss
as "lower resilience", we should test whether the substrates differ in capacity for
*recovery* after perturbation — and independently corroborated by the experimental
literature survey, whose sharpest conceptual point is that stiffness, mobility and
healing are three different axes: a system can be stiff but kinetically frozen, or soft
but highly mobile and therefore fast to repair.

We have measured one axis. This is the design for the second.

## Why the old damage model cannot answer it

`generate_*(disorder=a)` regenerates the substrate from scratch at each amplitude. No
dynamics, no history, no memory. Turning the jitter back down recovers exactly, because
there is nothing to anneal — the "recovery curve" would be the dose-response curve read
backwards. It would look like a result and be an artefact.

## The damage model instead

**Simpleton flips.** Three rhombi meeting at a degree-3 vertex fill a hexagon admitting
exactly two tilings; exchanging them sends the interior vertex to the opposite corner.
This is *the* elementary phason rearrangement: local, reversible, tiling-preserving, and
exact in lift coordinates as v → v + s_a e_a + s_b e_b + s_c e_c.

Validated in `phason_flips.py`: on an 8-fold patch, 435 flippable sites (37.7% of
vertices); 40 flips leave vertex count, edge count, crossings (0), quadrilateral
fraction (100%), Euler characteristic (2) and rhombus vocabulary all unchanged.

Damage is then a **count of flips per vertex**, not an uncalibrated amplitude. This
answers the one criticism the experimental survey levelled at the computational result,
and it is directly comparable to measured defect densities — the ~5% local tiling-error
figure for octagonal Mn₈₀Si₁₅Al₅ being the obvious anchor.

## The leak this design must avoid

The obvious repair rule — re-test each vertex against the true window using its
neighbours' consensus perpendicular position — **is the address classifier**. Annealing
with the address channel and then measuring the address channel rebuilds the §5.4 leak
in a new costume. Every relaxation rule below uses **parallel-space and tiling-local
information only**. Perpendicular coordinates appear nowhere in any dynamics.

## Branch A — entropic, run first

No energy at all. Damage by K random simpleton flips, then let *unbiased* flip dynamics
continue for a further T steps.

This branch is run first precisely because it requires no arbitrary modelling choice.
It is the null against which any energetic recovery must be judged.

**Prediction.** Under unbiased dynamics a random tiling has no restoring force, so the
address channel will **not** recover. AUC should continue to fall, or plateau at the
random-tiling value, and not return toward its clean value. Confirming this is
informative rather than empty: it would establish that address recovery in a
quasicrystal requires energetics, not merely mobility — which is exactly the
distinction the experimental literature insists on and which a bare "golden heals
faster" reading elides.

**The valuable number regardless of recovery** is the *loss rate per flip per vertex*.
That is the cleanest damage-matched family comparison available anywhere in this
project, because damage is counted in physical units rather than inferred from a
generator-specific amplitude. Report it for all three families.

**Also measured, addressing the relayed suggestion directly**: number of local
rearrangements against address readability, to test whether greater local change
correlates with restoration or only with further loss.

## Branch B — energetic, run second and only after A

Requires an energy for which the ideal quasicrystal is the ground state, computable
from the tiling alone. This is the modelling choice that will drive the answer, so it
is fixed here rather than after seeing anything.

**Candidate energy**: vertex-star frequency, E = Σ_v −log f*(type(v)), where f* is the
distribution of local vertex configurations in the clean patch and `type` is the cyclic
sequence of edge directions around a vertex.

**Known failure mode, to be checked before the energy is used for anything.** This
energy is minimised by whatever tiling maximises the commonest vertex types, which may
be a *periodic approximant* rather than the quasicrystal. If a low-temperature run from
the clean tiling drifts away from it — measured as rising damage against the clean
patch, or a collapsing rhombus-frequency ratio — the energy is wrong and Branch B is
withdrawn until a better one is found. **A recovery result obtained from an energy that
does not fix the clean tiling is worthless**, and this check comes before any recovery
measurement, not after.

## Protocol common to both branches

- Substrates: the rank-4 congruence family, all three members, matched active-set count
  as in the headline protocol.
- Damage levels: flips per vertex spanning roughly 0.01 to 0.20, so the ~5% experimental
  anchor sits inside the range.
- Address measurement: identical to the headline — two Galois perpendicular coordinates
  plus radius, `matched_rate_labels` at fraction 0.05, gradient boosting, 3-fold CV, AUC,
  shuffle null at every point.
- Seeds: at least 3, reporting mean and standard deviation.
- Tiling validity asserted after every damage and relaxation stage: zero crossings, 100%
  quadrilateral faces, Euler 2. Any violation aborts the run rather than being reported.

## What would make this experiment uninformative

- Flip dynamics that exhaust available sites, so damage saturates below the target range.
- A relaxation that recovers the address channel while also recovering it in the shuffle
  null, which would indicate the label rather than the substrate is being repaired.
- Any dynamics that touches perpendicular coordinates.

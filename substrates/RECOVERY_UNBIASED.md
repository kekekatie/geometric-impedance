# Result: unbiased phason dynamics — no recovery, no retained history, no family effect

The energy-free phase of the recovery programme (`PREDICTION_recovery.md`, Branch A),
plus the history-recoverability test that GPT's revised sequencing put ahead of Branch
B. Both are run without any energy functional, so neither can be accused of finding
structure in a landscape built to contain it. Scored first, interpreted second.

## Protocol

- Substrates: the rank-4 singular family (`generate_rank4`, N = 8/10/12), genuine
  rhombus tilings; flip machinery `phason_flips_rank4.py` (validated: 40 flips leave all
  three crossing-free, 100% quadrilateral, Euler 2).
- Damage in **flips per vertex**, a physical unit, not a jitter amplitude.
- Branch A: extent 12, 6 seeds. History: extent 10, 6 seeds, damage 0.06 flips/vertex.
- Figure: `figures/recovery_unbiased.png`.

## Branch A — structural loss per flip is family-independent

Vertex loss (1 − vertex Jaccard against the clean tiling) vs flips/vertex, 6 seeds:

| flips/vtx | 0.02 | 0.05 | 0.10 | 0.15 | 0.20 | 0.35 | loss/flip | mobility |
|---|---|---|---|---|---|---|---|---|
| silver | .038 | .085 | .149 | .199 | .239 | .314 | 1.89 | 39.3% |
| golden | .037 | .082 | .144 | .188 | .228 | .302 | 1.84 | 32.8% |
| platinum | .037 | .084 | .142 | .184 | .218 | .292 | 1.83 | 32.6% |

Near the origin the three are identical, which is expected rather than a finding: a
simpleton flip changes ~2 vertices whatever the tiling, so the low-damage slope is a
property of the move, not the field. The curves rise monotonically with no dip — unbiased
dynamics have no restoring force, so structure is only lost, never spontaneously
recovered. The entropic null, made structural and classifier-free.

**A small effect does survive at saturation**: silver > golden > platinum in vertex loss
at 0.35 flips/vertex (.314 / .302 / .292; sds .004–.014), reproduced from the extent-10
pilot. It is small, it lives only in the heavily-damaged regime, and it is **plausibly a
state-space / constraint effect** (a more constrained tiling wanders less), not an
established field effect. Recorded, not claimed. Not worth chasing ahead of the
conceptually more important tests.

## History recoverability — mobility erases history, alike across fields

Two matched-budget histories from the clean tiling: **clustered** flips (inside a disk)
vs **dispersed** flips (whole patch). Readout is leak-free: a defect is a bulk vertex
whose local type is absent from the ideal vocabulary (a substrate property, not a stored
snapshot), and the statistic is defect spatial clustering (mean NN distance vs an
equal-size random bulk draw) — no clean-snapshot comparison, no degree/label classifier.
Separation = CE(dispersed) − CE(clustered); large positive = history present. 6 seeds:

| relax flips/vtx | silver | golden | platinum |
|---|---|---|---|
| 0.00 | 0.448 ± .082 | 0.383 ± .121 | 0.486 ± .083 |
| 0.06 | 0.044 ± .051 | 0.052 ± .145 | 0.049 ± .039 |
| 0.18 | 0.006 ± .017 | −0.027 ± .076 | −0.033 ± .049 |

Right after damage the history is plainly present (clustered damage → clustered defects).
After only **0.06 flips/vertex** of free relaxation the separation has fallen ~90% to
within noise of zero, and by 0.18 it is gone — **identically for all three families**.
Unbiased phason mobility does not carry spatial history; it diffuses it away, and no
cyclotomic field holds it longer than another.

## Combined verdict

Under unbiased (energy-free) phason dynamics the three families **neither recover
structure nor retain spatial history, and show no field-specific difference** beyond a
small saturation-regime wandering ordering that is likely state-space size. Free mobility
is a forgetful medium. If recovery or memory lives anywhere in this system, it requires
**energetics — a restoring force / pinning — not mere mobility.** That is the motivation
for Branch B and the reason it must be gated.

## Scorecard (narrowed, per GPT)

What is established is the narrow claim: the earlier **static** address observable and
**unbiased per-flip microscopic loss** are *not the same observable* and do *not*
reproduce the same family separation. The broader "static retention vs dynamic **recovery**
rankings differ" is **not** yet supported, because no recovery has been measured. H0
(no family difference under matched, energy-free perturbation) is currently favoured for
both microscopic loss and history retention.

## Caveats

- History uses **one readout** (defect spatial clustering). It bounds spatial-clustering
  memory, not every possible relational residue; a subtler feature could persist longer.
- The saturation-regime loss ordering is small and confounded with state-space size /
  mobility; not claimed as a field effect.
- Extent 10–12, 6 seeds. Solid for a null, but a positive would need finite-size scaling.

## What this gates

Branch B (energetic relaxation) is the only remaining place a genuine field-specific
recovery could live. It is gated behind:
1. this result (done — energy-free dynamics give the null, so any recovery is genuinely
   attributable to the energetics), and
2. explicit validation that the candidate energy fixes the ideal tiling as its ground
   state and has **not** simply encoded quasiperiodic order by construction
   (`phason_energy.py` implements the energy and its ground-state gate; unrun).

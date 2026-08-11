# Coupled address/transport multiplex on Ammann-Beenker

Two layers on one node set: perpendicular-space coordinates as a static address
layer, the tile-edge graph as transport. Run with `python3 multiplex_ab.py`
(5,437-vertex patch, interior-75%, single seed).

## Design note: the obvious coupling is degenerate

An AB edge is a unit step along one lattice axis, so **every edge has
|Δperp| = 1.000 exactly** — and |Δparallel| = 1.000 too. An edge-distance
coupling `exp(-|Δperp|²/2σ²)` is therefore a constant that cancels under
row-normalisation, leaving the plain random walk at every σ. The address layer
has to enter as a *potential on vertices* instead:

    P_ij ∝ A_ij · exp(-perp_r_j² / 2σ²),   row-normalised

Vertex perp radius does vary (0.51–3.01), so this is non-degenerate.

## A1 — a uniform window shift is a symmetry, not a perturbation

| shift | edge Jaccard | address AUC | shuffle null |
|---|---|---|---|
| 0.00 | 1.000 | 0.9955 | 0.518 |
| 0.05 | 0.920 | 0.9917 | 0.490 |
| 0.15 | 0.789 | 0.9936 | 0.534 |
| 0.30 | 0.638 | 0.9934 | 0.494 |
| 0.60 | 0.398 | 0.9960 | 0.483 |

The address channel does not degrade at all, even as 60% of edges change. A
uniform shift is a rigid phason *translation*, which maps AB to a locally
isomorphic AB — the channel re-registers rather than breaking. "At what phase
does readability break" has the answer: not under this perturbation, because it
is a symmetry of the construction.

## A2 — random phason disorder gives the dose-response curve

Independent perturbation of each lattice point's perpendicular coordinate before
the acceptance test, producing scattered flips rather than a coherent shift.

| amplitude | edge Jaccard | positives | address AUC | shuffle null |
|---|---|---|---|---|
| 0.00 | 1.000 | 172 | 0.9955 | 0.515 |
| 0.02 | 0.958 | 185 | 0.9881 | 0.557 |
| 0.05 | 0.913 | 199 | 0.9756 | 0.479 |
| 0.10 | 0.829 | 224 | 0.9825 | 0.512 |
| 0.20 | 0.685 | 201 | 0.9312 | 0.495 |
| 0.40 | 0.479 | 54 | **0.7478** | 0.461 |

The channel is robust to weak disorder and degrades sharply past amplitude ~0.2.
The shuffle null sits at chance throughout, so the measurement is clean.

~~Worth noting without leaning on it: at amplitude 0.40 the AB address channel
falls to 0.748, close to where unperturbed Penrose sits (0.786).~~ **Retracted.**
This was single-seed noise at ~5,400 vertices. At ~16,800 vertices with 4 seeds
AB reaches only 0.8356 ± 0.0104 at amplitude 0.40, above Penrose's best value
anywhere in its sweep. See `PHASON_DOSE_RESPONSE.md`.

## B — the address layer resists localisation

Random walk from 8 central sources, 200 steps. Coupled uses the true perp radii;
the shuffle null permutes them across vertices, preserving sparsity and the exact
weight multiset while destroying the correspondence.

| σ | coupled spread | coupled localisation | shuffled spread | shuffled localisation |
|---|---|---|---|---|
| ∞ (uncoupled) | 12.123 | 1.53e-03 | — | — |
| 3.0 | 12.135 | 1.56e-03 | 12.059 | 1.57e-03 |
| 1.5 | 11.837 | 1.94e-03 | 11.236 | 2.29e-03 |
| 1.0 | 10.575 | 3.52e-03 | 8.756 | 7.08e-03 |
| 0.7 | 7.063 | 1.57e-02 | 4.612 | 7.43e-02 |
| 0.5 | 3.118 | 1.79e-01 | 2.402 | 3.43e-01 |

**The structured potential localises far less than the matched random one.** At
σ = 0.7 the shuffled potential is nearly five times more localised than the
coupled one, from exactly the same weights. The coherent address layer keeps
transport spread out; scrambling it into disorder pins transport down.

This is the opposite of the anchoring behaviour the architecture was proposed to
demonstrate. ~~It is consistent with the general result that quasiperiodic
potentials resist localisation — the Aubry-André phenomenology.~~ **The
quasiperiodic reading is withdrawn.** Against fields carrying an identical value
multiset, a smooth radial ramp resists localisation *more* than the
perpendicular-space field does, and a long-wavelength periodic field more still.
The effect is spatial correlation length, not quasiperiodic order. See
`LOCALISATION_MECHANISM.md`.

The shuffle null is what makes the result visible. Without it the only
observation would be "localisation rises as σ falls", which is true of any
potential and means nothing.

## What needs doing before any of this is quotable

- Single seed throughout. A2 is visibly noisy (0.9756 at amplitude 0.05 against
  0.9825 at 0.10) and the positive count collapses to 54 at amplitude 0.40, so
  that AUC is the least reliable number in the table. Replicate at 10 seeds.
- Experiment B uses 8 sources and 200 steps on the unperturbed substrate only.
  Sweep phason disorder and σ jointly to get the full surface.
- A Penrose cut-and-project generator with window shifting is still needed to run
  the comparison that motivated all of this.

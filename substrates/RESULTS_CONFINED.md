# Results — address made physical: within a fixed motif, address predicts confined-state weight

*EXPLORATORY, not a sealed test. Code: `confined_address.py`; figures
`confined_address_{golden,silver,platinum}.png`. The visual companion to the coherence
ladder (`RESULTS_COHERENCE.md`): if the address-reading lives in the coherent stationary
spectral structure, then holding the local vertex type FIXED, the eigenstate weight should
still vary with global perpendicular-space placement. It does.*

## The question (GPT's within-motif design)

The E≈0 **confined states** are locked to local motifs, so a pooled "confined weight ↔
address" correlation might merely rediscover "motif ↔ address". The sharp, conditional
question: **for the same local vertex type, does confined-state weight vary with
perpendicular-space address — controlling for physical structure, including long-range?**
If yes: local physical identity does *not* fully determine spectral role; global
quasiperiodic placement does.

## Method

- Per vertex: **confined weight** = Σ_{|E|<0.1} |φ_k(v)|² (weight in the E≈0 spike/pseudogap).
- **Vertex type** = rotation/reflection-invariant angular-gap signature (the standard handful
  of vertex configurations), so classes are large.
- Within each common class, **effect size** = held-out-offset R² gain of adding ADDRESS
  features (perp coord + hull depth + shell-perp + perp-variance + gradient) over a baseline
  of PHYSICAL features **including long-range** (density/coordination/angular order out to
  r=12). Held-out over 4 window offsets; extent 12.

## Result — yes, robustly, across all three families

Within-motif address effect (R² gain of address over physical-incl-long-range), common
classes:

| family | representative common motif classes (n; address effect) |
|---|---|
| golden (N=10)   | #3 (1205; **+0.094**), #15 (600; **+0.116**), #8 (490; +0.042), #10 (1169; +0.038) |
| silver (N=8)    | #5 (978; **+0.261**), #2 (2353; **+0.193**), #7 (403; +0.069), #3 (2830; +0.047) |
| platinum (N=12) | #5 (858; **+0.215**), #3 (1998; **+0.127**), #7 (947; +0.117), #12 (620; +0.116) |

Every common, well-behaved class shows a **positive** within-motif address effect; several are
large (silver up to +0.26). (Two pathological classes with already-negative held-out physical
R² — platinum #11, golden #1 — are broken regressions, not counter-evidence; excluded from
interpretation.) So **the same local vertex configuration carries systematically different
confined-state weight depending on where it sits in perpendicular space** — controlling for
long-range physical structure.

## The picture (`confined_address_golden.png`)

Left: all vertices of a single motif class in physical space, coloured by confined weight —
bright and dark copies of the *identical* local configuration, spatially organized. Right:
confined weight vs hull/window depth for that one motif — a clear, **non-monotonic** relation
with a **resonant peak at intermediate depth** (~0.35): confined states preferentially inhabit
a specific perpendicular-space depth, within a fixed motif. (That preferred-depth resonance is
a candidate home for Karen's "compounding, depending on circumstances" intuition — a special
placement where the standing mode piles up.)

## Interpretation

This is the visual manifestation of the coherence-ladder finding. The confined eigenmodes
solve Hψ = Eψ — a globally self-consistent standing pattern — so their amplitude at a vertex
depends on the vertex's place in the *whole* quasiperiodic arrangement, not only its local
neighbourhood. Two vertices that are locally identical can play different spectral roles
because the global standing-wave consistency distinguishes them by address. Not "perpendicular
space physically pokes through" (we do not claim that) — the clean statement is:

> **Local physical identity does not fully determine spectral role; global quasiperiodic
> (perpendicular-space) placement does.**

## Caveats

- Exploratory; extent 12, 4 offsets; held-out-offset but not stratified-shuffle controlled
  (the physical-incl-long-range baseline + held-out CV is the control here).
- Heterogeneous across vertex types; a few rare/ill-conditioned classes give unstable
  regressions and are excluded.
- Confined window |E|<0.1 is the E≈0 region (the pre-registered *secondary* transport window,
  which already showed the largest address increments).

## Files

`confined_address.py` · `confined_address_{golden,silver,platinum}.png` · builds on
`transport_run.py`, `RESULTS_COHERENCE.md`, `RESULTS_TRANSPORT.md`.

# Crossover brief — GIV quasicrystal programme, for the materials-science desk

*Where this programme stands right now, written so a materials-science reader can spot
overlap with real quasicrystal physics and tell us what they've got. Full crew narrative:
`SYNTHESIS.md`. This brief is the short, portable version.*

## The setup, in MS terms

Substrates are rank-4 cut-and-project rhombus tilings at three symmetries: **8-fold
(Ammann–Beenker, "silver"), 10-fold (Penrose, "golden"), 12-fold ("platinum")** — all
validated planar tilings, matched at rank 4 and perpendicular dimension 2. The elementary
dynamical move is the **simpleton (hexagon) phason flip**. Damage is counted in **flips per
vertex**, deliberately a physical count comparable to measured tiling-error densities (our
anchor: the ~5% octagonal figure for Mn₈₀Si₁₅Al₅). The "address" of a vertex is its
perpendicular-space coordinate; we study how readable/robust that address is.

## Recent NULLS (all under energy-free / unbiased phason dynamics)

- **No dynamic self-repair.** Structural loss per flip is family-independent; damage only
  accumulates, nothing spontaneously heals.
- **History erased fast.** Clustered vs dispersed damage of equal budget becomes
  indistinguishable within ~0.06 flips/vertex, alike across families — mobility *diffuses*
  history rather than carrying it.
- **State-space "tendency" is generic.** Deeper local continuation-volume carries structure
  beyond degree, but a matched random-tiling scramble reproduces it → **not**
  quasiperiodic-specific.
- **No conserved discrete charge.** The congruence class is fully scrambled by flips
  (every increment mod 5 / mod 9) → no topological Z₂ from the class.
- Together these **cross-validate an earlier synchronization ("metronome") null**: the
  geometry governs *static structure*, not *free dynamics*.

## Recent POSITIVES (the static side)

- **A degree confound, found and controlled.** The old headline "silver preserves address
  best" was largely vertex-**degree** redundancy. Degree-controlled, it reverses:
  **golden (Penrose/decagonal) carries the richest *degree-independent* perpendicular-space
  address information**; silver's address is largely redundant with degree. (Not yet a
  confirmed full hierarchy — a second, independent metric agrees silver is weakest but not
  on golden-vs-platinum.)
- **The address is locally encoded in the vertex-star configuration** (the local vertex
  "type"): reconstructs at R²≈0.85 and **transfers across window offsets** (structural, not
  memorization).
- **Golden's window has a real inversion pair-structure** (two equal-area inverted pieces)
  that silver lacks — but it is a window symmetry, not a conserved charge.

## What we've decided to do NEXT (crew consensus)

1. **Transit impedance (the missing rung).** Every dynamics test so far moved the *tiling
   itself*; none moved a *thing across it*. Put a minimal localized excitation on the
   **fixed** substrate and measure its transit, against a **degree-preserving rewired
   control**, to isolate genuine higher-order geometric influence from degree / edge-length
   / void statistics.
2. **Endogenous objects.** Whether the tiling admits **topologically-protected defects
   (disclinations)** — objects "made of the map" — now that the congruence class is ruled
   out as a protected charge.
3. **Audit two physics papers** (baryon-decuplet widths; meson widths) with the same
   degrees-of-freedom / known-baseline scrutiny the tiling work received.

## Where YOUR materials-science results might cross over (the ask)

- **Phason kinetics / elasticity** — measured phason elastic constants, flip rates, or
  imaged phason rearrangements (e.g. decagonal Al–Cu–Co) that could calibrate our
  flips/vertex axis or the energetics we deliberately left out.
- **Random-tiling vs energetic stabilization** — evidence on whether real quasicrystals are
  entropically (random-tiling, Henley/Elser) or energetically stabilized; bears directly on
  our "recovery needs energetics, not mobility" null.
- **Defects / disclinations** — densities, mobilities, and whether disclinations act as
  persistent localized objects (for the "thing made of map" thread).
- **Transport** — electronic or excitation transport, critical/localized states,
  conductivity anomalies across 8/10/12-fold quasicrystals (for the transit-impedance
  experiment: which observable actually reveals geometric influence).
- **Self-repair / annealing** — the decagonal self-healing evidence (growth-error repair,
  grain coalescence): does it contradict our energy-free null, or is it simply the
  kinetic/energetic axis we didn't test?

## Deeper pointers

`SYNTHESIS.md` · `substrates/RECOVERY_UNBIASED.md` · `substrates/RESULTS_INTRINSIC_DRIFT.md`
· `substrates/RESULTS_STATIC_ADDRESS.md` · `LEADS.md`

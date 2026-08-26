# Results — where does the address-reading live? (the coherence ladder)

*EXPLORATORY mechanism probe, not a sealed test. Code: `wave_dephasing.py`, figure
`coherence_ladder.png` (`plot_dephasing.py`). First rung of the "WHY can coherent dynamics
read the address?" question (transport confirmatory: `RESULTS_TRANSPORT.md`). We did NOT
run the expensive noisy-dynamics sweep yet — the cheap eigenstate ladder already answers the
conceptual question.*

## The question

The confirmatory run showed a coherent wave reads golden's address and the classical random
walk does not. The tempting gloss was "memory reads memory": the wave accrues phase along
paths and interference exposes the multiscale structure. GPT rightly asked us to separate
two very different things before telling that story:

- **dynamical interference** — phase accumulated between eigenstates *over time*;
- **eigenstate structure** — the wave's stationary, geometry-shaped standing-wave patterns.

Both are "coherent". Only one might be doing the reading.

## The ladder

Three per-vertex RETURN observables in the sealed primary window |E| ∈ [0.8, 2.5], decreasing
coherence, all from the eigenstates (no noisy simulation needed for this rung):

1. **coherent return** P_coh(v) = ⟨ |Σ_{k∈win} |φ_k(v)|² e^{−iE_k t}|² ⟩_t — full dynamical
   interference (short times t = 0.3/0.6/1.2, so interference is genuinely present).
2. **diagonal ensemble** P_diag(v) = Σ_{k∈win} |φ_k(v)|⁴ — the infinite-time average:
   dynamical phases between eigenstates gone, eigenstate structure intact.
3. **classical return** — the sealed incoherent null (random-walk return). (It is *not* "no
   eigenstates" — a classical diffusion operator has spectral modes too, and they can even
   carry signed components. The real distinction, GPT's cleanup: **coherent amplitude
   dynamics** — complex amplitudes, unitary phase evolution, interference, standing modes
   bound by a global Hψ = Eψ consistency — versus **stochastic probability dynamics** —
   real, contractive relaxation of probabilities, no interference. The address sensitivity
   sits with the former.)

Address increment (M4-over-M3, held-out-offset CV, extent 12, 4 offsets):

| rung (coherence high → low) | silver | golden | platinum |
|---|---|---|---|
| 1. coherent return (interference) | +0.079 | +0.032 | +0.075 |
| 2. diagonal ensemble (phase gone) | +0.082 | +0.032 | +0.061 |
| 3. classical return (no eigenstates) | +0.004 | +0.001 | +0.001 |

Stratified shuffle kills the increment on every eigenstate rung (golden −0.017; silver/
platinum small residuals), and reads ≈0 for classical — so the eigenstate-rung signal is the
address, as before.

## The finding: plateau, then cliff

The shape is not a slope. **Rung 1 ≈ rung 2 everywhere** — removing all dynamical
interference (going to the diagonal ensemble) barely changes the address increment (golden
identical; silver identical; platinum a faint +0.014 interference bonus). Then it **falls off
a cliff** to classical (rung 3 ≈ 0).

So the mechanism is **not dynamical phase-accrual over paths.** The precise, safe statement
(GPT's cleanup): **the address sensitivity resides in the stationary spectral structure of
the coherent tight-binding Hamiltonian, and does not require dynamical inter-eigenstate phase
interference.** The coherent eigenmode |φ_k⟩ satisfies Hψ = Eψ — one amplitude pattern that
must be *globally* self-consistent across the whole graph at once — so it can be sensitive to
global quasiperiodic placement beyond any local motif. The classical walker's diffusion modes
solve no such signed, globally-constrained amplitude problem, so they carry degree /
bottleneck / local-connectivity structure but not this address-relevant organization.

## The reframe (honest correction of the poetry)

"Memory reads memory" survives, but transformed and made precise:

- The reader's requisite "memory" is **not** dynamical phase-history accrued along paths
  (that adds almost nothing here). It is the wave's **global standing-mode consistency** — one
  signed amplitude pattern that must fit the whole graph's connectivity at once (Hψ = Eψ).
  Not "spatial accrual in time" (an eigenmode does not literally accrue — GPT's caution) but
  *global self-consistency across space*. Karen's "accruement" survives as: the pattern is
  fixed by fitting the entire arrangement simultaneously, not built up step by step.
- **map-memory + shape-memory** (GPT's phrasing): the geometry embodies relations; the
  eigenmode embodies the geometry in a globally-constrained standing pattern. One static
  relational structure becomes legible through another static relational structure — which is
  eerily close to the programme's reconstructive-memory theme: *no transcript required, the
  relation survives in form.*
- This snaps neatly onto the programme's oldest theme: **quasiperiodicity governs static
  structure, not free dynamics.** Eigenstates are *static*. So even the wave reads the
  geometry through its *stationary* structure — the address is a static property, read by a
  static (standing) structure. The border wall holds even here.
- Coherence is still necessary — you need the coherent, signed-amplitude Hamiltonian to have
  these globally-constrained stationary modes — but *interfering* them dynamically is not what
  does the reading.

## Status and caveats

- Exploratory; extent 12, 4 offsets; single patch per offset; bulk-only.
- Rungs 1 and 2 are eigenstate-based and are equal within noise — the "monotone decrease"
  I first expected was the wrong shape; the true shape is plateau-then-cliff, which is the
  cleaner and more informative result.
- The expensive **stochastic Haken–Strobl sweep** (dial γ to physically destroy the
  eigenstates toward the classical limit) is still worth doing to get the *death-curve shape*
  as standing structure is dismantled (threshold vs gradual — where Karen's "compounding,
  depending on circumstances" intuition would show up). But the conceptual penny — it is
  eigenstate structure, not dynamical interference — has already dropped from this cheap
  ladder.

## Files

`wave_dephasing.py` · `plot_dephasing.py` · `coherence_ladder.png` · builds on
`transport_run.py` / `RESULTS_TRANSPORT.md`.

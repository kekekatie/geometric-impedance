# Draft pre-registration: intrinsic transition-graph asymmetry (the entropic-geometry test)

**Status — DRAFT for crew review (Karen, Gemini, GPT). Not sealed, not run.** Once the
crew agrees the design it is sealed by commit; nothing above the amendment line changes
after the first result is seen.

Precedes Branch B. Branch B *imposes* an energy whose ground state is the ideal tiling
(Case A: "we wrote go-home into the law"). This test asks whether the state space
*already* contains a directional bias before any energy is imposed (Case B: "we discover
one"). You try discover before impose, so this runs first and Branch B stays gated behind
it.

---

## 1. Why this exists

Branch A (`RECOVERY_UNBIASED.md`) gave the null: unbiased flips forget microstructure and
history, alike across 8/10/12. But it measured **microscopic identity** and it picked
**uniformly among legal moves** — possibility with no stated preference. The open question
in `geometry + ? -> P(x_{t+1} | x_t)` is the `?`, and it was never measured.

Two facts sharpen the target:

- **Possibility is not preference.** The cut-and-project geometry says which moves are
  *possible*. It does not, on its own, say which possibility is *realised*. Branch A
  supplied the trivial answer (uniform); the interesting answer is whether the
  combinatorics of the state space supply a non-trivial one.
- **Micro-forgetting is consistent with a macro-drift.** Entropic selection predicts a
  drift of a **coarse (macrostate) coordinate**, not memory of a microstate. So Branch A's
  micro-null does not touch it. This is the unmeasured half.

**This is a named, established mechanism, not a lone speculation.** The random-tiling
model of quasicrystals (Henley; Elser) holds that the quasiperiodic symmetry is selected
by **configurational entropy alone** — the zero-phason-strain macrostate maximises the
number of tilings, with no energy. GPT's "Ω(coherent) > Ω(incoherent)" is exactly that
claim. So Case B has real physics behind it and the literature is directly on-target.

Operational demand, taken seriously: define the "incompleteness/asymmetry of the present"
as a **signed quantity** and measure it. No poetry passes this document.

## 2. Coordinates (defined without rewarding "home")

Each is a coarse observable of the current state; measuring drift of one imposes no energy,
as measuring a ball's height imposes no gravity.

- **g_phi — phason strain.** The mean perpendicular-space position of the accepted
  vertices, and its spatial gradient across the patch. A clean-reference-free variant: the
  RMS spatial gradient of local perp-position, which is zero for any strain-free tiling and
  needs no comparison to the specific clean instance.
- **g_c — coherence.** Fraction of bulk vertices whose local type lies in the ideal
  vocabulary (1 − defect fraction; the vocabulary is a substrate property, `phason_energy`).
  Clean-instance-free.
- **Omega — local state-space volume.** Number of legal flips |A(x)| (mobility), and a
  short-horizon reachable-set size (count of distinct states reachable within r flips),
  reported as log Ω.

## 3. Primary estimator — the exact per-state signed drift

At a sampled state x, enumerate **all** legal flips A(x) and compute, uniformly over that
state's own moves,

    b_g(x) = (1/|A(x)|) * sum_{y in A(x)} [ g(y) − g(x) ].

This is the one-step expected change of the coordinate, exact per state (an average over
the actual move set, not a noisy trajectory estimate). Plot ⟨b_g⟩ against g(x) across many
sampled states. A **restoring drift** — the geometry tending to reduce the coordinate — is
b_g(x) < 0 where g(x) sits above its strain-free value (and the mirror for g_c: b_{g_c} > 0
where coherence is low). That signed, coordinate-resolved curve *is* the quantity the
whole idea has been asking for.

## 4. Controls — the two ways this could fool us

Two null mechanisms would fake a restoring drift; both must be defeated.

- **Bounded-coordinate regression (the main trap).** If g is bounded, extreme states
  trivially have more moves inward than outward, so b_g looks restoring for reasons that
  have nothing to do with quasiperiodic order. **Control**: compare b_g(x) at a given g to
  the same quantity in a **low-order-matched scrambled** state at the *same* g — a
  random-tiling configuration matched on density, degree, tile frequencies and defect
  count but with quasiperiodic order destroyed (the flip-saturated ensemble from Branch A
  supplies this for free). Intrinsic drift is only what the genuine substrate shows *over
  and above* the matched scramble at equal g. This is the dynamic form of the same
  discipline the degree-control and history tests used.
- **Proposal-multiplicity artefact.** "Uniform over moves" breaks detailed balance when
  |A(x)| varies, biasing the *stationary* walk toward many-move states. The per-state b_g
  above is a property of the move set and does not depend on this, but any **global/flow**
  claim does. **Control**: recompute stationary drift under a Metropolis-corrected proposal
  (accept x→y with min(1, |A(x)|/|A(y)|)) that enforces a uniform stationary measure over
  states; a flow that survives the correction is intrinsic, one that vanishes was
  bookkeeping.

Boundary: bulk-restrict all coordinates (coordination ≥ 3), open patch. Finite size: this
is a single-patch, ensemble-over-dynamics design; a positive requires finite-size scaling
across extents before it is believed.

## 5. Hypotheses

- **H0 — no intrinsic bias.** After the controls, b_g ≈ 0 in every independently-motivated
  coordinate, no Ω–coherence gradient, detailed balance holds. Bare geometry has no tipping
  tendency; the `?` is not entropy/combinatorics.
- **H1 — intrinsic entropic restoring drift, not family-specific.** A restoring b_g toward
  the strain-free / higher-coherence macrostate survives both controls, similarly across
  8/10/12. This is the random-tiling mechanism operating; interesting, but generic to
  rhombus tilings.
- **H2 — family-specific intrinsic bias.** The surviving drift or the Ω–coherence gradient
  **differs across the cyclotomic fields.** This is the outcome that would matter for GIV:
  the geometry of the specific field supplies a specific tendency.

**Explicitly not tested here:** the strong claim that static asymmetry sustains *endless*
motion. A closed fixed patch equilibrates; any real drift here is transient (the toddler
reaches the ground). Sustained falling-forward needs a continually renewed asymmetry —
plausibly a **growing** accessible state space — which lives one level above a fixed tiling
and is recorded in §8 as future work, not claimed here.

## 6. Predictions, to be scored

- **P1** phason-strain drift b_{g_phi} is restoring at the ensemble level (random-tiling
  theory expects the zero-strain macrostate to be entropically preferred). **Credence 0.70.**
- **P2** that restoring drift **survives the matched-scramble control** at equal g (i.e. it
  is not mere bounded-coordinate regression). **Credence 0.45.**
- **P3** some coordinate's intrinsic drift or Ω–coherence gradient is **family-specific**
  (H2). **Credence 0.25.**
- **P4** the proposal-corrected stationary flow is non-zero (a genuine current, not an
  artefact). **Credence 0.30.**

Overall: **H0 0.35 / H1 0.40 / H2 0.25.** Recorded to be scored, not because precise.

## 7. Protocol

- Substrates: rank-4 singular family, N = 8/10/12, matched active-set count, bulk-restricted.
- State sampling: unbiased trajectories over a spread of damage (0 → ~0.30 flips/vertex),
  plus clustered/dispersed history endpoints, to cover a range of g values.
- At each sampled state: enumerate A(x); compute exact b_g(x) for every coordinate; record
  |A(x)| and g_c.
- Matched-scramble baseline: for each sampled g, the corresponding flip-saturated
  random-tiling state; compute b_g there for subtraction.
- Detailed-balance control: a subset rerun under the Metropolis-corrected proposal.
- Seeds: ≥ 6 trajectories; report mean and CI. State the single-patch caveat.
- Family comparison across 8/10/12, and a scaling check across at least two extents if a
  signal appears.

## 8. Out of scope, recorded so it is not lost

**Expansion / growing state space.** The sustained version of "reconstruction into each new
slice of now" likely requires the accessible configuration space to keep growing, so that
there is always more continuation-volume ahead and the drift never equilibrates. This is
the conceptual home of the cosmological-time reading and of the "constant falling forward"
image. It is deliberately not part of this test, which measures only the transient,
present-state drift on a fixed patch. Flagged for a future design once the static asymmetry
is established or ruled out.

## 9. What would count as a real finding vs a real null

- **Finding**: a restoring b_g in an independently-defined coordinate that survives the
  matched-scramble control (not bounded-coordinate regression) and, for the GIV-relevant
  version, differs across the fields; ideally with a proposal-corrected non-zero stationary
  flow and a finite-size trend.
- **Null**: detailed balance, zero surviving signed drift in every coordinate, no
  Ω–coherence gradient. The bare geometry has no intrinsic tipping tendency; the restoring
  `?` must enter through energetics, boundaries, or nonequilibrium driving after all — which
  sends us to Branch B with a clear conscience, having ruled out the cheaper explanation.

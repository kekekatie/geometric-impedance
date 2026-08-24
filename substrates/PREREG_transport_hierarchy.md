# Draft pre-registration: does a physical law READ the address? (transport-hierarchy test)

**Status — DRAFT for crew review (Karen, Gemini, GPT, Fable; Claude). Not sealed. No
confirmatory run made.** Once the crew agrees, sealed by commit; corrections then go only in
a dated amendment.

Grounded in the MaterialsDeepResearch report (Experiments 2 + 3) and our own surviving
static result. It converts that result into a causal-dynamical question and reuses the
nested-increment method we already validated (`static_degree_controlled.py`).

---

## 1. Why this exists

Our static work established: **golden carries the richest *degree-independent* perpendicular-
space address information** (silver's is largely degree-redundant), and the address is
locally encoded in the vertex-star type. But the border-wall lesson — echoed independently by
the materials report — is that **geometry only *provides* structure; a physical *law* has to
*read* it.** The report is specific about which laws read what: **coherent** dynamics
(tight-binding / scalar wave) can read multiscale phase-coherent structure and is where
quasiperiodicity has demonstrated teeth; **incoherent** dynamics (random walks, resistor
networks) are dominated by degree, bottlenecks and edge weights — exactly our nulls'
territory. So the question is not "is the address there" (it is) but **does any physically
natural dynamics actually read it, beyond low-order structure?**

## 2. The law (fixed in advance; address NEVER inserted)

- **Primary engine — tight-binding quantum walk.** Hamiltonian H = the tiling's adjacency
  (uniform hopping on tile edges); a robustness variant weights hopping by edge length. This
  is a physically natural coherent law. **The perpendicular-space address appears nowhere in
  H** — only later, as an *analysis feature*. This guards the report's Experiment-4 trap:
  address-aware dynamics that differs only because address was written into the law is not
  evidence that transport reads address.
- **Null engine — incoherent random walk** (uniform-neighbour). The report predicts this is
  degree-dominated and reads no higher-order structure; it is the contrast that makes a
  coherent positive meaningful.

## 3. Observables

- **Primary: per-vertex Local Density of States (LDOS)** from H (spectral weight at each
  vertex in a fixed energy window). A coherent quantity a wave actually "sees", and per-vertex
  so it feeds the nested-increment machinery directly.
- **Aggregate (stage-two): eigenstate localization** (inverse participation ratios), spectral
  level-spacing statistics, and early-time wavepacket spreading exponent (pre-boundary).
- **Null: random-walk local return/mixing** per vertex (degree-dominated baseline).

## 4. Primary metric — the nested increment (our method)

Predict the per-vertex transport observable (LDOS) from nested feature sets, held-out-offset
CV, and read the **increments**:

- **M0** size/density (baseline)
- **M1** + degree, incident edge-length distribution
- **M2** + local motif / vertex-star **type** and local radial counts g(r)
- **M3** + local angular-spectrum / structure-factor descriptors *(coarse version buildable;
  full S(k) surrogate is stage-two)*
- **M4** + **multiscale / global perpendicular-space address** structure

**The decisive quantity is the M4 increment over M3** — does globally-organised address
structure predict coherent transport *beyond* local motif and spectral structure? Note a
subtlety we already measured: address ≈ vertex-type locally (reconstruction R²≈0.85), so M2
likely already captures the *local* address content. M4 is therefore deliberately the
*multiscale/global* address organisation, not the local motif — the true "higher-order
quasiperiodic sequence" content the report says is rarely isolated.

**Decisive control — address-shuffle (ladder rung 8):** permute the perpendicular-address
labels across vertices while keeping the graph fixed. A genuine M4 increment must **vanish**
under this shuffle; if it survives the shuffle, it was never address.

## 5. Control ladder (report Experiment 2)

Buildable now: (1) original QC; (2) periodic approximant; (3) degree-preserving rewiring;
(8) perpendicular-address label shuffle. **Stage-two (flagged, harder on an irregular point
set):** (4) pair-correlation-preserving coordinate scramble; (5) Fourier-phase surrogate
preserving radial S(k); (6) angular-spectrum-matched surrogate; (7) local-patch-frequency
surrogate. We build the clean rungs first and are explicit about which surrogates are
approximate — three honest rungs beat eight faked ones. The framing is the report's: **at
what level of structural matching does the transport signal disappear?**

## 6. Hypotheses

- **H_read** — coherent transport carries address information beyond low-order structure: the
  M4-over-M3 increment is positive held-out AND killed by the address-shuffle. A physical law
  reads the address.
- **H_loworder** — any coherent transport signal is captured by M1–M3 (degree / motif / S(k));
  M4 adds nothing. The address is structurally real but **dynamically unread** at this coupling
  — consistent with the report's weak-to-moderate verdict.
- **H_structurefactor** — the signal lives at M3: "address" reduces to the structure factor
  (the report's isotropic-gap mechanism). Real, but not *hidden-coordinate* content.
- **H_incoherent-null** — the incoherent engine shows no M4 increment regardless; the
  coherent-vs-incoherent contrast is itself a clean finding about *which law reads what*.

## 7. Predictions, to be scored (calibrated to the report's caution)

- **P1** incoherent engine M4 increment ≈ 0 (degree-dominated). **Credence 0.80.**
- **P2** coherent engine shows a positive M4-over-M3 increment that the address-shuffle kills.
  **Credence 0.35** — the report says higher-order surviving full low-order matching is the
  rare case.
- **P3** most coherent structure sits at M3 (reduces to S(k)/angular). **Credence 0.50.**
- **P4** family ordering — **not predicted.** We learned that lesson.

Overall: **H_loworder/H_structurefactor 0.55 / H_read 0.30 / H_incoherent-contrast-only 0.15.**
Scoreable, not precise. Note: even the likely outcome (address reduces to lower-order
structure) is a real, publishable clarification of what "address" operationally *is*.

## 8. Protocol

- Substrates: rank-4 singular family, N = 8/10/12, fixed patches, bulk-restricted analysis,
  fresh window offsets for held-out CV (as in the static test).
- Engines: tight-binding (primary), incoherent walk (null); edge-length-weighted TB as
  robustness.
- Metric: per-vertex LDOS regressed on M0→M4, held-out-offset CV, report each increment with
  CI; address-shuffle null at every point.
- Seeds/offsets ≥ 4; single-patch caveat stated; scaling check across ≥ 2 extents if a signal
  appears.

## 9. Known limitations (stated before the run)

- Finite patch: boundary affects localization and spreading; use bulk-restricted observables
  and eigenstates away from the edge.
- LDOS is spectrum-global, so every control-ladder variant changes the whole spectrum — the
  comparison is between *whole reconstructed systems*, which is intended.
- The hard surrogate rungs (4–7) are approximate; stage-two, and labelled as such.
- Address ≈ local motif, so the informative increment is specifically M4-over-M3
  (global/multiscale), not M2 — designed in.

## 10. Decision rule

Claim "a physical law reads the address" only if the coherent M4-over-M3 increment is
(a) positive held-out, (b) killed by the address-shuffle, and (c) not reproduced by the
incoherent engine. If it reduces to M3 → report "address = structure factor." If M4 ≈ 0 →
report "address is structurally real but dynamically unread at this coupling." No family
ordering is claimed unless it survives the same increment discipline.

## 11. Out of scope (parallel/future branches)

- The **energetic phason model** (report Experiment 1: F_ph = ½∫K wᵢⱼwₖₗ, overdamped
  kinetics, target τ(q)∝q⁻²) — only if a specific proposition warrants it, never to make
  tilings heal.
- The **lifted-Burgers defect** experiment (report Experiment 5: conserved (b∥, b⊥) closure
  charge) — the cleanest "object made of the map," a strong parallel branch.

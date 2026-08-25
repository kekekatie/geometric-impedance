# Pre-registration: does a physical law READ the address? (transport-hierarchy test)

**Status — SEALED (2026-08-25). Crew: Karen, Gemini, GPT, Fable; Claude. Incorporates
Fable's five knives and GPT's six (stratified shuffle decisive; M4 frozen as an explicit
list; multiscale/hull-depth descriptors; energy window fixed from the wave pilot;
incoherent timescale fixed from the measured mixing scale; bulk/boundary separated; claim
kept narrow). One deliberate departure from GPT recorded in §5: the PRIMARY energy window
is the critical mid-band, not E≈0 — reasoning stated there. Sealed by this commit;
corrections go only in a dated amendment. The exploratory basis is `wave_pilot.py` /
`wave_pilot.png` (spectra, localization, mixing); no confirmatory increment has been run.**

Grounded in the MaterialsDeepResearch report (Experiments 2 + 3), our surviving static
result, and the wave pilot. It converts the static result into a causal-dynamical question
and reuses the nested-increment + held-out-offset method we validated
(`static_degree_controlled.py`, `reconstruct_v2.py`).

---

## 1. Why this exists

Static work established: **golden carries the richest *degree-independent* perpendicular-
space address information**, and the address is locally encoded in the vertex-star type
(reconstructs at R²≈0.85). The border-wall lesson — substrate self-rearrangement is mostly
generic nulls, but a coherent reader on a *fixed* substrate visibly responds to its
organization (the wave pilot shows confined states, a pseudogap, and critical/multifractal
states) — makes the sharp question: **does a physically natural coherent dynamics read the
address *specifically*, beyond degree, local motif, and local structure factor?** Not "is
the address there" (it is), and NOT "does quasiperiodicity help transport" or "does perp
space physically act" — those larger claims wait.

## 2. The law (fixed in advance; address NEVER inserted)

- **Primary engine — tight-binding quantum walk.** H = the tiling's adjacency (uniform
  hopping on tile edges); robustness variant weights hopping by edge length. **The
  perpendicular-space address appears NOWHERE in H** — only later, as an *analysis feature*.
  This guards the report's Experiment-4 trap.
- **Null engine — incoherent random walk** (uniform-neighbour). The report predicts this is
  degree-dominated; it is the contrast that makes a coherent positive meaningful.

## 3. Observables

- **Primary: per-vertex Local Density of States (LDOS)** = Σ_{states in window} |ψ(v)|²,
  in a fixed energy window (§5). A coherent quantity a wave actually "sees", per-vertex so
  it feeds the nested-increment machinery.
- **Null: per-vertex random-walk return probability** P_return(v, t) at short times
  t ∈ {5, 10, 20} steps (§5 fixes this below the mixing scale). Degree-dominated baseline.
- **Bulk-only** (see §8): all regressions use vertices with r < 0.8·r_max; boundary
  vertices are reported separately, never mixed into the primary.

## 4. Primary metric — the nested increment (our validated method)

Predict the per-vertex observable from nested feature sets, held-out-offset CV, read the
**increments** (R², with CI over offsets/seeds):

- **M0** — intercept + local vertex density (count within a small fixed radius).
- **M1** — + degree + incident-edge-length summaries (mean, variance).
- **M2** — + **local motif**: vertex-star **type** (local configuration class) + radial
  neighbour counts g(r) at small radii (local coordination shells). Captures local structure
  incl. the *local* address (address ≈ motif locally, R²≈0.85).
- **M3** — + **coarse local structure-factor / angular descriptors**: local bond-
  orientational order parameters ψ_n = |Σ_bonds e^{i n θ}| for n ∈ {N, N/2, 2N}, and g(r)
  at medium radii. (Local S(k) surrogate.)
- **M4** — + the **frozen multiscale-address list** (§4a).

**Decisive quantity: the M4-over-M3 increment.** Does the multiscale organization of the
address predict coherent transport *beyond* local motif and local structure factor?

### 4a. M4 — FROZEN feature list (fixed before any confirmatory run)

Each is a per-vertex function of the perpendicular-space **address field** organized over
*space* — the part local motif cannot see. Exactly these, no additions post-seal:

1. **Window/hull depth** — signed distance of the vertex's perp coordinate to the
   acceptance-window boundary (min over window facets).
2. **Shell-averaged perp coordinate** — mean of neighbours' 2-D perp-address over graph-
   distance shells at radii r ∈ {2, 4, 8} edges (two components each).
3. **Address variance across scales** — variance of neighbours' perp-address within radii
   r ∈ {2, 4, 8} edges (spread of the local address field at each scale).
4. **Perp-address gradient magnitude** — ‖∇address‖ estimated by least-squares plane fit of
   neighbours' perp-address vs physical position within radius 3.

(For families with a kernel, the address is the 2-D Galois perp coordinate, as everywhere
in the programme; the kernel/congruence label is NOT used — it is physically null, per the
Gate-0 finding.)

### 4b. Decisive control — the STRATIFIED address shuffle (GPT knife A; replaces the plain shuffle)

Permute the perp-address labels **among vertices within the same M3 bin** (same local motif
type + degree decile + orientational class), then **recompute M4 from the shuffled field**.
This destroys the *spatial/global* organization of the address while preserving all local
structure. A genuine M4 increment must **vanish** under this stratified shuffle; if it
survives, it was leaking M3, not reading global address. (The plain global shuffle is
reported too, but the stratified shuffle is the kill condition — it is the transport analogue
of the degree-stratified null that decided the static test.)

## 5. Energy window (primary) and incoherent timescale — fixed from the pilot

**Primary window: the critical mid-band, |E| ∈ [0.8, 2.5].** Reasoning (departure from GPT,
who suggested E≈0): the E≈0 states are *confined* — locked to specific local motifs — so
LDOS there is largely predicted by M2/M3 by construction, making E≈0 the window LEAST able
to reveal an M4-over-M3 increment, even though it shows the biggest *family* contrast. The
mid-band states are critical/multifractal (spread across scales), so multiscale address
organization has its best independent shot there. Bandwidth is ≈[−4.2, 4.2] (pilot); the
mid-band excludes both the E≈0 confined spike and the extreme band edges.

**Secondary window: near-zero, |E| ≤ 0.2** (the confined/pseudogap region). Pre-committed as
a contrast: largest family difference, but expected motif-dominated. Reported, not the
primary basis for the claim.

**Incoherent timescale: t ∈ {5, 10, 20} steps**, all far below the measured random-walk
mixing time (~800–1150 steps across families; pilot). The mixing scale itself is reported.

## 6. Hypotheses

- **H_read** — coherent transport carries address beyond low-order structure: the M4-over-M3
  increment is positive held-out AND killed by the stratified shuffle. A physical law reads
  the address.
- **H_loworder** — any coherent signal is captured by M1–M3; M4 adds nothing. Address is
  structurally real but dynamically unread at this coupling.
- **H_structurefactor** — the signal lives at M3 (address reduces to the structure factor).
- **H_incoherent-null** — the incoherent engine shows no M4 increment regardless; the
  coherent-vs-incoherent contrast is itself a clean finding about which law reads what.

## 7. Predictions, to be scored (calibrated to the report's caution)

- **P1** incoherent engine M4 increment ≈ 0 (degree-dominated). **Credence 0.80.**
- **P2** coherent engine shows a positive M4-over-M3 increment (primary window) that the
  stratified shuffle kills. **Credence 0.35** — higher-order surviving full low-order
  matching is the rare case.
- **P3** most coherent structure sits at M3 (reduces to S(k)/angular). **Credence 0.50.**
- **P4** family ordering — **not predicted.** (Lesson learned.)

Overall: **H_loworder/H_structurefactor 0.55 / H_read 0.30 / H_incoherent-contrast-only
0.15.** Even the likely outcome (address reduces to lower-order structure) is a real
clarification of what "address" operationally is.

## 8. Protocol

- Substrates: rank-4 singular family, N = 8/10/12, fixed patches (extent as in the static
  test), **bulk-restricted analysis (r < 0.8 r_max)**; boundary vertices reported separately.
- Engines: tight-binding (primary), incoherent walk (null); edge-length-weighted TB as a
  robustness variant.
- Metric: per-vertex observable regressed on M0→M4, **held-out-offset CV** (train on a set
  of window offsets, test on fresh offsets, as in the static test); report each increment
  with CI; stratified-shuffle null at M4 for every point; plain-shuffle reported alongside.
- Offsets/seeds ≥ 4; single-patch caveat stated; scaling check across ≥ 2 extents if a
  signal appears.
- Regressor: gradient-boosted trees or ridge on standardized features (fixed in the harness
  before the run); the SAME regressor for every rung and both engines.

## 9. Known limitations (stated before the run)

- Finite patch: boundary affects localization/spreading → bulk-restricted observables and
  bulk eigenstates only in the primary; the pilot already flagged a corner-localized E≈0
  state as an edge artefact.
- LDOS is spectrum-global, so every control-ladder variant changes the whole spectrum — the
  comparison is between whole reconstructed systems, which is intended.
- Address ≈ local motif, so the informative increment is specifically M4-over-M3
  (multiscale), not M2 — designed in, and the stratified shuffle enforces it.
- Hard surrogate rungs (pair-correlation / Fourier-phase / angular-matched coordinate
  scrambles) remain stage-two and approximate; the clean rungs (periodic approximant,
  degree-preserving rewiring, stratified address shuffle) are built first.

## 10. Decision rule

Claim "a physical law reads the address" only if, in the **primary window**, the coherent
M4-over-M3 increment is (a) positive held-out, (b) killed by the **stratified** shuffle, and
(c) not reproduced by the incoherent engine. If it reduces to M3 → "address = structure
factor." If M4 ≈ 0 → "address is structurally real but dynamically unread at this coupling."
No family ordering is claimed unless it survives the same increment discipline. The secondary
(E≈0) window is reported for contrast and never substitutes for the primary.

## 11. Out of scope (parallel/future branches)

- The **energetic phason model** (report Exp. 1) — only if a specific proposition warrants it.
- The **lifted-Burgers defect** (report Exp. 5) — Gate 0 gave its lesson (no cheap endogenous
  Burgers object under the clean constructions tried; the multigrid bridge is a real asset).
  Studying an *imposed* defect's motion would be a separate "engineering a traveller" project.

# Stage D — implementation pre-registration (SEALED before any K* is measured)

**Purpose.** Stage D is the one stage with genuine empirical content. This file
pins every free implementation choice *before* running, so no number can steer
the design (anti-fishing). It sits under the sealed `SEALED_PREREGISTRATION.md`
(Part III / §B) and only fills in the operational blanks that document left open.

**Sealed prediction (from the master prereg, unchanged):** K*(k) is **flat**
across approximant orders — locking governed by coordination/degree, not the
Diophantine class. Confidence moderate-to-high. Expected outcome: NULL.

**Kill / discovery (D-positive, unchanged):** K*(k) → K*(∞) at the substrate's
registered shrink ratio, ±15%: AB in the **silver band [0.352, 0.476]**, Penrose
in the **golden band [0.525, 0.711]**. A shared ratio across substrates, a ratio
in the wrong band, or convergence at any unregistered rate is **not** a hit.

---

## 1. The dynamical system (pinned)

Kuramoto oscillators on the substrate's own graph:

    dθ_i/dt = ω_i + K · Σ_{j ∈ neighbours(i)} sin(θ_j − θ_i)

- One oscillator per vertex; springs = native tiling edges (unweighted).
- Global order parameter r(t) = | (1/N) Σ_j exp(i θ_j) |  ∈ [0,1].
- Integration: RK4, dt = 0.05, transient T_trans = 200 time units discarded,
  then r time-averaged over T_avg = 200 units. Random initial phases, fixed seed.
- Coupling is **unnormalised** (raw edge sum) — K* is meant to be dominated by the
  graph's spectral gap, which is the physical content; degree normalisation would
  partly launder that away. (Secondary degree-normalised run may be reported, but
  the primary is unnormalised.)

## 2. Natural frequencies ω_i (pinned — the "volume" decision)

- **Source:** the vertex depth (distance of its perp coord to the acceptance-window
  boundary) — the substrate's own voice, already computed per patch.
- **PRIMARY — standardised:** ω_i = (depth_i − mean(depth)) / std(depth) per patch.
  This holds the *spread* of natural frequencies identical across every rung and
  both substrates, so the ONLY thing varying up the ladder is the graph structure
  (wiring + the spatial arrangement of fast/slow vertices, both preserved). This
  isolates aperiodicity / Diophantine class, exactly as the master prereg's
  "everything else held" mandate requires.
- **SECONDARY — raw:** ω_i = depth_i (recentred to zero mean only). Lets each
  tiling keep its own natural frequency spread. Reported alongside as a robustness
  lens: agreement strengthens; disagreement means the depth *distribution* carries
  signal and is itself reportable.
- Both use the identical spatial depth field; only the global rescaling differs.

## 3. Substrate graphs (pinned)

- **Topology held fixed throughout: TORUS** (single phason-wall seam, pristine
  interior), for every rung AND the convergence analysis — never mixed with open
  patches (master prereg §B5.2: boundary conditions change the spectral gap).
- **AB:** wrapped by the naive convergent cell (single window, any period valid).
- **Penrose:** wrapped by the class-preserving (×5) cell — the true period (a
  naive wrap glues wrong-class vertices at the seam). Established in gate #1.
- **Ladder:** orders k = 1, 2, 3, 4 (convergents per phase0_registration).
- **The "ideal":** NOT a separately built object (an ideal QC has no finite torus,
  and mixing topologies is forbidden). Instead the test is the **convergence of
  the K*(k) sequence itself**: fit K*(k) = K*(∞) + A·ρ^k and read the geometric
  ratio ρ. Flat sequence ⇒ null; ρ = √2−1 (AB) / 1/φ (Penrose) within the bands ⇒
  D-positive.

## 4. K* detection (pinned — the "when did it sync" rule)

- Sweep K over a grid; at each K, time-average r to steady state (§1).
- **K* = the coupling at which the steady-state r first crosses r_c = 0.5**,
  by linear interpolation between grid points. r_c = 0.5 sits well above the
  finite-size incoherent floor (~1/√N) for all sizes used (§5), and below the
  saturated-sync plateau. Fixed now; never adjusted after seeing curves.
- K grid: 0.02 … 2.0 in steps of 0.02 (refined by bisection near the crossing).

## 5. Finite-size canary F (pinned — mandatory)

- Each rung run at **≥ 3 torus sizes** (distinct cell-tilings of the same
  approximant, i.e. n×n super-cells: n = 1, 2, 3 where cell size permits).
- K*(N) must be **N-independent** (converged to a plateau) before any K* is used.
  An N-dependent K* ∝ 1/N is a finite-size artefact and the reported K* is the
  large-N plateau (or extrapolation). No plateau ⇒ that rung's K* is not reported.

## 6. Controls (pinned, reporting order)

1. **Primary:** the approximant torus ladder vs its own convergence (§3).
2. **Secondary:** degree-preserving rewire of each graph — an upper bound on how
   much *non-degree* structure can move K*. A native-vs-rewire gap is NOT evidence
   for D-positive (master prereg §B4).
3. Both the standardised (§2 primary) and raw (§2 secondary) frequency runs.

## 7. Outcome definitions (pre-committed)

- **NULL (expected):** K*(k) flat within canary-F error, both substrates; no
  substrate-specific geometric convergence. Report the flat curves. Honest, worth
  publishing as "the dynamical onset does not feel the Diophantine class."
- **D-POSITIVE (the prize):** K*(k) converges geometrically with per-substrate
  ratio in the correct disjoint band (silver / golden), reproduced across sizes
  (canary F) and not manufactured by the rewire control. Only then is anything
  claimed.
- **Report everything:** full K*(k) curves, both frequency conventions, both
  controls, all sizes, pass or fail — including partial/ambiguous outcomes.

## 8. Integrity locks

- Standardised-primary is fixed here, before any run. Raw is a declared secondary,
  not a fallback to fish with.
- r_c = 0.5, dt = 0.05, T_trans/T_avg = 200/200, unnormalised coupling: all frozen
  above. Any later change is logged in a changelog with reason, never silently.
- Canary F is mandatory before any K* is quoted.

*Sealed at implementation time; the master SEALED_PREREGISTRATION.md governs.*

# Draft pre-registration v2: intrinsic transition-graph asymmetry (the entropic-geometry test)

**Status — DRAFT for crew review (Karen, Gemini, GPT). Not sealed, not run.** v2
incorporates GPT's review of v1 (see the change-log at the foot). Once the crew agrees, it
is sealed by commit; nothing above the amendment line changes after the first result.

Precedes Branch B. Branch B *imposes* an energy whose ground state is the ideal tiling
(Case A: "we wrote go-home into the law"). This test asks whether the state space *already*
contains a directional bias before any energy is imposed (Case B: "we discover one"). You
try discover before impose.

---

## 1. The evidential ladder (the spine of the design)

Each rung must be passed before the next is claimed:

1. **Signed quantity exists** — some coordinate has a non-zero one-step expected drift.
2. **Beats the bounded/degree null** — the drift is not mere regression of a bounded
   coordinate nor an ordinary random-walk preference for high-degree states.
3. **Deeper continuation volume** — after conditioning on immediate mobility, alternative
   legal moves still lead to systematically unequal *future* state-space volume.
4. **QC-specific** — the effect exceeds a low-order-matched random-tiling scramble; it is a
   property of quasiperiodic order, not generic rhombus-tiling combinatorics.
5. **Field-specific** — the surviving effect differs across 8/10/12.

Rung 3 is the experiment we most want to preserve, and it is **target-free**: it never
refers to the ideal tiling at all.

## 2. Why this exists

Branch A forgot microstructure and history, alike across fields — but it measured
microscopic identity and picked uniformly among moves. Possibility with no stated
preference. The `?` in `geometry + ? -> P(x_{t+1}|x_t)` was never measured, and entropic
selection predicts a **coarse (macrostate)** drift, not microstate memory, so the micro-null
does not touch it.

**Literature, stated narrowly (per GPT).** Configurational entropy is known to produce
phason-elastic restoring tendencies in *specific* random-tiling ensembles (Henley; Elser).
It is **not** a universal theorem that every 8/10/12 rhombus ensemble has its entropy
maximum at the ideal zero-strain cut. Whether *these* state spaces do is precisely what
this test decides.

## 3. Coordinates and observables (with their standing)

- **d(x) — transition-graph degree / mobility.** The number of legal flips |A(x)|. A plain
  scalar, not an entropy. (v1 wrongly called this Ω.)
- **Ω_r(x), S_r = log Ω_r — continuation volume.** The number/measure of *distinct* states
  reachable within flip horizon r (bounded BFS for small r = 2,3, or a sampled distinct-state
  count). This is the target-free quantity of rung 3.
- **g_phi — phason strain (PRIMARY drift coordinate, but floor-limited).** The coarse phason
  field w(r) = ⟨h(a)⟩ locally averaged, h(a) = a·perp4; strain = the offset-subtracted
  spatial variation of w. A **uniform** perpendicular offset is *not* strain (demonstrated:
  offset-invariant). **`phason_strain.py` also shows the naive estimator has a large
  finite-size floor** (clean ~0.10, flipped ~0.14 at extent 12, cell 8), shrinking with cell
  size — so g_phi may be used only with its clean finite-size floor characterized across
  extents and cell sizes and subtracted, on patches large enough to separate signal from
  floor. Raw per-vertex perp gradients are **not** used.
- **g_c — coherence (SECONDARY, target-informed).** Fraction of bulk vertices whose local
  type is in the ideal vocabulary. Demoted from v1: vocabulary membership already encodes
  quasiperiodic admissibility, so this is not target-free. Its ideal vocabulary must be
  shown stable under extent and boundary exclusion before use.

## 4. Primary experiment (rung 3, target-free)

At sampled states x, **conditioning on immediate mobility d(x)**, ask whether the legal
moves y ∈ A(x) lead to systematically unequal continuation volumes Ω_r(y):

    delta_S(x) = (1/|A(x)|) * sum_{y in A(x)} [ S_r(y) - S_r(x) ]

and whether Ω_r(y) varies across the moves y beyond what d alone predicts. This is the
clean operational form of "state-space geometry supplies a tendency": at matched present
coordinates and matched immediate mobility, do alternative futures have unequal volume? It
refers to no ideal, no energy, no target.

## 5. Secondary experiment — the signed drift

The one-step expected drift of a coordinate g, exact per state (average over that state's own
moves):

    b_g(x) = (1/|A(x)|) * sum_{y in A(x)} [ g(y) - g(x) ],

plotted against g(x). Restoring drift = b_g < 0 above the strain-free value (mirror for g_c).
Run for g_phi (floor-characterized) and g_c (secondary).

## 6. Controls — the four ways this could fool us

- **Bounded-coordinate regression** (main trap for §5). Extreme states trivially drift
  inward. Defeated by the matched-scramble comparison at equal g (below) and by the
  conditional analysis (§7).
- **Degree bias** (main trap for §4). A random walk prefers high-degree states for trivial
  reasons; that is *not* the claim. The claim is unequal continuation volume **after
  conditioning on d(x)**. Degree conditioning is built into rung 3.
- **Matched-scramble specification (fixed before any result, applied blind to b_g).** The
  control state is a flip-saturated random tiling matched to the genuine state on a
  pre-declared vector: vertex count, degree distribution, tile/rhombus frequencies, defect
  count, and the target coordinate g — each within a stated tolerance (±2% on distributional
  moments; exact on counts where possible). Selection: draw flip-saturated states, accept the
  nearest match under a fixed weighted distance on those variables; if no state matches
  within tolerance for a given g bin, that bin is reported as "no admissible control" and
  excluded, never stretched. **Scramble validity is demonstrated, not assumed**: the accepted
  controls must retain the low-order vector (by construction/tolerance) *and* be shown to have
  destroyed higher-order quasiperiodic order (collapsed perp-space structure / decorrelated
  order metric) — else the "scramble" is not one.
- **Detailed-balance audit (recast from v1's P4).** On a symmetric reversible flip graph
  under a Metropolis-corrected proposal (accept x→y with min(1, d(x)/d(y))), detailed balance
  and zero stationary cycle affinity are *expected*. A non-zero corrected stationary current
  is therefore treated as a **bug signal** — trigger an implementation / state-definition /
  boundary audit before any physical reading — not as a discovery.

## 7. Conditional analysis (not subtraction alone)

Beyond subtracting the matched-scramble baseline, fit whether **order / family label
predicts b_g (or delta_S) after conditioning on** g, d(x), defect count, and tile
statistics. A surviving partial effect of the field label, with the low-order variables held,
is the rigorous form of "the geometry of *this* field supplies the tendency." Report effect
sizes with CIs, not p-values alone.

## 8. Hypotheses (H1 split per GPT)

- **H0** — no intrinsic bias survives the controls: b_g ≈ 0, no delta_S gradient after
  degree conditioning, detailed balance holds.
- **H1a** — a drift exists but is **reproduced by the matched random-tiling control**:
  generic constraint/graph combinatorics, not quasiperiodic.
- **H1b** — a drift **beyond** the low-order controls, i.e. genuinely quasiperiodic-ensemble
  entropic, but **common across fields**.
- **H2** — a **robust field-specific excess** drift/volume asymmetry across 8/10/12.

**Tempering H2 (per GPT):** a field-specific result motivates GIV-level investigation, but
lower-level causes are ruled out first — move topology, acceptance-window geometry,
recurrence, state-space connectivity, and finite-size arithmetic. GIV interpretation is the
*last* resort, not the first.

## 9. Predictions, to be scored

- **P1** g_phi drift is restoring at the ensemble level (random-tiling expectation).
  **Credence 0.65.**
- **P2** it survives the matched-scramble control at equal g (not bounded regression).
  **Credence 0.40.**
- **P3** delta_S shows unequal continuation volume **after conditioning on d(x)** (rung 3).
  **Credence 0.40.**
- **P4 (control, not discovery)** the Metropolis-corrected stationary current is **zero**
  within noise; non-zero triggers an audit. **Expected outcome: zero.**
- **P5** any surviving effect is **field-specific** (H2). **Credence 0.20.**

Overall: **H0 0.35 / H1a 0.20 / H1b 0.25 / H2 0.20.** Scoreable, not precise.

## 10. Protocol

- Substrates: rank-4 singular family, 8/10/12, matched active-set count, bulk-restricted.
- State sampling: unbiased trajectories over a spread of damage, plus clustered/dispersed
  endpoints, to cover a range of g and d.
- Per sampled state: enumerate A(x); compute d(x), b_g(x) for each coordinate, and Ω_r/S_r
  for small r (BFS r=2, sampled r=3).
- Matched-scramble baseline (§6) at each g bin; conditional regression (§7).
- Detailed-balance audit (§6) on a subset.
- Seeds ≥ 6; report mean and CI; single-patch caveat stated; scaling check across ≥ 2
  extents (also needed to characterize the g_phi floor).

## 11. Out of scope, recorded so it is not lost

**Growing state space (expansion).** The sustained version of "reconstruction into each new
slice of now" plausibly needs the accessible configuration space to keep growing, so drift
never equilibrates — the home of the cosmological-time reading. Strictly downstream; not part
of this fixed-patch test.

---

## Change-log: v1 -> v2 (GPT review)

1. g_c demoted to secondary/target-informed; vocabulary-stability check required.
2. g_phi tightened: explicit coarse field w(r); offset≠strain; finite-size floor
   demonstrated (`phason_strain.py`) and required to be characterized/subtracted; raw
   per-vertex gradients excluded.
3. |A(x)| renamed d(x) (degree/mobility); Ω_r/S_r reserved for reachable continuation volume.
4. Degree bias made an explicit null; the interesting claim is unequal volume *after*
   conditioning on d(x).
5. Matched-scramble fully specified (variables, tolerances, algorithm, no-match handling,
   blind to b_g) and its validity to be demonstrated, not assumed.
6. Conditional/matched-state analysis added alongside subtraction.
7. P4 recast from expected discovery to a detailed-balance **audit control**.
8. Random-tiling literature claim narrowed (specific ensembles, not a universal theorem).
9. H1 split into H1a / H1b / H2.
10. H2 wording tempered; lower-level causes ruled out before GIV interpretation.
Plus: explicit evidential ladder (§1); the target-free continuation-volume experiment
elevated to primary (§4).

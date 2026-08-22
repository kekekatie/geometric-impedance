# Draft pre-registration v3: intrinsic transition-graph asymmetry (the entropic-geometry test)

**Status — DRAFT, believed sealable, awaiting the crew's go (Karen, Gemini, GPT).** v3
incorporates GPT's second review; change-log at the foot. Once sealed by commit, nothing
above the amendment line changes after the first result.

Precedes Branch B. Branch B *imposes* an energy whose ground state is the ideal tiling
(Case A: "we wrote go-home into the law"). This asks whether the state space *already*
contains a directional bias before any energy is imposed (Case B: "we discover one").

---

## 1. The evidential ladder (the spine)

Each rung must pass before the next is claimed:

1. **A signed quantity / branch asymmetry exists** — some coordinate has non-zero one-step
   expected drift, or continuation volume varies across a state's immediate moves.
2. **Beats the bounded/degree null** — not mere regression of a bounded coordinate, nor the
   ordinary random-walk preference for high-degree states.
3. **Deeper continuation volume, conditioned on mobility** — after conditioning on d(x),
   alternative legal moves still lead to systematically unequal *future* state-space volume.
4. **QC-specific** — exceeds a low-order-matched random-tiling scramble, and survives a
   label-shuffle: the effect is tied to quasiperiodic order, not generic graph topology.
5. **Field-specific** — the surviving effect differs across 8/10/12.
6. **Exploited, not merely available** — the dynamics actually *flows* toward high-volume
   branches beyond the degree-explained baseline. Rungs 1-5 can all hold while the walk still
   samples uniformly; this rung is the "tip" actually realised.

Rungs 3-4 are target-free — they never refer to the ideal tiling.

## 2. Why this exists

Branch A forgot microstructure and history, alike across fields — but it measured
microscopic identity and picked uniformly among moves. The `?` in
`geometry + ? -> P(x_{t+1}|x_t)` was never measured; entropic selection predicts a coarse
macrostate drift, not microstate memory, so the micro-null does not touch it.

**Literature, narrowly (per GPT).** Configurational entropy produces phason-elastic restoring
tendencies in *specific* random-tiling ensembles (Henley; Elser); it is **not** a universal
theorem that every 8/10/12 rhombus ensemble has its entropy maximum at the ideal zero-strain
cut. Whether *these* do is what this decides.

## 3. Observables and their standing

- **d(x) — degree / mobility.** Number of legal flips |A(x)|. A scalar, not an entropy.
- **Ω_r(x), S_r = log Ω_r — continuation volume.** Distinct states reachable within flip
  horizon r: exact bounded BFS for r = 2, sampled for r = 3. Horizon-local by necessity
  (see §8 caveat).
- **Branch distribution and asymmetry (the "tip" quantity).** For state x, the set
  {S_r(y) : y ∈ A(x)} over its immediate moves; its dispersion
  `V_r(x) = Var_{y}[S_r(y)]` and contrast `C_r(x) = max_y S_r(y) − min_y S_r(y)`. A genuine
  tip needs unequal downstream opportunity *across the available moves*, not merely a large
  neighbourhood. Also `ΔS_r(x) = mean_y S_r(y) − S_r(x)` (does the average move grow volume).
- **g_phi — internal-space strain (secondary drift coordinate; floor-limited).** Careful
  wording: the perpendicular coordinate h(a) = a·perp4 supplies the *microscopic* internal-
  space degree of freedom; the *coarse phason field* is w(r) = ⟨h⟩ locally averaged; strain
  is the offset-subtracted spatial variation of w (uniform offset is not strain —
  demonstrated). `phason_strain.py` shows a large finite-size floor, so g_phi is admissible
  only after §6's baseline characterisation.
- **g_c — coherence (secondary, target-informed).** Ideal-vocabulary bulk fraction; vocabulary
  stability under extent/boundary to be shown first.

## 4. Primary experiment (rungs 3-4, target-free)

Conditioning on immediate mobility d(x), measure the **branch distribution** {S_r(y)} over
y ∈ A(x): its dispersion V_r(x) / contrast C_r(x) and mean drift ΔS_r(x). The core question:

> At matched present-state conditions and matched immediate mobility, do some legal next
> moves open into systematically larger future configuration volumes than others?

Then rung 6: does unbiased dynamics **sample high-S_r branches beyond the degree baseline**?
The uniform-neighbour walk has stationary π(x) ∝ d(x); measure finite-time occupancy vs S_r
*after conditioning on d*, to separate a genuine volume-driven flow from the trivial degree
one.

## 5. Secondary experiment — signed drift

`b_g(x) = mean_{y∈A(x)} [g(y) − g(x)]`, exact per state, plotted vs g, for g_phi (floor-
corrected, §6) and g_c. Restoring drift = b_g < 0 above the strain-free value.

## 6. g_phi baseline characterisation (mechanical, before g_phi is used)

Per GPT: run **clean** patches over several extents L and several cut offsets; estimate the
clean finite-size baseline `g_phi,0(L)` and its scaling with patch/coarse-cell size; then use
either the baseline-corrected `Δg_phi = g_phi − g_phi,0(L)` or the normalised excess
`g̃_phi = (g_phi − g_phi,0(L)) / σ_clean(L)`. Choice decided **after** seeing the clean
distribution: subtraction if the floor is deterministic-with-size, z-scoring if noisy. No
signed-drift claim on g_phi before this is done.

## 7. Controls — the five ways this could fool us

- **Bounded-coordinate regression** (trap for §5): defeated by the matched-scramble at equal
  g and by the conditional analysis.
- **Degree bias** (trap for §4): the claim is unequal volume *after conditioning on d(x)*;
  degree conditioning is built into the primary experiment and into rung 6.
- **Matched random-tiling scramble** (rung 4; fixed now, applied blind to the drift): flip-
  saturated states matched to the genuine state on a pre-declared vector — vertex count,
  degree distribution, tile/rhombus frequencies, defect count, and the target coordinate —
  each within a stated tolerance (±2% distributional, exact on counts); nearest match under a
  fixed weighted distance; a g-bin with no in-tolerance match is reported "no admissible
  control", never stretched. Scramble validity **demonstrated** (retains the low-order vector,
  destroys higher-order order) not assumed.
- **Within-family degree-matched control** (new, per GPT): compare two *ordinary* states from
  the *same* family at matched d(x) and low-order observables, and ask whether deep Ω_r varies
  more than expected — testing whether "deep future volume" is structured *before* any QC-vs-
  scramble label is attached.
- **Label-shuffle negative control** (new, per GPT): shuffle the state→(coherence/family)
  label while preserving degree. If the Ω_r–orderedness relation survives the shuffle, the
  structure is graph-topological but **not** tied to quasiperiodic order. This cleanly
  separates "state-space structure exists" from "structure aligns with QC order" — different
  discoveries.
- **Detailed-balance audit** (recast from a v1 error): on the reversible flip graph under a
  Metropolis-corrected proposal (min(1, d(x)/d(y))), zero stationary cycle affinity is
  *expected*; a non-zero corrected current is a **bug signal** triggering an implementation /
  state-definition / boundary audit, not a discovery.

## 8. Conditional analysis, and the horizon caveat

- **Conditional (not subtraction alone):** fit whether order / family label predicts the tip
  quantities (V_r, C_r, ΔS_r, b_g) after conditioning on g, d(x), defect count and tile
  statistics; report effect sizes with CIs.
- **Horizon-locality (per GPT):** Ω_r is reliable only for small r (2, sampled 3). A null
  therefore means *no short-horizon continuation-volume asymmetry detected* — **not** "the
  state space has no directional asymmetry." Conversely a positive at r = 2 is *stronger* in
  one sense: the asymmetry is very local in configuration space, leaving little room for
  long-range modelling artefacts.

## 9. Hypotheses

- **H0** — no intrinsic bias survives the controls.
- **H1a** — a drift/branch-asymmetry exists but is reproduced by the matched random-tiling
  control (generic graph combinatorics).
- **H1b** — an effect beyond the low-order controls (genuinely quasiperiodic-ensemble), but
  common across fields.
- **H2** — a robust **field-specific** excess across 8/10/12.

**Tempered (per GPT):** a field-specific result motivates GIV-level work only after lower-
level causes are excluded — move topology, acceptance-window geometry, recurrence, state-space
connectivity, finite-size arithmetic. GIV is the last resort, not the first.

## 10. Predictions, to be scored

- **P1** g_phi drift restoring at ensemble level (random-tiling expectation). **0.65.**
- **P2** survives the matched-scramble at equal g (not bounded regression). **0.40.**
- **P3** branch asymmetry V_r/C_r exceeds the degree-matched and label-shuffle nulls (rungs
  3-4). **0.40.**
- **P4 (control)** Metropolis-corrected stationary current is zero within noise; non-zero
  triggers an audit. **Expected: zero.**
- **P5** any surviving effect is field-specific (H2). **0.20.**
- **P6** dynamics flows toward high-S_r branches beyond the degree baseline (rung 6, "tip
  realised"). **0.25.**

Overall: **H0 0.35 / H1a 0.20 / H1b 0.25 / H2 0.20.** Scoreable, not precise.

## 11. Interpretation to be *earned*, not assumed

If (and only if) the data climb the ladder, the natural reading is the crew's second
commandment made operational: **least resistance ~ largest accessible continuation volume** —
the present tips toward the futures that open onto more future. This is stated as the
interpretation the data would license, not a premise; H0 and H1a would retire it.

## 12. Out of scope, recorded so it is not lost

**Growing state space (expansion).** The sustained "reconstruction into each new slice of now"
plausibly needs the accessible configuration space to keep growing, so drift never
equilibrates — home of the cosmological-time reading. Strictly downstream of this fixed-patch
test.

## 13. Compute honesty

Ω_r is a config-space BFS and grows fast; computing S_r(y) for every y ∈ A(x) at every
sampled x is d(x) × BFS per state. So: r = 2 exact where feasible, r = 3 sampled over a
subset of moves/states, with the horizon caveat (§8) attached to every claim.

---

## Change-log

**v1 -> v2 (GPT review 1):** g_c demoted; g_phi tightened + floor demonstrated; d(x) vs Ω_r/S_r
naming; degree bias made a null; matched-scramble specified; conditional analysis added; P4
recast as audit; literature narrowed; H1 split; H2 tempered; evidential ladder added; target-
free experiment elevated to primary.

**v2 -> v3 (GPT review 2):** branch asymmetry V_r/C_r added as the core "tip" quantity
(unequal downstream opportunity across immediate moves, distinct from total neighbourhood
size); rung 6 added (asymmetry *exploited* vs merely *available*: flow toward high-S_r beyond
the π ∝ d degree baseline); within-family degree-matched control added; label-shuffle negative
control added; g_phi baseline-characterisation procedure specified (§6); microscopic-coordinate
vs coarse-field wording made careful; horizon-locality caveat strengthened; "least resistance ~
continuation volume" interpretation stated as earned-not-assumed (§11); compute-honesty note
(§13).

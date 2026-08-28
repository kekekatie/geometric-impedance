# Draft pre-registration: does address survive an increasingly complete real-space description? (physical-radius saturation)

**Status — DRAFT for crew knife-sharpening (Karen, Gemini, GPT/work-GPT, Fable; Claude). NOT
sealed, NOT run. No data touched to write this.** Repairs and strengthens the confound controls
behind the sealed transport result (`PREREG_transport_hierarchy.md`, `RESULTS_TRANSPORT.md`).
Built from work-GPT's foundation audit (2026-08-26) + Claude's adversarial response. Seal only
after the crew signs off; corrections then go in a dated amendment.

---

## 0. The narrowed claim we are testing

The audit correctly narrowed the transport positive to: *perpendicular-space descriptors capture
transport-relevant stationary spectral structure not exhausted by the physical descriptors
tested so far.* This pre-reg asks the decisive follow-up: **does that "not exhausted" survive as
the real-space description is made progressively more complete and more expressive?**

## 1. The central test — the physical-radius ladder

For a coherent observable, measure the **address increment**

    ΔR²_addr(r) = R²( physical(r) + address ) − R²( physical(r) ),   held out,

as the physical description grows over radii **r = 2 → 4 → 8 → 12 → 16** (edge units). Report
ΔR²_addr(r) with confidence intervals across offsets and extents, as a curve.

- **physical(r):** a genuinely expressive real-space block within radius r — radial density
  histogram g(ρ) for ρ up to r (fixed bin width), neighbour-degree distribution moments within
  r, coarse-grained bond-orientational order ψₙ averaged within r, edge-length distribution
  moments within r, and local packing/void statistics within r. It grows monotonically with r.
- **address:** the frozen M4 perpendicular-space block from the sealed test — hull/window depth,
  shell-averaged perp at scales {2,4,8}, address variance across those scales, perp-address
  gradient. Fixed across all r (address never changes; only the physical baseline grows).

### Pre-registered outcomes (mutually exclusive readings of the curve)
1. **Fades to zero:** ΔR²_addr(16) / ΔR²_addr(2) < 0.25 and CI includes 0 at r=16 → address is a
   brilliant **compression of long-range physical geometry**; no irreducible perp content.
2. **Positive plateau:** ΔR²_addr(r) flattens with CI excluding 0 for r ≥ 8 (and
   ΔR²_addr(16)/ΔR²_addr(8) > 0.6) → the tested physical descriptions **do not exhaust** what
   address captures.
3. **Representational, not informational:** ΔR²_addr(r) only collapses once physical(r) is given
   the **equal-expressiveness** treatment (§3 parity control), not merely more radius → the
   original advantage was chiefly a **better representation** of shared information.
4. **Unstable / finite-size:** ΔR²_addr(r) varies beyond its cross-offset CI across extents →
   the result is finite-size dependent; report as unresolved, do not interpret.

## 2. Corrected conditional null (repairs the sealed shuffle's gap)

The sealed stratified shuffle conditioned on fine motif type (which *does* subsume orientational
class and degree — a point on which we correct the audit) but **not** on the continuous
descriptors g(r), edge lengths. This pre-reg promotes a **fully-conditional null** to first
class, in two forms, at every rung r:

- **(a) Residual-orthogonal null (primary).** Cross-fit residualize each address feature against
  physical(r) with the same nonlinear model; keep only the physical(r)-orthogonal residual; test
  its increment. (This generalizes the already-run roadmap-step-1 residualization to every r.)
- **(b) Conditional permutation null.** Permute address labels within **k-nearest-neighbour cells
  in physical(r)-feature space** (not just motif×degree bins), so all of physical(r) — continuous
  descriptors included — is approximately held fixed. A genuine increment must vanish under both.

## 3. Fake-address and equal-feature-count controls (guards representation/capacity artefacts)

At every rung r, alongside the real increment, measure:
- **Fake-address:** a surrogate field with the address's **marginal distribution and spatial
  autocorrelation matched** but its genuine perpendicular-space organization destroyed
  (phase-scrambled / stratified-shuffled address). Expected ΔR² ≈ 0. Guards "any smooth field
  helps."
- **Equal-count noise:** a block of random features with the **same dimensionality** as the
  address block. Expected ΔR² ≈ 0. Guards "more columns ⇒ higher R²" (GBT capacity).
- **Equal-count physical (parity):** an **additional** genuine physical block of the *same
  dimensionality* as the address block. If this matches the address increment, outcome 3
  (representational) is favoured; if address still beats equal-count physical, informational.

## 4. Address-feature ablations (what specifically carries the signal)

At a fixed reference radius, remove each address-feature group **one at a time** (hull/window
depth; shell-averaged perp; address variance; perp gradient) and measure the drop; and test each
group **alone**. Identifies which perpendicular-space quantity actually carries the increment
(and whether it is the *pointwise depth* vs the *neighbourhood organization* — connecting to
`RESULTS_ADDRESS_SPLIT.md`).

## 5. Validation, extents, offsets (stability + leakage)

- **Held-out-offset CV** (≥ 6 fresh window offsets) — as in the sealed test.
- **Spatially-blocked CV (new):** additionally split each single patch into disjoint spatial
  blocks (quadrants/rings), train on some, test on held-out blocks — guards *within-patch*
  spatial-autocorrelation leakage that offset-CV alone can miss. The claim must survive **both**.
- **Multiple extents:** run at ≥ 3 patch extents (e.g. 12 / 14 / 16) to expose finite-size
  dependence (outcome 4). Bulk-only (r < 0.8 r_max) throughout.
- Same regressor (fixed before the run) for every rung, control, and family.

## 6. Observable — spectral now, one dynamical endpoint required

- **Primary (this pre-reg):** per-vertex coherent LDOS in the mid-band window |E|∈[0.8,2.5], as
  sealed. Honestly labelled a **stationary spectral** observable, *not* literal transport.
- **Required dynamical endpoint (stage-two, pre-registered here):** the "reads the address"
  language is earned for **transport** only once the increment also appears on a genuinely
  dynamical quantity — pre-specified as the **bulk wavepacket mean-square-displacement exponent**
  from a localized start, measured pre-boundary — analysed with the identical ladder + controls.
  Until then the claim is about spectral structure, not transport.

## 7. Coherence-causation (sequenced after radius)

The quantum/classical contrast shows *which structure* carries address, not that *coherence
causes* it (two different observables, not a dial). The **Haken–Strobl dephasing sweep** — one
observable, γ dialled from coherent toward classical — is the causal test, and is pre-registered
to run **only after** the radius result is settled (per the audit's ordering).

## 8. Hypotheses & credences (to be scored)

- **H_compression** (outcome 1): address fades under a complete real-space description. **0.40.**
- **H_irreducible** (outcome 2): a positive plateau survives. **0.20.**
- **H_representational** (outcome 3): collapses only under equal-expressiveness. **0.30.**
- **H_unstable** (outcome 4): finite-size dependent. **0.10.**
Honest prior, post-audit and post-residualization: the mass has shifted toward compression /
representational and away from "irreducible hidden address" — the residual-orthogonal result
(+0.004) already leans that way.

## 9. Decision rule

Read the ΔR²_addr(r) curve against §1's four pre-registered outcomes, requiring the increment to
(a) survive **both** conditional nulls (§2), (b) exceed **both** the fake-address and equal-count
controls (§3), and (c) be stable across extents (§5). Only a signal meeting all three, on the
dynamical endpoint (§6) as well as LDOS, earns "a physical law reads the address as transport."
Absent that, report the precise weaker outcome. No new ontology ("perp space is physical")
regardless of result.

## 10. Out of scope / later

Cross-system reconnaissance ("where else does a compact internal coordinate predict a system's
response beyond bounded-radius physical descriptors?") is deliberately quarantined until this
radius experiment says what kind of object we are carrying. Coherence sweep per §7.

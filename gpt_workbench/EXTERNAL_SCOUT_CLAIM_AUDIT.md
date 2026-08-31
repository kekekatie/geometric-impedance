# External-scout claim-language audit — current manifests vs the six implications

**Date 2026-08-31. Documentation-only audit. No study dynamics / address / LDOS / β / targets
accessed; nothing sealed; science branch untouched.** Originally read-only; following Work-GPT/Sol's
approval, its single indispensable finding (implication 3) was applied as a documentation-only
wording repair — G5 relabelled cross-engine non-reproduction, "coherence-specific" removed as an
earned verdict (MSD v8.1 §7/§12; concordance G5). No endpoints, thresholds, other gates, denominators,
config sets, or runtime design were changed. Companion to
`EXTERNAL_LITERATURE_SCOUT_SYNTHESIS_DRAFT.md` (commit `03d5f40`).

Audited: conditional-null **v4.1**, physical-radius **v7**, MSD **v8.1**, decision-gate concordance.
The six implications are quoted in the scout synthesis §"Provisional implications".

---

## Headline
Five of the six implications are already substantially satisfied by the current claim language. The
**one genuine pre-seal claim-language error is implication 3** (a coherent-only result must not be
called "coherence-specific" merely because the specified CTMC does not reproduce it — inspect the
generator mismatch first).

## The one genuine pre-seal claim-language error — implication 3

**Exact potentially-overstrong sentences:**
- MSD §7: *"if a **classical** config fails, the corresponding **coherence-specific (G5) comparison
  is inconclusive**"*
- MSD §12 G5: *"it **prevents the strongest coherence-specific claim**"* (implying a G5 pass
  **licenses** such a claim)
- `DECISION_GATE_CONCORDANCE.md` G5 question: *"not reproduced by the classical walk?"*

**The defect.** The coherent engine is `H = A` (MSD §1); the sole classical comparator is the
**degree-normalised** CTMC `Q = A·D⁻¹ − I` (MSD §10). On the **irregular** quasicrystal graphs
(degree is itself a feature), these are **different operators**, so a G5 divergence can reflect
**generator choice, not coherence** — exactly Scout 1's caution ("adjacency-CTQW and degree-normalised
classical diffusion use different operators; a coherence-specific claim requires operator-level
care"). "Coherence-specific" is therefore not earned by G5 as written.

**Verdict — wording repair, INDISPENSABLE pre-seal.** Relabel G5 as *"not reproduced by the specified
degree-normalised classical walk"* and strike "coherence-specific" as an earned verdict; add a
one-line generator-mismatch caveat. The frozen top-line claim (MSD §12: *"predicts heterogeneity in
full-spectrum wavepacket spreading beyond the frozen physical descriptions and controls"*) is
**already correct** and needs no change — only the G5-adjacent "coherence-specific" language does.

**Optional robustness control — NOT pre-seal (corrected per Work-GPT/Sol).** To separate coherence
from generator choice one must **match the generators, which changes BOTH engines** — not swap only
the classical side. Simply substituting a classical combinatorial-Laplacian walk `Q' = A − D = −L`
against the present quantum `H = A` is **not** generator-matched (it pairs a Laplacian classical
process with an adjacency quantum process). The correct future study is a **paired Laplacian
comparison**: quantum `e^{−itL}` versus classical `e^{−tL}` (with `L = D − A`), **signs and
conventions frozen at design time**.
- *Cost:* it re-runs **both** engines under a new generator — a whole second propagation design, not a
  cheap add-on.
- *Scientific caveat:* even the paired-Laplacian comparison is **not a uniquely definitive** classical
  analogue; there is **no unique** classical counterpart of a given quantum generator. It **brackets**
  the coherence-vs-generator confound, it does not close it. It **changes both engines** and is a
  **separate future study**, **not a pre-seal addition** (adding it now would be protocol creep —
  implication 6), the way MSD §11 defers the mid-band secondary.

## Implications already satisfied — no manifest change

| # | Implication | Status | Evidence (exact) |
|---|---|---|---|
| **1** | residual = beyond frozen `physical(r)` family, not beyond the rooted neighbourhood unless exact-patch matched | **Satisfied** | Residual null is `X_r`-orthogonal (cond-null §2); claims read *"beyond the frozen physical descriptions and controls"* (§7); §7 explicitly *"NOT a categorical 'irreducible' verdict."* No exact rooted-patch matching is done, and none is claimed. |
| **2** | address = compact encoding of multiscale context, not a strong ontology | **Satisfied** | Cond-null §7 *"No literal perpendicular-space DOF ontology"*; MSD §12 *"No inference that perpendicular space is a literal physical degree of freedom."* |
| **4** | don't imply pair/topology/loop/bottleneck matched unless they were | **Satisfied** | Claims scoped to *"the frozen physical descriptions/descriptors and controls,"* never to "geometry"/"topology." The matched family (dens, deg, g(ρ), ψ, Voronoi, motif) demonstrably excludes ring/loop, connectivity/bottleneck, chord/lineal-path descriptors — and no sentence claims otherwise. |
| **5** | preserve spectral-vs-transport & finite-size | **Satisfied** | MSD §3 *"full-spectrum wavepacket-transport test — NOT a mid-band test … does not by itself establish the mid-band LDOS mechanism"*; §11 removes the spectral secondary; G0 `t_bound* > 8` strict + authorised *finite-size-limited* outcome (§12). Matches Scout 3's near-null / finite-size caution. |

**Optional documentation-only notes (future, not sealing blockers):** (a) enumerate in the manifests
the descriptors *not* matched (loop/ring, connectivity/bottleneck, chord-length) so "physical
descriptors" is never over-read (implication 4); (b) add the positive phrase "compact encoding of
multiscale structural context" to the address framing (implication 2); (c) note that any future
*"beyond the rooted radius-`r` neighbourhood"* claim would require exact weighted-patch isomorphism
matching, Scout-1 style (implication 1).

## Recommendation — indispensable vs future

- **Indispensable pre-seal — DONE (approved by Work-GPT/Sol; applied MSD v8.1 + concordance):** the
  implication-3 wording repair in MSD §7/§12 and concordance G5 — removed "coherence-specific" as a
  G5-earned verdict, relabelled G5 **cross-engine non-reproduction** against the specified
  degree-normalised classical CTMC, stated the generator-mismatch caveat explicitly. Claim-language
  only; no protocol expansion; top-line claim unchanged.
- **Future exploratory (register, do not build now):** the **paired-Laplacian** comparison (quantum
  `e^{−itL}` vs classical `e^{−tL}`, signs frozen — changes **both** engines, not a uniquely
  definitive analogue); the three optional documentation notes; and — only if a "beyond the rooted
  neighbourhood" claim is ever desired — exact weighted radius-`r` patch-isomorphism matching.

Per implication 6, only the one wording repair is treated as blocking; everything else is deferred.
**Update (2026-08-31):** Work-GPT/Sol approved this conclusion — implication 3 is an indispensable
claim-language repair, with **no new propagation control** added. The G5 wording repair has been
applied as a documentation-only amendment (MSD v8.1 §7/§12, `DECISION_GATE_CONCORDANCE.md` G5); no
endpoints, thresholds, other gates, denominators, config sets, or runtime design were changed, and the
frozen top-line claim is unchanged.

*Not part of the scientific record until reviewed and merged.*

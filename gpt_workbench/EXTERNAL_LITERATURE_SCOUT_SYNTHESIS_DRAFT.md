# DRAFT — external literature-scout synthesis (PROVISIONAL LEAD MAP, not verified authority)

**Status — DRAFT reconnaissance record for crew review. NOT sealed. NOT part of the scientific
record. No study dynamics / address values / LDOS / β / targets / scientific outcomes were accessed
in producing it; no science-branch file was altered.**

> **Provenance and epistemic status (read first).** The material below is a synthesis of **three
> ChatGPT Deep Research reconnaissance reports** supplied to Work-GPT/Sol and relayed by Katie. It is
> a **lead map, not verified authority.** Every claim, exponent, and citation here is **unverified**
> and must be checked against the **primary source** before it is used in any manifest,
> preregistration, or eventual paper. **Post-design literature findings must not be allowed to alter
> endpoints or decision thresholds opportunistically** (see implication 6). This file exists so the
> leads are *durable and auditable*, not so they are *acted on*.

*Source: transcribed by the `gpt/workbench` Claude collaborator from crew-relayed Deep Research
output; committed to `gpt/workbench` only.*

---

## Scout 1 — Dynamics at locally indistinguishable sites

**Central result (as reported).** Exact isomorphism of **weighted rooted radius-`r`
neighbourhoods** fixes the adjacency **closed-walk moments through length `2r+1`**. For the CTQW
return amplitude, the first possible difference caused by structure *outside* the matched ball is
therefore of order **`t^{2r+2}`**. **Cospectral** vertices remain identical in return amplitude at
**every** time; **automorphism-equivalent** vertices are indistinguishable up to relabelling.

**Small reproducible example (as reported).** NetworkX **Frucht graph**, vertices 0 and 6. Rooted
balls isomorphic through radius 2; diagonal adjacency moments agree through `k=5`, then differ at
`k=6`: **95 vs 93**. Both the CTQW return **and an ordinary classical random walk** distinguish
them — **this is not uniquely quantum.**

**Important caution (as reported).** On **irregular** graphs, adjacency-CTQW and
degree-normalised classical diffusion use **different operators**. A quantum/classical difference
may therefore reflect **generator choice** rather than coherence. A "coherence-specific" claim
requires **operator-level care**.

**Literature areas.** Cospectral and strongly cospectral vertices; walk-regular non-transitive
graphs; equitable partitions; graph covers; photonic CTQW; microwave latent symmetry.

**Reported gap.** No identified experiment explicitly (i) matching rooted neighbourhoods through a
stated `r`, (ii) matching onsite / coupling / disorder conditions, and then (iii) demonstrating an
effect attributable **solely** to structure beyond `r`.

## Scout 2 — Inflation ancestry as multiscale site context

**Central result (as reported).** Atomic/molecular RG paths, conumber ordering, and
perpendicular-space coordinates can predict local spectral structure, impurity susceptibility, and
— in metallic-mean chains — launch-dependent dynamics. These labels ordinarily **encode
progressively larger physical environments**; they **should not automatically be treated as
independent hidden degrees of freedom.**

**Strongest dynamical analogue (as reported).** Thiem & Schreiber, silver-mean chain: a launch site
remaining atomic through five RG steps follows the atomic-RG spreading exponent (**β ≈ 0.3828**) and
shows hierarchical time-domain resonances. **No explicitly radius-matched contrasting launch partner
was supplied.**

**Strongest deeper-ancestry response (as reported).** Moustaj, Kempkes & Morais Smith: sites sharing
an initial atomic/molecular class but differing in **deeper RG path** show different responses to an
**introduced onsite impurity**. This is an **impurity-response** result, **not** pristine launch
transport.

**Two-dimensional static analogue (as reported).** Oktel's Ammann–Beenker **compact localised
states**: centres share the same immediate eight-edge vertex type, while **acceptance-window
subregions / larger environments** distinguish localised-state classes.

**Experimental analogue (as reported).** Reisner et al. measured site-resolved
**LDOS / multifractality** in dielectric-resonator **Fibonacci** chains; conumber ordering exposes
recursive structure. **Spectral, not transport.**

**Transport platform (as reported).** A reported **2026 photonic Fibonacci** experiment measures MSD
and autocorrelation across localisation-to-ballistic regimes, but **does not** apparently perform
ancestry-conditioned locally-matched launches.

**Reported gap.** No clean experiment or numerical study explicitly pairing **weighted radius-`r`
isomorphic** sites with **different deeper ancestry** and then showing **different pristine
spreading.**

**Primary leads (verify before use).**
- Thiem & Schreiber — arXiv:1204.4017
- Moustaj, Kempkes & Morais Smith — arXiv:2011.11428
- Macé et al. — arXiv:1601.00532
- Oktel — arXiv:2103.08678
- Reisner et al. — arXiv:2207.13755
- Penrose magnetisation — arXiv:0711.2670

## Scout 3 — Transport after low-order structural matching

**Central result (as reported).** Density and ordinary two-point structure **do not necessarily
determine transport.** The evidence becomes **much weaker** when pair information, motifs, topology,
bottlenecks, boundaries, and local geometry must **all** be matched **simultaneously.**

**Strongest classical computational comparison (as reported).** Skolnick & Torquato's **degenerate
Debye random media** share phase fraction and the **complete conventional two-point correlation
`S₂(r)`**, yet differ in percolation, diffusion, and fluid transport. Pore-size, chord/lineal-path,
connectivity, and bottleneck descriptors **also differ**, so this establishes the **insufficiency of
`S₂`**, not a uniquely isolated higher-point cause.

**Strongest coherent analogue (as reported).** Deterministic **Rudin–Shapiro** chains possess
random-like **uniform pair diffraction** while exhibiting singular-continuous spectral structure and
**weak anomalous wavepacket diffusion.** Longer words and motif statistics were **not fully matched**
to Bernoulli controls.

**Downgraded common examples (as reported — each changes something en route).**
- stealthy hyperuniform vs random **deliberately changes `S(k)`**;
- random dimers **deliberately change short-range pair correlations**;
- hyperuniform vortex pins **change weak channels / bottlenecks**;
- fixed-degree amorphous networks **can still differ** in bond lengths, angles, rings, and `S(k)`;
- phason randomisation **changes local geometry and connectivity**;
- photonic band gaps are **spectral**, not automatically transport measurements.

**Near-null warning (as reported).** Jagannathan & Tarzia report **substantial eigenstate /
multifractal changes without corresponding diffusion-exponent changes** over part of the disorder
range; apparent enhanced delocalisation can also be **finite-size dependent.**

**Primary leads (verify before use).**
- Skolnick & Torquato — Phys. Rev. E **104**, 045306; arXiv:2107.12856
- Kroon & Riklund — Phys. Rev. B **69**, 094204
- Jagannathan & Tarzia — Phys. Rev. B **107**, 054206
- random-dimer photonic transport literature
- stealthy-hyperuniform transparency — arXiv:1510.05807

---

## Provisional implications requiring independent audit (verbatim intent)

1. Describe any residual as information **beyond the frozen `physical(r)` descriptor family**, **not**
   beyond the **complete rooted radius-`r` neighbourhood** — unless **exact rooted-patch matching**
   was performed.
2. Treat perpendicular address as a **compact encoding of multiscale structural context** unless
   evidence supports a stronger interpretation.
3. Do **not** call a coherent-only result **"coherence-specific"** merely because the specified CTMC
   comparator does not reproduce it; **inspect the generator mismatch first.**
4. Do **not** imply pair structure, graph topology, loop statistics, or bottlenecks were matched
   **unless they genuinely were.**
5. **Preserve spectral-versus-transport and finite-size distinctions.**
6. **Do not expand the current protocol indefinitely** in response to this reconnaissance. Identify
   only **genuine claim-language errors** or **indispensable pre-seal controls.**

---

## Audit trace against the current manifests (summary; full analysis returned to crew)

A narrow audit against the six implications was performed on 2026-08-31 (full findings in
`EXTERNAL_SCOUT_CLAIM_AUDIT.md`). Headline: five of the six implications are already substantially
satisfied by the current claim language; **the one genuine pre-seal claim-language repair is
implication 3** — the term "coherence-specific" was used as a verdict earned via **G5**, whose only
classical comparator is the **degree-normalised CTMC `Q = A·D⁻¹ − I`**, while the coherent engine uses
**`H = A`**. On the irregular quasicrystal graphs these are **different operators**, so a G5 divergence
can reflect **generator choice, not coherence** (Scout 1 caution). **Following Work-GPT/Sol's
approval this was applied as a documentation-only repair** (MSD v8.1 §7/§12; concordance G5): G5 is
relabelled **cross-engine non-reproduction** and "coherence-specific" removed as an earned verdict —
no new propagation control, no endpoint/threshold/gate/denominator/config-set/runtime change, top-line
claim unchanged. The remaining implications (1, 2, 4, 5) require **no manifest change**. The only
generator-matched way to separate coherence from generator choice would be a **paired-Laplacian**
study (quantum `e^{−itL}` vs classical `e^{−tL}`, signs frozen — changes **both** engines), registered
as a **separate future study**, not a pre-seal addition.

*Not part of the scientific record until reviewed and merged. Leads unverified; check primary sources
before any citation or claim.*

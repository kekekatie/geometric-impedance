# Silent Corruption in Aperiodic Substrates: A Relational Integrity Diagnostic for Error-Correcting Architectures

**K. T. Niedzwiecki**

Independent Researcher, South Australia

---

## Abstract

Li and Boyle (2024) demonstrated that aperiodic tilings — including Penrose, Ammann-Beenker (AB), and Fibonacci geometries — give rise to a remarkable class of quantum error-correcting codes (QECCs) in which quantum information is encoded through the geometric structure of the tiling itself. Their analysis establishes that these codes are robust against erasure errors, where a finite patch of the tiling is deleted and reconstructed from the surrounding geometry. Here we introduce a substrate-level diagnostic for a distinct perturbation class we term *silent relational corruption*: the scrambling of a graph's connectivity topology while preserving local degree statistics. Unlike erasure, silent relational corruption produces no detectable gap in the substrate — the perturbation leaves no visible trace. Although motivated by aperiodic quantum error-correcting codes, the present audit is classical: it evaluates recoverability of privileged-persistence sites under controlled graph perturbations, not the performance of a quantum code. Using a matched degree-preserving rewiring protocol applied to AB (N=16,997) and Penrose (N=21,539) substrates generated via cut-and-project methods, we demonstrate that vulnerability to silent relational corruption is substrate-dependent and predictable from a geometric invariant: the exo/endo persistence axis. AB substrates, whose structural logic is stored in hidden perpendicular-space coordinates (exo-addressed), retain near-ceiling identity recoverability under full relational scrambling (AUC = 0.986). Penrose substrates, whose structural logic resides entirely in the local relational weave (endo-reconstructive), show substantially reduced identity recoverability (AUC = 0.855 for the best-performing hybrid model; address-only AUC = 0.661). We further demonstrate that identity persistence and functional reconstruction are operationally distinct processes — the former is address-led, the latter weave-led — and that hybrid architectures incorporating both channels provide complementary redundancy under mixed damage. These findings suggest that silent relational corruption resistance should be evaluated as a substrate selection criterion for aperiodic error-correcting architectures.

---

## 1. Introduction

The discovery that aperiodic tilings constitute quantum error-correcting codes (Li & Boyle, 2024) establishes a deep connection between quasicrystalline geometry and quantum information theory. In the Li-Boyle construction, quantum information is encoded in superpositions of tilings within a single equivalence class, exploiting the local indistinguishability property: any finite patch of one tiling appears somewhere in every other tiling of the same type. This property guarantees that local erasure — the deletion of any finite region — reveals nothing about the encoded quantum state, and that the erased region can be uniquely reconstructed from the complementary geometry.

The Li-Boyle framework has been extended to Ammann-Beenker and Fibonacci tilings, to finite spatial tori, to discrete spin systems, and to arbitrary spatial dimensions. Connections to condensed matter physics, quantum gravity, and holographic tensor networks have been noted (Boyle, Dickens & Flicker, 2020; Boyle & Mygdalas, 2026). However, the error model analysed to date has been exclusively erasure-based: errors that delete patches, producing detectable gaps in the tiling substrate.

Real physical substrates face a broader spectrum of perturbation. In any implementation, the effective interaction graph may differ from the intended design due to calibration drift, crosstalk, fabrication defects, or coupling disorder. These processes share a common abstract structure: they modify the relational topology of the substrate while preserving local statistical properties such as the degree sequence. We do not model any specific physical noise process here. Instead, we use degree-preserving rewiring as an abstract stress test for what we term *silent relational corruption* — perturbation that alters global topology without producing any locally detectable signature.

This perturbation class may function as a substrate-level analogue of decoherence: the degradation of structural coherence through scrambling that preserves local statistics but disrupts global organisation. We avoid claiming a direct equivalence to quantum decoherence, which carries a specific formal meaning. The analogy is structural and motivational; the diagnostic itself is classical.

We show that vulnerability to silent relational corruption is not uniform across aperiodic substrates. Rather, it is predictable from a geometric invariant we have previously identified (Niedzwiecki, 2025, 2026): the axis distinguishing *exo-addressed* persistence (where structural privilege is determined by hidden perpendicular-space coordinates, invariant under graph rewiring) from *endo-reconstructive* persistence (where structural privilege is encoded entirely in the local relational weave, and disrupted when that weave is scrambled).

This paper presents a substrate-integrity diagnostic — a pre-code auditor — that evaluates aperiodic tiling graphs against silent relational corruption and identifies a functionally important split: identity persistence (recovering what was encoded) is address-led, while functional reconstruction (supporting continued organisation after damage) is weave-led. We propose that this dual-audit framework provides a new criterion for substrate selection in the design of aperiodic error-correcting architectures.

## 2. Background

### 2.1 Aperiodic tilings and the cut-and-project method

Aperiodic tilings such as the Penrose and Ammann-Beenker geometries are generated by projecting higher-dimensional periodic lattices onto irrationally oriented lower-dimensional subspaces. The physical tiling occupies "parallel space," while the orthogonal complement constitutes "perpendicular space." The selection of lattice points for projection is governed by an acceptance window in perpendicular space.

The Ammann-Beenker (AB) tiling possesses 8-fold rotational symmetry, generated from a Z⁴ multigrid construction with an octagonal acceptance window in its two-dimensional perpendicular space. The Penrose tiling possesses 5-fold (or 10-fold) symmetry, generated via a 5D cut-and-project construction with residue-class pentagonal acceptance windows.

### 2.2 The Li-Boyle aperiodic QECC

In the Li-Boyle construction, quantum states are superpositions of all tilings within a single equivalence class (the set of all tilings related by rigid rotations and translations). Local indistinguishability — the property that any finite patch appears in every tiling of the same type — ensures that erasure of any finite region reveals no information about the encoded state. The erased region can be uniquely inferred from the surrounding intact geometry, satisfying the recoverability criterion for quantum error correction.

Li and Boyle construct variants of this code on Penrose, Ammann-Beenker, and Fibonacci substrates, demonstrating that the error-correcting property is generic to aperiodic tilings exhibiting local indistinguishability.

### 2.3 The exo/endo persistence axis

In prior work (Niedzwiecki, 2025, 2026), we established that aperiodic geometries store structural constraint through two fundamentally distinct mechanisms:

**Exo-addressed persistence (Ammann-Beenker).** Privileged structural sites — nodes that consistently retain signal across multiple conductance-retention scales — are predictable from their perpendicular-space coordinates (the octagonal shell structure). This predictability survives complete degree-preserving rewiring of the physical graph. The structural blueprint exists in a hidden coordinate space external to the relational graph.

**Endo-reconstructive persistence (Penrose).** Privileged sites are predicted by graph-local features — the immediate relational neighbourhood. This predictability is substantially reduced under degree-preserving rewiring. The structural blueprint is embedded in the relational weave; scrambling the weave disrupts the blueprint.

This asymmetry is confirmed in the present study using matched protocols on AB (N=16,997) and Penrose (N=21,539) substrates at comparable scale.

## 3. An error taxonomy for aperiodic substrates

We distinguish three perturbation classes relevant to aperiodic architectures, characterised by what they damage and whether they are locally detectable:

### 3.1 Erasure (patch deletion)

A contiguous region of the tiling is removed. The perturbation is *loud*: the blank patch is immediately detectable, and a correction algorithm can examine the surrounding intact geometry to reconstruct the missing region. This is the perturbation class addressed by Li and Boyle. Both Penrose and AB substrates handle it well, as demonstrated by the recoverability proof.

### 3.2 Silent relational corruption (degree-preserving topological scrambling)

The connectivity of the tiling graph is modified through edge swaps that preserve the degree of every node. Vertices are neither added nor removed; what changes is which vertices connect to which. The perturbation is *silent*: there is no blank patch, no missing node, no change in local degree statistics. The graph remains locally plausible — it retains the same degree distribution, the same number of vertices and edges — but its global topological coherence has been disrupted.

The critical distinction from erasure is detectability. An erasure triggers a correction protocol because the gap is visible. Silent relational corruption leaves no such trace. Any system relying exclusively on the integrity of its relational weave for structural coherence is vulnerable to this perturbation class, precisely because it cannot detect when the weave has been altered.

### 3.3 Address corruption (perpendicular-space noise)

Noise is applied directly to the hidden perpendicular-space coordinates that define the exo-addressed layer. This perturbation class is specific to substrates possessing an address layer (e.g., AB) and degrades the identity-persistence channel while leaving the relational weave intact. It is included in our diagnostic to test the hybrid architecture's resilience under mixed damage.

## 4. Methods

### 4.1 Substrate generation

**AB substrate:** 22,663-node Ammann-Beenker tiling generated via Z⁴ multigrid construction, with edges defined by K-vector neighbour relations (pairs of vertices whose integer lifting coordinates differ by exactly one unit along a single lattice axis). 44,126 edges. Interior-75% subset (16,997 nodes) used for primary analysis to avoid boundary effects.

**Penrose substrate:** 28,719-node Penrose tiling generated via 5D cut-and-project construction with pentagrid method. 54,695 edges. Interior-75% subset (21,539 nodes) used for primary analysis.

Both substrates include full perpendicular-space coordinates for every vertex, enabling cross-validated logistic regression using address features (perpendicular-space coordinates and derived quantities) and weave features (graph-local density metrics recomputed from the current adjacency matrix).

### 4.2 Privileged site identification

Strict shared-core nodes are identified via a conductance-retention surrogate: nodes maintaining top-quartile retention of random-walk packets across three structural scales (graph-distance radius 2, Euclidean-distance radius 3× median edge length, and one-hop packet seeds). This produces 752 strict shared-core nodes on the AB interior subset and 208 on the Penrose interior subset.

### 4.3 Degree-preserving rewiring

A double-edge-swap algorithm is applied to each substrate, maintaining the exact degree sequence while randomising the specific connectivity pattern. Rewiring intensity is set to 5× the edge count (5E) per replicate: 220,630 attempted swaps for AB, 273,475 for Penrose. Ten rewired replicates per substrate were generated, achieving near-complete topological randomisation (edge Jaccard index between native and rewired graphs: 0.0001 for both substrates).

### 4.4 Address noise

Gaussian noise of varying magnitude (0.00, 0.20, 0.40, 0.60, 0.80, 1.00 standard deviations of the native coordinate distribution) is added to perpendicular-space coordinates prior to the address-feature prediction step, enabling a fine-grained assessment of the hybrid rescue effect.

### 4.5 Two-audit framework

We introduce a dual-audit protocol that separates two operationally distinct questions:

**Identity persistence audit.** After perturbation (rewiring ± address noise), can the *original native* strict shared-core sites be recovered from the available features? This tests whether the substrate retains a recoverable record of its prior structural organisation.

**Fresh reconstruction audit.** After perturbation, if conductance-retention labels are regenerated on the damaged graph, what predicts the *new* privileged sites? This tests whether the perturbed system can still support coherent structural organisation — independent of its original configuration.

### 4.6 Prediction and evaluation

Cross-validated logistic regression models are fitted using three feature blocks: address-only (perpendicular-space features), weave-only (graph-local features recomputed from the current adjacency), and hybrid (address + weave). Performance is evaluated by area under the ROC curve (AUC), averaged across rewired replicates. Standard deviations across replicates are reported.

## 5. Results

### 5.1 Native baseline verification

Regenerated conductance-retention labels on the native (undamaged) graphs confirm methodological fidelity, with consistent privileged-site identification across the three seed protocols.

### 5.2 Identity persistence under silent relational corruption

Under full degree-preserving rewiring (5E intensity) with no address noise, using interior-75% subsets:

| Substrate | Address AUC | Weave AUC | Hybrid AUC |
|-----------|------------|-----------|------------|
| AB        | 0.986 (0.000) | 0.991 (0.001) | 0.989 (0.001) |
| Penrose   | 0.661 (0.000) | 0.830 (0.004) | 0.855 (0.003) |

The AB substrate retains near-ceiling identity recoverability through its address layer. The Penrose substrate's identity is recoverable only through weave and hybrid features, at substantially reduced fidelity; the address-only channel is weak (AUC = 0.661).

### 5.3 The hybrid rescue under mixed damage

As address noise increases on AB, address-only identity AUC degrades while hybrid remains near ceiling. The weave channel compensates for address degradation, providing complementary redundancy: each channel covers the other's failure mode. This rescue effect is absent on Penrose, where address signal is too weak to contribute meaningfully; hybrid tracks weave at all noise levels.

### 5.4 Fresh reconstruction is weave-led on both substrates

Under full degree-preserving rewiring, the regenerated privileged sites bear almost no overlap with the native originals (Jaccard: 0.004 for AB, 0.003 for Penrose). On both substrates, the address channel is at chance level for predicting fresh sites (AUC ≈ 0.52–0.54), while the weave channel strongly predicts where new privileged sites form (AUC: 0.892 for AB, 0.912 for Penrose).

This establishes a clean functional separation. The address layer carries no information about *where the system will reconstruct* — only about *where things were*. The weave layer carries no memory of the original configuration — only about *where things are now*. The address is a fossil record: it preserves the coordinates of the prior state, even after the living system has completely reorganised. The weave is the living ecology: it determines where reconstruction happens in the present tense.

### 5.5 The address-as-noise effect

On both substrates, adding noised address features to the fresh reconstruction model degrades performance relative to weave-only prediction. This confirms that the two audits measure genuinely distinct processes: features that aid identity persistence can actively impair fresh reconstruction prediction when they carry noise rather than signal.

## 6. Discussion

### 6.1 Silent relational corruption as a substrate-level vulnerability

The central finding is that aperiodic substrates differ in their vulnerability to silent topological scrambling, and that this vulnerability is predictable from the exo/endo persistence axis. AB substrates possess a geometric shield: their structural logic is stored in perpendicular-space coordinates that are invariant under any rearrangement of the physical graph. Penrose substrates have no such shield; their structural logic is the relational weave itself.

For architectures built on aperiodic substrates, this asymmetry implies that the choice of geometry may carry consequences beyond those visible under erasure testing alone. A substrate whose structural coherence depends entirely on the integrity of its relational weave — as the Penrose substrate does — is inherently more exposed to any perturbation process that modifies connectivity without producing a detectable signal. The perturbation would not announce itself; the substrate would offer no indication that its structural organisation had been compromised.

We note that this finding does not constitute a demonstration of failure in any quantum error-correcting code. It identifies a substrate-level asymmetry that we propose is relevant to code design: before constructing a code on a given aperiodic geometry, a relational integrity audit of the kind presented here may reveal vulnerabilities that erasure testing alone would not expose.

### 6.2 Identity and reconstruction: two requirements for structural integrity

The dual-audit framework reveals that structural integrity under perturbation involves two operationally distinct requirements:

**Identity persistence** — the ability to recover the prior structural organisation — is address-led. It requires a stable coordinate system external to the perturbable graph. On AB, perpendicular-space coordinates provide this. On Penrose, no such system exists with comparable strength.

**Functional reconstruction** — the ability of the perturbed system to continue supporting coherent structural organisation — is weave-led. It depends on the current local topology, regardless of what the original configuration was. This requirement is met on both substrates: both AB and Penrose systems can regenerate coherent privileged sites from their current graph structure after rewiring.

A system that satisfies only the first requirement remembers what it was but may no longer function. A system that satisfies only the second requirement continues to function but has lost the record of its prior state. A substrate that must both update and remember — as any system encoding persistent information must — requires both layers.

The hybrid address-weave architecture provides exactly this complementary structure. Under mixed damage (relational scrambling + address noise), the hybrid channel on AB outperforms either channel alone, because each covers the other's specific vulnerability. This is not mere redundancy through duplication; it is redundancy through *functional complementarity*, with each channel serving a distinct operational role.

## 7. Limitations and future work

This study establishes a classical substrate-integrity diagnostic, not a quantum error-correcting code simulation. The conductance-retention surrogate used to identify privileged sites is a classical analogue of the structural constraints that underpin aperiodic tiling organisation. Translating these findings into the full quantum-mechanical framework of the Li-Boyle construction — including explicit calculation of logical error rates under degree-preserving perturbation of the code Hamiltonian — is a necessary next step to determine whether the substrate-level asymmetry identified here propagates into differential code performance.

The "hybrid" architecture tested here is a simple feature concatenation (address + weave) fed to a logistic classifier. More sophisticated integration strategies — such as a hierarchical model that queries the address layer for identity and the weave layer for reconstruction separately — may better capture the complementary redundancy that the data suggest.

Finally, the relationship between the abstract stress test presented here and physically realistic noise channels in specific hardware platforms deserves careful analysis. Degree-preserving rewiring serves as a principled worst-case probe of relational integrity, but a quantitative mapping to specific noise parameters in superconducting, trapped-ion, or photonic architectures would strengthen the bridge to experimental quantum error correction.

We also note a suggestive connection to recent work on spacetime quasicrystals (Boyle & Mygdalas, 2026), which extend aperiodic tiling geometry into Minkowski spacetime while preserving the cut-and-project structure that underpins both quasicrystalline order and the Li-Boyle QECC. If aperiodic geometry plays a role in the error-correcting structure of spacetime — as suggested by connections to holographic tensor networks and conformal quasicrystals (Boyle, Dickens & Flicker, 2020) — then the exo/endo axis may carry implications for how information survives topological perturbation at cosmological scales. This remains speculative but may warrant future investigation.

## 8. Conclusion

We have introduced a substrate-level diagnostic for silent relational corruption — degree-preserving topological scrambling that produces no locally detectable signature — and demonstrated that vulnerability to this perturbation class is substrate-dependent and predictable from the exo/endo persistence axis in aperiodic geometries.

The Ammann-Beenker substrate, with its exo-addressed structural logic stored in hidden perpendicular-space coordinates, retains near-ceiling identity recoverability (AUC = 0.986) under full relational scrambling. The Penrose substrate, with its endo-reconstructive structural logic stored entirely in the local relational weave, shows substantially reduced identity recoverability under the same perturbation (hybrid AUC = 0.855; address-only AUC = 0.661) — and, critically, the perturbation produces no locally detectable trace.

The dual-audit framework introduced here separates two operationally distinct aspects of structural integrity: identity persistence (address-led: recovering what the system was) and functional reconstruction (weave-led: supporting continued coherent organisation after perturbation). These map onto distinct functional requirements, and a hybrid architecture incorporating both channels provides complementary redundancy under mixed damage.

We propose that silent relational corruption resistance be evaluated as a criterion in the design and selection of aperiodic substrates for error-correcting architectures, alongside the established criterion of erasure recoverability.

---

## References

Boyle, L., Dickens, M., & Flicker, F. (2020). Conformal quasicrystals and holography. *Physical Review X*, 10, 011009.

Boyle, L., & Mygdalas, S. (2026). Spacetime quasicrystals. arXiv:2601.07769.

Li, Z., & Boyle, L. (2024). The Penrose tiling is a quantum error-correcting code. arXiv:2311.13040.

Niedzwiecki, K. T. (2025). Memory without memory: Geometric persistence in aperiodic networks. Zenodo.

Niedzwiecki, K. T. (2026). Two strategies for geometric persistence: Exo-addressed vs. endo-reconstructive survival in aperiodic tilings. Zenodo.

---

## Figure captions

**Figure 1.** Identity vs. fresh reconstruction under full 5E degree-preserving rewiring, with 10 replicates per substrate. Four panels comparing AB (top row) and Penrose (bottom row) across identity audit (left column) and fresh reconstruction audit (right column). The identity/reconstruction split is visible in the separation between columns: AB identity is address-led (address AUC = 0.986), while Penrose identity requires the hybrid channel (AUC = 0.855). Fresh reconstruction is weave-led on both substrates (address at chance, weave AUC > 0.89).

**Figure 2.** Apples-to-apples comparison of identity persistence AUC under matched 5E stress testing. AB interior-75% (N=16,997) vs Penrose interior-75% (N=21,539), both with edge Jaccard = 0.0001 indicating near-complete topological randomisation. The exo/endo asymmetry is preserved at matched scale.

---

*Correspondence: K. T. Niedzwiecki. Independent researcher, South Australia. GitHub: kekekatie/giv-theory.*

*Data and analysis code: Available at [Zenodo DOI] and [GitHub repository].*

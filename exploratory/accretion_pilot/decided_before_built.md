# Decided before it is built: Local choices and their consequences in a growing Penrose tiling
**K. T. Niedzwiecki**
**16 October 2026**

## Abstract
How much of an unbuilt pattern can a local choice already constrain? We examine this question in a growing Penrose tiling by following both options at a two-way choice. Two preregistered computational studies compare the resulting tiles with an internal-space representation of compatible offsets. In the first, a learned cut-direction table predicts the dominant edge family in $17/17$ held-out configurations. A corrected exploratory analysis of all 45 configurations identifies five direction-family correspondences; all 41 elongated differences align with the associated orientation rule within $2.6^{\circ}$. In a follow-up, the initial forced response carries the predicted family in $45/45$ configurations, including 32 absent from the first sample. Later choices can alter further details. Under explicit completeness and valid-extension assumptions, an initial forced sequence belongs to every completion of the chosen patch before its tiles are placed. This supports a distinction between determination and construction, while leaving open the full extent and persistence of a choice's consequences.

## 1. Begin with a choice
Imagine a pattern growing one tile at a time. At some exposed places, only one tile fits the local rules. At others, more than one fits. Our algorithm fills the forced places first and makes a choice only when no forced placement remains. Figure 1 begins at such a choice. We keep the existing patch, take option A in one copy and option B in another, and let both grow.

The difference is larger than the initial tile. Over the following steps, a narrow region appears where the two branches contain different tiles. A small decision at the boundary has a spatially extended consequence. Our question is how much of that consequence can be identified early, and how much is already fixed rather than merely likely.

A Penrose tiling has order without a repeating unit cell. Its higher-dimensional description supplies a second view of the same construction [1, 2]. Alongside the visible patch, we calculate a region of internal offsets compatible with its vertices. We call this region F. An offset is a parameter in the mathematical construction, not a position somewhere else in the visible pattern.

Each added tile contributes constraints. For the choices analysed here, the two branches yield opposing boundary facets in F along a shared line. We call this the cut line. The local growth rule does not consult F to decide which tile to place: F is an analytical description of the constraints left by construction. Nor does a nonempty computed F, by itself, establish that the decorated patch has a valid infinite completion.

Local-rule growth of Penrose tilings is established prior work [3]. The contribution of this note is the comparison between an early cut in the compatibility region, the geometry of the subsequent branch difference, and the portion of that response obtained without another choice.

## 2. Watching the consequence take shape
A front is the exposed boundary where tiles can attach. A slice is one update of the patient scheduler: it places locally forced tiles when available and otherwise makes a choice. A slice is an algorithmic step, not a unit of physical time. The implementation uses triangular half-tiles of the rhombic tiling; counts below are half-tile counts.

To compare branches, we do more than ask which has grown farther. A tile enters the measured changed region when the other branch has a different tile covering its centroid. Tiles extending into space the other branch has not reached are excluded from that measurement. This distinction matters because the two branches can have unequal coverage.

In the first study we compare the branches after 20 slices. Across 45 distinct configurations, no measured changed region is empty and its median size is 84 half-tiles. The example in Figures 1 and 2 was selected by proximity to the median size among elongated cases, rather than by visual appeal.

The cut is measured after the first forced slice. Most of the changed region is constructed later. Pooling 4,331 placement observations gives the descriptive fit placement slice $\approx 2.44 + 1.09 \times$ distance along the strip, in edge lengths. Distance is the absolute projection along the fitted strip axis, measured from the initial option-A tile's centroid. Larger differences contribute more observations to this fit, and observations within a configuration are related. It describes construction in these runs; it is neither a causal propagation law nor a measured speed limit.

This brings the central tension of the study into view. In the compatibility region $F$, the dividing cut line is already present after the first forced slice; in the world, the corresponding strip of changed tiles is assembled one local step at a time over twenty slices, never outrunning the attaching front. How can a single static cut in the hidden offset region anticipate the direction and structure of a strip that has not been built yet—and is that unbuilt response merely a statistical tendency, or is a substantial core of it already logically settled the moment the choice is made?

## 3. A directional pattern and a connected core
Tile edges fall into five indexed families, each a direction. A half-tile has sides in two families. We count the fraction of changed tiles incident to each family and call the largest share the dominant family. This measures directional preference; it does not by itself establish a single connected ribbon.

The first study trained a lookup table on worlds 0-11 and tested it on worlds 12-23, excluding configurations already seen in training. It predicted the dominant family in $17/17$ held-out configurations. The test contained only three families, with counts 11, 3 and 3; always choosing its majority family would score $11/17$.

The original angle bins were misplaced. The registered scorecard remains intact; correcting the bins yields the following descriptive mapping across all 45 configurations, including training cases:

| Cut-line direction | Dominant family | Configurations |
| :--- | :--- | :--- |
| $18^{\circ}$ | 2 | 11 |
| $54^{\circ}$ | 1 | 1 |
| $90^{\circ}$ | 0 | 22 |
| $126^{\circ}$ | 4 | 8 |
| $162^{\circ}$ | 3 | 3 |

All 41 elongated differences lie within $2.594^{\circ}$ of the associated orientation rule. The rare directions have little coverage, particularly the single family-1 case.

The follow-up asks whether the pattern is already present before another choice. It is: the initial forced response has the predicted dominant family in $45/45$ configurations. The largest chain selected by the predicted-family adjacency covers at least half of each side's changed tiles in $90/90$ sides, with median share 0.670. This establishes a substantial connected core in the sampled responses, rather than identifying the entire difference with one ribbon.

## 4. A later choice can change what happens next
For each follow-up configuration, we run five continuations of each initial option, changing the random streams used for later choices. The dominant family remains the same across all five paired A/B comparisons in $44/45$ configurations, and in those cases equals the early prediction.

That headline needs its denominator unpacked. Of 450 branch continuations, 380 make no further choice within 20 slices; 70 make one. Among the 14 configurations in which a later choice occurs, family persistence is $13/14$. Among the other 31 it is $31/31$. Different random streams do not necessarily produce different geometries when there is no decision for the randomness to affect.

Figure 4 shows the exception. Its initial forced response has predicted family 2, but the five later paired comparisons have dominant families [2, 2, 3, 3, 3]. The A branch makes no later choice; each B continuation makes one. The same initial option can therefore coexist with different subsequent outcomes in these finite runs.

The stricter registered test P4 asks whether core tiles built from a later choice onward agree across continuations of the same option. Only two configurations supply eligible covered comparisons; one passes and one fails. Pooled agreement is $44/92$ comparison instances. The sample is small, but it is enough to defeat a blanket claim of complete later agreement under that test.

It does not follow that every earlier constraint disappears at the next choice. A later choice changes some details without erasing the built patch. Whether other unbuilt features remain fixed must be assessed separately. The initial forced burst is a certified subset under the assumptions below, not the measured boundary of all influence from the original choice.

## 5. In what sense is something already decided?
The word decided can mean either a successful prediction or a logical consequence. The orientation and family counts are empirical findings. The claim about an initial forced sequence has a different basis.

Assume that the patch after the chosen option has at least one valid complete extension. Assume also that, at each exposed site, candidate enumeration includes every tile that could occupy that site in such an extension, and that the geometry and legality checks are correct. If exactly one candidate remains, every complete extension must contain it. After adding it, apply the same reasoning again. By induction, each tile in the resulting forced sequence belongs to every completion of the chosen patch. A simultaneous slice must also consist of mutually compatible additions.

Under those assumptions, the sequence is fixed before the algorithm has placed all its tiles. The program still has to discover and construct it step by step. Nothing in the argument requires a signal to travel into the unbuilt region, or a second mechanism that places tiles ahead of the front.

The argument does not prove that the implementation's candidate list is complete. Nor does it turn nonempty F into a proof of global extendability. Those remain assumptions requiring separate justification if the computational result is to become an unconditional theorem about all valid completions.

The forced-only calculation stops when no forced placement remains, or at a cap of 40 slices. Of 90 branch responses, 66 reach the cap and 24 stop earlier. For the capped responses, 40 is a lower bound on forced duration, not a natural endpoint. Duration in slices is also not a measurement of spatial width.

Three statuses are therefore useful:
*   **Already built:** A tile is present in the current patch.
*   **Certified by the forcing argument:** A tile belongs to the computed forced sequence and is fixed in every completion, subject to the stated assumptions.
*   **Not certified by that argument:** Further analysis is needed: the tile may be genuinely open, or fixed for reasons this local calculation has not established.

These statuses need not form three neat spatial bands. In particular, reaching another choice ends this simple forced-sequence certificate; it does not prove that every tile beyond it is undecided.

The distinction gives the title its precise meaning. "Before it is built" refers to the logical status of the forced continuation relative to the chosen patch. It does not assert that the whole 20-slice difference is settled, or that an early numerical predictor determines every later tile.

## 6. Why the directions correspond
The five directions offer a short geometric explanation, with a clear boundary between arithmetic and observation. In the coordinate convention used by the code, physical family j has direction edge direction $=18^{\circ}+72^{\circ}j$, with $j=0,1,2,3,4$.

A vertex has five integer lift coordinates. The internal projection assigns the jth coordinate direction angle 144°j. This is the indexed correspondence underlying the familiar angle-doubling description: successive indexed directions advance by $72^{\circ}$ in the physical plane and $144^{\circ}$ in the internal plane. It is not a rule that doubles arbitrary angles between arbitrary vectors.

The window representation used here has four pentagonal sections. Their facet-normal directions agree, modulo $180^{\circ}$, with the five indexed internal directions; the supplementary numerical check evaluates the actual window used by the implementation.

The empirical bridge is that the measured cut normal corresponds to the dominant changed family. Across the 45 first-study configurations, that correspondence is exact to numerical precision. It gives cut-line direction $=90^{\circ}-36^{\circ}j$ (mod 180°).

If a changed region's axis is perpendicular to that family's physical edges, its direction is $108^{\circ}+72^{\circ}j$. Eliminating j gives strip-axis direction $=108^{\circ}-2\times$ cut-line direction (mod 180°). Algebraically, this angle-doubling reflects a general property of cut-and-project lattices: the physical tiling and the internal acceptance window are images of each other under Galois conjugation of the underlying number field ($\tau \leftrightarrow -1/\tau$ for the golden field $\mathbb{Q}(\sqrt{5})$), which permutes the five pentagrid directions by $j \mapsto 2j \pmod 5$ and doubles the step between consecutive indexed directions from $72^\circ$ to $144^\circ$.

This last step is exact arithmetic once the family correspondence and perpendicular alignment are supplied. The alignment of a finite, fitted changed region is an empirical input: the 41 elongated cases differ from the formula by at most 2.5935167334°. Rounder regions do not provide an equally informative long axis.

The pentagrid description [1, 2] motivates a relation between an internal offset and where a family of tracks falls. But a proof that every relevant two-way growth choice induces the observed branch-difference family has not been supplied. Nor does the connected-core measurement establish that the complete difference is one ribbon. We therefore present this as a partial geometric explanation of a measured correspondence, not a universal ribbon theorem.

## 7. Constraint, construction and room for novelty
The same developing pattern can be described through what has been placed, what is already implied, and what remains open. The studies make that distinction concrete. Early compatibility geometry identifies a directional feature; a substantial initial response is obtained without another guess; later choices can alter additional structure.

An earlier decision can thus establish a long, coherent commitment without freezing the future. Within the initial forced burst—which reaches the 40-slice cap in 66 of 90 branch responses and halts earlier at a new live choice in 24—consequences are settled before they are built, and the front constructs them one local layer at a time. Where the forced burst meets a subsequent choice, direct certification hands over. The earlier choice does not dictate which option the later choice will take (P4), but it biases what remains possible, because the later choice inherits the narrower compatibility region $F$ carved by the earlier cut. Between a periodic crystal (where the first cell settles everything and the present has no decisions left to make) and unconstrained random growth (where every site requires a guess and decisions have no forced reach), this local-rule Penrose growth occupies an intermediate regime: long forced runs of coherent structure punctuated by genuine branch points.

This also clarifies the motivating phrase the reach of the present. Behind the front, tiles are already built; at the front, a single attaching layer is being placed; ahead of the front, a connected core of future placements is already logically fixed by the current patch before any tile is laid there. The attaching boundary and the settled reach are distinct quantities and come apart differently: the first is one layer thick by construction, whereas the second extends as far as the forced burst runs and ends where the next choice begins.

The compatibility region $F$ offers a corresponding perspective on memory. Nothing in these results requires $F$ to act as a historical store that records the sequence of past events. Rather, $F$ shrinks because choices were made and fewer completions remain compatible with the built patch. The window does not hold the past; it holds the constraint the past has left on the future, while the expanding front discovers and builds that constraint step by step.

**A three-dimensional question**
Local growth of icosahedral tilings and its relation to worm planes already have a developed literature [4]. A natural extension is to ask whether early compatibility constraints identify the orientation and extent of branch-dependent forced regions in that setting.

The two-dimensional correspondence cannot simply be relabelled as six edge families. The construction discussed by Hann, Socolar and Steinhardt has six star directions and fifteen possible worm-plane normal directions [4, Sections II and IV.A]. An appropriate correspondence must distinguish edge directions from face and worm-plane normals before it is registered and tested. Even a successful three-dimensional tiling experiment would leave its interpretation as physical space as a separate question.

**What this note establishes**
An early cut identifies a directional feature of the later difference. A substantial connected core appears in the forced response, whose membership in every completion follows under explicit assumptions. Later choices can still alter further details. A local choice has more reach than its own tile, while the future can retain unresolved structure.

## 8. Methods and sampling
**Growth and selection.** Both studies use the atlas-based local candidate rule and patient scheduler in the repository [5]. Each grows 24 worlds from finite seeds, targeting 1,500 added half-tiles per world. Eligible two-way choices require positive computed compatibility areas for both branches and a detected cut line. The first study records 67 eligible choices and the follow-up 65. Each reduces to 45 configuration keys by retaining the first occurrence.

The key represents the whole base patch relative to the choice point, using translation-normalized coordinates rounded to 0.001 edge lengths and a truncated hash. "Distinct" and cross-study overlap therefore refer to this operational key, not an independently proved classification of patches. The two samples share 13 keys; the follow-up adds 32. The predicted family is found in the forced response of all 32 new cases. These counts provide additional configurations, not 32 statistically independent experimental replications.

**Window measurement.** F is obtained by intersecting vertex/window half-plane constraints at the patch's lift rank. Opposing facets in the two branch regions identify the cut. The measurement follows the first forced slice. A cut can be detected from the choice tile alone in only $14/45$ follow-up configurations; in all 14 its direction agrees with the later reading. We do not describe the measured cut as universally available at the instant that tile is selected.

**Branch comparison.** Each option is continued for 20 slices. Within an A/B pair the random-stream seed is shared. Changed half-tiles are nonidentical tiles whose centroids are covered by a nonidentical tile of the other branch. Tile identity retains the implementation's decoration information. Family shares count incident edge directions and can sum to more than one because each half-tile has two families. The dominant family is the largest share, with the implementation's fixed index ordering for ties.

The fitted axis is the leading principal component of changed-tile centroids. Aspect ratio is the square root of the ratio of the two covariance eigenvalues; a ratio of at least 3 defines an elongated region. Angles are compared modulo $180^{\circ}$. The construction fit pools placement slice against absolute distance along that axis; no independent-observation uncertainty estimate is inferred from its 4,331 entries.

**Forced responses and connected cores.** Each branch is grown without further guesses until forced growth stops or reaches 40 slices. The changed region is then computed between those responses. Core adjacency joins changed tiles through shared edges of the predicted family, or through the common base joining the two halves of a rhombus. The largest connected component defines the core. The P2 denominator is all changed tiles on that branch's side.

**Later choices.** The follow-up also runs five 20-slice continuations of each initial option. P4 selects core tiles placed from the first later guess onward, including that guess's slice. For each option it compares every ordered pair of continuations, counting only tiles whose locations are covered in the other continuation. Its pooled denominator counts comparison instances, not unique independent tiles. A configuration passes when its worst eligible pair has at least 99% agreement. The registered target was that at least 80% of eligible configurations pass.

## 9. Registered tests and descriptive follow-up
**Table 1. Original registered scorecards.** The cut-direction results retain the original bins; the corrected mapping in Section 3 is reported separately.
*   **C1:** Largest family share exceeds the next by $\ge0.15$ in $\ge70\%$ of configurations | $44/45$ criterion met
*   **C2:** Training lookup predicts family in $\ge80\%$ of held-out configurations with a known direction | $17/17$ criterion met; three families represented
*   **C3:** Observed training bins map to different families | Four bins four families; criterion met in registered bins
*   **C4:** Axis lies within $20^{\circ}$ of perpendicular to the dominant family's edges in $\ge70\%$ of elongated cases | $41/41$ criterion met
*   **P1:** Initial forced response has predicted family in $\ge90\%$ of configurations | $45/45$ criterion met
*   **P2:** Largest core covers $\ge50\%$ of changed tiles in $\ge60\%$ of branch sides | $90/90$ sides; median 0.670, IQR 0.662-0.686
*   **P3:** Dominant family agrees across five paired continuations in $\ge90\%$ of configurations | $44/45$ criterion met; these also match the prediction
*   **P4:** Worst covered core comparison agrees at $\ge99\%$ in $\ge80\%$ of eligible configurations | $1/2$ criterion not met; $44/92$ pooled instances

The original cut-line bins rounded angles to multiples of $36^{\circ}$, whereas the observed lines lie at $18^{\circ}+36^{\circ}k$. The binning merged the $126^{\circ}$ and $162^{\circ}$ directions, producing a mixed training bin. The held-out examples fell in unmixed bins. The corrected all-sample mapping is informative, but it is not a replacement held-out test of all five families.

Follow-up family counts for indices 0-4 are 16, 0, 13, 6, 10. In particular, the follow-up supplies no family-1 example. The 32 new configurations have counts 11, 0, 9, 5 and 7. Coverage across families remains uneven.

The $13/14$ persistence rate among configurations with later choices is a descriptive stratification performed in review. It is useful because the overall $44/45$ includes many runs with no later choice. The non-core control for post-choice comparisons gives 1,208/2,242 identical covered instances, showing that the comparison procedure can register differences where later choices occur.

Both registrations precede the corresponding implementation additions in the recorded Git history on 15 October 2026: 04:59:34 versus 05:00:48 UTC for the first study, and 05:46:30 versus 05:47:45 UTC for the follow-up. This establishes the repository chronology, not the absence of earlier private exploration. The audit and figure reconstruction are later descriptive work.

## 10. Reproducibility and contributions
The source baseline is repository commit d4e00c5d4396c38bd69b265907b5f3d6c5bc030a, under exploratory/accretion_pilot/ [5]. The cut_direction/ and settled_test/ directories contain the original studies and saved results. Registrations, the exploratory bin correction, source code and this baseline should be retained alongside the manuscript.

The supplementary checks recompute saved-data summaries and window-direction arithmetic, then reconstruct two selected prefixes with the original engine. The overview, key 2a3cfb2c41f77386 (world 19, slice 31), matches the saved geometry measurements and every placement-time pair. Selection uses the median changed-region size among elongated cases, with a lexicographic key tie-break.

The exception, key 180fb0b920bb845b (follow-up world 21, slice 8), reproduces its entire saved situation dictionary. Figure 4 uses the first indexed pair of B continuations with distinct geometry and distinct paired A/B dominant families. Seeds, streams and comparisons are recorded in results/reconstruction.json.

The companion archive contains the figures, captions, audit outputs, reconstruction scripts and retrieval instructions. Engine reproduction also requires the baseline repository. These are targeted checks with the original implementation, not a complete historical rerun or independent implementation replication. The presentation revision changes no cases or measured results.

**Acknowledgements and Research Provenance**
This work developed through a sustained, year-long collaboration between K. T. Niedzwiecki and a diverse ecosystem of AI assistants. The human author initiated and directed the research, maintaining the overarching physical intuitions and foundational framework. Google Gemini (versions 2.5 Pro and 3.1 Pro) served as the primary conversational partners, providing the imagination and flexibility needed to bridge novel ideas with discrete geometry. The rigorous mathematical formalization and manuscript refinement were achieved through the wide-ranging capabilities of Anthropic Claude and OpenAI GPT (Astra). Claude Code implemented and ran the original studies, while Fable helped shape much of the finishing detail. Astra contributed critical reviews and checks. Argon’s Ammann-bar discussion with the author helped motivate the cut-direction question. These models, both early and recent, acted as invaluable collaborators—each bringing their own strengths to the theory's refinement. The human author is responsible for all final claims and publication decisions. A provenance of this human-AI collaboration is archived at: [Link to upcoming essay].

## References
*   [1] N. G. de Bruijn. Algebraic theory of Penrose's non-periodic tilings of the plane. 1. Indagationes Mathematicae (Proceedings) 84(1), 39-52 (1981). doi:10.1016/1385-7258(81)90016-0.
*   [2] N. G. de Bruijn. Algebraic theory of Penrose's non-periodic tilings of the plane. II. Indagationes Mathematicae (Proceedings) 84(1), 53-66 (1981). doi:10.1016/1385-7258(81)90017-2.
*   [3] G. Y. Onoda, P. J. Steinhardt, D. P. DiVincenzo and J. E. S. Socolar. Growing Perfect Quasicrystals. Physical Review Letters 60, 2653-2656 (1988). doi:10.1103/PhysRevLett.60.2653.
*   [4] C. Hann, J. E. S. Socolar and P. J. Steinhardt. Local growth of icosahedral quasicrystalline tilings. Physical Review B 94, 014113 (2016). doi:10.1103/PhysRevB.94.014113. Open manuscript.
*   [5] K. T. Niedzwiecki and AI buddies. Geometric impedance, computational research repository, baseline d4e00c5 (2026). Pinned source and saved data. Study directories: cut_direction/ and settled_test/.  

# Address Fragility in Aperiodic Substrates: Ammann-Beenker and Penrose Differ in Resilience, Not in Structure

K. T. Niedzwiecki
Independent Researcher, South Australia
Version 1.0 — August 2026

---

## Abstract

Cut-and-project quasicrystals carry two independent descriptions of the same
vertex set: a relational one, the graph of tile edges, and an addressed one, the
coordinates in the perpendicular space that the projection discards. A previous
analysis by this author reported that these two substrates differ in whether the
addressed description exists at all — that Ammann-Beenker retains site identity
through perpendicular space under relational scrambling (AUC 0.986) while Penrose
does not (0.661).

That conclusion does not survive its own controls. We show that the reported
asymmetry is produced by three separable measurement artefacts: a linear
classifier reading a nonlinear decision boundary, unmatched positive rates
between substrates, and — dominantly — boundary contamination penetrating the two
substrates to different depths. With all three removed, both substrates address
their own privileged sites almost perfectly in bulk: 0.9996 for Ammann-Beenker
against 0.9816 for Penrose, a gap of 0.018 against shuffle nulls at 0.50.

The substrates nonetheless differ, and sharply, in a way the earlier analysis
could not see. Under phason disorder — the physically correct perturbation for a
quasicrystal, applied as independent jitter of each candidate's perpendicular
coordinate before the acceptance test — the two separate immediately. At the
first disorder step Ammann-Beenker loses 0.007 of its address readability and
Penrose loses 0.129, roughly nineteen times as much. The gap opens to 0.14 in one
step, reaches 0.21, and plateaus.

We conclude that the distinction between these substrates is one of **fragility,
not of structure**. Both possess a perpendicular-space address channel; what
differs is how that channel survives perturbation, whether the perturbation is
boundary truncation or phason strain. This is a narrower claim than the one it
replaces and a more useful one, since resilience under strain is the property an
error-correcting architecture would actually need.

---

## 1. Introduction

An aperiodic tiling produced by cut-and-project is a shadow. A periodic lattice
in n dimensions is sliced by a two-dimensional plane at an irrational angle, and
the lattice points falling within an acceptance window are projected onto it. The
resulting point set has no translational symmetry but retains long-range order,
and every vertex carries a second coordinate — its position in the perpendicular
space that the projection threw away.

This gives such a substrate two independent descriptions of the same sites. The
**relational** description is the graph of tile edges: who is adjacent to whom.
The **addressed** description is the perpendicular-space coordinate: where each
site sits in the discarded dimensions. The two are not derivable from each other
by any local rule, which makes their relative robustness a well-posed and
physically meaningful question. A perturbation that destroys one need not touch
the other.

A previous paper by this author [1] posed that question as an asymmetry between
substrates, reporting that Ammann-Beenker possesses a usable address channel and
Penrose does not. Section 4 shows that this conclusion was an artefact of
measurement rather than a property of the substrates. Sections 5 and 6 give what
we believe is the correct account: the address channel exists in both, and the
substrates differ instead in how readily it is destroyed.

We report the correction in full, including the mechanism of each error, because
the errors are general. All three would arise in any comparison of two graph
substrates, none is specific to quasicrystals, and each has a cheap null that
detects it.

---

## 2. Background

### 2.1 Cut-and-project construction

For a lattice **Z**ⁿ, a choice of two-dimensional parallel space fixes an
(n−2)-dimensional perpendicular complement. A lattice point is accepted when its
perpendicular projection falls inside an acceptance window, conventionally the
projection of the unit n-cube. Ammann-Beenker arises from **Z**⁴ with an
octagonal window and has a two-dimensional perpendicular space; Penrose arises
from **Z**⁵, with four pentagonal windows indexed by the lift sum, and a
three-dimensional perpendicular space. In both, an edge joins vertices whose
integer lifts differ by exactly one unit along a single lattice axis.

The perpendicular coordinate is not decoration. In cut-and-project, a vertex's
local environment is determined by which sub-region of the acceptance window its
perpendicular coordinate occupies. The address and the local structure are two
views of one fact.

### 2.2 Phason degrees of freedom

Quasicrystals admit a class of deformation with no periodic analogue. A **phason**
rearrangement shifts perpendicular-space coordinates while leaving the tiling
locally valid — tiles still meet, matching rules still hold, and the object
remains a quasicrystal throughout. Two cases must be distinguished, and
conflating them is easy:

- A **uniform shift** of the acceptance window is a rigid phason translation. It
  maps the tiling to a locally isomorphic tiling. It is a symmetry of the
  construction, not a perturbation, and Section 6.1 confirms it leaves the
  address channel entirely intact even when most edges have changed.
- **Phason disorder** — independent perturbation of each candidate's
  perpendicular coordinate before the acceptance test — scatters flips through
  the patch and generates genuine defects. This is the strain case, and it is the
  perturbation used throughout this paper.

### 2.3 What an address channel is, and what it is not

We define the address channel operationally: the extent to which a model reading
only perpendicular-space coordinates can identify a substrate's privileged sites,
where privilege is defined purely from graph topology. High readability means the
discarded dimensions still carry the information; chance readability means they
do not.

The earlier framing [1] treated this as a binary property distinguishing
substrates. We now regard that as a category error. Both substrates carry the
information; the question is how much perturbation the carrying survives.

---

## 3. Methods

### 3.1 Substrates

Both substrates were generated from scratch by cut-and-project rather than reused
from the earlier analysis, so that the measurements do not inherit its pipeline.
The Ammann-Beenker generator reproduces the original substrate exactly: rebuilding
the edge list from the original lift file's K0–K3 coordinates using the same
adjacency rule returns 44,126 edges and matches the file's own degree column on
all 22,663 vertices with zero mismatches. The Penrose generator, built
independently from the **Z**⁵ construction, produces single-edge-length tilings
with coordination numbers 3–7 and mean degree 3.92 against the original
substrate's 3.81.

Both generators reproduce the earlier analysis's published figures to within
0.005 (Section 4.1), which establishes that the corrections below apply to the
published analysis and not to a variant of it.

### 3.2 Privileged sites at matched positive rate

Privilege is scored from three retention measures on the graph — a radius-2 graph
ball, a Euclidean ball at three median edge lengths, and the closed neighbourhood
— combined as a rank-averaged composite and thresholded at a fixed fraction.

This replaces the earlier three-way top-quartile intersection, which fixed the
per-criterion threshold but left the resulting positive rate free. Under that
definition Ammann-Beenker yielded 4.4% positives and Penrose under 1%, and at
smaller patch sizes Penrose yielded too few to score at all. A comparison built on
it therefore differed in positive rate as well as in substrate. The composite
gives both substrates identical positive rates by construction.

The composite is built from graph topology alone. Address features are
perpendicular-space coordinates and share no term with it.

### 3.3 Perturbation

Phason disorder is applied as independent Gaussian jitter of each candidate's
perpendicular coordinate before the acceptance test. Vertices near the window
boundary enter or leave; the tiling remains a valid quasicrystal.

### 3.4 Evaluation and nulls

Address readability is the cross-validated AUC of a gradient-boosted classifier
predicting the privilege label from perpendicular-space coordinates alone. A
**shuffle null** — perpendicular coordinates permuted across vertices, preserving
the exact value distribution and destroying only the correspondence — runs beside
every measurement reported in this paper. No figure is quoted without one.

---

## 4. Correction to the earlier analysis

### 4.1 Reproduction

Run on the original substrates at the earlier analysis's own interior-75% crop
and intersection labels:

| quantity | published [1] | reproduced |
|---|---|---|
| AB identity / address | 0.9790 | 0.9792 |
| AB identity / weave | 0.9914 | 0.9910 |
| AB fresh / weave | 0.8923 | 0.8886 |
| Penrose identity / address | 0.661 | 0.6535 |
| Penrose identity / weave | 0.830 | 0.8322 |
| Penrose identity / hybrid | 0.855 | 0.8534 |

### 4.2 The weave figures are the preserved degree sequence

The earlier analysis perturbed substrates by degree-preserving edge rewiring,
which drives edge Jaccard to 0.0001 while leaving every vertex degree exactly
intact. Its "weave" features are local degree summaries, and its privilege label
is itself degree-driven: on a locally tree-like rewired graph the closed
neighbourhood retention score reduces algebraically to 2/(1 + mean neighbour
degree), a monotone function of one of the features supplied to the classifier
(empirically AUC 0.9991 on AB, 0.9993 on Penrose).

Consequently the identity weave channel scores 0.9910 on AB with the degree
family present, 0.9910 with the degree family alone, and 0.5002 with it removed.
On Penrose the corresponding figures are 0.8322, 0.8349 and 0.4964. The published
weave and hybrid figures measure the one property the perturbation was designed
not to destroy.

The fresh-reconstruction result reported in [1] fails a stronger test: it
reproduces at 0.8977 on a degree-matched configuration model with no tiling
ancestry whatsoever, against 0.8886 on the rewired tiling, and falls to 0.4967
when the degree-family features are ablated. It carries no substrate information
and is withdrawn.

### 4.3 The address gap is boundary contamination

The address channel is not affected by either leak — perpendicular coordinates
are neither degree features nor recoverable from a rewired graph. But the
published address figures were measured at a single interior crop. Sweeping that
crop, at matched positive rates:

| interior retained | AB | Penrose | gap |
|---|---|---|---|
| 90% | 0.9424 | 0.7473 | +0.195 |
| 75% | 0.9980 | 0.8234 | +0.175 |
| 60% | 0.9995 | 0.9492 | +0.050 |
| 50% | 0.9996 | 0.9837 | **+0.016** |
| 40% | 0.9995 | 0.9802 | +0.019 |
| 30% | 0.9997 | 0.9738 | +0.026 |

Shuffle nulls run 0.469–0.524 across all twelve cells.

Ammann-Beenker is saturated from 75% inward. Penrose requires trimming to roughly
50% before reaching bulk behaviour. The earlier analysis was conducted at
interior-75% — inside one substrate's saturated regime and outside the other's —
so what it measured was how far boundary contamination penetrates each substrate,
not whether each possesses an address channel.

### 4.4 Cumulative effect

| analysis | AB | Penrose | gap |
|---|---|---|---|
| as published (linear model, intersection label, 75%) | 0.986 | 0.661 | +0.325 |
| nonlinear model | 0.992 | 0.786 | +0.206 |
| matched positive rate | 0.998 | 0.823 | +0.175 |
| bulk crop | 0.9996 | 0.9837 | **+0.016** |

Each correction removed one confound and reduced the gap. The claim that Penrose
lacks a perpendicular-space address channel is withdrawn.

For completeness: the model-class dependence was itself checked for a
feature-completeness artefact. Penrose lifts from **Z**⁵ and needs a third
address coordinate, but recomputing perpendicular coordinates from the raw lift
reproduces the supplied values exactly, and the lift sum takes only four values,
so the published feature set is complete. Substituting the continuous lift sum
(0.7584) or a complete minimal address (0.7472) recovers nothing.

---

## 5. Result: fragility under phason disorder

Both substrates generated by cut-and-project at matched scale (~16,800 and
~17,500 vertices), cropped to interior-50%, matched 3% positive rate, four
disorder seeds per point.

| disorder | AB | Penrose | gap |
|---|---|---|---|
| 0.00 | 0.9996 ± 0.0001 | 0.9816 ± 0.0021 | +0.018 |
| 0.05 | 0.9929 ± 0.0010 | 0.8525 ± 0.0073 | +0.140 |
| 0.10 | 0.9818 ± 0.0028 | 0.7810 ± 0.0140 | +0.201 |
| 0.20 | 0.9511 ± 0.0092 | 0.7406 ± 0.0282 | +0.211 |
| 0.30 | 0.9041 ± 0.0163 | 0.6801 ± 0.0041 | +0.224 |
| 0.40 | 0.8436 ± 0.0051 | 0.6286 ± 0.0131 | +0.215 |

Shuffle nulls run 0.484–0.517 across all twelve cells; positive counts are
matched to within 5% at every row.

Pristine, the substrates are nearly equivalent. At the first disorder step
Ammann-Beenker loses 0.0067 and Penrose loses 0.1291 — a factor of roughly
nineteen. The gap opens to 0.140 in a single step, reaches 0.21 by amplitude 0.20,
and plateaus. Ammann-Beenker still retains 0.84 at the strongest disorder tested,
where Penrose has fallen to 0.63.

---

## 6. Supporting observations

### 6.1 A uniform window shift is a symmetry

Sweeping the acceptance window offset on Ammann-Beenker leaves address
readability entirely unchanged — 0.9955 at zero shift, 0.9960 at the largest —
while edge Jaccard against the reference patch falls to 0.398. A rigid phason
translation maps the substrate to a locally isomorphic substrate; the address
channel re-registers rather than degrading. This distinguishes the two phason
cases operationally and confirms that the degradation in Section 5 is a property
of disorder rather than of perpendicular-space motion as such.

### 6.2 Convergent evidence from an independent substrate family

Generalising the construction to **Z**ⁿ makes perpendicular dimension a free
parameter. At matched scale and matched positive rate, perpendicular dimension 2
loses 0.005 of its address readability at disorder 0.10 while dimensions 3 and 4
lose 0.250 and 0.197 — reproducing the Ammann-Beenker/Penrose asymmetry in a
different symmetry family with a different generator.

We report this as convergent but not conclusive. The perturbation is isotropic in
perpendicular space, whose dimension is the variable under test, and a
calibration measurement confirms that a fixed amplitude inflicts more damage at
higher dimension (9.4%, 12.8% and 15.9% of vertices flipped at amplitude 0.05).
Whether the effect survives being replotted against measured damage rather than
nominal amplitude is unresolved at the time of writing. We note also that the
data show no monotone scaling with dimension — dimensions 3 and 4 behave
similarly — so any account in terms of "how much was projected away" is not
supported.

---

## 7. Discussion

The property distinguishing these substrates is resilience, not possession. Both
carry site identity in perpendicular space; Ammann-Beenker's carrying survives
strain and Penrose's does not.

This is the more useful claim of the two for the error-correction motivation that
prompted the original work. An architecture that needs an addressed layer needs
one that survives the noise the physical system will actually impose. A channel
that reads perfectly on a pristine patch and collapses at the first strain is not
a resource. The relevant figure of merit is the slope, not the intercept.

The unified statement across both probes is that Penrose's address channel is
intrinsically more fragile than Ammann-Beenker's: it requires roughly twice the
boundary trimming to reach bulk behaviour, and it loses roughly nineteen times as
much readability at the onset of phason strain. Boundary truncation and phason
disorder are both perturbations of the acceptance condition, and Penrose is
markedly more sensitive to both.

**Why** remains unmeasured. The obvious structural difference is that Penrose's
acceptance region is four pentagons indexed by lift sum where Ammann-Beenker's is
a single octagon, and a fragmented window plausibly damages differently under
truncation and jitter than a connected one. We flag this as a hypothesis and
decline to assert it, having spent this paper removing mechanisms that were
asserted rather than measured.

---

## 8. Limitations

- All results use one privileged-site definition. Cross-validation against an
  independent definition is outstanding.
- Disorder amplitude is expressed in perpendicular-space units specific to these
  generators and does not convert to a physical phason strain measure without
  calibration.
- Four disorder seeds per point. The effects reported are large relative to their
  error bars, but ten would be standard.
- Section 6.2 is explicitly unresolved, as stated there.
- This is a classical substrate diagnostic. It is not a simulation of any quantum
  error-correcting code, and no claim is made about the performance of the
  Li-Boyle construction or any other.

---

## 9. Conclusion

Ammann-Beenker and Penrose do not differ in whether they carry site identity in
perpendicular space. In clean bulk both do, at 0.9996 and 0.9816 against nulls at
chance. They differ in how that identity survives perturbation, and the
difference is large: a factor of nineteen in readability lost at the onset of
phason strain, and a factor of two in the boundary trimming required to reach
bulk behaviour.

An earlier analysis by this author reported the difference as one of presence
rather than resilience. That conclusion was produced by a linear classifier
reading a nonlinear boundary, by unmatched positive rates, and dominantly by
measuring at a crop that lay inside one substrate's saturated regime and outside
the other's. All three artefacts are general to substrate comparison, none is
specific to quasicrystals, and each is caught by a null costing a few lines.

---

## References

[1] K. T. Niedzwiecki, *Silent Corruption in Aperiodic Substrates: A Relational
Integrity Diagnostic for Error-Correcting Architectures*, v3 matched-scale, 2026.
Zenodo record 15560880. The present paper supersedes its central result.

---

## Data and code availability

All substrates in this paper are generated from scratch by the code accompanying
it; no external data files are required. Generators, audit scripts, null controls
and per-run outputs are available at
`github.com/kekekatie/geometric-impedance`, under `substrates/`.

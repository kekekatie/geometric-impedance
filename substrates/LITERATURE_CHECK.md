# Literature check: is there an experimental phason-resilience ordering?

Priority #1 of the agreed roadmap. The cyclotomic result predicts address fragility
orders silver > platinum > golden. Before building anything further on it, the
question was whether the experimental record on real 8-, 10- and 12-fold
quasicrystals agrees, disagrees, or is silent.

Source: a deep-research survey covering experimental literature through 16 Aug 2026.
Treated as testimony, not evidence, and spot-checked below.

## Verdict

**Silent — underdetermined, not positive and not negative.**

There is no matched 8-/10-/12-fold dataset in which comparable specimens receive the
same calibrated damage and are measured on a common endpoint. The three families
have been studied with different chemistries, sample dimensions, preparation
histories, temperatures and probes, and with very unequal coverage. The survey's own
summary: the ordering "should presently be described as a specific computational
ordering of address retention under a particular synthetic perpendicular-space
disorder model, not as an experimentally validated ordering of quasicrystal phason
resilience."

The largest single gap is phason elasticity. No directly calibrated experimental
`K_ph` values exist for any of the three target families. The only absolute
determination is icosahedral Al–Pd–Mn (`K₁/k_BT ≈ 0.060`, `K₂/k_BT ≈ 0.031` per
atom), which is outside the rank-four planar comparison. Values quoted for decagonal
or dodecagonal phason elastic constants in the wider literature are generally from
Monte Carlo or molecular dynamics, not experiment.

## Traceability spot-check

Three citations checked against primary sources, chosen as the most load-bearing:

| Claim | Status |
|---|---|
| ~5% tiling mistakes in octagonal Mn₈₀Si₁₅Al₅, from 66 primary + 34 secondary Ammann-line jags | **Verbatim accurate.** Ultramicroscopy, 0304-3991(94)90120-1 |
| Defect-free decagonal growth around shrinkage pores, in-situ synchrotron tomography + MD | **Real.** Phys. Rev. Lett. **135**, 166203 (2025) |
| C₆₀/Pt₃Ti dodecagonal monolayer carries a directly extracted uniform phason strain | **Directionally accurate**; strain deduced from FFT spot shifts, accommodates the layer to a periodic substrate. Specific values (*a* ≈ 1.3, triangle:square 2.67 vs 2.309, ~4% defects) not verifiable at abstract level. Nat. Commun. **8**, 15367 (2017) |

The survey repeatedly qualifies with "the accessible abstract" — it is an
abstract-level reading, and says so. Its reference list is real journals with real
DOIs, several verified. This is a better testimony record than anything else this
project has been handed, and it still should not be cited without opening the papers.

## The observation that cuts against us

The ten-fold/golden family carries by far the strongest direct evidence for
phason-mediated error correction:

- thermal phason flips imaged directly in Al–Cu–Co above 1073 K
- growth errors repairing in ~1 s at 1183 K, 10–20 s at 1123 K (Al–Ni–Co)
- collective "domino" phason-flip strain relaxation by two distinct modes (Al–Cu–Co–Si)
- colliding decagonal grains rotating and coalescing into a single crystal
- growth fronts wrapping shrinkage pores with no retained crystallographic defect
- random phason strain as low as 0.0054 measured in Al₇₂.₇Ni₈.₅Co₁₈.₈

Taken at face value, that is difficult to reconcile with "golden is the least
resilient family."

## Why this is not yet a refutation — and what would make it one

**Coverage.** Al–Ni–Co / Al–Cu–Co decagonal is *the* workhorse two-dimensional
quasicrystal. There is no octagonal single crystal of comparable quality on which to
attempt these experiments, and the twelve-fold record is split across alloys,
fullerene monolayers, block-copolymer micelles and colloids. "Golden has the most
repair evidence" is close to "golden has the most evidence."

**Different quantity.** We measure *immediate* address readability under static
perpendicular-space jitter. The experiments measure *kinetic recovery*. High phason
stiffness and rapid phason healing are not synonyms — a system can be stiff but
kinetically frozen, or soft but highly mobile and fast to repair. These need not be
monotonically related, so the two records are not yet in contact.

**The publication-bias defence is available once.** It makes a prediction: if matched
8- and 12-fold repair experiments are performed and golden still wins on repair, the
resilience reading is wrong. The address-readability result could still stand, being
a different measured quantity, but the paper must not be written so that no
experimental outcome could embarrass it.

## What we gained

**A calibration anchor.** Real octagonal quasicrystals carry ~5% local tiling error.
Our damage axis is flipped-vertex fraction, and headline numbers are quoted at 10%.
These are not the same quantity — the survey is explicit that local defect percentages
have no simple universal conversion to a continuum phason strain tensor — but it is
the first time our x-axis has come within sight of a measured number.

**Language discipline for the paper.** "Address fragility" is not "resilience," and
the paper should say so where a reader might slide between them. §4 already carries
the caveat that disorder amplitude is generator-specific and uncalibrated; the survey
picked that up and treated it as decisive, which is the correct reading and a sign the
correction section is doing its job.

**A named next experiment.** The survey specifies the missing measurement: matched
specimens, one perturbation class at a time (mechanical loading along an aperiodic
axis, calibrated irradiation dose, thermal step, obstacle-mediated growth), phason
strain quantified in perpendicular-space diffraction coordinates before, immediately
after and during relaxation, with residual strain analysed against *measured* damage
rather than nominal amplitude — the same discipline we adopted computationally. It
also flags the 2025 field-controlled dodecagonal colloid as the most tractable
near-term platform, since every particle is trackable and chemistry is nearly
eliminated.

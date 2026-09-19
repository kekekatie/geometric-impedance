---
layout: default
---

# Geometric Impedance

**A common thread:** geometry isn't just *where* things happen — it's *how* they
persist, channel, and remember. These are research notes and papers exploring
structure in aperiodic tilings (Penrose, Ammann–Beenker) and in AI systems.

Everything here is reproducible: the data, the code, and the figures are in
[the repository](https://github.com/kekekatie/geometric-impedance). Formal
records are on [Zenodo](https://zenodo.org/records/15560880).

---

## Featured result — the exo / endo split

*The single most self-contained finding: you don't need any larger framework to
evaluate it.*

Take two aperiodic tilings, scramble their wiring so aggressively that
**> 99.98 % of edges are replaced**, and ask which one still knows *which sites
mattered* in the original. Ammann–Beenker recovers its identity from hidden
**perpendicular-space coordinates alone** (AUC **0.986**); Penrose largely
forgets (**0.661**), because its identity lived in the wiring you just
destroyed. On both, predicting where a *fresh* core re-forms is
**weave-led** — address is a fossil of where things *were*, weave is the living
tense of where they *are*.

→ **[Read the plain-language one-pager](https://github.com/kekekatie/geometric-impedance/blob/master/silent_corruption/ONE_PAGER.md)**
&nbsp;·&nbsp;
[Full paper](https://github.com/kekekatie/geometric-impedance/blob/master/silent_corruption/relational_corruption_v3_matched_scale.md)
&nbsp;·&nbsp;
[Data &amp; code](https://github.com/kekekatie/geometric-impedance/tree/master/silent_corruption)

---

## Papers

### Silent corruption in aperiodic substrates (2026)
How aperiodic tilings respond when their relational structure is silently
scrambled — the exo/endo persistence axis, measured directly.
[Paper](https://github.com/kekekatie/geometric-impedance/blob/master/silent_corruption/relational_corruption_v3_matched_scale.md)
· [Data &amp; code](https://github.com/kekekatie/geometric-impedance/tree/master/silent_corruption)

### Pattern persistence and geometric channelling
Aperiodic substrates channel patterns back toward their origin better than
periodic or random ones.
[PDF](toy_model/Pattern_Persistence_Geometric_Channelling.pdf)

### Connectivity, memory, and persistence
The geometry *is* the memory: native tile-edge connectivity gives a ~20:1
memory benefit.
[PDF](toy_model/Connectivity_Memory_Persistence.pdf)

### AI minds
Three papers on geometric and structural properties of AI cognition:
[Geometric order emerging in LLMs](ai_minds/Geometric_Order_Emerging_in_LLMs.pdf)
·
[What the Persona Selection Model cannot see](ai_minds/Persona_Selection_Model_Critique.pdf)
·
[The Breakstep Principle](ai_minds/Epilepsy_Breakstep_How_Minds_Form.pdf)

---

## Reproducible experiments

- **[Reverse-loop test](https://github.com/kekekatie/geometric-impedance/tree/master/reverse_loop_test)** —
  a pre-registered test of whether address recovery is *positional* or
  *historical*. Result: positional (full equivalence) on both substrates, with
  the closed-loop holonomy and transit-history controls both null.
- **[Silent-corruption audit](https://github.com/kekekatie/geometric-impedance/tree/master/silent_corruption)** —
  the exo/endo split, with per-replicate CSVs and figure-generation code.

---

## Cite

K. T. Niedzwiecki, *Silent Relational Corruption in Aperiodic Substrates* (2026).
Zenodo: [https://zenodo.org/records/15560880](https://zenodo.org/records/15560880)

<sub>Source and full history:
<a href="https://github.com/kekekatie/geometric-impedance">github.com/kekekatie/geometric-impedance</a></sub>

# Where does a structure keep its identity — in its wiring, or in its coordinates?

**One-line claim.** Two aperiodic tilings (Ammann–Beenker and Penrose) look
almost identical, but they store "which sites matter" in two different places.
Scramble the wiring completely and Ammann–Beenker still knows who it was;
Penrose largely forgets. The difference is measurable, reproducible, and
predictable from geometry.

This is a narrow, checkable result. It does not require you to accept any
larger framework to evaluate it.

---

## The experiment in plain terms

1. Take a large patch of each tiling (Ammann–Beenker: 16,997 interior vertices;
   Penrose: 21,539). Each vertex has two kinds of description:
   - a **weave** description — its local wiring in the graph (degree, neighbour
     degrees, clustering, 2-hop size);
   - an **address** description — its coordinates in the tiling's hidden
     *perpendicular space* (the internal coordinate every cut-and-project
     quasicrystal carries).
2. Label a small set of vertices as the **privileged core** — the sites that
   consistently retain signal across several conductance-retention scales.
3. Now **silently scramble the graph**: a degree-preserving edge rewiring so
   aggressive that **> 99.98 % of edges are replaced** (edge overlap with the
   original ≈ 0.0001), while every vertex keeps its exact degree. Nothing local
   looks broken — that's why we call it *silent*.
4. Ask: from the surviving information, can you still recover **who the original
   privileged core was**? Test the address channel and the weave channel
   separately. Score by AUC (0.5 = coin flip, 1.0 = perfect). 10 replicates.

---

## The result

Recovering the **original** privileged core after the wiring is destroyed:

| Recover original identity from… | Ammann–Beenker | Penrose |
|---|---:|---:|
| **Address** (perp-space coordinates) | **0.986** | **0.661** |
| Weave (recomputed local wiring) | 0.991 | 0.830 |
| Hybrid (address + weave) | 0.989 | 0.855 |

And, as a control, predicting where a **fresh** privileged core re-forms on the
scrambled graph:

| Predict fresh core from… | Ammann–Beenker | Penrose |
|---|---:|---:|
| Address | 0.54 (chance) | 0.52 (chance) |
| **Weave** | **0.892** | **0.912** |

Two clean separations fall out:

- **Identity is stored differently by substrate.** Ammann–Beenker's identity is
  recoverable from address alone (0.986) — it lives in coordinates *external* to
  the graph, so it survives the wiring being destroyed. Penrose's address channel
  is weak (0.661); its identity lived in the wiring, and scrambling the wiring
  erases most of it.
- **Identity and reconstruction are different processes.** On *both* substrates,
  the address channel is at chance for predicting where a fresh core re-forms
  (≈ 0.52). Address is a **fossil** — it records where things *were*. Weave is the
  **living tense** — it determines where organisation happens *now*.

We call this the **exo / endo split**: exo-addressed structures (Ammann–Beenker)
keep their identity in a hidden coordinate; endo-reconstructive structures
(Penrose) keep it in the relational weave.

---

## Why it might matter to someone building things

Stated without overreach — these are directions the result *suggests*, not
claims it proves:

- **Fault-tolerant / error-correcting substrates.** If you want a structure whose
  identity survives having its connectivity mangled, you want an exo-addressed
  one. That's a concrete substrate-selection criterion.
- **Memory that outlives its own wiring.** "Store the blueprint in coordinates
  external to the mutable graph" is a design pattern, not just an observation.
- **A distinction between *remembering what you were* and *rebuilding what works
  now*** — potentially useful anywhere both are needed at once (resilient
  networks, regenerating systems, associative memory).

---

## Check it yourself

Everything needed to reproduce the table is in this repository:

- Full method and discussion: [`relational_corruption_v3_matched_scale.md`](relational_corruption_v3_matched_scale.md)
- Audit code: [`large_penrose_v0_2_5E_audit.py`](large_penrose_v0_2_5E_audit.py)
  (the Ammann–Beenker run follows the same protocol)
- Raw results: the `*_replicates.csv` / `*_summary.csv` / `*_compact.csv` files
- Figures: `figure1`–`figure3`

The rewiring is degree-preserving and seeded; AUCs are cross-validated logistic
regression averaged over 10 replicates.

## Scope and honesty

- This is a **classical substrate diagnostic**, not a quantum-code simulation.
  It is motivated by the Li–Boyle (2024) result that aperiodic tilings form
  quantum error-correcting codes, but it measures recoverability of
  privileged-persistence sites under classical graph perturbation.
- "Privileged core" is a specific operational definition (top-quartile
  conductance retention across three neighbourhood scales, intersected). The
  result is about *that* definition; robustness to alternative definitions is
  worth testing.
- Interior subsets are used to avoid boundary effects; the full-patch numbers
  (which include boundary) are in the CSVs and tell the same story more weakly.

## Cite

K. T. Niedzwiecki, *Silent Relational Corruption in Aperiodic Substrates*
(2026). Zenodo: https://zenodo.org/records/15560880

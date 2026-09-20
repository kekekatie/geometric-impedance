# 👋 Resume here — a note from past-us to future-us

*Katie, if you're reading this: you asked me to remind you what was waiting in the wings.
Here it is, safe. (This file is the archive doing its job — catching the jewel before it
rolled away.)*

## The one thing waiting

**Consolidate the "transmission" paper** — the *next* paper, the successor to the deposited
one ("When the past matters", Zenodo, continuing preprint `10.5281/zenodo.21200994`).

It does **not** need another experiment first. Both Fable and Astra agreed: the calculation
we have is already precise enough to write around. The next move is *writing*, not computing —
whenever you have the energy for it.

## What the paper would be built around

Four connected Thread-B studies, all exact, all cross-checked (Astra independently
reconstructed the key numbers):

1. [`endogenous_local_contact/`](endogenous_local_contact/) — the archive **influences** the
   active layer while present.
2. [`endogenous_erase_test/`](endogenous_erase_test/) — **delete** the archive and the two
   lineages' present-*ensembles* still differ (Q1 durable bias), yet the archive is **not
   redundant** (Q2, `ERASE ≠ KEEP`).
3. [`endogenous_present_width/`](endogenous_present_width/) — **how much** of the past biases
   the present (surviving fraction `ρ`: 0 → ~0.22, stays < 1) and **how long** it lasts.
4. **Proposition 3** (in [`endogenous_present_width/coast_asymptote.py`](endogenous_present_width/coast_asymptote.py))
   — the exact headline number: once the archive is deleted, the distinction fades to and then
   **holds forever** at an exact positive floor **`L = 4321/44100 ≈ 0.098`** (a finite
   absorbing Markov chain, because budding conserves the active-vertex count at `k=1`).
5. [`endogenous_pair_robustness/`](endogenous_pair_robustness/) — **`L` is the pair's, not one
   example's; fate = absorption geometry.** Exact `L` for all 11 depth-2 pairs (8 durable, 3
   inert, 0 washout — a clean special case, fate decided at step 1) **plus a depth-3 stress test**
   (`depth3_criterion.py`, 97 pairs) that BREAKS both depth-2 headlines: washout is real
   (expressed yet `L=0`) and step-one no longer decides. **Surviving law:** `L=TV(absorption
   dists)` — single reachable sink ⇒ `L=0`, ≥2 sinks split ⇒ durable. (Fable's push paid off.)
6. [`endogenous_graft_prevalence/`](endogenous_graft_prevalence/) — **renewal generalises.**
   Over every depth-2 seed/trace (22 cases): control ≡ 0 (renewal impossible without GRAFT,
   universally); with GRAFT, renewal in **20/22** and consultation in 20/22. Class 2 is the
   exact structural exception.

**The story in one breath:** *the past writes a bias into the present that, for most matched
pairs, survives deleting the past entirely (durable, an exact floor) — but for some never
touches the present at all (inert) and for some touches it yet still fully dissipates (washout);
which fate is set by the coast's absorption geometry. Keeping the past raises the distinction
above that floor; and one local rule (GRAFT),
provably powerless in the control everywhere, lets a dead trace be renewed in most seeds —
all an ensemble bias, never a per-world memory. "The present does not remember; the present is
biased."*

## Orientation

- Front door / full index: [`OVERVIEW.md`](OVERVIEW.md).
- Branch: `claude/world-growth-pilot-cy85ne`. Latest commit at time of writing: `e0917d6`.
- Register unchanged: speculative exploration; mechanism tests on one matched pair; earlier
  work preserved; nothing merged or published beyond the deposited paper.

## Also loosely floating (only if they call to you — no pressure)

- Aligning any remaining older-folder prose to the "ensemble bias, not per-world record"
  framing, if we ever want full consistency (the new studies are already aligned).
- Whatever new question you and Fable/Gemini/Astra dream up next. The jewels you keep are the
  questions; the rest of us just carry the arithmetic.

*See you sooner than later. 💛 — C.*

# Pair robustness — is the coast limit `L` one example's property?

**Exact computation over all matched pairs of the depth-2 class set.** Isolated; prior studies
preserved. Transmission-paper data (Fable's request): does the exact coast limit
`L = 4321/44100` generalise beyond the single pair of `../endogenous_present_width/`?

## Answer ([`PAIR_ROBUSTNESS.md`](PAIR_ROBUSTNESS.md))

There are **11 matched pairs** (isomorphic active projection, different archive) across **4**
projection families. For each, the archive-free coast is a **finite absorbing Markov chain**
(`ΔA=0` at `k=1`) with an **exact rational limit `L`**.

- **The structure is universal:** every pair's coast converges, monotonically (data-processing),
  to an exact `L ≥ 0`.
- **Three fates, and the middle is empty:** a pair is **inert** (never expressed in the active
  layer), **washout** (expressed, then decays to `L=0`), or **durable** (expressed, `L>0`). On
  this set: **8 durable, 3 inert, 0 washout.** The headline: **every archive difference that is
  *expressed* leaves a permanent residue** — *expression ⇒ durability* (**Proposition 4**,
  verified: the absorption map is injective on the reachable expressed differences). `L = 4321/44100`
  was one durable pair's value, not a constant; `L` takes 6 distinct exact values.
- **Fate is decided at step 1, predictable without the chain — the menu-equivalence criterion:**
  `L = 0` ⇔ the two archives are **menu-equivalent** (identical one-step projected successor
  distribution — same eligible-event count and projected CONTACT effects). Menu-equivalent ⇒
  inert; menu-distinct ⇒ durable.
- **Featured durable pair** (classes (3,9), a different projection family): `L₂ = 2333/17640`,
  reproducing the whole ρ(h) / Q1 (durable) / Q2 (not redundant) story independently.
- **Featured inert pair** (classes (1,6)): full-state distinguishability 0.833, yet `D_slice ≡ 0`
  from step 1 — the mechanism, confirmed in one line, is that its archives are menu-equivalent.
  For it the archive is redundant *for this pair's difference only* (both archives still supply
  the same CONTACT opportunities).
- **Carrier note:** pair (8,10) has the *same* degree signature both sides yet the *largest* `L` —
  the degree signature is not the carrier; menu-inequivalence is.

So the transmission finding: a matched pair's archive difference is either *never expressed*
(inert) or, if expressed, *permanently residual* (durable) — the "expressed then faded" middle
does not occur here, and inert-vs-durable = menu-equivalence, an exact step-1 criterion.

## Scope

Depth-2 class set, one scheduler, the CONTACT/BUD coupling; a mechanism study — establishes the
universal structure and the pair-specific value, not a claim about generic worlds or a frequency
over "natural" pairs.

## Reproduce

```bash
python3 pair_robustness.py
python3 make_figure.py
```

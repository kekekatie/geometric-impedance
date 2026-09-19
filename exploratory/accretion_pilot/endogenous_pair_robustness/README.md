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
- **The value is the pair's:** `L` takes **6 distinct exact values** — **8/11 pairs are durable**
  (`L > 0`; the archive leaves a lasting ensemble bias, archive not redundant) and **3/11 are
  washout** (`L = 0`; the archive difference is *purely archival* — never expressed in the active
  layer, so the archive is redundant to the active future). `L = 4321/44100` was one durable
  pair's value, not a constant.
- **Featured second pair** (classes (3,9), a different projection family): `L₂ = 2333/17640`,
  reproducing the whole ρ(h) / Q1 (durable) / Q2 (not redundant) story independently.
- **Featured washout pair** (classes (1,6)): full-state distinguishability 0.833, yet coast ≡ 0
  and KEEP ≡ 0 — the difference lives only in the archive.

So the transmission finding is a **dichotomy**: a matched pair's archive difference is either
*transcribed* into the active present (durable) or *confined* to the archive (washout), and which
is an exact, computable property of the pair.

## Scope

Depth-2 class set, one scheduler, the CONTACT/BUD coupling; a mechanism study — establishes the
universal structure and the pair-specific value, not a claim about generic worlds or a frequency
over "natural" pairs.

## Reproduce

```bash
python3 pair_robustness.py
python3 make_figure.py
```

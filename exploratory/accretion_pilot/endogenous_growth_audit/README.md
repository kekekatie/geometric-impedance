# Endogenous-growth audit — repairs to the M1 proposal

**Proofs, counterexamples, and tiny exact enumeration only. No stochastic sweep, no
production experiment.** Repairs `../endogenous_growth_design/` per Astra's review; the
original is preserved with a dated correction appended pointing here. M1 (Competitive
Accretion Grammar) is **retained as a candidate**, corrected.

See [`AUDIT.md`](AUDIT.md) for the full corrected rules, the analytic-vs-bounded split, the
five confluence notions, the withdrawals, and the successor table.

## What changed (headline)

- **Frontier arithmetic:** proved `ΔB = k − d_A(y)`; for k≥1 every successor has `B ≥ k`,
  so **rewriting never deadlocks**. At **k=1** `B` is nonincreasing but never 0 and `|V|`
  grows every event → **"stalls / extinction" WITHDRAWN**. For **k≥2**, a star schedule
  keeps `B = k` while size, active vertices, and active components all grow (**more
  vertices ≠ more bonds**). **k=0 has ΔE=0**, not k+1 (invariants stated separately).
- **Confluence:** one-step non-joinability does **not** prove non-confluence. Now reported
  as a **finite-depth** result (competing-pair descendants stay disjoint to depth D=3) plus
  a **Q-immutability** invariant (once quiet, a vertex is frozen); **global non-confluence
  left open**. The five notions — commuting independent events / different event choices /
  reordering a fixed collection / confluence / distinguishability at equal event count —
  are separated. The universal "memory needs destructive competition + broken symmetry" is
  **WITHDRAWN**.
- **M2 is not a forgetful null:** three sprouts reach a star **or** a path (non-isomorphic,
  equal size) — **WITHDRAWN**; M2 confluence kept as a separate open question.
- **Exactness:** WL hashes only bucket; every bucket resolved by exact state-preserving
  isomorphism. Checks use `assert` + **nonzero exit** (printed text is not a gate).
- **Retained positive result:** depth-2 from `path(4)`, k=1 → **exactly 11 classes**; P and
  R land in different classes with **different available continuations** (successor table).

## Reproduce

```bash
python3 audit_checks.py   # exact; exits nonzero on any failed assertion. Currently: exit 0.
```

# Zero-net-pairing: are the zero-net-cost omission flips structurally matched?

**Frozen before any flip list is examined.** Branch `experiment/zero-net-pairing-2026-11-24`,
cut from `1922a7b` (the sealed local-witness-omission result). No sealed experiment file is
modified; the corrected decoder and omission engine are imported unchanged from
`exploratory/fresh_site_address_audit_2026-11-20/audit.py` and
`exploratory/local_witness_omission_2026-11-20/`.

## The question

Omitting a single incident **endpoint (X) check** from the archive query of a frozen loss
site flips many individual decoded labels while moving the **aggregate** tie-aware truth
credit by zero (or nearly zero): the weighted credit **lost** equals the weighted credit
**gained**. Committed examples (local-witness-omission `HANDBACK.md`):

- **Penrose_2 (e4): X5** — 44 label flips (+2 tie-status changes), lost = gained =
  `0.00020747` pp, **net 0.00000000 pp**.
- **Penrose_2 (e4): X0** — 18 label flips (+2 ties), lost = gained = `0.00008760` pp, net 0.
- **Penrose_1 (e14): X4 / X6** — 570 / 572 label flips (+12 ties), lost = gained =
  `0.02107022` / (its X6 counterpart) pp, net `+0.00001844` pp (small, not exactly zero).

Is the zero (or near-zero) **structural** — does every credit-losing history pair one-to-one
with a credit-gaining history of equal probability weight under a genuine symmetry — or a
numerical coincidence?

## Definitions (fixed)

At a fixed site (loss qubit `q`, 385,648 histories = exhaustive ≤2 ordinary faults × 8
onset/erasure variants, bounded `(3,3)` decoder, `p = 1e-3`, scored Z-logical observable,
tie-aware credit with ½ on a `1e-12` tie), for an omitted check `c`:

- **intact** decision = the diamond query on all four incident checks (`D.star`).
- **omitted** decision = the diamond query on the retained three checks
  (`D.star \ {c}`); the two withheld readings stay **absent**, never zeroed.
- A **flip** = a history where `label(omitted) ≠ label(intact)`.
- **credit delta** `δ = cred(omitted, truth) − cred(intact, truth)` ∈ {−1, −½, +½, +1}
  (tie-aware). **Lost** histories have `δ < 0`, **gained** have `δ > 0`. (A pure
  tie-status change with the same hard label contributes `δ = ±½` and is included.)
- **probability weight** `w = odds^k`, `odds = p/(1−p)`, `k` = number of ordinary faults.

## Candidate symmetries (frozen list)

A **pairing** is an involution/bijection σ on the 385,648 histories of the site. The
candidates, each a concrete map on `(ordinary-fault configuration, onset round, erasure
free-value (v_x, v_z))`:

- **(a) Erasure free-value swap** — permute `(v_x, v_z)` within a fixed scheme (e.g.
  `(v_x,v_z) ↦ (1−v_x, v_z)`, `(v_x,1−v_z)`, `(1−v_x,1−v_z)`), ordinary faults and onset
  fixed.
- **(b) Onset swap** — `onset 1 ↔ 2`, ordinary faults and free values fixed.
- **(c) Patch-graph automorphism fixing e4** — a permutation of data qubits / checks that
  preserves the `HX`/`HZ` incidence, **fixes the loss edge `e4`**, and maps the incident
  check set to itself; applied to the ordinary-fault support (and, as needed, onset/free
  value).
- **(d) Stabilizer / logical coset shift** — add a fixed stabilizer generator or a logical
  operator to the ordinary-fault configuration (mod 2), onset/free value fixed or jointly
  mapped.

Combinations of the above (e.g. an automorphism **and** a free-value swap) are permitted and
reported as such.

## Pairing criterion (frozen)

For an omitted check `c`, a candidate σ **explains the zero** iff σ is a bijection that maps
the **lost** set of `c`-flips onto the **gained** set, with, for every lost history `h`:
`w(σh) = w(h)` and `δ(σh) = −δ(h)`. Necessary first screen (**weight-matched**, step 4):
the multiset `{(w, −δ)}` over lost histories equals the multiset `{(w, δ)}` over gained
histories. If no single candidate (or disclosed combination) realizes an exact such
bijection, the verdict is **"no pairing found"**; the residue (unpaired flips) is reported.

For the Penrose_1 X4/X6 case, where the net is small but nonzero, the same machinery reports
how much of the movement is weight-matched and whether a candidate σ pairs the matched part,
leaving the unmatched residue (which carries the `+0.00001844` pp) explicit.

## Procedure

1. Commit this protocol (done here) before examining any flip list.
2. Reproduce the committed **X5** and **X0** rows of Penrose_2 **exactly** (flip counts, tie
   counts, lost/gained credit) with the imported engine. **Stop and report** on any mismatch.
3. For every flip of each studied check record: the ordinary-fault configuration, onset
   round, erasure free-value `(v_x, v_z)`, weight `w`, intact & omitted labels and posteriors,
   true outcome, and the direction (right→wrong / wrong→right, and the tie-aware `δ`).
4. Compare the lost and gained sets: do their `(w, |δ|)` multisets match exactly?
5. Test the candidate symmetries (a)–(d) and disclosed combinations; report which, if any,
   maps every lost history to a gained one of equal weight and opposite `δ`.
6. Repeat for X0 (Penrose_2) and X4 / X6 (Penrose_1).
7. `HANDBACK.md`: a plain-language paragraph for Katie, then one table per check (flips,
   weight-matched yes/no, pairing found, unpaired residue), and a one-line verdict:
   *"structural pairing explains the zero"* or *"no pairing found"*.

## Scope

Bounded `(3,3)` decoder, `k ≤ 2`, `p = 0.001`, the frozen sites **Penrose_2 (e4)** and
**Penrose_1 (e14)** only. This studies the structure of the already-measured zero/near-zero
net costs; it introduces no new decoder, site, or scoring rule.

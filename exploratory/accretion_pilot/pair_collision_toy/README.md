# Pair-collision toy — when two bonds share one quiet neighbour

**Two exact results, one certified interval, one lemma.** This folder is isolated from the rest of
the pilot, and prior studies are untouched. The rule set is the transmission paper's: **BUD at
`k=1` plus CONTACT**, with **uniform selection over all eligible events**, exactly as in
[`../endogenous_local_contact/`](../endogenous_local_contact/). The script imports that folder's
reference implementation and cross-checks the model against it.

**Start state.** Two active bonds `a–b` and `c–d`, plus **one quiet vertex `q` adjacent to `a` and
`c` only.** **Frozen** means no CONTACT is eligible *and* the active projection is a matching.

## Results

| quantity | value | status |
|---|---|---|
| **Task 1.** P(CONTACT ever fires) | **`1/3`** | exact (first-step identity plus brute force `t ≤ 6`) |
| **Task 2.** P(frozen end = one pair + two loners) | **`0.123896379462952 ≤ P ≤ 0.123896379462967`** | certified interval, width `1.5·10⁻¹⁴` |
| … conditional on the collision | `0.371689138388855 … 0.371689138388901` | `= 3 × the above` |
| is it `1/8`? | **no.** Already at `K=4` the certified upper bound is `0.124044 < 0.125` | certified |
| **Task 3.** BUD-only recurrent classes | singleton matchings, for every seed on `n ≤ 6` (208 classes) | proof sketch plus exhaustive check |

Exact endpoints (from [`results/pair_collision_report.txt`](results/pair_collision_report.txt)):

```
139494922095475785461194073181 / 1125899906842624000000000000000
  ≤  P(one pair + two loners)  ≤
139494922095492808288805926819 / 1125899906842624000000000000000
```

The only frozen end states are **one pair + two loners** (`B=1`) or **two pairs** (`B=2`). `B`
never reaches 0, because every BUD leaves the keeper–tip edge. So P(two pairs) = 1 − P above.

## Task 1: P(CONTACT ever fires) = 1/3

The start state has **5 eligible events**, all asserted:

- **1 CONTACT**, `CONTACT(a,q,c)`: the collision.
- **2 kill events**, `BUD(b,a)` and `BUD(d,c)`. These make `a` or `c` quiet, which leaves `q` with
  one active neighbour, so its menu is empty. By menu monotonicity it stays empty forever. The
  result is already frozen: two pairs, with no CONTACT ever eligible again, because BUD on a
  matching edge deposits a vertex whose menu is `{keeper, tip}`, an adjacent pair.
- **2 neutral events**, `BUD(a,b)` and `BUD(c,d)`. The depositor's own menu is `{keeper, tip}`,
  which is adjacent, so it is empty. `q` still sees `a` and `c`, and the reduced state returns
  exactly to the start.

So `p = 1/5 + (2/5)·p`, which gives **`p = 1/3`**. Brute-force enumeration on the full labelled
graph gives `P(collision by t) = (1/3)(1 − (2/5)^t)` exactly for `t = 1..6`
(`1/5, 7/25, 39/125, 203/625, 1031/3125, 5187/15625`).

## Task 2: the reduction, and why exactness stops at an interval

**Menu monotonicity** (proved in [`../endogenous_contact_timing/`](../endogenous_contact_timing/);
re-asserted here on every enumerated transition). A quiet vertex never gains a neighbour. Its
active neighbours can only leave, and an A–A edge between surviving actives is never removed. So
its menu only shrinks, and once it is empty the vertex can be **pruned** without changing any
future event count. Together with `ΔA = 0`, which gives exactly 4 actives forever:

> **Reduced state** = (active graph on the 4 actives, multiset of the active-neighbour sets `S` of
> the quiets whose menu is nonempty), canonical under the 24 relabellings.
> Eligible events = `2B + Σ |menu(S)|`.

This is **verified, not just argued**:

- The reduced chain's distribution over reduced states equals the brute-force full-graph
  distribution **exactly for `t = 0..5`**, which is 798 labelled states at `t=5`.
- Every full state's event count matches `2B + Σ|menu|`.
- The full-graph model reproduces the reference rule set of `../endogenous_local_contact/`, with
  the same event counts and the same successor multisets up to labelled isomorphism.

**The reduced chain is still infinite.** The brief's warning survives pruning. Copies of the same
`S` pile up. For example, one reachable state has 9 quiets all bridging the same pair `{0,2}`,
and each copy is a separate CONTACT event, so the counts change the rates. The maximum number of
kept quiets grows about linearly with depth (20 by depth 40), and the chain has cycles, including
a strongly connected component of more than 1,200 states at `K=6`. I found no finite lumping that
preserves the rates. So the answer is an infinite sum of rational terms, and I have **not** shown
it is rational. The table below gives what *is* certain.

**Truncation plus certificates.** Truncate at `K` kept quiets and give every boundary state
(more than `K` kept quiets) the value **0** for a lower bound and **1** for an upper bound. The
gap `hi − lo` is then exactly P(the process ever holds more than `K` menu-bearing quiets), which
falls roughly 30× per unit of `K`. Since it tends to 0, the process freezes almost surely. Each
bound is certified in **exact rationals**:

1. The script checks that every transient state can reach a frozen or boundary state. That makes
   `I−P` a nonsingular M-matrix, so `(I−P)⁻¹ ≥ 0`.
2. It then checks row by row, in exact `Fraction` arithmetic, that `(I−P)ℓ ≤ b₀` and
   `(I−P)u ≥ b₁`. That gives `ℓ ≤ P_true ≤ u`.

Floats only *propose* `ℓ` and `u`: the solve, nudged by a tiny multiple of the
expected-absorption-time vector. The exact check decides.

| K | states | certified lower | certified upper | width |
|---|---|---|---|---|
| 1 | 52 | 0.0154456 | 0.2250492 | 2.1e-01 |
| 2 | 153 | 0.0938285 | 0.1497355 | 5.6e-02 |
| 3 | 334 | 0.1212510 | 0.1265589 | 5.3e-03 |
| 4 | 612 | 0.1237656 | **0.1240442** | 2.8e-04 ← already excludes 1/8 |
| 6 | 1506 | 0.123896215 | 0.123896612 | 4.0e-07 |
| 8 | 2941 | 0.12389637931 | 0.12389637971 | 4.0e-10 |
| 10 | 5025 | 0.1238963794628 | 0.1238963794632 | 3.3e-13 |
| 12 | 7866 | 0.123896379462952 | 0.123896379462967 | 1.5e-14 |

The full table, with exact rational endpoints, is in
[`results/certified_intervals.txt`](results/certified_intervals.txt). At `K=12` the width is set
by the certificate slack, not by the truncation.

**If `P` is rational**, its denominator is at least **19,496,058**: the simplest rational in the
interval is `2415491/19496058`. That is not a claim that `P` is irrational. It only rules out
every "nice" closed form with a small denominator.

**Why the Monte Carlo said "≈ 0.1245, maybe 1/8".** An independent full-graph simulation, with no
reduction and no truncation ([`monte_carlo.py`](monte_carlo.py), 200k runs), gives
`0.12416 ± 0.00074`, `z = +0.36` against the certified value. At that sample size `1/8` sits only
about 1.1 SE away, so 200k runs cannot separate the two. It would take roughly 1.4M runs to do
that at 4σ. The collision frequency was `0.33267 ± 0.00105` (`z = −0.62` vs `1/3`).

## Task 3: lemma note

See [`BUD_RECURRENT_LEMMA.md`](BUD_RECURRENT_LEMMA.md). Under BUD-only at `k=1`, every recurrent
class of the coast chain is a **singleton**: a matching plus isolated vertices, absorbing, for
any seed. Sketch: `ΔB = 1 − d_A(y) ≤ 0`, so `B` is constant on a recurrent class. That forces
`d_A = 1` at every edge endpoint, so the state is a matching, and budding a matching edge
reproduces the matching. The check is exhaustive over **all 208 graphs with `n ≤ 6` vertices**.

## Scope

This is a mechanism toy: one start state and one rule set, where the weighting of BUD against
CONTACT is a modelling assumption, as in the transmission paper. Tasks 1 and 3 are exact. Task 2
is a certified interval with an explicit, checkable certificate, and it is **not** an exact
rational. Nothing here concerns physics or minds.

## Files

- [`pair_collision.py`](pair_collision.py): Tasks 1 and 2, the reduction checks, and the
  certificates. Exact; about 80 s; nonzero exit on any failed assert.
- [`monte_carlo.py`](monte_carlo.py): independent full-graph Monte Carlo gate. About 35 s for
  200k runs.
- [`bud_recurrent_lemma.py`](bud_recurrent_lemma.py): Task 3's exhaustive check. About 1 s.
- [`BUD_RECURRENT_LEMMA.md`](BUD_RECURRENT_LEMMA.md): the lemma note.
- `results/`: `pair_collision_report.txt`, `certified_intervals.txt`, `monte_carlo_report.txt`,
  `bud_recurrent_lemma_report.txt`.

## Reproduce

```bash
python3 pair_collision.py        # exit 0 iff all exact checks pass
python3 bud_recurrent_lemma.py   # exit 0 iff the lemma holds on all 208 graphs (n <= 6)
python3 monte_carlo.py           # optional: N=200000 seed=20260923; exit 0 iff within 4 SE
```

Requires `networkx`, `numpy`, `scipy`. The float solve only proposes the bounds; exact rational
checks certify them.

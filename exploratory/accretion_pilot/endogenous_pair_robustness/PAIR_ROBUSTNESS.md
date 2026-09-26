# Is the coast limit `L` one example's property, or the construction's? — and three fates

*Register: **speculative exploration**. Exact rational computation over **all** matched pairs of
the depth-2 class set; a mechanism study, not a sample of growing worlds. Isolated under
`exploratory/accretion_pilot/endogenous_pair_robustness/`; earlier work preserved; no merges,
publishing, sealed-study access. Results from [`pair_robustness.py`](pair_robustness.py)
(exit 0). Reuses the verified primitives of `../endogenous_present_width/`.*

**Fable's request (transmission-paper data).** The ERASE / ρ(h) / coast-asymptote analysis was
done on **one** matched pair. Was the exact coast limit `L = 4321/44100` a property of that one
example, or of the construction? Here we compute the **exact `L` for every matched pair** among
the 11 depth-2 classes, and — following Fable's sharper reading — classify the **three logical
fates** and find which occur.

> **Ensemble, not record** (carried from `../endogenous_present_width/`): all "distinguishability"
> here is a statement about the **distribution over presents**, never a per-world memory. `L` is
> a bias in the ensemble.

## Setup

A **matched pair** = two depth-2 classes with **isomorphic active projections** but
**non-isomorphic full graphs** (same active layer, different archive). There are **11** such
pairs across **4** active-projection families. For each, `ΔA = 0` at `k=1`, so (Proposition 3 of
`../endogenous_present_width/`) the archive-free coast is a **finite absorbing Markov chain** on
4-active-vertex projections, converging to the exact rational `L = TV(absorption distributions)`.

"**Expression**" = the archive difference reaches the active layer at all, measured by
`D_slice(h)` = TV of the two lineages' erased-slice distributions at horizon `h` (nonzero ⇒
expressed).

## Result — `L` for every matched pair ([`results/L_table.txt`](results/L_table.txt))

| pair | proj family | archives (q-deg) | exact `L` | `L` (float) | fate |
|---|---|---|---|---|---|
| (0,1) | 91016ad6 | (3,3) vs (2,3) | `4321/44100` | 0.0980 | durable |
| (0,2) | 91016ad6 | (3,3) vs (3,3) | `7/50` | 0.1400 | durable |
| (0,6) | 91016ad6 | (3,3) vs (2,4) | `4321/44100` | 0.0980 | durable |
| (1,2) | 91016ad6 | (2,3) vs (3,3) | `2099/8820` | 0.2380 | durable |
| **(1,6)** | 91016ad6 | (2,3) vs (2,4) | **`0`** | 0.0000 | **inert** |
| (2,6) | 91016ad6 | (3,3) vs (2,4) | `2099/8820` | 0.2380 | durable |
| **(3,4)** | a3bec69c | (2,3) vs (2,4) | **`0`** | 0.0000 | **inert** |
| **(3,9)** | a3bec69c | (2,3) vs (3,3) | `2333/17640` | 0.1323 | durable *(featured)* |
| (4,9) | a3bec69c | (2,4) vs (3,3) | `2333/17640` | 0.1323 | durable |
| **(5,7)** | 04fabdef | (2,3) vs (2,2) | **`0`** | 0.0000 | **inert** |
| (8,10) | 176ca6f6 | (3,4) vs (3,4) | `4/15` | 0.2667 | durable |

![pair robustness](figures/pair_robustness.png)

## The answer, in three parts

**1 — The structure is universal.** *Every* matched pair's archive-free coast is a finite
absorbing chain converging to an exact rational `L ≥ 0`, non-increasing (data-processing). A
property of the construction, not of one example.

**2 — Three logical fates, and the middle one is empty.** A matched pair could in principle be:

- **inert** — the archive difference is *never expressed* in the active layer (`D_slice(h) = 0`
  for all `h`);
- **washout** — expressed, and then the coast *decays* to `L = 0`;
- **durable** — expressed, and `L > 0`.

On the depth-2 set: **8 durable, 3 inert, and 0 washout.** The washout category is **empty** —
this is the headline. **Every archive difference that is expressed in the active layer at all
leaves a permanent residue.** Nothing that touches the present ever fully fades. (`L = 4321/44100`
was one durable pair's value; the original study happened to pick a durable pair.)

**"Expression ⇒ durability" — true at depth-2, but NOT a general theorem.** On the depth-2 set,
`coast[H] > 0 ⇔ L > 0` (no expressed difference decays to zero). *This is **depth-2-specific**:
at depth-3 it is **false** — there are pairs expressed in the active layer that decay to `L = 0`
(exact counterexamples in [`depth3_criterion.py`](depth3_criterion.py)). It was tempting to call
this "Proposition 4"; the honest status is a clean special case, superseded by the
absorption-geometry law below.*

**3 — The value (and the fate) is the pair's, and predictable at step 1.** `L` takes **6
distinct exact values**. And the fate is decided at the **first step**, without running the
chain:

> **Menu-equivalence criterion (exact on the depth-2 set): `L = 0` ⇔ the two archives are
> *menu-equivalent*** — they present the *same* one-step projected successor distribution
> (`D_slice(1) = 0`). Menu-equivalent ⇒ inert ⇒ `L = 0`; menu-distinct ⇒ durable ⇒ `L > 0`.

*This step-one criterion is also **depth-2-specific**. At depth-3 it breaks in **both**
directions (see [`depth3_criterion.py`](depth3_criterion.py)): a pair can be menu-equivalent at
step one and then **diverge** at step two (`D_slice(1)=0` but `D_slice(2)>0` — "same projected
menu" does not survive through time), and an `L=0` pair can already be **expressed** at step one
(`D_slice(1)>0`). So "fate decided at step one" is a clean depth-2 phenomenon, not a law.*

## Featured durable pair — classes (3,9), a different projection family

An independent matched pair (family `a3bec69c`, not the original's `91016ad6`; archives `(2,3)`
vs `(3,3)`), exact limit **`L₂ = 2333/17640 ≈ 0.1323`**. It reproduces the whole original story:
ρ(h) rises `0 → 0.20 → 0.26 → 0.28`; **Q1** the archive-free coast stays positive and converges
to `L₂ > 0` (durable bias); **Q2** `KEEP ≥ coast` at every tested step and differs after `H`
(deleting the archive changes the active future — archive not redundant). So the phenomenon is
not peculiar to the first pair or its family.

## Featured inert pair — classes (1,6): a *menu-equivalent* archive

Full-state distinguishability at `H=2` is large (**0.833** — the archives genuinely differ), yet
`D_slice` is **exactly 0 from the first step onward**: the difference is **never expressed** in
the active layer (nothing washes out — it was never present there). **Mechanism, confirmed in one
line:** the two archives are **menu-equivalent** — equal eligible-event count (6 = 6) and an
identical multiset of projected CONTACT successors — so the scheduler cannot tell the lineages
apart at the active level. That is *why* `L = 0`, exactly as the criterion predicts, without
running the chain.

**Scope of "redundant" for inert pairs.** For an inert pair the archive is redundant **for this
pair's difference only** — both archives still *supply* CONTACT opportunities to the active
layer; they just supply the *same* ones. The archive is not globally inert (cf.
`../endogenous_active_projection/`).

## A note on the carrier — pair (8,10)

Pair (8,10) has the **same** quiet-degree signature on both sides — `(3,4)` vs `(3,4)` — yet the
**largest** `L = 4/15`. So the crude degree signature is **not** the carrier of the difference;
menu-inequivalence is. Fate cannot be read off the archives' degree profile.

## The general law — `L = TV(absorption distributions)`, and the fork law ([`depth3_criterion.py`](depth3_criterion.py))

**(a) What always holds.** `L = TV(absorption distributions of the two lineages)` (Proposition 3,
generalised). So `L = 0` **iff** the two lineages' `H=2` slice distributions absorb identically —
fate is a property of the coast's **absorption geometry**, checked here on the depth-2 set (11
pairs) and the **depth-3** set (27 classes, **97 pairs**).

**(b) The fork law (the observed rule, stated with care).** Only one direction carries
information:

> **Among *expressed* pairs (`Δ ≠ 0` at `H=2`), `L > 0` iff the coast has ≥ 2 reachable
> absorbing classes ("sinks").** The *only-if* is trivial (you need two exits to split them, and
> a single sink forces both lineages to the same point mass, `L = 0` by definition). The *if* —
> that an expressed difference with two available exits **always splits them unequally** — is
> **verified on the enumerated set (0 violations across 75 expressed depth-3 pairs and the
> depth-2 durable pairs) but not proven.** *Open:* whether two reachable sinks can ever give
> identical absorption distributions (an expressed pair with ≥2 sinks and `L = 0`).

The *expressed* qualifier is essential: **15** unexpressed pairs (`Δ = 0`) have ≥2 sinks yet
`L = 0` (they absorb identically because their distributions were identical to begin with), so
"two sinks ⇒ `L>0`" is false without it.

> **In plain language: durability is a property of the future, not the past — the past can only
> leave a lasting mark where the coast forks.** Pair (22,26) is marked at step one, marked *more*
> at step two, and then drains to zero: a strong mark with no fork to hold it. Which fate a pair
> meets is a property of the **dynamics**, not of the history.

**(c) Remark — the tempting depth-2 shortcut.** At depth-2 the washout category is empty and
"fate is decided at step one" (`L=0 ⇔` archives menu-equivalent) holds exactly — a clean special
case. It does **not** generalise: at depth-3 both fail, with (22,25) (`D_slice(1)=0` yet
`D_slice(2)=17/120` — "same projected menu" does not survive relabelling through time) and (22,26)
(`L=0` with `D_slice(1)=1/6`) as exact counterexamples.

## Scope & limits

The depth-2 **and depth-3** class sets with one scheduler (uniform over individual events) and
the CONTACT/BUD coupling; a mechanism study. It establishes that the coast-limit *structure* is universal, that
the *value* and the *fate* are pair-specific, that on this set the washout fate is empty
(expression ⇒ durability), and that fate = menu-(in)equivalence. **Not** a claim about generic or
larger worlds, nor a frequency estimate over "natural" pairs; Proposition 4's generality is open.

## Files

- [`pair_robustness.py`](pair_robustness.py) — exact `L` for all depth-2 matched pairs; the
  three-fate classification, the (depth-2) washout-empty finding and step-one criterion; featured
  durable pair (ρ(h), Q1, Q2); featured inert pair with the menu-equivalence mechanism; the
  (8,10) note; asserts + nonzero exit.
- [`depth3_criterion.py`](depth3_criterion.py) — the depth-3 stress test: exact counterexamples
  showing washout is non-empty and "fate decided at step one" breaks both ways beyond depth-2,
  and the surviving absorption-geometry law (single sink ⇒ `L=0`); asserts + nonzero exit.
- [`results/pair_robustness_report.txt`](results/pair_robustness_report.txt),
  [`results/L_table.txt`](results/L_table.txt),
  [`results/depth3_criterion_report.txt`](results/depth3_criterion_report.txt);
  [`figures/pair_robustness.png`](figures/pair_robustness.png).

## Reproduce

```bash
python3 pair_robustness.py    # depth-2: exact L, three fates, step-one criterion
python3 depth3_criterion.py   # depth-3: the criterion breaks; the absorption-geometry law
python3 make_figure.py        # writes the figure
```

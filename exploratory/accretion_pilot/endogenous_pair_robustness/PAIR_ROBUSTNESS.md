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

## Beyond depth-2 — the criteria break, and the surviving law ([`depth3_criterion.py`](depth3_criterion.py))

Fable asked us to push on "fate decided at step one" before writing it down. Extending to the
**depth-3** class set (27 classes, **97 matched pairs**) settles it: **both** depth-2 headline
statements are depth-2-specific.

- **Washout is non-empty at depth-3** (5 pairs): e.g. classes (22,26), `D_slice(1)=1/6`,
  `D_slice(2)=17/90` (expressed, even growing) yet `L=0`. *Expression does not imply durability.*
- **"Fate decided at step one" breaks both ways:** (22,25) has `D_slice(1)=0` but
  `D_slice(2)=17/120>0` (menu-equivalent at step one, then diverges — "same projected menu" does
  **not** survive relabelling through time, exactly Fable's subtlety); and (22,26) has `L=0` with
  `D_slice(1)=1/6>0`. The depth-2 equivalence `L=0 ⇔ D_slice(1)=0` fails in both directions.

**The law that survives (and is the real one).** `L = TV(absorption distributions)` always
(Proposition 3), so `L=0` **iff** the two lineages' `H=2` slice distributions absorb identically.
Fate is set by the coast's **absorption geometry**, not by step one:

| fate | expressed? | reachable absorbing classes | `L` |
|---|---|---|---|
| **inert** | no (`D_slice ≡ 0`) | any | 0 |
| **washout** | yes | **exactly 1** (single sink) | 0 |
| **durable** | yes | **≥ 2**, split differently | > 0 |

Exact on depth-3: **every** washout pair has a **single** reachable absorbing class (all mass
funnels to one sink, so absorption is constant and any expressed difference is annihilated), and
**every** durable pair has **≥ 2**. So the checkable predictor of `L=0` is not "menu-equivalent
at step one" but "**a single reachable sink** (inert or washout), or an expressed difference that
happens to split ≥2 sinks equally." The depth-2 set simply contained no single-sink *expressed*
pair, which is why washout looked empty and step-one looked decisive there.

Open direction: a general characterization of when the BUD-only projection coast has one versus
several reachable absorbing classes (that is what really decides durability).

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

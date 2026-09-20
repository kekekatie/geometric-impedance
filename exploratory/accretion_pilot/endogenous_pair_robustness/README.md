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
- **Three fates:** a pair is **inert** (never expressed in the active layer), **washout**
  (expressed, then decays to `L=0`), or **durable** (expressed, `L>0`). On the **depth-2** set:
  **8 durable, 3 inert, 0 washout** — a clean special case where every *expressed* difference is
  permanent and fate is decided at step one (`L=0` ⇔ archives *menu-equivalent*, i.e. identical
  one-step projected successor distribution). Featured durable pair (3,9): `L₂ = 2333/17640` in a
  different family; featured inert pair (1,6): `D_slice ≡ 0`, menu-equivalent; (8,10): same degree
  signature both sides yet the largest `L` (signature isn't the carrier).
- **But those two depth-2 headlines are depth-2-specific — they BREAK at depth-3**
  ([`depth3_criterion.py`](depth3_criterion.py), 97 matched pairs): washout is **non-empty**
  (expressed pairs with `L=0`, e.g. (22,26)), and "fate decided at step one" fails both ways
  (menu-equivalent-at-step-one pairs that later diverge; `L=0` pairs already expressed at step
  one). Fable was right to make us check before writing it as a theorem.
- **The surviving law — absorption geometry.** `L = TV(absorption distributions)` always
  (Proposition 3). Fate is set by the coast's sinks: a **single reachable absorbing class ⇒ L=0**
  (inert if unexpressed, washout if expressed — all mass funnels to one sink); **≥2 sinks split
  differently ⇒ durable (L>0)**. Exact on depth-3: every washout is single-sink, every durable
  has ≥2. This replaces the step-one criterion as the real predictor.

So the transmission finding: `L` and the fate are the pair's, governed by the coast's absorption
geometry; the depth-2 set is a clean special case (washout-free, step-one-decidable), and the
general picture — all three fates, single-sink washout — appears once the seeds run deeper.

## Scope

Depth-2 **and depth-3** class sets, one scheduler, the CONTACT/BUD coupling; a mechanism study —
establishes the universal structure (Prop 3), the pair-specific value/fate, and that the depth-2
criteria are a special case superseded by the absorption-geometry law. Not a claim about generic
worlds; a general characterization of the coast's sink count is the open direction.

## Reproduce

```bash
python3 pair_robustness.py
python3 depth3_criterion.py
python3 make_figure.py
```

# The width of "now" — how much of the past biases the present, and for how long

**Exact enumeration, one matched pair, a mechanism test.** Isolated; prior studies preserved.
Follows the ERASE test with a quantitative measure, motivated by Katie's picture: only the
present exists, carrying an inherited **momentum** from a past that need not still exist.

> **Ensemble, not record.** Every statement here is about the **distribution over presents**,
> never a single world: a given active graph is a class **both** lineages produce; what differs
> is only the probability distribution. The mark of the past is a **bias in the ensemble** (the
> status of AUC in Study A), never a per-world memory. *The present does not remember; the
> present is biased.*

## Questions

1. **How much biases the present?** Of all the history that distinguishes the two lineages, what
   fraction is legible from the **present alone** (active slice) vs the **full state**
   (active + archive)?
2. **Fade or set?** Imprint history, **delete the past**, and let the present coast — does the
   inherited bias decay or persist, and to what? That decay-to-a-limit is the temporal **width
   of "now"**.

## Answers (exact; [`PRESENT_WIDTH.md`](PRESENT_WIDTH.md))

Distinguishability = how well you could tell which lineage a sample came from (total-variation
distance; also in bits via mutual information). Matched pair: isomorphic active projections,
archives `(3,3)` vs `(2,3)`.

- **Part 1 — the present becomes biased.** The surviving fraction `ρ(h) = D_slice/D_full` climbs
  from **0** (at `h=0` the two lineages' presents are identically distributed — all the
  distinction is in the archive) to **~0.22** by `h=3`, staying **< 1**: CONTACT ferries a
  growing *but bounded* share of the past into a bias over present structure.
- **Part 2 — coast vs re-read, with an exact limit.** After the archive is deleted,
  distinguishability is **provably non-increasing** (a single fixed BUD-only kernel *on
  projections* — well-defined only by Proposition 1 — applied to both lineages ⇒ data-processing
  inequality). It **converges to an exact positive limit**, **`L = 4321/44100 ≈ 0.0980`**
  (**Proposition 3**: the coast is a finite absorbing Markov chain because `ΔA = 0` at `k=1`; the
  limit is the TV between the lineages' absorption distributions over the two absorbing
  projections). With the archive **kept**, distinguishability instead stays **≥ the coast at
  every tested step** (non-monotone: `0.147 → 0.151 → 0.151 → 0.147`) — keeping the past holds
  the distinction **above the floor over the tested interval** (the floor itself persists with
  no past). NULL (BUD-only) is exactly 0 throughout.

So the distribution over presents carries a genuine, permanently-biased imprint of history; the
amount is bounded, and once the past is deleted the bias **fades to — and then holds forever
at — an exact positive floor** (a distinction that survives with *no past at all*). Keeping and
re-reading the past maintains a **larger** distinction than the coast over the tested interval;
it does not "sustain" the bias (the floor is self-sustaining), it *raises* it.

## Scope

One matched pair, small horizons, a designed CONTACT coupling, uniform-over-events scheduler.
Mechanism test — shows the effects **can and do** occur, not that they are typical. (The
asymptote `L` itself is exact — Proposition 3 — not a within-horizon guess.)

## Reproduce

```bash
python3 present_width.py
python3 coast_asymptote.py
python3 make_figure.py
```

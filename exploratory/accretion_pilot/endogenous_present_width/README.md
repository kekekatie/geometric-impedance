# The width of "now" — how much of the past survives in the present, and for how long

**Exact enumeration, one matched pair, a mechanism test.** Isolated; prior studies preserved.
Follows the ERASE test with a quantitative measure, motivated by Katie's picture: only the
present exists, carrying an inherited **momentum** from a past that need not still exist.

## Questions

1. **How much survives?** Of all the history that distinguishes the two lineages, what
   fraction is legible from the **present alone** (active slice) vs the **full state**
   (active + archive)?
2. **Fade or set?** Imprint history, **delete the past**, and let the present coast — does the
   inherited momentum decay or persist? That decay profile is the temporal **width of "now"**.

## Answers (exact; [`PRESENT_WIDTH.md`](PRESENT_WIDTH.md))

Distinguishability = how well you can tell which lineage you are in (total-variation distance;
also in bits via mutual information). Matched pair: isomorphic active projections, archives
`(3,3)` vs `(2,3)`.

- **Part 1 — the present inherits the past.** The surviving fraction
  `ρ(h) = D_slice/D_full` climbs from **0** (at `h=0` the present carries *none* of the
  history — it is all in the archive) to **~0.22** by `h=3`, and stays **< 1**: CONTACT ferries
  a growing *but bounded* share of the past into present structure. Most of the past stays in
  the past.
- **Part 2 — coast vs re-read.** After the archive is deleted, distinguishability is
  **provably non-increasing** (data-processing inequality: one fixed law, applied to both
  lineages) — inherited momentum can **only fade or hold, never regrow**. Here it **relaxes
  toward a positive floor** (`0.147 → 0.117 → 0.105 → 0.100`, shrinking drops): a short
  forgetting onto a **permanent residue**. With the archive **kept**, distinguishability
  instead **holds and grows** — amplification requires **the past still existing to be
  re-read**. NULL (BUD-only) is exactly 0 throughout.

So the present carries a genuine, partly-permanent momentum of its history; the amount is
bounded, and only the present can spend it — replenishing or sharpening it needs the past.

## Scope

One matched pair, small horizons, a designed CONTACT coupling, uniform-over-events scheduler.
Mechanism test — shows the effects **can and do** occur, not that they are typical; the
"positive floor" is a within-horizon observation, not a proven asymptote.

## Reproduce

```bash
python3 present_width.py
python3 make_figure.py
```

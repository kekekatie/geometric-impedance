# The width of "now" — how much of the past survives in the present, and for how long

*Register: **speculative exploration**. Exact rational distributions on **one matched pair**
(the same one used in `../endogenous_local_contact/` and `../endogenous_erase_test/`); a
**mechanism test**, not a sample of growing worlds. Isolated; earlier work preserved; no
merges/publishing/sealed-study access. All results from
[`present_width.py`](present_width.py) (exit 0). Distributions are **exact rationals**; only
the bit-valued entropies are floating readouts of those exact numbers.*

**Katie's reframing.** Only the **present moment** actually exists; it rides a moving
expansion front and carries an inherited **momentum** from its history — the past itself need
not still exist. The [ERASE test](../endogenous_erase_test/) already showed the present keeps
a durable mark after the archive is deleted. This study makes that quantitative and asks the
two questions the reframing raises: **how much** of the past is carried in the present alone,
and **how wide** (how long-lived) is that present — does the inherited momentum **fade** or
**set**?

## The measure

The two lineages differ only in their archive (they start with **isomorphic active
projections**). "How well can you tell which lineage you are in?" is a clean, operational
measure of how much history is *legible*. We use, at each moment:

- **D_full** = total-variation distance between the two lineages' distributions over the
  **full state** (active + archive). This is *all* the historically-distinguishing
  information. (With a uniform prior over the two lineages, the best single-shot guess of the
  lineage succeeds with probability `½ + D_full/2`.)
- **D_slice** = the same distance over the **erased slice** (present only; quiet vertices
  deleted). This is the history legible **from the present alone**.
- **ρ(h) = D_slice / D_full ∈ [0, 1]** — the **surviving fraction**: what share of the
  distinguishing memory is readable without the archive.

We also give the information-theoretic version in **bits**: `I = ` Jensen–Shannon divergence
between the lineages `=` mutual information between the lineage label and the observation
(uniform prior). `I_full`, `I_slice`, and the bit-fraction `I_slice/I_full`.

## Part 1 — the present progressively inherits the past

Under extended dynamics (BUD + CONTACT), with no erasure, measured at imprint horizons
`h = 0…3` ([`results/present_width_tables.txt`](results/present_width_tables.txt)):

| h | D_full (TV) | D_slice (TV) | **ρ = slice/full** | I_full (bits) | I_slice (bits) |
|---|---|---|---|---|---|
| 0 | 1.0000 | 0.0000 | **0.0000** | 1.0000 | 0.0000 |
| 1 | 0.8000 | 0.1333 | **0.1667** | 0.7455 | 0.0165 |
| 2 | 0.7133 | 0.1470 | **0.2061** | 0.6236 | 0.0361 |
| 3 | 0.6784 | 0.1514 | **0.2232** | 0.5642 | 0.0287 |

- **At `h = 0` the present carries *none* of the history** (`ρ = 0`): the slices are
  identical, while the full state distinguishes the lineages with certainty (`D_full = 1`).
  **All** the memory starts in the archive.
- **As history accumulates, `ρ` rises** (0 → 0.17 → 0.21 → 0.22): each CONTACT writes a new
  active–active edge, transcribing a little of the archive into the **present** structure. The
  present is *inheriting the momentum of its past*.
- **`ρ` stays well below 1.** Even at `h = 3` the present alone carries only ~22% of the
  distinguishing information; the rest still lives **only in the archive**. (This is the
  quantitative form of the ERASE test's "archive not redundant.")
- **`D_slice ≤ D_full` always** — the present can never carry *more* memory than active +
  archive together (a sanity floor, asserted).

*(So `ρ(h)` also answers the "imprint-knob" question: imprinting a longer history sets a
somewhat stronger present-mark — `D_slice` rises with `h` — though with diminishing returns
over this horizon.)*

## Part 2 — fade or set, and the temporal width of "now"

Imprint history to `H = 2` events (archive present), then **delete the entire archive** and
let the present **coast** under archive-free dynamics (BUD only — with no quiet vertices,
CONTACT is inert). Compare against **KEEP** (archive retained, extended throughout):

| step | archive **deleted** (coast) | archive **kept** (KEEP) |
|---|---|---|
| 2 (delete here) | 0.1470 | 0.1470 |
| 3 | 0.1174 | 0.1514 |
| 4 | 0.1049 | 0.1506 |
| 5 | 0.1003 | 0.1467 |

![present width](figures/present_width.png)

- **Coasting can only fade or hold — never regrow (provable).** After deletion the present
  evolves under a **single fixed** BUD-only kernel applied to **both** lineages, so the
  **data-processing inequality** forces the distinguishability to be **non-increasing**:
  `0.147 → 0.117 → 0.105 → 0.100`. Inherited momentum cannot amplify itself once the past is
  gone. *(Asserted exactly, and guaranteed by the theorem, not just observed.)*
- **It relaxes toward a positive floor, not to zero.** The successive drops shrink
  (`−0.030, −0.012, −0.005`): within the reachable horizon the momentum **partially fades and
  then holds** — a *permanent residue* of the past remains in the present. So the "width of
  now" here is not a clean cutoff but a **short relaxation onto a lasting core**. *(Stated with
  the finite-horizon caveat: we observe convergence toward a positive value over `K = 3`
  steps; we do not claim the exact asymptote.)*
- **Regrowth requires the past.** With the archive **kept**, distinguishability does **not**
  decay — it holds and even ticks **up** (`0.147 → 0.151`), staying above the coast at every
  future step. Amplification of a historical difference is a property of **the past being
  re-read** (CONTACT), never of the present coasting alone. This is the sharp complement to
  the data-processing bound: the one thing that can push distinguishability up is exactly the
  thing erasure removes.
- **NULL control:** BUD-only throughout gives distinguishability `0` at every step — with no
  CONTACT there is no momentum to inherit, and erasure has nothing to reveal.

All distributions are exact rationals summing to 1; the coast curve is invariant under a
nontrivial relabelling (identities used for measurement/erasure only).

## Reading (plain language)

Put the two parts together and Katie's picture comes out sharp:

1. **The present is born forgetful and *earns* its memory.** History is not automatically in
   the "now" — it starts entirely in the (about-to-be-deleted) past, and only the CONTACT rule
   ferries a fraction of it into present structure. The present carries momentum **because a
   mechanism keeps transcribing the past into it**, not for free.
2. **Once the past is gone, the present can only spend its momentum, never mint more.** The
   inherited difference decays under coasting and settles onto a lasting floor; it can grow
   again **only** if the past is kept and re-read. So "how wide is now" has a real answer in
   this toy: the present has a **short forgetting time onto a permanent core**, and any
   *sharpening* of the past's imprint is the signature of the past still existing.

The honest one-line version: *in this model the present carries a genuine, permanent momentum
of its history — but the amount is bounded (ρ < 1, most of the past stays in the past), and it
can only be maintained or spent by the present alone; replenishing or amplifying it requires
the past to still exist.*

## Scope & limits

- One matched pair, small horizons (`h ≤ 3`, coast `K = 3`), one scheduler (uniform over
  individual events — a modelling choice), one designed CONTACT coupling. A mechanism test
  that these effects **can and do** occur, not a measurement of how typical they are, and not
  a large- or long-time claim. The "positive floor" is a within-horizon observation, not a
  proven asymptote.
- Distinguishability measures *how legible the lineage is*, not "the archive's content";
  `ρ < 1` means the lineages stay only partly separable from the present, consistent with —
  but not identical to — a full information-preservation statement.

## Files

- [`present_width.py`](present_width.py) — matched pair; full & slice iso-class distributions
  (exact, WL-bucketed); ρ(h) and bit-measures; the coast-vs-keep future with the
  data-processing non-increase, the regrowth contrast, the NULL control, normalisation and
  relabelling invariance. Asserts + nonzero exit.
- [`results/present_width_report.txt`](results/present_width_report.txt),
  [`results/present_width_tables.txt`](results/present_width_tables.txt);
  [`figures/present_width.png`](figures/present_width.png).

## Reproduce

```bash
python3 present_width.py   # exact; exit 0 iff all checks pass  (~12 s)
python3 make_figure.py     # writes the two-panel figure
```

# Report v8 — neutral weight background, history-shaped placement

*Plain-language write-up, written after the run. Register: speculative
exploration; not a confirmatory study, not cosmology. Bounded follow-up. Rules
fixed in advance in [`DESIGN_NOTE_v8.md`](DESIGN_NOTE_v8.md). Intervention on initial
conditions only; dynamics unchanged. 200 seed blocks, 10,000 steps. Reproduce:
`python accretion_pilot_v8.py`.*

## Question

Can initial **diagonal placement** guide a later history-discriminating visitation
footprint when the **original-edge weights carry no A/B directional bias**?

## Setup

We built two worlds that share a neutral background `W_0(e) = (W_A(e)+W_B(e))/2` and
differ **only** in diagonal placement — `W_0+T_A` vs `W_0+T_B` — then evolved each
under the unchanged Growing rules and read the frozen v5 footprint
`S_high = Σ s(e)·1[w≥5.5]`. Primary endpoint **t=2000** (pre-selected from prior
exploration, where the footprint peaks).

**Construction verified** (`results/construction_checks.txt`): `W_0` is
transpose-invariant (no A/B directional cue); `T_B = σ(T_A)`; the two worlds have
matching initial edge count (174) and total weight (244), zero initial high bits,
and transpose-related full states (`W_0+T_B = σ(W_0+T_A)`). **Documented:** averaging
preserves the original-edge *total* weight (`Σ W_0 = Σ W_A = 214`) but **changes its
multiset** and hence the local growth-trigger schedule relative to any v6 world — so
`W_0` is a *specified neutral background*, not a removal of every historical
consequence (`W_0` still carries symmetrised history-shaped magnitude; only the
between-world difference is placement).

## Answer — placement alone gives only a fleeting early bias, at chance by t=2000

Fixed-orientation AUC distinguishing `T_A` from `T_B` (A-positive), and mean signed
separation, with seed-block bootstrap 95% CIs:

| checkpoint | AUC (T_A vs T_B) | signed separation (T_A − T_B) |
|---|---|---|
| 100 | 0.63 (peak) | — |
| 400 | 0.571 [0.517, 0.621] | +1.33 [0.26, 2.40] |
| 1000 | ≈0.50 | — |
| **2000 (primary)** | **0.484 [0.429, 0.537]** | **−0.56 [−2.96, 1.89]** |
| 10000 | 0.524 [0.472, 0.574] | +0.10 [−0.09, 0.29] |

- **At the primary endpoint (t=2000), placement alone is at chance:** AUC 0.484,
  CI straddling 0.5; signed separation CI includes 0.
- **There is a real but weak, transient *early* effect:** AUC peaks ~0.63 at t=100
  and is still 0.571 [0.517, 0.621] at t=400 (CI excludes chance; signed separation
  +1.33 [0.26, 2.40] excludes 0). The pre-placed `T_A` diagonals, present from t=0,
  get a head-start toward the four-traversal threshold, giving an early A-lean. It
  **decays to chance by t=1000–2000** and stays there.

Both worlds develop large per-world imbalance regardless (mean `|S|` ≈ 10.6–10.9 at
t=2000; matched high-bit counts ~70–71) — as in v7, the worlds grow a lopsided
high-bit pattern, but under the neutral background its **direction is not steered by
placement** beyond the early transient, so the two conditions are indistinguishable
at the peak.

## Reading it against v6/v7

v6/v7 showed the strong, reproducible directional footprint in the intact worlds
travelled with the **aligned weight cue**, and that crossing the cue mainly
scrambles direction-consistency (v7). v8 completes that picture from the other side:
with the directional weight cue fully **neutralised**, placement alone sustains **no**
directional footprint at the primary endpoint — only an early head-start that washes
out. Together these are consistent with the walker's direction being carried by the
**weight** background; placement contributes a transient early bias but does not, by
itself, hold a direction against a symmetric background.

## Interpretation boundaries (honoured)

- This shows `T_A` vs `T_B` has (at most) a weak, early, non-persistent effect on the
  footprint **under this particular symmetric `W_0` background**. It does **not**
  establish universal topology sufficiency, topology as the late storage carrier, or
  independence from reinforcement and subsequent growth.
- The near-chance result at t=2000 does **not** establish absence of all recoverable
  history, nor the necessity of aligned weights — it is what it is: at the
  pre-selected endpoint, this reader on these two worlds cannot tell them apart
  (AUC 0.484 [0.429, 0.537]).
- The initial **presence** pattern differs between the worlds by construction; the
  finding is that this difference does **not** guide the later thresholded visitation
  footprint (whose bits start empty) beyond an early transient.
- `|S|` remains *unsigned directional imbalance*, not memory by itself.

## One worthwhile next question

The early effect (AUC ~0.63 at t=100, decaying) is the interesting remnant: placement
buys a **head-start** that erodes. A bounded, still snapshot-friendly next step:
characterise the **decay** — from these v8 snapshots, at each checkpoint compute the
placement AUC and fit/where it crosses chance, and compare the per-diagonal high-bit
pattern at t=100–400 to the initial `T_A`/`T_B` masks (how much of the early signal
is literally "the pre-placed diagonals crossed threshold first"). That quantifies how
long an initial placement advantage survives a neutral background, using the
snapshots already retained here — before any alignment-axis intervention.

---

## Interpretation correction — 2026-09-07 (numbers above unchanged)

*Added while writing the v9 substrate-comparison design. The estimates above are
preserved; this tightens four claims.*

1. **"At chance" overstates the primary endpoint.** At t=2000 the reader shows **no
   clear discrimination** (AUC 0.484 [0.429, 0.537]); the interval is *consistent
   with chance* but does **not prove exact chance or equivalence**. Read it as
   "this reader does not distinguish the two worlds at the primary endpoint," not as
   proof of zero information.
2. **v8 does not establish that weights alone carry or dominate the causal
   influence.** v6 found effects of **both** initial weights **and** placement. v8
   shows only that placement *alone, against this symmetric `W_0` background*, gives
   no sustained discrimination — it does **not** isolate weights-alone, nor show
   weights dominate. The phrases above about the footprint "travelling with the
   weight cue" should be read as *consistent with* v6+v8 together, not as a
   demonstration that weights are the dominant carrier.
3. **The early activation-head-start is a hypothesis.** Checkpoint snapshots record
   states, not **threshold-crossing times**; "pre-placed diagonals crossed threshold
   first" is a plausible mechanism the snapshots do not directly verify.
4. **Do not fit a "time when memory disappears."** The suggested next step above of
   finding "where [the AUC] crosses chance" is **withdrawn**: a noisy AUC curve
   crossing 0.5 must not be turned into an estimated disappearance time. A sounder
   next step is to compare the early (t=100–400) per-diagonal high-bit pattern to the
   initial `T_A`/`T_B` masks (overlap fraction), reported with uncertainty and
   **without** fitting a crossing time.

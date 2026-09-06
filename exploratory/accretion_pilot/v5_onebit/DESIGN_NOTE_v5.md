# Follow-up design note (v5) — one bit per added diagonal

*Written before execution. Register: speculative exploration; not a confirmatory
study, not cosmology. Bounded, snapshot-only follow-up to v4 (chain v1 `cc514ee` →
v2 `cab9254` → v3 `fe49f64` → v4 `43d0c61`). Isolated under
`exploratory/accretion_pilot/v5_onebit/`. v1–v4 retained unchanged (a dated
documentation correction is appended to `../v4_decomposition/REPORT_v4.md`, numbers
preserved). No merges, publishing, sealed-study access, new dynamics, or parameter
sweeps. We reuse v4's saved per-edge snapshots and change only the reader.*

Requested by Astra (Katie has authorised Astra to steer routine steps here).

## Question

Can a **single bit per added diagonal** — whether it has accumulated **at least
four traversals** since activation — retain the late history (A vs B) distinction?

## The threshold (corrected)

Do **not** use exact `w == 6`. Under the dynamics an added edge starts at 1 and its
gap to the cap halves each traversal:

    6 − wₙ = 5 / 2ⁿ

so exact equality with 6 is only a floating-point rounding event, not a physical
completion. We use the threshold already implied by v3's whole-number quantiser:

    b(e) = 1 if w_e ≥ 5.5, else 0

Verified in exact (rational) arithmetic: `w ≥ 5.5` first holds at **n = 4**
(`w₃ = 5.375 < 5.5 ≤ 5.6875 = w₄`), and `round(w) = 6` ⇔ `w ≥ 5.5`. So the bit means
**"four-or-more traversals since activation"**, equivalently **"rounds to 6"** — we
describe it those ways, never "finished saturating".

## Readers (defined before execution; on present added diagonals only)

With the existing coordinate sign `s(e) = sign(col_mid − row_mid)`:

- `P_D  = Σ s(e)`              — added-edge **presence** contrast (each present diagonal counts 1);
- `S_high = Σ s(e)·b(e)`       — **high-bin** contrast (the one-bit reader);
- `S_low  = Σ s(e)·[1 − b(e)]` — **low-bin** contrast.

**Asserted per snapshot:** `S_high + S_low = P_D`. Missing diagonals are a **distinct
state**, not low-weight present edges — they enter none of these sums; we retain the
missing-diagonal mask and report counts.

**Primary one-bit score:** `S_high`, with the existing A-positive orientation.
**Complementary low-bin score:** `−S_low`, declared here (not chosen after results).
On complete topology `P_D = 0`, so `S_high = −S_low` exactly — this identity is
checked.

## Data and validation (snapshot-only)

Analyse v4's `../v4_decomposition/results/edge_snapshots.npz` directly — **no rerun
of trajectories**. Same 200 seed pairs, models, checkpoints. Before the new reader:
(i) validate the snapshot schema (universe, `is_original`, `signs`, 64 arrays of
shape (200, 272)); (ii) reproduce v4's added-edge readers `D0` and `D1` from the
snapshots and match v4's `summary_by_reader.csv` AUCs.

## Comparisons (every original checkpoint)

Compare the one-bit scores (`S_high`, and `−S_low`) against:

- added-edge exact-weight contrast `D0`;
- added-edge whole-number contrast `D1`;
- added-edge presence contrast `P_D`.

Report, per reader and checkpoint: **AUC** (A-positive, no post-hoc sign reversal),
**fixed sign-decoder balanced accuracy**, **paired ordering score**, **tie
fraction**, and **signed A/B separation** `mean(reader_A) − mean(reader_B)`.

## Bootstrap (whole seed pairs; checkpoints 400, 2000, 10000)

- one-bit (`S_high`) AUC, per model;
- **one-bit minus D1 AUC within Growing** (the cost of collapsing the
  whole-number added reader to a single bit);
- **Growing minus timing-matched-control** one-bit AUC.

We **do not infer equivalence from an interval containing zero**: we report the
estimated **loss or gain** and its uncertainty explicitly.

## Complete-topology subset (late; descriptive)

Repeat the late analysis on each model's complete-topology pairs (both A and B
worlds have all 128 diagonals present). Report included **seed identities and
counts**, and **whether the subsets match between models** — we do not silently
treat different subsets as a matched comparison. On this subset `P_D = 0`, so
`S_high = −S_low`; any discrimination there is carried by the bit pattern on an
identical set of diagonals.

## Interpretation limits (pre-stated)

A successful bit reader shows a **thresholded visitation footprint** retains
information about the imposed history. It does **not** reveal threshold-crossing
times, prove memory transfer, establish intrinsic addressing, or isolate
history-shaped placement from all remaining confounders. Early one-bit readings can
**mix edge-presence differences with visitation differences**; the
complete-topology subset removes the presence distinction for the late analysis.

## Deliverables

This note; snapshot-only analysis code + one-line reproduction command; validation
checks; raw/summary tables; one compact reader-comparison figure; a plain-language
report; and the dated v4 documentation correction. Keep **this one threshold only** —
no dropout, noise variants, new control families, or longer runs.

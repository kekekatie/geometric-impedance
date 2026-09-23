# Follow-up design note (v4) — reader decomposition

*Written before execution. Register: speculative exploration; not a confirmatory
study, not cosmology. Bounded follow-up to v3
(v3 commit chain: v1 `cc514ee` → v2 `cab9254` → v3 `fe49f64`). Isolated under
`exploratory/accretion_pilot/v4_decomposition/`. v1–v3 retained unchanged (v3's
numerical record preserved; a dated interpretation correction is appended to
`../v3_precision/REPORT_v3.md`). Nothing merged or published; no sealed-study
access, no new dynamics, no parameter sweeps, no dropout experiments.*

Requested by Katie and Astra. **We change only the reader, not the world.**

## Why this step (and what it corrects)

v3 showed robustness to whole-number weight quantisation and I wrongly read that as
"topological memory". It is not. Direct count of the v2 worlds: at t=10000, **399
of 400** Growing worlds have all 128 candidate diagonals active; one world has 126;
**2 missing candidate edges in total**. Topology is essentially identical across
worlds and histories at that checkpoint, so it cannot supply the full-reader AUC of
~0.613. The Δ=1 reader still resolves integer-scale *weight* differences. This
follow-up decomposes the readout to locate the discrimination, and the v3 claims
"topological", "sub-quantum", and "dropout would confirm topology" are withdrawn.

## Question

Where does the existing history readout obtain its discrimination at each stage —
**edge presence**, **weights on original (grid) edges**, or **weights on added
(diagonal) edges**?

## Worlds unchanged

Replay the identical v2 worlds (200 seed pairs, original checkpoints, timing-matched
control), importing v2 dynamics. Measurement consumes no dynamics RNG and does not
change trajectories. **Retain full edge snapshots** from this replay
(`results/edge_snapshots.npz`) so future reader-only analyses need not rerun the
worlds. Before interpretation, verify reproduction of v3's full-reader values at
Δ=0 and Δ=1 with complete model/history/seed/checkpoint coverage.

## Readers (all use the existing coordinate sign s(e) = sign(col_mid − row_mid))

Let `qΔ(w)` be the v3 quantiser (`Δ=0`: exact; `Δ=1`: `floor(w+0.5)`). "Original"
edges are the 144 base grid edges; "added" edges are activated diagonals.

1. **Presence only:** `P = Σ s(e)` over present edges (every present edge weight 1).
   No Δ.
2. **Original-edge weights:** `BΔ = Σ s(e)·qΔ(w_e)` over present **original** edges.
3. **Added-edge weights:** `DΔ = Σ s(e)·qΔ(w_e)` over **added** diagonals.
4. **Full reference:** `MΔ = BΔ + DΔ` (the v3 reader).

Δ ∈ {0, 1} only. **Additive identity asserted per snapshot:** `MΔ = BΔ + DΔ`
(stable `fsum` for Δ=0, exact integer arithmetic for Δ=1). Note that **AUC is not
additive** — a component's standalone AUC is not its share of the full AUC.

## Presence vs weight-departure decomposition (algebraic, not mechanistic)

Also compute, over all present edges,

    RΔ = Σ s(e)·[qΔ(w_e) − 6]

and assert the algebraic identity

    MΔ = 6·P + RΔ .

`6P` is the "presence backbone" (what the contrast would be if every present edge
sat exactly at the cap 6); `RΔ` is the signed shortfall from saturation. Near
saturation with near-complete, near-symmetric topology, `6P` is nearly equal for A
and B, so any surviving discrimination must live in `RΔ`. This is an **algebraic
decomposition of the readout, not an independently established mechanism.**

## Complete-topology subset (t=10000; descriptive, selected after evolution)

Report, separately by model and history:

- number of worlds with all 128 candidate edges present;
- total missing candidate edges;
- discrimination of the full (`M`) and `R` readers **restricted to
  complete-topology worlds**.

Preserve seed identities; compute paired scores only for pairs whose **both** A and
B worlds qualify; report the included counts. This subset is **descriptive and
selected after evolution**, not a new matched causal comparison. Within it topology
is identical for every world, so a presence-only reader offers no distinction by
construction; any discrimination there is carried by weights.

## Statistics (per reader, per checkpoint)

- **AUC** with the original orientation, **no post-hoc sign reversal**.
- **Paired ordering score** `frac(reader_A > reader_B)` (ties ½) and **tie fraction**.
- **Fixed sign-decoder balanced accuracy** (predict A if reader>0, B if <0, ½ if 0).
- **Signed separation** `mean(reader_A) − mean(reader_B)`.

At checkpoints 400, 2000, 10000: **seed-pair bootstrap** 95% intervals for each
reader's AUC and for the Growing−control AUC differences, resampling whole A/B seed
pairs. All comparisons are **exploratory**.

## Interpretation guards (pre-stated)

- **A component's standalone predictive performance is not its unique causal
  contribution.** The components are correlated; cancellation or reinforcement
  between `B`, `D` (and between `6P`, `R`) can matter. We report standalone AUCs and
  the algebraic identities, and do not equate them.
- **Failure of the presence contrast does not rule out every possible topology-based
  decoder.** It rules out *this* coordinate-signed presence sum.
- **Conversely, identical labelled topology genuinely offers no distinction to any
  topology-only reader** within the complete-topology subset.
- We will **not** describe any temporal shift in which component predicts as "memory
  transfer" without further evidence — such a shift is an observation about readers,
  not a demonstrated mechanism.

## Deliverables

This note; code + one-line reproduction command; retained edge snapshots;
validation (vs v3) and decomposition-identity checks; raw and summary tables; one
compact figure comparing the presence, original-edge, added-edge and full readers
over time; a plain-language report separating observations, algebraic identities,
and mechanistic hypotheses; and the dated correction to v3.

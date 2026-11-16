# Pass 2 protocol (FROZEN before running) — k=3 sample + cap sensitivity

2026-11-16. Frozen per Sol's audit, starting from Pass 1 at `f278297`. This file
is committed **before any Pass 2 decode**. It fixes every design choice; results
go in a later commit. The paper claim will be tied to the fault range and decoder
bounds actually tested here.

## Fixed from Pass 1 (unchanged)

- Code/decoder: `nd_surface.Surface(5)` + `nd_infer.Decoder(5, (2,2))`, the
  bounded-frame method. Bulk site **(2,2)**, star {9,10,13,14}, interior, four
  neighbours, query 8, outside both logical supports.
- Noise p = 1e-3, onsets {1,2}, deadline round 4, five rounds, four arms
  (thick, thin, diamond, whole), XOR parity composition, Bernoulli-odds weights.
- **Primary run caps: `w_frame = 3`, `w_dec = 3`** (same as Pass 1).
- Scoring: Pass 1's exact 1e-12 tie rule with half-credit against truth
  (`tie-aware`), reported alongside hard-label (zero-favouring tiebreak).

## 1. Primary k=3 sample (frozen)

- **Primitives.** The 370 ordinary-fault primitives in canonical nd_run pool
  order (25 data × 5 rounds × {X,Z} = 250; then MZ on the 12 Z-stabs × 5 = 60;
  then MX on the 12 X-stabs × 5 = 60), indexed 0–369. (`pass2_sample.primitives`.)
- **Draw.** 25,000 **distinct** triples (sorted index 3-tuples), uniformly without
  replacement, `random.Random(SEED)`, **SEED = 20261116**.
  - Sample sha256 (canonical sorted list, `a,b,c;...`): **`34aa495f75035da6b0be05d7dafeef3bbbe433b7e7df1b0e61d90b16b14ffb88`**
  - First triple `(0,1,164)`, last `(360,364,366)`. (`pass2_sample.draw`.)
- **Histories.** Each triple × {onset 1, onset 2} × {(vx,vz) ∈ {0,1}²} = **8**
  histories ⇒ **200,000** histories, all weight `odds³` (k=3). The **same**
  histories are given to all four arms.
- **Estimand.** Within-k=3 mean paired difference (equal weights within the
  stratum): `μ = mean over k=3 histories of (credit_A − credit_B)`, for
  **A−B ∈ {thick−thin, diamond−thin}**, in both tie-aware and hard scoring.

## 2. Reporting for the primary sample

- Per arm: tie-aware and hard within-k=3 truth; exact tie count and tie weight
  fraction.
- Paired `thick−thin` and `diamond−thin`: wins in **both** directions
  (A-strictly-better mass, B-strictly-better mass), tie-involved mass, net.
- `whole` vs `thick`: label agreement and posterior (p0,p1) agreement.
- **95% interval (cluster-robust).** The 8 histories from one triple are one
  group. Cluster bootstrap over the **25,000 triples** (resample triples with
  replacement), **B = 10,000**, percentile 2.5 / 97.5; **BOOT_SEED = 20261117**.
  Report the cluster-SE normal-approx interval alongside as a cross-check.
- **Combination (conditional on k≤3).** Combined within-k≤3 margin
  `= Σ_{k=0..3} π_k · margin_k`, with frozen model weights
  `π = [0.691003, 0.255927, 0.047266, 0.005804]` (k=0,1,2 margins exact from
  Pass 1; k=3 margin = this sample's estimate, with its bootstrap interval
  propagated). Report the **remaining P(k≥4) = 0.000574** (Binomial(370, 1e-3))
  separately; it is outside the tested range.
- **Benchmark (frozen).** A within-k=3 `thick−thin` advantage of **0.4 percentage
  points** contributes `π_3 × 0.004 = 2.32e-5` to the combined margin ≈ the entire
  existing d=5 gap (0.000023). Decision rule: if the 95% interval lies well below
  0.004, k=3 does not materially change the picture; if it spans both 0 and 0.004,
  the effect size is left open; if it lies above, k=3 matters.

## 3. Stress panel (frozen construction rule, reported SEPARATELY)

Constructed, not sampled; never pooled into the population estimate. Two parts:

- **(a) Near-loss faults.** Local primitive set `P_loc` = {X and Z faults on the
  nine neighbourhood data qubits — the 3×3 block (1,1)…(3,3), i.e. the union of
  the supports of star stabs {9,10,13,14} — at rounds 0–4} ∪ {MZ on {9,10,13,14}∩
  Z-stabs and MX on {9,10,13,14}∩X-stabs at rounds 0–4}. Enumerate **all weight-1
  and weight-2** configs from `P_loc`, each × 8 variants. Exact count recorded at
  build (a property of this frozen rule, not an outcome).
- **(b) Loss-crossing chains.** For each sector logical (Z_L, X_L), find every
  **minimum-weight representative** `R` (logical ⊕ stabilizer-coset, searched over
  all stabilizer subsets of that sector) whose support **includes data (2,2)**.
  For each `R` and each placement round t ∈ {1,3}, form the ambiguous **pair**:
  the two ordinary-fault histories whose symmetric difference is `R\{(2,2)}`
  (the loss at onset t supplies the (2,2) contribution), so the pair shares its
  observed readings through the deadline with **opposite true parity**. Report
  each pair's two histories, shared readings, opposite truths, and every arm's
  label/posterior.

For the panel report each arm's tie-aware and hard truth, tie counts, and the
`thick−thin` / `diamond−thin` decomposition — **separately** from §1–2.

## 4. Cap sensitivity (frozen)

- **Inputs (fixed before decoding):** the **first 250 triples** of the canonical
  sample (`cap250` sha256 **`cc8be35776d64ddca09dc534666a29ee8198b449b982b686d2ed9eda0eab5310`**),
  all 8 variants (2,000 histories), **plus** the entire stress panel (§3).
- **Configs compared on identical inputs:** `(w_frame, w_dec) =` **(3,3)**,
  **(4,3)**, **(3,4)**.
  - **(4,3) frame-only:** recompute **both** the saved frame table **and** the
    candidate-history frame filter (`_frame_col`) at `w_frame = 4`; keep the
    marginal at `w_dec = 3`.
  - **(3,4) inference-only:** **reuse** the original `w_frame = 3` saved frame;
    raise the marginal to `w_dec = 4`.
- **Prefix accounting:** count observed prefix codes **absent** from the frame
  table, and distinguish **fallback zeros** (prefix absent ⇒ default-0 frame) from
  **supported zeros** (prefix present, committed-argmax 0), under each cap.
- **Report:** frame changes, posterior shifts, label flips, tie changes, and
  paired truth differences, for each cap change, on the random subset and on the
  stress panel.
- **Escalation:** if **both** individual changes materially affect the
  `thick−thin` / `diamond−thin` comparison, also run **(4,4)** on the same panel.
- **Exact method / feasibility.** Weight-4 enumeration is 19,190,605 prefix combos
  per sector (frame, `w_frame=4`) and 47,239,010 combos per sector (marginal,
  `w_dec=4`). Build the weight-≤4 tables **exactly** by **chunked** enumeration
  into packed uint64 arrays (fits in 15 GB RAM: ≈1.2 GB/sector for the marginal);
  reuse the existing packed-query decode. Tables are built once per cap config and
  reused across the panel. If memory/runtime forces a smaller panel, **freeze the
  smaller subset first and document the change** before looking at its outcomes.

## 5. Handback (deliverable)

`HANDBACK_PASS2.md`: this protocol's commit + the results commit, the replay
command, and **one table** covering (i) the random k=3 sample (with the combined
k≤3 estimate, interval, and benchmark verdict), (ii) the stress panel, and
(iii) the cap comparison. The paper claim stays tied to: fault range **k ≤ 3**
(exact for k≤2, 25k-triple sample for k=3) plus the neighbourhood **stress panel**,
and decoder bounds **(w_frame, w_dec)** actually tested, with **P(k≥4) = 0.000574**
reported as untested residual.

## Amendment A (2026-11-16, before any cap outcome): cap-panel reduction

Frozen before running the cap comparison, per §4's shrink clause. The §4 cap panel
specified the 250-triple subset **plus the entire stress panel** (48,840 near-loss
histories). Measuring the w_dec=4 marginal showed it scans 47.24M configs per
distinct full-detector evidence (~200 ms/history, and thick's full-detector
evidence never caches), so the full near-loss census would cost ~2 h **per cap** —
infeasible for (3,4) and (4,4). **Reduction:** the cap panel is the 250-triple
subset (2,000 histories) **plus only the weight-1 near-loss configs** (110 × 8 =
880), total **2,880 histories**. Rationale: the k=3 triples are where a 4th
hypothesis fault most plausibly interacts with w=4; the weight-1 near-loss configs
are the local probes; and the full weight-≤2 near-loss is already covered by the
(3,3) stress census (which, separately, found **zero** ties and **zero** ambiguous
record-groups in the loss neighbourhood — the d=5 seams are non-local). No cap
outcome was inspected before fixing this.

## Replay (once results exist)

```sh
cd src
python3 pass2_sample.py                 # re-derive the frozen sample + hashes
python3 pass2.py primary                # 200k k=3 histories, 4 arms  (~15 min)
python3 pass2.py stress                 # constructed panel
python3 pass2.py caps                   # (3,3)/(4,3)/(3,4) [+ (4,4) if needed]
python3 pass2_report.py                 # combines + the handback table
```

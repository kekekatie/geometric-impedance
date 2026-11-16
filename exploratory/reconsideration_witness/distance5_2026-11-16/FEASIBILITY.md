# Distance-5 feasibility pass + frozen protocol (checkpoint 1)

2026-11-16. Built on the corner run `78f8337`. This is the feasibility pass Sol asked
for **before** freezing the full distance-5 run: propose a tractable inference method,
validate it reproduces Astra's exact d=3 (commit `09a79c1`) within a frozen tolerance,
keep the whole-archive == thick equality, and confirm it runs at d=5. The frozen d=5
bulk protocol is at the bottom; the full run is launched only after this is committed.

## The bottleneck and the method

Astra's E_frame decoder tabulates the committed-logical frame over a **dense** index of
the prefix (rounds 0–3) syndrome: 2^17 per sector at d=3. At d=5 the prefix is 48
detector bits per sector, so the dense table would be 2^49 — infeasible.

**Proposed tractable method (`nd_surface.py` + `nd_infer.py`):** replace the dense frame
with a **bounded-weight committed-logical MAP**, stored as a **sparse** table over only
the prefix syndromes reachable by ≤ `w_frame` ordinary faults. Everything else mirrors
Astra exactly: bounded marginal (`w_dec = 3` per sector), XOR parity composition,
Bernoulli-odds weights, ε = 1e-12 ties (zero-favouring), shared-onset inference, the four
arms, the site-agnostic archive, JSON serialization, and the accounting. Conditioning is
done with **packed-uint64 signatures** so a query over all ≈1.05M candidate configs is a
single masked integer compare. The method is general in `d`.

- Sparse frame table: **4,812** entries/sector at d=3 (vs 65,536 dense), **279,272** at d=5.
- Bounded-weight is **approximate** vs Astra's exact (unbounded) frame; the d=3 deviation
  is the frozen tolerance, and the **same** method is used at both distances so the
  d3-vs-d5 comparison is apples-to-apples.

## d=3 validation (this method vs Astra's exact E_frame `09a79c1`)

| arm | Astra exact (raw / wt-agree / truth) | this method (raw / wt-agree / truth) |
|---|---|---|
| thick | 0 / 1.000000 / 0.995901 | 0 / 1.000000 / 0.995901 |
| thin | 3,433 / — / 0.993003 | 3,371 / 0.996994 / 0.993013 |
| diamond | **341** / 0.999962 / 0.995891 | **331** / 0.999964 / 0.995890 |
| whole | 0 / 1.000000 / 0.995901 | 0 / 1.000000 / 0.995901 |

Diamond split: Astra 123/218, this method 114/217. **whole == thick exactly** (0
mismatches); **JSON serialize→restore roundtrip exact** (0 mismatches); **payload bits
identical** (40/26/66). So the bounded-frame approximation moves the raw diamond count by
10 (2.9%) and every weighted metric by ≤ 2×10⁻⁶.

**Frozen tolerance.** A method is "faithful" here if, at d=3, it keeps whole == thick and
the JSON roundtrip exact, reproduces the payload bits exactly, matches Astra's raw
disagreement counts within **± 5%**, and matches every weighted agreement / truth metric
within **1×10⁻⁴**. The bounded-frame (`w_frame = w_dec = 3`) method meets this.

## d=5 tractability (measured)

- Geometry: 25 data, 24 stabs; **bulk site (2,2)**, star {9,10,13,14} = 2Z+2X, interior,
  **four neighbours**, outside both logical supports (Z_L = bottom row, X_L = left column).
  Diamond query **8** (same as d=3 bulk) — exactly Sol's "missing tile still has four
  neighbours."
- Setup 9 s; ≈1.05M config rows/sector; memory fine.
- Correctness confirmed on samples: **whole == thick (0), roundtrip (0)**.
- Speed after packing: **≈56 ms/history → full 68,128-history run ≈ 64 min** (was ≈19 h
  with the naive marginal).
- **Storage confirmed** (same packing convention): thick **40 → 120** bits; thin base
  **26 → 74** bits; archive coordinate cost **5 → 7** bits/event; diamond max **66 → 116**.

## Frozen protocol for the full d=5 bulk run

- **Code/decoder:** `nd_surface.Surface(5)` + `nd_infer.Decoder(5, (2,2))`, the
  bounded-frame method validated above, `w_dec = w_frame = 3`.
- **Site:** bulk **(2,2)** (recorded geometry above). **Onsets** {1,2}, **deadline** 4,
  **p = 1e-3**, five rounds, four arms — all unchanged from d=3.
- **Ensemble:** the same *shape* — ≤ 2 ordinary faults + the loss at (2,2), two onsets, four
  freed-value pairs — XOR parity, Bernoulli-odds weights. **Ensemble size scales with the
  code:** the single-fault pool is 370 at d=5 vs 130 at d=3 (25 data × 5 rounds × 2 sectors
  + 24 measurement faults), so "≤ 2 extra faults" enumerates **549,088** histories at d=5
  vs 68,128 at d=3 — about 8× more. (Corrected: an earlier draft of this line carried the
  d=3 count 68,128; the probes' "est full 68128" was a placeholder, not the true d=5 count.)
- **Comparison baseline:** the **same method at d=3** (diamond 331, the `nd` d=3 run),
  not Astra's exact 341, so d3-vs-d5 is like-with-like. Astra's exact 341 is the external
  anchor the method was validated against. **Because the ensembles differ in size, raw
  disagreement *counts* are not directly comparable across distances; the fair cross-distance
  comparison is the *weighted* metrics** (agreement / disagreement % / truth, each normalised
  by total ensemble weight = the fault-model probability of that outcome). These are exactly
  the metrics Sol asked to compare.
- **Serialization:** full run scored via `direct`; JSON serialize/restore roundtrip
  validated on the d=5 probe (0 mismatches on 150 histories); a full cold
  fresh-process restart across distinct states is a follow-up (runtime), not this run.
- **Report:** d=3-vs-d5 bulk table — raw disagreements, weighted reference agreement and
  disagreement %, weighted truth accuracy, diamond-right/reference-right split, query
  size, and **weighted-mean and maximum** deadline payload bits (they can tell different
  stories). Keep whole == thick.
- **Frozen predictions.**
  - **M1 — whole == thick** at d=5 (0 disagreements). ~90%.
  - **M2 — storage** as measured: thick 120, thin 74, 7 bits/event, diamond max 116. ~90%.
  - **M3 — query 8** (four-neighbour bulk). ~98%.
  - **M4 — OPEN (Sol):** whether the d=5 bulk diamond-vs-reference **weighted** disagreement
    **grows or shrinks** relative to d=3 bulk (0.0036% weighted, raw 331/68,128 under this
    method) is left open. Two effects pull opposite ways: the bigger quilt gives *distant
    evidence* more room to live outside the fixed 8-reading window (pushes the gap up), while
    the shared thin record roughly triples (26 → 74 bits) and the logical is better protected
    (pushes it down). Compared in weighted terms, since the ensembles differ 8× in size.

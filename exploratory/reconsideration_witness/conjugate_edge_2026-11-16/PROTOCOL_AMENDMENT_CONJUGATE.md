# Distance-3 conjugate edge-loss control: frozen before outcomes

2026-11-16. A geometric control on the exact same distance-3 patch and Astra's corrected
**E_frame** decoder, built on the edge run `93cf914` (which itself extends Astra's bulk
baseline `09a79c1`). Committed **before** the conjugate harness runs. Single distance-3
edge site only.

## The control, and why it is clean

The scored logical is `Z_L`, decoded by the **X-sector**, which reads the **Z-stabs**;
the Z-sector (X-stabs) only informs the onset posterior. So the number of **Z-arms** in
the loss star is the number of *logical-sector* readings in the local diamond, and the
number of **X-arms** is the number of *onset-sector* readings.

Both edge sites have a 3-check star (**6** lip readings) — identical bracket size — but
the conjugate sector is open:

| site | star | Z-arms (logical sector) | X-arms (onset sector) | lip bits | bulk disagreements |
|---|---|---:|---:|---:|---:|
| bulk (1,1) | {1,2,5,6} | 2 | 2 | 8 | 341 |
| Z-open edge (1,2) | {2,3,6} | **1** | 2 | 6 | 896 |
| X-open edge (2,1) | {5,6,7} | **2** | 1 | 6 | *to measure* |

(1,2) lost a **Z-arm** (a *logical-sector* reading) and its disagreements jumped
341→896. (2,1) keeps **both Z-arms** and loses an **X-arm** (an *onset-sector* reading)
instead. This isolates **which sector's missing check** caused the jump, with bracket
size (6 vs 8) held fixed between the two edges. Like the others, (2,1) is outside both
logical supports, so the `Z_L` convention is unchanged.

## Everything else unchanged

Astra's `correction_2026-11-14/src/model.py` is reused **unchanged** (it is report-routed).
The only input that differs from `93cf914` is the report site, now `(2,1)`. Carried
forward exactly: the 68,128 contribution histories (loss relocated to (2,1)); XOR parity;
Bernoulli-odds weights `(p/(1-p))^w`, p=1e-3; ε=1e-12 ties with zero-favouring labels and
tie-aware expected scores; the report-blind two-bit committed MAP frame; shared-onset
inference; five rounds 0–4; deadline 4; decoder bound 3 per sector; the four arms; the
site-agnostic archive; the actual JSON serialization and **cold fresh-process restart**;
and the deadline-payload / JSON-byte / query accounting.

The edge diamond query reconstructs **6** old detector values: X-sector Z-stabs {5,7} ×
onsets {1,2} = 4; Z-sector X-stab {6} × {1,2} = 2.

## Frozen predictions (conjugate (2,1), d=3)

- **H1 — query size.** 6 readings, positions (5,1),(5,2),(6,1),(6,2),(7,1),(7,2). ~98%.
- **H2 — whole == thick.** 0 disagreements, posteriors within 1e-12. ~90%.
- **H3 — the witness persists.** thin+diamond strictly fewer disagreements than thin alone. ~80%.
- **H4 — cold restart.** Fresh-process restoration reproduces every decision (Δ ≤ 1e-12). ~95%.
- **H5 — THE CONJECTURE (sector, not size).** Because (2,1) keeps **both logical-sector
  Z-arms**, its diamond/reference disagreements are **much closer to the bulk 341 than to
  the Z-open edge's 896** — i.e. retaining both Z-arms restores near-bulk re-judgment
  accuracy at 6 bits. Concretely: (2,1) disagreements **< 550** (nearer 341 than 896), and
  materially below (1,2)'s 896. Conf ~70%. If instead (2,1) ≈ 896, the jump was bracket
  **size**, not sector; if (2,1) ≈ 341, it was the **logical-sector Z-arms**.

## Handback

A clean **3-way distance-3 geometry comparison table**: bulk (1,1) 2X+2Z / Z-open (1,2)
2X+1Z / X-open (2,1) 1X+2Z, each with raw and weighted disagreements vs its own
same-deadline thick reference, weighted truth correctness, diamond-right vs reference-right
split, query size and deadline-payload bits. One replayable (2,1) disagreement if found.
Protocol, baseline and result commits, and the replay command. Scope: this single
distance-3 conjugate edge site.

# Distance-3 corner-loss run: frozen before outcomes

2026-11-16. The corner site in the distance-3 geometry series, on the exact same patch
and Astra's corrected **E_frame** decoder. Built on the conjugate-edge run `9564067`
(which carries the bulk baseline `09a79c1` and both edge runs). Committed **before** the
corner harness runs. Single distance-3 corner site only.

## The site and the series

The corner **(2,2)** has a two-check star **{6 (X), 7 (Z)}** — one X-check and one
Z-check — so the local diamond query reconstructs **4** old detector values (vs 6 at an
edge, 8 in the bulk). Like every site used so far, (2,2) lies **outside both** logical
supports (`Z_L` = {(0,0),(1,0),(2,0)}, `X_L` = {(0,0),(0,1),(0,2)}), so the scored `Z_L`
convention is unchanged. (The corner (0,0) was rejected because it lies on both supports,
which would add a second change.)

| site | star | checks | Z-arms (logical) | X-arms (onset) | query | prior disagreements |
|---|---|---:|---:|---:|---:|---:|
| bulk (1,1) | {1,2,5,6} | 4 | 2 | 2 | 8 | 341 |
| edge (1,2) | {2,3,6} | 3 | 1 | 2 | 6 | 896 |
| edge (2,1) | {5,6,7} | 3 | 2 | 1 | 6 | 837 |
| **corner (2,2)** | **{6,7}** | **2** | **1** | **1** | **4** | *to measure* |

A clarification carried forward from the edges (Sol): these runs move the loss **site**
as well as shrink the neighbourhood, so they do **not** cleanly separate the importance
of the two kinds of check; and under the model's weighting the (2,1) edge disagrees
> 2× as often as (1,2) (0.097% vs 0.0428%) despite similar raw counts. The corner adds a
fourth point in the "fewer local checks" direction, not a sector-isolation claim.

## Everything else unchanged

Astra's `correction_2026-11-14/src/model.py` is reused **unchanged** (report-routed; only
the site differs). Carried forward exactly: 68,128 contribution histories (loss at (2,2));
XOR parity; Bernoulli-odds weights `(p/(1-p))^w`, p=1e-3; ε=1e-12 ties with zero-favouring
labels and tie-aware expected scores; the report-blind two-bit committed frame;
shared-onset inference; rounds 0–4; deadline 4; decoder bound 3 per sector; four arms;
site-agnostic archive; actual JSON serialization and **cold fresh-process restart**; and
the deadline-payload / JSON-byte / query accounting.

## Frozen predictions (corner (2,2), d=3)

- **K1 — query size.** The corner diamond reconstructs exactly **4** old detector values:
  positions (6,1),(6,2),(7,1),(7,2). ~98%.
- **K2 — whole == thick.** Thin+whole-archive reproduces the thick same-deadline reference
  exactly (0 disagreements; posteriors within 1e-12). ~90%.
- **K3 — the witness persists.** thin+diamond strictly fewer disagreements than thin alone. ~80%.
- **K4 — cold restart.** Fresh-process restoration reproduces every decision (Δ ≤ 1e-12). ~95%.
- **K5 — OPEN (per Sol).** Whether the local diamond's disagreement with the reference
  **grows again** at the two-check corner is left open. The bracket-size trend from the
  edges suggests it should grow (fewer local checks → less re-judgment), but the corner
  also has a different pruned-error neighbourhood, so no direction is pre-committed. Both
  the raw count and the weighted disagreement are reported.

## Handback

A single **bulk–edge–edge–corner** table: raw disagreements, weighted reference agreement
(and the implied weighted disagreement %), weighted truth accuracy, diamond-right vs
reference-right split, query size and deadline-payload bits. One replayable corner
disagreement if found. Protocol, baseline and result commits, replay command. Scope: this
single distance-3 corner site. Distance-5 (the "bigger quilt, missing tile still has four
neighbours" question) is explicitly deferred.

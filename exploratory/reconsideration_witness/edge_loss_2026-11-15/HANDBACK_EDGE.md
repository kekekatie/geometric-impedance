# Distance-3 edge-loss run: handback

**Result: moving the loss from the bulk site (1,1) to the edge site (1,2) makes the
local diamond substantially *weaker* — diamond/reference disagreements rise from 341
to 896 (≈2.6×) — even though the local query shrinks from 8 readings to 6. The smaller
3-check edge star captures less of the pruned information, so the reduced query is a
real information reduction, not a free saving.** Whole-archive still reproduces thick
exactly, and the "agreement ≠ correctness" nuance persists (≈⅓ of diamond disagreements
are the diamond being right and the same-deadline reference wrong).

Built on Astra's corrected **E_frame** baseline `09a79c1` (reproduced byte-for-byte here
first: thin 3433, diamond 341, split 123/218). Frozen edge protocol `4509bd6`, committed
before this run. Her `model.py` is reused **unchanged**; the only scientific change is
the loss site, which enters solely through the report (driving both the diamond query
geometry and the erasure hypotheses).

## Bulk vs edge (same E_frame model; each site scored against its own thick reference)

| arm | raw disagreements bulk → edge | weighted agreement bulk → edge | weighted correctness vs truth bulk → edge |
|---|---:|---:|---:|
| thick (reference) | 0 → 0 | 1.000000 → 1.000000 | 0.995901 → 0.995666 |
| thin alone | 3,433 → 3,280 | 0.996987 → 0.996565 | 0.993003 → 0.994206 |
| **thin + diamond** | **341 → 896** | **0.999962 → 0.999572** | 0.995891 → 0.995523 |
| thin + whole archive | 0 → 0 | 1.000000 → 1.000000 | 0.995901 → 0.995666 |

**Who was right when diamond and thick disagreed** (diamond-right / reference-right vs truth):
bulk **123 / 218**, edge **301 / 595**. The diamond is right on ~⅓ of its disagreements
at both sites (bulk 36%, edge 34%), so a third of the "gap" is the optimal soft reference
mispredicting a rare individual history, not the diamond failing.

**The diamond's value shrinks at the edge.** Thin→diamond reduces disagreements 10.1×
in the bulk (3,433→341) but only 3.7× at the edge (3,280→896). (Thin-alone is itself
slightly easier at the edge — 3,280 vs 3,433 — but the local query recovers less than
half as much of that deficit.)

## Accounting (query separated from deadline payload and JSON bytes)

Deadline-snapshot payload bits (not temporal/process peaks); compact JSON state bytes
reported separately; query = detector readings passed to the restorer.

| arm | site | query readings | payload bits max | payload bits mean | JSON bytes max | JSON bytes mean |
|---|---|---:|---:|---:|---:|---:|
| thick | bulk/edge | 40 | 40 | 40.000 | 387 | 387.000 |
| thin | bulk/edge | 0 | 26 | 26.000 | 236 | 236.000 |
| diamond | bulk | 8 | 66 | 36.435 | 299 | 263.754 |
| diamond | **edge** | **6** | **61** | **33.975** | 293 | 260.802 |
| whole | bulk | 24 | 66 | 36.435 | 297 | 261.754 |
| whole | **edge** | 24 | **61** | **33.975** | 291 | 258.802 |

The edge diamond reconstructs **6** old detector values (Z-stab 2 ×{1,2}; X-stabs 3,6
×{1,2}) vs 8 in the bulk; whole reconstructs 24 at both. The edge archive payload max/mean
is *lower* (61/33.975 vs 66/36.435) because the edge loss touches 3 checks rather than 4,
so fewer checks fire and the site-agnostic archive is smaller on these histories.

## Frozen-prediction scorecard (G1–G5)

| | prediction | verdict |
|---|---|---|
| G1 | edge query reconstructs 6 old detector values | **HELD** (positions (2,1),(2,2),(3,1),(3,2),(6,1),(6,2)) |
| G2 | whole-archive == thick at the same deadline | **HELD** (0 disagreements; posteriors within 1e-12) |
| G3 | thin+diamond strictly fewer disagreements than thin alone | **HELD** (896 < 3,280) |
| G4 | cold fresh-process restart reproduces every decision | **HELD** (272,512 roundtrip checks, 0 mismatches; 4 cold processes, max prob Δ = 0.0) |
| G5 | **open:** does the disagreement rate rise or fall vs bulk? | **RESOLVED — it RISES** (341 → 896, ≈2.6×); the smaller edge star makes locality less sufficient |

Checks: 272,512 direct-vs-JSON-roundtrip arm checks, 0 mismatches; whole==thick every
history; archive-to-dense reconstruction 0 mismatches; two archive arms identical records;
four fresh-process restorations (thick 27,792 / thin 5,514 / diamond 27,792 / whole 27,792
distinct states), all child exits 0, probabilities within 1e-12.

## One replayable edge disagreement

Faults (scoring only): `X@(0,0) round 1` and `X@(1,2) round 1` (the second coincides with
the loss site and onset 1). True onset 1, **truth = 1**. Decisions: **thick = 0, thin = 0,
diamond = 1, whole = 0.** Here the **diamond is correct (1 = truth) and the reference is
wrong (0)** — another case where the local edge checks resolve the logical that the full
same-deadline record mis-judges. (Present in `results/edge_E_frame.json → example` and the
`bulk_vs_edge.json` summary.)

## Replay

```sh
cd exploratory/reconsideration_witness/edge_loss_2026-11-15/src
python3 edge_run.py            # run E_frame at the edge site, cold restart, summarize
# or stepwise: python3 edge_run.py run ; python3 edge_run.py cold ; python3 edge_run.py summarize
```

- **Baseline (bulk) commit:** `09a79c1` (Astra's corrected E_frame). **Edge protocol
  commit:** `4509bd6`. **Edge result commit:** this commit.
- Reuses `correction_2026-11-14/src/model.py` unchanged; `edge_run.py` only relocates the
  loss to (1,2) and passes `report={'site':[1,2],'onsets':[1,2],'deadline':4}`.
- Runtime JSONL state/restore files are regenerated by the replay (git-ignored).

## Scope and limits

Single distance-3 edge site. No corner site, no distance-5, no later deadline or broader
fault bound. Carries forward Astra's bounds and caveats: bounded (≤2 ordinary faults,
≤3 per-sector decoder) model, not an unbounded optimal decoder; payloads are deadline
snapshots, not temporal/process-memory peaks; reference agreement is distinct from truth;
no distance-scaling, minimum-memory, or circuit-level physical-loss claim. The main new
fact is directional and site-specific: **at this edge site the local diamond is markedly
less sufficient than in the bulk**, which motivates (but does not settle) whether the gap
keeps growing toward the corner and at larger distance.

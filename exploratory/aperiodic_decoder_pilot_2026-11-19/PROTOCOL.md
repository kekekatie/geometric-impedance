# 18-site delayed-report decoder pilot — frozen protocol

**Frozen before any score is examined.** This file fixes every design choice; results
and the exhaustive-vs-sampled decision go in a later commit (a one-line amendment at the
end records the final ensemble choice, committed *before* any truth/benefit outcome is
read). Branch: `claude/aperiodic-decoder-pilot-2026-11-19`, forked from geometry commit
`9c059c76461c33fe921be23ed51b9cc88e19504b`.

## The question this run carries

Put a finger on any eligible edge of a certified patch. Two vertex (X) checks and two
face (Z) checks touch it. If a delayed report names that edge, the local decoder asks
those four checks for their readings at rounds 1 and 2 — eight readings, every time. Does
the value of those eight readings change as the finger moves from edge to edge? Where
does access to the rest of the archive still help?

## Source commits (frozen)

| role | commit | path |
|---|---|---|
| geometry pilot (patches, certificates, figure) | `9c059c7` | `exploratory/aperiodic_qec_geometry_2026-11-19/` |
| frozen geometry cut/selection rule | `cbce124b` | (committed before geometry selection) |
| audited corrected decoder (logic reused) | `09a79c1` | `exploratory/reconsideration_witness/correction_2026-11-14/src/model.py` (= tip of `fix/distance3-bulk-audit-2026-11-14`, byte-identical in tree) |
| tractable bounded `(w_frame,w_dec)` engine reused | `6d0dc09`-line | `distance5_2026-11-16/src/nd_surface.py`, `nd_infer.py` |
| paired-cap audit (scoring discipline) | `7e40b4e` | `exploratory/reconsideration_witness/pass2_audit_2026-11-17/` |
| AB generator (vendored, unchanged) | `49bccf21` | `substrates/generate_ab.py` |
| Penrose source (unchanged) | `7ddcb9b3` | `exploratory/accretion_pilot/penrose_address_environment/penrose_address.py` |

We adopt `model.py`'s **two-earlier-round query bookkeeping, arm definitions, boundary
parity, committed-frame and cold-restart state**, and the **bounded `(w_frame,w_dec)`
frame-table + marginal** engine from `nd_infer.py` (the dense `model.py` frame map is
`2^(10·4)` per sector here — infeasible — so the sparse bounded frame is the correct and
already-audited reuse). We write only a **geometry adapter** (`PatchCode`, a
`nd_surface.Surface` subclass that loads `DATA / STABS / STAR / LZ / XL` from the saved
patch JSON) and a thin `PatchDecoder(nd_infer.Decoder)` that injects it. No original
tiling, geometry, or decoder file is edited.

## The 18 sites (frozen; pure certified geometry)

Each patch: 21 data qubits, `rank HX = rank HZ = 10`, `k = 1`, distances `(3,3)`, six
eligible interior loss edges, all eligible Z-checks weight 4. Loss site = the edge's data
qubit. Each edge's four incident checks = two endpoint X-checks + two adjacent face
Z-checks; query = those four checks at rounds `{1,2}` = 8 check–round coordinates. Check
IDs `X#`/`Z#` index rows of `HX`/`HZ`.

| patch | edge id | lost qubit | incident checks | endpoint degrees |
|---|---:|---:|---|---|
| **square** (control, degree-fixed) | 9 | 5 | X1 X2 Z1 Z4 | (4,4) |
| square | 10 | 6 | X1 X5 Z3 Z4 | (4,4) |
| square | 12 | 8 | X2 X6 Z4 Z5 | (4,4) |
| square | 15 | 11 | X4 X5 Z3 Z6 | (4,4) |
| square | 17 | 13 | X5 X6 Z4 Z7 | (4,4) |
| square | 18 | 14 | X5 X9 Z6 Z7 | (4,4) |
| **AB** | 8 | 4 | X0 X2 Z2 Z3 | (3,4) |
| AB | 10 | 6 | X1 X2 Z2 Z4 | (3,4) |
| AB | 12 | 8 | X2 X3 Z3 Z5 | (4,5) |
| AB | 13 | 9 | X2 X6 Z4 Z5 | (4,6) |
| AB | 15 | 11 | X3 X7 Z5 Z6 | (3,5) |
| AB | 22 | 16 | X6 X7 Z5 Z9 | (3,6) |
| **Penrose** | 4 | 2 | X0 X1 Z2 Z3 | (4,5) |
| Penrose | 5 | 3 | X0 X2 Z2 Z4 | (3,4) |
| Penrose | 6 | 4 | X0 X4 Z4 Z5 | (3,4) |
| Penrose | 7 | 5 | X0 X5 Z3 Z5 | (4,5) |
| Penrose | 9 | 7 | X1 X6 Z3 Z6 | (3,5) |
| Penrose | 18 | 14 | X5 X6 Z3 Z9 | (3,5) |

The **square is the degree-fixed control**: all six endpoint-degree pairs are `(4,4)`, so
any variation among its six sites is variation at *fixed endpoint degree*. Individual
edges are preserved throughout; sites are never pooled by degree in this pilot.

Each edge also carries, for the output table (descriptors, not gating metrics): stable
edge id; sorted endpoint degrees; **distance to the rough boundary** `d_rough` and **to
the smooth boundary** `d_smooth` (convention: minimum over the edge's two endpoint
vertices of the patch vertex–edge **graph distance**, in number of edges, to the nearest
vertex incident to a rough- resp. smooth-arc edge; `0` if an endpoint is itself on that
arc); and the available **lift / layer identifiers** (`lift`, `integer_sum`, and for
Penrose `sum(K)` layer; AB's `sum(K)%5` integer label) carried through for future use.
The perpendicular-space predictor test is **not** run here — it is reserved for
independent patches (per the geometry handback: six sites in one patch are correlated and
the selection favoured interior/degree variety).

## Scored observable (frozen)

Each patch's certified **Z-logical support** (`logical_Z`) scores the final **X-error
parity**: `truth = (Σ_{q ∈ logical_Z} cumulative_X_error[q]) mod 2`, evaluated at the last
round. The support is fixed across all four arms and all loss sites within a patch.
(`logical_Z`: square `[18,12,4]`, AB `[13,7,2]`, Penrose `[10,9,1]`.)

## Delayed-report model (frozen, inherited)

Five measurement rounds `0–4`; inherited per-primitive noise `p = 1e-3`; candidate loss
onsets `{1,2}`; report delivered after round 4. The retained state is built after round 3,
**before the loss site is known** (commit rounds `0,1,2`; live rounds `3,4`). The decoder
marginalizes over a **shared unknown onset** in both sectors (same `onset` term couples
the X- and Z-sector marginals). Baseline decoder bounds `(w_frame, w_dec) = (3,3)`; these
bound the number of ordinary faults in a candidate explanation. Primitive noise
probabilities are held fixed as check weight varies.

| arm | evidence at the deadline |
|---|---|
| **thick** | full detector history, rounds 0–4 |
| **thin** | rounds 3–4; one boundary parity per check for rounds 0–2 (`det0⊕det1⊕det2`); two committed frame bits from the pre-report prefix |
| **diamond** | thin state **+** the eight old values at the four certified incident checks in rounds 1 and 2 |
| **whole** | thin state **+** reconstruction of every discarded reading (site-independent sparse fired-check archive) |

`diamond` and `whole` draw on the **same site-independent sparse archive** prepared before
the report (non-zero prefix detectors). The serialized-state restart path is exercised
(serialize → JSON round-trip → `decode_state`), and payload is split into **stored before
the report** (archive size) vs **read after it arrived** (diamond's 8 query values).

## History ensemble (frozen)

Ordinary-fault primitive pool (per patch, abstractly identical index sets): data `X`/`Z`
faults `21 × 5 × 2 = 210`, plus measurement faults `MZ (10×5=50)` and `MX (10×5=50)` =
**310 primitives**. The inherited ensemble is **zero-, one-, and two-ordinary-fault**
configurations, each crossed with **both onsets `{1,2}`** and **all four erasure-value
pairs `(v_x, v_z) ∈ {0,1}²`** (the erasure contributes a free `X` and/or `Z` fault on the
loss qubit at the onset) = **8 variants** per configuration. Faults compose by GF(2)
parity (`compose`, XOR). The **same ordinary-fault configurations are used across all six
sites of each patch** (and, for maximal comparability, across all three patches — the
primitive index sets coincide); **all four arms see identical histories at a site**.

Weight of a configuration with `k` ordinary faults `= odds^k`, `odds = p/(1−p)`,
`p = 1e-3` (the erasure is the free, uncounted fault). The denominator is `W = Σ weights`
over the evaluated ensemble; every weighted metric is `(Σ weight · value) / W`. Note
`k = 0,1` carry ≈96.5% of the total weight, so weighted benefits are governed by the
low-order strata.

**Enumeration size.** Exhaustive `≤2` faults `= 1 + 310 + C(310,2) = 48,206` configs `× 8
= 385,648` histories/site `× 18 ≈ 6.9M` — likely multi-hour. Per the resource clause we
pre-specify a **seeded representative fallback**, chosen *before any score is read*:

- **Exhaustive** `k ∈ {0,1}` (`311` configs `× 8 = 2,488` histories/site).
- **Seeded `k = 2` sample**: `N` configurations drawn **uniformly without replacement**
  from the sorted list of all `C(310,2) = 47,895` index pairs, `random.Random(20261119)`,
  the **same sample reused at all 18 sites**; SHA-256 of the sorted sampled list recorded
  at run time. Each sampled `k=2` config carries a Horvitz–Thompson inflation
  `odds² · (47,895 / N)` so the `k=2` stratum's total weight matches the full ensemble;
  `W` uses the exact `47,895 · odds²` for that stratum.
- **Decision rule (committed before scores).** Benchmark one site end-to-end. If the
  extrapolated exhaustive total is `≤ 4 h`, run exhaustive. Otherwise run the fallback
  with the **largest `N ∈ {2000, 4000, 6000, 8000}`** whose extrapolated total is `≤ 3 h`.
  The chosen mode and `N` are recorded in the amendment below *before* any truth/benefit
  outcome is examined. Results are labelled **exhaustive** or **sampled**; under sampling,
  the record-ambiguity fraction (Metric B) is reported as an **observed lower bound**.

## Tie rule (frozen)

Normalized-posterior tolerance `EPS = 1e-12`: a decision is a **tie** iff
`|p0 − p1| ≤ EPS` after normalization. Truth credit is **tie-aware**: strict win `= 1`,
tie `= 0.5`, strict loss `= 0`. Hard-label credit (zero-favouring tiebreak) is reported
alongside. Per-arm weighted **tie rate** uses the same `EPS`.

## Metrics per edge (frozen)

**A — where does forgetting cost us?** On identical histories, weighted tie-aware truth
credit for each arm; paired differences **thick − thin**, **diamond − thin**, and
**thick − diamond**, in percentage points, with **negative and zero values kept visible**.
Separately: each arm's weighted **disagreement with thick's decision** and **posterior
difference from thick** (fraction of weight with `|p0 − p0_thick| > EPS`). The full-record
call can itself be wrong on an individual history, so disagreement is reported apart from
truth.

**B — where is the record ambiguous, and where does the decoder tie?** At fixed patch,
loss edge, and report, group histories by **exact full detector record**. Report the
fraction of evaluation probability in groups containing **both** scored truths within the
evaluated ensemble (record ambiguity). Separately report each arm's weighted **tie rate**.
Both are preserved even if one is zero everywhere (our earlier audit found opposite-truth
histories with identical records whose posteriors were far from 50/50). Under sampling the
ambiguity fraction is an observed lower bound.

## Validation (frozen; run before interpreting any site difference)

1. **Adapter sanity.** Rebuild `HX`/`HZ` from `STABS`; confirm `HX·HZ^T = 0`, ranks `10`,
   `⟨LZ, XL⟩ = 1`, and the certified distances via weight-1/2 syndrome enumeration in
   both sectors.
2. **Single-fault tests, both sectors.** For a single `X` (resp. `Z`) data fault, the
   fired Z-checks (resp. X-checks) equal the incident stabilizers, and the scored logical
   parity equals the fault's overlap with `logical_Z` (resp. the X-sector check).
3. **`whole == thick`.** Identical labels and posteriors to `EPS` on every evaluated
   history.
4. **Restart == direct.** `serialize → JSON round-trip → decode_state` reproduces the
   direct decode for every arm (checked on a seeded subsample at scale, exhaustively on
   the validation set).
5. **Diamond query shape.** Exactly **four distinct incident checks** and **eight distinct
   check–round coordinates** in every diamond query, matching the certified `query`.
6. **Frozen-case replay.** Replay an original d=3 decoder case against its saved output
   before interpreting the new patches.

Any failed invariant is investigated **before** interpreting site differences.

## Cap sensitivity (frozen)

Freeze a representative, seeded sensitivity panel spanning all 18 sites (the exhaustive
`k ≤ 1` histories at every site, plus a small shared seeded `k = 2` subset). Replay the
same panel at `(w_frame,w_dec) = (3,3)`, `(4,3)`, `(3,4)`, and `(4,4)` **if feasible**.
Report observed prefix codes **absent** from the frame table (unsupported frame prefixes,
fallback vs supported zeros) and **changes in the paired arm benefits** (thick−thin,
diamond−thin, thick−diamond) at each cap. If a visible feature moves or changes sign,
identify the affected edges.

## Deliverables (frozen)

An **18-row machine-readable table** (`results/edges.json` / `.csv`) and **one figure**
(`results/heatmap.(svg|png)`): three rows, one per tiling, each drawing the actual patch
**twice** — left coloured by **thick − thin**, right by **diamond − thin** — on a shared
scale **centred at zero**, untested edges left neutral, each tested edge given a short id.
An all-zero map is a result worth showing. Commit and push the branch; return the protocol
and result commits, a direct figure link, and one reproduction command. The handback ends
in plain language: when you move your finger across each patch, where does the cost of
forgetting change; where do eight old readings recover that cost; and which observation,
if any, deserves a test on fresh patches.

## Amendment (ensemble choice — recorded before any score is read)

_To be filled with the benchmark result and the committed exhaustive/sampled choice and
`N`, before the scoring run is examined._

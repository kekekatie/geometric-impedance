# 18-site delayed-report decoder pilot — handback

Branch `claude/aperiodic-decoder-pilot-2026-11-19`, forked from geometry `9c059c7`.
Protocol frozen in [`PROTOCOL.md`](PROTOCOL.md) (commit `c1dab63`) **before any score**;
ensemble amendment (sampled `N=8000` k=2, seed 20261119) recorded from timing alone
(commit `607ed43`) before any truth/benefit outcome. Decoder reused by adapter + subclass
from the audited bounded engine; **no tiling, geometry, or decoder source edited**.

- Protocol: `c1dab63` (+ amendment `607ed43`)
- Adapter + validation: `0563573`; downstream code: `eea2b0f`
- Primary results + figure: `9adb298`; frozen caps + discriminator test: `<this commit>`
- Figure: [`results/heatmap.png`](results/heatmap.png) (+ `.svg`); table:
  [`results/edges.csv`](results/edges.csv) / [`edges.json`](results/edges.json); caps:
  [`results/caps.json`](results/caps.json), [`results/caps_discriminator.json`](results/caps_discriminator.json)
- Replay (one command): `cd src && PYTHONPATH=. python3 validate.py && PYTHONPATH=. python3 run_all.py && PYTHONPATH=. python3 aggregate.py && PYTHONPATH=. python3 figure.py && PYTHONPATH=. python3 caps.py && PYTHONPATH=. python3 caps_disc.py`

## Validation (all pass, before interpreting sites)

Ranks `10/10`, commutation, anticommuting weight-3 logicals, no weight-≤2 X-logical on
all three patches; single-fault syndrome + logical parity in both sectors; **`whole ==
thick` labels+posteriors and `restart == direct` with 0 anomalies across all
1,196,784 decoded histories**; every diamond query is exactly 4 distinct checks / 8
distinct check–round coords matching the certified query; the frozen d=3 bulk example
replays bit-for-bit through the untouched `nd_infer` engine; and the chunked cap builder
reproduces the stock decoder at `(3,3)` (0 mismatches). `results/validation.json`.

## How the run was scored

Per site: `8,311` ordinary-fault configurations (exhaustive `k≤1` + seeded `N=8000` k=2,
Horvitz–Thompson weighted) × 8 onset/erasure variants = **66,488 histories**, identical
across the four arms; tie-aware truth credit (½ on a `1e-12` tie); weights `odds^k`. The
`k=2` stratum is sampled, so the record-ambiguity fraction (Metric B) is an **observed
lower bound**; the paired truth benefits are governed by `k≤1` (≈96.5% of weight) and are
not materially sampling-limited. All benefits below are **percentage points (pp)**.

## A. Where does forgetting cost us?

The headline is clean and lives in the **square control**, where every eligible edge has
endpoint degrees `(4,4)` — so any variation there is variation *at fixed endpoint degree*:

| square edge | lost qubit | on a logical? | cost of forgetting (thick − thin) | 8 readings (diamond − thin) | thick − diamond |
|---|---:|---|---:|---:|---:|
| S1 | 5 | no | −0.00050 | +0.00055 | −0.00105 |
| S2 | 6 | no | −0.00105 | +0.00055 | −0.00160 |
| S3 | 8 | no | −0.00011 | +0.00066 | −0.00077 |
| S4 | 11 | no | −0.00055 | +0.00072 | −0.00127 |
| S5 | 13 | no | 0.00000 | −0.00011 | +0.00011 |
| **S6** | **14** | **yes (logical_X)** | **+0.11431** | **+0.11597** | **−0.00166** |

The five off-logical edges cost essentially nothing to forget (mean **−0.0004 pp**;
slightly *negative*, i.e. the full record is occasionally wrong where the thin skin is
right — "agreement ≠ correctness," as in all earlier stages). The single edge whose lost
qubit lies on a logical operator costs **0.114 pp — about 109× the off-logical
magnitude.** So at fixed endpoint degree the cost of forgetting is governed by **whether
the lost edge carries logical information**, not by local vertex degree. (`S6` is the
*only* one of all 18 eligible edges, across all three patches, that lies on a logical
support.)

The two aperiodic patches — whose eligible edges span degree pairs `(3,4)…(4,6)` but
**none** of which lie on a logical — occupy a much narrower band:

| | range of thick − thin (pp) | range of diamond − thin (pp) |
|---|---|---|
| AB (6 edges) | −0.0003 … **+0.00698** | −0.0009 … +0.00414 |
| Penrose (6 edges) | **−0.00199** … +0.00591 | −0.00243 … +0.00309 |

That entire aperiodic spread (~0.009 pp) is **an order of magnitude below** the
on-logical effect. Within it there is a weak, correlated gradient — the costliest
aperiodic edges are the higher-degree-sum ones (AB `A4` = `(4,6)`, `+0.0070`; Penrose
`P1` = `(4,5)`, `+0.0059`), and edges sitting on the smooth boundary tend lowest or
slightly negative (Penrose `P2`, `−0.0020`) — but with six correlated sites per patch
this is a hint, not a fitted effect (see scope).

Disagreement-with-thick and posterior-difference-from-thick (reported separately in the
table) track the same ordering: the thin skin disagrees with the full record most at
`S6` and the higher-degree aperiodic edges, and most of that disagreement the diamond
closes.

## Where do the eight old readings recover that cost?

**Everywhere.** The `diamond − thin` column essentially equals `thick − thin` at every
edge, so `thick − diamond` — the part of the archive the local bracket fails to recover —
is tiny (|·| ≤ **0.003 pp** at all 18 sites, and **−0.0017 pp at the big `S6`**, i.e. the
diamond matches the full record there to within noise). The bracket draws on a
site-independent sparse archive of **at most 8 stored events** before the report and
reads its **8** values after it arrives. Eight readings at the four incident checks are a
faithful stand-in for the whole archive across every tested geometry — and at the one
edge where forgetting actually costs something, they recover all of it.

## B. Record ambiguity and decoder ties

The fraction of evaluation weight in groups sharing an exact full detector record but
carrying both scored truths is small and roughly flat across sites — **~0.006–0.009**
(lowest on smooth-boundary edges, highest at `S6` = 0.00863 and the higher-degree
aperiodic edges), an **observed lower bound** under k=2 sampling. Per-arm weighted tie
rates are tiny everywhere (thick ~1.5–2.0×10⁻⁴). As in the earlier audit, record
ambiguity exists without the decoder sitting at 50/50: the full record expresses a
confident preference on most same-record pairs. So the archive's edge at `S6` is **real
re-judgment**, not tie-breaking.

## C. Cap sensitivity — (3,3) vs (4,3) vs (3,4) vs (4,4)

Two panels, because the first was uninformative and saying so matters (this is exactly the
pitfall the d=5 paired-cap audit flagged — never claim cap-robustness from a panel that
contains no discriminating history).

**(i) Frozen seeded panel — a prefix-coverage check only.** The pre-registered seeded
panel (per site: k=0 + seeded k=1 + seeded k=2, ×8 = 120 histories; 2,160 across the 18
sites) was replayed at all four caps via the audited chunked builder (which reproduces the
stock decoder at `(3,3)`, 0 mismatches). Every arm agreed on every panel history, so every
paired benefit is **identically 0 at every cap**, and `prefix_absent = 0` at every cap.
This confirms **full frame-prefix coverage** (no fallback zeros on typical histories at
`w_frame=3`) but, having no arm-discriminating history, it provides **no test of the
benefits' cap-sensitivity**. `results/caps.json`. (Deviation from the §4 "exhaustive k≤1"
wording: the panel used a seeded k=1 subset for `w=4` feasibility; it is superseded below.)

**(ii) Discriminator panel — the real cap test.** For the signal-carrying edges we
collected, at `(3,3)`, **every** history on which the four arms disagree (the only
histories that carry any paired benefit) and re-decoded exactly those at all four caps.
Reconstructing the benefit from the discriminators (true weights / full `W`) reproduces the
primary `(3,3)` benefit to ≤0.002 pp — a built-in check — and its movement at higher caps
is the actual cap-sensitivity:

| edge | discrim. histories | thick − thin across (3,3)/(4,3)/(3,4)/(4,4) (pp) | span | diamond − thin | label flips vs (3,3) |
|---|---:|---|---:|---|---:|
| **square_e18** (on-logical) | 692 | +0.1166 / +0.1159 / +0.1170 / +0.1163 | **0.0011** | +0.1159 → +0.1155 (flat) | 0 / 18 / 83 / 102 |
| AB_e22 (off-logical) | 145 | +0.0041 / +0.0034 / +0.0038 / +0.0032 | 0.0009 | +0.00116 (flat) | 0 / 32 / 4 / 36 |
| Penrose_e2 (off-logical) | 101 | −0.0010 / −0.0007 / −0.0009 / −0.0006 | 0.0004 | ~0 | 0 / 24 / 18 / 34 |

**The archive benefit is cap-stable.** At the on-logical `square_e18` — where the whole
signal lives — thick−thin moves by **<0.0011 pp (<1% of its 0.116 pp value)** across all
four caps; the label flips grow with the caps but **cancel in the net benefit**, and
`diamond−thin` is equally flat. No edge changes the **sign** of any benefit at any cap.

This is the **opposite** of the d=5 diagnostic-panel finding (where raising `w_frame` let
the thin decoder catch up and collapsed the margin): here raising the caps does **not**
erase the advantage, because the patch benefit is a genuine **on-logical, distance-limited**
effect, not a bounded-decoder artifact. The faint d=5-style "richer frame lets thin catch
up" drift is visible **only** at the tiny off-logical benefits (AB_e22 loses ~¼ of its
0.004 pp as `w_frame`→4) and is negligible in absolute terms. `results/caps_discriminator.json`.

## Plain-language answer

**When you move your finger across each patch, where does the cost of forgetting
change?** Almost nowhere — and then enormously at one spot. Across most edges the thin
skin plus its committed frame is as good as the full record (sometimes a hair better).
The cost jumps ~100× only at the edge whose lost qubit lies on a logical operator. On the
square, with every endpoint degree held at `(4,4)`, that single on-logical edge is the
whole signal — so **the cost of forgetting is set by logical incidence, not by how many
tiles meet at the edge's ends.** The aperiodic degree variety (3–6) moves it by at most a
tenth of that.

**Where do eight old readings recover that cost?** Everywhere, including the expensive
on-logical edge: the four incident checks read at the two onset rounds recover
essentially the entire archive advantage (the full record buys ≤0.003 pp beyond them).
The local onset-lip bracket is sufficient on all 18 tested geometries.

**Which observation deserves a test on fresh patches?** The logical-incidence effect —
that the cost of forgetting concentrates on loss edges overlapping a logical operator and
dwarfs any endpoint-degree effect. These three patches contain only **one** on-logical
eligible edge (in the square), so the large effect rests on a single site; and the six
edges per patch are correlated and selection-enriched (geometry handback). Confirming it
needs independent patches with several on- and off-logical edges, holding boundary
proximity fixed, before logical incidence can be called a predictor — and the
perpendicular-space predictor stays reserved for those independent cuts.

## Scope

Bounded decoder `(w_frame,w_dec)=(3,3)` on a bounded `≤2`-ordinary-fault ensemble (k=2
sampled); three single patches at distance `(3,3)`; the square control is newly built
under the edge-qubit convention, not the earlier rotated square. Individual edges are
preserved throughout; sites are never pooled by degree. Reference agreement is kept
distinct from truth. No perpendicular-space prediction is claimed here.

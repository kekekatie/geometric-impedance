# Pass 2 handback — k=3 sample, stress panel, cap sensitivity

2026-11-16. Executes the frozen `PROTOCOL_PASS2.md` (commit `ecb7113`; cap-panel
reduction Amendment A in `ee0c23d`). Starts from Pass 1 `f278297`; same d=5 bulk
site (2,2), noise, deadline, four arms.

- Protocol commit: `ecb7113` (+ Amendment A `ee0c23d`)
- Results commits: primary `0920b2b`, stress `ee0c23d`, caps + this handback: see final commit
- Replay: `cd src && python3 pass2.py primary && python3 pass2.py stress && python3 pass2.py caps && ...`

## Headline

**k=3 does not overturn the collapse, but it stops it from looking like it goes to
zero.** The within-k=3 archive advantage over the thin record is small (0.234 pp,
95% CI [0.168, 0.301] pp — below Sol's 0.4 pp benchmark) yet clearly positive and
**non-monotonic**: it is *larger* than k=2 (0.049 pp), reversing Pass 1's
decreasing trend. Combining exact k≤2 with the k=3 sample lifts the combined k≤3
thick−thin margin from 2.32×10⁻⁵ to **3.68×10⁻⁵** (CI [3.29, 4.07]×10⁻⁵) — k=3
adds ~59%. Still ~0.0037% absolute (an ~80× collapse from d=3's 0.29%), so the
headline holds, but the archive's advantage does **not** vanish with fault order;
higher-order faults partially restore it, and unlike k≤2 the k=3 advantage is
**decisive** (real wins, not 50/50 ties). Untested residual: P(k≥4) = 0.000574.

## (i) Random k=3 sample — 25,000 triples, 200,000 histories, (w_frame,w_dec)=(3,3)

Sample sha256 `34aa495f…b14ffb88`, seed 20261116; cluster bootstrap over the 25,000
triples (8 histories/triple = one group), B=10,000, boot seed 20261117.

| quantity | tie-aware | hard |
|---|---:|---:|
| within-k=3 **thick − thin** | **0.002342**  CI [0.001675, 0.003008] | 0.002200  CI [0.001135, 0.003270] |
| within-k=3 **diamond − thin** | 0.001335  CI [0.001020, 0.001665] | 0.001240  CI [0.000895, 0.001605] |
| cluster SE (thick−thin) | 0.000338 | — |

Per-arm within-k=3 truth: thick 0.972803, diamond 0.971795, thin 0.970460,
whole 0.972803. Tie weight fraction: thick 0.01608, thin 0.01050, diamond 0.01009.
`whole` vs `thick`: **0** label disagreements, **0** posterior disagreements.

Paired `thick vs thin` (fraction of the k=3 sample): only-thick-right **0.00215**,
only-thin-right **0.00020** (≈10:1 decisive archive wins — *not* ties), tie-involved
0.01690, net 0.00274. So at k=3 the archive's edge is real decisions, unlike the
all-ties character at k≤2. The diamond bracket recovers ~57% of the k=3 archive
advantage (0.134 of 0.234 pp).

**Combined over k≤3** (model weights π=[0.691003, 0.255927, 0.047266, 0.005804];
k≤2 exact from Pass 1, k=3 from this sample):

| | within-stratum thick−thin (tie-aware) |
|---|---:|
| k=0 | 0 |
| k=1 | −0.0000000 |
| k=2 | 0.000491 |
| k=3 | **0.002342** (CI [0.001675, 0.003008]) |
| **combined k≤3** | **3.68×10⁻⁵** (CI [3.29, 4.07]×10⁻⁵) |
| benchmark (0.4 pp within-k=3) | 2.32×10⁻⁵ |
| **P(k≥4), untested** | **0.000574** |

Benchmark verdict: the within-k=3 CI lies entirely below the 0.4 pp line, so k=3
will not add as much as the whole existing gap — but it is detectably positive and
raises the combined margin ~59%, so it is **not negligible**, and the non-monotonic
rise (k=2 → k=3) means "collapse → 0" would be the wrong extrapolation.

## (ii) Stress panel — near-loss census + empirical seam scan

Near-loss = all weight-1 and weight-2 ordinary faults on the 3×3 loss neighbourhood
(110 primitives), 48,840 histories.

| arm | tie-aware truth |
|---|---:|
| thick | 0.997707 |
| whole | 0.997707 |
| diamond | 0.997707 |
| thin | 0.997215 |

In the neighbourhood the **diamond bracket exactly equals thick** (local skin fully
recovers the archive); thin lags 0.049 pp. **Empirical seam scan: 0 ties, 0
same-record-opposite-truth groups** over 39,511 record-groups. So the d=5 seams are
**not local** to the loss: the minimum (2,2)-crossing logical is weight **5** (16
representatives per sector), so a same-record ambiguity needs ≥ weight-4 ordinary
support — the k≤2 thick-ties seen globally (5,408 in the full d=5 ensemble, Pass 1)
come from *delocalized* weight-2 configurations, not the loss neighbourhood. A
useful negative result: the ambiguity that erodes the archive's authority lives in
the code at large, not around the missing tile.

## (iii) Cap sensitivity — (3,3) vs (4,3) vs (3,4) [+ (4,4)]

_Pending the cap run; filled on completion._

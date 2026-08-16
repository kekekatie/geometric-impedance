# Pre-registered prediction: address fragility on the rank-4 family

**Recorded before the run.** Nothing below may be edited after the first result is
seen; corrections go in a separate section appended at the bottom, dated.

The previous headline was measured on a family since shown to be structurally
unmatched — the 10-fold member was not a tiling (664 crossing edges, Euler −682) and
the stars were amputated for 10- and 12-fold. That result is UNDETERMINED. The rank-4
congruence family (`RANK4_FAMILY.md`) fixes all of it: rank 4, perpendicular dimension
2, complete N-fold star, genuine rhombus tilings, validated exactly against Penrose.

## The two live hypotheses make different predictions

I said in conversation that field and fragmentation were perfectly confounded here.
That was too pessimistic, and measuring the windows showed why.

*(Numbers below corrected 2026-08-16 before any result was seen — see the amendment
at the foot of this file. The superseded sampled estimates were 1.6706 / 1.8412 /
2.0202.)*

Exact window geometry, computed by slicing the zonotope rather than hulling sampled
points (`window_geometry.py`):

| | pieces | piece shapes | window area | perimeter | perimeter/area |
|---|---|---|---|---|---|
| 8-fold silver | 1 | octagon | 4.8284 | 8.0000 | **1.6569** |
| 10-fold golden | 5 | pentagons, decagons | 17.2048 | 30.7768 | **1.7889** |
| 12-fold platinum | 9 | hexagons, 9-gons, 12-gons | 33.5885 | 62.3538 | **1.8564** |

Silver's window comes out at area 2 + 2√2 and perimeter exactly 8, the analytic
Ammann-Beenker octagon, which is a good check on the machinery.

Perimeter-to-area is monotone in the number of pieces. So:

**H1 — field.** Fragility is set by the cyclotomic field, and the previous ordering
replicates:

> **silver > platinum > golden**

**H2 — fragmentation.** Fragility is set by how finely the arithmetic cuts the window.
More window boundary per unit area means more of the point set sits near an edge and
is exchangeable under perturbation:

> **silver > golden > platinum**

**H0 — null.** No ordering survives damage-matching, or the spread is within seed
noise.

**H1 and H2 agree that silver is most robust and disagree on golden versus platinum.
That single comparison is the discriminating test.** Silver-first is therefore *not*
evidence for either; only the golden/platinum contrast counts.

**Refinement forced by the exact numbers.** The covariate is not evenly spaced. Silver
sits 8.0% below golden in perimeter/area, while golden sits only 3.8% below platinum.
If H2 is right and perimeter/area is the driver, then the golden-to-platinum fragility
gap should be roughly **half** the silver-to-golden gap, not equal to it. That is a
sharper prediction than a bare ordering, and it cuts both ways: it means the
discriminating contrast is a small one, and a golden/platinum difference inside seed
noise is a genuinely possible outcome that supports neither hypothesis. If the observed
golden-to-platinum gap is instead *larger* than the silver-to-golden gap, that fits
neither H1 nor H2 as stated and should be reported as such rather than rounded toward
whichever ordering it resembles.

## Which I expect, and why

**Modest lean to H2**, roughly 45 / 35 / 20 across H2 / H1 / H0. Stated so it can be
scored, not because the number is precise.

For H2: perimeter/area is monotone, mechanistically direct, and computable in advance
from the window alone. And platinum's middle position in the old result came from a
substrate with only 4 of its 6 star directions.

For H1: golden's fragility is *independently* established through Penrose in the
confirmed dose-response result, and Penrose is a genuine member of this family — the
singular 10-fold one. So golden being fragile is not an artefact of the broken
substrate, and H1 remains well supported.

Against both: the old 12-fold *was* a valid tiling (it was 10-fold that broke), so the
old platinum number is not junk, merely measured with an amputated star.

## Protocol, fixed in advance

- **Substrates**: `generate_rank4.generate(N, ...)` for N = 8, 10, 12, default offset,
  default extra offset, `build_edges(lifts, N, ustar)`.
- **Scale matching**: extents chosen so the *active-set count* matches across the three,
  not the extent and not the raw patch size. Active set is the innermost vertices by
  distance from the patch centroid.
- **Bulk crop**: active set no more than 40% of the patch, to stay inside the bulk
  regime established in `BOUNDARY_SENSITIVITY.md`.
- **Labels**: `matched_rate_labels(..., fraction=0.05)`, so positive rates match by
  construction.
- **Features**: the two Galois perpendicular coordinates plus their radius. Identical
  across all three families — now genuinely so, since perpendicular dimension is 2 for
  all of them. The congruence class is **excluded** from the headline feature set.
- **Model**: `HistGradientBoostingClassifier(max_iter=200)`, 3-fold stratified CV, AUC.
- **Damage**: flipped-vertex fraction against the clean patch of the same N. All
  comparisons read against **measured damage**, never nominal disorder amplitude.
- **Seeds**: at least 3 per point; report mean and standard deviation.
- **Null**: shuffle null at every point, expected near 0.5.

## Subsidiary predictions

1. **Clean channel high for all three** — AUC ≥ 0.95 at zero disorder for each. If
   platinum comes in far lower, as it did at 0.75 in the Z^m family, that is a separate
   finding about the substrate and must be reported before any ordering is discussed.
2. **The congruence class is inert** — measured separately, AUC ≤ 0.60 at zero disorder
   for golden and platinum, matching Penrose's 0.5398. If the class is *not* inert, the
   headline feature set is not the whole address and the whole comparison needs
   revisiting.
3. **Damage per unit disorder amplitude orders with perimeter/area** — silver takes the
   least damage at a given amplitude, platinum the most. This is a prediction about the
   *x*-axis, not the result, and it is exactly why damage-matching is required.

## What would count as a failure of the whole programme

- Orderings that do not survive damage-matching, or that flip between seeds.
- Silver not most robust, which neither hypothesis allows.
- The congruence class carrying substantial address information.

## Scoring

Write the result into `RANK4_HEADLINE.md` and state plainly which of H1, H2, H0 it
supports, before any interpretation. If it supports H2, the paper's central claim
changes from the field to window fragmentation, and the field becomes the thing that
*determines* the fragmentation rather than the proximate cause.

Either way, φ(N) = 4 has exactly three members, so a single family cannot carry this
alone. Confirmation needs φ(N) = 6, where there are more members and the class counts
need not track the fields monotonically.

---

## Amendment, 2026-08-16 — before any result was seen

Two corrections, both to substrate facts rather than to the hypotheses. The
hypotheses, the discriminating contrast, the credences and the protocol are unchanged
from the original commit.

**1. Patch saturation bug.** `_extra_positions` swept the preimage offset `z` over a
fixed absolute range. Because the extra functional `u = Kn` grows linearly with
distance from the origin, that range stops containing the relevant preimage beyond
some radius, and the patch silently stops growing. Caught by a scale probe: the 12-fold
patch returned exactly 561 vertices at extents 22, 26 and 30. Fixed by reducing `u`
into its symmetric residue range per point and searching only immediate neighbours.
Patches now grow properly (12-fold: 2074 / 3658 / 5673 at extents 12 / 16 / 20) and
about seventeen times faster.

Re-audited on corrected patches — all three remain perfect rhombus tilings:

| N | vertices | edges | mean degree | crossings | quads | Euler | rhombi | classes |
|---|---|---|---|---|---|---|---|---|
| 8 | 3357 | 6600 | 3.932 | 0 | 100.00% | 2 | 2 | 1 |
| 10 | 3194 | 6238 | 3.906 | 0 | 100.00% | 2 | 2 | 5 |
| 12 | 3658 | 7152 | 3.910 | 0 | 100.00% | 2 | 3 | 9 |

**2. Window geometry now exact.** The first measurement hulled sampled perpendicular
coordinates. That underestimates area and perimeter unevenly — silver's single window
drew thousands of samples while each of platinum's nine pieces drew a few hundred — and
the bias inflates perimeter/area for the more fragmented members, which is precisely
the direction that would manufacture support for H2. Replaced with exact zonotope
slicing in `window_geometry.py`. The ordering survives; the golden-to-platinum gap
narrows from 9.7% to 3.8%, which is why the refinement above was added.

**Patch sizes for the run.** 8-fold reaches ~3400 vertices at extent 14, 10-fold ~3200
at extent 16, 12-fold ~3700 at extent 16. Extents will be tuned so the *active-set
count* matches at 1200, comfortably inside the 40% bulk-crop limit for all three.

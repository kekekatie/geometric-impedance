# The rank-4 congruence-window family

The substrate family that is matched on every axis at once. Built after both
earlier families failed, each on a different requirement.

## Why the earlier families failed

**Z⁴ cyclotomic.** Matched perpendicular dimension, but the edge rule "differ by one
basis vector" is basis-dependent. It spans the complete octagonal star only because
ζ₈⁴ = −1; it amputates one of five decagonal directions and two of six dodecagonal
ones. The 10-fold member is not a tiling at all — 664 crossing edges, Euler −682.
→ `TILING_CONFOUND.md`

**Z^m canonical.** Complete stars, proper tilings, but the extra perpendicular
coordinates are not inert (AUC 0.7937 and 0.6169 at zero disorder against a shuffle
null near 0.49), so perpendicular dimension genuinely differs.
→ `GALOIS_BLOCK_RESULT.md`

## The construction

The extra dimensions were never real. Z[ζ_N] has rank 4 for N = 8, 10, 12. The star
has m = N/2 directions, and the relation lattice K = ker(Z^m → Z[ζ_N]) has rank m − 4,
spanned by shifts of the cyclotomic polynomial's coefficients:

| N | Φ_N | m | K | classes |
|---|---|---|---|---|
| 8 | x⁴ + 1 | 4 | rank 0 (degree exceeds m) | **1** |
| 10 | x⁴ − x³ + x² − x + 1 | 5 | rank 1, (1,−1,1,−1,1) | **5** |
| 12 | x⁴ − x² + 1 | 6 | rank 2, (1,0,−1,0,1) and its shift | **9** |

K is orthogonal to both the parallel plane and the Galois-conjugate plane, so a
lattice point's "extra" perpendicular coordinates are fixed by its class modulo K.
They are a **finite label, not a continuum.** The acceptance window is therefore a
union of pieces in a 2-dimensional perpendicular space, indexed by a congruence class
of the rank-4 point — which is what Penrose's four pentagons have always been.

Class count is `det Gram(K)`: 1, 5, 9. All classes are occupied in every patch built.

## Two corrections found while building it

**Boundary ties.** The zonotope's extent along each extra direction *exactly* equals
the spacing between successive preimages of the same rank-4 point — measured ratio
1.0000 for N = 10 and for both directions of N = 12. With a closed window and no
offset there, points sitting on a slice boundary are accepted twice. A generic offset
along the extra directions removes every tie; the generator now asserts that no point
is accepted by two preimages.

**The edge rule needs the preimage check.** A rank-4 step by ζ^k is necessary but not
sufficient: two accepted points can differ by ζ^k while their accepted preimages in
Z^m differ by e_k *plus a kernel element*, which is not an edge of the tiling. The
extra functional u = Kn must advance by exactly K e_k. Without this the 12-fold graph
carried spurious edges and mean degree 4.736, impossible for a quadrangulation, which
must sit at or just below 4.

## Audit

| N | vertices | edges | mean degree | crossings | quads | Euler | rhombi | classes |
|---|---|---|---|---|---|---|---|---|
| 8 | 1757 | 3432 | 3.907 | **0** | 100.00% | 2 | 2 (45°, 90°) | 1 |
| 10 | 954 | 1810 | 3.795 | **0** | 100.00% | 2 | 2 (36°, 72°) | 5 |
| 12 | 561 | 1047 | 3.733 | **0** | 100.00% | 2 | 3 (30°, 60°, 90°) | 9 |

All three are genuine rhombus tilings with the complete N-fold star, at rank 4 and
perpendicular dimension 2.

## Validation against Penrose — PASS

`validate_rank4_penrose.py`. The rank-4 identities for the Penrose convention are

    a_k = n_k − n_4                     rank-4 coordinates
    Σa = j − 5n_4 ≡ j (mod 5)           index sum is a congruence class
    n·PERP = a·PERP[:4]                 since Σ PERP = 0

giving the acceptance test *accept a iff Σa mod 5 ∈ {1,2,3,4} and perp(a) ∈ window[c]*,
with star e₀, e₁, e₂, e₃, −(1,1,1,1) — the last being the image of the Z⁵ step e₄.

Compared against `generate_penrose.py`, itself verified against the published
substrate, inside a radius both patches fully cover:

```
comparison radius: 14.988
  Z^5   -> rank 4 : 872 points        rank-4 direct : 872 points
  only in Z^5     : 0                 only in rank-4: 0
  edges in Z^5    : 1677              edges in rank-4: 1677
  edge difference : 0
```

Exact, vertices and edges alike. **Penrose was always a rank-4, perpendicular-
dimension-2 cut-and-project.** The fifth dimension is bookkeeping.

## What is now matched, and what varies

Held fixed: lattice rank 4; perpendicular dimension 2; the complete N-fold star, so
the edge rule is basis-independent; genuine rhombus tilings; window derived from the
projected m-cube by the same rule.

Varying: the cyclotomic field, and with it the number of window pieces — 1, 5, 9.

The number of pieces is therefore a **mechanism variable forced by the arithmetic**
rather than imposed by hand. That is the "lattice-commensurate window fragmentation"
lead, flagged in `LEADS.md` as the only fragmentation that does not destroy a tiling
because it cuts along a lattice invariant rather than across one. It arrived on its
own, which is worth more than finding it by searching for it.

It also means field and fragmentation are still **perfectly confounded** across these
three members — 1, 5, 9 pieces map one-to-one onto silver, golden, platinum. This
family cannot separate them either. Separating them needs members where the two
disagree, which the φ(N)=4 family cannot supply, since it has exactly three members.
Recorded now so it is not discovered later.

## Note on genericity — SUPERSEDED, see RANK4_HEADLINE.md

The general-N generator uses a generic offset along the extra directions, so its
10-fold member occupies all 5 classes. Penrose proper is the *singular* member, with
class 0 empty and four pentagons.

**The claim originally made here — that the generic member "avoids degenerate
configurations and is the better default" — is wrong, and was shown wrong by the
headline run.** The offset does not avoid degenerate configurations, it creates them:
slicing the zonotope at arbitrary levels yields near-degenerate slivers (52 points in
one 10-fold class) and strongly heterogeneous local environments (12-fold class mean
degrees from 3.49 to 4.84). That makes the congruence class predict vertex degree and
hence retention, so the class stops being inert — it reads 0.8230 for generic 10-fold
against 0.5210 for singular Penrose.

The singular convention takes the natural window sections and gives balanced pieces.
The correct way to break the exact ties documented above is a deterministic half-open
window rule, not a jitter that moves the cut. Class occupancy and per-class degree
homogeneity should be acceptance criteria for the substrate before any address
measurement is taken.

The validation above reproduces the singular Penrose convention exactly, and is
unaffected.

## Next

1. Re-run the headline on this family, damage-matched, **direction recorded in git
   before the run**. Genuine risk to the result.
2. Recovery, using `phason_flips.py` — now applicable, since all three are proper
   rhombus tilings.

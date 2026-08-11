# What in the address layer resists localisation? Not quasiperiodicity.

The multiplex run showed a perpendicular-space potential localising transport far
less than the same weights shuffled, and that was read as quasiperiodic order
resisting localisation. A shuffle null only excludes *random*, so this tests four
potentials carrying an **identical multiset of values**, differing only in how
those values are arranged over the vertices.

Original AB substrate, 22,663 vertices, 8 sources, 200 steps, random replicated
over 5 permutations. Run with `python3 localisation_mechanism.py`.

## Localisation relative to random at matched sigma (lower = resists more)

| sigma | quasiperiodic | smooth (radial) | periodic (10 osc.) |
|---|---|---|---|
| 1.50 | 0.984 | 0.979 | 1.035 |
| 1.00 | 0.919 | 0.882 | 1.200 |
| 0.70 | 0.708 | 0.622 | 1.537 |
| 0.50 | 0.325 | 0.240 | 1.487 |

The quasiperiodic field does resist localisation — but **a plain smooth radial
ramp resists it more**, at every sigma. Quasiperiodicity is not the ingredient.

## The periodic comparison is entirely wavelength-dependent

At sigma 0.50, varying only the period of the cosine field:

| oscillations across patch | wavelength | localisation vs random |
|---|---|---|
| 3 | 57.1 | **0.180** |
| 6 | 28.5 | 0.552 |
| 10 | 17.1 | 1.599 |
| 20 | 8.6 | 2.625 |
| 40 | 4.3 | 1.548 |

Quasiperiodic sits at 0.349. A periodic potential beats it at long wavelength and
loses badly at short wavelength, spanning 0.18 to 2.63 across the sweep. The
earlier statement that a periodic potential localises *more* than a random one was
an artefact of one arbitrary wavelength choice.

## Conclusion

**The effect is spatial correlation length, not quasiperiodic order.** Smooth or
long-wavelength potentials leave transport alone; short-wavelength and random
potentials dam it. The perpendicular-radius field lands wherever its effective
correlation scale puts it — between the two, and beaten by both a radial ramp and
a three-oscillation cosine.

The original measurement stands: perp_r as a potential localises transport about
three times less than the same values randomly permuted. What does not stand is
the interpretation. That result says the address field is *not random*, which is
true of essentially any structured field, and carries no information about
quasiperiodicity. The Aubry-André reading in `MULTIPLEX_FINDINGS.md` should be
withdrawn.

## The null that would actually settle it

Compare the quasiperiodic field against a surrogate with the **same spatial power
spectrum but randomised phases**. That holds the two-point correlation structure
fixed — the thing shown here to drive the whole effect — and varies only the
higher-order structure that makes a field quasiperiodic rather than merely
correlated. If the quasiperiodic field still wins against a phase-randomised
surrogate of itself, the claim is real. Nothing short of that null can support it.

Implementation note: the field lives on an irregular point set, so this needs
interpolation to a grid, phase randomisation there, and resampling back.

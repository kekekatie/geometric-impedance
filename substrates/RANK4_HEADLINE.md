# Result: the headline re-run on the rank-4 family

Protocol and hypotheses fixed in advance in `PREDICTION_rank4_headline.md`. Nothing
below departs from it. Scored first, interpreted second, as that document requires.

## Verdict

**The discriminating test is void, and silver > golden is reconfirmed.**

Not H1, not H2, and not H0 in the interesting sense. The ordering came out
silver > golden > platinum, which is H2's ordering — but it cannot be claimed for H2,
because platinum failed the pre-registered clean-channel check and never had an address
channel to lose. You cannot measure how fast something degrades if it was never intact.

**Two of the three subsidiary predictions failed.** Both failures are more informative
than the headline.

## The curves

Damage is flipped-vertex fraction against the clean patch of the same family. Active
set 1200 vertices for all three (35.7% / 37.6% / 32.8% of patch), 3 seeds.

| damage | silver | golden | platinum | s−g gap | g−p gap | g−p / s−g |
|---|---|---|---|---|---|---|
| 0.05 | 0.9808 | 0.8784 | 0.6366 | 0.1024 | 0.2418 | **2.36** |
| 0.10 | 0.9615 | 0.8377 | 0.5894 | 0.1239 | 0.2483 | **2.00** |
| 0.15 | 0.9656 | 0.7652 | 0.5780 | 0.2003 | 0.1872 | 0.93 |
| 0.20 | 0.9305 | 0.7280 | 0.6006 | 0.2024 | 0.1274 | 0.63 |
| 0.25 | 0.9172 | 0.6648 | 0.5706 | 0.2524 | 0.0942 | 0.37 |

Shuffle nulls sat between 0.43 and 0.53 everywhere.

H2's refinement predicted the golden-to-platinum gap would be **about half** the
silver-to-golden gap. At low damage it is **two to two-and-a-half times larger**. The
prediction document anticipated this exact case: *"If the observed golden-to-platinum
gap is instead larger than the silver-to-golden gap, that fits neither H1 nor H2 as
stated and should be reported as such rather than rounded toward whichever ordering it
resembles."* So it is reported as such. The apparent convergence toward the predicted
ratio at high damage is not support — it is both curves arriving at the floor.

## Failed subsidiary prediction 1: platinum has no clean channel

Predicted AUC ≥ 0.95 at zero disorder for all three. Observed:

| | clean AUC | shuffle |
|---|---|---|
| silver | 0.9635 | 0.497 |
| golden | 0.9588 | 0.450 |
| platinum | **0.6658** | 0.461 |

Platinum's whole curve then runs 0.666 → 0.544 across the full damage range, mostly
inside its own seed noise (±0.03 to ±0.08). It is flat because it is at the floor, not
because it is robust.

This is **not** the old tiling breakage recurring. The 12-fold substrate is sound:
3658 vertices, zero edge crossings, 100% quadrilateral faces, Euler characteristic 2,
mean degree 3.910, complete six-line star. The tiling is fine; the *address channel* is
what is missing.

It is also the **second** time 12-fold has come in weak, under two independent
constructions — 0.7307 in the Z^m family, 0.6658 here. Twice, under different lattices,
different windows and different edge rules, starts to look like a property of the
12-fold substrate rather than a bug in either generator.

## Failed subsidiary prediction 2: the congruence class is not inert

Predicted class AUC ≤ 0.60 at zero disorder, matching Penrose's reported 0.5398.
Observed at zero disorder: **golden 0.8230**, **platinum 0.6619**.

Worse, for platinum the class label **beats the continuous address** at nearly every
damage level:

| damage | platinum address (2D Galois) | platinum class |
|---|---|---|
| 0.000 | 0.6658 | 0.6619 |
| 0.083 | 0.6019 | 0.5988 |
| 0.122 | 0.5734 | **0.6520** |
| 0.163 | 0.5801 | **0.6775** |
| 0.210 | 0.6060 | **0.6876** |
| 0.253 | 0.5680 | **0.6936** |

A discrete 9-valued label carries more address information than the two continuous
coordinates it was assumed to be secondary to — and unlike the continuous channel, it
does not decay.

This contradicts `discrete_vs_continuous.py`, which concluded Penrose's discrete
component was inert and which has been cited repeatedly, including as the justification
for treating the rank-4 reinterpretation as safe. `class_inertness.py` re-tests singular
Penrose, generic 10-fold and generic 12-fold under one identical protocol to determine
whether the substrates genuinely differ or the earlier test was underpowered.

## What this suggests about platinum — a hypothesis, not a result

With nine window pieces the pieces are small, so *which* piece a point falls in may
carry more information than *where* in the piece it falls. If so, the 12-fold address is
mostly discrete, the pre-registered feature set was simply the wrong one for platinum,
and the family is not comparable on a feature set chosen for silver.

That is testable and cheap — measure the address with the class included, for all
three — and it is exactly what `class_inertness.py` reports. It should be run before any
further interpretation of platinum.

## Scoring my own prediction

I recorded 45 / 35 / 20 across H2 / H1 / H0 and a modest lean to fragmentation. The
ordering matched H2 and the quantitative refinement did not, and the reason both
happened is a possibility I did not put on the list at all: that the substrate would
fail the measurement rather than pass or fail the hypothesis. Two of three subsidiary
predictions failed. The lean was not vindicated, and the ordering agreeing with it is
the sort of thing that would have been easy to bank had the refinement not been written
down first.

## What survives

**Silver > golden at matched damage, on a validated substrate family.** Solid at every
damage level, well clear of seed noise and of the shuffle null, on genuine rhombus
tilings with complete stars at matched rank and perpendicular dimension. That is the
core of the original result and it now rests on substrates that survive audit.

**Field versus fragmentation remains open.** The contrast that would have settled it is
unusable until platinum's address channel is understood.

## Next

1. `class_inertness.py` — running. Settles the contradiction and tests the discrete-
   address hypothesis for platinum.
2. Diagnose platinum's channel before anything else. φ(N) = 6 is premature while a
   member of φ(N) = 4 cannot be measured.
3. The secondary damage model (full perpendicular jitter, allowing class flips) is
   implemented and unrun. It is more relevant now than when it was written, since the
   class turns out to be live.

---

## Diagnosis: the failure was my choice of extra offset, not the 12-fold substrate

`class_inertness.py`, same protocol for all three, active set 1200:

| substrate | vertices | CLASS | perp 2D | both |
|---|---|---|---|---|
| Penrose (singular, Z⁵) | 6705 | **0.5210** | 0.9244 | 0.9233 |
| rank-4 10-fold (generic) | 3194 | 0.8230 | 0.9588 | **0.9964** |
| rank-4 12-fold (generic) | 3658 | 0.6619 | 0.6658 | **0.8579** |

**The old finding stands.** Singular Penrose's class reads 0.5210, matching the 0.5398
reported by `discrete_vs_continuous.py`. That result was not underpowered and does not
need correcting. It is the *generic* members whose class is live.

The mechanical check identifies why. Class occupancy and mean degree per class:

| substrate | class sizes | mean degree range |
|---|---|---|
| Penrose (singular) | 953 / 2418 / 2441 / 893 | 3.54 – 4.13 |
| 10-fold (generic) | 1280 / 940 / **196** / **52** / 726 | 3.44 – 4.20 |
| 12-fold (generic) | 898 / 572 / 409 / 549 / 294 / 179 / 431 / 207 / **119** | 3.49 – **4.84** |

Singular Penrose's four pentagons are balanced and their local environments similar.
The generic members carry near-degenerate slivers — 52 points in one 10-fold class — and
strongly heterogeneous local environments, with one 12-fold class at mean degree 4.84
against 3.49 for another. So the class predicts degree, degree predicts retention, and
the class becomes informative. Exactly the mechanical explanation the script was written
to check for, and it is the one that fits.

**This is a property of the extra offset, not of the arithmetic.** `EXTRA_OFFSET =
(0.0731, 0.0517)` decides where the slices fall and therefore how large each piece is.
I introduced it to break the exact ties documented in `RANK4_FAMILY.md`, and justified
it in that file on the grounds that "the generic one avoids degenerate configurations
and is the better default."

**That was backwards.** The offset does not avoid degenerate configurations, it creates
them: it slices the zonotope at arbitrary levels and produces slivers. The singular
convention — the one Penrose actually uses — takes the natural sections, which is why
its pieces are balanced. The correct fix is a deterministic half-open window rule to
break the ties, not a jitter that moves the cut.

So platinum's "missing address channel" was an artefact of excluding a live feature: with
the class included it reads **0.8579**, not 0.6658. Its address is largely discrete, and
the pre-registered feature set was chosen on silver, where no class exists at all.

### What this does and does not change

It does **not** rescue the discriminating contrast. The comparison still ran on
substrates whose class structure was distorted by my offset, so the golden/platinum
result stays void. It must be re-run on the singular convention.

It does **not** touch silver > golden. Silver has one class and no extra offset, so its
substrate is unaffected; golden's continuous channel alone reads 0.9588 clean, and the
ordering against silver holds throughout.

It does mean **`RANK4_FAMILY.md`'s "note on genericity" is wrong** and is corrected there.

### Revised next steps

1. Rebuild the family on the **singular** convention, with a deterministic half-open
   rule breaking the exact ties. Validate as before: 10-fold must reproduce Penrose's
   four balanced pentagons.
2. Check class occupancy and per-class degree homogeneity as an acceptance criterion for
   the substrate, *before* any address measurement. This should have been an acceptance
   criterion from the start.
3. Re-run the headline. The prediction document stands unamended; this was a substrate
   defect, not a hypothesis revision.

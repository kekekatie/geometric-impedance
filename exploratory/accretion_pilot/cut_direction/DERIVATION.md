# Why "strip direction = 108° − 2 × cut direction"? A derivation sketch

> **Revised after Astra's review (2026-10-15).** The arithmetic core is right, and Astra reproduced it
> independently. Two steps were stated too strongly:
>
> - step 1 is an observation for finite strips, not "by construction";
> - step 4 is about the dominant *family* of the changed region, not one traced ribbon.
>
> The "settled vs built" wording is softened to "predicted early, built later". The text below has
> been updated to match.

*Written with Katie on 2026-10-15, after `cut_direction/` found the rule in all 41 elongated strips.
Numerical checks: [`derivation_check_EXPLORATORY.py`](derivation_check_EXPLORATORY.py) →
[`results/derivation_check_EXPLORATORY.txt`](results/derivation_check_EXPLORATORY.txt).*

The rule comes from four steps. Each is marked by how solid it is:

- **[by construction]** follows from how our code defines things;
- **[geometry]** follows from the shapes involved;
- **[observed]** has been measured, not proven.

## Step 1: a ribbon runs across its own edges [on average by construction; for finite strips, observed]

- A ribbon of family *j* is a chain of tiles glued across edges of direction *j*, like the rungs of a
  ladder. So it runs perpendicular to those edges.
- In our tilings, family *j*'s edges point at 18° + 72°·*j* (`perp_map.edge_dir`). So a family-*j*
  ribbon runs at **108° + 72°·*j*** (mod 180°).
- *Qualified (Astra):* gluing across parallel edges makes a ribbon connected. Its average direction
  is perpendicular, but a finite zigzag segment's fitted axis needn't be exactly perpendicular. A
  bounded-deviation argument would close this. For now the finite strips' agreement is an
  observation: C4 held for 41/41 elongated strips, all within 3°.

## Step 2: the window doubles angles [by construction]

- Every vertex is lifted to five integers K₀…K₄, and stepping along a family-*j* edge changes K_*j* by
  one (`perp_map.lift`).
- Its window address is Σ K_*j* ζ^(2*j*), where ζ is a fifth root of unity (`perp_map.perp`). So a
  family-*j* edge, seen in the window, points along ζ^(2*j*), at angle **144°·*j***.
- In the world, consecutive families are 72° apart. In the window, they are 144° apart. **Angles
  double.**

## Step 3: the window's facets face those same five directions [geometry, checked]

- The window is four pentagons. Every facet of every pentagon faces along one of the five directions
  of ζ^(2*j*) (check (a)).
- A cut can only run along a facet line, so its **normal** always points along some ζ^(2*j*).

## Step 4: the cut faces along ζ^(2*j*) of the changed region's dominant family [observed 45/45; argued, not proven]

- **Observed:** in all 45 distinct situations, the cut's normal lies exactly along ζ^(2*j*) of the
  dominant edge family of the changed region (check (b): deviation 0.000000°). Dominant family means
  the most common family among changed tiles (~2/3 of them); no single ribbon was traced.
- **Why it should be so (de Bruijn's picture):** the five families of ribbons sit on five families of
  parallel grid lines. Where family *j*'s lines fall depends only on how far the hidden offset sits
  along family *j*'s window direction, ζ^(2*j*). So a choice about *where a family-j ribbon goes* can
  only depend on that one component of the offset. In the window, that is a cut perpendicular to
  ζ^(2*j*).
- **What's still missing (broader than first stated):**
  - evidence that one connected ribbon organises the difference (untested);
  - that the difference comes from the initial choice alone, not from later guesses in the 20
    slices (uncontrolled);
  - a proof that a forced-growth choice is always a decision about one ribbon's track.

## Putting it together [arithmetic]

- From steps 2–4, a choice deciding family *j* has its cut line at 90° − 36°·*j*: perpendicular to its
  normal at 144°·*j*, folded mod 180°. So *j* = (90° − cut) / 36°.
- From step 1, the strip runs at 108° + 72°·*j* = 108° + 2·(90° − cut) = **108° − 2 × cut**
  (mod 180°).
- The "−2" is the angle-doubling of step 2, showing through. Check (c): the identity holds exactly, and
  matches the measured strips within 2.6°.

## In plain words

The hidden window and the visible world are two views of the same five families of lines, with
angles doubled between them.

- When a choice is made, the window gets cut across one family's direction. That **predicts** which
  family, and which direction, the later changed strip will have. Whether it *settles* it is the next
  test.
- The world then builds the strip tile by tile, over the following slices, never outrunning the front
  (by construction).
- The window's cut and the world's strip look like one decision seen through the angle-doubling lens.
  That is the hypothesis the next study tests.

## What would make this a proof

1. Show that two options of a forced-growth choice always differ by the track of a single ribbon
   (step 4's missing piece).
2. Write out the pentagrid ↔ window correspondence for our four-pentagon window, with our sign
   conventions.

Both are standard territory in the Penrose literature (de Bruijn 1981). The work would be in matching
our conventions carefully, not in inventing new mathematics.

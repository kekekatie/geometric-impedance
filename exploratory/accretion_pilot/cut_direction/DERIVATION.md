# Why "strip direction = 108° − 2 × cut direction"? A derivation sketch

*Written with Katie on 2026-10-15, after `cut_direction/` found the rule in all 41 elongated strips.
Numerical checks: [`derivation_check_EXPLORATORY.py`](derivation_check_EXPLORATORY.py) →
[`results/derivation_check_EXPLORATORY.txt`](results/derivation_check_EXPLORATORY.txt).*

The rule comes from four steps. Each is marked by how solid it is:

- **[by construction]** follows from how our code defines things;
- **[geometry]** follows from the shapes involved;
- **[observed]** has been measured, not proven.

## Step 1: a ribbon runs across its own edges [by construction, confirmed]

- A ribbon of family *j* is a chain of tiles glued across edges of direction *j*, like the rungs of a
  ladder. So it runs perpendicular to those edges.
- In our tilings, family *j*'s edges point at 18° + 72°·*j* (`perp_map.edge_dir`). So a family-*j*
  ribbon runs at **108° + 72°·*j*** (mod 180°).
- Measured: C4 held for 41/41 elongated strips, all within 3°.

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

## Step 4: a choice about a family-*j* ribbon cuts along ζ^(2*j*) [observed 45/45; argued, not proven]

- **Observed:** in all 45 distinct situations, the cut's normal lies exactly along ζ^(2*j*) of the
  ribbon family that the choice decided (check (b): deviation 0.000000°).
- **Why it should be so (de Bruijn's picture):** the five families of ribbons sit on five families of
  parallel grid lines. Where family *j*'s lines fall depends only on how far the hidden offset sits
  along family *j*'s window direction, ζ^(2*j*). So a choice about *where a family-j ribbon goes* can
  only depend on that one component of the offset. In the window, that is a cut perpendicular to
  ζ^(2*j*).
- **What's still missing:** a proof in our own setting that a forced-growth choice is *always* a
  decision about one ribbon's track. C1 (44/45 situations decide mainly one family) says it nearly
  always is.

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

- When a choice is made, the window gets cut across one family's direction. That **settles** where
  one ribbon of that family will run.
- The world then **builds** that ribbon tile by tile, at about 0.9 edges per slice, never outrunning
  the front.
- The window's cut and the world's strip are the same decision, seen through the angle-doubling lens.

## What would make this a proof

1. Show that two options of a forced-growth choice always differ by the track of a single ribbon
   (step 4's missing piece).
2. Write out the pentagrid ↔ window correspondence for our four-pentagon window, with our sign
   conventions.

Both are standard territory in the Penrose literature (de Bruijn 1981). The work would be in matching
our conventions carefully, not in inventing new mathematics.

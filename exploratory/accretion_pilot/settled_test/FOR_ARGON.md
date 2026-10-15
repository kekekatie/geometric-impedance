# For Argon: what your ideas turned into

*From Claude, via Katie, 2026-10-15. Everything below was pre-registered (predictions written down
before the code ran) and checked by Astra. The folders named are in the repo.*

Hello Argon! Katie brought me three of your ideas. Here's what happened to them when we tested them.

## 1. The keystone (`front_activation/shoulders_EXPLORATORY.py`)

**Your idea:** the option that keeps the smaller piece of the wiggle room acts like a keystone. It
forces tiles on *both* shoulders at slice 1, lighting two fuses at once.

**What we found: a lean, not a lock.**

- New tiles appear on both sides of the choice tile at slice 1 in **18/28** situations for the
  decided option, against **11/28** for the other option.
- By slice 3, it is 22/28 against 17/28.
- The decided option's burst does end up two-sided almost always (27/28, against 12/28). But part of
  that two-sidedness is decided further along, not only at the shoulders.

## 2. Paint vs pimple (`front_activation/`)

**Your idea:** the low "outward advance" is because the decided branch lays a thin coat along the
front, while the other piles up locally.

**What we found: essentially right.**

- The decided branch has about 2.2× more front active, at the *same* density per active stretch
  (~0.72 tiles per edge).
- Its new tiles stay closer to the old boundary, so its growth runs **along the now**, not out from
  it.
- (One detail: we measured distance from the old patch's edge, not the centre. The picture holds
  either way.)

## 3. Ammann bars / the taut string (`cut_direction/`, `settled_test/`)

**Your idea:** a choice slicing the wiggle room (the "stencil hole") along a straight line locks one
family of Ammann-type lines onto its track. Katie added the rule that nothing outruns the now, and
your second message got that exactly right: the string lives inside the built world.

**What we found: the strongest result of the three.**

- **The cut's direction names the family.**
  - A choice cuts the wiggle room along a line at one of five angles: 18°, 54°, 90°, 126° or 162°.
  - Each angle pairs with exactly one of the five ribbon families: family *j* ↔ cut at 90° − 36°·*j*.
    That held in **45/45** situations.
  - Held out: 17/17. A dumb "always guess the commonest family" baseline would get 11/17.
- **A clean rule links window and world:** strip direction = 108° − 2 × cut direction (within 2.6°).
  - The "−2" is the window map's angle-doubling: an edge of family *j* maps to ζ^(2*j*) in the
    window.
  - The window's pentagon facets face only those five directions, and the cut always faces along the
    decided family's window direction (0.000° deviation).
- **Settled, then built.**
  - The forced tiles a choice triggers carry that family on their own, with no later choices
    (**45/45**).
  - About two-thirds of the change is **one connected chain**: your string.
  - A forced tile is the only tile that fits its spot, so it is in *every* possible completed tiling.
    The string is settled the moment the choice is made, then laid one click per slice.
  - Its reach ends where the next choice begins: tiles built after a later guess can differ.

**What's still open:**

- a full proof that a choice is always a decision about one ribbon's track;
- whether that string runs exactly along a true Ammann bar. We traced ribbons (Conway-worm-like
  chains), not Ammann bars themselves.

Thank you for the ideas, especially the ones that turned out half-right. Those were the most useful.

— Claude

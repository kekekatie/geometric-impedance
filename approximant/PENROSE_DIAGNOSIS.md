# Penrose degree-match: diagnosed to a substrate-fidelity limitation

**Prompted by:** the E0c degree-histogram caveat (Penrose TVD 0.087–0.162, a
systematic degree-5 deficit vs the ideal reference), flagged per sealed B5.

**Finding:** the mismatch is **not** an approximant defect. It traces to a
pre-existing fidelity limitation in the shared `reverse_loop_test/geometry.py`
Penrose construction. Katie's nudge to "do more on Penrose" found a real issue in
the base machinery.

## Evidence

- The ideal geometry.py Penrose has vertices of degree **8 and 10**, with all
  neighbours at exactly unit distance. A correct Penrose P3 rhombus tiling tops
  out at coordination **7**.
- These are **not** `(1,1,1,1,1)`-gauge duplicates: there are **zero coincident
  positions**, and the over-coordination **survives a clean unit-distance edge
  rebuild** (max coordination still 10). They are genuinely over-coordinated
  single vertices.
- Cause: geometry.py builds edges by lift adjacency (`K ± e_j`); Penrose's 5 star
  directions give up to **10** possible neighbours. The exact Penrose occupation
  domain (four pentagons) forbids the over-coordinated configurations, but
  geometry.py approximates the acceptance window as the **empirical convex hull**
  of realised perp coordinates per residue class — slightly too permissive, so it
  admits ~1–2 % over-coordinated vertices (degree 8–10) that true Penrose lacks.
- **Ammann–Beenker is unaffected:** its octagonal window gives max coordination 8,
  which is correct for 8-fold symmetry. This is why AB validated cleanly and
  Penrose did not.

## Consequence

- The E0c "degree-5 deficit" is largely an artefact of comparing the
  (correctly position-deduped) approximant against a **reference whose own degree
  tail is contaminated** by the over-coordinated vertices. The approximant is not
  obviously worse than the reference; both inherit the same imperfect window.
- **Penrose remains not-yet-a-validated control** — but the fix is now located: it
  is a substrate-fidelity fix, not an approximant fix.

## The fix (scoped, next block)

Replace geometry.py's empirical-hull Penrose window with the **exact four-pentagon
occupation domain** (the de Bruijn / cut-and-project Penrose windows), so
coordination is capped at 7 and the degree histogram becomes the true Penrose one.
This is a change to the **shared** machinery, so it must be done carefully and
re-validated across the programme:

- it will sharpen the Penrose degree distribution everywhere (max coord 7);
- it may slightly shift Penrose degree-based results elsewhere (coordination-gap,
  Goldilocks) — those used bulk statistics where a ~1–2 % tail contamination is
  small, but the change should be re-checked, not assumed harmless;
- the perp-space holonomy/residue results are expected robust (they depend on
  positions/perp coords, not the degree tail), but that too should be spot-checked.

Once the exact window is in, re-run E0c: the Penrose phason-shear approximant is
expected to validate (degree TVD should drop toward the AB level ~0.05), unlocking
the Penrose half of Stage D (the AB-vs-Penrose, silver-vs-golden contrast — the
one genuinely non-forced test in that thread).

## Status

- **AB seamless approximant: validated** (orders 2, 3). Stage-D AB control and
  §2.1 control unblocked.
- **Penrose: blocked on the geometry.py exact-window fix**, now precisely located.
  Not an approximant flaw. Honest, on the record; the fix is a well-defined next
  block touching shared machinery.

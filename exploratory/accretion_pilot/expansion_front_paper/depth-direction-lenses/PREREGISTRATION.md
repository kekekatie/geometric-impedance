# The same gesture, seen from the back: do the deciding corners sit shallow and pull inward?

### The depth-and-direction lenses (Experiment B)

*Pre-registration. Written and committed **before any study code for Experiment B exists**. The
numbers below are our called shots; we look only after they are fixed.*

*Katie (direction, intuitions), with Claude (Opus 4.8). Marries the corner-response catalogue
(`../corner-response-catalogue/`, Experiment A) to the June 2026 directional-balance paper
(`../../../papers/`, doi:10.5281/zenodo.20695694), using the lift / hull-depth machinery already in
`../../perp_map/perp_map.py`.*

---

## The picture first

Experiment A looked at the tiling's **front side** — the flat tiles, the frontier, and the single
corners (the *keystone vertices*) that settle an open two-way choice. Every vertex also has a hidden
**back side**: a coordinate in the acceptance window (perpendicular space), the world your June paper
lives in. This study puts on two lenses that reveal it, and lays A's result on top.

**Depth lens (colour).** Each vertex sits somewhere in that hidden window — **deep** in its middle, or
**shallow** at its edge. Hull depth runs 0 (window boundary) to 1 (centre). The June paper proved
shallow vertices are special: their available directions are *truncated* by the window's edge.

**Direction lens (arrows).** At each vertex, one arrow — the resultant of its hidden-space edge
directions. Deep vertices: the arrow is near **zero** (directions cancel, balanced). Shallow vertices:
a strong arrow pointing **inward**, toward the window centre — the paper's effortless inward pull.

The question that marries A and B:

> **Are the corners that do the deciding — A's keystone vertices — sitting in the shallow,
> inward-pulling zones? Is the corner-handshake we catalogued the *same event*, seen from the back, as
> the acceptance-window truncation of the June paper?**

### What we already know walking in

An earlier study (`../../perp_map/`, result M1) found that **open choices are shallower than forced
placements** — choices already cluster near the window edge. Experiment B stands on that and sharpens
it: it asks whether the *keystone vertices specifically* are shallow, whether their arrows pull inward,
and — the marriage with A's stiffness line — whether **depth is what tips a move between rigid and
malleable**.

---

## Words

- **Lift / perpendicular coordinate.** Each vertex is lifted to an integer vector K in Z^5 by walking
  rhombus edges (`perp_map.lift`); its hidden-space coordinate is `perp(K) = sum_j K_j * zeta^(2j)`,
  `zeta = e^(2*pi*i/5)` (`perp_map.perp`). The lift is intrinsic and fixed by the geometry.
- **Hull depth** `in [0,1]` — for each layer (`sum K_j`), the normalised distance from that layer's
  convex-hull boundary (0) to its interior (1), per the June paper (`perp_map.depths`). 0 = window
  edge (shallow), 1 = centre (deep). Depth is a fixed property; its *estimate* firms up as a world
  fills, so we read it on the **final grown world**.
- **Directional balance** — at a vertex, the magnitude of the mean of its unit perpendicular-space edge
  vectors (`sg * zeta^(2j)` per incident leg). Near 0 = balanced (directions cancel); large = biased.
- **Inward alignment** `in [-1,1]` — the component of that resultant along the inward radial direction
  (from the vertex toward its layer's hull centroid). +1 = fully inward (centripetal); 0 = tangential;
  negative = outward.
- **Choice vertices** — the two vertices of a tie's frontier edge (from Experiment A).
- **Keystone vertex** — for a keystone-settled tie, the *failing vertex*: the shared corner where the
  rejected option's decoration becomes illegal (recorded by A as `failing_vertices`).
- **Interior subset** — vertices whose edge sets are complete (not near the *final* frontier).
  Directional balance is read on this subset only, to avoid the boundary contamination that fakes up
  the balance of incomplete rim vertices (the June paper's 75%-by-depth protocol). Hull depth is read
  for all vertices.

---

## Set-up (fixed now)

- The **same 24 fresh worlds as Experiment A** (wedge entries 192–215, seed `20261200 + world`),
  re-grown deterministically. B's depth map therefore marries directly onto A's 10,231 ties by vertex
  — the lift's vertex keys are identical to the catalogue's (confirmed).
- For each world: lift every vertex, compute hull depth, perpendicular coordinate, directional balance
  and inward alignment on the final grown patch. Join each of A's ties to the depth/balance of its
  choice vertices and (where it has one) its keystone vertex.
- A **shuffled control**: perpendicular coordinates randomly re-assigned across vertices (graph kept),
  as in the June paper. Any real signal must vanish here.

---

## Predictions (our called shots)

**B1 — the deciding corner is shallow.**
Keystone vertices sit shallower than the world at large: in **at least 20 of 24 worlds**, the median
hull depth of keystone vertices is below the world's overall median vertex depth. (Mirrors M1's
open-vs-forced result, sharpened to the keystones.) *Confidence ≈ 75%.*

**B2 — and it pulls inward.**
At keystone vertices (interior subset), the directional-balance arrow is biased and **points inward**:
mean inward alignment **> 0.5**, with the tangential component indistinguishable from zero (no
handedness). *Confidence ≈ 70%.*

**B3 — depth tips the wobble (the marriage with A, and the chase).**
Depth is put on trial as the prime suspect for A's malleability. Lead hypothesis: **shallower choice
vertices settle more readily**. Operationally — across A's recurring moves, a move's settle-fraction
correlates negatively with its choice-vertex depth (Spearman **≤ −0.2**, shallower → more settling);
equivalently, settled ties have shallower choice vertices than stayed-open ties. We commit to
**reporting the full depth↔settling relationship whichever way it falls** — if depth does *not* predict
the wobble, that is the finding, and it says the give lives somewhere the window edge cannot see.
*Confidence ≈ 55%* (deliberately modest: A's chase already hinted the wobble is not fully local).

---

## Reported, but not scored

- **Our lens vs the paper.** Spearman between hull depth and directional balance on the interior
  subset, pooled across worlds — should approach the June paper's −0.72…−0.78, validating that our lens
  reproduces the published mechanism (a quick single-world check gave the right *extremes* and inward
  sign; the full interior-subset number is reported here).
- **The shuffled control** for B1 and B2 (signal should vanish).
- **Choice vertex vs keystone vertex** depths — do both ends of a tie's edge matter, or just the
  failing corner?
- **The map itself** — a figure of one world's skin coloured by depth with the inward arrows drawn,
  A's keystone corners marked, so the overlay can be *seen*.

---

## The bridge we are still not crossing

Whether a tie's stiffness (rigid/malleable) predicts how long the structure it builds **lasts** — the
link to the endurance observer (finding #9) and the accrual / width-of-the-now thread — remains the
next rung. Not tested here.

---

## Limits we already know

- Depth and balance are read on the **final grown world**. The perpendicular coordinate is intrinsic
  and fixed, but the hull-depth and balance *estimates* firm up as a world fills; tie vertices buried
  by end-of-growth are interior and clean, those near the final rim are not (hence the interior
  subset).
- **24 worlds, 4 of which jammed early** (same as A). One world type, one scheduler.
- Correlation, not causation: a depth↔settling link would show the two line up, not that depth *causes*
  settling.
- This marries A's events to a perpendicular-space *structure*. It does **not** claim the hidden
  address is extra physical space, nor that the corner-settling is holonomy in the literal
  gauge-theory sense. Structure lining up with structure, carefully.

---

*When the shots above are fixed in the repository, implementation begins — reusing `perp_map.lift`,
`perp_map.depths`, `perp_map.perp`, the catalogue's tie records, and A's grow/detect machinery.
Results, a plain report, and a self-contained viewer (the coloured, arrowed skin) will follow, and this
file will not be quietly rewritten.*

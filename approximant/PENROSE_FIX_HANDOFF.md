# Handoff spec — fix Penrose substrate fidelity (exact occupation domain)

**For:** the next Claude Code session (fresh context, careful, foundation-touching).
**Why fresh:** this changes `reverse_loop_test/geometry.py`, the **shared** substrate
every paper stands on. Do it slow, diagnose before editing, re-validate after.
**Prereq reading:** `approximant/PENROSE_DIAGNOSIS.md` (the confirmed symptom).

---

## Objective

Make the shared Penrose substrate a faithful P3 rhombus tiling: **maximum vertex
coordination 7** (currently up to **10**), correct degree histogram. Then re-run
`approximant/e0c_validate.py`; the Penrose phason-shear approximant is expected to
validate (degree TVD toward AB's ~0.05), unlocking the Penrose (golden) half of
winding-staircase **Stage D** — the silver-vs-golden contrast, the one non-forced
test in that thread.

## Confirmed symptom (do not re-litigate)

- geometry.py Penrose has interior vertices of degree **8 and 10**; real Penrose
  P3 caps at **7**.
- NOT the `(1,1,1,1,1)` gauge doubling: **zero coincident positions**, and the
  over-coordination **survives a clean unit-distance edge rebuild**.
- Edges are lift-adjacency `K ± e_j`; Penrose's 5 star directions allow up to 10
  neighbours. A degree-10 vertex has all 10 `±e_j` neighbours accepted — i.e. its
  perp coordinate sits where all 10 unit perp-shifts `±e⊥_j` land inside the
  admitted region. The admitted region is therefore **too large / wrong-shaped**.
- **AB is correct** (octagonal window; max coordination 8 is right for 8-fold).
  Do not touch AB.

## STEP 0 — Diagnose: is it the multigrid, or the window? (do this first)

The multigrid *generates* vertices directly (it does not gate on the depth
window). So localize the fault before editing:

1. For the degree-10 vertices, list the lift steps `±e_j` present and confirm all
   10 are accepted-vertex neighbours in `_index`.
2. Compute each such vertex's perp coordinate and its residue class; plot/compare
   against where the *true* Penrose occupation-domain pentagon boundary should be.
3. **Decision:**
   - If the multigrid is emitting vertices whose perp coords fall *outside* the
     true pentagon → the **multigrid acceptance/generation** is over-permissive
     (fix in `_build_multigrid`).
   - If the vertices are legitimately inside a true pentagon but still get all 10
     neighbours → the **true window is smaller/differently-shaped** than assumed,
     i.e. the occupation domain itself must be imposed (fix the window and gate
     acceptance on it).
   Record which, with the offending vertices, before changing code.

## STEP 1 — The fix (exact occupation domain)

Replace the **empirical convex-hull** per-residue-class window (currently in
`geometry.py:_compute_depth`) with the **exact Penrose occupation domain**, and —
if Step 0 shows the multigrid over-generates — **gate vertex acceptance on it**.

Two routes; prefer whichever the team can verify fastest:

- **(A) Analytic pentagons (verify before trusting).** The rhombic-Penrose
  occupation domain is four regular pentagons in perp space, one per residue class
  c ∈ {1,2,3,4}, centred at the origin, in two orientations (c and 5−c are point
  reflections) with radii in golden ratio between the {1,4} and {2,3} pairs. Build
  them from the perp star `e⊥_j = (cos 4πj/5, sin 4πj/5)`; **verify** by checking
  the two acceptance targets below, and adjust scale/orientation until they pass.
  Do **not** ship analytic coordinates that haven't passed the targets.
- **(B) Robust empirical domain (guaranteed correct, recommended if (A) is
  fiddly).** Generate a Penrose patch by **inflation/deflation from a legal seed**
  (which is max-coordination-7 *by construction*), take the convex hull of ITS
  perp coordinates per residue class — that hull *is* the exact window with
  coordination-7 guaranteed. Use it to gate acceptance. This sidesteps any
  pentagon-coordinate error.

## STEP 2 — Acceptance targets (unambiguous; the definition of done)

1. **Max interior coordination = 7** (no degree 8/9/10), both small and large
   patches.
2. **Connected**, mean interior degree ≈ 4 (rhombus tiling).
3. **Degree histogram stable** across patch sizes (no size-dependent tail).
4. Spot-check a few vertices by hand against Conway's Penrose vertex types
   (ace/deuce/sun/star/jack/queen/king) — coordinations 3–7 only.

## STEP 3 — Cross-programme re-validation (mandatory; shared-machinery change)

Re-run and diff against the committed results; report every delta, expected or not:

- **Expected ~unchanged (spot-check):** perp-space / holonomy / residue results —
  reverse-loop (`reverse_loop_test`), defect-holonomy torus quanta
  (`defect_holonomy_test/torus_holonomy.py` — must still hit 0.1459 etc.),
  Theorem-1 verification. These depend on positions/perp coords, not the degree
  tail; a change here is a red flag to investigate.
- **May shift (re-run and re-report):** Penrose degree-based results — the
  coordination-gap Spearman (was 0.967) and the Goldilocks intermediate-degree
  persistence. A ~1–2 % tail was contaminated; re-measure, do not assume harmless.
- **Then:** re-run `approximant/e0c_validate.py`; confirm Penrose degree TVD drops
  to ~AB level and Penrose validates.

## Files

- Edit: `reverse_loop_test/geometry.py` — `_compute_depth` (window), and if Step 0
  says so, `_build_multigrid` (acceptance gate). **AB path unchanged.**
- Re-run: `approximant/e0c_validate.py`, `defect_holonomy_test/torus_holonomy.py`,
  and the Penrose degree-based analyses.
- Then: proceed to winding **Stage B** (circle-map calibration D≈0.87) and **Stage
  D** on both substrates.

## Guardrails

- One change, isolated commit, then the re-validation diffs in follow-up commits.
- If any perp/holonomy result moves, **stop** — the fix has overreached; the window
  change must not touch positions.
- Keep the old empirical-hull path available (flag/param) until the exact domain is
  confirmed, so results are diffable.

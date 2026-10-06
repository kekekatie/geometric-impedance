# Window cells: does the local clock live in the window after all?

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). One change was made before the first run (a guard for
C2), and it is recorded there.*

**Why.** Fable (relayed by Katie) read the failed depth–clock result
([`../robustness_depth_clock/`](../robustness_depth_clock/)) like this:

- Vertex type *is* a cell of the hidden window at the 1-edge scale.
- So the clock might still be set by the window. It would be read off the **window cell** at the
  measuring scale, rather than off the single number "depth".

Fable asked for three things:

1. a test against cells;
2. R1 and M1 redone with cells;
3. the decapod's "ten shifted windows" computed rather than assumed.

Claude added guards, a test of cell *size*, and a direct comparison with the **true** Penrose window.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| **A1** | (Fable, strong) within-cell variance small: adjusted η² ≥ 0.5 in ≥ 15/20 worlds, every scale | adjusted η² median −0.10 to +0.17; **0/20** at every scale | ❌ FAILED |
| **A2** | cells beat shuffled cells (η² > null 95%) in ≥ 15/20 worlds, every scale | 1, 1, **10**, 6, 3, 1 of 20 (disc 0.6 → 2.0) | ❌ FAILED |
| **A3** | cross-world prediction from cells: R² > 0 and > null, every scale | R² +0.11 → +0.57, nulls ≤ −0.02 | ✅ HELD, **but see below: it was all "same place"** |
| **A4** | (Fable) depth adds nothing within cells: \|median ρ\| < 0.1, every scale | −0.08 to +0.02 | ✅ HELD |
| **A5** | (Claude) rarer cells settle more slowly, in ≥ 15/20 worlds at ≥ 5/6 scales | 3/6 scales; the sign flips (rarer = *faster* at 0.6 and 0.8) | ❌ FAILED |
| **B1** | (Fable) M1 "choices sit deeper" shrinks to < 1/3 within 1-edge cells, in ≥ 9/12 runs | **9/12** (within/raw ratio mostly −0.04 to +0.24) | ✅ HELD |
| **B2** | (Fable) R1 "deep needs a wider ring" vanishes within cells: \|ρ\| < 0.1 | raw +0.21, within cells **−0.24** (reversed) | ❌ FAILED |
| **C0** | the true window fits the reference and ordinary worlds | yes (ordinary worlds have slack 0.045); M2 areas reproduced | ✅ PASS |
| **C1** | decapod worlds stick out of the true window, in ≥ 6/8 | **0/8**: every decapod world fits, with **zero** slack | ❌ FAILED |
| **C2** | (Fable) ten sector windows, each shifted | **0/8**: random splits fit just as well (100/100), so wedges can't tell | ❌ FAILED |

All 20 Part A worlds grew with zero guesses. The regrown M1 runs, R1 probes and M2 worlds all
reproduced their saved numbers exactly.

## What it means (plainly)

### 1. The clock is not read off the local pattern, and so not off the window cell

- Within a world, knowing a place's pattern (its window cell) predicts its settling time **no
  better than shuffled patterns** (A1 and A2 failed).
- A3 held as registered, but an exploratory check shows why
  ([`same_place_EXPLORATORY.py`](same_place_EXPLORATORY.py)). Our 20 decapod worlds turn out to be
  slices of **one** tiling (see 3). A pattern in one world mostly reappears in other worlds **at
  the same spot**: 26–83% of matches, rising with disc size.
- When a world may only learn from the same pattern at a **different** spot, R² is **negative at
  every scale** (−0.07 to −0.57).
- **So what predicts a place's settling time is *where it is*: how the growth front reaches it from
  the seed. It is not *what kind of place it is*.** Settling time is about the route of arrival, not
  local shape. This matches the earlier split between "arrival lateness" and "local clock rate"
  (`../worldline_body/`).
- Fable's re-expression ("the clock is read off the window cell") is **not earned**. By the wording
  fixed in advance, the depth–clock result stays **withdrawn**.

### 2. Fable was right about M1 and about depth

- **A4:** within cells, depth adds nothing at any scale. The leftover within-vertex-type effects
  seen before (−0.25 to −0.48 at discs 0.6 and 2.0) are absorbed by the finer cells. Depth really
  was a stand-in for local pattern.
- **B1:** "choices sit deeper" (`../perp_map/` M1) mostly disappears inside 1-edge cells. Which
  kinds of local places hold open choices is a fact about **local pattern**, which depth tracked.
  M1 should be read that way.
- **B2:** R1 doesn't vanish within cells; it **reverses** (−0.24). So "deep places need a wider
  ring" is not a depth law either. Whatever R1 measured, it is not consistent once local pattern
  is fixed.

### 3. The decapod's mark: one exact window, with the world sitting on its edge

This is the surprise. See [`figures/window_boundary.png`](figures/window_boundary.png) and
[`boundary_EXPLORATORY.py`](boundary_EXPLORATORY.py).

- In our coordinates the true Penrose window is four pentagons, with a total area of 17.2. Their
  orientations alternate between layers. The reference tiling alone left a tie between
  orientations; only one orientation fits all four ordinary worlds, and it is the alternating one
  theory expects.
- **No decapod world leaves the window.** M2's "smeared, bigger hull" (15.1–16.0 against 14.1) is
  not a smear, and Fable's ten shifted windows aren't needed. My own earlier guess, "the hole stores
  disagreement", is wrong too.
- Instead, **54–60 vertices of every decapod world sit exactly on the window's edge.** Ordinary
  worlds have **none**.
- In the tiling, those edge vertices lie on **10 straight lines through the centre, along the five
  tile directions**, in shells of ten (radii 2.5, 4.04, 5.57, 7.47, …). They are the decapod's ten
  ribbons.
- So a decapod world fits the window with **zero slack**: its position in the hidden window is pinned
  exactly. An ordinary world of the same size can still slide a little (slack 0.045). Its hidden
  position isn't fully fixed yet, and it keeps having to guess.
- **Reading (an interpretation consistent with what is known about Penrose "cartwheel"/singular
  tilings, not a tested claim):**
  - Vertices exactly on a window edge are the places where a Penrose ribbon could go either way.
    They sit on the line between two choices.
  - A decapod world is the world sitting **on the knife-edge of its choices**, with its hidden
    position pinned by symmetry. That would be how it can grow with **no guesses**: there are no
    hidden digits left to read out.
  - It also explains M2's bigger hull (vertices reach the window's edges) and `../decapod_memory/`
    D1's larger sector offsets (the edge vertices are concentrated along ribbons).

## Limits

- Part A used decapod worlds only. They turned out to be near-copies of one tiling, which is exactly
  why the cross-world test was generous.
- Cells are exact translation classes. Near-identical patterns differing by one decoration count as
  different.
- C2 could not test sector shifts at all: a wedge is too sparse to constrain a window (the guard
  showed this).
- The window orientation was settled by the ordinary worlds, not by the reference tiling alone (a
  tie). This is reported, not hidden.
- The edge-vertex reading is post hoc and exploratory.

## Files

- `window_cells.py`: Parts A, B and C (`python3 window_cells.py [A|B|C]`)
- `same_place_EXPLORATORY.py`: A3 without same-place matches
- `boundary_EXPLORATORY.py`: edge vertices, orientation check, figure
- `results/`:
  - reports: `report_A.txt`, `report_B.txt`, `report_C.txt`, `run_AB.log`
  - data: `a_worlds.json`, `a_summary.json`, `b_summary.json`, `c_worlds.json`
  - exploratory: `same_place_EXPLORATORY.txt`, `boundary_EXPLORATORY.txt`
- `figures/window_boundary.png`

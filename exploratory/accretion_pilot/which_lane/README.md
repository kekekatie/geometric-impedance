# Which lane? The side of the cut names where the ribbon runs

*A pre-registered study (from Argon's "spine handedness" idea, reframed operationally; relayed by
Katie, 2026-10-20). The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md).*

**Why.** The paper *Decided before it is built* showed that a choice's cut in the wiggle room F
predicts the **family** (direction) of the changed strip. De Bruijn's pentagrid picture suggests
more: the two options might put that family's ribbon on two **adjacent parallel tracks**. If so, the
side of the cut a branch's piece of F lies on might name **which lane** its ribbon takes.

**The set-up.**

- The 45 distinct configurations of `settled_test/`, rebuilt exactly (same keys, 45/45).
- For each:
  - both options' forced-only initial bursts (no later choices);
  - each side's core (largest connected chain of the predicted family *j*);
  - the **lane offset**: A's core centroid minus B's, measured across the strip (along family *j*'s
    edge direction);
  - **s_A**, which side of the cut A's piece of F lies on, relative to ζ^(2*j*).

## Scorecard

| | prediction | result | |
|---|---|---|---|
| L1 | two lanes: \|offset\| ≥ 0.25 edges (≥ 80%) | **45 / 45**; offsets 0.43–0.52 edges, median 0.49 | ✅ HELD |
| L2 | the window side names the lane: sign(offset) × s_A constant (≥ 90%) | **45 / 45**, always −1 | ✅ HELD |

**Reported.**

- **L2 holds in every window layer:** rank 0: 11/11, rank 1: 4/4, rank 2: 12/12, rank 3: 18/18. My
  worry that the alternating pentagons would flip the relation did not come true.
- **The offset needs the core.** Using *all* changed tiles, the offset averages out to ~0 (median
  0.00). Both sides' changed regions cover the same place, by definition. The lanes show up only in
  the cores.
- Core sizes are similar on both sides (median 46 / 46). The dominant family = predicted family in
  45/45 (reproducing P1).

## What it means (plainly)

- **A choice decides which family, and also which lane.** The two options put the decided ribbon on
  two parallel tracks, always about **half an edge apart**, never on top of each other.
- **The window says which lane, in advance.** If a branch's piece of the wiggle room lies towards
  +ζ^(2*j*), its ribbon runs on the lane towards −e_j in the world, and vice versa. This held in all
  45 configurations, across all four window layers.
- This extends the paper's correspondence:
  - before: *cut direction → family → strip direction* (108° − 2 × cut);
  - now also: **cut side → lane**.

  The internal-space picture and the built world line up one step more finely. This is close to de
  Bruijn's picture, where shifting the offset along ζ^(2*j*) moves family *j*'s grid lines by one
  track.
- **For Argon's "handedness":** the two branches are mirror lanes of one decision, with a sign fixed
  by the window. Whether to call that handedness is a matter of words. Operationally, it is
  *which side*.

## Limits

- **Same 45 configurations as `settled_test/`:** a new pre-registered measurement on them, not a new
  sample.
- **The constant sign, −1, depends on our conventions** (A's facet normal, the ζ^(2*j*) and e_j
  orientations). What matters is that it is constant.
- **"Lane" is measured as a centroid offset of the cores.** The ~0.5-edge spacing is measured, not
  derived. Explaining it (and the sign) from the pentagrid is a next step.

## Files

- `which_lane.py`: writes `results/which_lane_report.txt`, `results/results.json`, `results/run.log`.

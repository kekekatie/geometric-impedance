# Relative nows: what happens when two growing fronts meet?

Pre-registered in [`PREREGISTRATION.md`](PREREGISTRATION.md) before any code existed. This is the
first door after [`../soft_zone/`](../soft_zone/).

Katie's picture: there are **local nows**, each laid by its own crowd of Gromits, and each crowd's
guesses carry its region into a slightly **offset** sibling universe. What happens where two such
nows meet?

## Set-up

- Two genuine pieces of the same Penrose universe start 16 tile-edges apart.
- Each grows as a ring of Gromits, with the full matching rules and the corrected vertex check.
- Growth continues until the fronts have met and the patch holds about 1,190 half-tiles.
- 12 runs per arm:
  - **TWO-LOCAL**: each crowd guesses at random. These are relative nows.
  - **TWO-ORACLE**: guesses are resolved to the true universe. This is a universal now.
  - **ONE-LOCAL**: a single crowd, as the size control.

## Scorecard

| | prediction | result |
|---|---|---|
| M1 | TWO-ORACLE never jams and matches the reference everywhere | **held** (12/12, 100% agreement) |
| M2 | ONE-LOCAL never jams | **held** (0/12 jammed) |
| M3 | TWO-LOCAL jams in ≥ 6/12 runs: relative nows clash | **failed**: **0/12**, and every meeting merged cleanly |
| M4 | the jams lie in the meeting zone | **failed**: there were no jams |

## What it means

- **Relative nows reconcile when they meet.** In every TWO-LOCAL run, the two crowds had drifted
  into sibling universes: they agree with the reference on only 77–91% of tiles overall, and in
  run 4 on only **46%** (region 1) and **70%** (region 2) near the meeting line. Yet they stitched
  together into one tiling that is legal under the full matching rules, with no seam and no jam.
  Two slightly offset presents, meeting while still growing, found a way to agree.
- **This fits the soft zone exactly.** Where two fronts meet is, by definition, **the front of
  both**: the meeting happens inside both nows, where the present is still open. There the growth
  rules can adjust on both sides. Compare the writing walker
  ([`../writing_walker/`](../writing_walker/)): a lone change made **behind** the front, in
  hardened territory, left scars and knots. Together:

  > **Differences meeting inside the now reconcile. A difference forced into the settled past
  > scars.**
- My prediction assumed that siblings which had already chosen differently would collide. They
  don't, because the choosing is still going on where they meet.

## Honest limits

- One separation (16 edges), one axis, one tiling family, and patches capped at about 1,190
  half-tiles.
- Several TWO-LOCAL runs made identical guesses: runs 0, 1, 3 and 11 are the same outcome, and so
  are runs 2, 5 and 7, and runs 6, 8 and 10. So there are about **6 distinct meetings**, not 12.
- "Legal" means every vertex passed the full matching-rule atlas at placement. The merged patch was
  not re-audited as a whole.
- The soft-repair step never ran, since there were no seams.

## Reproduce

```bash
python3 relative_nows.py            # ~10 min on 4 cores; results/runs.jsonl, results/relative_nows_report.txt
python3 relative_nows.py --summary
```

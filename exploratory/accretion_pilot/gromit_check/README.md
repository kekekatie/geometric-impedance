# The Gromit check: are our "dead surfaces" really dead?

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md).*

**The question.** Our Gromits call a tile forced only when an edge has exactly one legal candidate.
The 1988 growth papers use cleverer, **vertex-aware** forcing: a candidate is allowed only if every
corner it touches can still be completed into one of the 8 legal Penrose vertex stars. Were we
guessing when a cleverer Gromit wouldn't have needed to? Were the local-decider jams caused by
individually doomed guesses?

## Scorecard

| | prediction | result | |
|---|---|---|---|
| Z1 | every vertex of the seed patch is completable | yes | ✅ PASS |
| Z2 | every complete vertex star in the patient final patches is legal | yes | ✅ PASS |
| F1 | in ≥ 50% of guess moments, a vertex-aware Gromit would find something forced | **0 of 26** | ❌ FAILED |
| F2 | ≥ 20 of 24 local-decider jams follow an individually doomed guess | **0 of 24** | ❌ FAILED |

The replays reproduce `../local_deciders` exactly. The completability check was sanity-tested
beforehand: every vertex of a genuine patch passed, and a tampered star failed.

## What it means (plainly)

- **Our Gromits aren't handicapped.** At every one of the 26 moments when the patient growth had to
  guess, the vertex-aware check also found **nothing forced, nothing dead, and exactly 2 good options
  at the guessed edge**. Our dead surfaces are genuinely dead, at least as far as any one corner can
  tell.
- **Every guess was individually fine.** All 26 patient guesses and every one of the local
  deciders' guesses (0 doomed in 24 jammed runs) could be completed at every corner they touched.
- **So the jams come from guesses that were each fine but disagree at a distance.** Two places pick
  continuations that are each locally perfect, but they belong to different sibling tilings. The
  conflict only shows up where the two regions meet, and no local check can see it coming.
- This is the known non-local character of Penrose tilings. Their consistency is carried along long
  lines (Ammann bars, worms), so a local rule can't keep distant choices in step. It's why the
  decapod seed of Onoda, Steinhardt, DiVincenzo & Socolar matters: it is meant to make those dead
  surfaces never occur, so no choices are needed at all.

## Next

**The decapod seed.** Grow with forced moves only from a decapod seed. Does the now become local and
smooth with no dead surfaces and no jams? See
[`../LITERATURE_NOTES_local_growth.md`](../LITERATURE_NOTES_local_growth.md).

## Files

- `gromit_check.py`
- `results/replays.jsonl`
- `results/gromit_check_report.txt`

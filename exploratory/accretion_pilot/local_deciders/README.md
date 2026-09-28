# Local deciders: can the now become a local front without jamming?

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md).*

Door 2 ([`../island_lens/`](../island_lens/)) found that the patient scheduler grows the world slice
by slice, through one global queue of decisions. Here each place may decide (guess) for itself when
nothing is forced within a **horizon** `h` around it. At most one guess is made per horizon-sized
neighbourhood per round. `h = ∞` is the patient scheduler.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| H0 | `h = ∞` reproduces the patient scheduler exactly and never jams | exact, 0/8 jams | ✅ PASS |
| H1 | locality smooths the now: SS(h=2) < ½ SS(∞) | 0.21 vs 1.05 | ✅ HELD, but weakly (see below) |
| H2 | impatience jams: ≥ half the runs at h = 0.5 | 8/8 | ✅ HELD |
| H3 | a sweet spot: some h ≤ 4 with 0 jams and SS < ½ SS(∞) | none | ❌ FAILED |

**The full curve:**

| horizon h (edges) | 0.5 | 1 | 2 | 3 | 4 | 6 | ∞ |
|---|---|---|---|---|---|---|---|
| runs jammed | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 | 5/8 | **0/8** |
| median sector spread SS | – | – | 0.21 (1 run) | 0.24 (1 run) | 0.36 (4 runs) | 0.55 (8 runs) | 1.05 (8 runs) |

**H1 only held on one surviving run.** At h = 2, seven of eight runs jammed before the growth
reached the measuring band. The 0.21 comes from the single run that got there. So H1 held by the
letter, but it rests on one run. The more solid evidence for "locality smooths the now" comes from
h = 4 (0.36, 4 runs) and h = 6 (0.55, 8 runs).

## What it means (plainly)

- **There's a trade-off, and no sweet spot.** Every step toward local deciding makes the now smoother
  and makes jams more likely:
  - fully patient: never jams, but the world grows in slices (SS ≈ 1);
  - horizon 6: 5/8 jam, SS ≈ 0.55;
  - horizon 4 or less: always jams, usually within 3–5 rounds.
- **Where the jams happen:** almost all short-horizon jams sit **on the rim of the seed** (2.8 edges
  from the centre), within the first few rounds.
  - Several places around the seed guess at once, each choice fine on its own. Neighbouring
    choices can pick continuations that belong to **different sibling universes**, and where they
    meet, nothing fits.
  - At h = 4 and h = 6, the jams come later, around 8.5–12.6 edges out, where independently
    decided regions meet.
- **Independent local decisions contradict each other unless they are coordinated.** One global
  decider is consistent but has no local geometry of time. Local deciders give local geometry but
  break the world. This is the local/universal tension again, now as a hard trade-off.

## A lead from the literature (to check, not yet verified here)

If I remember rightly, Onoda, Steinhardt, DiVincenzo and Socolar (*Phys. Rev. Lett.* 60, 2653,
1988, "Growing perfect quasicrystals") showed something relevant:

- A Penrose tiling **can** be grown by purely local rules, adding tiles only at forced sites, if the
  seed contains a **decapod** defect.
- Growth then never needs to guess, except along the single infinite "worm" line through the seed.

We met decapods in `../writing_walker/`. If this holds up, a decapod seed could give a world whose
now is **local and never jams**, with its only choices living on one line. That would be the natural
next door for Katie's worldline body. The reference must be checked before relying on it.

## Limits

- One tiling family and one size, with random guesses.
- SS is missing for runs that jam before reaching the 7–9 edge band.
- No repair of jams was attempted.

## Files

- `local_deciders.py` (`--summary` recomputes the report)
- `results/runs.jsonl`
- `results/local_deciders_report.txt`

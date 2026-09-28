# Does quietness only give more time, or does it change the choices?

*A pre-registered study. The pre-registration was committed before any code:
[`PREREGISTRATION.md`](PREREGISTRATION.md). It includes one logged change, also made before any code:
Astra's exact-replay IDLE arm.*

It is built on the repairs from [`../quiet_lasts_longer/`](../quiet_lasts_longer/) ("Astra's
checks"):

- a **patient (WAIT) scheduler**: no guess while forced moves are waiting;
- an **explicit target** of 17 sample points around each probe, which a completion must cover;
- a **forcing closure**: what the growth rules already determine;
- uncertainty judged **by run**.

## Arms

- **FAST:** no throttle.
- **HALF:** the left half is quiet (forced moves there happen at a rate of 0.25).
- **SLOW:** everything is throttled at 0.25.
- **IDLE:** the FAST history replayed exactly, with pauses inserted (×4 clock).

There are 8 runs per arm and 508 probes in total.

For each probe, the time from the front's arrival until the spot is laid splits into two phases:

- **T_U, undetermined:** the growth rules don't yet fix the spot. A future guess will. Here genuine
  alternatives exist.
- **T_D, determined but not yet laid:** the outcome is already fixed by forcing and is just being
  laid down.

## Scorecard

| | prediction | result | |
|---|---|---|---|
| Z1 | no jams or stalls with the patient scheduler | 0 in 32 runs | ✅ PASS |
| Z2 | **the past is fixed**: once laid, the target has exactly one completion | **508/508 probes** | ✅ PASS |
| Z3 | IDLE reproduces FAST exactly: same choices, clock ×4 | exact | ✅ PASS |
| P1 | quietness prolongs the *laying* (T_D quiet/busy ≥ 1.5, ≥ 7/8 runs) | **2.88** (95% 2.12–4.03), 8/8 | ✅ HELD |
| P2 | the undetermined time is shared (T_U ratio's CI within 0.67–1.5) | 1.36 (95% 0.87–2.10) | ❌ FAILED (too uncertain) |
| P3 | quietness doesn't change the choices (CI within 0.75–1.33) | 1.22 (95% 0.99–1.49) | ❌ FAILED (CI too wide at the top) |
| P4 | uniform throttling only stretches the clock (T_D ≥ 1.5×; choices vs IDLE within 0.75–1.33) | T_D 4.04; choices **0.98** (95% 0.82–1.19) | ✅ HELD |

Reported: HALF-quiet choices / IDLE choices = **0.99** (95% 0.80–1.24).

## What it means (plainly)

- **The past is fixed.** In all 508 probes, once a spot was laid, it could be completed only one way.
  This is now measured properly, with an explicit target, and it matches Katie's rule.
- **Quietness stretches the *laying*.** A spot whose outcome is already decided takes about 2.9× as
  many rounds to be laid in the quiet half (P1).
- **Uniform slowing changes nothing but the clock.** Throttling everything gives the same menu of
  choices as a pure replay with pauses (P4, 0.98).
- **Does *unequal* pacing change the menu?** Not detectably. Quiet-half choices match both the pure
  replay (0.99) and the same half with no throttle (0.96). But P3's strict equivalence bound failed:
  the quiet/busy ratio was 1.22, with an interval reaching 1.49. The exploratory numbers below
  suggest that this ratio mostly reflects the busy side having slightly *fewer* choices (0.85 against
  FAST, CI 0.70–1.05), plus a left/right difference present even with no throttle. So: **no evidence
  that quietness changes the choices, but not proven equal either.**

### Exploratory (post hoc)

[`results/baseline_and_coupling_EXPLORATORY.txt`](results/baseline_and_coupling_EXPLORATORY.txt)

- **Deciding is shared; laying is local.**
  - Compared with FAST, the *undetermined* time in the HALF arm grows about equally in **both**
    halves: ×3.5 in the quiet half and ×4.2 in the busy half. The busy half is held back as much as
    the quiet one.
  - The *laying* time grows mostly where it is quiet: ×3.6 in the quiet half against ×1.3 in the
    busy half.
  - This is largely **built into the patient scheduler**. A guess waits until nothing is forced
    *anywhere*, so there is effectively one shared moment of decision for the whole patch.
- **The local clock for laying is the same everywhere.** A determined spot is laid after about
  **19 nearby happenings** in every arm and every half (18.4–20.5; HALF quiet/busy 0.94, 95%
  0.86–1.01). On its own clock, a quiet place isn't slower at all.
- **The halves differ even with no throttle** (FAST left/right T_U 1.66, CI 1.02–2.96). The seed and
  the guess location are not symmetric, so quiet/busy comparisons should always be read against
  this baseline.
- **Apparent choices while determined** average about 2. Locally, a spot often *looks* open when
  forcing elsewhere has already settled it.

## Limits

- One tiling family, one throttle, one target size.
- "Determined" means determined by the growth's local forcing rule, not by logic in principle.
- Choices are sampled (16 attempts, one-step look-ahead).
- The patient scheduler makes the moment of decision global by design.

## Files

- `continuation_choices.py` (`--summary` recomputes the report)
- `results/runs.jsonl`
- `results/continuation_choices_report.txt`
- `results/baseline_and_coupling_EXPLORATORY.txt`

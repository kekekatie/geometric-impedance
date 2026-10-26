# Closure pre-registration: does the surviving front still determine the deleted choice?

### Phase 2 of the paired-front pilot — the experimental closure for Paper 1

*Pre-registration. Written and committed **after** a validation gate established the measure (below) but
**before** the scaled confirmatory run. Argon's idea (5D window retrodiction); Katie (direction); Astra
(the separation of physical difference from readability, complete stop reasons, no arbitrary labels);
Claude (gauge fix, jam-censoring, this spec). The numbers are our called shots.*

---

## The question

From one common forced-saturated state `S*` where a fork still has two legal options, commit A in one arm
and B in the other and grow both with ordinary patient-scheduler growth. **After the original choice-tiles
are pruned out of the retained active skin, does the surviving ring alone still determine which option was
taken?** Two measures, plus one exploratory:

- **F1 — decoration-trace survival** (from the Phase-1 pilot): does the shared-ground blue/orange trace
  persist on the living skin after both choice-tiles are pruned?
- **F2 — 5D window retrodiction** (Argon's pure test): take **only** the surviving skin tiles (post-prune),
  compute their joint internal-space compatibility region `F(skin_t)` in the fork's gauge, and intersect it
  with the two original candidate regions `C^A`, `C^B`. If `F(skin_t) ∩ C^true > 0` while
  `F(skin_t) ∩ C^other = 0`, the living ring **uniquely retrodicts the committed option** with the
  alternative excluded to zero area — even though the choice-tile was deleted steps ago.
- **F3 — the Coiled-Spring / slack check (EXPLORATORY, secondary):** does the fork's birth decisiveness
  (**fingerprint stiffness**, and wall-nearness) predict how long/robustly the trace and retrodiction
  survive? NOT a confirmatory closure — E-prime's lean was weak and ~20 forks is low power.

## What this is, named honestly (Astra's distinction, kept)

F2 uses the **global lift** (absolute tile coordinates) and the fork's own two candidate regions. It is a
**retrodictability / information-presence** result — *the choice is provably still recoverable from the
surviving structure* — which is exactly the "memory without an archive" claim for Paper 1. It is **not** a
position-blind *local* observer (a myopic sensor that does not know where it is); that is a cleaner,
harder follow-up and is explicitly out of scope here. We will not phrase F2 as "an observer on the front
read it."

## The measure, and the validation gate it already passed (disclosed)

A one-fork-at-a-time gate was run **before** this pre-registration and fixed two things, both required:

1. **Gauge consistency.** `perp_map.lift` anchors its 5D coordinates at the first tile's vertex, so a
   *pruned* skin (a filtered subset) is lifted in a **shifted gauge** and its region is translated away
   from `C^A`/`C^B` (giving false "ambiguous"). Fix: lift the **full arm patch** (which starts with `S*`,
   so it shares the `S*`-anchored gauge of `C^A`/`C^B`) and read the skin's constraints from **that** lift,
   restricted to skin vertices and to `S*`'s four internal layers. With the fix, every clean arm's
   `F(skin_t)` equals its committed region `C^A` (area-exact) with `∩ C^other = 0`, to step 44.
2. **Jam censoring.** Some arms make a later free choice that grows into a global **contradiction** (a jam);
   a jammed tiling has *no* compatible offset, so `F = 0` legitimately. Jammed arms are **censored**
   (recorded with stop reason `jam`, excluded from F2 scoring), never counted as retrodiction failures.

The gate result (6 worlds): **6/6 A-arms and 3/3 non-jammed B-arms retrodicted the true option with the
alternative at exactly zero area, at step 44** — dozens of steps after the choice-tile was pruned (~7–10).
Jammed B-arms (worlds 5, 7) were censored. This pre-registration freezes that method; the scaled run below
is the confirmatory test.

## Set-up (fixed now)

- **~20–24 deduplicated forks.** Grow fresh worlds (wedge 300+); select the first forced-saturated fork
  with two legal options past a min patch size; **deduplicate by configuration** (`whole_key` of the fork
  neighbourhood) so seed near-duplicates (the worlds-2≡4 collision) cannot inflate the count.
- Per fork, per arm: ordinary growth to a fixed horizon; record choice-tile **departure** step, **jam**
  step (first step with empty `F(full)`), and all stop reasons. Retrodiction is evaluated only at steps
  that are **post-departure AND pre-jam**.
- Predictors recorded per fork: fingerprint stiffness, wall-nearness, patch age (for F3 and its age control).

## Predictions (called shots)

**F1 — the decoration trace survives the tiles.** In **≥ 70%** of distinct forks, the shared-ground trace
is still non-zero on the living skin after both choice-tiles are pruned. *Confidence ≈ 80%* (Phase-1 pilot
showed 6/7).

**F2 — the surviving ring retrodicts the deleted choice.** Among **non-jammed** arms, the surviving skin
pins the offset to its committed region and excludes the alternative to zero area at a post-departure step
in **≥ 90%** of arms (expected near 100% from the gate). We report the **jam rate** (censored arms) openly
as the real limit on coverage, and the **last post-departure step** at which retrodiction still holds (is
it maintained to the horizon, or does it eventually blur?). *Confidence ≈ 75%* that non-jammed retrodiction
is ≥ 90%; the honest content is the **persistence of the pin**, since the candidate regions are disjoint.

**F3 — decisiveness vs persistence (EXPLORATORY, two-sided, reported not scored).** Spearman(stiffness,
trace-persistence) and (stiffness, retrodiction-window) reported with sign and age control; **no pass/fail
bar** — flagged for a future, higher-powered test. *No confidence stated; this is a flag, not a claim.*

## Reported, but not scored

- Jam rate per option (is one option more dead-end-prone? worlds 5, 7 hinted B jams more).
- `F(skin_t)` area vs `C^true` area over time (does the pin stay area-exact, or loosen?).
- Front displacement (the permanent, separate consequence) for completeness.
- Fraction of forks where candidate regions `C^A`, `C^B` are disjoint (the exclusion's basis).

## Limits we already know

- Retrodictability (analyst + lift), **not** blind local decoding — stated, not hidden.
- The measure lives in `S*`'s four-layer internal slab; skin vertices outside it are dropped (reported as
  out-of-layer counts). As the front advances far, fewer skin vertices remain in-slab — a horizon on the
  method, not necessarily on the information.
- Jammed continuations are censored; the scored set is non-jammed arms only.
- RNG coupling after divergence is a convention; same-option background trace was ~0 in Phase 1, so later
  choices mostly displace rather than re-decorate.
- F3 is underpowered (~20 forks) and exploratory; no closure rests on it.

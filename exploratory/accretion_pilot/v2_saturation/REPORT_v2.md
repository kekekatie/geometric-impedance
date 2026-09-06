# Report v2 — timing-matched control, run toward saturation

*Plain-language write-up, written after the run. Register: speculative
exploration; not a confirmatory study, not cosmology. Bounded follow-up to v1
(commit `cc514eed26805e8448b669c813ff30776aa049ec`). Rules and parameters were
fixed in advance in [`DESIGN_NOTE_v2.md`](DESIGN_NOTE_v2.md) and used unchanged.
200 paired seeds, 10,000 subsequent steps. Reproduce with
`python accretion_pilot_v2.py`.*

## What we changed (only two things)

1. **The control's timing is now honest.** In v1 the matched control received its
   random diagonals in big batches *at measurement checkpoints*, so its edges were
   younger than Growing's and had fewer chances to shape movement. v2 replays
   Growing's activation counts **event by event** — during the imposed history and
   at every single subsequent step — placing edges at random among canonically
   sorted inactive candidates with a separate RNG, order *traverse → reinforce →
   activate*, asserting identical cumulative counts after every event. We call this
   **activation-time-and-count matched**. Positions and evolved weights are still
   unmatched; the *timing itself is inherited from Growing and can depend on
   history*, so only the control's **placement** is history-blind, not the whole
   control.
2. **We ran to 10,000 steps** (checkpoints 0, 100, 200, 400, 1000, 2000, 5000,
   10000) to watch the world head toward saturation.

Everything else is v1. As a gate, v2 reproduces v1's Fixed / Reinforced / Growing
results **per seed, exactly** (max abs diff 5e-7, i.e. CSV rounding; see
[`results/validation_vs_v1.txt`](results/validation_vs_v1.txt)). A fixture confirms
the checkpoint list does not change the trajectory. The v1 control is retained in
`../results/` for side-by-side comparison.

## What changed after fixing the timing

**The v1 conclusion survives the stricter control — and is if anything cleaner.**
Growing still carries more durable, more discriminable history than the
random-placement control, now with the age/timing confound removed. The paired
between-model bootstrap (resampling whole A/B seed pairs) shows the memory-AUC
advantage of Growing over the timing-matched control is significant at every
horizon we checked:

| Growing − Control | step 400 | step 2000 | step 10000 |
|---|---|---|---|
| memory AUC difference | **+0.141 [0.091, 0.190]** | **+0.172 [0.100, 0.235]** | **+0.095 [0.017, 0.170]** |
| effective-alternatives difference | +788 [747, 831] | +557 [507, 605] | +8.7 [4.9, 13.0] |
| structural-access difference | +3.1 [2.7, 3.5] | +0.0 [−0.1, 0.2] | −0.0 [−0.01, 0.0] |
| \|M_norm\| magnitude difference | +0.039 [0.022, 0.057] | +0.036 [0.027, 0.045] | +0.0002 [−0.0001, 0.0006] |

Read across the bottom two rows: by saturation the **opportunity gap essentially
closes** (both worlds end up with nearly all diagonals and nearly all weights at
6, so structural access and route diversity converge — Growing 4090 vs Control
4081 effective 4-step routes at step 10000), and the **memory-magnitude gap
vanishes too** (both `|M_norm|` shrink to ~0.002, and their difference is no longer
distinguishable from zero). Yet the **memory-AUC gap stays significantly positive**
(+0.095, CI excludes 0). History-shaped placement keeps a small but real *ordering*
advantage even after magnitudes have collapsed and resources have equalised.

**Magnitude vanishes; sign survives — exactly the distinction Astra asked for.**
This is the most important qualitative point and it is visible directly in the
numbers. At step 10000 the normalised contrast `|M_norm|` ≈ 0.002 for every
changing model — memory *magnitude* is essentially gone — but the paired ordering
score is still above chance (Growing 0.635, Reinforced 0.590, Control 0.525;
Fixed 0.500). A tiny **signed residual** keeps the histories orderable long after
their strength is negligible. So one must **not** infer chance-level decoding from
structural convergence, nor durable *practical* memory from a surviving sign.

**Growing vs Reinforced tells the complementary story.** Reinforcement alone
remembers but funnels: its effective alternatives sit *below* baseline for a long
time (107 at step 0, only reaching the initial 256 as its base edges saturate to a
uniform grid) and its structural access never moves off 40 (no new edges). Growing
beats it enormously on opportunity at all times (+3834 effective routes, +40
reachable vertices at step 10000). On memory, Growing leads Reinforced early
(AUC diff +0.109 [0.064, 0.155] at step 400) but the gap is **no longer
significant by step 10000** (+0.063 [−0.017, 0.140]) — once both are near
saturation their residual traces are comparable.

## The long-run reasoning, verified and made precise

Astra's reading — finite candidate set, bounded positive weights, no deletion,
persistent exploration ⇒ everything activates and every weight → 6 — is **correct**
as a limit, and we separate the three things it is easy to conflate:

1. **Structural convergence: yes, provably, in the limit.** The weighted walk is an
   irreducible recurrent Markov chain on a finite connected graph, so every present
   edge is traversed infinitely often and its weight → 6; every cell's four base
   edges then exceed the growth threshold, so every candidate eventually activates.
   Empirically the world is *heading there but not there yet at 10,000 steps*:
   fraction of candidates still inactive falls to 0.00004 (Growing activates
   127.995 of 128 candidates on average — a handful of seeds still miss one), and
   mean weight headroom `(6 − w)` falls to 0.017 (Growing) but not 0. **10,000 steps
   does not reach full saturation**, and we do not auto-extend.
2. **How long histories stay distinguishable: much longer than their magnitude.**
   As above — sign persists after magnitude collapses. At saturation itself the
   graph is symmetric (all weights 6, all diagonals present), so `M_A = M_B = 0` and
   decoding is exactly chance; the approach to that is slow and sign-dominated.
3. **Numerical rounding: real at the edge level, invisible at the aggregate level.**
   With `w ← w + 0.5(6 − w)` the gap `(6 − w)` halves per traversal, so after ~54
   traversals an edge is *exactly* 6.0 in float64. This shows up plainly: the
   fraction of present edges sitting exactly at 6.0 jumps late — Reinforced reaches
   0.82 by step 10000 (its 144 heavily-trodden base edges), Growing/Control 0.10
   (they spread traffic over ~272 edges, many far from the probe). **But exact ties
   in the *aggregate* readout `M_A == M_B` stay at 0.0000 throughout** (Fixed
   excepted, where everything is 0): `M` is a sum over ~270 floats, so individual
   saturated edges rarely make two whole worlds tie. We report both.

## Wording correction (carried from v1)

v1 called the subsequent evolution "symmetric erosion". Corrected: the *rule* is
symmetric between the two mirror histories, but an individual walker responds to
its own history-shaped weights and can **reinforce** the existing trace. The data
show this directly — Growing's raw contrast *rises* before it falls (mean `M_A`
84 → 113 over the first 400 steps) as the walker re-treads the worn side; only
later does homogenisation win and drive it toward 0.

## Reading the observables correctly

- **The paired ordering score is not single-world classification accuracy.** It
  asks, for each seed, whether that seed's A-world outscores its *own* paired
  B-world on a coordinate-defined symmetry contrast. It is a relative,
  coordinate-aided readout — memory *with external coordinates*, not intrinsic
  self-addressing.
- **Effective alternatives measures walk diversity including backtracking**, not
  the number of independent destinations and not useful transport. `exp(H)` over
  length-4 weighted walks counts how spread the next-four-steps distribution is; a
  walker that can step back and forth over a rich local neighbourhood scores high.
  It should not be read as "can reach more places usefully".

## What remains unresolved

- **Placement-near-the-probe is still a live confounder.** Growing's diagonals
  appear where the journey wore the world — which, for these histories, is right at
  the central probe. The timing fix removes the age confound but **not** the
  possibility that Growing's residual memory/opportunity edge is partly a
  *locality* effect (edges near the readout point) rather than a *history-shape*
  effect per se. We deliberately did not add more control families or parameter
  sweeps in this run, as instructed.
- **Unequal evolved weights remain unmatched.** We match activation count, timing
  and initial weight, not fully-evolved weight; Growing's diagonals sit on busier
  routes and end slightly heavier. Some of the residual advantage could ride on
  that.
- **Saturation is approached, not reached.** The very-long-run limit (exact chance,
  exact symmetry) is established analytically but not observed; the last mile is
  slow and sign-dominated.

## One worthwhile next question

Disentangle **locality** from **history-shape** with a single further control that
keeps everything v2 matches *and* matches placement locality: activate the same
per-event counts among the inactive candidates **closest to the probe**,
history-blind. If Growing still beats *that* control on the memory-AUC ordering,
the residual advantage is genuinely about the *shape* of the history and not merely
where the readout happens to sit. That is the clean test this pilot now sets up but
does not yet run.

# Twins in the hidden window — design note (mirrors first, messengers later)

*Register: speculative exploration. This is a design note plus one bounded exact feasibility
test ([`twins_mirror_feasibility.py`](twins_mirror_feasibility.py), exit 0). It is isolated from
the rest of the pilot, and prior studies are untouched. It bridges two pilot threads: the growth
model (`endogenous_*`, `pair_collision_toy/`) and the perpendicular-space geometry of
[`../fibonacci_address_environment/`](../fibonacci_address_environment/).*

## The question, and why it splits in two

In the Fibonacci chain, a site's **hidden (perpendicular) address** fixes its local environment.
Two sites whose addresses fall in the same window cell look identical out to radius `r`, however
far apart they are physically. These are **twins**. Their **first-disagreement radius `r*`** is
the first radius at which their environments differ. Closer addresses give a larger `r*`.

"Twins can inform each other" can mean two very different things:

| | **Mirrors** (this note) | **Messengers / resonance** (Phase 2) |
|---|---|---|
| mechanism | none: the rules are local in physical space and never read the address | a rule couples sites through their addresses |
| why twins match | same mould, same local world | a designed-in link |
| honest claim | "shared geometry ⇒ shared future, for this long" | "adding the link changes X beyond the mirror baseline" |

Mirrors have to come first. They are the **baseline** that any messenger effect must be measured
against. Without it we could not tell resonance apart from the twins simply resembling each
other.

## Phase 1 — mirrors: the model

All of these are modelling choices, and each is stated as one.

- **Substrate.** A patch of the exact Fibonacci chain. Every site starts **active**, and every
  tile is an active bond that carries its length `ℓ ∈ {L=τ, S=1}`.
- **Rule.** BUD at `k=1`, as in the transmission paper. The rule reads geometry in two ways:
  - `BUD(x,y)` fires at **rate `1/ℓ`**. That is MOTION.md's conductance choice, and since
    `1/τ = τ−1`, every rate is an exact element of `ℚ(τ)`.
  - New bonds **inherit** their parent bond's length.

  **No rule reads the address.**
- **Time.** Continuous, with an independent clock per event. This is the *local* form of
  "uniform over events". The discrete uniform lottery is the embedded chain of the rate-1
  version, but its normaliser, the total event count, couples far-apart sites. That would be a
  hidden messenger, so it is excluded.
- **Observable (feasibility).** `u(s) = P(the twin's own site is still active at time s)`. Expand
  it as `u(s) = Σ cₙ sⁿ/n!` with `cₙ = (Gⁿf)(X₀)`, where `G` is the generator. Each `cₙ` is
  computed exactly in `ℚ(τ)`.
- **Control.** The **blind** rule, with every rate equal to 1 and lengths ignored.

### Light-cone lemma (argued here; checked computationally)

`cₙ` depends only on the tiles within distance `n` of `v`, which is the environment `Eₙ`.

*Sketch.* `G` applied to a function of the bonds within distance `d` of `v` gives a function of
the bonds within distance `d+1`. The only events that change such a function are BUDs on those
bonds or on bonds touching their endpoints. BUD rewires only the bonds at `x` and `y`, and a new
tip hangs at distance 0 from its keeper. `f = 1[v active]` depends on the bonds at `v`, so `cₙ`
reads out to distance `n`.

*Check.* Enlarging the patch from radius `n` to `n+1` never changes `cₙ` (asserted, `n ≤ 4`).
**Consequence.** Twins with first disagreement at `r*` have `cₙ` equal for **every `n < r*`**.

## Phase 1 — the feasibility result (exact, 6 pairs)

| `r*` | sites | physical distance | address distance | first differing order |
|---|---|---|---|---|
| 1 | 20, 40 | 27.4 | 0.584 | **1** |
| 2 | 21, 44 | 31.7 | 0.348 | **2** |
| 3 | 21, 52 | 42.7 | 0.257 | **3** |
| 4 | 20, 46 | 35.9 | 0.112 | **4** |
| 5 | 21, 47 | 35.9 | 0.112 | **5** |
| 6 | 22, 48 | 35.9 | 0.112 | **6** |

- **The mirror law, on this rule.** For every pair, twins agree exactly at every order below
  `r*`, and the difference **appears exactly at order `r*`**, with no accidental cancellation.
  So `u_i(s) − u_j(s) = Θ(s^{r*})`: the hidden-address depth is the length of the shared future.
  Closer addresses mean deeper twins, a longer shared future, and a later divergence.
- **Blind control.** Every pair is identical at every computed order. The address has an effect
  only if some rule reads the geometry, here the tile lengths. That was expected, but it is now
  checked, and it is the pre-registration point for Phase 2.
- **Honesty about "shared".** In continuous time there is no hard light cone. At any positive
  time the twins differ, by an amount of order `s^{r*}`. What is exactly shared is the
  **short-time expansion up to order `r*−1`**, which is the analogue of MOTION.md's walk onset
  `2(r*−1)`.

## Phase 1 — the full experiment (proposed, not yet run)

1. **Beyond onset: the size of the shared future.** Compute the twins' local futures (the
   distribution of the radius-1 neighbourhood of `v`) over real time windows `s ∈ [0, S]`, with
   certified bounds, as in `pair_collision_toy/`. Report `TV_ij(s)` and ask: is `TV` monotone in
   the address distance `|Δq|` (at fixed `s`, over many pairs)?
2. **Substrate controls.**
   - Periodic `LSLSLS…`: every same-type site is an exact twin at all depths, so the shared
     future is total.
   - Randomly shuffled L/S with the same frequencies: there is no address, so twins are
     accidental and short.
   - Fibonacci should sit between them. That is the quasicrystal signature.
3. **Add CONTACT.** This needs a length rule for the new bond, for example the mean of the two
   mediating bonds, or `L` always. It lets archive-mediated coupling in, and asks whether the
   mirror law survives or the archive adds a second, slower channel.
4. **Scale.** The feasibility code enumerates `Gⁿf` with memoisation and takes about 7 minutes
   for `n ≤ 6`. Going past `n ≈ 8` needs the reduced-state tricks from `pair_collision_toy/`.

## Phase 2 — messengers, and Katie's resonance idea (parked, with its test pre-registered)

**The idea, in Katie's framing.** An accreting universe that only accretes and does not keep
losing things. Something like a **resonant event**, triggered between hidden-window twins, lets
the geometry of perpendicular space hold on to what ordinary, non-resonant dynamics lets
collapse.

**Where the pilot already sees loss.** It sees it in two exact places:

- **Menu monotonicity** ([`../endogenous_contact_timing/`](../endogenous_contact_timing/)). A
  quiet trace's menu only shrinks. Once it is empty, the trace can never matter again.
- **The collapse lemma** ([`../pair_collision_toy/BUD_RECURRENT_LEMMA.md`](../pair_collision_toy/BUD_RECURRENT_LEMMA.md)).
  Under BUD-only, the active structure always collapses to a bare matching. `B` only falls.

GRAFT ([`../endogenous_graft_experiment/`](../endogenous_graft_experiment/)) was a first
*local* renewal rule. Resonance would be a **non-local but geometric** one.

**A candidate rule (to be refined together).** `RESONATE(t, v)`: a dead quiet trace `t` is
re-opened, getting one new CONTACT pair, when an active vertex `v` lies in the **same depth-`r`
address cell** as `t`, meaning the trace "hears its twin". Its rate is `ρ` and its resonance
depth is `r`.

**Open design question.** Grown vertices, the tips, have no Fibonacci address. Candidates:

- inherit the keeper's address, so a lineage shares one address;
- inherit the depositor's address, so an address moves forward;
- an address built from both, such as a midpoint in perpendicular space.

This choice decides what "twin" means once growth starts.

**Pre-registered test.**

- **Outcome.** The long-run number of live (menu-bearing) traces. It is 0 under BUD+CONTACT by
  menu monotonicity. Does resonance keep it positive, stationary and accreting?
- **The essential control.** **Address-blind revival at the same rate `ρ`**, which re-opens a
  random dead trace. If blind revival preserves as much, the effect is *any revival*, not
  *geometry*. The claim "perpendicular-space geometry is what preserves" needs resonance to beat
  blind revival.
- **Second control.** The same resonance rule on the **shuffled** substrate, where there are no
  true twins.
- **Mirror baseline.** Phase 1's `TV(s)`. The messenger effect is whatever resonance adds beyond
  it.

## What this is not

This is a geometric mechanism toy. It makes no claim about physics, cosmology or
quasicrystal materials. "Resonance" is a name for a designed-in rule, not a discovered physical
phenomenon.

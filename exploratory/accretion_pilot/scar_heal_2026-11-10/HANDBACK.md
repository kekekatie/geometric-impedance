# HANDBACK — can forgetting heal a scar?

*2026-11-10. For Katie / Fable / Astra. Pre-registered in `PROTOCOL.md` (commit `5a86554`) with the
harness validated (SKIP reproduces the committed ablation; NULL == SKIP) before the HEAL arm took a
step. An intervention world: the growing edge acts, departing from the paper's runs. Frozen
engine/lift/reader `84130b9` unchanged; nothing written to any paper cache; nothing fed back into a
scientific constructor.*

## For Katie, in plain words

**What we asked.** Brief 2 found the thinned skin's hidden address *predicts* the tile `c` at the
world-7 step-35 scar, and never contains the deleted "witness" tile — the witness is foreign to the
neighbourhood. This brief lets the thinned world act: peel the skip label, lay `c`, and keep
building. Does the floor heal, does the flaw move, or does it come back?

**What came back.** **The floor heals.** The moment the scar is reopened the scheduler lays `c` (its
only legal tile), the former scar edge becomes an ordinary interior edge, the neighbourhood settles
into legal arrangements, no new scar appears anywhere near it, and by the end of the watch the
healed world carries **one fewer scar** than the untouched baseline. The foreign witness tile *was*
the whole scar; forgetting it removed the obstruction. (See `figures/heal_w7_s0.png`: the open blue
edge on the left becomes `c` filling the gap on the right.)

**But the forgetting is what did it.** Two control arms matter. If you take the **full history** and
delete only the one witness tile, `c` does go in — but the floor does **not** heal: three new scars
pop up right beside it and it ends with *more* scars than the baseline. And if you drop the skip
policy **entirely** and refill every dormant scar, the world ends with far more scars still. So it
is not "one foreign tile" that heals the scar — it is that the thinned skin has *forgotten enough*:
exactly the interior that would otherwise fight `c`. The healing and the forgetting are the same
act.

**What it does not show.** The growing world does **not** consult its address or choose to forget —
the engine's rule is local, and this is a deliberate outside intervention, not something real growth
does. It is one scar in one world, a short watch (to step 60), with correlated replicates. It makes
no claim about the paper's runs, about scars healing in general, or about real growth forgetting.

## The arms (world-7 stream-0, radius 2S, from the step-35 checkpoint; horizon N = 60)

| arm | intervention | result at horizon |
|---|---|---|
| **SKIP** | none (baseline) | reproduces committed ablation to step 44; **14 scars** at N (12 at step 44) |
| **NULL** | unpin + re-pin, place nothing | **identical to SKIP** (harness check) |
| **HEAL** (primary) | unpin `e`; scheduler places `c` | `c` at step 36; **edge `e` closes at step 36**; no new scar within 3·S; **13 scars** (one below SKIP); no arrest; **0 A-only calls** in the identity readout → **A. Heals** |
| **ONE-TILE** | full history − witness; place `c` | evaluator menu after removal is **exactly `{c}`** (the witness alone is the blocker); `c` placed, edge closes, **but 3 new scars within 3·S** and **16 scars** at N → does **not** heal |
| **REQUERY** | fill every 1-candidate pinned scar each step | **20 scars** at N → the skip labels are protective as a whole |

**Settling (HEAL, at N):** of `c`'s three vertices, one has a complete star and it is **legal**
(degree 6, `L.star ∈ L.STARS`); the other two are still on the growing boundary (incomplete) by the
short horizon, so no star at `c` is complete-and-illegal. **Identity readout (HEAL band at N):**
open 5 B / 19 empty; closed 3 B / 2 ambiguous / 19 empty; **0 A calls** (both conventions). **Local
address:** the π/8 window `F(W)` around the site is tracked each step. **Divergence from SKIP:** step
36 (immediate, by construction — HEAL places the extra tile).

## Replicates (correlated; the w7 arms share one scar, group-3 share another)

| case | radius | class | HEAL: c@ / close@ / new-scars-3S / scars@N | note |
|---|---|---|---|---|
| **w7-s0** | 2S | **A. Heals** | 36 / 36 / 0 / 13 (SKIP 14) | primary |
| w7-s1 | 2S | A. Heals | 36 / 36 / 0 / 13 | stream replicate |
| w7-s0 | 3S | A. Heals | 38 / 38 / 0 / 13 | wider skin also heals |
| w7-s0 | 1S | B. Moves | 27 / 27 / 4 / 14 | thin skin: the misfit is displaced |
| w15/w19/w28-s0 | 1S | B. Moves | 43 / 43 / 4 / 12 | group-3: least-assured (Brief 2 withheld their headline) |

The result is **graded**: the richer the retained skin (2S, 3S) the cleaner the heal; the thinner
(1S) or more degraded (group-3), the scar closes but the misfit moves nearby rather than vanishing.
Every ONE-TILE arm confirms the evaluator menu is exactly `{c}` after the witness is removed, yet
none of them heals as cleanly as the thinned HEAL arm — "one foreign tile" is too simple.

## Declared outcome

**A. Heals** (primary w7-s0-r2, SKIP reproduced, NULL == SKIP, bounded by the horizon N = 60): for
this scar and horizon, deleting the foreign witness removed the obstruction. The skip label was
preserving a verdict the reduced world no longer needed. Read beside it: **ONE-TILE does not heal**
→ the rest of the deleted interior also mattered; the healing is a property of the thinned world, not
of removing a single tile from full history. Precedence applied as pre-registered (no arrest, no
scars-above-SKIP, no A-call → not D; no complete-illegal star → not C; closed ∧ legal ∧ no 3·S scar
∧ scars ≤ SKIP−1 → A).

**Trilogy, in one line.** Brief 1: the vertex-reader is *blind* to `c`. Brief 2: the hidden address
*predicts* `c` (`p_c = 1`), the witness is address-foreign. Brief 3: acting on that prediction in the
thinned world *heals* the scar — and the forgetting is what makes the healing possible.

## Scope and numerics

One scar in one world, horizon step 60 (step 44 the paper-comparison point), correlated replicates.
An intervention world that departs from the paper's runs and makes no claim about them. No claim that
scars heal in general or that real growth forgets. Float reproduction with the ablation's tolerances
(`verify_legal`; convex-clip `1e-12`; reader `1e-9`/`1e-12`). `S` = engine edge length ≈ 0.02129;
"near the site" = within 3·S of `e`'s midpoint. All five arms run on their own reconstructed copy of
the checkpoint; outputs only to this study folder.

## Files / reproduce

`PROTOCOL.md`, `scar_heal.py`, `scar_heal.json` (raw per-arm, per-case), `make_figure.py` →
`figures/heal_w7_s0.png`, `HANDBACK.md`.

```bash
export EFP_SNAPSHOT=<84130b9>/exploratory/accretion_pilot/expansion_front_paper
export MPLBACKEND=Agg PYTHONUTF8=1 AMBER_BASE_CACHE=<base> AMBER_CACHE=<scratch> AMBER_FORK_CACHE=<forks.pkl>
cd scar_heal_2026-11-10
python3 scar_heal.py harness            # SKIP + NULL + horizon
python3 scar_heal.py run scar_heal.json
python3 make_figure.py
```

No merge, no force-push; branch `claude/scar-heal-2026-11-10` from `100c06e`.

# Stage 2, Component 2: does the diamond recover the same-deadline decision?

*Results for `stage2_surface.py` + `stage2_run.py`, frozen by Amendment A of
`PREREGISTRATION_2D.md` (`d22dbe9`). Replay: `python3 stage2_surface.py` (self-checks)
then `python3 stage2_run.py` -> `stage2_handback.json`. d=3 rotated patch, bulk loss
at (1,1), 68,128 histories (weight ≤ 2), exact two-sector onset-averaged decoder.*

**Joined causal pipeline (per Sol).** The sparse scar archive is built **before the
flag names the site** (site-agnostic fired-check coordinates). Each arm then **restarts
from the serialized state alone** and reads only what it kept — thin-alone reads
live + boundary; thin+diamond and thin+whole **query the one shared archive** (a fired
check → 1, a quiet one → 0). A self-check confirms the restart reproduces the direct
decode on all 68,128 histories (0 mismatches), so the result below is from the real
keep-then-restart pipeline, not from reading the simulator's record.

## One-line answer

The local diamond recovers the same-deadline reference on **99.994%** of the ensemble —
an **11× cut** in disagreements vs a thin window alone (5679 → 514) — so it is the right
*local* object for the loss. But the 514 residual disagreements are **not** all the
diamond being worse: on **150** of them the diamond is *correct and the reference is
wrong*. Agreement with the reference is not correctness, and pure locality is sometimes
better than the full soft reference on a rare individual history.

## The four arms (d=3 bulk, weighted by model prior)

| arm | agreement vs reference | logical correct vs truth | raw disagreements | query readings | peak storage (bits) |
|---|---|---|---|---|---|
| Thick window | 1.000000 (ref) | 0.995904 | 0 | all | 40 (full window) |
| Thin alone | 0.994111 | 0.992025 | 5679 | 0 | 24 (live 16 + boundary 8) |
| **Thin + diamond** | **0.999944** | 0.995880 | **514** | **≤ 8 fixed, local** | 64 (24 + archive) |
| Thin + whole archive | 1.000000 | 0.995904 | 0 | mean 3.33 fired | 64 (same archive) |

## Scorecard (frozen C1–C5)

| | prediction | verdict |
|---|---|---|
| C1 | thin+diamond ≥ 99% agreement, far above thin-alone | **HELD** (0.99994 vs 0.9941; 11× fewer disagreements) |
| C2 | thin+whole-archive == thick == reference exactly | **HELD** (0 mismatches over 68,128) |
| C3 | thin-alone strictly more disagreements than thin+diamond | **HELD** (5679 > 514) — the 2D witness exists |
| C4 | if whole beats diamond, resolving readings lie outside the star | **HELD** (514 cases; resolving reading outside the star) — *but see the correctness nuance* |
| C5 | diamond query ≤ 8 fixed; whole = O(pruned fired) | **HELD** (diamond 8; whole mean 3.33 at p=1e-3) |

Self-checks: restart == direct decode (0); whole-archive == thick (0); sparse and dense
archives reconstruct the same readings including quiet checks = 0.

## Agreement is not correctness (the Sol nuance, quantified)

Of the **514** histories where thin+diamond disagrees with the same-deadline reference:

| | count |
|---|---|
| diamond matches truth → **the reference is wrong** | **150** |
| reference matches truth → the diamond is wrong | 364 |
| both wrong | 0 |

So a third of the "locality gap" is the reference — an *optimal soft decoder at the
deadline* — mispredicting a rare individual history, where the local diamond happens to
be right. This is why the diamond's correctness-vs-truth (0.995880) sits a hair below
thick's (0.995904): its 364 genuine misses are nearly offset by 150 cases where it beats
the reference. The capstone claim is therefore even gentler than Component-2's first
pass suggested: the diamond is *not* strictly worse than the full record for being
right — it is differently wrong, and sometimes more right.

**The replayable example.** Faults `X@(0,0) round 0` and `X@(0,0) round 4` on the corner
qubit (0,0), far from the loss. **Reference = 1, truth = 0, diamond = 0** — the diamond
is correct and the reference is wrong. The single resolving reading is the pruned fired
check **`Z-stab 0 at round 0`** (in (0,0)'s star, *outside* the loss diamond `{1,2,5,6}`):
putting just that one old reading into the diamond flips it from 0 to 1 — i.e. onto the
*reference's wrong* answer. So the reading that "resolves" the disagreement toward the
reference here actually resolves it toward the error.

## Memory and query size (honest at d=3)

Peak retained state through the flag: thick 40 bits (full uncommitted window), thin 24,
thin+diamond = thin+whole = 64 (they keep the **same** archive). At d=3 the archive's
coordinate overhead (5 bits/event) makes thin+archive peak *larger* than the tiny dense
window — the Component-1 crossover: on a small patch "keep every fired check's address"
costs more than "keep the whole dense window." The storage **saving is a larger-d
phenomenon** (Component 1: it grows with `N·L` and as `p→0`). What is already distance-
independent here is the **query**: the diamond reads a fixed ≤ 8 local positions whatever
the archive holds, while the whole arm reads every archived event (mean 3.33).

## What this establishes, and the next step

- The 2D re-judgment witness is real (C3); the onset-lip diamond is the right *local*
  restoration (C1), recovering the same-deadline decision to 99.994% from a genuinely
  serialized, site-agnostic, pre-flag archive (restart verified).
- Locality is not *exact* (C4): 514 cases differ from the full record — but on 150 of
  them locality is the one that is right. "Thin + bracket = thick" holds for the loss;
  beyond it, the diamond and the full record simply make different rare errors.
- **Decision on boundary / d=5.** Two questions the d=3 bulk run sharpens: does the
  locality gap (and its diamond-right share) *grow* with distance, and does the storage
  saving turn positive once `N·L` is large enough to beat the coordinate overhead? Those,
  plus the boundary-loss case (3-check diamond, D4), are the natural next run. The d=3
  bulk deliverable is complete.

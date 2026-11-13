# Stage 2, Component 2: does the diamond recover the same-deadline decision?

*Results for `stage2_surface.py` + `stage2_run.py`, frozen by Amendment A of
`PREREGISTRATION_2D.md` (`d22dbe9`). Replay: `python3 stage2_surface.py` (self-checks)
then `python3 stage2_run.py` -> `stage2_handback.json`. d=3 rotated patch, bulk loss
at (1,1), 68,128 histories (weight ≤ 2), exact two-sector onset-averaged decoder.*

## One-line answer

**Mostly, but not completely — and the gap is informative.** The local diamond
recovers the same-deadline reference on **99.994%** of the ensemble (weighted), an
**11× reduction** in disagreements versus thin-alone (5679 → 514), so it is the right
*local* object for re-judging the loss. But it is **not** exactly the thick window:
**514 cases** need pruned readings *outside* the lost qubit's star, which only the
whole archive keeps. Pure locality around the loss is necessary and highly effective,
but a thin window still sheds re-judgment-relevant detectors elsewhere.

## The four arms (d=3 bulk, weighted by model prior)

| arm | agreement vs reference | logical correct vs truth | raw disagreements | query readings | memory (bits) |
|---|---|---|---|---|---|
| Thick window | 1.000000 (ref) | 0.995904 | 0 | all detectors | full record |
| Thin alone | 0.994111 | 0.992025 | 5679 | 0 beyond live+boundary | live 16 + boundary 8 |
| **Thin + diamond** | **0.999944** | 0.995880 | **514** | **≤ 8 (fixed, local)** | live 16 + boundary 8 + diamond 8 |
| Thin + whole archive | 1.000000 | 0.995904 | 0 | mean 3.33 fired (O(pruned fired)) | live 16 + boundary 8 + archive |

## Scorecard (frozen C1–C5)

| | prediction | verdict |
|---|---|---|
| C1 | thin+diamond ≥ 99% agreement, far above thin-alone | **HELD** (0.99994 vs 0.9941; 11× fewer disagreements) |
| C2 | thin+whole-archive == thick == reference exactly | **HELD** (0 mismatches over 68,128) |
| C3 | thin-alone strictly more disagreements than thin+diamond | **HELD** (5679 > 514) — the 2D witness exists |
| C4 | if whole beats diamond, resolving readings lie outside the star | **HELD, and it happens**: 514 cases, resolving readings outside the loss star (not hidden) |
| C5 | diamond query ≤ 8 fixed; whole = O(pruned fired) | **HELD** (diamond 8; whole mean 3.33 at p=1e-3) |

Self-checks all passed: whole-archive == thick on every history; the sparse fired-check
archive and the dense lip-plane reconstruct the **same** readings (quiet checks = 0);
`decode_arm` is a pure function of each arm's serialized evidence, so a fresh restart
reproduces it.

## The locality gap (C4), honestly

The 514 diamond-misses are all one-directional: **whole recovers, diamond misses; never
the reverse.** A replayable example: faults `X@(0,0) round 0` and `X@(0,0) round 4` on
the corner qubit (0,0) — far from the loss at (1,1). The round-4 reading is live; the
**round-0 reading is pruned**, and it fires Z-stab 0, which is in (0,0)'s star but
**not** in the loss diamond `{1,2,5,6}`. The diamond arm therefore cannot pair the two
X-errors and mis-judges; the whole archive keeps that pruned Z-stab-0 reading and
re-judges correctly. So the resolving reading is a pruned fired check **outside the loss
star** — exactly the failure mode C4 named.

**What this means.** The diamond solves the *loss-locality* problem: nearly all of
thin-alone's extra failures were loss-neighbourhood re-judgments, and the diamond fixes
them (5679 → 514). The residual 514 are not about the loss at all — they are ordinary
pruned errors on the logical support that a thin window sheds regardless, and that only
a full archive restores. So **"thin + local bracket = thick" holds for the loss, but a
thin window is not a full substitute for a thick window in general.** At a realistic
error rate the residual is tiny (0.006% weighted), because those cases are rare
multi-error configurations — but it is non-zero, and it is a genuine limit on pure
locality, not an artefact to sweep away.

**Caveat (frozen choice).** The gap is measured against this protocol's minimal carried
state (boundary = the round-2 syndrome, 8 bits). A richer committed frame would carry
more of the pruned region and shrink the 514; the number is an upper bound on the
locality failure given the thinnest honest boundary.

## Memory and query size

At p = 1e-3 the whole-archive's mean readings (3.33 fired) are actually **fewer** than
the diamond's fixed 8 — syndromes are sparse, so "keep every fired check" is cheap. The
diamond's advantage is that it is **bounded and local** (≤ 8 readings regardless of
patch size or error rate), while the whole archive grows with the firing rate and the
patch. The trade is the one Component 1 quantified: local-bounded vs
activity-proportional.

## What this establishes, and the next step

- The 2D re-judgment witness is real (C3), and the onset-lip diamond is the correct
  *local* restoration for it (C1), recovering the same-deadline decision to 99.994%.
- Pure locality is **not exact** (C4): 514 rare cases need pruned information outside the
  star — the capstone "thin + bracket = thick" is true for the loss but not in general.
- **Decision on boundary / d=5 (per the protocol).** The interesting open question the
  d=3 bulk run surfaces is whether the locality gap *grows* with distance (more room for
  distant pruned errors on a longer logical) or stays a rare-multi-error tail. That —
  and the boundary-loss case (smaller diamond, D4) — is the natural next run. The d=3
  bulk deliverable is complete.

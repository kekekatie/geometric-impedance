# PROTOCOL — can forgetting heal a scar?

*Pre-registered 2026-11-10, committed **before** the HEAL arm takes its first step (SKIP and NULL
ran first as harness checks). For Katie / Fable / Astra. An **intervention** world: the growing
edge acts, departing from the paper's runs — placing `c` is illegal against full history by
definition. Nothing here is written into any paper cache; frozen engine/lift/reader `84130b9`
unchanged; nothing feeds back into a scientific constructor.*

## Question

Brief 2 found that at the world-7 step-35 scar the nearby skin's hidden address predicts the
candidate `c` (`p_c = 1`) and never contains the deleted witness tile — the witness is foreign to
the local pattern. This brief lets the thinned world act on what it has: reopen the dormant scar,
place `c`, keep growing. Does the scar heal, move, return, or spread? The referee checks found zero
perp-space holonomy on all 190 loops (scars carry no conserved defect charge), so nothing known
forbids a scar vanishing — a reason the first outcome is *possible*, not a prediction.

## Checkpoint, scar, candidate (reproduced; harness validated before this commit)

The arms start from the world-7 stream-0 live-only (radius 2S) checkpoint **after step 35**,
reconstructed in-process from the committed serialized step-23 state and stepped forward with the
frozen scheduler. The in-process harness reproduces the committed ablation placements/tiles/scars
at every step 23–44 (SKIP), and NULL equals SKIP. Scar edge
`e = [(0.628274, -0.079527), (0.640786, -0.062306)]`; candidate
`c = (1, …, (0.640786, -0.096748))` (the single reduced-menu tile, full-history menu empty).

## Horizon

**N = 60** (one horizon for all arms). SKIP was verified to run to step 60 without arrest (band
485→642, scars 12→14). **Step 44** is recorded as the paper-comparison checkpoint. Every outcome
class is bounded by the horizon: "heals" means "no trouble seen by step 60".

## Arms (own copy of the checkpoint each; same frozen scheduler and serialized RNG)

| arm | state | intervention |
|---|---|---|
| **SKIP** | live-only skin 2S | none; scar stays pinned (baseline) |
| **NULL** | live-only skin 2S | unpin and re-pin at once; place nothing (== SKIP) |
| **HEAL** | live-only skin 2S | **unpin `e`**; the forced scheduler places `c` (its only candidate); continue live-only (primary arm) |
| **ONE-TILE** | full history **minus the witness tile** | unpin `e`; require the evaluator menu at `e` to be exactly `{c}` (else report menu and stop); place `c`; continue with full history retained |
| **REQUERY** | live-only skin 2S | from step 35 on, each step every pinned scar with **exactly one** legal candidate is unpinned and filled (no skip policy); secondary |

## Measurements (per arm, to horizon)

1. **Closure** — the former scar edge `e` leaves the frontier (both sides occupied); record the step.
2. **Settling** — at `c`'s three vertices, when the star is complete (angle sum 2π), does it pass
   the frozen complete-vertex-star check (`L.star ∈ L.STARS`)? Report each vertex (angle sum,
   degree, complete, legal).
3. **New scars near the site** — any scar pinned after the intervention whose edge midpoint is
   within **3·S** (`S` = engine edge length ≈ 0.02129) of `e`'s midpoint; record step and distance.
4. **Scar ledger** — total pinned scars per step per arm; the difference from SKIP at the horizon.
5. **Arrest** — whether any arm reaches a step with no forced and no free site (`total_arrest`).
6. **Local address** — `F(W)` area of the committed π/8 window around the scar, recomputed on the
   HEAL band each step; does it stay non-empty as the gap fills?
7. **Identity readout** — the 24-window native + closed reader grid (6 centres × 4 half-widths) on
   the HEAL band at the horizon, both conventions, never merged. **Any A-only call on this
   B-committed world is reported first.**
8. **Divergence** — the first step at which HEAL's placements differ from SKIP's, and (from the
   ledgers and bands) how far the difference has spread by the horizon.

## Outcome classes (declared; read off HEAL on w7-s0-r2, with SKIP reproduced and NULL == SKIP)

- **A. Heals** — scar closed; every complete star at `c`'s vertices legal; **no** new scar within
  3·S; scar total ≤ SKIP − 1 at the horizon. *Deleting the foreign witness removed the obstruction.*
- **B. Moves** — scar closed, but ≥ 1 new scar within 3·S. *The misfit was displaced; report where.*
- **C. Returns** — a complete star at a vertex of `c` that is **not** legal (or a new dead site
  sharing a vertex with `c` within two steps). *The local rule admitted a tile the wider skin cannot
  absorb.*
- **D. Spreads** — more scars than SKIP at the horizon, an arrest, or any A-only identity call.
  *Report the damage first.*

Precedence (fixed): D if arrest or scars > SKIP or any A-only call; else C if any complete-but-
illegal star at `c`; else A if closed ∧ stars legal ∧ no new scar within 3·S ∧ scars ≤ SKIP−1;
else B if closed ∧ a new scar within 3·S; else report the table with no clean class.

The **ONE-TILE** arm is read beside the class, not as part of it: if HEAL heals and ONE-TILE does
not, the rest of the deleted interior also mattered and "one foreign tile" is too simple. Every
statement is labelled by who could know it — the growing edge, or only the reader.

## Brief 2 follow-up

Brief 2's Gate 1 confirmed that the ideal patch at the sampled offsets contains every **vertex** of
the window W (so every W tile, which the reader sees by its vertices). The decorated-tile
reproduction is noted here as confirmed at vertex level; a decorated-triangle cross-check is added
if cheap.

## Rules, scope, deliverables

Isolation: each arm on its own reconstructed checkpoint; outputs only to this study folder and
scratch, never a paper cache. Correlated labels: the world-7 arms (s0/s1, radii 1S/2S/3S) share one
physical scar; group-3 (w15/w19/w28 at step 42) are a separate labelled set (Brief 2 withheld their
headline — least-assured healing). Float reproduction, same tolerances as the ablation
(`verify_legal`, convex-clip `1e-12`, reader `1e-9`/`1e-12`). Scope to restate: one scar in one
world, short horizon, correlated replicates; an intervention world that makes no claim about the
paper's runs; no claim that scars heal in general or that real growth forgets.

Deliverables: `PROTOCOL.md`, `scar_heal.py`, `scar_heal.json` (raw per-arm), `HANDBACK.md`
(plain-language first; one table of arms × measurements; declared class; a before/after figure of
the scar site at the intervention step and the horizon). Branch `claude/scar-heal-2026-11-10` from
`100c06e`; no merge, no force-push.

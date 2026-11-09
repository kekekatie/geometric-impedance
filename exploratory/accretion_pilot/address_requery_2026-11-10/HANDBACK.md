# HANDBACK — can the skin's hidden address re-judge a dormant scar?

*2026-11-09 (brief dated 2026-11-10). For Katie / Fable / Astra. One small diagnostic on a world
already grown. Pre-registered in `PROTOCOL.md` (commit `30afe8d`) with the window tile lists fixed
in `protocol_windows.json` before any `F(W + c)` was computed. Frozen engine/lift/reader `84130b9`
untouched; the scar stays skipped; nothing here fed back into any constructor.*

## For Katie, in plain words

**What we asked.** At the first dormant-scar disagreement (world 7, step 35), the reduced live
skin's *local rule* lets in a tile `c` that the full history forbids. The *window reader* is a
different instrument — it can sometimes see a clash in the hidden (perpendicular-space) address
that the local rule misses. So: can the reader, from the reduced skin alone, **reject** `c` at the
scar — i.e. is the "reason" the skin shed still recoverable from the pattern around it?

**What came back.** **No — not here.** Adding `c` to the window around the scar changes the
reader's compatibility region `F` by **nothing at all**: `F(W + c)` is identical to `F(W)` at
every window size and under both conventions, in all seven correlated cases. So the reader never
rejects `c` at the scar. On small windows it *admits* `c` (it fits); on wide windows the region is
already empty, so the reader is *silent*. Restoring the one deleted neighbour (the "reason" tile)
doesn't change this. And we checked the reader isn't just asleep: it never wrongly rejects a true
tile (0/clean), it does reject some locally-illegal tiles, and — tellingly — it **does** reject
`c` when `c` is dropped into windows **far from the scar** (a quarter to three-quarters of the ring
away). In other words, the only place the reader rejects `c` is where `c` obviously doesn't belong;
at the scar's own neighbourhood, the hidden address has nothing to say against it.

**What it does *not* show.** It does not show the growing world "uses" its address (the engine's
rule is local — this was only ever about what a reader can recover). It is one query in one world
with correlated replicates, a numerical reader under two conventions (not a symbolic proof), and it
says nothing about other scars, longer horizons, or other tilings. The honest one-liner for the
paper: *the shed reason was local to the corner record; a window address-reader does not recover
it.*

## Gate 0 (both reproduced before the test)

- The step-35 query reproduces `amber_lobe_audit_2026-11-07/independent_query.json` exactly: pinned
  edge `[(0.628274, -0.079527), (0.640786, -0.062306)]`, reduced menu one tile
  `c = (1, …, (0.640786, -0.096748))`, full-history menu empty.
- The full-band 528-window native reader grid reproduces **111 B / 64 ambiguous / 353 empty / 0 A**.

(The rebuilt fork cache serialises to a different pickle SHA than the amber run — an environment
difference recorded in the protocol; content faithfulness is certified by these two reproductions,
not the hash.)

## Result (window × convention × class), per case

`F(W + c) = F(W)` in **every** window below (same area, same Chebyshev radius), so `c` is never the
binding constraint at the scar; there is **no REJECT at any scale**. Narrow→wide the class runs
ADMIT → UNDEFINED as the region empties.

| case | radius | step | hw=π/8 | hw=π/4 | hw=π/2 | hw=3π/4 (primary) | whole skin |
|---|---|---|---|---|---|---|---|
| **w7-s0** (primary) | 2S | 35 | ADMIT | UNDEFINED | UNDEFINED | **UNDEFINED** | UNDEFINED |
| w7-s1 (replicate) | 2S | 35 | ADMIT | UNDEFINED | UNDEFINED | UNDEFINED | UNDEFINED |
| w7-s0 | 1S | 26 | ADMIT | ADMIT | ADMIT | UNDEFINED (open) / ADMIT (closed) | UNDEFINED |
| w7-s0 | 3S | 37 | ADMIT | UNDEFINED | UNDEFINED | UNDEFINED | UNDEFINED |
| w15-s0 | 1S | 42 | ADMIT | ADMIT | UNDEFINED | UNDEFINED | UNDEFINED |
| w19-s0 | 1S | 42 | ADMIT | ADMIT | UNDEFINED | UNDEFINED | UNDEFINED |
| w28-s0 | 1S | 42 | ADMIT | ADMIT | UNDEFINED | UNDEFINED | UNDEFINED |

Open and closed agree except at the w7-s0 1S primary window, where `F(W)` is a measure-zero point:
open (positive-area) reads UNDEFINED, closed (feasible-including-boundary) reads ADMIT. The classes
are reported separately and never merged. The candidate lifts consistently against the retained
skin in every case (`lift_c.consistent = true`).

## Controls (same state and window sizes)

| control | what a healthy reader shows | result |
|---|---|---|
| **True-tile** (interpretation gate) | ADMIT every defined window; 0 false rejects | **Clean: 0 false rejects**, open and closed, every case. The headline may be read. |
| **Wrong-tile** (sensitivity) | some REJECTs | Non-zero where defined: e.g. w7-s0-1S 4/9 (open), 2/9 (closed); group-3 2/6, 1/6. The reader can say no. |
| **Restored-state** (witness tile added to the window) | class once the reason is present | `F(W')` stays empty and `F(W' + c) = F(W')`: restoring the deleted neighbour does **not** give the window reader rejection power. The reason is a corner-level fact the address test does not reconstruct. |
| **Displaced-window** (c added far from the scar) | local vs global | **REJECT** in 13 of the far windows (w15/w19/w28 at half & three-quarter ring; w7-s0-1S at a quarter). Any rejection of `c` is a *global* "foreign tile" effect, **not** a local scar re-judgment. |

## Declared outcome

Read off the primary window (w7-s0, true-tile control clean): **primary = UNDEFINED under both
conventions (class C at the primary scale)**, but the class **changes along the ladder** (ADMIT at
narrow half-widths), so the formal declared class is **D (Split)** — *"report the full table; the
scale at which the class changes is the finding."* The decisive, scale-invariant fact behind the
table is that **`c` never changes `F` at the scar**, so the address never rejects `c` there. In the
language of the pre-declared classes this lands on **B's conclusion** — *the reason lives only in
the shed corner; reconsideration needs the local witness even for a window reader* — reached through
a C/D-shaped table rather than a clean ADMIT.

## Witness (where the reason is *not*)

Where `F(W)` is empty, its minimal infeasible set is 2–3 half-planes supplied by retained tiles
**other than** `c` and other than the deleted neighbour (recorded per case in
`address_requery.json`). The emptiness is an intrinsic, larger-scale incompatibility of the
multi-scar reduced band, independent of the queried candidate — another way of seeing that the
scar's own address does not encode the local verdict on `c`.

## Scope and limits (as pre-registered)

- One diagnosed query in one world, with correlated replicates (the w7 radii share one physical
  scar; w15/w19/w28 share another — reported as correlated, never independent trials).
- A numerical reader under two conventions (open positive-area cutoff `1e-12`; closed Chebyshev
  `TOL_R = 1e-9`, box `50`), not a symbolic proof. Smallest non-empty `F` area seen: ~`3.7e-2`.
- A reader's recovery, not a mechanism of the growth rule.
- No claim about other scars, longer horizons, or other tilings.

## Reproduce

```bash
export EFP_SNAPSHOT=<84130b9>/exploratory/accretion_pilot/expansion_front_paper
export MPLBACKEND=Agg PYTHONUTF8=1
# base cache (jam/verify/trace), then per-step states:
#   audit_2026-11-05/observe.py            (AF_REPRO=<repo>, AF_CACHE=<base>)
#   amber_lobe_ablation_2026-11-06 run_continuation.run(w,si,r) with common.RESULTS repointed
export AMBER_BASE_CACHE=<base> AMBER_CACHE=<scratch> AMBER_FORK_CACHE=<forks.pkl>
cd address_requery_2026-11-10 && python3 address_requery.py address_requery.json
```

Files: `PROTOCOL.md`, `protocol_windows.json` (committed first), `address_requery.py`,
`address_requery.json` (raw per-window results, both conventions, controls, witnesses),
`HANDBACK.md`. No merge, no force-push; branch `claude/address-requery-2026-11-10`.

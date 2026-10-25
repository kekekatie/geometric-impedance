# Audit response: Astra's review of the A–D′ trail (25 Oct 2026)

Astra reviewed branch `claude/determined-lamport-udebxg` and filed a line-by-line critique. The review
is substantially correct and is accepted. This document records the corrections; the experiment READMEs
carry the original (uncorrected) numbers and should be read alongside this file until a recount pass
updates them.

## Corrections accepted

**A — the keystone count was mis-defined.** The pre-registration defined a keystone as *necessary and
sufficient*; the code (`response_test`) set the `single_keystone` drawer on *sufficiency alone*. Recount
(from the saved `worlds.json`):

| | count | share of 6,606 settlements |
|---|---|---|
| keystone as coded (sufficient-alone) | 5,994 | **90.7%** (as quoted) |
| keystone as **planned** (necessary **and** sufficient) | 5,434 | **82.3%** (the honest number) |
| redundant (a single tile settles it, but none is strictly necessary) | 560 | 9.3% |

A1 still holds (82.3% ≥ the pledged 60%), and all 5,434 true keystones are corner-settles — but
**82.3%, not 90.7%, is the planned result.** Further: the committee drawer bundles non-local/unresolved
cases (not always a minimal joint set); the placebo used observed additions, not the planned random
legal candidate tiles; and corner-rule failure alone does not exclude a simultaneous shared *edge*.

**B — depth is hull-relative and measured late.** Hull depth is normalised to the *finite patch's*
per-layer hull (1 at its point-cloud centroid), so "below 0.5" does not by itself prove unusually
shallow placement. Depth and arrows are read at the *final* patch, not at settlement. The pledged
coordinate-shuffling control was replaced by resampling keystone depths (not the planned null).
Near-zero *mean* tangential alignment does not establish the absence of individual handedness. B1 failed
in all 24 worlds; a revised baseline may be worth testing but does not rescue the original prediction.

**C — the 91.2% is classes, and "genuine" is bounded-test only.** C2's 83/91 = 91.2% counts malleable
*fingerprint classes* with ≥ 1 occurrence unresolved by the bounded forced-only test — **not** 91% of
individual ties. That test is limited to radius 10·S and 60 rounds, so "unresolved by the bounded test"
is justified but "globally genuine free choice" is not proved. `≤ 1` candidates conflates a surviving
singleton with zero/closed edges and should be split. The wall measure (`after_first` → compatibility
area) is a **branch-response diagnostic**, not a literal vertex-to-partition distance or proof of a
causal wall. C3 did not directly run the planned matched comparison against B's outer-depth effect.

**D — the inversion is a counting asymmetry.** D stopped counting when the target resolved but let
unresolved targets run to saturation/cap, giving larger counts to unresolved cases — so the "malleable
anchors more" inversion does not establish load-bearing ribs. The "dip" was a largest-gap/std heuristic,
not Hartigan's dip test; failing it does not prove unimodality.

**D′ — a throwaway debug was over-read as a signal (my error).** The committed pilot is 22×(−1) + 2×71.
The −1 is bookkeeping (both arms reach the same final patch, differing by the pre-placed intervention
tile). The 107/368/−53 figures cited in the first validation note came from a *separate* probe that
placed an arbitrary option on all ties, not the surviving option on settlements; they are retracted as
support. See `rib-length/VALIDATION_NOTE.md`. **"Genuine free choices are the load-bearing ribs" is a
hypothesis, not a finding.**

## Cross-cutting limits (accepted)

- End-of-run / jam-open ties are scored `stayed_open` even with < 20 slices observed — censoring needs
  explicit handling throughout.
- The fingerprint is an edge-centred, reflection-folded crop that does not mark the target edge; "same
  move" needs validation.
- Radii 1–4 do not justify "no matter how wide"; recurrence filters change the population per radius.
- Repeated ties within a world are not independent; tiny pooled p-values are not thousands of
  independent confirmations.
- The three-history skin-equivalence checks do not verify the 24-world catalogue against the hollow-skin
  engine.
- Large forced cascades and persistent connected motif renewal are different observables.

## What still carries (with the above caveats)

- A: a single sufficient neighbour settles the large majority of settlements, and the true
  necessary-and-sufficient keystones (82.3%) are corner-settles.
- B2: inward alignment 0.749 on the final-patch completed-corner subset (a real, if late-measured,
  signal).
- C3: the branch-response wall measure separates settled (≈ 0.000) from stayed-open (≈ 0.382 ≈ 1/φ²)
  ties sharply — a strong diagnostic, not a proof of a causal wall.

## Recommended next step (per Astra)

A small audit/recount first, preserving historical outputs (this document begins it). Then a paired
visual diagnostic from a locally saturated state — no commitment / option A / option B — colouring
common placements grey and branch-specific additions separately, marking the intervention tile,
contradictions and stopping reasons; comparing final tile sets; increasing radius/cap; and using fresh
worlds for confirmation. For endurance, track connected same-class renewal along the actual skin with
local-active-step clocks, waiting, burial and censoring.

Working conclusion: some bounded-test-unresolved choices are promising candidates for substantial forced
growth after commitment. Size, robustness and persistence remain to be tested.

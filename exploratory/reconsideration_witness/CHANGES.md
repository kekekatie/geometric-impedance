# Changes to the frozen protocol

The `PREREGISTRATION.md` protocol (commit `5971221`, before any code or outcome)
is otherwise unchanged. The only item the protocol allowed to be revised after
seeing outcomes is the restoration rule, and that revision is recorded here, as
required ("if the run shows it must be revised to fit the pair, the revision is
recorded in `CHANGES.md` and then tested on fresh histories with full counts
reported").

## 2026-11-12 — restoration rule revised (pre-registered one-bit rule failed)

**Frozen rule (as written):** `b = det(c0,1) XOR det(c1,1)` (round-1 d1-leg
parity of the pruned core syndrome), applied as `revised = frame XOR live XOR b`.

**Outcome:** FAILED. On the first witness pair `b` takes the same value for both
histories, so it cannot separate them; across all witness pairs the best variant
agrees with the reference on 141/258 decisions (~chance). Reported as-is in
`search.py` / `handback.json` (`restoration.preregistered_frozen_rule`). The
pre-registration hedged this to ~55% confidence; the hedge was correct.

**Revision (post-hoc, discovered by examining the result, then re-frozen):** the
minimal information that lets the streaming decoder reproduce the full-history
reference's post-flag revision is **two** pruned core detectors, `(c0,t0)` and
`(c1,t0)` (the two round-0 check detectors), on top of the retained `frame` and
boundary `m2`. This was discovered on the even-indexed groups and then confirmed,
unchanged, to determine the reference on the held-out odd-indexed groups
(`restoration_analysis_EXPLORATORY.py`, `restoration_posthoc.json`,
`held_out.same_positions_determine_reference_on_held_out_groups = true`).

**Full counts with the re-frozen rule** (258 witness decisions): agrees with the
reference 129/129 pairs (by construction); logical correctness vs simulator truth
39.1% (un-restored streaming) -> 62.0% (restored, matching the reference).
Reported separately, as required.

**Interpretation.** The pre-registered prediction P4 ("one bit restores the
verdict") is FALSE in both its forms: neither the specific frozen bit nor any
single detector/parity heals all pairs. The true minimum is two bits. This is a
genuine, reportable divergence from the paper's one-tile/one-corner minimality,
not an artefact — and the mechanism (the erasure frees the middle qubit at the two
onset rounds, leaving the round-0 syndrome on both checks as the un-absorbable
carrier of the committed logical) is given in `REPORT.md`.

No other frozen parameter (circuit, noise/loss model, flag payload/release,
decoders, window/buffer, tie handling, search bounds, success criterion, controls)
was changed.

#!/usr/bin/env python3
"""
test_failstop.py -- focused regression for the independent-legality FAILURE-STOP path
in verify_supplement.verify_case.

It injects a single forced legality failure via verify_supplement._FORCE_ILLEGAL (a
test-only hook that is None in every scientific run) at the first genuinely-legal
placement of step >= 3, then confirms that:
  * the trial stops at that step -- NO subsequent growth step executes;
  * the endpoint is marked a validation failure, not horizon completion;
  * the failure record carries enough to reproduce it (step, batch position, offending
    tile, evaluator pre-state, and the unvalidated remainder of the already-computed
    batch), with a note that the batch was computed before validation;
  * the offending tile and the unvalidated remainder are NOT accepted into history.

The injected failure data lives here and in memory only. Nothing is written to results/;
the scientific artifacts are untouched. Exits non-zero on failure.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_supplement as VS

FAILS = []
def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    state = {"fired": False, "step": None, "pos": None}
    def hook(step, pos, tile, legal):
        # fire exactly once, on the first truly-legal placement at step >= 3, so that
        # steps 1..2 are fully validated and accepted before the forced failure at step 3.
        if (not state["fired"]) and legal and step >= 3:
            state.update(fired=True, step=step, pos=pos)
            return False
        return legal

    VS._FORCE_ILLEGAL = hook
    try:
        rec, _pre = VS.verify_case(7, 0)     # w7-s0; failure forced at step 3, long before jam/44
    finally:
        VS._FORCE_ILLEGAL = None             # never leak the hook into any other run

    print(f"[failstop] forced illegal at step {state['step']}, batch position {state['pos']}")
    il = rec["independent_legality"]; f = il["first_failure"]
    check(state["fired"], "failure path was exercised (a legal placement was forced illegal)")
    check(not il["all_legal"], "independent_legality.all_legal is False")
    check(f is not None and f["step"] == state["step"] and f["batch_position"] == state["pos"],
          "failure record pins the exact step and batch position")
    check(bool(f) and "evaluator_pre_state_keys" in f and "unvalidated_remainder" in f and f.get("note"),
          "failure record carries reproducible pre-state, unvalidated remainder, and note")
    check(rec["endpoint_status"] == "validation_failure" and rec["horizon_complete"] is False,
          "endpoint marked 'validation_failure', not horizon completion")
    check(rec["growth_steps_executed"] == state["step"] and rec["steps_checked"][-1] == state["step"]
          and state["step"] < 44,
          f"NO subsequent growth step executed (stopped at step {state['step']}, before 44)")
    pre = set(f["evaluator_pre_state_keys"]) if f else set()
    check(bool(f) and f["tile"] not in pre,
          "offending tile is absent from accepted history (not added)")
    check(bool(f) and all(k not in pre for k in f["unvalidated_remainder"]),
          "unvalidated remainder is absent from accepted history (not accepted)")

    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)}"); sys.exit(1)
    print("FAILURE-STOP REGRESSION PASSED.")


if __name__ == "__main__":
    main()

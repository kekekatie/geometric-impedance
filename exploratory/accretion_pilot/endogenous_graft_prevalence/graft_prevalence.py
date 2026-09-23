#!/usr/bin/env python3
"""
graft_prevalence.py -- how PREVALENT is GRAFT-enabled renewal across the whole depth-2 seed
set, not just the one hand-built seed of ../endogenous_graft_experiment/?

Fable's request (transmission-paper data): run the GRAFT test (extended = BUD+CONTACT+GRAFT
vs control = BUD+CONTACT; scheduler uniform over individual events; horizons 0..4; outcomes
O0/O1/O2 about a designated quiet trace) on EVERY reachable depth-2 seed, for EVERY quiet
trace in it, and report how often renewal occurs.

Outcomes (about the designated quiet trace q; cumulative "by step t"):
  O0  q gains a new active NEIGHBOUR (a GRAFT adds an edge q-w).
  O1  q gains a CONTACT pair it has NEVER previously had (newly-enabled relevance / renewal).
  O2  a subsequently selected CONTACT THROUGH q consumes such a newly-enabled pair
      (renew-then-consult).
Seed set: the 11 depth-2 classes (the same set the matched-pair work uses), each with its 2
quiet vertices -> 22 (seed, trace) cases. We split by whether the trace's CONTACT menu starts
empty (as the original hand seed did) or non-empty (delayed-consultation opportunities exist).

Register: speculative exploration; exact rational enumeration; a mechanism study, not a sample
of growing worlds. Isolated; earlier work preserved. asserts + nonzero exit. Reuses the
verified machinery of ../endogenous_graft_experiment/ and the class set of
../endogenous_present_width/.
"""
from __future__ import annotations
import os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "endogenous_graft_experiment"))
sys.path.insert(0, os.path.join(HERE, "..", "endogenous_present_width"))
import graft_experiment as GE
import present_width as PW

REPORT = os.path.join(HERE, "results", "graft_prevalence_report.txt")
TABLE = os.path.join(HERE, "results", "prevalence_table.txt")
LINES, FAILS = [], []
HZN = 4


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    log("=" * 96)
    log("GRAFT PREVALENCE -- renewal across every depth-2 seed and quiet trace (exact)")
    log("=" * 96)
    fulls = PW.depth2_classes()

    cases = []          # (class, q, menu0, ext(O0,O1,O2)@4, ctl(O0,O1,O2)@4)
    for c, G in enumerate(fulls):
        for q in [n for n in G if G.nodes[n]["label"] == "Q"]:
            menu0 = len(GE.C_q(G, q))
            ea, *_ = GE.enumerate_process(G, GE.events_extended, q, horizon=HZN)
            ca, *_ = GE.enumerate_process(G, GE.events_control, q, horizon=HZN)
            ext = (ea[HZN]["o0"], ea[HZN]["o1"], ea[HZN]["o2"])
            ctl = (ca[HZN]["o0"], ca[HZN]["o1"], ca[HZN]["o2"])
            cases.append((c, q, menu0, ext, ctl))

    N = len(cases)
    empty = [x for x in cases if x[2] == 0]
    nonempty = [x for x in cases if x[2] > 0]

    # ---- table ----
    rows = ["class  q  menu0 | EXTENDED O0        O1(renewal)     O2(consult)   | CONTROL O0/O1/O2"]
    for (c, q, m0, ext, ctl) in cases:
        rows.append(f"  {c:>2}  {q:>2}   {m0}   |  "
                    f"{float(ext[0]):.3f}  {float(ext[1]):.3f}          {float(ext[2]):.3f}       "
                    f"|  {float(ctl[0]):.0f}/{float(ctl[1]):.0f}/{float(ctl[2]):.0f}")
    with open(TABLE, "w") as f:
        f.write("\n".join(rows) + "\n")
    for r in rows:
        log("  " + r)

    # ---- control: renewal is impossible without GRAFT, across the WHOLE seed set ----
    log("=" * 96)
    ctl_zero = all(ctl == (0, 0, 0) for (_, _, _, _, ctl) in cases)
    require(ctl_zero,
            f"CONTROL (BUD+CONTACT): O0=O1=O2=0 for ALL {N} traces -- the menu-monotonicity "
            f"theorem holds across the entire depth-2 seed set, not just one seed (renewal is "
            f"impossible without GRAFT everywhere)")

    # ---- prevalence of renewal (O1>0) and consultation (O2>0) with GRAFT ----
    renew = [x for x in cases if x[3][1] > 0]
    consult = [x for x in cases if x[3][2] > 0]
    log(f"[prevalence] renewal (extended O1>0): {len(renew)}/{N} traces "
        f"({100*len(renew)/N:.0f}%)")
    log(f"[prevalence] consultation (extended O2>0): {len(consult)}/{N} traces "
        f"({100*len(consult)/N:.0f}%)")
    log(f"  by starting menu: empty-menu traces {len(empty)} "
        f"(renewal {sum(1 for x in empty if x[3][1]>0)}, consult {sum(1 for x in empty if x[3][2]>0)}); "
        f"non-empty-menu traces {len(nonempty)} "
        f"(renewal {sum(1 for x in nonempty if x[3][1]>0)}, consult {sum(1 for x in nonempty if x[3][2]>0)})")
    require(len(renew) > 0 and len(consult) > 0,
            f"with GRAFT, renewal occurs in {len(renew)} and consultation in {len(consult)} of "
            f"{N} traces -- renewal is not peculiar to the one hand-built seed")
    # renewal implies a new neighbour was added first (O1<=O0 pathwise on these seeds)
    require(all(x[3][1] <= x[3][0] + Fr(1, 10**9) for x in cases),
            "O1 <= O0 for every trace (a never-before pair arrives via a new neighbour); the two "
            "are reported separately")
    # consultation cannot exceed renewal (must renew before you can consult a renewed pair)
    require(all(x[3][2] <= x[3][1] + Fr(1, 10**9) for x in cases),
            "O2 <= O1 for every trace (you must gain a never-before pair before consulting one)")

    # ---- exact aggregate figures ----
    meanO1 = sum((x[3][1] for x in cases), Fr(0)) / N
    meanO2 = sum((x[3][2] for x in cases), Fr(0)) / N
    maxO1 = max(cases, key=lambda x: x[3][1])
    log("=" * 96)
    log(f"[aggregate] mean renewal prob O1 (by step 4) over {N} traces = {meanO1} "
        f"= {float(meanO1):.4f}")
    log(f"[aggregate] mean consultation prob O2 (by step 4) = {meanO2} = {float(meanO2):.4f}")
    log(f"[aggregate] strongest renewal: class {maxO1[0]} q={maxO1[1]} (menu0={maxO1[2]}) "
        f"O1={float(maxO1[3][1]):.4f}")

    log("=" * 96)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    log(f"Reading: across all {N} (seed, quiet-trace) cases of the depth-2 set, the control "
        f"(no GRAFT) yields renewal probability EXACTLY 0 everywhere -- the impossibility is "
        f"universal, not a one-seed artefact. Adding GRAFT makes renewal reachable in "
        f"{len(renew)}/{N} traces and consultation in {len(consult)}/{N}, with mean renewal "
        f"probability {float(meanO1):.3f} by 4 events. A designed coupling, one scheduler, one "
        f"seed depth -- a mechanism/prevalence study, not a claim about generic worlds.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    globals()["_CASES"] = cases
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
depth3_criterion.py -- does the depth-2 "fate decided at step one" survive to depth-3?

Fable's push (before writing it as a theorem): the two directions of the depth-2 criterion
"L=0 <=> menu-equivalent (D_slice(1)=0)" have different status, and "menu-equivalent => inert"
looked like it might be provable for all seeds via a projected bisimulation. The subtlety he
flagged is whether "same projected menu" survives relabelling through time. This file settles
it by search: it either survives, or it breaks with an exact counterexample.

RESULT: it BREAKS at depth-3. Both depth-2 headline statements are depth-2-specific:
  * "washout category is empty" (expression => durability, the old Proposition 4) is FALSE
    at depth-3: there are pairs expressed in the active layer (D_slice>0) with L=0.
  * "fate decided at step one" (L=0 <=> D_slice(1)=0) is FALSE at depth-3 in BOTH directions:
      - a step-one-equivalent pair that later diverges (D_slice(1)=0 but D_slice(2)>0), and
      - an L=0 pair already expressed at step one (D_slice(1)>0 but L=0).

What SURVIVES, and is the real law: L = TV(absorption distributions) always (Proposition 3),
so L=0 IFF the two lineages' H=2 slice distributions absorb identically. Fate is governed by
the ABSORPTION GEOMETRY of the coast, not by step one:
  * durable (L>0): expressed AND the two lineages split the (>=2) reachable absorbing classes
    differently;
  * washout (L=0, expressed): the coast funnels all mass into a SINGLE reachable absorbing
    class, so absorption is constant and any expressed difference is annihilated;
  * inert (L=0, never expressed): the slice distributions are identical from the start.
On depth-3, EVERY washout pair has exactly one reachable absorbing class and EVERY durable
pair has two -- the single-sink mechanism, exact.

Register: speculative exploration; exact rational enumeration on the depth-3 class set; a
mechanism study, not a sample. Isolated; earlier work preserved. asserts + nonzero exit.
Reuses ../endogenous_present_width/ and pair_robustness.coast_limit.
"""
from __future__ import annotations
import os, sys
from collections import Counter
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "endogenous_present_width"))
import present_width as PW
import pair_robustness as PR

REPORT = os.path.join(HERE, "results", "depth3_criterion_report.txt")
LINES, FAILS = [], []


def log(s=""):
    LINES.append(s); print(s)


def require(cond, msg):
    LINES.append(("  [PASS] " if cond else "  [FAIL] ") + msg)
    print(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


def depth3_classes():
    seed = PW.path(4); states = []
    for e1 in PW.events_bud(seed):
        G1 = PW.bud(seed, e1[1], e1[2])
        for e2 in PW.events_bud(G1):
            G2 = PW.bud(G1, e2[1], e2[2])
            for e3 in PW.events_bud(G2):
                states.append(PW.bud(G2, e3[1], e3[2]))
    return PW.class_reps(states)


def Dslice(Ga, Gb, h):
    si = PW.run_process(Ga, PW.events_ext, h, PW.events_ext, 0, False)[1]
    sj = PW.run_process(Gb, PW.events_ext, h, PW.events_ext, 0, False)[1]
    return PW.tv(si[h], sj[h])


def main():
    log("=" * 94)
    log("DEPTH-3 CRITERION -- does 'fate decided at step one' survive beyond depth-2? (No.)")
    log("=" * 94)
    d3 = depth3_classes()
    pairs = [(a, b) for a in range(len(d3)) for b in range(a + 1, len(d3))
             if PW.iso(PW.erase(d3[a]), PW.erase(d3[b])) and not PW.iso(d3[a], d3[b])]
    log(f"depth-3 classes: {len(d3)} (each 4 active + 3 quiet, DeltaA=0); matched pairs: "
        f"{len(pairs)}")
    require(len(pairs) > 50, "a large depth-3 matched-pair set to stress-test the depth-2 claims")

    # ---- classify every pair: D_slice(1,2,3), L, #reachable absorbing classes ----
    rec = {}
    for (a, b) in pairs:
        d1 = Dslice(d3[a], d3[b], 1); d2 = Dslice(d3[a], d3[b], 2); d3s = Dslice(d3[a], d3[b], 3)
        L, shapes, _ = PR.coast_limit(d3[a], d3[b])
        expressed = (d1 > 0 or d2 > 0 or d3s > 0)
        fate = "durable" if L > 0 else ("washout" if expressed else "inert")
        rec[(a, b)] = dict(d1=d1, d2=d2, d3=d3s, L=L, nsink=len(shapes), fate=fate)
    fates = Counter(r["fate"] for r in rec.values())
    log(f"fates at depth-3: durable {fates['durable']}, inert {fates['inert']}, "
        f"washout {fates['washout']}")

    # ---- (1) the WASHOUT category is NON-EMPTY at depth-3 (old Prop 4 breaks) ----
    log("=" * 94)
    washouts = [p for p in pairs if rec[p]["fate"] == "washout"]
    require(len(washouts) > 0,
            f"WASHOUT is NON-EMPTY at depth-3 ({len(washouts)} pairs): there ARE pairs expressed "
            f"in the active layer (D_slice>0) that decay to L=0. 'Expression => durability' "
            f"(depth-2 Proposition 4) is FALSE beyond depth-2 -- exactly the case Fable asked to "
            f"find")
    wex = washouts[0]
    log(f"  exact washout exemplar {wex}: D_slice(1)={rec[wex]['d1']}, D_slice(2)={rec[wex]['d2']}"
        f", D_slice(3)={rec[wex]['d3']}, L={rec[wex]['L']} (expressed, yet washes out)")

    # ---- (2) 'fate decided at step one' breaks in BOTH directions ----
    log("=" * 94)
    step1_late = [p for p in pairs if rec[p]["d1"] == 0 and (rec[p]["d2"] > 0 or rec[p]["d3"] > 0)]
    l0_expr1 = [p for p in pairs if rec[p]["L"] == 0 and rec[p]["d1"] > 0]
    require(len(step1_late) > 0,
            f"STEP-ONE BREAKER ({len(step1_late)} pairs): D_slice(1)=0 yet D_slice(2)>0 -- "
            f"menu-equivalent at step one, then DIVERGES. 'Same projected menu' does NOT survive "
            f"through time (the relabelling subtlety Fable named). e.g. {step1_late[0]}: "
            f"D1={rec[step1_late[0]]['d1']}, D2={rec[step1_late[0]]['d2']}")
    require(len(l0_expr1) > 0,
            f"FORWARD BREAKER ({len(l0_expr1)} pairs): L=0 yet D_slice(1)>0 -- so "
            f"'L=0 => menu-equivalent' also fails. e.g. {l0_expr1[0]}: "
            f"D1={rec[l0_expr1[0]]['d1']}, L=0. The depth-2 equivalence L=0 <=> D_slice(1)=0 "
            f"breaks in BOTH directions at depth-3")

    # ---- (3) the law that SURVIVES: fate = absorption geometry (single-sink mechanism) ----
    log("=" * 94)
    log("[surviving law] L = TV(absorption distributions); fate is set by the coast's "
        "absorption geometry")
    require(all(rec[p]["nsink"] == 1 for p in washouts),
            "MECHANISM: every washout pair has exactly ONE reachable absorbing class -- the "
            "coast funnels all mass into a single sink, so absorption is constant and any "
            "expressed difference is annihilated (L=0). That is WHY expression can fail to be "
            "durable")
    require(all(rec[p]["nsink"] >= 2 for p in pairs if rec[p]["fate"] == "durable"),
            "every durable pair has >= 2 reachable absorbing classes -- durability requires the "
            "lineages to split the sinks differently (a nonzero absorption difference)")
    # single sink => L=0 (either inert or washout); >=2 sinks can be any fate
    require(all(rec[p]["L"] == 0 for p in pairs if rec[p]["nsink"] == 1),
            "single reachable sink => L=0 always (inert if unexpressed, washout if expressed) -- "
            "an exact, checkable predictor of L=0 that REPLACES the step-one criterion")

    # ---- (4) contrast: at depth-2 none of these breakers exist (the clean special case) ----
    log("=" * 94)
    d2 = PW.depth2_classes()
    d2pairs = [(a, b) for a in range(len(d2)) for b in range(a + 1, len(d2))
               if PW.iso(PW.erase(d2[a]), PW.erase(d2[b])) and not PW.iso(d2[a], d2[b])]
    d2wash = 0
    for (a, b) in d2pairs:
        d1 = Dslice(d2[a], d2[b], 1); d2s = Dslice(d2[a], d2[b], 2)
        L, _, _ = PR.coast_limit(d2[a], d2[b])
        if L == 0 and (d1 > 0 or d2s > 0):
            d2wash += 1
    require(d2wash == 0,
            "at DEPTH-2 the washout category is empty and the step-one criterion holds -- so the "
            "depth-2 findings were a genuine (clean) SPECIAL CASE, not a general law; depth-3 is "
            "where the general absorption-geometry picture becomes visible")

    log("=" * 94)
    if FAILS:
        log(f"FAILED: {len(FAILS)} check(s): " + "; ".join(FAILS))
    else:
        log("ALL EXACT CHECKS PASSED.")
    log("Verdict for the write-up: do NOT state 'fate decided at step one' or 'expression => "
        "durability' as theorems -- both are depth-2-specific and break at depth-3 (exact "
        "counterexamples above). State instead the surviving law: L = TV(absorption "
        "distributions); a single reachable absorbing class forces L=0 (inert or washout); "
        ">=2 sinks with a differential split give durable L>0. The three fates all occur once "
        "the seed set is deep enough. Mechanism study on the depth-3 class set; general proof "
        "of when the coast has one vs several sinks is the open direction.")
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w").write("\n".join(LINES) + "\n")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()

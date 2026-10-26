#!/usr/bin/env python3
"""
window_retrodiction.py -- Phase-2 closure (Argon's 5D window retrodiction).

Pre-registered in CLOSURE_PREREGISTRATION.md. After the choice-tiles are pruned from the retained active
skin, does the surviving ring still DETERMINE which option was taken?
  F1  decoration-trace survival (shared-ground blue/orange still non-zero post-prune)
  F2  5D window retrodiction: F(skin_t) computed in the fork's gauge excludes C^other to zero area while
      keeping C^true -- the living ring uniquely retrodicts the deleted choice
  F3  (exploratory) does fork stiffness predict persistence?

Validated method (see gate in CLOSURE_PREREGISTRATION.md):
  * GAUGE FIX: lift the FULL arm patch (shares S*'s anchor) and read skin constraints from THAT lift,
    restricted to skin vertices and S*'s four internal layers -- never lift the pruned skin alone.
  * JAM CENSORING: an arm that grows into a contradiction has empty F(full); it is censored, not scored.

Retrodictability (analyst + global lift), NOT a position-blind local observer -- stated honestly.

Run:  python3 window_retrodiction.py --need 22 --steps 44
"""
from __future__ import annotations
from pathlib import Path
import sys, json, argparse, collections
import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
EFP = HERE.parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(EFP)); sys.path.insert(0, str(EFP / "corner-response-catalogue"))
import figures as F
import paired_front as P
import perp_map as M
import corner_response as CR
Sl, CD, D, L, S = F.Sl, F.CD, F.D, F.L, F.S
WIN = Sl.WIN
dk = P.dk
RES = HERE / "results"; RES.mkdir(exist_ok=True)
STIFF = json.loads((EFP / "corner-response-catalogue" / "results" / "summary.json").read_text())["stiffness"]


def F_in_gauge(tiles, rank, restrict_vkeys=None):
    """Compatibility-region area from a tile set's vertices, in the lift's own (S*-anchored for a full
    arm patch) gauge, restricted to S*'s four layers. If restrict_vkeys is given, only those vertices
    (the skin) contribute -- but the lift is still the full patch, so the gauge is consistent."""
    K, _, _ = M.lift(tiles)
    cm = {}
    items = K.items() if restrict_vkeys is None else ((vk, K[vk]) for vk in restrict_vkeys if vk in K)
    for vk, k in items:
        layer = int(k.sum())
        if layer not in rank:
            continue
        rk = rank[layer]; z = M.perp(k); n, h = WIN[rk]
        for i, (nx, ny) in enumerate(n):
            c = nx * z.real + ny * z.imag - h
            if c > cm.get((rk, i), -1e18):
                cm[(rk, i)] = c
    return cm


def _score_step(full, rank, cTrue, cOther):
    skin, _ = P.skin_of(full)
    vkeys = {L.key(z) for t in skin for z in t[1:]}
    cm = F_in_gauge(full, rank, restrict_vkeys=vkeys)
    f0 = Sl.area(Sl.region(cm))
    aTrue = Sl.area(Sl.region(cm, cTrue)); aOther = Sl.area(Sl.region(cm, cOther))
    if f0 <= 1e-12:
        return "jam", f0, aTrue, aOther               # empty skin region = contradiction
    v = "correct" if (aTrue > 1e-9 and aOther <= 1e-9) else \
        ("wrong" if (aOther > 1e-9 and aTrue <= 1e-9) else "ambiguous")
    return v, f0, aTrue, aOther


def retrodict_arm(Sstar, cX, other, stream, steps, rank, cTrue, cOther):
    """Grow one arm; score retrodiction at the LAST valid (post-departure, pre-jam) step -- found by
    walking back from the end so a clean arm costs one lift. Robustness sampled at 3 steps, not all."""
    arm = P.grow_arm(Sstar, cX, stream, steps)
    snaps = arm["snaps"]
    dep = next((s for s in range(1, len(snaps))
                if dk(cX) not in {dk(t) for t in P.skin_of(snaps[s])[0]}), None)
    verdict = aTrue = aOther = f0 = last_step = all_correct = None
    censored = True
    if dep is not None:
        # last valid step: walk back from the end to the first non-jammed (F>0) step at/after dep
        for s in range(len(snaps) - 1, dep - 1, -1):
            v, f0, aTrue, aOther = _score_step(snaps[s], rank, cTrue, cOther)
            if v != "jam":
                verdict = v; last_step = s; censored = False; break
        if not censored:
            # robustness: sample dep, midpoint, last_step
            sample = sorted(set([dep, (dep + last_step) // 2, last_step]))
            all_correct = True
            for s in sample:
                v, *_ = _score_step(snaps[s], rank, cTrue, cOther)
                if v != "correct":
                    all_correct = False; break
    jammed = arm["stop"] == "jam"
    return dict(stop=arm["stop"], guesses=arm["guesses"], dep=dep, jam=jammed, nsnaps=len(snaps),
                verdict=verdict, aTrue=aTrue, aOther=aOther, f0=f0, last_step=last_step,
                all_correct=all_correct, censored=censored), arm


def fork_key(Sstar, mid, r=6):
    local = [t for t in Sstar if abs(P.cen(t) - mid) <= r * S]
    return CD.whole_key(local, mid)


def predictors(Sstar, edge, mid):
    cs = D.candidates(L.Patch(Sstar), *edge[:3])
    rank = Sl.rank_of(Sstar)
    Fraw = Sl.area(Sl.region(Sl.constraints(Sstar, rank)))
    wall = None
    if len(cs) == 2 and Fraw > 0:
        pcs = [Sl.area(Sl.region(CD.after_first(Sstar, c, rank))) for c in cs]
        wall = float(min(pcs) / Fraw)
    fp = CR.fingerprint(Sstar, mid, CR.RPRIMARY); stiff = STIFF.get(fp)
    return wall, (None if stiff is None else float(stiff))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--need", type=int, default=22)
    ap.add_argument("--steps", type=int, default=44)
    ap.add_argument("--nstreams", type=int, default=2)
    ap.add_argument("--maxworlds", type=int, default=80)
    args = ap.parse_args()
    seen = set(); rows = []
    for k in range(args.maxworlds):
        if len(rows) >= args.need:
            break
        try:
            cs0 = P.common_state(k, P.centres(args.maxworlds)[k])
        except Exception as e:
            print(f"world {k}: common_state error ({type(e).__name__})", flush=True); continue
        if cs0 is None:
            continue
        Sstar, edge, mid, cs, meta = cs0
        key = fork_key(Sstar, mid)
        if key in seen:
            print(f"world {k}: duplicate fork config, skipped", flush=True); continue
        seen.add(key)
        A, B = cs[0], cs[1]
        rank = Sl.rank_of(Sstar)
        cA = CD.after_first(Sstar, A, rank); cB = CD.after_first(Sstar, B, rank)
        cAarea = Sl.area(Sl.region(cA)); cBarea = Sl.area(Sl.region(cB))
        disjoint = Sl.area(Sl.region(cA, cB)) <= 1e-12
        streams = [P.SEED0 * 1000 + k * 7919 + 101 * i for i in range(args.nstreams)]
        armrecs = []   # one per (option, stream)
        f1s_fork = []
        for si, stream in enumerate(streams):
            rA, armA = retrodict_arm(Sstar, A, B, stream, args.steps, rank, cA, cB)
            rB, armB = retrodict_arm(Sstar, B, A, stream, args.steps, rank, cB, cA)
            rA["opt"] = "A"; rA["stream"] = si; rB["opt"] = "B"; rB["stream"] = si
            armrecs += [rA, rB]
            # F1: coupled trace density at a post-departure step (both choice-tiles gone). Use each arm's
            # last valid (non-jammed) step so a jam doesn't poison it.
            dep = max([d for d in (rA["dep"], rB["dep"]) if d is not None], default=None)
            lv = [x for x in (rA["last_step"], rB["last_step"]) if x is not None]
            if dep is not None and lv:
                s = min(lv)   # both arms valid and post-departure here
                if s >= dep:
                    skA, frA = P.skin_of(armA["snaps"][s]); skB, frB = P.skin_of(armB["snaps"][s])
                    b = P.buckets(skA, frA, skB, frB)
                    f1s_fork.append(round(b["shared_frac"], 3))
        wall, stiff = predictors(Sstar, edge, mid)
        f1 = dict(frac=float(np.median(f1s_fork)), n=len(f1s_fork)) if f1s_fork else None
        row = dict(world=k, patch=meta["patch"], cAarea=round(cAarea, 4), cBarea=round(cBarea, 4),
                   disjoint=disjoint, arms=armrecs, F1=f1, wall=wall, stiff=stiff)
        rows.append(row)
        sc = [a for a in armrecs if not a["censored"]]
        nok = sum(1 for a in sc if a["verdict"] == "correct")
        print(f"world {k}: patch {meta['patch']} | arm-streams scored {len(sc)}/{len(armrecs)}, correct {nok}/{len(sc)} | "
              f"jam {sum(1 for a in armrecs if a['jam'])}/{len(armrecs)} | "
              f"F1={f1['frac'] if f1 else None} stiff={None if stiff is None else round(stiff,2)}", flush=True)
        (RES / "closure_measurements.json").write_text(json.dumps(rows, indent=2, default=float))

    # ---- aggregate ----
    arms = [a for r in rows for a in r["arms"]]
    scored = [a for a in arms if not a["censored"]]
    correct = [a for a in scored if a["verdict"] == "correct"]
    robust = [a for a in scored if a["all_correct"]]
    censored = [a for a in arms if a["censored"]]
    disj = sum(r["disjoint"] for r in rows)
    out = []
    out.append("Window retrodiction closure (Phase 2): does the surviving front determine the deleted choice?")
    out.append(f"distinct forks: {len(rows)}   (arm-streams: {len(arms)}; scored non-jammed: {len(scored)}; censored: {len(censored)})")
    out.append(f"candidate regions C^A, C^B disjoint: {disj}/{len(rows)} forks")
    out.append("")
    out.append(f"F2  retrodiction (surviving ring excludes the wrong option to zero area, post-prune):")
    out.append(f"    correct at last valid step: {len(correct)}/{len(scored)} scored arm-streams")
    out.append(f"    correct at EVERY post-departure pre-jam step (robust): {len(robust)}/{len(scored)}")
    wrong = [a for a in scored if a["verdict"] == "wrong"]; amb = [a for a in scored if a["verdict"] == "ambiguous"]
    out.append(f"    wrong: {len(wrong)}   ambiguous: {len(amb)}")
    out.append(f"    censored (jammed, or choice-tile never left the skin, before a post-departure step): {len(censored)}/{len(arms)}")
    jamA = sum(1 for a in arms if a["opt"] == "A" and a["jam"])
    jamB = sum(1 for a in arms if a["opt"] == "B" and a["jam"])
    nA = sum(1 for a in arms if a["opt"] == "A"); nB = sum(1 for a in arms if a["opt"] == "B")
    out.append(f"    jam rate by option: A {jamA}/{nA}, B {jamB}/{nB} (is one option more dead-end-prone?)")
    out.append("")
    f1s = [r["F1"]["frac"] for r in rows if r["F1"] is not None]
    f1pos = sum(1 for x in f1s if x > 0)
    out.append(f"F1  decoration-trace survival post-prune: non-zero in {f1pos}/{len(f1s)} forks "
               f"(median density {np.median(f1s):.3f})" if f1s else "F1: no post-departure data")
    out.append("")
    # F3 exploratory
    pers = []  # per fork: stiffness vs persistence (fraction of this fork's scored arm-streams that are robust)
    for r in rows:
        if r["stiff"] is None:
            continue
        sc = [a for a in r["arms"] if not a["censored"]]
        pscore = (sum(1 for a in sc if a["all_correct"]) / len(sc)) if sc else 0.0
        tracefrac = r["F1"]["frac"] if r["F1"] else 0.0
        pers.append((r["stiff"], pscore, tracefrac, r["world"]))
    out.append("F3 (EXPLORATORY, two-sided, not scored): fork stiffness vs post-prune persistence")
    if len(pers) >= 4:
        st = [p[0] for p in pers]
        out.append(f"    Spearman(stiffness, robust-arm count)   = {spearmanr(st, [p[1] for p in pers])[0]:+.3f}  (n={len(pers)})")
        out.append(f"    Spearman(stiffness, trace density)      = {spearmanr(st, [p[2] for p in pers])[0]:+.3f}")
        out.append("    (underpowered; a flag for a future test, not a closure claim)")
    else:
        out.append(f"    too few stiffness-covered forks ({len(pers)})")

    txt = "\n".join(out)
    print("\n" + txt)
    (RES / "closure_report.txt").write_text(txt + "\n")
    print("\nwrote results/closure_report.txt, results/closure_measurements.json")


if __name__ == "__main__":
    main()

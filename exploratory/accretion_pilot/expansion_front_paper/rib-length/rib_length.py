#!/usr/bin/env python3
"""
rib_length.py -- the corrected endurance bridge (Experiment D').
(PREREGISTRATION.md, frozen before this file.)

Rib length = marginal forward forcing of a settlement:
  count_forced(before + surviving option) - count_forced(before),
both grown forced-only to local saturation. The ambient domino-wave cancels, so
what remains is what the settlement itself unlocks. Fixes Experiment D, whose
burst-at-birth measured ambient traffic (open ties had the biggest reach).

  D'1  rigid settlements force more forward structure (larger rib length).
  D'2  rib length is bimodal (ribs vs hinges).
  D'3  rib length does NOT track frontier-advance rate (the D confound cancels).

Run:  python3 rib_length.py            |    python3 rib_length.py --worlds 2 --nadd 500 --serial
"""
from __future__ import annotations
from pathlib import Path
import sys, os, json, random, argparse
from multiprocessing import Pool
import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "corner-response-catalogue"))
import figures as F
import corner_response as CR

L, D, S, SN = F.L, F.D, F.S, F.SN
RES = HERE / "results"; RES.mkdir(exist_ok=True)
EPS = 1e-9
LOCAL_R = 10
BURST_CAP = 60
_STIFF = json.loads((HERE.parent / "corner-response-catalogue" / "results" / "summary.json").read_text())["stiffness"]
RECUR = set(_STIFF)


def count_forced(patch, mid, cap=BURST_CAP, R=LOCAL_R):
    """Localised forced-only growth to saturation; total tiles placed. No edge early-stop."""
    P = L.Patch(list(patch)); rr = R * S + EPS; total = 0
    for _ in range(cap):
        forced = {}
        for e in P.frontier():
            if abs((e[0] + e[1]) / 2 - mid) > rr:
                continue
            cs = D.candidates(P, *e[:3])
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        placed = 0
        for t in forced.values():
            if P.legal(t):
                P.add(t); placed += 1
        total += placed
        if placed == 0:
            break
    return total


def grow_world(k):
    rng = random.Random(CR.SEED0 + k)
    P = L.Patch(L.seed_patch(CR.centres()[k], 3 * S)); n0 = len(P.tris); r = 0
    active, done, ties = {}, set(), []
    status = "ok"

    def resolve(sk, rec, rib=None):
        tie = active.pop(sk); done.add(sk)
        local_added = len(CR.near(P.tris[len(tie["before"]):], tie["mid"], CR.RPRIMARY))
        slices = max(r - tie["first_slice"], 1)
        rec.update(world=k, fp=tie["fp"], stiffness=_STIFF.get(tie["fp"]),
                   rib=rib, advance_rate=local_added / slices)
        ties.append(rec)

    while len(P.tris) - n0 < CR.N_ADD:
        r += 1
        fr = P.frontier(); cand = {}; fmap = {}; jam = False
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = True; break
            sk = CR.ek(e); cand[sk] = len(cs); fmap[sk] = e
        if jam:
            status = "JAM"; break
        for sk in list(active):
            tie = active[sk]
            if sk not in cand:
                resolve(sk, dict(drawer="gone"))
            elif cand[sk] == 1:
                added_local = CR.near(P.tris[len(tie["before"]):], tie["mid"], CR.RPRIMARY)
                rec = CR.response_test(tie["before"], added_local, tie["edge"])
                rib = None
                if rec.get("drawer") in ("single_keystone", "committee") and tie["fp"] in RECUR:
                    surv = D.candidates(P, *tie["edge"][:3])        # 1 remaining at resolution
                    if len(surv) == 1:
                        dk = D.dkey(surv[0])
                        bc = D.candidates(L.Patch(tie["before"]), *tie["edge"][:3])
                        sb = next((c for c in bc if D.dkey(c) == dk), None)
                        if sb is not None:
                            rib = count_forced(tie["before"] + [sb], tie["mid"]) - count_forced(tie["before"], tie["mid"])
                resolve(sk, rec, rib)
            elif r - tie["first_slice"] >= CR.K:
                resolve(sk, dict(drawer="stayed_open"))
        for sk, n in cand.items():
            if n == 2 and sk not in active and sk not in done:
                e = fmap[sk]; mid = (e[0] + e[1]) / 2; before = list(P.tris)
                fp = CR.fingerprint(before, mid, CR.RPRIMARY)
                active[sk] = dict(before=before, edge=e, first_slice=r, mid=mid, fp=fp)
        forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= CR.N_ADD:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            continue
        cs = SN.ordered(D.candidates(P, *fr[0][:3])); gk = CR.ek(fr[0])
        if gk in active:
            resolve(gk, dict(drawer="directly_chosen"))
        P.add(rng.choice(cs))
    for sk in list(active):
        resolve(sk, dict(drawer="stayed_open", at_end=True))
    return dict(world=k, status=status, ties=[t for t in ties if t["fp"] in RECUR and t["rib"] is not None])


def dip(x):
    x = np.sort(np.asarray(x, float))
    if len(x) < 20:
        return None
    lo, hi = np.percentile(x, 5), np.percentile(x, 95); core = x[(x >= lo) & (x <= hi)]
    if len(core) < 10:
        return None
    return float(np.diff(core).max() / (core.std() + EPS))


def score(worlds):
    ties = [t for w in worlds for t in w["ties"] if t["stiffness"] is not None]
    rib = np.array([t["rib"] for t in ties]); stiff = np.array([t["stiffness"] for t in ties])
    rate = np.array([t["advance_rate"] for t in ties])
    lines = [f"worlds {len(worlds)}; settlements with rib length {len(ties)}",
             f"rib length: median {np.median(rib):.1f}, mean {rib.mean():.1f}, p10 {np.percentile(rib,10):.0f} "
             f"p90 {np.percentile(rib,90):.0f}, max {rib.max()}, negatives {int((rib<0).sum())}"]

    rho = spearmanr(stiff, rib)[0]
    rigid = rib[stiff >= CR.RIGID_CUT]; mall = rib[stiff < CR.RIGID_CUT]
    d1 = rho > 0.2 and np.median(rigid) > np.median(mall)
    lines.append(f"D'1: {'HELD  ' if d1 else 'did not hold'}  Spearman(stiffness, rib) {rho:.3f} (pledged > 0.2); "
                 f"rigid median {np.median(rigid):.1f} (n {len(rigid)}) vs malleable {np.median(mall):.1f} (n {len(mall)})")

    dd = dip(rib); d2 = dd is not None and dd > 0.5
    lines.append(f"D'2: {'HELD  ' if d2 else 'did not hold'}  bimodality gap/std {dd if dd is None else round(dd,3)} (pledged > 0.5)")

    rho3 = spearmanr(rib, rate)[0]; d3 = abs(rho3) < 0.2
    lines.append(f"D'3: {'HELD  ' if d3 else 'did not hold'}  Spearman(rib, advance-rate) {rho3:.3f} (pledged |rho| < 0.2; "
                 f"D's broken reach was -0.279)")

    summary = dict(settlements=len(ties), rib_median=float(np.median(rib)),
                   D1=dict(held=bool(d1), spearman=float(rho), rigid_median=float(np.median(rigid)), mall_median=float(np.median(mall))),
                   D2=dict(held=bool(d2), dip=dd),
                   D3=dict(held=bool(d3), spearman=float(rho3)),
                   rib_values=[int(t["rib"]) for t in ties], stiffness_values=[float(t["stiffness"]) for t in ties])
    return "\n".join(lines), summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=CR.N_WORLDS)
    ap.add_argument("--nadd", type=int, default=None)
    ap.add_argument("--serial", action="store_true")
    args = ap.parse_args()
    if args.nadd:
        CR.N_ADD = args.nadd
    ids = list(range(args.worlds))
    if args.serial or args.worlds == 1:
        worlds = [grow_world(k) for k in ids]
    else:
        with Pool(min(4, args.worlds), maxtasksperchild=1) as p:
            worlds = p.map(grow_world, ids)
    report, summary = score(worlds)
    print(report)
    jd = lambda o: o.item() if hasattr(o, "item") else str(o)
    (RES / "worlds.json").write_text(json.dumps(worlds, default=jd))
    (RES / "summary.json").write_text(json.dumps(summary, indent=2, default=jd))
    (RES / "rib_length_report.txt").write_text(report + "\n")


if __name__ == "__main__":
    main()

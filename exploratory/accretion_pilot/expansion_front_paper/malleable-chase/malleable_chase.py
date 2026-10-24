#!/usr/bin/env python3
"""
malleable_chase.py -- what tips the wobble (Experiment C).
(PREREGISTRATION.md, frozen before this file.)

Stage 1: forced-only burst (localised) from each recurring-fingerprint tie -- does
the board force it without any guess (secretly rigid, timing) or does it stay
two-way (genuinely needs a guess)?
Stage 2: the interior-wall ruler min(pA,pB)/F_area from the decided-before F
machinery -- is that where the deciding sits, and does it tip the genuine survivors?

Run:  python3 malleable_chase.py                    # full, 24 worlds, parallel
      python3 malleable_chase.py --worlds 2 --nadd 500 --serial   # quick test
"""
from __future__ import annotations
from pathlib import Path
import sys, os, json, math, random, collections, argparse
from multiprocessing import Pool
import numpy as np
from scipy.stats import spearmanr, mannwhitneyu

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "corner-response-catalogue"))
import figures as F
import corner_response as CR

L, D, S, Sl, SN, CD = F.L, F.D, F.S, F.Sl, F.SN, F.CD
RES = HERE / "results"; RES.mkdir(exist_ok=True)
EPS = 1e-9
LOCAL_R = 10          # forced-burst radius, in S (settling is highly local; A found ~2S)
BURST_CAP = 60        # forced-burst slice cap

# A's recurring fingerprints and their rigid/malleable labels (stiffness line at radius 2)
_STIFF = json.loads((HERE.parent / "corner-response-catalogue" / "results" / "summary.json").read_text())["stiffness"]
RECUR = set(_STIFF)
MALLEABLE = {fp for fp, f in _STIFF.items() if f < CR.RIGID_CUT}


def forced_burst(before, edge, mid, cap=BURST_CAP, R=LOCAL_R):
    """Grow forced-only within R of the tie; never guess. Settles / saturates / caps."""
    P = L.Patch(list(before)); rr = R * S + EPS
    for _ in range(cap):
        if len(D.candidates(P, *edge[:3])) <= 1:
            return "settled"
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
        if placed == 0:
            return "saturated_open"
    return "cap_open"


def f_measures(before, edge):
    """Compatibility region F and each option's slice; wall-nearness = min(pA,pB)/F_area."""
    try:
        rank = Sl.rank_of(before); cm0 = Sl.constraints(before, rank); aF = Sl.area(Sl.region(cm0))
        cs = D.candidates(L.Patch(before), *edge[:3])
        if len(cs) != 2 or aF <= 0:
            return None
        pcs = [Sl.area(Sl.region(CD.after_first(before, c, rank))) for c in cs]
        if min(pcs) < 0:
            return None
        return dict(F=float(aF), wall=float(min(pcs) / aF))
    except Exception:
        return None


def grow_world_c(k):
    """Catalogue growth, plus burst + F-measures for every recurring-fingerprint tie."""
    rng = random.Random(CR.SEED0 + k)
    P = L.Patch(L.seed_patch(CR.centres()[k], 3 * S)); n0 = len(P.tris); r = 0
    active, done, ties = {}, set(), []
    status = "ok"

    def resolve(sk, rec):
        tie = active.pop(sk); done.add(sk)
        rec.update(world=k, drawer=rec.get("drawer"), fp=tie["fp"], malleable=tie["fp"] in MALLEABLE,
                   burst=tie["burst"], wall=tie["wall"], Farea=tie["Farea"])
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
                resolve(sk, rec)
            elif r - tie["first_slice"] >= CR.K:
                resolve(sk, dict(drawer="stayed_open"))
        for sk, n in cand.items():
            if n == 2 and sk not in active and sk not in done:
                e = fmap[sk]; mid = (e[0] + e[1]) / 2; before = list(P.tris)
                fp = CR.fingerprint(before, mid, CR.RPRIMARY)
                burst = wall = Farea = None
                if fp in RECUR:
                    burst = forced_burst(before, e, mid)
                    fm = f_measures(before, e)
                    if fm:
                        wall = fm["wall"]; Farea = fm["F"]
                active[sk] = dict(before=before, edge=e, first_slice=r, mid=mid,
                                  fp=fp, burst=burst, wall=wall, Farea=Farea)
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
    return dict(world=k, status=status, ties=[t for t in ties if t["fp"] in RECUR])


def score(worlds):
    ties = [t for w in worlds for t in w["ties"]]
    bursted = [t for t in ties if t["burst"] is not None]
    lines = [f"worlds {len(worlds)}; statuses {dict(collections.Counter(w['status'] for w in worlds))}; "
             f"recurring-fingerprint ties {len(ties)}; bursted {len(bursted)}"]
    lines.append(f"burst fates: {dict(collections.Counter(t['burst'] for t in bursted))}")

    # per-fingerprint burst-settle fraction
    byfp = collections.defaultdict(list)
    for t in bursted:
        byfp[t["fp"]].append(t["burst"] == "settled")
    settle_frac = {fp: np.mean(v) for fp, v in byfp.items() if len(v) >= CR.MIN_RECUR}
    mal = {fp: f for fp, f in settle_frac.items() if fp in MALLEABLE}
    rig = {fp: f for fp, f in settle_frac.items() if fp not in MALLEABLE}

    # method control: rigid fingerprints should burst-settle ~ 1.0
    rig_mean = float(np.mean(list(rig.values()))) if rig else 0.0
    lines.append(f"METHOD CONTROL: rigid fingerprints burst-settle mean {rig_mean:.3f} over {len(rig)} fps "
                 f"(want ~1.0; validates the separator)")

    # C1 -- much of the wobble is timing (secretly rigid = burst-settles every time)
    secret = [fp for fp, f in mal.items() if f >= 0.999]
    c1 = len(secret) / len(mal) if mal else 0.0
    lines.append(f"C1: {'HELD  ' if c1 >= 0.50 else 'FAILED'}  secretly-rigid (timing) malleable fps "
                 f"{len(secret)}/{len(mal)} = {c1:.1%} (need >= 50%)")

    # C2 -- a genuine core survives
    genuine = [fp for fp, f in mal.items() if f < 0.999]
    c2 = len(genuine) / len(mal) if mal else 0.0
    lines.append(f"C2: {'HELD  ' if c2 >= 0.15 else 'FAILED'}  genuine-(a) malleable fps "
                 f"{len(genuine)}/{len(mal)} = {c2:.1%} (need >= 15%)")

    # C3 -- interior ruler beats outer: settled ties nearer the wall than stayed-open
    wset = [t["wall"] for t in ties if t["wall"] is not None and t["drawer"] in ("single_keystone", "committee")]
    wopen = [t["wall"] for t in ties if t["wall"] is not None and t["drawer"] == "stayed_open"]
    if wset and wopen:
        _, p = mannwhitneyu(wset, wopen, alternative="less")
        # standardized effect (rank-biserial-ish via medians/IQR)
        eff = (np.median(wopen) - np.median(wset)) / (np.std(wset + wopen) + EPS)
        c3 = np.median(wset) < np.median(wopen) and p < 0.05
        lines.append(f"C3: {'HELD  ' if c3 else 'FAILED'}  wall-nearness settled median {np.median(wset):.3f} "
                     f"(n {len(wset)}) < stayed-open {np.median(wopen):.3f} (n {len(wopen)}); "
                     f"Mann-Whitney p {p:.2e}; std effect {eff:.3f} (B's outer-depth effect was ~0.1)")
    else:
        c3 = False; lines.append("C3: N/A  insufficient F-measures")

    # C4 -- within genuine-(a) fingerprints, burst-settlers nearer the wall than stayers
    gset = [t["wall"] for t in bursted if t["fp"] in genuine and t["burst"] == "settled" and t["wall"] is not None]
    gstay = [t["wall"] for t in bursted if t["fp"] in genuine and t["burst"] != "settled" and t["wall"] is not None]
    if len(gset) >= 5 and len(gstay) >= 5:
        _, p4 = mannwhitneyu(gset, gstay, alternative="less")
        c4 = np.median(gset) < np.median(gstay) and p4 < 0.05
        lines.append(f"C4: {'HELD  ' if c4 else 'did not hold'}  genuine-(a) burst-settlers wall-nearness median "
                     f"{np.median(gset):.3f} (n {len(gset)}) < stayers {np.median(gstay):.3f} (n {len(gstay)}); p {p4:.2e}")
    else:
        c4 = None; lines.append(f"C4: N/A  too few genuine-(a) settlers/stayers ({len(gset)}/{len(gstay)})")

    # reported: the true stiffness line (burst-settle fractions)
    dist = collections.Counter(round(f, 1) for f in mal.values())
    lines.append("  reported (true stiffness after removing timing; burst-settle fraction -> #malleable fps): " +
                 "; ".join(f"{b:.1f}:{dist[b]}" for b in sorted(dist)))

    summary = dict(recurring_ties=len(ties), bursted=len(bursted),
                   burst_fates=dict(collections.Counter(t["burst"] for t in bursted)),
                   method_control_rigid_settle=rig_mean,
                   C1=dict(held=c1 >= 0.5, frac=c1, secret=len(secret), malleable=len(mal)),
                   C2=dict(held=c2 >= 0.15, frac=c2, genuine=len(genuine)),
                   C3=dict(held=bool(c3), settled_wall=float(np.median(wset)) if wset else None,
                           open_wall=float(np.median(wopen)) if wopen else None),
                   C4=dict(held=c4, settler_wall=float(np.median(gset)) if gset else None,
                           stayer_wall=float(np.median(gstay)) if gstay else None),
                   true_stiffness=dict(sorted(((fp, round(float(f), 4)) for fp, f in mal.items()), key=lambda kv: kv[1])))
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
        worlds = [grow_world_c(k) for k in ids]
    else:
        with Pool(min(4, args.worlds), maxtasksperchild=1) as p:
            worlds = p.map(grow_world_c, ids)
    report, summary = score(worlds)
    print(report)
    (RES / "worlds.json").write_text(json.dumps(worlds, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
    (RES / "summary.json").write_text(json.dumps(summary, indent=2))
    (RES / "malleable_chase_report.txt").write_text(report + "\n")


if __name__ == "__main__":
    main()

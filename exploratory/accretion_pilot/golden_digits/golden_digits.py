#!/usr/bin/env python3
"""
golden_digits.py -- confirm ../slack/'s follow-up findings on 24 fresh worlds (PREREGISTRATION.md, frozen before this
file). Wiggle room F tracked every slice; at every two-way choice both options are grown forced-only up to 8 slices and
their pieces of F compared. `python3 golden_digits.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "slack"))
import slack as Sl
T, F_, L, D, S = Sl.T, Sl.F_, Sl.L, Sl.D, Sl.S
SEED0, N_ADD = 20261140, 1500
TAU = (1 + 5 ** 0.5) / 2
G = {"1/t^4": TAU ** -4, "1/(2t^2)": 1 / (2 * TAU ** 2), "1/t^3": TAU ** -3, "(5-sqrt5)/10": (5 - 5 ** 0.5) / 10,
     "1/(2t)": 1 / (2 * TAU), "1/t^2": TAU ** -2, "1/sqrt5": 5 ** -0.5, "1/2": 0.5}
RES = os.path.join(HERE, "results")


def centres():
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[24:48]


def world(k):
    rng = random.Random(SEED0 + k); c0 = centres()[k]
    P = L.Patch(L.seed_patch(c0, 3 * S)); n0 = len(P.tris); r = 0
    rank = Sl.rank_of(P.tris)
    trace = [(0, Sl.area(Sl.region(Sl.constraints(P.tris, rank))), "start")]; choices = []; status = "ok"
    while len(P.tris) - n0 < N_ADD:
        r += 1
        fr = P.frontier(); forced = {}; jam = False
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = True; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        if jam:
            status = "JAM"; break
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= N_ADD:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed:
            trace.append((r, Sl.area(Sl.region(Sl.constraints(P.tris, rank))), "forced")); continue
        if forced:
            continue
        e = fr[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
        base = list(P.tris); aF = Sl.area(Sl.region(Sl.constraints(base, rank)))
        rec = dict(slice=r, n_options=len(cs), area=aF)
        if len(cs) == 2 and aF > 0:
            QA, A, sA, rA = F_.sibling(base, cs[0]); QB, B, sB, rB = F_.sibling(base, cs[1])
            cA = Sl.constraints(list(QA.tris), rank); cB = Sl.constraints(list(QB.tris), rank)
            rec.update(A=Sl.area(Sl.region(cA)) / aF, B=Sl.area(Sl.region(cB)) / aF, overlap=Sl.area(Sl.region(cA, cB)) / aF,
                       sib=(sA, sB, rA, rB))
        t = rng.choice(cs); rec["picked"] = cs.index(t); P.add(t); choices.append(rec)
        trace.append((r, Sl.area(Sl.region(Sl.constraints(P.tris, rank))), "choice"))
    return dict(world=k, status=status, slices=r, trace=trace, choices=choices)


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(world, range(24))
    json.dump(W, open(os.path.join(RES, "worlds.json"), "w"))
    two = [c for w in W for c in w["choices"] if c.get("A") is not None]
    dead = [c for c in two if min(c["A"], c["B"]) == 0 and abs(max(c["A"], c["B"]) - 1) < 0.01]
    live = [c for c in two if c not in dead]
    clean = [c for c in live if c["A"] > 0 and c["B"] > 0 and c["overlap"] < 0.01 and abs(c["A"] + c["B"] - 1) < 0.01]
    lines = [f"worlds: statuses {dict(collections.Counter(w['status'] for w in W))}; choices {sum(len(w['choices']) for w in W)}, "
             f"two-option with F > 0: {len(two)}, dead-optioned {len(dead)}"]
    g1 = len(clean) >= 0.9 * len(live)
    lines.append(f"  G1: {'HELD  ' if g1 else 'FAILED'}  clean splits {len(clean)}/{len(live)} (need >= 90%)")
    mins = [min(c["A"], c["B"]) for c in clean]
    near = [min(G, key=lambda n: abs(G[n] - x)) for x in mins]
    hit = [n for n, x in zip(near, mins) if abs(G[n] - x) <= 0.002]
    g2 = bool(mins) and len(hit) >= 0.9 * len(mins)
    lines.append(f"  G2: {'HELD  ' if g2 else 'FAILED'}  smaller share within 0.002 of the golden family: {len(hit)}/{len(mins)} (need >= 90%)")
    cnt = collections.Counter(hit)
    mode = cnt.most_common(1)[0][0] if cnt else None
    lines.append(f"  G3: {'HELD  ' if mode == '1/t^2' else 'FAILED'}  commonest member {mode}; counts {dict(cnt.most_common())}")
    outside = sorted(round(x, 4) for n, x in zip(near, mins) if abs(G[n] - x) > 0.002)
    lines.append(f"      shares outside the family: {outside}")
    bad = 0; shr = 0
    for w in W:
        last = None; prev = None
        for r, a, kind in w["trace"]:
            if kind == "forced" and prev and prev > 0 and abs(a - prev) > 1e-6 * prev:
                shr += 1
                if last is None or r - last != 1:
                    bad += 1
            if kind == "choice":
                last = r
            prev = a
    lines.append(f"  G4: {'HELD  ' if bad == 0 else 'FAILED'}  forced slices that shrank F: {shr}; not exactly one slice after a choice: {bad}")
    emp = {w["world"] for w in W if any(a <= 0 for _, a, _ in w["trace"])}
    jams = {w["world"] for w in W if w["status"] == "JAM"}
    g5 = (emp <= jams) and (jams <= emp)
    lines.append(f"  G5: {'HELD  ' if g5 else 'FAILED'}{' (first half untestable: no F emptied)' if not emp else ''}  worlds with empty F {sorted(emp)}; "
                 f"jammed worlds {sorted(jams)}")
    kept = []
    for w in W:
        a = [c["area"] for c in w["choices"]]
        kept += [a[i + 1] / a[i] for i in range(len(a) - 1) if a[i] > 0 and a[i + 1] > 0]
    picks = [("larger" if (c["A"], c["B"])[c["picked"]] >= 0.5 else "smaller") for c in clean]
    lines.append(f"  reported: wiggle room kept per choice (main world) {dict(sorted(collections.Counter(round(x, 3) for x in kept).items()))}; "
                 f"main world took the larger piece {picks.count('larger')}, smaller {picks.count('smaller')}")
    print("\n".join(lines))
    open(os.path.join(RES, "golden_digits_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

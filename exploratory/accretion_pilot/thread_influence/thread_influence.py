#!/usr/bin/env python3
"""
thread_influence.py -- does influence travel as fast as the thread is made? (PREREGISTRATION.md, frozen before this
file.) 24 ordinary worlds from 24 different seed centres; at every choice both siblings are grown forced-only up to 12
slices; the difference between them (influence) is compared with the decided ribbon (the ribbon through each sibling's
chosen tile that lies along the front): who leads, and how fast each spreads. `python3 thread_influence.py`.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, hashlib, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gold_thread"))
import ribbons_EXPLORATORY as R
F, M, D, L, S = R.F, R.M, R.D, R.L, R.S
N_WORLDS, N_ADD, SEED0, AHEAD, MIN_D, MIN_SL = 24, 1500, 20261110, 12, 3, 5
RES = os.path.join(HERE, "results")
cen = F.cen


def centres():
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]   # one symmetry wedge (mirror lines every 18 deg)
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[:N_WORLDS]


def sibling(base, t):
    """forced-only growth up to AHEAD slices. returns patch, [(tile, slice)], status, slices reached."""
    Q = L.Patch(list(base))
    if not Q.legal(t):
        return Q, [(t, 0)], "ILLEGAL", 0
    Q.add(t); new = [(t, 0)]
    for s in range(1, AHEAD + 1):
        st, placed, any_forced = F.step(Q)
        if st == "JAM":
            return Q, new, "JAM", s - 1
        if not placed:
            return Q, new, ("needs_guess" if not any_forced else "stuck"), s - 1
        new += [(u, s) for u in placed]
    return Q, new, "ahead", AHEAD


def decided_ribbon(Q, t, u):
    legs, _ = R.legs_and_base(t)
    fams = sorted({M.edge_dir(p, q)[0] for p, q in legs},
                  key=lambda j: abs(math.cos(math.radians(18 + 72 * j) - cmath.phase(u))))
    j = fams[0]
    rib, _ = R.ribbons(list(Q.tris))
    root = rib[j][D.dkey(t)]
    return j, {k for k, r in rib[j].items() if r == root}


def slope(xs, ys):
    if len(xs) < 2 or np.ptp(xs) == 0:
        return float("nan")
    return float(np.polyfit(xs, ys, 1)[0])


def analyse(sibA, sibB, chosen, line):
    m, u = line
    xc = lambda z: ((z - m) * u.conjugate()).real / S
    yc = lambda z: abs(((z - m) * u.conjugate()).imag) / S
    smax = min(sibA[3], sibB[3])
    out = []
    for X, Y, t in ((sibA, sibB, chosen[0]), (sibB, sibA, chosen[1])):
        j, Rk = decided_ribbon(X[0], t, u)
        lead = []; hD = []; hR = []; leak = []; ss = []; onR = None; dl = []
        for s in range(1, smax + 1):
            Xs = [w for w, sl in X[1] if sl <= s]; Ys = [w for w, sl in Y[1] if sl <= s]
            ky = {D.dkey(w) for w in Ys}; kx = {D.dkey(w) for w in Xs}
            yo = [w for w in Ys if D.dkey(w) not in kx]
            dl = [w for w in Xs if D.dkey(w) not in ky and any(L.inside(cen(w), *v[1:]) for v in yo)]
            rs = [w for w in Xs if D.dkey(w) in Rk]
            if dl:
                xs = [xc(cen(w)) for w in dl]
                if len(dl) >= MIN_D:
                    for w in (dl[int(np.argmax(xs))], dl[int(np.argmin(xs))]):
                        lead.append(D.dkey(w) in Rk)
                ss.append(s); hD.append((max(xs) - min(xs)) / 2)
                xr = [xc(cen(w)) for w in rs]; hR.append((max(xr) - min(xr)) / 2 if xr else 0.0)
                leak.append(max(yc(cen(w)) for w in dl))
                onR = sum(D.dkey(w) in Rk for w in dl) / len(dl)
        out.append(dict(family=j, lead=lead, slices=ss, v_delta=slope(ss, hD), v_ribbon=slope(ss, hR),
                        v_leak=slope(ss, leak), share_on_R=onR, final_delta=len(dl) if smax else 0))
    return smax, out


def world(k):
    rng = random.Random(SEED0 + k); c0 = centres()[k]
    P = L.Patch(L.seed_patch(c0, 3 * S)); n0 = len(P.tris); r = 0; choices = []; status = "ok"
    while len(P.tris) - n0 < N_ADD:
        r += 1
        fr = P.frontier(); forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                status = "JAM"; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        if status == "JAM":
            break
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= N_ADD:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            continue
        e = fr[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
        sig = hashlib.md5(repr(sorted(D.dkey(t) for t in P.tris)).encode()).hexdigest()[:16]
        rec = dict(world=k, slice=r, n_options=len(cs), sig=sig)
        if len(cs) == 2:
            base = list(P.tris); line = F.front_line(P, e)
            sA, sB = sibling(base, cs[0]), sibling(base, cs[1])
            smax, sides = analyse(sA, sB, cs, line)
            rec.update(statuses=(sA[2], sB[2]), reached=(sA[3], sB[3]), sizes=(len(sA[1]), len(sB[1])), smax=smax, sides=sides)
        choices.append(rec)
        P.add(rng.choice(cs))
    hist = hashlib.md5(repr(sorted(D.dkey(t) for t in P.tris)).encode()).hexdigest()[:16]
    return dict(world=k, centre=[c0.real, c0.imag], status=status, slices=r, history=hist, choices=choices)


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(world, range(N_WORLDS))
    json.dump(W, open(os.path.join(RES, "worlds.json"), "w"))
    seen = set(); C = []
    for w in W:
        for c in w["choices"]:
            if c["sig"] not in seen:
                seen.add(c["sig"]); C.append(c)
    two = [c for c in C if c["n_options"] == 2]
    lines = [f"worlds: {len(W)}, statuses {sorted(set(w['status'] for w in W))}, distinct histories {len({w['history'] for w in W})}; "
             f"choices {sum(len(w['choices']) for w in W)}, distinct {len(C)}, with 2 options {len(two)}",
             f"sibling statuses {dict(collections.Counter(s for c in two for s in c['statuses']))}; slices both reached: "
             f"{sorted(c['smax'] for c in two)}",
             f"sibling sizes (tiles laid): {[tuple(c['sizes']) for c in two]}"]
    lead = [x for c in two for sd in c["sides"] for x in sd["lead"]]
    d1 = np.mean(lead) if lead else float("nan")
    lines.append(f"  D1: {'HELD  ' if d1 >= 0.7 else 'FAILED'}  leading tile of the difference lies on the decided ribbon in "
                 f"{sum(lead)}/{len(lead)} = {d1:.2f} (need >= 0.70)")
    ok = [c for c in two if c["smax"] >= MIN_SL and all(sd["v_ribbon"] > 0.1 for sd in c["sides"])]
    ratios = [float(np.mean([sd["v_delta"] / sd["v_ribbon"] for sd in c["sides"]])) for c in ok]
    d2n = sum(0.8 <= x <= 1.25 for x in ratios)
    d2 = bool(ratios) and d2n / len(ratios) >= 0.7
    lines.append(f"  D2: {'HELD  ' if d2 else 'FAILED'}  v_delta / v_ribbon in [0.8, 1.25] in {d2n}/{len(ratios)} choices (need >= 70%); "
                 f"ratios {sorted(round(x, 2) for x in ratios)}")
    vd = [float(np.nanmean([sd["v_delta"] for sd in c["sides"]])) for c in two if c["smax"] >= MIN_SL]
    md = float(np.nanmedian(vd)) if vd else float("nan")
    lines.append(f"  D3: {'HELD  ' if 0.67 <= md <= 1.13 else 'FAILED'}  median v_delta {md:.2f} edges/slice (need 0.67-1.13); "
                 f"values {sorted(round(x, 2) for x in vd)}")
    vr = [float(np.nanmean([sd["v_ribbon"] for sd in c["sides"]])) for c in two if c["smax"] >= MIN_SL]
    vl = [float(np.nanmean([sd["v_leak"] for sd in c["sides"]])) for c in two if c["smax"] >= MIN_SL]
    sh = [sd["share_on_R"] for c in two for sd in c["sides"] if sd["share_on_R"] is not None]
    lines.append(f"  reported: median v_ribbon {np.nanmedian(vr):.2f}; median forward leakage speed {np.nanmedian(vl):.2f} edges/slice; "
                 f"median share of the difference on the decided ribbon {np.median(sh):.2f}")
    print("\n".join(lines))
    open(os.path.join(RES, "thread_influence_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

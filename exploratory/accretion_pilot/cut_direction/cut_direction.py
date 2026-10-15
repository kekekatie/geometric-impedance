#!/usr/bin/env python3
"""
cut_direction.py -- does the direction of the cut in the wiggle room name the ribbon family that gets decided?
(PREREGISTRATION.md, frozen before this file.) 24 fresh ordinary worlds, patient scheduler. At every live two-way
choice: the cut line between the two options' pieces of F (each measured after its first slice), and, after both options
are grown 20 slices in lockstep, the decided strip (tiles one sibling has where the other has a different tile), its
edge-direction family shares, its long axis, and when each strip tile was built.
`python3 cut_direction.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, hashlib, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for sub in ("speed_of_now", "golden_digits", "perp_map"):
    sys.path.insert(0, os.path.join(HERE, "..", sub))
import speed_of_now as SN
import shapes_EXPLORATORY as SH
import perp_map as M
Sl, L, D, S = SN.Sl, SN.L, SN.D, SN.S
SEED0, N_ADD, N_WORLDS, AHEAD, TRAIN = 20261180, 1500, 24, 20, 12
C1_GAP, C2_NEED, C4_RATIO, C4_DEG = 0.15, 0.80, 3.0, 20.0
RES = os.path.join(HERE, "results")
cen = lambda t: sum(t[1:]) / 3
is_leg = lambda p, q: abs(abs(q - p) - S) < 1e-4 * S


def centres():
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[144:144 + N_WORLDS]


def families(t):
    return {M.edge_dir(p, q)[0] for p, q in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])) if is_leg(p, q)}


def whole_key(tiles, z):
    rk = lambda w: (round((w - z).real / S, 3), round((w - z).imag / S, 3))
    return hashlib.md5(repr(sorted((t[0], rk(t[1]), rk(t[2]), rk(t[3])) for t in tiles)).encode()).hexdigest()[:16]


def after_first(base, c, rank):
    Q = L.Patch(list(base)); Q.add(c); st, n, kind = SN.patient(Q, random.Random(0))
    tiles = list(Q.tris) if kind == "forced" else base + [c]
    return Sl.constraints(tiles, rank)


def grow(base, c, stream):
    Q = L.Patch(list(base)); Q.add(c); rng = random.Random(stream); built = {D.dkey(c): 0}; status = "ok"
    for s in range(1, AHEAD + 1):
        n0 = len(Q.tris); st, n, kind = SN.patient(Q, rng)
        if st == "JAM":
            status = "JAM"; break
        for t in Q.tris[n0:]:
            built[D.dkey(t)] = s
    new = Q.tris[len(base):]
    return new, built, status


def strip(newA, newB):
    kA = {D.dkey(t) for t in newA}; kB = {D.dkey(t) for t in newB}
    oA = [t for t in newA if D.dkey(t) not in kB]; oB = [t for t in newB if D.dkey(t) not in kA]
    cov = lambda p, others: any(L.inside(p, *u[1:]) for u in others)
    return [t for t in oA if cov(cen(t), oB)], [t for t in oB if cov(cen(t), oA)]


def world(k):
    rng = random.Random(SEED0 + k); c0 = centres()[k]
    P = L.Patch(L.seed_patch(c0, 3 * S)); n0 = len(P.tris); r = 0; rank = Sl.rank_of(P.tris); out = []; status = "ok"
    skipped = collections.Counter()
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
        if placed or forced:
            continue
        cs = SN.ordered(D.candidates(P, *fr[0][:3]))
        if len(cs) == 2:
            base = list(P.tris); cm0 = Sl.constraints(base, rank); aF = Sl.area(Sl.region(cm0))
            cA, cB = after_first(base, cs[0], rank), after_first(base, cs[1], rank)
            pA, pB = Sl.area(Sl.region(cA)), Sl.area(Sl.region(cB))
            line = SH.cut_line(cm0, cA, cB)
            if aF <= 0 or pA <= 0 or pB <= 0:
                skipped["not live"] += 1
            elif line is None:
                skipped["no cut line"] += 1
            else:
                z = (fr[0][0] + fr[0][1]) / 2; key = whole_key(base, z)
                n_, c_ = line
                direction = (round(((math.degrees(math.atan2(n_[1], n_[0])) + 90) % 180) / 36) * 36) % 180
                stream = SEED0 * 1000 + int(key, 16) % (2 ** 31)
                (nA, bA, sA), (nB, bB, sB) = grow(base, cs[0], stream), grow(base, cs[1], stream)
                uA, uB = strip(nA, nB)
                st = uA + uB
                rec = dict(world=k, slice=r, key=key, direction=int(direction), line_angle=float((math.degrees(math.atan2(n_[1], n_[0])) + 90) % 180),
                           pieces=[pA / aF, pB / aF], status=[sA, sB], n_strip=len(st))
                if st:
                    sh = [sum(j in families(t) for t in st) / len(st) for j in range(5)]
                    rec["shares"] = sh
                    pts = np.array([cen(t) for t in st]) / S
                    X = np.c_[pts.real - pts.real.mean(), pts.imag - pts.imag.mean()]
                    w, v = np.linalg.eigh(X.T @ X / len(pts))
                    ax = math.degrees(math.atan2(v[1, -1], v[0, -1])) % 180
                    rec.update(ratio=float(math.sqrt(w[-1] / max(w[0], 1e-12))), axis=float(ax))
                    # settled vs built: for strip tiles, slice built vs distance from the choice point along the axis
                    u = complex(v[0, -1], v[1, -1]); zc = cen(cs[0])
                    rec["built"] = [(float(abs(((cen(t) - zc) * u.conjugate()).real) / S), (bA if t in uA else bB)[D.dkey(t)]) for t in st]
                out.append(rec)
        P.add(rng.choice(cs))
    return dict(world=k, status=status, skipped=dict(skipped), choices=out)


def angdiff(a, b):
    d = abs(a - b) % 180
    return min(d, 180 - d)


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(world, range(N_WORLDS))
    json.dump(W, open(os.path.join(RES, "worlds.json"), "w"), default=lambda o: o.item() if hasattr(o, "item") else str(o))
    first = {}
    for w in W:
        for c in w["choices"]:
            first.setdefault(c["key"], c)
    U = list(first.values())
    withs = [c for c in U if c.get("shares")]
    lines = [f"worlds: statuses {dict(collections.Counter(w['status'] for w in W))}; skipped {dict(sum((collections.Counter(w['skipped']) for w in W), collections.Counter()))}; "
             f"choices used {sum(len(w['choices']) for w in W)}; distinct situations {len(U)}; with a non-empty strip {len(withs)}; "
             f"cut directions {dict(collections.Counter(c['direction'] for c in U))}"]
    fam = lambda c: int(np.argmax(c["shares"]))
    gap = lambda c: sorted(c["shares"])[-1] - sorted(c["shares"])[-2]
    c1n = sum(gap(c) >= C1_GAP for c in withs)
    lines.append(f"  C1: {'HELD  ' if withs and c1n >= 0.7 * len(withs) else 'FAILED'}  decided family beats the next by >= {C1_GAP} in {c1n}/{len(withs)} (need >= 70%); "
                 f"top shares median {np.median([max(c['shares']) for c in withs]):.2f}, gaps median {np.median([gap(c) for c in withs]):.2f}")
    train = [c for c in withs if c["world"] < TRAIN]
    seen = {c["key"] for c in train}
    test = [c for c in withs if c["world"] >= TRAIN and c["key"] not in seen]
    table = {}
    for d in sorted({c["direction"] for c in train}):
        cnt = collections.Counter(fam(c) for c in train if c["direction"] == d)
        table[d] = cnt.most_common(1)[0][0]
        lines.append(f"      training: cut direction {d:3d} deg -> families {dict(cnt.most_common())}")
    lines.append(f"      lookup table (fixed from training): {table}")
    pred = [c for c in test if c["direction"] in table]
    c2n = sum(table[c["direction"]] == fam(c) for c in pred)
    lines.append(f"  C2: {'HELD  ' if pred and c2n >= C2_NEED * len(pred) else 'FAILED'}  table predicts the decided family in {c2n}/{len(pred)} test situations "
                 f"(need >= 80%); test situations with an unseen direction: {len(test) - len(pred)}")
    c3 = len(set(table.values())) == len(table)
    lines.append(f"  C3: {'HELD  ' if c3 else 'FAILED'}  table is one-to-one: {len(table)} directions -> {len(set(table.values()))} distinct families")
    el = [c for c in withs if c["ratio"] >= C4_RATIO]
    c4n = sum(angdiff(c["axis"], (18 + 72 * fam(c) + 90) % 180) <= C4_DEG for c in el)
    lines.append(f"  C4: {'HELD  ' if el and c4n >= 0.7 * len(el) else 'FAILED'}  long axis within {C4_DEG:.0f} deg of perpendicular to the family's edges in {c4n}/{len(el)} "
                 f"elongated strips (need >= 70%); angles {sorted(round(angdiff(c['axis'], (18 + 72 * fam(c) + 90) % 180)) for c in el)}")
    # reported
    pairs = [(d, s) for c in withs for d, s in c["built"]]
    if pairs:
        dd = np.array([p[0] for p in pairs]); ss = np.array([p[1] for p in pairs])
        bins = [(0, 2), (2, 4), (4, 6), (6, 8), (8, 12), (12, 20)]
        lines.append("  reported (settled vs built): median slice at which strip tiles were built, by distance from the choice point along the strip: " +
                     "; ".join(f"{a}-{b} edges: {np.median(ss[(dd >= a) & (dd < b)]):.0f} (n {int(((dd >= a) & (dd < b)).sum())})" for a, b in bins if ((dd >= a) & (dd < b)).any()))
    lines.append(f"  reported: all situations (train and test) agreeing with the table: {sum(table.get(c['direction']) == fam(c) for c in withs)}/{len(withs)}; "
                 f"strip sizes median {np.median([c['n_strip'] for c in U]):.0f}; empty strips {len(U) - len(withs)}")
    print("\n".join(lines))
    open(os.path.join(RES, "cut_direction_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

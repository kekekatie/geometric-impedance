#!/usr/bin/env python3
"""
who_made_it.py -- can the tiling tell who made it? (PREREGISTRATION.md, frozen before this file.)
SELECT worlds toss a fair coin at each choice; REVEAL worlds draw a hidden offset t0 uniformly from the seed patch's
wiggle room and take, at each choice, the option whose piece contains it. Part 1: 48 seeds x both modes (dead ends,
vertex-type frequencies). Part 2: one seed, 40 worlds per mode (which first-choice piece the finished tiling lies in).
`python3 who_made_it.py`.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "slack"))
import slack as Sl
F_, L, D, S = Sl.F_, Sl.L, Sl.D, Sl.S
N_ADD, NPERM = 1500, 2000
RES = os.path.join(HERE, "results")


def centres48():
    ks = [complex(*k) for k in L.corners(L.REF)]
    ks = [z for z in ks if abs(z) > 1e-9 and -1e-6 <= math.degrees(cmath.phase(z)) % 360 <= 18 + 1e-6]
    ks.sort(key=lambda z: (round(abs(z), 9), round(cmath.phase(z) % (2 * math.pi), 9)))
    return ks[:48]


def sample_in(poly, rng):
    tri = [(poly[0], poly[i], poly[i + 1]) for i in range(1, len(poly) - 1)]
    ar = [abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) / 2 for a, b, c in tri]
    a, b, c = rng.choices(tri, weights=ar)[0]
    u, v = rng.random(), rng.random()
    if u + v > 1:
        u, v = 1 - u, 1 - v
    return (a[0] + u * (b[0] - a[0]) + v * (c[0] - a[0]), a[1] + u * (b[1] - a[1]) + v * (c[1] - a[1]))


def contains(cm, t):
    return all(Sl.WIN[rk][0][i][0] * t[0] + Sl.WIN[rk][0][i][1] * t[1] >= c - 1e-12 for (rk, i), c in cm.items())


def vertex_types(P):
    mids = np.array([(e[0] + e[1]) / 2 for e in P.frontier()])
    cnt = collections.Counter()
    for k, lst in P.V.items():
        if abs(sum(d for _, d, _ in lst) - 2 * math.pi) > 1e-6:
            continue
        z = complex(*k)
        if np.min(np.abs(mids - z)) < 2 * S:
            continue
        cnt[str(L.star(lst))] += 1
    return dict(cnt)


def world(args):
    mode, centre, stream = args
    rng = random.Random(stream)
    P = L.Patch(L.seed_patch(centre, 3 * S)); n0 = len(P.tris); rank = Sl.rank_of(P.tris)
    t0 = sample_in(Sl.region(Sl.constraints(P.tris, rank)), rng) if mode == "REVEAL" else None
    status = "ok"; choices = []; fallbacks = 0; first = None
    while len(P.tris) - n0 < N_ADD:
        st, placed, anyf = F_.step(P)
        if st == "JAM":
            status = "JAM"; break
        if placed or anyf:
            continue
        e = P.frontier()[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
        if len(cs) != 2:
            P.add(rng.choice(cs)); continue
        base = list(P.tris); aF = Sl.area(Sl.region(Sl.constraints(base, rank)))
        cms = [Sl.constraints(list(F_.sibling(base, c)[0].tris), rank) for c in cs]
        shares = [Sl.area(Sl.region(cm)) / aF if aF > 0 else None for cm in cms]
        if mode == "SELECT":
            k = rng.randrange(2)
        else:
            inside = [contains(cm, t0) for cm in cms]
            if sum(inside) == 1:
                k = inside.index(True)
            else:
                fallbacks += 1; k = rng.choices([0, 1], weights=[s or 0 for s in shares])[0] if shares[0] is not None and sum(shares) > 0 else rng.randrange(2)
        dead = shares[0] is not None and min(shares) == 0
        smaller = None if shares[0] is None or shares[0] == shares[1] else (shares[k] < shares[1 - k])
        choices.append(dict(shares=shares, picked=k, dead_option=dead, took_dead=dead and shares[k] == 0, took_smaller=smaller))
        if first is None:
            first = dict(cms=[{f"{a}|{b}": c for (a, b), c in cm.items()} for cm in cms], shares=shares)
        P.add(cs[k])
    # where does the finished world lie relative to the first choice's pieces? (read from the finished tiling only)
    first_piece = None
    if first is not None and status == "ok":
        poly = Sl.region(Sl.constraints(P.tris, rank))
        if poly and Sl.area(poly) > 0:
            cx = sum(p[0] for p in poly) / len(poly); cy = sum(p[1] for p in poly) / len(poly)
            ins = [contains({tuple(int(x) for x in key.split("|")): c for key, c in cm.items()}, (cx, cy)) for cm in first["cms"]]
            if sum(ins) == 1:
                fs = first["shares"]; j = ins.index(True)
                first_piece = "smaller" if fs[j] < fs[1 - j] else "larger"
    return dict(mode=mode, stream=stream, status=status, choices=choices, fallbacks=fallbacks, types=vertex_types(P),
                first_piece=first_piece, first_shares=first and first["shares"])


def main():
    os.makedirs(RES, exist_ok=True)
    C = centres48()
    part1 = [("SELECT", C[k], 20261200 + k) for k in range(48)] + [("REVEAL", C[k], 20261300 + k) for k in range(48)]
    part2 = [("SELECT", C[0], 20261400 + i) for i in range(40)] + [("REVEAL", C[0], 20261500 + i) for i in range(40)]
    with Pool(4, maxtasksperchild=1) as p:
        W1 = p.map(world, part1); W2 = p.map(world, part2)
    json.dump(dict(part1=W1, part2=W2), open(os.path.join(RES, "worlds.json"), "w"),
              default=lambda o: o.item() if hasattr(o, "item") else str(o))     # numpy scalars
    lines = []
    for mode in ("SELECT", "REVEAL"):
        ws = [w for w in W1 if w["mode"] == mode]; ch = [c for w in ws for c in w["choices"]]
        lines.append(f"Part 1 {mode}: jams {sum(w['status'] == 'JAM' for w in ws)}/48; choices {len(ch)}; dead options met "
                     f"{sum(c['dead_option'] for c in ch)}, taken {sum(c['took_dead'] for c in ch)}; took the smaller piece "
                     f"{sum(c['took_smaller'] is True for c in ch)}/{sum(c['took_smaller'] is not None for c in ch)}; fallbacks "
                     f"{sum(w['fallbacks'] for w in ws)}")
    rj = sum(w["status"] == "JAM" or any(c["took_dead"] for c in w["choices"]) for w in W1 if w["mode"] == "REVEAL")
    lines.append(f"  W1: {'HELD  ' if rj == 0 else 'FAILED'}  REVEAL worlds that took a dead option or jammed: {rj}/48")
    types = sorted({t for w in W1 for t in w["types"]})
    freq = lambda w: np.array([w["types"].get(t, 0) for t in types], float) / max(1, sum(w["types"].values()))
    X = np.array([freq(w) for w in W1]); y = np.array([w["mode"] == "REVEAL" for w in W1])
    rng = np.random.default_rng(2026); worst = 1.0; rows = []
    for j, t in enumerate(types):
        obs = abs(X[y, j].mean() - X[~y, j].mean())
        perm = [abs(X[yy, j].mean() - X[~yy, j].mean()) for yy in (rng.permutation(y) for _ in range(NPERM))]
        pv = (1 + sum(p_ >= obs for p_ in perm)) / (NPERM + 1); worst = min(worst, pv)
        sd = X[:, j].std() or 1
        rows.append(f"{t}: SELECT {X[~y, j].mean():.4f} vs REVEAL {X[y, j].mean():.4f}, effect {obs / sd:.2f} SD, p {pv:.3f}")
    w2 = worst >= 0.01 / len(types)
    lines.append(f"  W2: {'HELD  ' if w2 else 'FAILED'}  no vertex type differs at p < 0.01/{len(types)}; smallest p {worst:.4f}")
    lines += ["      " + r for r in rows]
    for mode in ("SELECT", "REVEAL"):
        ws = [w for w in W2 if w["mode"] == mode and w["first_piece"]]
        k = sum(w["first_piece"] == "smaller" for w in ws); n = len(ws)
        fs = [w["first_shares"] for w in W2 if w["first_shares"]][0]; s = min(fs)
        target = 0.5 if mode == "SELECT" else s
        lo, hi = target - 1.96 * math.sqrt(target * (1 - target) / n), target + 1.96 * math.sqrt(target * (1 - target) / n)
        ok = lo <= k / n <= hi
        lines.append(f"  W3 {mode}: in the smaller first-choice piece {k}/{n} = {k / n:.3f}; expected {target:.3f} "
                     f"(95% interval {lo:.3f}-{hi:.3f}): {'consistent' if ok else 'NOT consistent'}; first-choice shares {[round(x, 3) for x in fs]}")
        if mode == "SELECT":
            w3s = ok
        else:
            w3r = ok
    lines.append(f"  W3: {'HELD  ' if w3s and w3r else 'FAILED'}  the crowd carries the signature")
    print("\n".join(lines))
    open(os.path.join(RES, "who_made_it_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

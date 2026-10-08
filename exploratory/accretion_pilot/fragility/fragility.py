#!/usr/bin/env python3
"""
fragility.py -- what can a choice un-make? (PREREGISTRATION.md, frozen before this file.)
Ordinary worlds grown with the patient scheduler; at every guess both siblings are grown forced-only for up to 8 rounds
and compared: un-made tiles, changed vertices, fragility by vertex type, the un-made region's shape, and its relation to
the local front line. `python3 fragility.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, hashlib, collections
from multiprocessing import Pool
import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "perp_map"))
import perp_map as M
D, L, S = M.D, M.L, M.S
N_WORLDS, N_ADD, SEED0, AHEAD, FRONT_R, NEAR, MIN_N = 12, 1500, 20261090, 8, 2.0, 1.5, 6
RES = os.path.join(HERE, "results")
cen = lambda t: sum(t[1:]) / 3


def full(V, k):
    return abs(sum(d for _, d, _ in V[k]) - 2 * math.pi) < 1e-6


def corner_keys(tiles):
    return {L.key(z) for t in tiles for z in t[1:]}


def step(P):
    """one round of forced growth. returns (status, placed tiles, forced-but-unplaced flag)."""
    forced = {}
    for e in P.frontier():
        cs = D.candidates(P, *e[:3])
        if not cs:
            return "JAM", [], False
        if len(cs) == 1:
            forced.setdefault(D.dkey(cs[0]), cs[0])
    placed = []
    for t in forced.values():
        if P.legal(t):
            P.add(t); placed.append(t)
    return "ok", placed, bool(forced)


def sibling(tiles, t):
    Q = L.Patch(list(tiles))
    if not Q.legal(t):
        return Q, [t], "ILLEGAL", 0
    Q.add(t); new = [t]; status = "ahead"
    for rr in range(AHEAD):
        st, placed, any_forced = step(Q)
        if st == "JAM":
            return Q, new, "JAM", rr
        if not placed:
            return Q, new, ("needs_guess" if not any_forced else "stuck"), rr
        new += placed
    return Q, new, status, AHEAD


def front_line(P, e):
    m = (e[0] + e[1]) / 2
    mids = np.array([(f[0] + f[1]) / 2 for f in P.frontier()])
    near = mids[np.abs(mids - m) <= FRONT_R * S]
    X = np.c_[near.real - near.real.mean(), near.imag - near.imag.mean()]
    w, v = np.linalg.eigh(X.T @ X)
    u = complex(v[0, -1], v[1, -1])
    return m, u / abs(u)


def compare(base_keys, QA, A, QB, B, line):
    m, u = line
    dist = lambda z: abs(((z - m) * u.conjugate()).imag) / S
    kA = {D.dkey(t) for t in A}; kB = {D.dkey(t) for t in B}
    onlyA = [t for t in A if D.dkey(t) not in kB]; onlyB = [t for t in B if D.dkey(t) not in kA]
    covered = lambda p, others: any(L.inside(p, *u_[1:]) for u_ in others)
    unA = [t for t in onlyA if covered(cen(t), onlyB)]; unB = [t for t in onlyB if covered(cen(t), onlyA)]
    changed = (corner_keys(unA) | corner_keys(unB)) - base_keys
    exposed = []
    for Q, X, Y, YQ in ((QA, A, B, QB), (QB, B, A, QA)):
        Yset = corner_keys(Y)
        for k in corner_keys(X) - base_keys:
            if not full(Q.V, k):
                continue
            z = complex(*k)
            if k not in Yset and not covered(z, Y):
                continue
            exposed.append(dict(type=str(L.star(Q.V[k])), changed=k in changed, dist=dist(z)))
    cents = np.array([cen(t) for t in unA + unB]) / S
    shape = None
    if len(cents) >= MIN_N:
        X = np.c_[cents.real - cents.real.mean(), cents.imag - cents.imag.mean()]
        w, v = np.linalg.eigh(X.T @ X / len(cents))
        axis = complex(v[0, -1], v[1, -1])
        ang = abs(math.degrees(cmath.phase(axis * u.conjugate()))) % 180
        shape = dict(ratio=float(math.sqrt(w[-1] / max(w[0], 1e-12))), angle_to_front=float(min(ang, 180 - ang)))
    cd = [dist(complex(*k)) for k in changed]
    return dict(n_unmade=len(unA) + len(unB), n_changed=len(changed), shape=shape,
                near_share=float(np.mean([d <= NEAR for d in cd])) if cd else None, exposed=exposed)


def world(k):
    rng = random.Random(SEED0 + k)
    P = L.Patch(L.seed_patch(0j, 3 * S)); n0 = len(P.tris); r = 0; choices = []; status = "ok"
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
        cs = sorted(D.candidates(P, *e[:3]), key=lambda u: (u[0], L.key(u[1]), L.key(u[2]), L.key(u[3])))
        sig = hashlib.md5(repr(sorted(D.dkey(t) for t in P.tris)).encode()).hexdigest()[:16]
        rec = dict(world=k, round=r, n_tiles=len(P.tris), n_options=len(cs), sig=sig, frontier=len(fr))
        if len(cs) == 2:
            base = list(P.tris); base_keys = corner_keys(base); line = front_line(P, e)
            (QA, A, sA, rA), (QB, B, sB, rB) = sibling(base, cs[0]), sibling(base, cs[1])
            rec.update(status=(sA, sB), rounds=(rA, rB), **compare(base_keys, QA, A, QB, B, line))
        choices.append(rec)
        P.add(rng.choice(cs))
    return dict(world=k, status=status, rounds=r, tiles=len(P.tris) - n0, choices=choices)


def flip_sites():
    """mean number of degree-3 rhombus vertices within 1 edge of a vertex of each type, in the reference tiling."""
    V = L.corners(L.REF); nb = collections.defaultdict(set)
    for t in L.REF:
        for p, q in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
            if abs(abs(q - p) - S) < 1e-4 * S:
                nb[L.key(p)].add(L.key(q)); nb[L.key(q)].add(L.key(p))
    out = collections.defaultdict(list)
    for k in nb:
        if abs(complex(*k)) > 0.5 or not full(V, k) or not all(full(V, j) for j in nb[k]):
            continue
        out[str(L.star(V[k]))].append(sum(len(nb[j]) == 3 for j in nb[k] | {k}))
    return {ty: float(np.mean(v)) for ty, v in out.items()}


def eta2(y, lab):
    y = np.asarray(y, float); tot = ((y - y.mean()) ** 2).sum(); g = collections.defaultdict(list)
    for yi, li in zip(y, lab):
        g[li].append(yi)
    return float(sum(len(v) * (np.mean(v) - y.mean()) ** 2 for v in g.values()) / tot) if tot else float("nan")


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(world, range(N_WORLDS))
    json.dump(W, open(os.path.join(RES, "worlds.json"), "w"))
    allc = [c for w in W for c in w["choices"]]
    seen = set(); C = []
    for c in allc:
        if c["sig"] not in seen:
            seen.add(c["sig"]); C.append(c)
    two = [c for c in C if c["n_options"] == 2]
    lines = [f"worlds: statuses {[w['status'] for w in W]}; tiles {[w['tiles'] for w in W]}; rounds {[w['rounds'] for w in W]}",
             f"choices: {len(allc)} in total, {len(C)} distinct; options per choice {dict(collections.Counter(c['n_options'] for c in C))}",
             f"choices per world {[len(w['choices']) for w in W]}; mean rounds between choices "
             f"{np.mean([w['rounds'] / max(1, len(w['choices'])) for w in W]):.1f}; choice rounds (world 0) {[c['round'] for c in W[0]['choices']]}"]
    f0 = all(c["n_options"] == 2 for c in C) and all("ILLEGAL" not in c["status"] for c in two)
    jam = collections.Counter(tuple(sorted(s == "JAM" for s in c["status"])) for c in two)
    lines.append(f"  F0: {'PASS' if f0 else 'FAIL'}  every choice has exactly 2 options and legal first tiles")
    lines.append(f"  dead ends (sibling jams): neither {jam[(False, False)]}, one {jam[(False, True)]}, both {jam[(True, True)]}; "
                 f"sibling statuses {dict(collections.Counter(s for c in two for s in c['status']))}; rounds ahead "
                 f"median {np.median([x for c in two for x in c['rounds']]):.0f}")
    lines.append(f"  un-made tiles per choice: {sorted(c['n_unmade'] for c in two)}")
    shp = [c["shape"] for c in two if c["shape"]]
    f1n = sum(s["ratio"] >= 3 for s in shp)
    f1 = bool(shp) and f1n / len(shp) >= 0.7
    lines.append(f"  F1: {'HELD  ' if f1 else 'FAILED'}  un-made region elongated (ratio >= 3) in {f1n}/{len(shp)} choices (need >= 70%); "
                 f"ratios {sorted(round(s['ratio'], 1) for s in shp)}; angle to front line {sorted(round(s['angle_to_front']) for s in shp)}")
    big = [c for c in two if c["n_changed"] >= MIN_N]
    f3n = sum(c["near_share"] >= 0.8 for c in big)
    f3 = bool(big) and f3n / len(big) >= 0.7
    lines.append(f"  F3: {'HELD  ' if f3 else 'FAILED'}  >= 80% of changed vertices within {NEAR} edges of the front line in {f3n}/{len(big)} "
                 f"choices (need >= 70%); shares {sorted(round(c['near_share'], 2) for c in big)}")
    ex = [x for c in two for x in c["exposed"]]
    fs = flip_sites()
    by = collections.defaultdict(lambda: [0, 0])
    for x in ex:
        by[x["type"]][0] += x["changed"]; by[x["type"]][1] += 1
    types = [ty for ty, (a, n) in by.items() if n >= 30 and ty in fs]
    frag = {ty: by[ty][0] / by[ty][1] for ty in types}
    rho = spearmanr([fs[ty] for ty in types], [frag[ty] for ty in types]).correlation if len(types) >= 3 else float("nan")
    lines.append(f"  vertex types (flip sites, fragility, exposures): " + "; ".join(
        f"{i}: {fs[ty]:.2f}, {frag[ty]:.3f}, {by[ty][1]}" for i, ty in enumerate(sorted(types, key=lambda t: fs[t]))))
    lines.append(f"  F2: {'HELD  ' if rho >= 0.5 else 'FAILED'}  Spearman(flip sites, fragility) over {len(types)} types = {rho:+.3f} (need >= +0.5)")
    e_where = eta2([x["changed"] for x in ex], [int(x["dist"] / 0.5) for x in ex])
    e_what = eta2([x["changed"] for x in ex], [x["type"] for x in ex])
    lines.append(f"  F4: {'HELD  ' if e_where > e_what else 'FAILED'}  eta2 of changed by distance band {e_where:.3f} vs by vertex type {e_what:.3f}; "
                 f"exposed {len(ex)}, changed share {np.mean([x['changed'] for x in ex]):.3f}")
    print("\n".join(lines))
    open(os.path.join(RES, "fragility_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

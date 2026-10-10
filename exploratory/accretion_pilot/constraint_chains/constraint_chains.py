#!/usr/bin/env python3
"""
constraint_chains.py -- which route carries a choice's consequences? (PREREGISTRATION.md, frozen before this file.)
For every tile in the difference between two siblings, find its critical tiles (single-removal: without u, the forcing
edge no longer has t as its unique candidate) and classify the links from differing parents: decided ribbon, other edge,
corner, distant. Advances of the difference along the front get a best route. `python3 constraint_chains.py`.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, hashlib, collections
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "thread_influence"))
import thread_influence as T
R, F, M, D, L, S = T.R, T.F, T.M, T.D, T.L, T.S
AHEAD, NBR, KEY_R, N_BASE = 12, 2.5, 3.0, 400
RES = os.path.join(HERE, "results")
cen = F.cen
vkeys = lambda t: {L.key(z) for z in t[1:]}
ROUTES = ["decided ribbon", "other edge", "corner", "distant", "none"]


def config_key(tiles, m):
    rk = lambda w: (round((w - m).real / S, 3), round((w - m).imag / S, 3))
    items = sorted((t[0], rk(t[1]), rk(t[2]), rk(t[3])) for t in tiles if abs(cen(t) - m) <= KEY_R * S)
    return hashlib.md5(repr(items).encode()).hexdigest()[:16]


def sibling(base, t):
    """forced-only growth recording, for each placed tile, (slice, forcing edge (p, q, r, owner))."""
    Q = L.Patch(list(base))
    if not Q.legal(t):
        return Q, {}, "ILLEGAL", 0
    Q.add(t); rec = {D.dkey(t): (t, 0, None)}
    for s in range(1, AHEAD + 1):
        forced = {}
        for e in Q.frontier():
            cs = D.candidates(Q, *e[:3])
            if not cs:
                return Q, rec, "JAM", s - 1
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), (cs[0], e))
        placed = 0
        for k, (u, e) in forced.items():
            if Q.legal(u):
                Q.add(u); rec[k] = (u, s, e); placed += 1
        if not placed:
            return Q, rec, ("needs_guess" if not forced else "stuck"), s - 1
    return Q, rec, "ahead", AHEAD


def criticals(base, rec, t, s, e):
    """(Z ok, list of critical context tiles)."""
    c = cen(t)
    ctx = [u for u in base if abs(cen(u) - c) <= NBR * S] + \
          [u for u, sl, _ in rec.values() if 0 <= sl < s and abs(cen(u) - c) <= NBR * S]
    owner = e[3]
    if all(D.dkey(u) != D.dkey(owner) for u in ctx):
        ctx.append(owner)
    ok = lambda tiles: (lambda cs: len(cs) == 1 and D.dkey(cs[0]) == D.dkey(t))(D.candidates(L.Patch(tiles), *e[:3]))
    if not ok(ctx):
        return False, []
    crit = [owner]
    for i, u in enumerate(ctx):
        if D.dkey(u) == D.dkey(owner):
            continue
        if not ok(ctx[:i] + ctx[i + 1:]):
            crit.append(u)
    return True, crit


def contact(u, t, jstar, Rk):
    shared = vkeys(u) & vkeys(t)
    if len(shared) == 2:
        pts = {L.key(z): z for z in t[1:]}; p, q = [pts[k] for k in shared]
        if R.is_leg(p, q) and M.edge_dir(p, q)[0] == jstar and D.dkey(u) in Rk and D.dkey(t) in Rk:
            return "decided ribbon"
        return "other edge"
    return "corner" if len(shared) == 1 else "distant"


def analyse_choice(base, cs, line, rng):
    m, u = line
    xc = lambda z: ((z - m) * u.conjugate()).real / S
    sib = [sibling(base, c) for c in cs]
    smax = min(sib[0][3], sib[1][3])
    out = dict(smax=smax, statuses=[x[2] for x in sib], sides=[])
    for (Q, rec, st, rr), (Q2, rec2, _, _), t0 in ((sib[0], sib[1], cs[0]), (sib[1], sib[0], cs[1])):
        X = {k: v for k, v in rec.items() if v[1] <= smax}; Y = {k: v for k, v in rec2.items() if v[1] <= smax}
        yo = [v[0] for k, v in Y.items() if k not in X]
        delta = {k for k, v in X.items() if k not in Y and any(L.inside(cen(v[0]), *w[1:]) for w in yo)}
        jstar, Rk = T.decided_ribbon(Q, t0, u)
        links, z_fail, tile_routes, adv_routes, ncrit = [], 0, [], [], []
        order = sorted(delta, key=lambda k: X[k][1])
        lo = hi = None
        for k in order:
            t, s, e = X[k]
            x = xc(cen(t))
            if s == 0:
                lo = hi = x; continue
            okz, crit = criticals(base, rec, t, s, e)
            if not okz:
                z_fail += 1; continue
            ncrit.append(len(crit))
            kinds = [contact(p, t, jstar, Rk) for p in crit if D.dkey(p) in delta]
            links += kinds
            best = next((r for r in ROUTES[:4] if r in kinds), "none")
            tile_routes.append(best)
            prev = [xc(cen(X[j][0])) for j in delta if X[j][1] < s]
            if prev and (x > max(prev) or x < min(prev)):
                adv_routes.append(best)
        # baseline: a few non-difference forced tiles
        nond = [k for k, v in X.items() if k not in delta and v[1] >= 1]
        base_kinds = []
        for k in rng.sample(nond, min(len(nond), 6)):
            t, s, e = X[k]
            okz, crit = criticals(base, rec, t, s, e)
            if okz:
                base_kinds += [contact(p, t, jstar, Rk) for p in crit]
        out["sides"].append(dict(n_delta=len(delta), z_fail=z_fail, links=links, tile_routes=tile_routes,
                                 adv_routes=adv_routes, base_kinds=base_kinds, ncrit=ncrit))
    return out


def world(k):
    rng = random.Random(T.SEED0 + k); brng = random.Random(4040 + k); c0 = T.centres()[k]
    P = L.Patch(L.seed_patch(c0, 3 * S)); n0 = len(P.tris); r = 0; choices = []
    while len(P.tris) - n0 < T.N_ADD:
        r += 1
        fr = P.frontier(); forced = {}; jam = False
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if not cs:
                jam = True; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        if jam:
            break
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= T.N_ADD:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed or forced:
            continue
        e = fr[0]
        cs = sorted(D.candidates(P, *e[:3]), key=lambda w: (w[0], L.key(w[1]), L.key(w[2]), L.key(w[3])))
        if len(cs) == 2:
            mid = (e[0] + e[1]) / 2
            rec = dict(world=k, slice=r, key=config_key(P.tris, mid))
            rec.update(analyse_choice(list(P.tris), cs, F.front_line(P, e), brng))
            choices.append(rec)
        P.add(rng.choice(cs))
    return dict(world=k, choices=choices)


def shares(xs):
    c = collections.Counter(xs); n = sum(c.values())
    return {r: round(c[r] / n, 3) if n else float("nan") for r in ROUTES}, n


def main():
    os.makedirs(RES, exist_ok=True)
    with Pool(4, maxtasksperchild=1) as p:
        W = p.map(world, range(T.N_WORLDS))
    json.dump(W, open(os.path.join(RES, "worlds.json"), "w"))
    seen = set(); C = []
    for w in W:
        for c in w["choices"]:
            if c["key"] not in seen:
                seen.add(c["key"]); C.append(c)
    sides = [sd for c in C for sd in c["sides"]]
    nd = sum(len(sd["tile_routes"]) + sd["z_fail"] for sd in sides); zf = sum(sd["z_fail"] for sd in sides)
    adv = [r for sd in sides for r in sd["adv_routes"]]
    adv_p = [r for r in adv if r != "none"]
    sh_adv, n_adv = shares(adv_p)
    lines = [f"choices: {sum(len(w['choices']) for w in W)} in total, {len(C)} distinct local configurations (3-edge structural key)",
             f"slices both siblings reached: {sorted(c['smax'] for c in C)}",
             f"  Z: {'PASS' if zf <= 0.01 * nd else 'FAIL'}  {nd - zf}/{nd} difference tiles uniquely forced by their 2.5-edge context",
             f"  advances: {len(adv)}, with a differing parent {n_adv} ({dict(collections.Counter(adv))})",
             f"  best-route shares among advances with a differing parent: {sh_adv}"]
    c1 = sh_adv["corner"] >= 1 / 3; c2 = sh_adv["other edge"] > sh_adv["corner"]; c3 = sh_adv["decided ribbon"] <= 0.5
    lines += [f"  C1: {'HELD  ' if c1 else 'FAILED'}  corner share {sh_adv['corner']:.3f} (need >= 0.333)",
              f"  C2: {'HELD  ' if c2 else 'FAILED'}  other-edge share {sh_adv['other edge']:.3f} > corner share {sh_adv['corner']:.3f}",
              f"  C3: {'HELD  ' if c3 else 'FAILED'}  decided-ribbon share {sh_adv['decided ribbon']:.3f} (need <= 0.5)"]
    sh_all, n_all = shares([r for sd in sides for r in sd["tile_routes"]])
    sh_links, n_links = shares([x for sd in sides for x in sd["links"]])
    sh_base, n_base = shares([x for sd in sides for x in sd["base_kinds"]])
    lines += [f"  reported: best route over all {n_all} difference tiles: {sh_all}",
              f"  reported: all differing-parent links ({n_links}) by contact: {sh_links}",
              f"  reported: baseline critical links of non-difference tiles ({n_base}) by contact: {sh_base}",
              f"  reported: critical tiles per forced placement: median {np.median([x for sd in sides for x in sd['ncrit']]):.0f}, "
              f"range {min(x for sd in sides for x in sd['ncrit'])}-{max(x for sd in sides for x in sd['ncrit'])}"]
    print("\n".join(lines))
    open(os.path.join(RES, "constraint_chains_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

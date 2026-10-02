#!/usr/bin/env python3
"""
perp_map.py -- a perp-space map of grown worlds (PREREGISTRATION.md, frozen before this file).
Lift every vertex to K in Z^5 along rhombus edges; perp address z_perp = sum K_j zeta^(2j); layer = sum K_j; hull depth
from each world's own per-layer convex hull (Niedzwiecki 2026, doi:10.5281/zenodo.20695694).
V0 on the reference tiling; M1 open vs forced frontier edges by depth (patient growth); M2 perp hull area of decapod vs
fillable worlds. `python3 perp_map.py` runs everything and writes results/.
"""
from __future__ import annotations
import os, sys, json, math, cmath, random, collections
from multiprocessing import Pool
import numpy as np
from scipy.spatial import ConvexHull

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "decapod_seed"))
import decapod_seed as D
L, S = D.L, D.S
ZETA = cmath.exp(2j * math.pi / 5)
N_M1, SEEDS_M1, SEED0 = 1000, 12, 20261070
RES = os.path.join(HERE, "results")


def edge_dir(p, q):
    a = math.degrees(cmath.phase(q - p)) % 360
    m = round((a - 18) / 36) % 10
    assert abs(((a - 18 - 36 * m) + 180) % 360 - 180) < 1e-3, "edge not along a tile direction"
    return (m // 2, 1) if m % 2 == 0 else (((m - 5) // 2) % 5, -1)


def lift(tiles):
    """BFS lift over rhombus edges (legs). Returns {key: K}, pos {key: z}, conflicts [K difference]."""
    adj = collections.defaultdict(list); pos = {}
    for t in tiles:
        for p, q in ((t[1], t[2]), (t[2], t[3]), (t[3], t[1])):
            if abs(abs(q - p) - S) < 1e-4 * S:
                kp, kq = L.key(p), L.key(q); pos[kp] = p; pos[kq] = q
                j, sg = edge_dir(p, q)
                adj[kp].append((kq, j, sg)); adj[kq].append((kp, j, -sg))
    K = {}; conflicts = []
    for start in adj:
        if start in K:
            continue
        K[start] = np.zeros(5, dtype=int); dq = collections.deque([start])
        while dq:
            u = dq.popleft()
            for v, j, sg in adj[u]:
                kv = K[u].copy(); kv[j] += sg
                if v not in K:
                    K[v] = kv; dq.append(v)
                elif not np.array_equal(K[v], kv):
                    conflicts.append(tuple(int(x) for x in K[v] - kv))
    return K, pos, conflicts


def perp(k):
    return sum(int(k[j]) * ZETA ** (2 * j) for j in range(5))


def depths(K):
    """hull depth per vertex from the world's own per-layer convex hulls; also hull areas per layer."""
    by = collections.defaultdict(list)
    for v, k in K.items():
        by[int(k.sum())].append((v, perp(k)))
    dep = {}; areas = {}
    for lay, items in by.items():
        if len(items) < 10:
            continue
        pts = np.array([[z.real, z.imag] for _, z in items])
        h = ConvexHull(pts); areas[lay] = float(h.volume)
        c = pts.mean(axis=0)
        n = h.equations[:, :2]; b = h.equations[:, 2]
        denom = -(n @ c + b)
        g = ((pts - c) @ n.T / denom).max(axis=1)
        for (v, _), gv in zip(items, g):
            dep[v] = float(min(1.0, max(0.0, 1.0 - gv)))
    return dep, areas, sorted(by)


def grow(ring, n_add, rs, wall=False, record=False):
    rng = random.Random(rs)
    P = L.Patch(list(ring)); n0 = len(P.tris); r = 0; events = []; guesses = []; status = "ok"
    while len(P.tris) - n0 < n_add:
        r += 1
        if r > 20000:
            status = "STALL"; break
        fr = [e for e in P.frontier() if not wall or abs((e[0] + e[1]) / 2) > D.APO + 1e-6]
        forced = {}
        for e in fr:
            cs = D.candidates(P, *e[:3])
            if record:
                events.append((L.key(e[0]), L.key(e[1]), len(cs)))
            if not cs:
                status = "JAM"; break
            if len(cs) == 1:
                forced.setdefault(D.dkey(cs[0]), cs[0])
        if status == "JAM":
            break
        placed = 0
        for t in forced.values():
            if len(P.tris) - n0 >= n_add:
                break
            if P.legal(t):
                P.add(t); placed += 1
        if placed == 0:
            if forced:
                continue
            cs = sorted(D.candidates(P, *fr[0][:3]), key=lambda u: (u[0], L.key(u[1]), L.key(u[2]), L.key(u[3])))
            P.add(rng.choice(cs)); guesses.append((L.key(fr[0][0]), L.key(fr[0][1])))
    return list(P.tris), events, guesses, status


def m1_task(k):
    tiles, events, guesses, status = grow(L.seed_patch(0j, 3 * S), N_M1, SEED0 + k, record=True)
    K, pos, conf = lift(tiles)
    dep, areas, layers = depths(K)
    d = lambda a, b: (dep[a] + dep[b]) / 2 if a in dep and b in dep else None
    op = [d(a, b) for a, b, n in events if n >= 2 and d(a, b) is not None]
    fo = [d(a, b) for a, b, n in events if n == 1 and d(a, b) is not None]
    gd = [d(a, b) for a, b in guesses if d(a, b) is not None]
    sig = hash(tuple(sorted(L.canon(t)[1].__hash__() for t in tiles)))
    return dict(run=k, status=status, conflicts=len(conf), layers=layers, n_open=len(op), n_forced=len(fo),
                med_open=float(np.median(op)), med_forced=float(np.median(fo)), guess_depths=gd, history=sig)


def m2_task(args):
    s, kind, ring = args
    tiles, _, guesses, status = grow(ring, 800, D.SEED0 + 100 * s, wall=True)
    K, pos, conf = lift(tiles)
    dep, areas, layers = depths(K)
    return dict(seed=s, kind=kind, status=status, guesses=len(guesses), conflicts=sorted(set(conf)),
                n_conflicts=len(conf), layers=layers, total_area=float(sum(areas.values())), areas=areas,
                n_vertices=len(K))


def main():
    os.makedirs(RES, exist_ok=True)
    ref = [t for t in L.REF if max(abs(z) for z in t[1:]) < 10 * S]
    K, pos, conf = lift(ref)
    lays = sorted({int(k.sum()) for k in K.values()})
    v0 = not conf and len(lays) == 4 and lays[-1] - lays[0] == 3
    lines = [f"  V0: {'PASS' if v0 else 'FAIL'}  reference tiling: {len(K)} vertices, lift conflicts {len(conf)}, layers {lays}"]
    with Pool(4, maxtasksperchild=2) as p:
        m1 = p.map(m1_task, range(SEEDS_M1))
    json.dump(m1, open(os.path.join(RES, "m1_runs.json"), "w"))
    wins = sum(r["med_open"] < r["med_forced"] for r in m1)
    lines.append(f"M1 runs: statuses {[r['status'] for r in m1]}; lift conflicts {[r['conflicts'] for r in m1]}; "
                 f"distinct histories {len({r['history'] for r in m1})}")
    for r in m1:
        lines.append(f"    run {r['run']}: median depth open {r['med_open']:.3f} (n {r['n_open']}) vs forced {r['med_forced']:.3f} "
                     f"(n {r['n_forced']}); guessed-edge depths {[round(x, 2) for x in r['guess_depths']]}")
    lines.append(f"  M1: {'HELD  ' if wins >= 9 else 'FAILED'}  open edges shallower than forced in {wins}/12 runs (need >= 9)")
    seeds = json.load(open(os.path.join(D.RES, "seeds.json")))
    R = [json.loads(l) for l in open(os.path.join(D.RES, "runs.jsonl"))]
    ok0 = lambda s: all(r["status"] == "ok" and not r["guesses"] for r in R if r["seed"] == s)
    dec = [x for x in seeds if x["kind"] == "DECAPOD" and ok0(x["seed"])][:8]
    fil = [x for x in seeds if x["kind"] == "FILLABLE"]
    ring = lambda x: [tuple([t[0]] + [complex(*z) for z in t[1:]]) for t in x["tiles"]]
    with Pool(4, maxtasksperchild=2) as p:
        m2 = p.map(m2_task, [(x["seed"], x["kind"], ring(x)) for x in dec + fil])
    json.dump(m2, open(os.path.join(RES, "m2_worlds.json"), "w"))
    fa = float(np.median([w["total_area"] for w in m2 if w["kind"] == "FILLABLE"]))
    da = [w["total_area"] for w in m2 if w["kind"] == "DECAPOD"]
    for w in m2:
        lines.append(f"    {w['kind']:<8} seed {w['seed']:>3}: {w['status']}, guesses {w['guesses']}, vertices {w['n_vertices']}, "
                     f"layers {w['layers']}, total perp hull area {w['total_area']:.2f}, lift conflicts {w['n_conflicts']} {w['conflicts'][:4]}")
    m2ok = all(a > fa for a in da)
    lines.append(f"  M2: {'HELD  ' if m2ok else 'FAILED'}  decapod worlds' total perp hull area > fillable median ({fa:.2f}): "
                 f"{sum(a > fa for a in da)}/{len(da)}; decapod areas {[round(a, 2) for a in da]}")
    print("\n".join(lines))
    open(os.path.join(RES, "perp_map_report.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

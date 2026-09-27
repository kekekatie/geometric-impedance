#!/usr/bin/env python3
"""
decapod.py -- is the writing walker's stubborn centre knot one of Conway's bad decapods?
(PREREGISTRATION_DECAPOD.md, frozen before this file existed.)

D1 (asserted): the pristine centre decagon has a legal filling.
D2: with everything outside fixed, EVERY filling of the centre decagon reachable by interior flips is
    checked; prediction: none is legal (push 0.2 and 0.05).
D3: flips anywhere within radius 3, exhaustive up to 500,000 states: the centre knot still does not heal.
D4: walkers on other roads (family 0 and family 1, lines -4..4): "stubborn within depth 4" agrees with
    "contains a decagon ring" for >= 90% of mid-wake knots.
"""
from __future__ import annotations
import os, sys, math, itertools, json, collections
from multiprocessing import Pool
import writing_walker as W
import healing as H

PHI = (1 + 5 ** 0.5) / 2
EV, GAMMA, par = W.EV, W.GAMMA, W.par
LINES, FAILS, VERDICTS = [], [], []


def log(s=""):
    LINES.append(s); print(s, flush=True)


def require(cond, msg):
    log(("  [PASS] " if cond else "  [FAIL] ") + msg)
    if not cond:
        FAILS.append(msg)


def verdict(tag, held, msg):
    VERDICTS.append((tag, held, msg)); log(f"  {tag}: {'HELD  ' if held else 'FAILED'}  {msg}")


# ------------------------------------------------------------ generalised walker (any family J, line C)
def build_road(J, C, delta, t0=30.0):
    EJ = EV[J]; EJP = (-EJ[1], EJ[0])

    def off(x):
        return delta * W.h(W.SCALE * W.dot(EJP, x), t0)

    faces = {}
    R = W.R
    nrange = range(-int(R) - 3, int(R) + 4)
    for r, s in itertools.combinations(range(5), 2):
        det = EV[r][0] * EV[s][1] - EV[r][1] * EV[s][0]
        for nr in nrange:
            for ns in nrange:
                br, bs = nr + GAMMA[r], ns + GAMMA[s]
                x = ((br * EV[s][1] - bs * EV[r][1]) / det, (bs * EV[r][0] - br * EV[s][0]) / det)
                on_road = (r == J and nr == C) or (s == J and ns == C)
                if on_road and delta > 0:
                    o = s if r == J else r
                    bo = (ns if r == J else nr) + GAMMA[o]
                    d = (-EV[o][1], EV[o][0]); p0 = (bo * EV[o][0], bo * EV[o][1])
                    g = lambda u: W.dot(EJ, (p0[0] + u * d[0], p0[1] + u * d[1])) - GAMMA[J] - C - \
                        off((p0[0] + u * d[0], p0[1] + u * d[1]))
                    u_star = (C + GAMMA[J] - W.dot(EJ, p0)) / W.dot(EJ, d)
                    lo, hi = u_star - 2.0, u_star + 2.0; glo = g(lo)
                    assert glo * g(hi) < 0
                    for _ in range(80):
                        mid = 0.5 * (lo + hi); gm = g(mid)
                        if gm * glo <= 0:
                            hi = mid
                        else:
                            lo, glo = mid, gm
                    u = 0.5 * (lo + hi); x = (p0[0] + u * d[0], p0[1] + u * d[1])
                if x[0] ** 2 + x[1] ** 2 > (R + 3) ** 2:
                    continue
                base = [math.ceil(x[0] * EV[j][0] + x[1] * EV[j][1] - GAMMA[j]) for j in range(5)]
                if J not in (r, s) and delta > 0:
                    sj = W.dot(EJ, x) - GAMMA[J]
                    if C < sj < C + off(x):
                        base[J] -= 1
                corners = []
                for dr, ds in ((0, 0), (1, 0), (1, 1), (0, 1)):
                    K = list(base); K[r] = nr + dr; K[s] = ns + ds
                    corners.append(tuple(K))
                if any(math.hypot(*par(K)) > R for K in corners):
                    continue
                faces[frozenset(corners)] = (tuple(corners), (r, s), nr, ns)
    return faces, EJP


def star_ok(T, K, atlas):
    return T.star(K) in atlas


# ------------------------------------------------------------ D1 / D2: exhaustive decagon fillings
def decagon_fillings(F, atlas, centre=(0.0, 0.0)):
    dc = lambda K: math.hypot(par(K)[0] - centre[0], par(K)[1] - centre[1])
    local = [cs for cs, *_ in F.values() if any(dc(K) <= PHI + 2.5 for K in cs)]
    T0 = H.Tiling(local)
    ring = [K for K in T0.vf if abs(dc(K) - PHI) < 0.02]
    assert len(ring) == 10
    seen = {frozenset(T0.faces)}; stack = [T0]; legal = 0; n = 0
    while stack:
        t = stack.pop(); n += 1
        inside = [K for K in t.vf if dc(K) < PHI - 0.05]
        if all(star_ok(t, K, atlas) for K in ring + inside):
            legal += 1
        for v in inside:
            plan = t.flip_plan(v)
            if plan is None:
                continue
            t2 = t.copy(); t2.apply(plan); key = frozenset(t2.faces)
            if key not in seen:
                seen.add(key); stack.append(t2)
    return n, legal


# ------------------------------------------------------------ D3: wide capped search (diff-encoded states)
def wide_search(F, atlas, knot, illegal, radius=3.0, cap=500_000):
    near = lambda K: math.hypot(*par(K)) <= radius
    local = [cs for cs, *_ in F.values() if any(math.hypot(*par(K)) <= radius + 3 for K in cs)]
    start = H.Tiling(local); start_keys = set(start.faces)
    ks = set(knot); others = illegal - ks
    ids, rev = {}, {}

    def fid(k):
        if k not in ids:
            ids[k] = len(ids); rev[ids[k]] = k
        return ids[k]

    def realise(diff):
        t = start.copy()
        for i in sorted(diff):
            k = rev[i]
            if k in t.faces:
                t.apply(([k], [], None))
        for i in sorted(diff):
            k = rev[i]
            if k not in start_keys:
                t.apply(([], [facemap[k]], None))
        return t

    facemap = dict(start.faces)
    seen = {frozenset()}; frontier = [frozenset()]; states = 1; depth = 0
    while frontier and states < cap:
        depth += 1; nxt = []
        for diff in frontier:
            t = realise(diff)
            for v in [K for K in list(t.vf) if near(K)]:
                plan = t.flip_plan(v)
                if plan is None:
                    continue
                d2 = set(diff)
                for k in plan[0]:
                    d2 ^= {fid(k)}
                for cs in plan[2 - 1]:
                    k = frozenset(cs); facemap.setdefault(k, cs); d2 ^= {fid(k)}
                d2 = frozenset(d2)
                if d2 in seen:
                    continue
                seen.add(d2); states += 1
                t2 = t.copy(); t2.apply(plan)
                changed = {K for i in d2 for K in rev[i]} | ks
                bad = {K for K in changed if K in t2.vf and math.hypot(*par(K)) <= radius + 1 and not star_ok(t2, K, atlas)}
                if not (bad - others) and not (bad & ks):
                    return True, depth, states
                nxt.append(d2)
                if states >= cap:
                    break
            if states >= cap:
                break
        frontier = nxt
    return False, depth, states


# ------------------------------------------------------------ memory-safe version of healing.heal_search
def heal_search_lean(T, knot, atlas, illegal_before, radius=None, depth_max=None, cap=400_000, strict_cap=False):
    """Same breadth-first search, same move set, same success test and same 400,000-state cap as
    healing.heal_search, but each state is stored as a small DIFF from the start instead of a full copy
    of the neighbourhood (the full copies exhausted memory on large knots: OOM-killed workers)."""
    radius = H.RADIUS if radius is None else radius
    depth_max = H.DEPTH if depth_max is None else depth_max
    pts = list(knot); ks = set(knot); others = illegal_before - ks
    near = lambda K: min(H.dist(K, q) for q in pts) <= radius
    local = [cs for cs in T.faces.values() if any(min(H.dist(K, q) for q in pts) <= radius + 3 for K in cs)]
    start = H.Tiling(local); start_keys = set(start.faces); facemap = dict(start.faces)
    ids, rev = {}, {}

    def fid(k):
        if k not in ids:
            ids[k] = len(ids); rev[ids[k]] = k
        return ids[k]

    def realise(diff):
        t = start.copy()
        rem = [rev[i] for i in diff if rev[i] in start_keys]
        add = [facemap[rev[i]] for i in diff if rev[i] not in start_keys]
        if rem:
            t.apply((rem, [], None))
        if add:
            t.apply(([], add, None))
        return t

    seen = {frozenset()}; frontier = [frozenset()]
    for depth in range(1, depth_max + 1):
        nxt = []
        for diff in frontier:
            t = realise(diff)
            for v in [K for K in list(t.vf) if near(K)]:
                plan = t.flip_plan(v)
                if plan is None:
                    continue
                d2 = set(diff)
                for k in plan[0]:
                    d2 ^= {fid(k)}
                for cs in plan[1]:
                    k = frozenset(cs); facemap.setdefault(k, cs); d2 ^= {fid(k)}
                d2 = frozenset(d2)
                if d2 in seen:
                    continue
                seen.add(d2)
                t2 = t.copy(); t2.apply(plan)
                check = {K for i in d2 for K in rev[i] if K in t2.vf} | {K for K in ks if K in t2.vf}
                bad = {K for K in check if t2.star(K) not in atlas}
                if not (bad - others) and not (bad & ks):
                    return depth
                nxt.append(d2)
                if strict_cap and len(seen) > cap:
                    return None          # strict: stop mid-level (used only for road (0,-2); see README)
        frontier = nxt
        if len(seen) > cap:
            return None
    return None


# ------------------------------------------------------------ D4: many roads
def ring_centre(knot):
    for v in knot:
        pv = par(v)
        for k in range(20):
            th = math.radians(18 * k)
            c = (pv[0] - PHI * math.cos(th), pv[1] - PHI * math.sin(th))
            on = [K for K in knot if abs(math.hypot(par(K)[0] - c[0], par(K)[1] - c[1]) - PHI) < 0.02]
            if len(on) >= 8:
                return c
    return None


def road_task(args):
    J, C = args
    base = W.build(0.0, 0.0); atlas = set(W.star_types(base).values())
    F, EJP = build_road(J, C, 0.2)
    types = W.star_types(F)
    illegal = {K for K, tp in types.items() if tp not in atlas}
    mid = [K for K in illegal if abs(W.dot(EJP, par(K))) <= 25]
    groups, left = [], set(mid)
    while left:
        g, st = [], [left.pop()]
        while st:
            u = st.pop(); g.append(u)
            for q in list(left):
                if H.dist(u, q) <= H.LINK:
                    left.discard(q); st.append(q)
        groups.append(g)
    T = H.Tiling([cs for cs, *_ in F.values()])
    rows = []
    for g in groups:
        d = heal_search_lean(T, g, atlas, illegal)
        c = ring_centre(g)
        rows.append(dict(J=J, C=C, size=len(g), healed=d is not None, depth=d, ring=c is not None,
                         centre=c, t=round(sum(W.dot(EJP, par(K)) for K in g) / len(g), 2)))
    return rows


def main():
    os.makedirs(W.RES, exist_ok=True)
    log("=" * 96)
    log("DECAPOD TEST -- is the walker's stubborn centre knot a bad (unfillable) decagon?")
    log("=" * 96)
    base = W.build(0.0, 0.0); atlas = set(W.star_types(base).values())
    require(build_road(0, 0, 0.2)[0] == W.build(0.2, 30.0),
            "the generalised road builder reproduces the original walker exactly on its own road")
    n0, l0 = decagon_fillings(base, atlas)
    log(f"  pristine centre decagon: {n0} fillings reachable by interior flips; legal: {l0}")
    require(l0 >= 1, "D1: the pristine centre decagon has at least one legal filling")
    d2 = []
    for delta in (0.2, 0.05):
        n, l = decagon_fillings(W.build(delta, 30.0), atlas)
        d2.append(l == 0)
        log(f"  walker push {delta}: {n} fillings of the centre decagon reachable; legal: {l}")
    verdict("D2", all(d2), "no filling of the centre decagon is legal once the walker has passed (push 0.2 and 0.05)")
    F = W.build(0.2, 30.0)
    Tt, illegal, groups = H.knots_of(F, atlas)
    centre_knot = min(groups, key=lambda g: abs(sum(W.dot(W.EJP, par(K)) for K in g)))
    ok, depth, states = wide_search(F, atlas, centre_knot, illegal)
    log(f"  wide search (radius 3, cap 500,000): {'HEALED at depth ' + str(depth) if ok else 'not healed'}; "
        f"{states} states explored, deepest level {depth}")
    verdict("D3", not ok, f"the centre knot does not heal with flips anywhere within radius 3 ({states} states)")
    roads = [(0, c) for c in range(-4, 5)] + [(1, c) for c in range(-4, 5)]
    with Pool(os.cpu_count()) as p:
        rows = [r for rs in p.map(road_task, roads) for r in rs]
    agree = sum(1 for r in rows if r["ring"] == (not r["healed"]))
    for r in rows:
        log(f"    road family {r['J']} line {r['C']:+d}: knot at t={r['t']:+6.1f} size {r['size']:>2} "
            f"{'HEALED d=' + str(r['depth']) if r['healed'] else 'stubborn':<11} decagon ring: {r['ring']}")
    stub = [r for r in rows if not r["healed"]]
    log(f"  {len(rows)} knots on {len(roads)} roads; stubborn: {len(stub)}; with decagon ring: "
        f"{sum(r['ring'] for r in rows)}; stubborn AND ring: {sum(1 for r in stub if r['ring'])}")
    verdict("D4", rows and agree / len(rows) >= 0.9,
            f"'stubborn' agrees with 'contains a decagon ring' for {agree}/{len(rows)} knots "
            f"({agree / max(len(rows), 1):.0%}; need >= 90%)")
    log("=" * 96)
    log("PREDICTIONS: " + ", ".join(f"{t} {'held' if h else 'FAILED'}" for t, h, _ in VERDICTS))
    log("STRUCTURAL CHECKS: " + ("ALL PASSED" if not FAILS else "FAILED: " + "; ".join(FAILS)))
    open(os.path.join(W.RES, "decapod_report.txt"), "w").write("\n".join(LINES) + "\n")
    json.dump(rows, open(os.path.join(W.RES, "decapod_roads.json"), "w"), default=str)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
